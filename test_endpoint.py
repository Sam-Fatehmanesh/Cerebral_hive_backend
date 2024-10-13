import requests
import json


def test_api():
    base_url = "http://localhost:8090/"
    headers = {"Content-Type": "application/json"}
    timeout = 10  # 10 seconds timeout

    try:
        # Test post_query
        query = {"query": "What is the least common type of dog?"}
        response = requests.post(
            f"{base_url}/completions",
            headers=headers,
            json=query,
            timeout=timeout,
            stream=True,
        )

        if response.status_code == 200:
            print("Get Context - Success!")
            print("Response:", response.json())
        else:
            print("Get Context - Error:", response.status_code)
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
