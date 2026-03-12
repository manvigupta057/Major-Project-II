from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
import os

from vector_store import search_similar
from llm_interface import generate_answer, generate_suggestions
from auth import router as auth_router, get_current_user

app = FastAPI(title="Healthcare Chatbot API")

# Middleware for OAuth Sessions
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Auth Routes
app.include_router(auth_router)

# Request models
class QueryRequest(BaseModel):
    query: str

class SuggestionRequest(BaseModel):
    text: str

@app.get("/health")
def health_check():
    return {"status": "Backend is running!"}

@app.post("/query")
def query_endpoint(request: QueryRequest, current_user: str = Depends(get_current_user)):
    """Takes user question, searches dataset, returns AI answer. (Protected)"""
    context_chunks = search_similar(request.query, top_k=5)
    answer = generate_answer(request.query, context_chunks)
    return {"query": request.query, "answer": answer, "user": current_user}

@app.post("/suggestions")
def suggestions_endpoint(request: SuggestionRequest, current_user: str = Depends(get_current_user)):
    """Returns 5 keyword suggestions when user types 3+ words. (Protected)"""
    words = request.text.strip().split()
    if len(words) < 3:
        return {"suggestions": [], "message": "Type at least 3 words"}
    suggestions = generate_suggestions(request.text)
    return {"suggestions": suggestions}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
