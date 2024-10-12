import unittest
import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

class TestContextAPI(unittest.TestCase):
    BASE_URL = "http://localhost:8090/api"
    HEADERS = {"Content-Type": "application/json"}
    TIMEOUT = 10

    def setUp(self):
        # Prepare some test data
        self.test_data = [
            ("What is the capital of France?", "The capital of France is Paris."),
            ("Who wrote Romeo and Juliet?", "William Shakespeare wrote Romeo and Juliet."),
            ("What is the largest planet in our solar system?", "Jupiter is the largest planet in our solar system."),
            ("Who painted the Mona Lisa?", "Leonardo da Vinci painted the Mona Lisa."),
            ("What is the boiling point of water?", "The boiling point of water is 100 degrees Celsius or 212 degrees Fahrenheit at sea level."),
        ]
        
        # Store all test data
        for question, answer in self.test_data:
            self.store_answer(question, answer)
        
        # Wait for indexing
        time.sleep(5)

    def store_answer(self, question, answer):
        data = {
            "query": {"query": question},
            "answer": {"answer": answer}
        }
        response = requests.post(f"{self.BASE_URL}/store_answer", headers=self.HEADERS, json=data, timeout=self.TIMEOUT)
        self.assertEqual(response.status_code, 200)

    def get_context(self, question):
        query = {"query": question}
        response = requests.post(f"{self.BASE_URL}/get_context", headers=self.HEADERS, json=query, timeout=self.TIMEOUT)
        self.assertEqual(response.status_code, 200)
        return response.json()["context"]

    def test_context_retrieval(self):
        for question, answer in self.test_data:
            context = self.get_context(question)
            self.assertIn(answer, context)

    def test_context_length(self):
        context = self.get_context("What is the capital of France?")
        self.assertEqual(len(context), 5)

    def test_repeated_query(self):
        context1 = self.get_context("What is the capital of France?")
        context2 = self.get_context("What is the capital of France?")
        self.assertEqual(context1, context2)

    def test_unrelated_query(self):
        context = self.get_context("What is the price of bitcoin?")
        self.assertFalse(any("Paris" in item for item in context))

    def test_long_query(self):
        long_query = "What is the capital of France? " * 100
        context = self.get_context(long_query)
        self.assertTrue(any("Paris" in item for item in context))

    def test_special_characters(self):
        special_query = "What is the capital of France? #$%^&*()!"
        context = self.get_context(special_query)
        self.assertTrue(any("Paris" in item for item in context))

    def test_concurrent_requests(self):
        def make_request(question):
            return self.get_context(question)

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, question) for question, _ in self.test_data]
            results = [future.result() for future in as_completed(futures)]

        self.assertEqual(len(results), len(self.test_data))
        for context in results:
            self.assertEqual(len(context), 5)

if __name__ == '__main__':
    unittest.main()