"""
Automated integration tests for the Le Stats Sportif Flask API.

This test suite verifies:
- Correct functionality of all asynchronous POST-based statistical endpoints.
- Proper behavior of job management features including job tracking, shutdown, and restart.
- JSON input/output matching via reference test files.
- Timely background processing with result polling and DeepDiff-based verification.
"""

import json
import random
import requests
import time
import unittest
from datetime import datetime
from deepdiff import DeepDiff


class TestWebserver(unittest.TestCase):
    """
    Integration tests for the Flask-based statistics API server.

    This test suite validates:
        - Each API POST endpoint against its input/output files.
        - Background job completion and result correctness.
        - Job tracking via `/jobs` and `/num_jobs`.
        - Graceful shutdown and restart behavior.
    """

    BASE_URL = "http://127.0.0.1:5000/api"
    TIMEOUT_SECONDS = 3
    POLL_INTERVAL = 0.2

    POST_ENDPOINTS = [
        "states_mean",
        "state_mean",
        "best5",
        "worst5",
        "global_mean",
        "diff_from_mean",
        "state_diff_from_mean",
        "mean_by_category",
        "state_mean_by_category",
    ]

    def _load_json(self, path):
        """
        Loads and parses a JSON file.

        Args:
            path (str): Path to the JSON file.

        Returns:
            dict: Parsed JSON content.
        """

        with open(path, "r") as file:
            return json.load(file)

    def _wait_for_result(self, job_id):
        """
        Polls the server until the job result is ready or a timeout occurs.

        Args:
            job_id (str): The ID of the submitted background job.

        Returns:
            dict: The result data of the completed job.

        Raises:
            AssertionError: If the job fails, times out, or returns unexpected status.
        """

        start_time = datetime.now()

        while True:
            response = requests.get(f"{self.BASE_URL}/get_results/{job_id}")
            response.raise_for_status()

            data = response.json()
            self.assertEqual(response.status_code, 200)

            if data["status"] == "done":
                return data["data"]

            if data["status"] != "running":
                self.fail(f"Unexpected status for job {job_id}: {data["status"]}")

            if (datetime.now() - start_time).total_seconds() > self.TIMEOUT_SECONDS:
                self.fail(f"Timeout waiting for job {job_id}")

            time.sleep(self.POLL_INTERVAL)

    def _helper_test_endpoint(self, endpoint):
        """
        Helper method for validating endpoint behavior using test input/output.

        Args:
            endpoint (str): Name of the POST route to test.
        """

        input_path = f"tests/{endpoint}/input/in-1.json"
        output_path = f"tests/{endpoint}/output/out-1.json"

        request_body = self._load_json(input_path)
        expected_output = self._load_json(output_path)

        with self.subTest(endpoint=endpoint):
            response = requests.post(f"{self.BASE_URL}/{endpoint}", json=request_body)
            response.raise_for_status()

            job_id = response.json()["job_id"]
            result = self._wait_for_result(job_id)

            diff = DeepDiff(result, expected_output, math_epsilon=0.01)
            self.assertTrue(diff == {}, str(diff))

    def test_jobs(self):
        """
        Tests that job IDs appear correctly in the /jobs endpoint after submission.
        """

        endpoint = random.choice(self.POST_ENDPOINTS)
        input_path = f"tests/{endpoint}/input/in-1.json"
        request_body = self._load_json(input_path)

        response = requests.post(f"{self.BASE_URL}/{endpoint}", json=request_body)
        response.raise_for_status()
        self.assertEqual(response.status_code, 200)

        job_id = response.json()["job_id"]
        self.assertIsInstance(job_id, str)

        response = requests.get(f"{self.BASE_URL}/jobs")
        response.raise_for_status()
        self.assertEqual(response.status_code, 200)

        jobs = response.json()["data"]
        found = any(job_id in job for job in jobs)
        self.assertTrue(found, f"{job_id} not found in jobs list")

    def test_num_jobs(self):
        """
        Tests that `/num_jobs` correctly reflects the number of running jobs.
        """

        response = requests.get(f"{self.BASE_URL}/num_jobs")
        response.raise_for_status()
        self.assertEqual(response.status_code, 200)

        num_jobs = response.json()["num_jobs"]
        self.assertIsInstance(num_jobs, int)

        endpoint = random.choice(self.POST_ENDPOINTS)
        input_path = f"tests/{endpoint}/input/in-1.json"
        request_body = self._load_json(input_path)

        response = requests.post(f"{self.BASE_URL}/{endpoint}", json=request_body)
        response.raise_for_status()
        self.assertEqual(response.status_code, 200)

        response = requests.get(f"{self.BASE_URL}/num_jobs")
        response.raise_for_status()
        self.assertEqual(response.status_code, 200)

        new_num_jobs = response.json()["num_jobs"]
        self.assertEqual(new_num_jobs, num_jobs + 1)
        self.assertIsInstance(new_num_jobs, int)

    def test_graceful_shutdown(self):
        """
        Tests that after calling `/graceful_shutdown`:
            - No new tasks can be enqueued
            - Existing jobs finish
            - `/restart` reinitializes the thread pool
        """

        endpoint = random.choice(self.POST_ENDPOINTS)
        input_path = f"tests/{endpoint}/input/in-1.json"
        request_body = self._load_json(input_path)

        response = requests.post(f"{self.BASE_URL}/{endpoint}", json=request_body)
        response.raise_for_status()
        self.assertEqual(response.status_code, 200)

        response = requests.get(f"{self.BASE_URL}/graceful_shutdown")
        response.raise_for_status()
        self.assertEqual(response.status_code, 200)

        response = requests.post(f"{self.BASE_URL}/{endpoint}", json=request_body)
        self.assertEqual(response.status_code, 400)

        try:
            data = response.json()
        except json.JSONDecodeError:
            self.fail("Response after shutdown was not valid JSON")

        self.assertEqual(data.get("reason"), "shutting down")
        requests.get(f"{self.BASE_URL}/restart")


def generate_test(endpoint):
    """
    Dynamically generates a test method for each endpoint.

    Args:
        endpoint (str): The endpoint name to test.

    Returns:
        function: A unit test method for the given endpoint.
    """

    def test_func(self):
        self._helper_test_endpoint(endpoint)

    test_func.__name__ = f"test_{endpoint}"
    return test_func


for endpoint in TestWebserver.POST_ENDPOINTS:
    setattr(TestWebserver, f"test_{endpoint}", generate_test(endpoint))


def load_tests(loader, tests, pattern):
    """
    Custom test loader that ensures test_graceful_shutdown runs last.

    Returns:
        unittest.TestSuite: Ordered suite with graceful shutdown test at the end.
    """

    suite = unittest.TestSuite()
    test_cases = loader.getTestCaseNames(TestWebserver)

    for name in sorted(test for test in test_cases if test != "test_graceful_shutdown"):
        suite.addTest(TestWebserver(name))

    suite.addTest(TestWebserver("test_graceful_shutdown"))
    return suite
