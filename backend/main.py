from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
import shutil, os
import easyocr
from fastapi import UploadFile, File

from vector_store import search_similar
from llm_interface import generate_answer, generate_suggestions
from auth import router as auth_router
from query_router import route_query, parse_data_intent
from data_engine import data_engine

app = FastAPI(title="Healthcare Chatbot API (v2)")

reader = easyocr.Reader(['en'])  

@app.post("/upload-receipt")
async def upload_receipt(file: UploadFile = File(...)):
    # Save the uploaded file to a temporary location
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    results = reader.readtext(temp_path, detail=0)
    extracted_text = " ".join(results)   # Fixed: was 'result', should be 'results'
    os.remove(temp_path)  

    return {"extracted_text": extracted_text}

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
    elif state == "SYMPTOM_CHECK":
        if "yes" in query.lower():
            disease_name = query.split("for")[-1].strip().replace(".", "")
            if not disease_name: disease_name = "your condition"
            
            answer = "I understand. It's important to monitor those symptoms closely."
            follow_up = {
                "disease": disease_name,
                "question": f"Would you like to know about the remedies for {disease_name} or would you like to know how can you control these symptoms?"
            }
            new_state = "REMEDY_ASK"
        else:
            answer = "I understand. Is there anything else you would like to know about your medical records or other conditions?"
            new_state = "IDLE"
        answer = ensure_string(answer)
        
    elif state == "REMEDY_ASK":
        if "yes" in query.lower():
            disease_name = query.split("for")[-1].strip().replace(".", "")
            if not disease_name: disease_name = "your condition"
            
            # Perform RAG for remedies, cures, and medications
            search_query = f"Remedies, cures, and medications for {disease_name}"
            context = search_similar(search_query, top_k=4)
            llm_res = generate_answer(f"Provide a combination of remedies, cure, and medication for {disease_name} based on the records.", context)
            
            remedy_text = ensure_string(llm_res.get("answer"))
            answer = f"{remedy_text}"  # Just the remedy text
            follow_up = {
                "disease": disease_name,
                "question": "Are you taking any recent medications for this condition?"
                }
            new_state = "MEDICATION_CHECK"
        else:
            answer = "I understand. Please let me know if you have any other questions."
            new_state = "IDLE"
        answer = ensure_string(answer)

    elif state == "MEDICATION_CHECK":
        if "yes" in query.lower():
            # Instruction for uploading receipt
            answer = "I understand. Please upload your recent medication receipt here (as an image) so I can verify them for you based on your records."
            follow_up = None
            new_state = "IDLE"
        else:
            # Standard closing if no medications
            answer = "I understand. You can now ask anything further about your records or other conditions here."
            follow_up = None
            new_state = "IDLE"
        answer = ensure_string(answer)

    elif category == "INTERACTIVE":
        # Handled by states above, but as a fallback:
        answer = "I'm here to help. Could you please provide more details or ask a question?"
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
