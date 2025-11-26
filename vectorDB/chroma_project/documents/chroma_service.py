import chromadb
import os
from dotenv import load_dotenv

project_dir = os.path.dirname(os.path.dirname(__file__))
env_path = os.path.join(project_dir, ".env")
load_dotenv(env_path)

class ChromaService:
    _client = None
    _collection = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            cls._client = chromadb.CloudClient(
                api_key=os.getenv("CHROMA_API_KEY"),
                tenant=os.getenv("CHROMA_TENANT"),
                database=os.getenv("CHROMA_DATABASE"),
            )
        return cls._client

    @classmethod
    def get_collection(cls):
        if cls._collection is None:
            client = cls.get_client()
            cls._collection = client.get_or_create_collection(name="documents")
        return cls._collection

    @classmethod
    def add_documents(cls, ids, documents, metadatas):
        collection = cls.get_collection()
        collection.add(documents=documents, ids=ids, metadatas=metadatas)
