import pandas as pd
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq client for code generation
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"

# Load the dataset once
CSV_PATH = r"c:\Users\manvi\Downloads\archive\healthcare_dataset.csv"
if os.path.exists(CSV_PATH):
    df = pd.read_csv(CSV_PATH)
    print(f"Pandas Engine: Loaded {len(df)} records.")
else:
    df = pd.DataFrame()
    print("Warning: CSV not found for Pandas Engine.")

def execute_data_query(query: str) -> str:
    """
    Translates natural language to Pandas code and executes it.
    """
    if df.empty:
        return "Dataset not loaded."

    columns = list(df.columns)
    
    prompt = f"""You are a Python expert focused on Pandas.
    The user has a dataset 'df' with these columns: {columns}
    
    Translate the user's natural language question into a SINGLE LINE of Python code that calculates the answer from 'df'.
    
    Rules:
    1. Respond ONLY with the code string. No explanations.
    2. Example output for "Total count": len(df)
    3. Example output for "Average age": df['Age'].mean()
    4. Example output for "Most common gender": df['Gender'].mode()[0]
    
    Question: {query}
    Code:"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )

    code = response.choices[0].message.content.strip()
    
    # Safety check: basic filter
    safe_keywords = ["df", "len", "mean", "count", "sum", "min", "max", "mode", "iloc", "loc"]
    if not any(k in code for k in safe_keywords) or "os" in code or "sys" in code:
        return f"Query blocked for safety or invalid: {code}"

    try:
        # Execute the generated code on the 'df' variable
        result = eval(code)
        return str(result)
    except Exception as e:
        return f"Error executing query logic: {e} (Code generated: {code})"
