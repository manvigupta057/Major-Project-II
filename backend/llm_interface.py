import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"  # Fast and reliable Groq model


def generate_answer(query: str, context_chunks: list[str]) -> str:
    """
    Takes user question + retrieved dataset chunks,
    sends to Groq LLM, returns a grounded answer.
    """
    context = "\n\n".join(context_chunks)

    prompt = f"""You are a helpful healthcare assistant.
Answer the user's question ONLY using the context provided below.
If the answer is not in the context, say "I don't have enough data to answer this."

Context:
{context}

Question: {query}
Answer:"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return response.choices[0].message.content


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