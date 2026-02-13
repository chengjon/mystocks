"""
Data Quality Metrics Module

Provides data quality detection capabilities measuring four core dimensions:
- Completeness: Check for missing values and record counts
- Accuracy: Validate data against expected rules
- Timeliness: Check data freshness and update frequency
- Consistency: Compare data across different sources
"""

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class QualityDimension(str, Enum):
    """Data quality dimensions"""

    COMPLETENESS = "completeness"
    ACCURACY = "accuracy"
    TIMELINESS = "timeliness"
    CONSISTENCY = "consistency"


@dataclass
class QualityScore:
    """Quality score for a specific dimension"""

    dimension: QualityDimension
    score: float  # 0-100
    details: Dict[str, Any] = field(default_factory=dict)
    measured_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class QualityReport:
    """Complete quality report for a dataset"""

    dataset_id: str
    overall_score: float
    dimension_scores: List[QualityScore]
    measured_at: datetime = field(default_factory=datetime.utcnow)
    anomalies: List[Dict[str, Any]] = field(default_factory=list)


class DataQualityChecker:
    """
    Data quality checker that measures quality across multiple dimensions.
    """

    def __init__(self):
        self._quality_history: Dict[str, List[QualityReport]] = {}

    async def check_completeness(
        self,
        dataset_id: str,
        data: List[Dict[str, Any]],
        required_fields: Optional[List[str]] = None,
    ) -> QualityScore:
        """
        Check data completeness.

        Args:
            dataset_id: Dataset identifier
            data: List of data records
            required_fields: List of required field names

        Returns:
            QualityScore for completeness dimension
        """
        if not data:
            return QualityScore(
                dimension=QualityDimension.COMPLETENESS,
                score=0.0,
                details={"error": "No data to check"},
            )

        details: Dict[str, Any] = {}
        total_missing = 0
        total_fields = len(data) * len(data[0]) if data else 0

        if required_fields:
            missing_per_record = []
            for i, record in enumerate(data):
                missing = [f for f in required_fields if f not in record or record[f] is None]
                missing_per_record.append(len(missing))
                total_missing += len(missing)

            details["missing_fields"] = {str(i): count for i, count in enumerate(missing_per_record)}
        else:
            for record in data:
                for key, value in record.items():
                    if value is None or value == "":
                        total_missing += 1

        completeness_ratio = 1.0 - (total_missing / max(total_fields, 1))
        score = completeness_ratio * 100

        details.update(
            {
                "total_records": len(data),
                "total_fields": total_fields,
                "total_missing": total_missing,
                "completeness_ratio": completeness_ratio,
            }
        )

        return QualityScore(dimension=QualityDimension.COMPLETENESS, score=score, details=details)

    async def check_timeliness(
        self,
        dataset_id: str,
        last_update: Optional[datetime] = None,
        expected_interval_seconds: int = 3600,
    ) -> QualityScore:
        """
        Check data timeliness.

        Args:
            dataset_id: Dataset identifier
            last_update: Last update timestamp
            expected_interval_seconds: Expected update interval

        Returns:
            QualityScore for timeliness dimension
        """
        details = {}

        if not last_update:
            return QualityScore(
                dimension=QualityDimension.TIMELINESS,
                score=0.0,
                details={"error": "No last update timestamp available"},
            )

        now = datetime.now(timezone.utc)
        time_since_update = (now - last_update).total_seconds()

        if time_since_update <= expected_interval_seconds:
            score = 100.0
        elif time_since_update <= expected_interval_seconds * 2:
            score = 75.0
        elif time_since_update <= expected_interval_seconds * 4:
            score = 50.0
        elif time_since_update <= expected_interval_seconds * 8:
            score = 25.0
        else:
            score = 0.0

        details.update(
            {
                "last_update": last_update.isoformat(),
                "time_since_update_seconds": time_since_update,
                "expected_interval_seconds": expected_interval_seconds,
                "is_fresh": time_since_update <= expected_interval_seconds,
            }
        )

        return QualityScore(dimension=QualityDimension.TIMELINESS, score=score, details=details)

    async def check_accuracy(
        self,
        dataset_id: str,
        data: List[Dict[str, Any]],
        validation_rules: Optional[Dict[str, Any]] = None,
    ) -> QualityScore:
        """
        Check data accuracy using validation rules.

        Args:
            dataset_id: Dataset identifier
            data: List of data records
            validation_rules: Dictionary of validation rules

        Returns:
            QualityScore for accuracy dimension
        """
        if not data:
            return QualityScore(
                dimension=QualityDimension.ACCURACY,
                score=0.0,
                details={"error": "No data to check"},
            )

        details = {}
        violations = []

        if validation_rules:
            for i, record in enumerate(data):
                record_violations = []
                for field_name, rules in validation_rules.items():
                    if field_name in record:
                        value = record[field_name]
                        if value is not None:
                            if "min" in rules and value < rules["min"]:
                                record_violations.append(f"{field_name} < {rules['min']}")
                            if "max" in rules and value > rules["max"]:
                                record_violations.append(f"{field_name} > {rules['max']}")
                            if "pattern" in rules and not re.match(str(rules["pattern"]), str(value)):
                                record_violations.append(f"{field_name} doesn't match pattern")
                if record_violations:
                    violations.append({"record": i, "violations": record_violations})

        passed_count = len(data) - len(violations)
        accuracy_ratio = passed_count / max(len(data), 1)
        score = accuracy_ratio * 100

        details.update(
            {
                "total_records": len(data),
                "passed_records": passed_count,
                "failed_records": len(violations),
                "accuracy_ratio": accuracy_ratio,
                "violations": violations[:10],  # Limit to first 10
            }
        )

        return QualityScore(dimension=QualityDimension.ACCURACY, score=score, details=details)

    async def check_consistency(self, dataset_id: str, sources_data: Dict[str, List[Dict[str, Any]]]) -> QualityScore:
        """
        Check data consistency across different sources.

        Args:
            dataset_id: Dataset identifier
            sources_data: Dictionary mapping source names to data lists

        Returns:
            QualityScore for consistency dimension
        """
        if len(sources_data) < 2:
            return QualityScore(
                dimension=QualityDimension.CONSISTENCY,
                score=100.0,
                details={"info": "Only one source, consistency = 100%"},
            )

        details: Dict[str, Any] = {}
        inconsistencies = []

        # Get common keys from first source
        first_source = list(sources_data.keys())[0]
        common_keys = set(sources_data[first_source][0].keys()) if sources_data[first_source] else set()

        # Compare record counts
        record_counts = {k: len(v) for k, v in sources_data.items()}
        details["record_counts"] = record_counts

        # For each key, check consistency across sources
        for key in common_keys:
            values_by_source = {}
            for source_name, data in sources_data.items():
                if data and key in data[0]:
                    values = set(str(row[key]) for row in data if key in row)
                    values_by_source[source_name] = values

            # Check if values overlap
            all_values = set()
            for values in values_by_source.values():
                all_values.update(values)

            # Calculate overlap ratio
            overlap = sum(len(v) for v in values_by_source.values())
            total = len(all_values) * len(values_by_source) if all_values else 1
            consistency_ratio = overlap / total if total > 0 else 1.0

            if consistency_ratio < 1.0:
                inconsistencies.append(
                    {
                        "field": key,
                        "consistency_ratio": consistency_ratio,
                        "unique_values_per_source": {k: len(v) for k, v in values_by_source.items()},
                    }
                )

        consistency_ratio = 1.0 - (len(inconsistencies) / max(len(common_keys), 1))
        score = consistency_ratio * 100

        details.update(
            {
                "total_fields_compared": len(common_keys),
                "inconsistent_fields": len(inconsistencies),
                "consistency_ratio": consistency_ratio,
                "inconsistencies": inconsistencies[:10],
            }
        )

        return QualityScore(dimension=QualityDimension.CONSISTENCY, score=score, details=details)

    async def get_overall_score(
        self,
        dataset_id: str,
        scores: List[QualityScore],
        weights: Optional[Dict[str, float]] = None,
    ) -> float:
        """
        Calculate overall quality score from dimension scores.

        Args:
            dataset_id: Dataset identifier
            scores: List of QualityScore objects
            weights: Optional weights for each dimension

        Returns:
            Overall score (0-100)
        """
        default_weights = {
            "completeness": 0.30,
            "accuracy": 0.30,
            "timeliness": 0.20,
            "consistency": 0.20,
        }

        weights = weights or default_weights
        score_dict = {s.dimension.value: s.score for s in scores}

        overall = sum(score_dict.get(dim, 0) * weight for dim, weight in weights.items())

        return overall

    async def check_all_dimensions(
        self,
        dataset_id: str,
        data: Optional[List[Dict[str, Any]]] = None,
        last_update: Optional[datetime] = None,
        validation_rules: Optional[Dict[str, Any]] = None,
        comparison_sources: Optional[Dict[str, List[Dict[str, Any]]]] = None,
    ) -> QualityReport:
        """
        Perform comprehensive quality check across all dimensions.

        Args:
            dataset_id: Dataset identifier
            data: Dataset records
            last_update: Last update timestamp
            validation_rules: Validation rules for accuracy check
            comparison_sources: Data from different sources for consistency check

        Returns:
            Complete QualityReport
        """
        scores = []
        anomalies = []

        # Check completeness
        if data is not None:
            completeness = await self.check_completeness(dataset_id, data)
            scores.append(completeness)
            if completeness.score < 80:
                anomalies.append(
                    {
                        "dimension": "completeness",
                        "severity": "high" if completeness.score < 60 else "medium",
                        "message": f"Completeness score: {completeness.score:.1f}%",
                    }
                )

        # Check timeliness
        timeliness = await self.check_timeliness(dataset_id, last_update)
        scores.append(timeliness)
        if timeliness.score < 80:
            anomalies.append(
                {
                    "dimension": "timeliness",
                    "severity": "high" if timeliness.score < 60 else "medium",
                    "message": f"Timeliness score: {timeliness.score:.1f}%",
                }
            )

        # Check accuracy
        if data is not None and validation_rules:
            accuracy = await self.check_accuracy(dataset_id, data, validation_rules)
            scores.append(accuracy)
            if accuracy.score < 80:
                anomalies.append(
                    {
                        "dimension": "accuracy",
                        "severity": "high" if accuracy.score < 60 else "medium",
                        "message": f"Accuracy score: {accuracy.score:.1f}%",
                    }
                )

        # Check consistency
        if comparison_sources:
            consistency = await self.check_consistency(dataset_id, comparison_sources)
            scores.append(consistency)
            if consistency.score < 80:
                anomalies.append(
                    {
                        "dimension": "consistency",
                        "severity": "high" if consistency.score < 60 else "medium",
                        "message": f"Consistency score: {consistency.score:.1f}%",
                    }
                )

        overall = await self.get_overall_score(dataset_id, scores)

        report = QualityReport(
            dataset_id=dataset_id,
            overall_score=overall,
            dimension_scores=scores,
            anomalies=anomalies,
        )

        # Store in history
        if dataset_id not in self._quality_history:
            self._quality_history[dataset_id] = []
        self._quality_history[dataset_id].append(report)

        return report

    async def get_quality_trend(self, dataset_id: str, limit: int = 24) -> List[QualityReport]:
        """
        Get historical quality trend for a dataset.

        Args:
            dataset_id: Dataset identifier
            limit: Maximum number of historical records

        Returns:
            List of historical QualityReports
        """
        return self._quality_history.get(dataset_id, [])[-limit:]
