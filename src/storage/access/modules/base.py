"""
Storage access base utilities and interfaces.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

import pandas as pd

from src.core import DataClassification, DataManager


class IDataAccessLayer(ABC):
    """Abstract data access layer."""

    @abstractmethod
    def save_data(self, data, classification: DataClassification, table_name: Optional[str] = None, **kwargs):
        """Save data to storage."""

    @abstractmethod
    def load_data(self, classification: DataClassification, table_name: Optional[str] = None, filters=None, **kwargs):
        """Load data from storage."""

    @abstractmethod
    def update_data(
        self,
        data,
        classification: DataClassification,
        table_name: Optional[str] = None,
        key_columns=None,
        **kwargs,
    ):
        """Update data in storage."""

    @abstractmethod
    def delete_data(self, classification: DataClassification, table_name: Optional[str] = None, filters=None, **kwargs):
        """Delete data from storage."""


def normalize_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Normalize DataFrame column names and basic types."""
    if dataframe is None or dataframe.empty:
        return dataframe

    df = dataframe.copy()

    # Normalize column names by trimming and replacing spaces with underscores.
    df.columns = [col.strip().replace(" ", "_") for col in df.columns]

    numeric_columns = {"volume", "price", "high", "low", "open"}
    for col in df.columns:
        if col.lower() in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Detect time columns and convert to datetime.
    time_tokens = ("time", "date", "timestamp", "datetime", "ts")
    time_columns = [col for col in df.columns if any(token in col.lower() for token in time_tokens)]
    for col in time_columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    # Sort by the first detected time column if present.
    if time_columns:
        df = df.sort_values(by=time_columns[0]).reset_index(drop=True)

    return df


def validate_time_series_data(dataframe: pd.DataFrame) -> bool:
    """Validate that a DataFrame contains time-series data."""
    if dataframe is None or dataframe.empty:
        return False

    time_tokens = ("time", "date", "timestamp", "datetime", "ts")
    time_columns = [col for col in dataframe.columns if any(token in col.lower() for token in time_tokens)]
    if not time_columns:
        return False

    # Accept only datetime typed columns to avoid mixed or invalid types.
    for col in time_columns:
        if pd.api.types.is_datetime64_any_dtype(dataframe[col]):
            return True

    return False


def get_database_name_from_classification(classification: DataClassification) -> str:
    """Resolve database name for a classification using DataManager when available."""
    manager = DataManager(enable_monitoring=False)
    if hasattr(manager, "get_database_name"):
        return manager.get_database_name(classification)

    # Fallback to classification name if DataManager lacks helper.
    return classification.name.lower()


__all__ = [
    "IDataAccessLayer",
    "normalize_dataframe",
    "validate_time_series_data",
    "get_database_name_from_classification",
]
