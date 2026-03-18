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
    conversation_state: str = "IDLE"

class SuggestionRequest(BaseModel):
    text: str

def ensure_string(val):
    """Recursively ensures we return a string, not a dict/object for React."""
    if isinstance(val, dict):
        # Prefer 'answer' or 'question' keys if they exist in the nested dict
        return ensure_string(val.get("answer") or val.get("question") or val.get("follow_up") or str(val))
    return str(val) if val is not None else ""

@app.post("/query")
async def query_endpoint(request: QueryRequest):
    query = request.query
    state = request.conversation_state
    category = route_query(query)
    
    answer = ""
    follow_up = None 
    new_state = "IDLE"
    
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
        answer = ensure_string(answer)
        new_state = "IDLE" # Data queries are usually one-off
    elif category == "INTERACTIVE" or state == "SYMPTOM_CHECK":
        if "yes" in query.lower() or "no" in query.lower():
            disease_name = query.split("for")[-1].strip().replace(".", "")
            if not disease_name: disease_name = "your condition"
            
            base_answer = f"I understand. It's important to monitor those symptoms closely." if "yes" in query.lower() else "I'm glad to hear that you aren't experiencing those specific symptoms."
            answer = f"{base_answer} You can now ask anything further about your records or other conditions here."
            
            # Reset to IDLE so the user can type a fresh question without buttons
            follow_up = None
            new_state = "IDLE"
        else:
            answer = "I understand. Is there anything else you would like to know about your medical records or other conditions?"
            new_state = "IDLE"
        
        answer = ensure_string(answer)
    else:
        # SEMANTIC Routing (Default / Initial Question)
        context_chunks = search_similar(query, top_k=5)
        llm_res = generate_answer(query, context_chunks)
        
        answer = ensure_string(llm_res.get("answer"))
        disease = ensure_string(llm_res.get("disease", "General"))
        question = ensure_string(llm_res.get("follow_up"))
        
        follow_up = {"disease": disease, "question": question}
        new_state = "SYMPTOM_CHECK"
        
    return {
        "query": query,
        "answer": answer,
        "follow_up": follow_up,
        "new_state": new_state,
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
