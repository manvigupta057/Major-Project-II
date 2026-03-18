import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"  # Fast and reliable Groq model


def generate_answer(query: str, context_chunks: list[str]) -> dict:
    """
    Takes user question + retrieved dataset chunks,
    sends to Groq LLM as an Expert Doctor, 
    returns a JSON object with answer and a follow-up question.
    """
    import json
    context = "\n\n".join(context_chunks)

    prompt = f"""You are an Expert Medical Doctor and Data Analyst. Use the provided hospital records to assist the user.
    
    TASK:
    1. Answer the user's question accurately based ONLY on the context.
    2. Identify the primary disease discussed.
    3. Propose ONE short, friendly follow-up question to check the user's symptoms related to that disease.
    
    RESPONSE FORMAT (Strict JSON):
    {{
        "answer": "Your detailed answer here...",
        "disease": "Primary disease name",
        "follow_up": "Your single symptom-check question here"
    }}

    Context (Hospital Records):
    {context}

    User Question: {query}
    """

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {
            "answer": "I encountered an error processing the medical records.",
            "disease": "General",
            "follow_up": "How can I help you further?"
        }


def generate_suggestions(partial_query: str) -> list[str]:
    """
    Takes partially typed text (min 3 words),
    returns 5 relevant healthcare keyword suggestions.
    """
    prompt = f"""The user is typing a healthcare-related query and has typed: "{partial_query}"
    
    Suggest exactly 5 short, relevant healthcare keyword phrases to complete or extend this query.
    Return only the 5 suggestions as a numbered list, nothing else."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )

    raw = response.choices[0].message.content
    # Parse numbered list into clean array
    lines = [line.strip() for line in raw.strip().split("\n") if line.strip()]
    suggestions = [line.split(". ", 1)[-1] for line in lines if line]
    return suggestions[:5]

