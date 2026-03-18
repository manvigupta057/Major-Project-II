import re
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"

def route_query(query: str) -> str:
    """
    Categorizes the query into DATA or SEMANTIC.
    Uses rule-based detection first, then LLM refinement.
    """
    query_lower = query.lower()
    
    # Interactive Check (Yes/No buttons)
    if "yes, i am experiencing" in query_lower or "no, i don't have" in query_lower:
        return "INTERACTIVE"

    # Improved Rule-based detection
    data_keywords = [
        "how many", "count", "average", "most", "highest", 
        "lowest", "top", "least", "maximum", "minimum", "common",
        "total", "sum", "percentage"
    ]
    
    if any(keyword in query_lower for keyword in data_keywords):
        return "DATA"

    # LLM Refinement for ambiguous queries
    prompt = f"""Analyze this healthcare query: "{query}"
    
    Classify into:
    - DATA: If it requires calculation, statistics, counts, or finding a specific record attribute based on quantitative logic.
    - SEMANTIC: If it asks for medical knowledge, descriptions, instructions, or qualitative information.
    
    Example DATA: "Which condition is most common?", "How many patients?"
    Example SEMANTIC: "What are symptoms of cancer?", "Who treated Bobby Jackson?"
    
    Return ONLY 'DATA' or 'SEMANTIC'.
    Classification:"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        result = response.choices[0].message.content.strip().upper()
        return "DATA" if "DATA" in result else "SEMANTIC"
    except:
        return "SEMANTIC" # Default fallback

def parse_data_intent(query: str):
    """
    Extracts function name and parameters for the Data Engine.
    """
    prompt = f"""The user asked: "{query}"
    
    Map this to one of these functions:
    1. count_condition(condition: str)
    2. most_common_condition()
    3. get_total_patients()

    Return a JSON string like:
    {{"function": "name", "params": {{"param_name": "value"}}}}
    If no condition is mentioned, params should be empty.
    
    JSON:"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" },
            temperature=0.0
        )
        import json
        return json.loads(response.choices[0].message.content)
    except:
        return {"function": "unknown", "params": {}}
