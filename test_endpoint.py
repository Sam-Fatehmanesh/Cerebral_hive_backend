import requests
import json

def test_query_api():
    url = "http://localhost:8000/api/query"
    headers = {"Content-Type": "application/json"}
    
    # Test data
    data = {
        "query": "What is the capital of France?",
        "continue_api_key": "your_continue_api_key_here"
    }
    
    # Send POST request
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    # Check response
    if response.status_code == 200:
        print("Success!")
        print("Response:", response.json())
    else:
        print("Error:", response.status_code)
        print("Response:", response.text)

if __name__ == "__main__":
    test_query_api()