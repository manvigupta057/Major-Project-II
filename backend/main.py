from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
import os

from vector_store import search_similar
from llm_interface import generate_answer, generate_suggestions
from auth import router as auth_router
from query_router import route_query, parse_data_intent
from data_engine import data_engine

app = FastAPI(title="Healthcare Chatbot API (v2)")

# Middleware
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "fallback-secret"))
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

class QueryRequest(BaseModel):
    query: str

class SuggestionRequest(BaseModel):
    text: str

@app.post("/query")
async def query_endpoint(request: QueryRequest):
    query = request.query
    category = route_query(query)
    
    answer = None
    
    if category == "DATA":
        intent = parse_data_intent(query)
        func_name = intent.get("function")
        params = intent.get("params", {})
        
        try:
            if func_name == "count_condition":
                answer = data_engine.count_condition(params.get("condition", ""))
            elif func_name == "most_common_condition":
                answer = data_engine.most_common_condition()
            elif func_name == "get_total_patients":
                answer = data_engine.get_total_patients()
            else:
                answer = "I'm sorry, I couldn't perform that specific data calculation."
        except Exception as e:
            answer = f"Error performing calculation: {str(e)}"
    else:
        # SEMANTIC Routing
        context_chunks = search_similar(query, top_k=5)
        answer = generate_answer(query, context_chunks)
        
    return {
        "query": query,
        "answer": answer,
        "category": category,
        "user": "Demo User"
    }

@app.post("/suggestions")
async def suggestions_endpoint(request: SuggestionRequest):
    """Returns 5 keyword suggestions when user types 3+ words."""
    words = request.text.strip().split()
    if len(words) < 3:
        return {"suggestions": [], "message": "Type at least 3 words"}
    suggestions = generate_suggestions(request.text)
    return {"suggestions": suggestions}

@app.get("/health")
def health():
    return {"status": "v2 online"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
