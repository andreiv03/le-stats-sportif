"""
Route for computing the difference between a single state's mean and the global mean.

This module defines the `/api/state_diff_from_mean` endpoint, which receives a health-related
question and a state, and dispatches a background job that calculates how much the state's
average deviates from the overall global mean.
"""

from flask import Blueprint, current_app, request
from app.utils import enqueue_task, extract_fields

state_diff_from_mean_bp = Blueprint("state_diff_from_mean", __name__)


# pylint: disable=R0801
@state_diff_from_mean_bp.route("/api/state_diff_from_mean", methods=["POST"])
def state_diff_from_mean_request():
    """
    Handles POST requests to compute how far a specific state's average is from the global mean.

    Expects:
        JSON body with:
            - 'question' (str): The question to filter by.
            - 'state' (str): The name of the state.

    Returns:
        JSON response with the job ID for the asynchronous task.
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
        state_diff_from_mean,
        {
            "df": current_app.data_ingestor.get_data(),
            **fields,
        },
    )


def state_diff_from_mean(args):
    """
    Task handler that calculates the difference between a state's mean value and the global mean.

    Args:
        args (dict): Contains:
            - 'df' (pd.DataFrame): The dataset.
            - 'question' (str): The question to filter by.
            - 'state' (str): The state to compute the mean for.

    Returns:
        dict: The state's deviation from the global mean, in the form:
              {"<state>": <float>}
    """

    df = args.get("df")
    question = args.get("question")
    state = args.get("state")

    filtered_df = df[df["Question"] == question]
    global_mean = filtered_df["Data_Value"].mean()

    filtered_df = filtered_df[filtered_df["LocationDesc"] == state]
    state_mean = filtered_df["Data_Value"].mean()
    result = global_mean - state_mean

    return {state: result}
