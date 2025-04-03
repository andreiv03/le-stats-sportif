"""
Root route for listing available API endpoints.

Provides a simple HTML-formatted overview of all registered routes and their supported methods.
Useful for development and debugging.
"""

from flask import Blueprint, current_app

index_bp = Blueprint("index", __name__)


@index_bp.route("/", methods=["GET"])
@index_bp.route("/index", methods=["GET"])
def index_request():
    """
    Displays all available API endpoints and their HTTP methods.

    Returns:
        str: An HTML-formatted message listing all routes.
    """

    message = "Hello, World!\n Interact with the web server using one of the defined routes:\n"

    for rule in current_app.url_map.iter_rules():
        methods = ", ".join(sorted(rule.methods - {"HEAD", "OPTIONS"}))
        message += f'<p>Endpoint: "{rule}", Methods: "{methods}"</p>'

    return message
