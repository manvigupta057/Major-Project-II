import requests
import json

BASE_URL = "http://localhost:8000"

test_cases = [
    "How many patients have Diabetes?",
    "How many patients have Cancer?",
    "Which medical condition is most common?",
    "Which hospital has the most admissions?",
    "Which doctor treated Bobby Jackson?",
    "What is the average billing amount for Cancer patients?",
    "How many patients are in total?"
]

def run_tests():
    print(f"{'Query':<45} | {'Category':<10} | {'Answer'}")
    print("-" * 80)
    for query in test_cases:
        try:
            response = requests.post(f"{BASE_URL}/query", json={"query": query})
            data = response.json()
            category = data.get("category", "N/A")
            answer = data.get("answer", "N/A")
            print(f"{query:<45} | {category:<10} | {answer}")
        except Exception as e:
            print(f"Error testing '{query}': {e}")

if __name__ == "__main__":
    run_tests()
