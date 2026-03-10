import os
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
from langchain_ollama import OllamaEmbeddings
from config import Config
from document_processor import Document

class VectorStore:
    def __init__(self,
                 collection_name: str = None,
                 persist_directory: str = None,
                 embedding_model: str = None):
        self.collection_name = collection_name or Config.COLLECTION_NAME
        self.persist_directory = persist_directory or Config.CHROMA_DB_DIR
        self.embedding_model_name = embedding_model or Config.EMBEDDING_MODEL
        
        self.embedding_model = OllamaEmbeddings(model=self.embedding_model_name)
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
    
    def generate_embeddings(self, texts):
        return self.embedding_model.embed_documents(texts)

    def store_to_chromadb(self, documents, embeddings, metadatas):
        if not documents:
            return

        ids = [f"doc_{self.collection.count() + i}" for i in range(len(documents))]
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
    
    def generate_query_embedding(self, query):
        return self.embedding_model.embed_query(query)

    def retrieve_from_chromadb(self, query_embedding, k=None):
        k = k or Config.MAX_SEARCH_RESULTS
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )
        
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else None,
                    'id': results['ids'][0][i] if results['ids'] else None
                })
        
        return formatted_results
    
    def delete_all_documents(self):
        ids = self.collection.get(include=[])['ids']
        if ids:
            self.collection.delete(ids=ids)
            print(f"Deleted {len(ids)} documents from ChromaDB")
        else:
            print("No documents to delete")
    
    def get_collection_stats(self):
        return {
            'name': self.collection_name,
            'count': self.collection.count(),
            'persist_directory': self.persist_directory,
            'embedding_model': self.embedding_model_name
        }