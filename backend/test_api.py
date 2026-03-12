import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health Check: {response.json()}")

def test_query(query_text):
    payload = {"query": query_text}
    response = requests.post(f"{BASE_URL}/query", json=payload)
    print(f"Query: {query_text}")
    print(f"Answer: {json.dumps(response.json(), indent=2)}")

def test_suggestions(partial_text):
    payload = {"text": partial_text}
    response = requests.post(f"{BASE_URL}/suggestions", json=payload)
    print(f"Suggestions for: {partial_text}")
    print(f"Result: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    test_health()
    test_query("What is hypertension?")
    test_suggestions("What is the treatment")
