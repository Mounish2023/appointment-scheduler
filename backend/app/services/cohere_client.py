import cohere
from ..config import settings

# from langchain_cohere import CohereEmbeddings

# embeddings = CohereEmbeddings(
#     model="embed-english-v3.0",
# )

class CohereClient:
    def __init__(self):
        if not settings.COHERE_API_KEY:
             print("Warning: COHERE_API_KEY not set.")
             self.client = None
        else:
            self.client = cohere.ClientV2(settings.COHERE_API_KEY)

    def embed_texts(self, texts: list[str], model="embed-v4.0") -> list[list["int8"]]:
        if not self.client:
            print("Error: Cohere client not initialized.")
            return []
        
        try:
            # Cohere v4/v3 embedding
            response = self.client.embed(
                texts=texts,
                model=model,
                input_type="search_document",
                output_dimension=1024,
                embedding_types=["int8"]

            )
            embeddings = response.embeddings.int8
            return embeddings
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            return []
    def generate_query_vector(self, query: str, model="embed-v4.0") -> list[list["int8"]]:
        if not self.client:
            print("Error: Cohere client not initialized.")
            return []
        try:
            response = self.client.embed(
                texts=[query],
                model=model,
                input_type="search_query",
                output_dimension=1024,
                embedding_types=["int8"]
            )
            embeddings = response.embeddings.int8
            return embeddings[0]
        except Exception as e:
            print(f"Error generating query vector: {e}")
            return []
