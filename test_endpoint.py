import requests
import json

def test_api():
    base_url = "http://localhost:8090/api"
    headers = {"Content-Type": "application/json"}
    timeout = 10  # 10 seconds timeout

    try:
        # Test get_context
        query = {"query": "What is the capital of France?"}
        response = requests.post(f"{base_url}/get_context", headers=headers, json=query, timeout=timeout)
        
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
            "query": {"query": "What is the capital of France?"},
            "answer": {"answer": answer}
        }
        response = requests.post(f"{base_url}/store_answer", headers=headers, json=data, timeout=timeout)
        
        if response.status_code == 200:
            print("Store Answer - Success!")
            print("Response:", response.json())
        else:
            print("Store Answer - Error:", response.status_code)
            print("Response:", response.text)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_api()