import os
import shutil
import time  
from document_processor import DocumentProcessor
from vector_store import VectorStore
from llm_interface import LLMInterface

class Config:
    pass

class RAGApplication:
    def __init__(self, selected_model=None, provider="ollama"):
        print("setting up...")
        self.document_processor = DocumentProcessor()
        self.vector_store = VectorStore()
        self.llm_interface = LLMInterface(model_name=selected_model, provider=provider)
        print(f"done. (Using model: {self.llm_interface.model_name}, Provider: {provider})")
    
    def process_data(self, file_path=None, **kwargs):
        print("\n--- Starting processing ---")
        raw_data = []
        if file_path:
            print(f"Loading file: {file_path}")
            start_time = time.time()
            raw_data = self.document_processor.load_file(file_path, **kwargs)
            end_time = time.time()
            print(f"   File loaded in {end_time - start_time:.2f} seconds.") 
             
        if not raw_data:
            print("No data loaded.")
            return

        print("Creating chunks...")
        start_time = time.time()
        all_documents = []
        for item in raw_data:
            chunks = self.document_processor.create_chunks(item['content'], item['metadata'])
            all_documents.extend(chunks)
        end_time = time.time()
        
        print(f"   Created {len(all_documents)} chunks in {end_time - start_time:.2f} seconds.")
        
        if not all_documents:
            return

        print("Generating vector embeddings...")
        start_time = time.time()
        texts = [doc.content for doc in all_documents]
        metadatas = [{k: str(v) for k, v in doc.metadata.items()} for doc in all_documents]
        
        embeddings = self.vector_store.generate_embeddings(texts)
        end_time = time.time()
        print(f"   Embeddings generated in {end_time - start_time:.2f} seconds.")

        print("Storing to ChromaDB...")
        start_time = time.time()
        self.vector_store.store_to_chromadb(texts, embeddings, metadatas)
        end_time = time.time()
        
        stats = self.vector_store.get_collection_stats()
        print(f"   Data stored in {end_time - start_time:.2f} seconds. Current DB Count: {stats['count']}")
            
    def query_loop(self):
        print("\n--- RAG Query Loop ---")
        print("Enter your query (or 'quit'/'exit' to stop).")
        
        while True:
            query = input("\nQuery: ").strip()
            
            if query.lower() in ['quit', 'exit']:
                print("Exiting...")
                break
            
            if not query:
                continue
            
            print("Generating query vector...")
            query_embedding = self.vector_store.generate_query_embedding(query)
            
            print("Retrieving from ChromaDB...")
            start_time = time.time()
            results = self.vector_store.retrieve_from_chromadb(query_embedding)
            end_time = time.time()
            
            threshold = 1.5
            relevant_results = [r for r in results if r['distance'] < threshold]
            
            print(f"   Found {len(relevant_results)} relevant chunks in {end_time - start_time:.4f} seconds.")
            
            if relevant_results:
                context_parts = []
                for r in relevant_results:
                    filtered_metadata = {
                        k: v for k, v in r['metadata'].items() 
                        if k not in ['chunk_start', 'chunk_end', 'row_index', 'source']
                    }
                    meta_str = ", ".join([f"{k}: {v}" for k, v in filtered_metadata.items()])
                    part = f"Context:\n{r['content']}\nMetadata: {meta_str}"
                    context_parts.append(part)
                
                context_text = "\n\n".join(context_parts)
                
                print("Generating answer with LLM...")
                start_time = time.time()
                answer = self.llm_interface.generate_answer(query, context_text)
                end_time = time.time()
                
                print(f"\n--- Answer ---\n{answer}\n--------------")
                print(f"(Response generated in {end_time - start_time:.2f} seconds)")
            else:
                print("No relevant info found.")

def main():
    if os.path.exists("./chroma_db"):
        print("clearing old db...")
        try:
            shutil.rmtree("./chroma_db")
        except:
            pass

    print("Choose your LLM Model:")
    print("1. llama3.2")
    print("2. llama3.2:1b")
    print("3. Groq")
    choice = input("Enter 1, 2, or 3 : ").strip()
    
    model_choice = "llama3.2"
    provider_choice = "ollama"

    if choice == "2":
        model_choice = "llama3.2:1b"
    elif choice == "3":
        model_choice = "llama-3.3-70b-versatile"
        provider_choice = "groq"

    app = RAGApplication(selected_model=model_choice, provider=provider_choice)
    
    csv_file = "realistic_restaurant_reviews.csv"
    if os.path.exists(csv_file):
        app.process_data(
            file_path=csv_file,
            text_columns=['Title', 'Review'],
            metadata_columns=['Rating', 'Date']
        )
        app.query_loop()
    else:
        print("csv file missing")

if __name__ == "__main__":
    main()