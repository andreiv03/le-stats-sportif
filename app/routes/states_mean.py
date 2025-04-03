"""
Route for initiating a background job that calculates the mean data value
for each state based on a specified question.

This module defines the `/api/states_mean` endpoint, which submits the job to the
thread pool and returns a job ID for asynchronous result retrieval.
"""

from flask import Blueprint, current_app, request
from app.utils import enqueue_task, extract_fields

states_mean_bp = Blueprint("states_mean", __name__)


# pylint: disable=R0801
@states_mean_bp.route("/api/states_mean", methods=["POST"])
def states_mean_request():
    """
    Handles POST requests to calculate mean values across all states.

    Expects JSON input with a `question` field. Submits the job to a background
    thread pool and returns a job ID.

    Returns:
        flask.Response: A JSON response containing the job ID.
    """

    logger = current_app.logger
    fields, error_response, status_code = extract_fields(request.json, "question")

    if error_response:
        logger.info('Missing "question" field in request body: "%s"', request.json)
        return error_response, status_code

    return enqueue_task(
        states_mean,
        {
            "df": current_app.data_ingestor.get_data(),
            **fields,
        },
    )


def states_mean(args):
    """
    Background task that calculates the mean value per state.

    Args:
        args (dict): A dictionary with the DataFrame and question.

    Returns:
        dict: Mapping of state names to their average value for the question.
    """

    df = args.get("df")
    question = args.get("question")

    filtered_df = df[df["Question"] == question]
    result = filtered_df.groupby("LocationDesc")["Data_Value"].mean()

    return result.sort_values(ascending=True)
