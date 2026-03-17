import requests

BASE_URL = "http://localhost:8000"

def test_query(query: str):
    print(f"\nTesting Query: {query}")
    try:
        response = requests.post(f"{BASE_URL}/query", json={"query": query})
        data = response.json()
        print(f"Category: {data.get('category')}")
        print(f"Answer: {data.get('answer')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test Data Routing
    test_query("How many total patients are in the records?")
    test_query("What is the average age of patients?")
    
    # Test Semantic Routing
    test_query("What are the common treatments for Diabetes?")
    test_query("Tell me about patient hypertension records.")
