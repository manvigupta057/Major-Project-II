from fastapi.testclient import TestClient
from api import app
from llm_interface import generate_answer
from vector_store import search_similar

client = TestClient(app)

print("--- Testing /query directly with TestClient ---")
response = client.post('/query', json={'query': 'What are the symptoms of heart attack?'})
print("Result STATUS:", response.status_code)
print("Result JSON/TEXT:", response.text)
