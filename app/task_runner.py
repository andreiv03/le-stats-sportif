"""
Thread-based asynchronous job execution for background task processing.

This module defines:
- ThreadPool: A controller that manages a pool of background TaskRunner threads.
- TaskRunner: A daemon thread responsible for fetching and executing submitted tasks.

Each task is handled without blocking the main Flask server process. Results are saved to disk.
"""

import json
import os
from threading import Thread, Event
from queue import Queue, Empty
from app.utils import extract_job_id


class ThreadPool:
    """
    Manages a pool of TaskRunner threads for concurrent job execution.

    Creates and manages a thread-safe task queue and worker threads to offload
    computation-heavy or time-consuming operations from the main Flask thread.
    """

    def __init__(self):
        self.num_threads = int(os.getenv("TP_NUM_OF_THREADS", os.cpu_count() or 1))
        self.tasks_queue = Queue()
        self.task_runners = []
        self.shutdown_event = Event()
        self.job_counter = 1

        for _ in range(self.num_threads):
            task_runner = TaskRunner(self.tasks_queue, self.shutdown_event)
            task_runner.daemon = True
            task_runner.start()
            self.task_runners.append(task_runner)

    def enqueue(self, task, logger):
        """
        Adds a new task to the processing queue.

        Args:
            task (dict): A dictionary with keys:
                - job_id (str): Unique job identifier.
                - handler (callable): Function to execute in background.
                - args (dict): Arguments passed to the handler.
        """

        if self.shutdown_event.is_set():
            raise RuntimeError("ThreadPool is shutting down.")

        logger.info('Enqueuing task with job ID: "%s"', self.job_counter)

        self.tasks_queue.put(task)
        self.job_counter += 1

    def shutdown(self):
        """Signals all threads to shut down and blocks until they finish."""

        self.shutdown_event.set()
        for task_runner in self.task_runners:
            task_runner.join()


class TaskRunner(Thread):
    """
    Worker thread that retrieves and processes tasks from a shared queue.

    Continuously polls the task queue and executes incoming jobs using the specified handler.
    The result is saved to disk under a file named after the job ID.
    """

    def __init__(self, tasks_queue, shutdown_event):
        super().__init__()
        self.tasks_queue = tasks_queue
        self.shutdown_event = shutdown_event
        self.running = False
        self.current_job_id = None

    def run(self):
        """
        Main loop that processes tasks from the queue.

        Tasks are pulled with a timeout to allow periodic shutdown checks.
        Results are saved to disk after execution.
        """

        while not self.shutdown_event.is_set():
            if self.tasks_queue.empty():
                continue

            try:
                task = self.tasks_queue.get(timeout=1)

                self.running = True
                self.current_job_id = task["job_id"]

                logger = task["logger"]
                job_id = task["job_id"]
                handler = task["handler"]
                args = task["args"]

                job_id_int = extract_job_id(job_id)
                logger.info('Processing task with job ID: "%s"', job_id_int)
                result = handler(args)

                self._save_result(job_id, result)
                logger.info('Task with job ID "%s" saved successfully', job_id_int)

            except Empty:
                continue

            finally:
                self.running = False
                self.current_job_id = None

    def _save_result(self, job_id, result):
        """
        Saves the result of a completed task to a JSON file.

        Args:
            job_id (str): Identifier used to name the result file.
            result (Any): Result object returned by the handler. Must be JSON-serializable.
        """

        os.makedirs("results", exist_ok=True)
        file_path = os.path.join("results", f"{job_id}.json")

        if hasattr(result, "to_dict"):
            result = result.to_dict()

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(result, file, indent=2)
