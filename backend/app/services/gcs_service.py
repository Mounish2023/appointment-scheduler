from google.cloud import storage
import datetime
import os
from ..config import settings
from fastapi import UploadFile
import json

with open("gen-lang-client-0323926280-da7a40e1c1f6.json", "r") as f:
    info = json.load(f)

class GCSService:
    def __init__(self):
        self.bucket_name = settings.GCS_BUCKET_NAME
        
        if not self.bucket_name:
             print("Warning: GCS_BUCKET_NAME not set in settings.")
        
        try:
            self.storage_client = storage.Client.from_service_account_info(info)
            self.bucket = self.storage_client.bucket(self.bucket_name) if self.bucket_name else None
            if self.bucket:
                print("DEBUG: GCS Bucket object created successfully")
        except Exception as e:
            print(f"Error initializing GCS client: {e}")
            self.storage_client = None
            self.bucket = None

    def upload_file(self, file: UploadFile, destination_blob_name: str, content_type: str = None) -> str:
        """Uploads a file to the bucket."""
        if not self.bucket:
             raise Exception("GCS Bucket not configured")

        blob = self.bucket.blob(destination_blob_name)
        
        # Reset file pointer to beginning just in case
        file.file.seek(0)
        
        blob.upload_from_file(file.file, content_type=content_type or file.content_type)
        
        return blob.name

    def generate_signed_url(self, blob_name: str, expiration_minutes: int = 15) -> str:
        """Generates a v4 signed URL for downloading a blob."""
        if not self.bucket:
             raise Exception("GCS Bucket not configured")

        blob = self.bucket.blob(blob_name)
        
        url = blob.generate_signed_url(
            version="v4",
            # This URL is valid for 15 minutes by default
            expiration=datetime.timedelta(minutes=expiration_minutes),
            method="GET",
        )

        return url

    def delete_file(self, blob_name: str):
         """Deletes a blob from the bucket."""
         if not self.bucket:
             raise Exception("GCS Bucket not configured")
         
         blob = self.bucket.blob(blob_name)
         blob.delete()

    def download_as_bytes(self, blob_name: str) -> bytes:
        """Downloads a blob as bytes."""
        if not self.bucket:
             raise Exception("GCS Bucket not configured")
        
        blob = self.bucket.blob(blob_name)
        return blob.download_as_bytes()
