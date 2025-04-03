"""
Route for computing mean values grouped by category and stratification per state.

This module defines the `/api/mean_by_category` endpoint. It receives a health-related
question and dispatches a background job to calculate the average value for each
segment (`Stratification1`) within the categories (`StratificationCategory1`)
for every state.
"""

from flask import Blueprint, current_app, request
from app.utils import enqueue_task, extract_fields

mean_by_category_bp = Blueprint("mean_by_category", __name__)


# pylint: disable=R0801
@mean_by_category_bp.route("/api/mean_by_category", methods=["POST"])
def mean_by_category_request():
    """
    Handles POST requests to compute mean values by stratification category and segment.

    Expects:
        JSON body with:
            - 'question' (str): The question to filter by.

    Returns:
        JSON response with the job ID for the asynchronous task.
    """

    logger = current_app.logger
    fields, error_response, status_code = extract_fields(request.json, "question")

    if error_response:
        logger.info('Missing "question" field in request body: "%s"', request.json)
        return error_response, status_code

    return enqueue_task(
        mean_by_category,
        {
            "df": current_app.data_ingestor.get_data(),
            **fields,
        },
    )


def mean_by_category(args):
    """
    Task handler to calculate the mean `Data_Value` for each Stratification1 segment
    within each StratificationCategory1 for each state, for a given question.

    Args:
        args (dict): Contains:
            - 'df' (pd.DataFrame): The dataset.
            - 'question' (str): The question to filter by.

    Returns:
        dict: Flattened dictionary like:
            {
                "('State', 'Category', 'Segment')": mean_value,
                ...
            }
    """

    df = args.get("df")
    question = args.get("question")

    filtered_df = df[df["Question"] == question]
    states_mean = filtered_df.groupby(
        ["LocationDesc", "StratificationCategory1", "Stratification1"]
    )["Data_Value"].mean()

    result = {
        f"('{state}', '{category}', '{stratification}')": value
        for (state, category, stratification), value in states_mean.items()
    }

    return result
