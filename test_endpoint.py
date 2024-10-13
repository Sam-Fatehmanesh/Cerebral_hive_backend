import requests
import json
import sys
import os

# Add the parent directory to the Python path to import from main.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import print_vector_db_contents


def test_api():
    base_url = "https://cerebral-hive-backend.onrender.com"
    # base_url = "http://localhost:8090"
    headers = {"Content-Type": "application/json"}
    timeout = 10  # 10 seconds timeout
    query = "Consider the paths of length $16$ that follow the lines from the lower left corner to the upper right corner on an $8\times 8$ grid. Find the number of such paths that change direction exactly four times, as in the examples shown below. "

    try:
        # Test post_query
        chat_completion_request = {
            "messages": [
                {"role": "user", "content": query}
            ],
            "model": "gpt-4o",  # or whatever model you're using
            "max_tokens": 2048,
            "stream": False
        }
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=chat_completion_request,
            timeout=timeout
        )

        if response.status_code == 200:
            print("Chat Completion - Success!")
            print("Response:", response.json())
        else:
            print("Chat Completion - Error:", response.status_code)
            print("Response:", response.text)

        '''

        # Simulate answer generation (this would be done by the Continue frontend)
        answer = "The capital of France is Paris."

        # Test store_answer
        data = {
            "query": {"query": "What is the capital of France?"},
            "answer": {"answer": answer},
        }
        response = requests.post(
            f"{base_url}/store_answer", headers=headers, json=data, timeout=timeout
        )

        if response.status_code == 200:
            print("Store Answer - Success!")
            print("Response:", response.json())
        else:
            print("Store Answer - Error:", response.status_code)
            print("Response:", response.text)
        '''

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

    # Print the contents of the vector database
    print("\nPrinting Vector Database Contents:")
    print_vector_db_contents()


if __name__ == "__main__":
    test_api()
