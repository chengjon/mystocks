"""
Unit tests for Data Quality Checker
"""

from datetime import datetime, timedelta

import pytest

from src.data_governance import DataQualityChecker, QualityDimension, QualityReport, QualityScore


class TestDataQualityChecker:
    """Tests for DataQualityChecker"""

    @pytest.fixture
    def checker(self):
        """Create a quality checker instance"""
        return DataQualityChecker()

    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing"""
        return [
            {"symbol": "000001", "name": "平安银行", "price": 10.5, "volume": 1000000},
            {"symbol": "000002", "name": "万 科Ａ", "price": 15.2, "volume": 2000000},
            {"symbol": "000003", "name": "国华网安", "price": None, "volume": 500000},
            {"symbol": "000004", "name": "深南电Ａ", "price": 8.3, "volume": None},
            {"symbol": "000005", "name": "世纪星", "price": 12.1, "volume": 800000},
        ]

    @pytest.mark.asyncio
    async def test_check_completeness_all_present(self, checker):
        """Test completeness check when all fields are present"""
        data = [
            {"symbol": "000001", "name": "平安银行", "price": 10.5},
            {"symbol": "000002", "name": "万 科Ａ", "price": 15.2},
        ]

        score = await checker.check_completeness("test_dataset", data)

        assert score.dimension == QualityDimension.COMPLETENESS
        assert score.score == 100.0
        assert "total_records" in score.details
        assert score.details["total_records"] == 2

    @pytest.mark.asyncio
    async def test_check_completeness_with_missing(self, checker, sample_data):
        """Test completeness check with missing values"""
        score = await checker.check_completeness("test_dataset", sample_data)

        assert score.dimension == QualityDimension.COMPLETENESS
        assert score.score < 100.0
        assert "total_missing" in score.details

    @pytest.mark.asyncio
    async def test_check_completeness_empty_data(self, checker):
        """Test completeness check with empty data"""
        score = await checker.check_completeness("test_dataset", [])

        assert score.dimension == QualityDimension.COMPLETENESS
        assert score.score == 0.0
        assert "error" in score.details

    @pytest.mark.asyncio
    async def test_check_timeliness_fresh_data(self, checker):
        """Test timeliness check for fresh data"""
        last_update = datetime.utcnow() - timedelta(minutes=30)

        score = await checker.check_timeliness("test_dataset", last_update=last_update, expected_interval_seconds=3600)

        assert score.dimension == QualityDimension.TIMELINESS
        assert score.score == 100.0
        assert score.details["is_fresh"] is True

    @pytest.mark.asyncio
    async def test_check_timeliness_stale_data(self, checker):
        """Test timeliness check for stale data"""
        last_update = datetime.utcnow() - timedelta(hours=5)

        score = await checker.check_timeliness("test_dataset", last_update=last_update, expected_interval_seconds=3600)

        assert score.dimension == QualityDimension.TIMELINESS
        assert score.score < 100.0
        assert score.details["is_fresh"] is False

    @pytest.mark.asyncio
    async def test_check_timeliness_no_timestamp(self, checker):
        """Test timeliness check when no timestamp is provided"""
        score = await checker.check_timeliness("test_dataset")

        assert score.dimension == QualityDimension.TIMELINESS
        assert score.score == 0.0
        assert "error" in score.details

    @pytest.mark.asyncio
    async def test_check_accuracy_valid_data(self, checker):
        """Test accuracy check with valid data"""
        data = [
            {"price": 10.5, "volume": 1000000},
            {"price": 15.2, "volume": 2000000},
        ]
        rules = {"price": {"min": 0, "max": 1000}}

        score = await checker.check_accuracy("test_dataset", data, rules)

        assert score.dimension == QualityDimension.ACCURACY
        assert score.score == 100.0
        assert score.details["passed_records"] == 2
        assert score.details["failed_records"] == 0

    @pytest.mark.asyncio
    async def test_check_accuracy_with_violations(self, checker):
        """Test accuracy check with validation violations"""
        data = [
            {"price": 10.5, "volume": 1000000},
            {"price": -5.0, "volume": 2000000},  # Invalid: negative price
        ]
        rules = {"price": {"min": 0, "max": 1000}}

        score = await checker.check_accuracy("test_dataset", data, rules)

        assert score.dimension == QualityDimension.ACCURACY
        assert score.score == 50.0
        assert score.details["failed_records"] == 1

    @pytest.mark.asyncio
    async def test_check_consistency_single_source(self, checker):
        """Test consistency check with single source"""
        sources_data = {"source1": [{"value": 10}, {"value": 20}]}

        score = await checker.check_consistency("test_dataset", sources_data)

        assert score.dimension == QualityDimension.CONSISTENCY
        assert score.score == 100.0

    @pytest.mark.asyncio
    async def test_check_consistency_multiple_sources(self, checker):
        """Test consistency check with multiple sources"""
        sources_data = {
            "source1": [{"value": 10}, {"value": 20}],
            "source2": [{"value": 10}, {"value": 20}],
        }

        score = await checker.check_consistency("test_dataset", sources_data)

        assert score.dimension == QualityDimension.CONSISTENCY
        assert score.score == 100.0

    @pytest.mark.asyncio
    async def test_check_consistency_with_inconsistencies(self, checker):
        """Test consistency check with inconsistent data"""
        sources_data = {
            "source1": [{"value": 10}, {"value": 20}],
            "source2": [{"value": 10}, {"value": 30}],  # Inconsistent: 20 vs 30
        }

        score = await checker.check_consistency("test_dataset", sources_data)

        assert score.dimension == QualityDimension.CONSISTENCY
        assert score.score < 100.0

    @pytest.mark.asyncio
    async def test_get_overall_score(self, checker):
        """Test calculating overall quality score"""
        scores = [
            QualityScore(dimension=QualityDimension.COMPLETENESS, score=90.0),
            QualityScore(dimension=QualityDimension.ACCURACY, score=80.0),
            QualityScore(dimension=QualityDimension.TIMELINESS, score=100.0),
            QualityScore(dimension=QualityDimension.CONSISTENCY, score=95.0),
        ]

        overall = await checker.get_overall_score("test_dataset", scores)

        # Expected: 0.3*90 + 0.3*80 + 0.2*100 + 0.2*95 = 27 + 24 + 20 + 19 = 90
        assert overall == 90.0

    @pytest.mark.asyncio
    async def test_check_all_dimensions(self, checker, sample_data):
        """Test comprehensive quality check across all dimensions"""
        last_update = datetime.utcnow() - timedelta(minutes=30)

        report = await checker.check_all_dimensions(
            dataset_id="test_dataset",
            data=sample_data,
            last_update=last_update,
            validation_rules={"price": {"min": 0, "max": 1000}},
        )

        assert report.dataset_id == "test_dataset"
        assert report.overall_score > 0
        assert len(report.dimension_scores) >= 2  # At least completeness and timeliness

    @pytest.mark.asyncio
    async def test_get_quality_trend(self, checker):
        """Test getting quality trend history"""
        # Create some history
        for _ in range(3):
            await checker.check_all_dimensions("test_dataset")

        trend = await checker.get_quality_trend("test_dataset")

        assert len(trend) == 3


class TestQualityScore:
    """Tests for QualityScore model"""

    def test_create_quality_score(self):
        """Test creating a quality score"""
        score = QualityScore(dimension=QualityDimension.COMPLETENESS, score=85.5, details={"test": "value"})
        assert score.dimension == QualityDimension.COMPLETENESS
        assert score.score == 85.5
        assert score.details["test"] == "value"


class TestQualityReport:
    """Tests for QualityReport model"""

    def test_create_quality_report(self):
        """Test creating a quality report"""
        scores = [QualityScore(dimension=QualityDimension.COMPLETENESS, score=90.0)]
        report = QualityReport(dataset_id="test", overall_score=90.0, dimension_scores=scores)
        assert report.dataset_id == "test"
        assert report.overall_score == 90.0
        assert len(report.dimension_scores) == 1
