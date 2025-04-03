"""
Route for computing mean values grouped by stratification category and segment
for a specific state.

This module defines the `/api/state_mean_by_category` endpoint. It receives a
health-related question and a specific U.S. state, then dispatches a background
job to calculate the average `Data_Value` for each segment (`Stratification1`)
within the categories (`StratificationCategory1`) for that state.
"""

from flask import Blueprint, current_app, request
from app.utils import enqueue_task, extract_fields

state_mean_by_category_bp = Blueprint("state_mean_by_category", __name__)


# pylint: disable=R0801
@state_mean_by_category_bp.route("/api/state_mean_by_category", methods=["POST"])
def state_mean_by_category_request():
    """
    Handles POST requests to compute mean values by stratification category and segment
    for a specific state.

    Expects:
        JSON body with:
            - 'question' (str): The question to filter by.
            - 'state' (str): The state to compute means for.

    Returns:
        JSON response with the job ID for the asynchronous task, or error if input is invalid.
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
        state_mean_by_category,
        {
            "df": current_app.data_ingestor.get_data(),
            **fields,
        },
    )


def state_mean_by_category(args):
    """
    Task handler to calculate the mean `Data_Value` for each Stratification1 segment
    within each StratificationCategory1 for a specific state and question.

    Args:
        args (dict): Contains:
            - 'df' (pd.DataFrame): The dataset.
            - 'question' (str): The health-related question to filter by.
            - 'state' (str): The state to filter data by.

    Returns:
        dict: Flattened dictionary with structure:
            {
                "('State', 'Category', 'Segment')": mean_value,
                ...
            }
    """

    df = args.get("df")
    question = args.get("question")
    state = args.get("state")

    filtered_df = df[(df["Question"] == question) & (df["LocationDesc"] == state)]
    states_mean = filtered_df.groupby(["StratificationCategory1", "Stratification1"])[
        "Data_Value"
    ].mean()

    result = {
        f"('{category}', '{stratification}')": value
        for (category, stratification), value in states_mean.items()
    }

    return {state: result}
