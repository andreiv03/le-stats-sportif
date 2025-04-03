"""
Flask server initialization and dependency wiring.

This module configures the main Flask application, sets up core components such as:
- Data ingestion
- Task runner thread pool
- Route registration

It exposes the `server` object as the running app instance.
"""

from flask import Flask, jsonify, request

from app.data_ingestor import DataIngestor
from app.logging_config import get_logger
from app.routes import register_blueprints
from app.task_runner import ThreadPool

server = Flask(__name__)
server.data_ingestor = DataIngestor("./nutrition_activity_obesity_usa_subset.csv")
server.logger = get_logger()
server.threadpool = ThreadPool()

register_blueprints(server)


@server.before_request
def handle_before_request():
    """
    Logs every incoming HTTP request before it is processed by a route.

    This hook runs before each request and records the HTTP method and request path
    to the server log. It is useful for tracking access patterns, debugging, and
    auditing incoming traffic. The log entry includes both the method (e.g., GET, POST)
    and the exact URL path requested by the client.

    Example:
        A POST request to `/api/states_mean` will log:
        "Received POST \"/api/states_mean\" request"
    """

    logger = server.logger
    logger.info('Received %s "%s" request', request.method, request.path)


@server.errorhandler(404)
def handle_not_found(_):
    """
    Logs and handles 404 Not Found errors.

    Args:
        _ (Exception): The raised error (unused).

    Returns:
        Response: JSON error response with status 404.
    """

    logger = server.logger
    logger.warning('Not Found: %s "%s"', request.method, request.path)
    return jsonify({"error": "Not Found"}), 404


@server.errorhandler(405)
def handle_method_not_allowed(_):
    """
    Logs and handles 405 Method Not Allowed errors.

    Args:
        _ (Exception): The raised error (unused).

    Returns:
        Response: JSON error response with status 405.
    """

    logger = server.logger
    logger.warning('Method Not Allowed: %s "%s"', request.method, request.path)
    return jsonify({"error": "Method Not Allowed"}), 405
