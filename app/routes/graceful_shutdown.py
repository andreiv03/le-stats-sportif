"""
Graceful shutdown endpoint for the background task thread pool.

This module defines the `/api/graceful_shutdown` endpoint, which triggers a shutdown
of all worker threads used for asynchronous task processing. The shutdown occurs in
a non-blocking manner, and the endpoint returns whether background jobs are still running.
"""

from threading import Thread
from flask import Blueprint, current_app, jsonify

graceful_shutdown_bp = Blueprint("graceful_shutdown", __name__)


@graceful_shutdown_bp.route("/api/graceful_shutdown", methods=["GET"])
def graceful_shutdown_request():
    """
    Handles GET requests to gracefully shut down the thread pool.

    Spawns a background thread to shut down all task runners and immediately responds
    with the current execution status.

    Returns:
        flask.Response: JSON object indicating task pool status:
            - {"status": "running"}: if any task is still executing or queue is not empty.
            - {"status": "done"}: if all tasks are finished and queue is empty.
    """

    Thread(target=current_app.threadpool.shutdown, daemon=True).start()
    any_active = any(runner.running for runner in current_app.threadpool.task_runners)

    logger = current_app.logger
    logger.info(
        "Graceful shutdown initiated. Running tasks: %s",
        any_active,
    )

    if not current_app.threadpool.tasks_queue.empty() or any_active:
        return jsonify({"status": "running"})

    return jsonify({"status": "done"})
