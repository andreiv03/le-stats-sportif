"""
Route for retrieving asynchronous job results from disk.

This module defines the `/api/get_results/<job_id>` endpoint, which reads
completed task results from JSON files saved by background workers.
"""

import json
import os
from json import JSONDecodeError
from flask import Blueprint, current_app, jsonify

from app.utils import extract_job_id

get_results_bp = Blueprint("get_results", __name__)


@get_results_bp.route("/api/get_results/<job_id>", methods=["GET"])
def get_results_request(job_id):
    """
    Retrieves the result of a previously submitted job.

    Args:
        job_id (str): The full job ID string, e.g., "job_id_5".

    Returns:
        JSON response indicating:
            - status: "done" with result data if ready
            - status: "running" if job still processing
            - status: "error" for invalid or failed jobs
    """

    logger = current_app.logger
    job_id = extract_job_id(job_id)

    if job_id is None or not 0 < job_id < current_app.threadpool.job_counter:
        logger.info('Invalid job ID "%s" in request', job_id)
        return jsonify({"status": "error", "reason": "Invalid job_id"}), 400

    file_path = os.path.join("results", f"job_id_{job_id}.json")

    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            return jsonify({"status": "done", "data": data})

        except JSONDecodeError:
            logger.error('Failed to decode JSON for job ID "%s"', job_id)

    is_running = any(
        runner.running and runner.current_job_id == f"job_id_{job_id}"
        for runner in current_app.threadpool.task_runners
    )

    if is_running:
        return jsonify({"status": "running"})

    return jsonify({"status": "error"}), 400
