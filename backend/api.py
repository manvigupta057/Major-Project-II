from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from vector_store import search_similar
from llm_interface import generate_answer, generate_suggestions

app = FastAPI(title="Healthcare Chatbot API")

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class QueryRequest(BaseModel):
    query: str

class SuggestionRequest(BaseModel):
    text: str


@app.get("/health")
def health_check():
    return {"status": "Backend is running!"}


@app.post("/query")
def query_endpoint(request: QueryRequest):
    """Takes user question, searches dataset, returns AI answer."""
    context_chunks = search_similar(request.query, top_k=5)
    answer = generate_answer(request.query, context_chunks)
    return {"query": request.query, "answer": answer}


@app.post("/suggestions")
def suggestions_endpoint(request: SuggestionRequest):
    """Returns 5 keyword suggestions when user types 3+ words."""
    words = request.text.strip().split()
    if len(words) < 3:
        return {"suggestions": [], "message": "Type at least 3 words"}
    suggestions = generate_suggestions(request.text)
    return {"suggestions": suggestions}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
