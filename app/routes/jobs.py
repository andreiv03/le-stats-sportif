"""
Route for listing all asynchronous job statuses.

This module defines the `/api/jobs` endpoint. It returns a list of all known
jobs with their status (`done` or `running`), sorted by job ID.
"""

import os
import re
from flask import Blueprint, current_app, jsonify

jobs_bp = Blueprint("jobs", __name__)


@jobs_bp.route("/api/jobs", methods=["GET"])
def jobs_request():
    """
    Returns the status of all background jobs.

    Jobs are collected from:
    - the `results/` directory (for completed jobs),
    - the active task runners (for currently running jobs).

    The response is a list of dictionaries in the form:
        [
            { "job_id_1": "done" },
            { "job_id_2": "running" },
            ...
        ]

    Returns:
        flask.Response: JSON response with overall status and list of job statuses.
    """

    done = {
        filename.replace(".json", ""): "done"
        for filename in os.listdir("results")
        if filename.startswith("job_id_") and filename.endswith(".json")
    }

    running = {
        runner.current_job_id: "running"
        for runner in current_app.threadpool.task_runners
        if runner.running and runner.current_job_id is not None
    }

    all_jobs = {**done, **running}
    sorted_jobs = sorted(
        all_jobs.items(), key=lambda item: int(re.search(r"\d+", item[0]).group())
    )

    logger = current_app.logger
    logger.info('Job statuses: "%s"', sorted_jobs)

    data = [{job_id: status} for job_id, status in sorted_jobs]
    return jsonify({"status": "done", "data": data})
