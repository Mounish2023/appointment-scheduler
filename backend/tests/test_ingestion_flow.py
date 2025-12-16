import unittest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os
import json

# Adjust path to import app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock external dependencies BEFORE importing IngestionService
# because IngestionService imports them at top level
sys.modules['app.database'] = MagicMock()
sys.modules['app.database'].document_extractor_client = MagicMock()
sys.modules['app.services.gcs_service'] = MagicMock()
sys.modules['app.services.cohere_client'] = MagicMock()
sys.modules['app.services.vespa_client'] = MagicMock()
sys.modules['fitz'] = MagicMock()

from app.services.ingestion_service import IngestionService

class TestIngestionService(unittest.IsolatedAsyncioTestCase):
    async def test_ingest_document_flow(self):
        # Setup Mocks
        service = IngestionService()
        
        # Mock GCS
        service.gcs_service.download_as_bytes.return_value = b"fake pdf content"
        mock_blob = MagicMock()
        service.gcs_service.bucket.blob.return_value = mock_blob
        
        # Mock LandingAI
        mock_parse_response = {
            "chunks": [
                {
                    "id": "chunk1",
                    "type": "text",
                    "text": "Hello World",
                    "grounding": {"page": 0}
                },
                {
                    "id": "chunk2",
                    "type": "figure",
                    "grounding": {"page": 0, "box": {"left": 0.1, "top": 0.1, "right": 0.5, "bottom": 0.5}}
                }
            ]
        }
        # Configure the mock to return an object that acts like the response
        # or just return the dict if the service handles it. 
        # The service calls .model_dump() or uses it directly.
        # Let's make it simple: service logic handles non-pydantic too.
        from app.database import document_extractor_client
        document_extractor_client.parse.return_value = mock_parse_response

        # Mock PyMuPDF (fitz)
        import fitz
        mock_doc = MagicMock()
        mock_page = MagicMock()
        fitz.open.return_value = mock_doc
        mock_doc.load_page.return_value = mock_page
        mock_doc.__len__.return_value = 1
        mock_pix = MagicMock()
        mock_page.get_pixmap.return_value = mock_pix
        mock_pix.tobytes.return_value = b"fake image bytes"

        # Mock Cohere
        service.cohere_client.embed_texts.return_value = [[0.1, 0.2, 0.3]]

        # Run
        await service.ingest_document("doc1", "user1", "gcs/path/doc.pdf")

        # Verifications
        
        # 1. Download
        service.gcs_service.download_as_bytes.assert_called_with("gcs/path/doc.pdf")
        
        # 2. Parse (LandingAI)
        document_extractor_client.parse.assert_called()
        
        # 3. Bronze Upload
        # Check if upload_from_string was called for bronze
        # We can inspect the calls to blob() and then upload_from_string
        service.gcs_service.bucket.blob.assert_any_call("bronze/user1/doc1.json")
        
        # 4. Silver Upload (Image)
        service.gcs_service.bucket.blob.assert_any_call("silver/user1/doc1/figures/chunk2.png")
        
        # 5. Silver Upload (Chunks)
        service.gcs_service.bucket.blob.assert_any_call("silver/user1/doc1/chunks.json")
        
        # 6. Embeddings
        service.cohere_client.embed_texts.assert_called()
        
        # 7. Gold Upload
        service.gcs_service.bucket.blob.assert_any_call("gold/user1/doc1/chunks.json")
        
        # 8. Vespa Feed
        # 2 chunks, so 2 calls? 
        # Wait, embedding is only for text chunks. chunk2 is figure.
        # Logic: for chunk in processed_chunks...
        # If schema supports all, it feeds all.
        print(f"Vespa calls: {service.vespa_client.feed_document.call_count}")
        self.assertEqual(service.vespa_client.feed_document.call_count, 2)

if __name__ == '__main__':
    unittest.main()
