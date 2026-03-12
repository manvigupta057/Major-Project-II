import pandas as pd
import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from config import Config

# 1. Configuration
# Make sure this path is exactly where your CSV is located!
CSV_FILE_PATH = r"c:\Users\manvi\Downloads\archive\healthcare_dataset.csv"
DB_PATH = Config.CHROMA_DB_DIR
COLLECTION_NAME = Config.COLLECTION_NAME

print("Loading Embedding Model...")
# Using a fast, standard, local embedding model
embedding_model = SentenceTransformer(Config.EMBEDDING_MODEL)

def ingest_data():
    if not os.path.exists(CSV_FILE_PATH):
        print(f"Error: Could not find dataset at {CSV_FILE_PATH}")
        return

    print("Reading CSV Data...")
    df = pd.read_csv(CSV_FILE_PATH)
    
    # Optional: If the dataset is huge, you might want to process a subset first for testing
    # df = df.head(1000) 

    documents = []
    metadata = []
    ids = []

    print("Processing Rows into Text Chunks...")
    for index, row in df.iterrows():
        # Convert the row into a readable string format for the vector DB
        row_text = ", ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
        
        documents.append(row_text)
        metadata.append({"row_index": index})
        ids.append(f"doc_{index}")

    print("Initializing ChromaDB...")
    client = chromadb.PersistentClient(path=DB_PATH)
    
    # Create or get the collection
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    print("Generating Embeddings and Storing Data (This might take a while)...")
    # Generate embeddings in batches to prevent memory crashes
    batch_size = 500
    for i in range(0, len(documents), batch_size):
        end_idx = min(i + batch_size, len(documents))
        
        batch_docs = documents[i:end_idx]
        batch_ids = ids[i:end_idx]
        batch_meta = metadata[i:end_idx]
        
        # Create vectors
        embeddings = embedding_model.encode(batch_docs).tolist()
        
        # Add to ChromaDB
        collection.add(
            documents=batch_docs,
            embeddings=embeddings,
            metadatas=batch_meta,
            ids=batch_ids
        )
        print(f"Processed {end_idx}/{len(documents)} rows...")

    print("✅ Ingestion Complete! Data saved to ChromaDB locally.")

if __name__ == "__main__":
    ingest_data()
