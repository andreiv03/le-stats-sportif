"""
Data ingestion utilities for nutrition and activity analysis.

This module provides a DataIngestor class to load and filter structured health survey data,
along with predefined question categories for evaluating wellness metrics.
"""

import os
import pandas as pd

QUESTIONS_BEST_IS_MIN = [
    "Percent of adults aged 18 years and older who have an overweight classification",
    "Percent of adults aged 18 years and older who have obesity",
    "Percent of adults who engage in no leisure-time physical activity",
    "Percent of adults who report consuming fruit less than one time daily",
    "Percent of adults who report consuming vegetables less than one time daily",
]

QUESTIONS_BEST_IS_MAX = [
    "Percent of adults who achieve at least 150 minutes a week of moderate-intensity "
    "aerobic physical activity or 75 minutes a week of vigorous-intensity "
    "aerobic activity (or an equivalent combination)",
    "Percent of adults who achieve at least 150 minutes a week of "
    "moderate-intensity aerobic physical activity or 75 minutes a "
    "week of vigorous-intensity aerobic physical activity and engage "
    "in muscle-strengthening activities on 2 or more days a week",
    "Percent of adults who achieve at least 300 minutes a week of "
    "moderate-intensity aerobic physical activity or 150 minutes a "
    "week of vigorous-intensity aerobic activity (or an equivalent combination)",
    "Percent of adults who engage in muscle-strengthening activities on 2 or more days a week",
]

COLUMNS = [
    "LocationDesc",
    "Question",
    "Data_Value",
    "StratificationCategory1",
    "Stratification1",
]


class DataIngestor:
    """
    Loads, filters, and exposes health-related survey data from a structured CSV file.

    This class ensures that only the relevant columns are loaded, missing values are filtered,
    and important question categories are available for downstream analysis.
    """

    def __init__(self, csv_path: str):
        os.system("rm -rf results")

        if not os.path.exists("results"):
            os.makedirs("results")

        self.questions_best_is_min = QUESTIONS_BEST_IS_MIN
        self.questions_best_is_max = QUESTIONS_BEST_IS_MAX

        if not csv_path:
            raise ValueError("CSV path is required.")

        if not os.path.isfile(csv_path):
            raise FileNotFoundError(f"CSV file not found at path: {csv_path}")

        try:
            self.df = pd.read_csv(csv_path, usecols=COLUMNS)
            self.df.dropna(subset=["Data_Value"], inplace=True)

        except Exception as exception:
            raise ValueError("Failed to read CSV file.") from exception

    def get_data(self):
        """
        Returns the loaded and filtered dataset.

        Returns:
            pd.DataFrame: A DataFrame containing relevant rows and columns from the CSV file.
        """

        return self.df

    def get_questions_best_is_min(self):
        """
        Retrieves questions where lower values reflect better health outcomes.

        Returns:
            list[str]: A list of question descriptions.
        """

        return self.questions_best_is_min

    def get_questions_best_is_max(self):
        """
        Retrieves questions where higher values reflect better health outcomes.

        Returns:
            list[str]: A list of question descriptions.
        """

        return self.questions_best_is_max
