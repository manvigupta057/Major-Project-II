import chromadb
from sentence_transformers import SentenceTransformer

from config import Config

# Configuration — must match what we used in ingest.py
DB_PATH = Config.CHROMA_DB_DIR
COLLECTION_NAME = Config.COLLECTION_NAME

# Load the same embedding model
embedding_model = SentenceTransformer(Config.EMBEDDING_MODEL)

# Connect to the ChromaDB we already built
client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_or_create_collection(name=COLLECTION_NAME)


def search_similar(query: str, top_k: int = 5) -> list[str]:
    """
    Takes the user's question, converts it to a vector,
    finds the most similar rows in the healthcare dataset.
    Returns top_k matching text chunks.
    """
    # Convert user query to embedding
    query_embedding = embedding_model.encode(query).tolist()

    # Search ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    # Extract matched documents
    matched_docs = results["documents"][0]
    return matched_docs