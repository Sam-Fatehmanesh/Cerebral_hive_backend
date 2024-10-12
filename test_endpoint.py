import requests
import json

def test_api():
    base_url = "http://localhost:8000/api"
    headers = {"Content-Type": "application/json"}
    
    # Test get_context
    query = {"query": "What is the capital of France?"}
    response = requests.post(f"{base_url}/get_context", headers=headers, data=json.dumps(query))
    
    if response.status_code == 200:
        print("Get Context - Success!")
        context = response.json()["context"]
        print("Context:", context)
    else:
        print("Get Context - Error:", response.status_code)
        print("Response:", response.text)
    
    # Simulate answer generation (this would be done by the Continue frontend)
    answer = "The capital of France is Paris."
    
    # Test store_answer
    data = {
        "query": query["query"],
        "answer": {"answer": answer}
    }
    response = requests.post(f"{base_url}/store_answer", headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        print("Store Answer - Success!")
        print("Response:", response.json())
    else:
        print("Store Answer - Error:", response.status_code)
        print("Response:", response.text)

if __name__ == "__main__":
    test_api()