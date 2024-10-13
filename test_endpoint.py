# import requests
# import json


# def test_api():
#     base_url = "http://localhost:8090/"
#     headers = {"Content-Type": "application/json"}
#     timeout = 10  # 10 seconds timeout

#     try:
#         # Test post_query
#         chat_completion_request = {
#             "messages": [
#                 {"role": "user", "content": "What is the least common type of dog?"}
#             ],
#             "model": "gpt-3.5-turbo",  # or whatever model you're using
#             "max_tokens": 2048,
#             "stream": False
#         }
#         response = requests.post(
#             f"{base_url}/chat/completions",
#             headers=headers,
#             json=chat_completion_request,
#             timeout=timeout
#         )

#         if response.status_code == 200:
#             print("Chat Completion - Success!")
#             print("Response:", response.json())
#         else:
#             print("Chat Completion - Error:", response.status_code)
#             print("Response:", response.text)

#         # Simulate answer generation (this would be done by the Continue frontend)
#         answer = "The capital of France is Paris."

#         # Test store_answer
#         data = {
#             "query": {"query": "What is the capital of France?"},
#             "answer": {"answer": answer},
#         }
#         response = requests.post(
#             f"{base_url}/store_answer", headers=headers, json=data, timeout=timeout
#         )

#         if response.status_code == 200:
#             print("Store Answer - Success!")
#             print("Response:", response.json())
#         else:
#             print("Store Answer - Error:", response.status_code)
#             print("Response:", response.text)

#     except requests.exceptions.RequestException as e:
#         print(f"An error occurred: {e}")


# if __name__ == "__main__":
#     test_api()



import requests
import json


def test_api():
    url = "http://localhost:8090/api/post_query"
    data = {"query": "least common dog breeds 2024"}
    
    response = requests.post(url, json=data, stream=True)
    
    if response.status_code == 200:
        print("Request successful!")
        for line in response.iter_lines():
            if line:
                try:
                    json_response = json.loads(line.decode('utf-8'))
                    if 'error' in json_response:
                        print("Error:", json_response['error'])
                    elif 'end' in json_response and json_response['end']:
                        print("End of stream")
                    else:
                        print("Response part:", json_response)
                except json.JSONDecodeError:
                    print("Failed to decode JSON:", line)
    else:
        print(f"Request failed with status code: {response.status_code}")
        print("Response:", response.text)

if __name__ == "__main__":
    test_api()
