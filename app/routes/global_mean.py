"""
Route for computing the global (overall) mean for a health question.

This module defines the `/api/global_mean` endpoint, which receives a question
and dispatches a background job to calculate the mean value across all states.
"""

from flask import Blueprint, current_app, request
from app.utils import enqueue_task, extract_fields

global_mean_bp = Blueprint("global_mean", __name__)


# pylint: disable=R0801
@global_mean_bp.route("/api/global_mean", methods=["POST"])
def global_mean_request():
    """
    Handles POST requests to compute the global mean for a health question.

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
        global_mean,
        {
            "df": current_app.data_ingestor.get_data(),
            **fields,
        },
    )


def global_mean(args):
    """
    Task handler to compute the overall average value for a given question.

    Args:
        args (dict): Contains 'df' (DataFrame) and 'question' (str)

    Returns:
        dict: A dictionary with the global mean under the key 'global_mean'.
    """

    df = args.get("df")
    question = args.get("question")

    filtered_df = df[df["Question"] == question]
    result = filtered_df["Data_Value"].mean()

    return {"global_mean": result}
