"""
Route for computing the difference of each state's mean from the global mean.

This module defines the `/api/diff_from_mean` endpoint, which receives a question
and dispatches a background job to compute the difference between each state's
average value and the overall global mean.
"""

from flask import Blueprint, current_app, request
from app.utils import enqueue_task, extract_fields

diff_from_mean_bp = Blueprint("diff_from_mean", __name__)


# pylint: disable=R0801
@diff_from_mean_bp.route("/api/diff_from_mean", methods=["POST"])
def diff_from_mean_request():
    """
    Handles POST requests to compute the difference from global mean per state.

    Expects:
        JSON body with 'question': str

    Returns:
        JSON containing the job_id for the async result.
    """

    logger = current_app.logger
    fields, error_response, status_code = extract_fields(request.json, "question")

    if error_response:
        logger.info('Missing "question" field in request body: "%s"', request.json)
        return error_response, status_code

    return enqueue_task(
        diff_from_mean,
        {
            "df": current_app.data_ingestor.get_data(),
            **fields,
        },
    )


def diff_from_mean(args):
    """
    Task handler that calculates the difference between each state's mean and the global mean.

    Args:
        args (dict): Contains 'df' (DataFrame) and 'question' (str)

    Returns:
        pd.Series: A Series with state names as keys and their deviation from global mean as values.
    """

    df = args.get("df")
    question = args.get("question")

    filtered_df = df[df["Question"] == question]
    states_mean = filtered_df.groupby("LocationDesc")["Data_Value"].mean()
    global_mean = filtered_df["Data_Value"].mean()
    result = global_mean - states_mean

    return result
