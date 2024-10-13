import requests
import json


def test_api():
    base_url = "http://localhost:8090/"
    # base_url = "https://cerebral-hive-backend.onrender.com"
    headers = {"Content-Type": "application/json"}
    timeout = 10  # 10 seconds timeout

    try:
        # Test post_query
        chat_completion_request = {
            "messages": [
                {"role": "user", "content": "What is the least common type of dog?"}
            ],
            "model": "gpt-3.5-turbo",  # or whatever model you're using
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

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    test_api()
