import os
import chromadb
import pandas as pd
from sentence_transformers import SentenceTransformer

import sys
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from config import Config

# Paths
DB_PATH = os.path.join('backend', Config.CHROMA_DB_DIR)
CSV_PATH = Config.CSV_PATH
COLLECTION_NAME = Config.COLLECTION_NAME
EMBEDDING_MODEL = Config.EMBEDDING_MODEL

print(f"--- ChromaDB Search ---")
try:
    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_collection(name=COLLECTION_NAME)
    print(f"Total records in DB: {collection.count()}")

    # Search for "Flu"
    model = SentenceTransformer(EMBEDDING_MODEL)
    query_vec = model.encode("Flu").tolist()
    results = collection.query(query_embeddings=[query_vec], n_results=5)
    
    print("\nTop 5 retrieved chunks for 'Flu':")
    for i, doc in enumerate(results['documents'][0]):
        print(f"{i+1}: {doc[:200]}...")
except Exception as e:
    print(f"ChromaDB Error: {e}")

print(f"\n--- CSV Search ---")
if os.path.exists(CSV_PATH):
    try:
        df = pd.read_csv(CSV_PATH)
        print(f"Total rows in CSV: {len(df)}")
        
        # Check for 'Flu' in any column
        found = df[df.apply(lambda row: row.astype(str).str.contains('Flu', case=False).any(), axis=1)]
        print(f"Rows matching 'Flu': {len(found)}")
        if len(found) > 0:
            print("First match:")
            print(found.iloc[0])
            
        # List unique medical conditions
        if 'disease' in df.columns:
            print("\nSample unique medical conditions:")
            print(df['disease'].unique()[:10])
    except Exception as e:
        print(f"CSV Error: {e}")
else:
    print(f"CSV not found at {CSV_PATH}")
