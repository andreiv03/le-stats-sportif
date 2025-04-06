"""
Route for restarting the thread pool after a graceful shutdown.

This module defines the `/api/restart` endpoint. It checks whether the thread
pool has been shut down, and if so, it reinstantiates it, allowing background
jobs to be submitted again.
"""

from flask import Blueprint, current_app, jsonify
from app.task_runner import ThreadPool

restart_bp = Blueprint("restart", __name__)


@restart_bp.route("/api/restart", methods=["GET"])
def restart_request():
    """
    Handles GET requests to restart the background thread pool.

    Returns:
        JSON response:
            - {"status": "restarted"} if the pool was previously shut down and has been restarted.
            - {"status": "running"} if the pool is already active.
    """

    if current_app.threadpool.shutdown_event.is_set():
        current_app.threadpool = ThreadPool()
        return jsonify({"status": "restarted"})

    return jsonify({"status": "running"})
