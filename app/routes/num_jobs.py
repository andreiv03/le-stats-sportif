"""
Route for retrieving the number of currently running background jobs.

This module defines the `/api/num_jobs` endpoint, which inspects the thread pool
to count how many jobs are actively being processed.
"""

from flask import Blueprint, current_app, jsonify

num_jobs_bp = Blueprint("num_jobs", __name__)


@num_jobs_bp.route("/api/num_jobs", methods=["GET"])
def num_jobs_request():
    """
    Returns the number of background jobs that are still running.

    Scans the task runners in the thread pool and counts those that
    are actively processing a job.

    Returns:
        flask.Response: JSON response with the count under "running_jobs".
    """

    running_count = sum(
        1
        for runner in current_app.threadpool.task_runners
        if runner.running and runner.current_job_id is not None
    )

    logger = current_app.logger
    logger.info('Number of running jobs: "%s"', running_count)

    return jsonify({"status": "done", "num_jobs": running_count})
