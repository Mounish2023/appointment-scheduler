
import os
import json
import fitz  # PyMuPDF
import tempfile
from pathlib import Path
from typing import List, Dict, Any
from app.database import document_extractor_client
from app.services.gcs_service import GCSService
from app.services.cohere_client import CohereClient
import re
from app.services.search_client import AzureSearchService

# TODO: Modifications: 
# 1. remove <a id=""></a> from the parsed document that comes at the start of the document
# 2. 

class IngestionService:
    def __init__(self):
        self.gcs_service = GCSService()
        self.cohere_client = CohereClient()
        self.search_service = AzureSearchService()

    def ingest_document(self, document_id: str, user_id: str, gcs_path: str, document_title: str):
        """
        Orchestrates the ingestion pipeline:
        1. Parse (LandingAI)
        2. Bronze Layer (Raw JSON)
        3. Silver Layer (Chunking + Crop Figures/Tables)
        4. Embedding (Cohere)
        5. Gold Layer (Chunks + Embeddings)
        6. Indexing (Vespa)
        """
        print(f"Starting ingestion for document {document_id} (User: {user_id})")
        
        try:
            # --- Prerequisite: Download PDF from GCS ---
            pdf_bytes = self.gcs_service.download_as_bytes(gcs_path)
            
            # Save to temporary file for libraries that prefer file paths (LandingAI, PyMuPDF)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                tmp_pdf.write(pdf_bytes)
                tmp_pdf_path = tmp_pdf.name

            try:
                # --- Step 1: Parse ---
                # Assuming document_extractor_client.parse accepts a file path
                print("Parsing document...")
                parse_response = document_extractor_client.parse(
                    document=Path(tmp_pdf_path),
                    model="dpt-2"
                )
                
                # The response might be an object, convert to dict/json if needed
                # Assuming parse_response is a pydantic model or similar that can be dumped to json
                # If it's a dict verify. The sample showed a JSON structure.
                # If it's an object use .dict() or .model_dump() or str() and json.loads()
                # For safety, let's assume it's serializable or use a helper if needed.
                # Based on usage `print(parse_response)`, it might be a string or object with __repr__.
                # We will cast to dict if possible.
                try:
                    raw_json_data = parse_response.model_dump() if hasattr(parse_response, 'model_dump') else parse_response
                except:
                     raw_json_data = parse_response # Fallback

                # --- Step 2: Bronze Layer ---
                bronze_path = f"bronze/{user_id}/{document_id}.json"
                print(f"Uploading Bronze Layer to {bronze_path}...")
                
                # Convert to valid JSON string
                json_content = json.dumps(raw_json_data, indent=2, default=str)
                
                # Upload string as file
                # We need to create a temporary file or use a BytesIO wrapper. 
                # GCSService expects UploadFile (Starlette) which has a .file attribute.
                # BUT GCSService.upload_file is designed for FastAPI UploadFile.
                # We should probably use the internal bucket directly or mock an UploadFile.
                # Better: Add a method to GCSService to upload bytes/string directly.
                # For now, I will create a dummy UploadFile-like object or modify GCSService.
                # Actually, I can just use the bucket directly since I have access to `self.gcs_service.bucket`.
                
                if self.gcs_service.bucket:
                     blob = self.gcs_service.bucket.blob(bronze_path)
                     blob.upload_from_string(json_content, content_type="application/json")
                else:
                     print("GCS Bucket not available, skipping upload.")

                # --- Step 3: Silver Layer (Chunking & Extraction) ---
                print("Processing chunks (Silver Layer)...")
                chunks = raw_json_data.get("chunks", [])
                processed_chunks = []
                
                # Open PDF for cropping
                doc = fitz.open(tmp_pdf_path)

                for chunk in chunks:
                    chunk_type = chunk.get("type", "text") # text, figure, table
                    chunk_id = chunk.get("id")
                    
                    # Clean content (remove <a id='...'></a>)
                    raw_text = chunk.get("markdown") or chunk.get("text") or ""
                    # Regex to remove anchor tags like <a id='...'></a>
                    cleaned_text = re.sub(r"<a id=['\"][a-f0-9\-]+['\"]></a>\s*", "", raw_text).strip()

                    processed_chunk = {
                        "chunk_id": chunk_id,
                        "document_id": document_id,
                        "chunk_type": chunk_type,
                        "chunk_page_number": chunk.get("grounding", {}).get("page"),
                        "chunk_processed_content": cleaned_text,
                        # chunkRawContent will be updated for figures/tables
                        "chunk_raw_content": cleaned_text,
                        "document_title": document_title
                    }

                    if chunk_type in ["figure", "table"]:
                         grounding = chunk.get("grounding", {})
                         box = grounding.get("box", {})
                         page_num = grounding.get("page", 0)
                         
                         if box and page_num is not None and page_num < len(doc):
                             page = doc.load_page(page_num)
                             # Calculate rect: box provides normalized coordinates? 
                             # Sample: left: 0.1, top: 0.3... 
                             # We need to scale by page size.
                             rect = fitz.Rect(
                                 box["left"] * page.rect.width,
                                 box["top"] * page.rect.height,
                                 box["right"] * page.rect.width,
                                 box["bottom"] * page.rect.height
                             )
                             
                             # Crop
                             pix = page.get_pixmap(clip=rect)
                             img_data = pix.tobytes("png")
                             
                             # Upload Image to GCS
                             asset_type_dir = "figures" if chunk_type == "figure" else "tables"
                             asset_url_key = "imageUrl" if chunk_type == "figure" else "tableUrl"
                             asset_filename = f"silver/{user_id}/{document_id}/{asset_type_dir}/{chunk_id}.png"
                             if self.gcs_service.bucket:
                                 blob = self.gcs_service.bucket.blob(asset_filename)
                                 blob.upload_from_string(img_data, content_type="image/png")
                                 
                                 processed_chunk["chunk_raw_content"] = asset_filename
                                #  processed_chunk[asset_url_key] = asset_filename

                    processed_chunks.append(processed_chunk)

                doc.close()

                # Upload Silver Layer Chunks
                silver_path = f"silver/{user_id}/{document_id}/chunks.json"
                print(f"Uploading Silver Layer to {silver_path}...")
                if self.gcs_service.bucket:
                     blob = self.gcs_service.bucket.blob(silver_path)
                     blob.upload_from_string(json.dumps(processed_chunks, indent=2, default=str), content_type="application/json")


                # --- Step 4: Embedding ---
                print("Generating embeddings...")
                texts_to_embed = [c["chunk_processed_content"] for c in processed_chunks if c["chunk_processed_content"].strip()]
                # Note: Cohere has a limit on batch size (96?). We might need to batch.
                
                # Simple batching
                batch_size = 90
                embeddings = []
                for i in range(0, len(texts_to_embed), batch_size):
                    batch = texts_to_embed[i:i+batch_size]
                    batch_embeddings = self.cohere_client.embed_texts(batch)
                    embeddings.extend(batch_embeddings)
                
                # Map back to chunks
                # Only chunks with text got embeddings. 
                # Chunks without text (if any) won't match index.
                # Strategy: Iterate chunks, if text exists, pop from embeddings.
                
                embed_iter = iter(embeddings)
                for chunk in processed_chunks:
                    if chunk["chunk_processed_content"].strip():
                        try:
                            chunk["chunk_embedding"] = next(embed_iter)
                        except StopIteration:
                            chunk["chunk_embedding"] = []
                    else:
                        chunk["chunk_embedding"] = []

                # --- Step 5: Gold Layer ---
                gold_path = f"gold/{user_id}/{document_id}/chunks.json"
                print(f"Uploading Gold Layer to {gold_path}...")
                if self.gcs_service.bucket:
                     blob = self.gcs_service.bucket.blob(gold_path)
                     blob.upload_from_string(json.dumps(processed_chunks, indent=2, default=str), content_type="application/json")


                # --- Step 6: Indexing (Azure AI Search) ---
                print("Indexing to Azure AI Search...")

                # Filter chunks that have embeddings
                chunks_with_embeddings = [c for c in processed_chunks if c.get("chunk_embedding")]

                # Transform chunks to Azure Search format
                azure_search_documents = []
                for chunk in chunks_with_embeddings:
                    doc = {
                        "id": chunk["chunk_id"], 
                        "chunk_id": chunk["chunk_id"],
                        "document_id": chunk["document_id"],
                        "document_title": chunk["document_title"],
                        "chunk_type": chunk["chunk_type"],
                        "chunk_processed_content": chunk["chunk_processed_content"],
                        "chunk_embedding": chunk["chunk_embedding"],
                        "chunk_page_number": chunk.get("chunk_page_number"),
                        "chunk_raw_content": chunk.get("chunk_raw_content")
                    }
                    azure_search_documents.append(doc)

                if azure_search_documents:
                    self.search_service.upload_documents(azure_search_documents)
                else:
                    print("No chunks with embeddings to index.")

                print("Ingestion complete.")

            finally:
                # Cleanup temp file
                if os.path.exists(tmp_pdf_path):
                    os.remove(tmp_pdf_path)

        except Exception as e:
            print(f"Error during ingestion: {e}")
            # Optionally update status in DB to "failed"
