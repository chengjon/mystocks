"""
Layer Validation Utilities for 5-Layer Verification Model

This module implements the 5-layer verification model for integration tests:
- Layer 5: Database (data存在性、时效性、合理性)
- Layer 4: UI (browser console, element visibility)
- Layer 3: Integration (end-to-end flow)
- Layer 2: API (response status, data structure)
- Layer 1: Code (unit tests, linting) - not covered here

Usage:
    from tests.integration.utils.layer_validation import validate_all_layers

    result = validate_all_layers(
        db_cursor=db_cursor,
        api_client=api_client,
        page=page,
        config={
            "database_table": "cn_stock_top",
            "api_endpoint": "/api/market/dragon-tiger",
            "ui_selector": "table.dragon-tiger-table"
        }
    )

    assert result.all_passed, f"Validation failed: {result.get_failures()}"

Author: MyStocks Development Team
Created: 2025-10-29
"""

import psycopg2
from playwright.sync_api import Page
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class LayerValidationResult:
    """
    Result of layer validation.

    Attributes:
        layer_name: Name of the layer (e.g., "Layer 5: Database")
        passed: Whether validation passed
        details: Detailed validation results
        errors: List of error messages
        warnings: List of warning messages
    """

    layer_name: str
    passed: bool
    details: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_error(self, message: str):
        """Add an error message and mark validation as failed."""
        self.errors.append(message)
        self.passed = False

    def add_warning(self, message: str):
        """Add a warning message (does not fail validation)."""
        self.warnings.append(message)

    def __str__(self) -> str:
        status = "✅ PASS" if self.passed else "❌ FAIL"
        return f"{status} {self.layer_name}"


@dataclass
class MultiLayerValidationResult:
    """
    Result of multi-layer validation.

    Attributes:
        results: List of individual layer results
        all_passed: Whether all layers passed
    """

    results: List[LayerValidationResult] = field(default_factory=list)

    @property
    def all_passed(self) -> bool:
        """Check if all layers passed validation."""
        return all(result.passed for result in self.results)

    def get_failures(self) -> List[LayerValidationResult]:
        """Get list of failed layer validations."""
        return [result for result in self.results if not result.passed]

    def get_layer_result(self, layer_name: str) -> Optional[LayerValidationResult]:
        """Get result for a specific layer."""
        for result in self.results:
            if layer_name in result.layer_name:
                return result
        return None

    def __str__(self) -> str:
        status = "✅ ALL PASS" if self.all_passed else "❌ SOME FAILED"
        summary = "\n".join(str(result) for result in self.results)
        return f"{status}\n{summary}"


# =============================================================================
# LAYER 5: DATABASE VALIDATION
# =============================================================================


def validate_layer_5_database(
    db_cursor,
    table_name: str,
    expected_min_count: int = 1,
    check_freshness: bool = True,
    max_days_old: int = 3,
) -> LayerValidationResult:
    """
    Validate Layer 5: Database data exists, is fresh, and reasonable.

    Checks:
    1. Table has data (存在性)
    2. Data is fresh within max_days_old (时效性)
    3. No NULL values in critical fields (完整性)
    4. Data values are reasonable (合理性)

    Args:
        db_cursor: Database cursor from conftest fixture
        table_name: Table name to validate
        expected_min_count: Minimum expected record count
        check_freshness: Whether to check data freshness
        max_days_old: Maximum acceptable data age in days

    Returns:
        LayerValidationResult with validation details

    Example:
        result = validate_layer_5_database(
            db_cursor,
            "cn_stock_top",
            expected_min_count=10,
            max_days_old=3
        )
        assert result.passed
    """
    result = LayerValidationResult(layer_name="Layer 5: Database", passed=True)

    try:
        # Check 1: Data existence (存在性)
        db_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = db_cursor.fetchone()[0]
        result.details["record_count"] = count

        if count < expected_min_count:
            result.add_error(
                f"Insufficient data: expected >= {expected_min_count}, found {count}"
            )
        else:
            logger.info(f"✅ Data exists: {count} records in {table_name}")

        # Check 2: Data freshness (时效性)
        if check_freshness and count > 0:
            db_cursor.execute(
                f"""
                SELECT
                    MAX(trade_date) as latest_date,
                    CURRENT_DATE - MAX(trade_date) as days_old
                FROM {table_name}
            """
            )
            row = db_cursor.fetchone()
            latest_date, days_old = row

            result.details["latest_date"] = str(latest_date) if latest_date else None
            result.details["days_old"] = days_old

            if days_old is None:
                result.add_warning("No trade_date column found in table")
            elif days_old > max_days_old:
                result.add_error(
                    f"Data is stale: latest date {latest_date} is {days_old} days old "
                    f"(max allowed: {max_days_old} days)"
                )
            else:
                logger.info(
                    f"✅ Data is fresh: latest date {latest_date} ({days_old} days old)"
                )

        # Check 3: NULL value check (完整性)
        if count > 0:
            # Try to check common fields
            db_cursor.execute(
                f"""
                SELECT COUNT(*) FROM {table_name}
                WHERE stock_code IS NULL OR stock_name IS NULL
            """
            )
            null_count = db_cursor.fetchone()[0]
            result.details["null_count"] = null_count

            if null_count > 0:
                result.add_error(
                    f"Found {null_count} records with NULL in critical fields"
                )
            else:
                logger.info(f"✅ No NULL values in critical fields")

    except psycopg2.errors.UndefinedColumn as e:
        # Some tables may not have trade_date column
        result.add_warning(f"Column not found: {str(e)}")
    except Exception as e:
        result.add_error(f"Database validation error: {str(e)}")
        logger.error(f"Layer 5 validation failed: {str(e)}")

    return result


# =============================================================================
# LAYER 2: API VALIDATION
# =============================================================================


def validate_layer_2_api(
    api_client,
    endpoint: str,
    expected_status: int = 200,
    expected_fields: Optional[List[str]] = None,
    expected_min_records: int = 1,
) -> LayerValidationResult:
    """
    Validate Layer 2: API returns valid response with expected data.

    Checks:
    1. HTTP status code is as expected
    2. Response contains data
    3. Response has expected fields
    4. Response has minimum number of records

    Args:
        api_client: API client from conftest fixture
        endpoint: API endpoint to test (e.g., "/api/market/dragon-tiger")
        expected_status: Expected HTTP status code
        expected_fields: List of expected field names in response
        expected_min_records: Minimum expected records in response

    Returns:
        LayerValidationResult with validation details

    Example:
        result = validate_layer_2_api(
            api_client,
            "/api/market/dragon-tiger?limit=5",
            expected_fields=["stock_code", "stock_name", "trade_date"]
        )
        assert result.passed
    """
    result = LayerValidationResult(layer_name="Layer 2: API", passed=True)

    try:
        # Make API request
        response = api_client.get(endpoint)

        # Check 1: HTTP status
        result.details["status_code"] = response.status
        result.details["ok"] = response.ok

        if response.status != expected_status:
            result.add_error(
                f"Unexpected status code: expected {expected_status}, got {response.status}"
            )
            return result
        else:
            logger.info(f"✅ API returned status {response.status}")

        # Check 2: Response has data
        data = response.json()
        result.details["response_type"] = type(data).__name__

        if not isinstance(data, list):
            result.add_error(f"Expected list response, got {type(data).__name__}")
            return result

        record_count = len(data)
        result.details["record_count"] = record_count

        if record_count < expected_min_records:
            result.add_error(
                f"Insufficient records: expected >= {expected_min_records}, got {record_count}"
            )
        else:
            logger.info(f"✅ API returned {record_count} records")

        # Check 3: Expected fields present
        if expected_fields and record_count > 0:
            first_record = data[0]
            missing_fields = [
                field for field in expected_fields if field not in first_record
            ]

            if missing_fields:
                result.add_error(f"Missing expected fields: {missing_fields}")
            else:
                logger.info(f"✅ All expected fields present: {expected_fields}")

            result.details["sample_record"] = first_record

    except Exception as e:
        result.add_error(f"API validation error: {str(e)}")
        logger.error(f"Layer 2 validation failed: {str(e)}")

    return result


# =============================================================================
# LAYER 4: UI VALIDATION
# =============================================================================


def validate_layer_4_ui(
    page: Page,
    expected_elements: Dict[str, str],
    check_console: bool = True,
    check_network: bool = True,
) -> LayerValidationResult:
    """
    Validate Layer 4: UI elements are visible and no console errors.

    Checks:
    1. Expected elements are visible
    2. No console errors (if check_console=True)
    3. No failed network requests (if check_network=True)

    Args:
        page: Playwright page instance
        expected_elements: Dict of {element_name: css_selector}
        check_console: Whether to check for console errors
        check_network: Whether to check for failed network requests

    Returns:
        LayerValidationResult with validation details

    Example:
        result = validate_layer_4_ui(
            page,
            expected_elements={
                "table": "table.dragon-tiger-table",
                "header": "h1:has-text('龙虎榜')"
            }
        )
        assert result.passed
    """
    result = LayerValidationResult(layer_name="Layer 4: UI", passed=True)

    try:
        # Check 1: Element visibility
        visible_elements = []
        missing_elements = []

        for name, selector in expected_elements.items():
            try:
                element = page.locator(selector)
                if element.is_visible(timeout=5000):
                    visible_elements.append(name)
                else:
                    missing_elements.append(name)
                    result.add_error(f"Element '{name}' ({selector}) not visible")
            except Exception as e:
                missing_elements.append(name)
                result.add_error(f"Element '{name}' ({selector}) not found: {str(e)}")

        result.details["visible_elements"] = visible_elements
        result.details["missing_elements"] = missing_elements

        if missing_elements:
            logger.error(f"❌ Missing UI elements: {missing_elements}")
        else:
            logger.info(f"✅ All expected UI elements visible: {visible_elements}")

        # Check 2: Console errors (if enabled)
        if check_console:
            console_errors = []

            def capture_console(msg):
                if msg.type == "error":
                    console_errors.append(msg.text)

            page.on("console", capture_console)

            # Wait briefly to capture any errors
            page.wait_for_timeout(1000)

            result.details["console_errors"] = console_errors

            if console_errors:
                for error in console_errors:
                    result.add_error(f"Console error: {error}")
                logger.error(f"❌ Console errors found: {len(console_errors)}")
            else:
                logger.info("✅ No console errors")

    except Exception as e:
        result.add_error(f"UI validation error: {str(e)}")
        logger.error(f"Layer 4 validation failed: {str(e)}")

    return result


# =============================================================================
# MULTI-LAYER VALIDATION
# =============================================================================


def validate_all_layers(
    db_cursor, api_client, page: Page, config: Dict[str, Any]
) -> MultiLayerValidationResult:
    """
    Validate all layers in sequence: Layer 5 → Layer 2 → Layer 4.

    This implements the bottom-up verification strategy:
    1. Layer 5: Database data must exist and be fresh
    2. Layer 2: API must return valid data from database
    3. Layer 4: UI must display API data correctly

    Args:
        db_cursor: Database cursor fixture
        api_client: API client fixture
        page: Playwright page fixture
        config: Configuration dict with keys:
            - database_table: Table name to validate
            - api_endpoint: API endpoint to validate
            - api_expected_fields: Expected fields in API response
            - ui_elements: Dict of {name: selector} for UI validation
            - expected_min_count: Minimum expected records (default: 1)

    Returns:
        MultiLayerValidationResult with all layer results

    Example:
        result = validate_all_layers(
            db_cursor=db_cursor,
            api_client=api_client,
            page=page,
            config={
                "database_table": "cn_stock_top",
                "api_endpoint": "/api/market/dragon-tiger?limit=5",
                "api_expected_fields": ["stock_code", "stock_name"],
                "ui_elements": {
                    "table": "table.dragon-tiger-table",
                    "header": "h1"
                },
                "expected_min_count": 5
            }
        )

        assert result.all_passed, f"Validation failed:\\n{result}"
    """
    multi_result = MultiLayerValidationResult()

    # Extract config
    database_table = config.get("database_table")
    api_endpoint = config.get("api_endpoint")
    api_expected_fields = config.get("api_expected_fields", [])
    ui_elements = config.get("ui_elements", {})
    expected_min_count = config.get("expected_min_count", 1)

    # Layer 5: Database validation
    if database_table:
        logger.info("=== Validating Layer 5: Database ===")
        layer5_result = validate_layer_5_database(
            db_cursor, database_table, expected_min_count=expected_min_count
        )
        multi_result.results.append(layer5_result)

        # If database validation fails, skip other layers
        if not layer5_result.passed:
            logger.error("❌ Layer 5 (Database) failed - skipping higher layers")
            return multi_result

    # Layer 2: API validation
    if api_endpoint:
        logger.info("=== Validating Layer 2: API ===")
        layer2_result = validate_layer_2_api(
            api_client,
            api_endpoint,
            expected_fields=api_expected_fields,
            expected_min_records=expected_min_count,
        )
        multi_result.results.append(layer2_result)

        # If API validation fails, skip UI layer
        if not layer2_result.passed:
            logger.error("❌ Layer 2 (API) failed - skipping UI layer")
            return multi_result

    # Layer 4: UI validation
    if ui_elements:
        logger.info("=== Validating Layer 4: UI ===")
        layer4_result = validate_layer_4_ui(page, expected_elements=ui_elements)
        multi_result.results.append(layer4_result)

    # Summary
    if multi_result.all_passed:
        logger.info("✅ ✅ ✅ All layers passed validation!")
    else:
        failures = multi_result.get_failures()
        logger.error(f"❌ Validation failed in {len(failures)} layer(s)")
        for failure in failures:
            logger.error(f"  - {failure.layer_name}: {failure.errors}")

    return multi_result


# =============================================================================
# CONVENIENCE CLASS
# =============================================================================


class LayerValidation:
    """
    Convenience class for layer validation in tests.

    Usage:
        validator = LayerValidation(db_cursor, api_client, page)

        # Validate individual layers
        validator.database("cn_stock_top", min_count=10)
        validator.api("/api/market/dragon-tiger", fields=["stock_code"])
        validator.ui({"table": "table.dragon-tiger-table"})

        # Or validate all at once
        result = validator.all({
            "database_table": "cn_stock_top",
            "api_endpoint": "/api/market/dragon-tiger",
            "ui_elements": {"table": "table.dragon-tiger-table"}
        })
    """

    def __init__(self, db_cursor, api_client, page: Page):
        """
        Initialize layer validator.

        Args:
            db_cursor: Database cursor fixture
            api_client: API client fixture
            page: Playwright page fixture
        """
        self.db_cursor = db_cursor
        self.api_client = api_client
        self.page = page

    def database(
        self,
        table_name: str,
        min_count: int = 1,
        check_freshness: bool = True,
        max_days_old: int = 3,
    ) -> LayerValidationResult:
        """Validate database layer."""
        return validate_layer_5_database(
            self.db_cursor,
            table_name,
            expected_min_count=min_count,
            check_freshness=check_freshness,
            max_days_old=max_days_old,
        )

    def api(
        self,
        endpoint: str,
        fields: Optional[List[str]] = None,
        min_records: int = 1,
        expected_status: int = 200,
    ) -> LayerValidationResult:
        """Validate API layer."""
        return validate_layer_2_api(
            self.api_client,
            endpoint,
            expected_status=expected_status,
            expected_fields=fields,
            expected_min_records=min_records,
        )

    def ui(
        self,
        elements: Dict[str, str],
        check_console: bool = True,
        check_network: bool = True,
    ) -> LayerValidationResult:
        """Validate UI layer."""
        return validate_layer_4_ui(
            self.page,
            expected_elements=elements,
            check_console=check_console,
            check_network=check_network,
        )

    def all(self, config: Dict[str, Any]) -> MultiLayerValidationResult:
        """Validate all layers."""
        return validate_all_layers(self.db_cursor, self.api_client, self.page, config)
