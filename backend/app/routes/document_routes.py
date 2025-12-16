from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status, BackgroundTasks
from typing import List
import os
import uuid
from datetime import datetime
from pydantic import BaseModel
from ..database import MongoDBClient
from ..routes.auth_routes import get_current_active_user
from ..schemas import User
from ..services.gcs_service import GCSService
from ..services.ingestion_service import IngestionService

router = APIRouter()
mongo_client = MongoDBClient()
documents_collection = mongo_client.get_collection(collection_name="documents")
gcs_service = GCSService()
ingestion_service = IngestionService()

class DocumentResponse(BaseModel):
    id: str
    filename: str
    content_type: str
    size: int
    created_at: datetime
    path: str # This will now store the GCS blob path

    class Config:
        from_attributes = True

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    print(f"DEBUG: Entering upload_document for user: {current_user.userid}, filename: {file.filename}")
    try:
        userid = current_user.userid
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        new_filename = f"{userid}/{file_id}{file_extension}"
        print(f"DEBUG: Generated new_filename: {new_filename} for userid: {userid}")

        # Upload to GCS
        print(f"DEBUG: Starting GCS upload for {file.filename} to path {new_filename}")
        gcs_path = gcs_service.upload_file(file, new_filename, file.content_type)
        print(f"DEBUG: GCS upload complete. GCS path: {gcs_path}")
        
        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()
        file.file.seek(0)
        print(f"DEBUG: Calculated file size: {file_size} bytes")
        
        document = {
            "id": file_id,
            "userid": str(userid),
            "filename": file.filename,
            "content_type": file.content_type,
            "size": file_size,
            "path": gcs_path,
            "created_at": datetime.now()
        }
        print(f"DEBUG: Document prepared for insertion: {document}")

        await documents_collection.insert_one(document)
        print(f"DEBUG: Document inserted into MongoDB with id: {file_id}")
        
        # Trigger Ingestion
        print(f"DEBUG: Triggering background ingestion for {file_id}")
        background_tasks.add_task(
            ingestion_service.ingest_document,
            document_id=file_id,
            user_id=str(userid),
            gcs_path=gcs_path,
            document_title=file.filename
        )

        return DocumentResponse(**document)

    except Exception as e:
        print(f"ERROR: Exception occurred during file upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}"
        )

@router.get("/", response_model=List[DocumentResponse])
async def get_documents(
    current_user: User = Depends(get_current_active_user)
):
    try:
        userid = current_user.userid
        cursor = documents_collection.find({"userid": str(userid)})
        documents = await cursor.to_list(length=1000)
        return [DocumentResponse(**doc) for doc in documents]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving documents: {str(e)}"
        )

@router.get("/{document_id}/download")
async def download_document(
    document_id: str,
    current_user: User = Depends(get_current_active_user)
):
    try:
        userid = current_user.userid
        document = await documents_collection.find_one({"id": document_id, "userid": str(userid)})
        
        if not document:
             raise HTTPException(status_code=404, detail="Document not found")

        # Generate signed URL
        signed_url = gcs_service.generate_signed_url(document["path"])
        
        return {"download_url": signed_url}

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating download URL: {str(e)}"
        )
