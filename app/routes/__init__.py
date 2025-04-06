"""
Registers all API route blueprints to the Flask application.

This module centralizes the blueprint registration process to keep the app factory clean.
"""

from .index import index_bp
from .states_mean import states_mean_bp
from .state_mean import state_mean_bp
from .best5 import best5_bp
from .worst5 import worst5_bp
from .global_mean import global_mean_bp
from .diff_from_mean import diff_from_mean_bp
from .state_diff_from_mean import state_diff_from_mean_bp
from .mean_by_category import mean_by_category_bp
from .state_mean_by_category import state_mean_by_category_bp
from .graceful_shutdown import graceful_shutdown_bp
from .jobs import jobs_bp
from .num_jobs import num_jobs_bp
from .get_results import get_results_bp
from .restart import restart_bp


def register_blueprints(app):
    """
    Registers all route blueprints to the provided Flask app.

    Args:
        app (Flask): The Flask application instance.
    """

    blueprints = [
        index_bp,
        states_mean_bp,
        state_mean_bp,
        best5_bp,
        worst5_bp,
        global_mean_bp,
        diff_from_mean_bp,
        state_diff_from_mean_bp,
        mean_by_category_bp,
        state_mean_by_category_bp,
        graceful_shutdown_bp,
        jobs_bp,
        num_jobs_bp,
        get_results_bp,
        restart_bp,
    ]

    for blueprint in blueprints:
        app.register_blueprint(blueprint)
