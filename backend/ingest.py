import pandas as pd
import os
import shutil
import chromadb
import kagglehub
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from config import Config

# 1. Configuration
DB_PATH = Config.CHROMA_DB_DIR
COLLECTION_NAME = Config.COLLECTION_NAME

print("Loading Embedding Model...")
# Using a fast, standard, local embedding model
embedding_model = SentenceTransformer(Config.EMBEDDING_MODEL)

def ingest_data():
    print("Downloading Healthcare Dataset via kagglehub...")
    path = kagglehub.dataset_download("prasad22/healthcare-dataset")
    csv_file_path = os.path.join(path, "healthcare_dataset.csv")

    if not os.path.exists(csv_file_path):
        print(f"Error: Could not find dataset at {csv_file_path}")
        return

    print(f"Reading CSV Data from {csv_file_path}...")
    df = pd.read_csv(csv_file_path)
    
    # df = df.head(1000) # Optional: uncomment to process a subset for quick testing

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
    
    # Wipe the old collection to remove previous data (restaurant reviews)
    try:
        client.delete_collection(name=COLLECTION_NAME)
        print("Cleared old ChromaDB collection.")
    except Exception:
        pass
    
    # Create the collection
    collection = client.create_collection(name=COLLECTION_NAME)

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
