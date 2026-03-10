from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os
import uuid
from app import RAGApplication, Config

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_app = RAGApplication(selected_model="llama-3.3-70b-versatile", provider="groq")

class QueryRequest(BaseModel):
    query: str

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        rag_app.vector_store.delete_all_documents()
        upload_dir = "uploads"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        file_path = os.path.join(upload_dir, f"{uuid.uuid4()}_{file.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        kwargs = {}
        if file.filename.endswith('.csv'):
            kwargs = {
                'text_columns': ['Title', 'Review'],
                'metadata_columns': ['Rating', 'Date']
            }
        elif file.filename.endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
            kwargs = {}
        rag_app.process_data(file_path=file_path, **kwargs)
        
        return {"message": "File processed successfully", "filename": file.filename}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
def query_document(request: QueryRequest):
    try:
        query = request.query
        query_embedding = rag_app.vector_store.generate_query_embedding(query)
        results = rag_app.vector_store.retrieve_from_chromadb(query_embedding)
        
        threshold = 1.5
        relevant_results = [r for r in results if r['distance'] < threshold]
        
        if not relevant_results:
            return {"answer": "I couldn't find any relevant information in the uploaded documents."}
        
        context_parts = []
        for r in relevant_results:
            filtered_metadata = {
                k: v for k, v in r['metadata'].items() 
                if k not in ['chunk_start', 'chunk_end', 'row_index']
            }
            meta_str = ", ".join([f"{k}: {v}" for k, v in filtered_metadata.items()])
            part = f"Context:\n{r['content']}\nMetadata: {meta_str}"
            context_parts.append(part)
        
        context_text = "\n\n".join(context_parts)
        
        answer = rag_app.llm_interface.generate_answer(query, context_text)
        return {"answer": answer}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
