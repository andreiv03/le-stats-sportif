"""
General utility functions for asynchronous task handling and other shared operations.

This module provides reusable helper functions for the application, such as
task enqueuing with the Flask thread pool. Additional utilities can be added here
to support common patterns used across route handlers and services.
"""

import re
from flask import current_app, jsonify


def enqueue_task(handler, args):
    """
    Enqueue a background task using the application's thread pool.

    Args:
        handler (Callable): The function to be executed asynchronously.
        args (dict): A dictionary of arguments to be passed to the handler.

    Returns:
        flask.Response: A JSON response containing the generated job ID.
    """

    logger = current_app.logger

    task = {
        "logger": logger,
        "job_id": f"job_id_{current_app.threadpool.job_counter}",
        "handler": handler,
        "args": args,
    }

    try:
        current_app.threadpool.enqueue(task, logger)

    except RuntimeError:
        return (
            jsonify({"status": "error", "reason": "shutting down"}),
            400,
        )

    return jsonify({"job_id": task["job_id"]})


def extract_fields(data, *required_fields):
    """
    Extracts and validates required fields from the incoming request data.

    Args:
        data (dict): The JSON body of the request.
        *required_fields (str): Variable number of required field names.

    Returns:
        tuple:
            - dict or None: A dictionary containing the extracted fields, else None.
            - Response or None: A JSON error response if validation fails, else None.
            - int or None: HTTP status code 400 if validation fails, else None.

    Example:
        fields, error, status = extract_fields(request.json, "question", "state")
    """

    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        return None, jsonify({"status": "error"}), 400

    return {field: data[field] for field in required_fields}, None, None


def extract_job_id(job_id):
    """
    Extracts the numeric job ID from a formatted string.

    Args:
        job_id (str): The job identifier string (e.g., "job_id_7").

    Returns:
        int or None: The numeric part of the job ID if valid, else None.
    """

    match = re.fullmatch(r"job_id_(\d+)", job_id)
    return int(match.group(1)) if match else None
