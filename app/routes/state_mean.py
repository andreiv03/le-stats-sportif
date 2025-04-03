"""
Route for initiating a background job that calculates the mean data value
for a specific state based on a given question.

This module defines the `/api/state_mean` endpoint, which submits the job to the
thread pool and returns a job ID for asynchronous result retrieval.
"""

from flask import Blueprint, current_app, request
from app.utils import enqueue_task, extract_fields

state_mean_bp = Blueprint("state_mean", __name__)


# pylint: disable=R0801
@state_mean_bp.route("/api/state_mean", methods=["POST"])
def state_mean_request():
    """
    Handles POST requests to calculate the mean value for a specific state.

    Expects JSON input with `question` and `state` fields. Submits the job to a
    background thread pool and returns a job ID.

    Returns:
        flask.Response: A JSON response containing the job ID.
    """

    logger = current_app.logger
    fields, error_response, status_code = extract_fields(
        request.json, "question", "state"
    )

    if error_response:
        logger.info(
            'Missing "question" or "state" field in request body: "%s"',
            request.json,
        )
        return error_response, status_code

    return enqueue_task(
        state_mean,
        {
            "df": current_app.data_ingestor.get_data(),
            **fields,
        },
    )


def state_mean(args):
    """
    Background task that calculates the mean value for a specific state.

    Args:
        args (dict): A dictionary with the DataFrame, question, and state.

    Returns:
        dict: A dictionary containing the state, question, and calculated mean.
    """

    df = args.get("df")
    question = args.get("question")
    state = args.get("state")

    filtered_df = df[(df["Question"] == question) & (df["LocationDesc"] == state)]
    result = filtered_df.groupby("LocationDesc")["Data_Value"].mean()

    return result.sort_values(ascending=True)
