"""
Route for computing the best 5 states based on a specific health question.

This module defines the `/api/best5` endpoint, which receives a question and
dispatches a background job to calculate the top 5 states with the lowest
mean values for that question.
"""

from flask import Blueprint, current_app, request
from app.utils import enqueue_task, extract_fields

best5_bp = Blueprint("best5", __name__)


# pylint: disable=R0801
@best5_bp.route("/api/best5", methods=["POST"])
def best5_request():
    """
    Handles POST requests to compute the best 5 states for a question
    where lower values are better.

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
        best5,
        {
            "df": current_app.data_ingestor.get_data(),
            "questions": current_app.data_ingestor.get_questions_best_is_min(),
            **fields,
        },
    )


def best5(args):
    """
    Task handler to compute the top 5 states with the lowest mean values for a given question.

    Args:
        args (dict): Contains:
            - 'df': pd.DataFrame
            - 'questions': list[str]
            - 'question': str

    Returns:
        dict: Mapping of top 5 states to their average value
    """

    df = args.get("df")
    questions = args.get("questions")
    question = args.get("question")

    filtered_df = df[df["Question"] == question]
    states_mean = filtered_df.groupby("LocationDesc")["Data_Value"].mean()
    result = states_mean.nsmallest(5)

    if question not in questions:
        result = states_mean.nlargest(5)

    return result
