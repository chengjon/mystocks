"""Unit tests for core data classification and storage strategy components."""

import pytest

from src.core.data_classification import DatabaseTarget, DataClassification
from src.core.data_storage_strategy import DataStorageStrategy


class TestDataClassification:
    """Test cases for DataClassification enum."""

    def test_data_classification_values(self):
        """Test that all expected data classification values exist."""
        expected_values = [
            "DAILY_KLINE",
            "MINUTE_KLINE",
            "TICK_DATA",
            "LEVEL2_SNAPSHOT",
            "SYMBOLS_INFO",
            "TECHNICAL_INDICATORS",
            "ORDER_RECORDS",
            "FUNDAMENTAL_METRICS",
        ]

        for value in expected_values:
            assert hasattr(DataClassification, value), f"Missing {value} in DataClassification"

    def test_data_classification_uniqueness(self):
        """Test that all data classification values are unique."""
        values = [cls.value for cls in DataClassification]
        assert len(values) == len(set(values)), "DataClassification contains duplicate values"

    def test_data_classification_string_conversion(self):
        """Test string conversion of data classification."""
        classification = DataClassification.DAILY_KLINE
        assert classification.value == "DAILY_KLINE"
        assert str(classification) == "DataClassification.DAILY_KLINE"


class TestDataStorageStrategy:
    """Test cases for DataStorageStrategy."""

    def test_classification_to_database_mapping(self):
        """Test that data classifications map to correct database targets."""
        # High-frequency time series data should go to TDengine
        assert DataStorageStrategy.CLASSIFICATION_TO_DATABASE[DataClassification.TICK_DATA] == DatabaseTarget.TDENGINE
        assert (
            DataStorageStrategy.CLASSIFICATION_TO_DATABASE[DataClassification.MINUTE_KLINE] == DatabaseTarget.TDENGINE
        )

        # Daily data and reference data should go to PostgreSQL
        assert (
            DataStorageStrategy.CLASSIFICATION_TO_DATABASE[DataClassification.DAILY_KLINE] == DatabaseTarget.POSTGRESQL
        )
        assert (
            DataStorageStrategy.CLASSIFICATION_TO_DATABASE[DataClassification.SYMBOLS_INFO] == DatabaseTarget.POSTGRESQL
        )
        assert (
            DataStorageStrategy.CLASSIFICATION_TO_DATABASE[DataClassification.INDUSTRY_CLASS]
            == DatabaseTarget.POSTGRESQL
        )

        # Trading data should go to PostgreSQL
        assert (
            DataStorageStrategy.CLASSIFICATION_TO_DATABASE[DataClassification.ORDER_RECORDS]
            == DatabaseTarget.POSTGRESQL
        )
        assert DataStorageStrategy.CLASSIFICATION_TO_DATABASE[DataClassification.FUND_FLOW] == DatabaseTarget.POSTGRESQL

    def test_all_classifications_have_mapping(self):
        """Test that all data classifications have database mappings."""
        for classification in DataClassification:
            assert (
                classification in DataStorageStrategy.CLASSIFICATION_TO_DATABASE
            ), f"No database mapping for {classification}"

    def test_get_database_target(self):
        """Test the get_database_target method."""
        strategy = DataStorageStrategy()

        # Test with valid classifications
        assert strategy.get_database_target(DataClassification.TICK_DATA) == DatabaseTarget.TDENGINE
        assert strategy.get_database_target(DataClassification.DAILY_KLINE) == DatabaseTarget.POSTGRESQL

    def test_get_database_target_invalid(self):
        """Test get_database_target with invalid input."""
        strategy = DataStorageStrategy()

        with pytest.raises(KeyError):
            strategy.get_database_target("INVALID_CLASSIFICATION")


class TestDatabaseTarget:
    """Test cases for DatabaseTarget enum."""

    def test_database_target_values(self):
        """Test that expected database target values exist."""
        assert hasattr(DatabaseTarget, "TDENGINE")
        assert hasattr(DatabaseTarget, "POSTGRESQL")

    def test_database_target_string_conversion(self):
        """Test string conversion of database targets."""
        tdengine_target = DatabaseTarget.TDENGINE
        postgres_target = DatabaseTarget.POSTGRESQL

        # Since DatabaseTarget inherits from str, str() returns the value
        assert str(tdengine_target) == "tdengine"
        assert str(postgres_target) == "postgresql"

        assert tdengine_target.value == "tdengine"
        assert postgres_target.value == "postgresql"
