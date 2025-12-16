from typing import List, Dict, Any
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from app.config import settings

class AzureSearchService:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AzureSearchService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.endpoint = settings.AZURE_SEARCH_ENDPOINT
            self.api_key = settings.AZURE_SEARCH_API_KEY
            self.index_name = settings.AZURE_SEARCH_INDEX_NAME
            self._search_client = None # To store the initialized SearchClient

            if not all([self.endpoint, self.api_key, self.index_name]):
                print("Warning: Azure Search environment variables are missing. Ingestion will fail.")
            self._initialized = True

    def get_client(self) -> SearchClient:
        if not all([self.endpoint, self.api_key, self.index_name]):
             raise ValueError("Azure Search environment variables are missing.")
        
        if self._search_client is None:
            self._search_client = SearchClient(
                endpoint=self.endpoint,
                index_name=self.index_name,
                credential=AzureKeyCredential(self.api_key)
            )
        return self._search_client

    def upload_documents(self, documents: List[Dict[str, Any]]):
        """
        Uploads a batch of documents to Azure AI Search.
        """
        if not documents:
            return

        client = self.get_client()
        try:
            results = client.upload_documents(documents=documents)
            print(f"Successfully uploaded {len(documents)} documents to Azure AI Search.")
            return results
        except Exception as e:
            print(f"Error uploading documents to Azure AI Search: {e}")
            raise
