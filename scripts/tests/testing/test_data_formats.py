"""
Test Data Format Conventions and Schemas

Tests all data format implementations to ensure consistency and correctness.
Reference: docs/api/API_SPECIFICATION.md
"""

import sys
import os
from decimal import Decimal
from datetime import date

# Calculate project root (3 levels up from script location)
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)

# Import test data formats and schemas
from web.backend.app.core.data_formats import (
    get_current_iso_timestamp,
    get_current_ms_timestamp,
    validate_price,
    validate_percentage,
    validate_volume,
    validate_currency,
    StockSymbolFormat,
    DateFormat,
    TimestampFormat,
    PrecisionRules,
    DataFormatConstants,
    DataFormatValidator,
    HTTPHeaderFormats,
)

from web.backend.app.schemas.base_schemas import (
    SuccessResponse,
    ErrorResponse,
    PaginationInfo,
    PaginatedResponse,
    ValidationErrorResponse,
    UnauthorizedResponse,
    ForbiddenResponse,
    NotFoundResponse,
    ServerErrorResponse,
    StockSymbolField,
    PriceField,
    PercentageField,
    VolumeField,
    CurrencyField,
    DateField,
    TimestampField,
    PaginationRequest,
)


# ============================================================================
# TEST RESULTS TRACKING
# ============================================================================


class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def add_pass(self, test_name: str):
        self.passed += 1
        print(f"  ✅ {test_name}")

    def add_fail(self, test_name: str, reason: str):
        self.failed += 1
        self.errors.append((test_name, reason))
        print(f"  ❌ {test_name}: {reason}")

    def print_summary(self):
        print(f"\n{'=' * 70}")
        print("TEST SUMMARY")
        print(f"{'=' * 70}")
        print(f"Passed:  {self.passed}")
        print(f"Failed:  {self.failed}")
        print(f"Total:   {self.passed + self.failed}")

        if self.failed > 0:
            print("\n❌ FAILED TESTS:")
            for test_name, reason in self.errors:
                print(f"  - {test_name}: {reason}")
        else:
            print("\n✅ ALL TESTS PASSED!")


results = TestResults()


# ============================================================================
# TIMESTAMP FORMAT TESTS
# ============================================================================


def test_iso_timestamp_format():
    """Test ISO 8601 timestamp generation"""
    try:
        ts = get_current_iso_timestamp()
        assert isinstance(ts, str), "Timestamp must be string"
        assert ts.endswith("Z"), "ISO timestamp must end with Z"
        assert "T" in ts, "ISO timestamp must contain T separator"
        results.add_pass("ISO 8601 timestamp generation")
    except Exception as e:
        results.add_fail("ISO 8601 timestamp generation", str(e))


def test_millisecond_timestamp_format():
    """Test millisecond timestamp generation"""
    try:
        ts = get_current_ms_timestamp()
        assert isinstance(ts, int), "Timestamp must be integer"
        assert ts > 0, "Timestamp must be positive"
        assert ts > 1000000000000, "Should be milliseconds (> 1 trillion)"
        results.add_pass("Millisecond timestamp generation")
    except Exception as e:
        results.add_fail("Millisecond timestamp generation", str(e))


def test_timestamp_format_enum():
    """Test TimestampFormat enum"""
    try:
        assert TimestampFormat.ISO_8601.value == "ISO_8601"
        assert TimestampFormat.MILLISECONDS.value == "MILLISECONDS"
        assert TimestampFormat.SECONDS.value == "SECONDS"
        results.add_pass("TimestampFormat enum definition")
    except Exception as e:
        results.add_fail("TimestampFormat enum definition", str(e))


# ============================================================================
# DECIMAL PRECISION TESTS
# ============================================================================


def test_price_validation():
    """Test price validation and precision"""
    try:
        # Valid price
        price = validate_price(123.456)
        assert price == Decimal(
            "123.46"
        ), f"Price should round to 2 decimals, got {price}"

        # Another valid price
        price2 = validate_price(Decimal("1850.50"))
        assert price2 == Decimal("1850.50")

        results.add_pass("Price validation and precision (2 decimals)")
    except Exception as e:
        results.add_fail("Price validation and precision", str(e))


def test_percentage_validation():
    """Test percentage validation with different precisions"""
    try:
        # Standard precision
        pct = validate_percentage(15.2569, high_precision=False)
        assert pct == Decimal(
            "15.26"
        ), f"Standard percentage should be 2 decimals, got {pct}"

        # High precision
        pct_high = validate_percentage(15.2569, high_precision=True)
        assert pct_high == Decimal("15.2569") or pct_high == Decimal(
            "15.25"
        ), f"High precision percentage should be 4 decimals, got {pct_high}"

        results.add_pass("Percentage validation (2-4 decimals)")
    except Exception as e:
        results.add_fail("Percentage validation", str(e))


def test_volume_validation():
    """Test volume validation (integer only)"""
    try:
        vol = validate_volume(1000000.5)
        assert vol == 1000000, "Volume should be integer"
        assert isinstance(vol, int), "Volume must be integer type"

        results.add_pass("Volume validation (integer only)")
    except Exception as e:
        results.add_fail("Volume validation", str(e))


def test_currency_validation():
    """Test currency validation and precision"""
    try:
        amount = validate_currency(123456789.5678)
        assert amount == Decimal(
            "123456789.57"
        ), f"Currency should round to 2 decimals, got {amount}"

        results.add_pass("Currency validation (2 decimals)")
    except Exception as e:
        results.add_fail("Currency validation", str(e))


def test_precision_rules_constants():
    """Test PrecisionRules constants"""
    try:
        assert PrecisionRules.PRICE == 2, "Price precision should be 2"
        assert PrecisionRules.PERCENTAGE == 2, "Percentage precision should be 2"
        assert PrecisionRules.RATIO == 4, "Ratio precision should be 4"
        assert PrecisionRules.VOLUME == 0, "Volume precision should be 0"
        assert PrecisionRules.CURRENCY == 2, "Currency precision should be 2"

        results.add_pass("PrecisionRules constants definition")
    except Exception as e:
        results.add_fail("PrecisionRules constants", str(e))


# ============================================================================
# SPECIAL FIELD FORMAT TESTS
# ============================================================================


def test_stock_symbol_validation():
    """Test stock symbol validation (6-digit format)"""
    try:
        # Valid symbols
        StockSymbolFormat.validate("600000")
        StockSymbolFormat.validate("000001")
        StockSymbolFormat.validate("399999")

        results.add_pass("Stock symbol validation (6-digit format)")
    except Exception as e:
        results.add_fail("Stock symbol validation", str(e))


def test_stock_symbol_invalid():
    """Test stock symbol validation rejects invalid formats"""
    try:
        # Should reject non-numeric
        try:
            StockSymbolFormat.validate("60000A")
            results.add_fail(
                "Stock symbol invalid rejection", "Should reject non-numeric"
            )
            return
        except ValueError:
            pass

        # Should reject wrong length
        try:
            StockSymbolFormat.validate("60000")
            results.add_fail(
                "Stock symbol invalid rejection", "Should reject 5-digit code"
            )
            return
        except ValueError:
            pass

        results.add_pass("Stock symbol validation rejects invalid formats")
    except Exception as e:
        results.add_fail("Stock symbol invalid rejection", str(e))


def test_date_validation():
    """Test date validation (YYYY-MM-DD format)"""
    try:
        # String date
        date_str = DateFormat.validate("2025-11-11")
        assert date_str == "2025-11-11"

        # Date object
        date_obj = date(2025, 11, 11)
        date_formatted = DateFormat.validate(date_obj)
        assert date_formatted == "2025-11-11"

        results.add_pass("Date validation (YYYY-MM-DD format)")
    except Exception as e:
        results.add_fail("Date validation", str(e))


def test_data_format_constants():
    """Test DataFormatConstants"""
    try:
        assert DataFormatConstants.TIMEZONE == "UTC"
        assert DataFormatConstants.STOCK_SYMBOL_LENGTH == 6
        assert DataFormatConstants.DEFAULT_PAGE_SIZE == 20
        assert DataFormatConstants.MAX_PAGE_SIZE == 100

        results.add_pass("DataFormatConstants definition")
    except Exception as e:
        results.add_fail("DataFormatConstants", str(e))


# ============================================================================
# RESPONSE SCHEMA TESTS
# ============================================================================


def test_success_response_schema():
    """Test SuccessResponse schema validation"""
    try:
        response = SuccessResponse(
            status="success", code=200, message="Test successful", data={"test": "data"}
        )

        assert response.status == "success"
        assert response.code == 200
        assert response.data == {"test": "data"}
        assert response.timestamp is not None

        results.add_pass("SuccessResponse schema validation")
    except Exception as e:
        results.add_fail("SuccessResponse schema", str(e))


def test_error_response_schema():
    """Test ErrorResponse schema validation"""
    try:
        response = ErrorResponse(
            status="error",
            code=400,
            message="Bad request",
            error="INVALID_INPUT",
            details={"field": "symbol"},
        )

        assert response.status == "error"
        assert response.code == 400
        assert response.error == "INVALID_INPUT"

        results.add_pass("ErrorResponse schema validation")
    except Exception as e:
        results.add_fail("ErrorResponse schema", str(e))


def test_pagination_info_schema():
    """Test PaginationInfo schema with auto-calculation"""
    try:
        pagination = PaginationInfo(page=1, page_size=20, total=100)

        assert pagination.page == 1
        assert pagination.page_size == 20
        assert pagination.total == 100
        assert (
            pagination.pages == 5
        ), f"Should calculate 5 pages for 100 items, got {pagination.pages}"

        results.add_pass("PaginationInfo schema with auto-calculation")
    except Exception as e:
        results.add_fail("PaginationInfo schema", str(e))


def test_paginated_response_schema():
    """Test PaginatedResponse schema"""
    try:
        response = PaginatedResponse(
            status="success",
            code=200,
            message="Data retrieved",
            data={
                "items": [{"id": 1}, {"id": 2}],
                "pagination": {"page": 1, "page_size": 20, "total": 100, "pages": 5},
            },
        )

        assert response.status == "success"
        assert len(response.data["items"]) == 2
        assert response.data["pagination"]["pages"] == 5

        results.add_pass("PaginatedResponse schema validation")
    except Exception as e:
        results.add_fail("PaginatedResponse schema", str(e))


def test_validation_error_response():
    """Test ValidationErrorResponse schema"""
    try:
        response = ValidationErrorResponse(
            status="error",
            code=400,
            message="Validation failed",
            error="VALIDATION_ERROR",
            details={
                "symbol": ["Invalid stock symbol format"],
                "price": ["Price must be positive"],
            },
        )

        assert response.code == 400
        assert response.error == "VALIDATION_ERROR"
        assert len(response.details) == 2

        results.add_pass("ValidationErrorResponse schema")
    except Exception as e:
        results.add_fail("ValidationErrorResponse schema", str(e))


def test_unauthorized_response():
    """Test UnauthorizedResponse schema"""
    try:
        response = UnauthorizedResponse(
            status="error",
            code=401,
            message="Authentication required",
            error="UNAUTHORIZED",
        )

        assert response.code == 401
        assert response.error == "UNAUTHORIZED"

        results.add_pass("UnauthorizedResponse schema")
    except Exception as e:
        results.add_fail("UnauthorizedResponse schema", str(e))


def test_forbidden_response():
    """Test ForbiddenResponse schema"""
    try:
        response = ForbiddenResponse(
            status="error", code=403, message="Permission denied", error="FORBIDDEN"
        )

        assert response.code == 403
        assert response.error == "FORBIDDEN"

        results.add_pass("ForbiddenResponse schema")
    except Exception as e:
        results.add_fail("ForbiddenResponse schema", str(e))


def test_not_found_response():
    """Test NotFoundResponse schema"""
    try:
        response = NotFoundResponse(
            status="error", code=404, message="Resource not found", error="NOT_FOUND"
        )

        assert response.code == 404
        assert response.error == "NOT_FOUND"

        results.add_pass("NotFoundResponse schema")
    except Exception as e:
        results.add_fail("NotFoundResponse schema", str(e))


def test_server_error_response():
    """Test ServerErrorResponse schema"""
    try:
        response = ServerErrorResponse(
            status="error",
            code=500,
            message="Internal server error",
            error="INTERNAL_SERVER_ERROR",
        )

        assert response.code == 500
        assert response.error == "INTERNAL_SERVER_ERROR"

        results.add_pass("ServerErrorResponse schema")
    except Exception as e:
        results.add_fail("ServerErrorResponse schema", str(e))


# ============================================================================
# FIELD SCHEMA TESTS
# ============================================================================


def test_stock_symbol_field_schema():
    """Test StockSymbolField Pydantic schema"""
    try:
        field = StockSymbolField(symbol="600000")
        assert field.symbol == "600000"

        results.add_pass("StockSymbolField Pydantic schema")
    except Exception as e:
        results.add_fail("StockSymbolField schema", str(e))


def test_price_field_schema():
    """Test PriceField Pydantic schema"""
    try:
        field = PriceField(price=150.50)
        assert field.price == Decimal("150.50")

        results.add_pass("PriceField Pydantic schema")
    except Exception as e:
        results.add_fail("PriceField schema", str(e))


def test_percentage_field_schema():
    """Test PercentageField Pydantic schema"""
    try:
        field = PercentageField(percentage=15.25)
        assert field.percentage == Decimal("15.25")

        results.add_pass("PercentageField Pydantic schema")
    except Exception as e:
        results.add_fail("PercentageField schema", str(e))


def test_volume_field_schema():
    """Test VolumeField Pydantic schema"""
    try:
        field = VolumeField(volume=1000000)
        assert field.volume == 1000000

        results.add_pass("VolumeField Pydantic schema")
    except Exception as e:
        results.add_fail("VolumeField schema", str(e))


def test_currency_field_schema():
    """Test CurrencyField Pydantic schema"""
    try:
        field = CurrencyField(amount=123456789.50)
        assert field.amount == Decimal("123456789.50")

        results.add_pass("CurrencyField Pydantic schema")
    except Exception as e:
        results.add_fail("CurrencyField schema", str(e))


def test_date_field_schema():
    """Test DateField Pydantic schema"""
    try:
        field = DateField(date="2025-11-11")
        assert field.date == "2025-11-11"

        results.add_pass("DateField Pydantic schema")
    except Exception as e:
        results.add_fail("DateField schema", str(e))


def test_timestamp_field_schema():
    """Test TimestampField Pydantic schema"""
    try:
        field = TimestampField()
        assert field.timestamp is not None
        assert isinstance(field.timestamp, str)

        results.add_pass("TimestampField Pydantic schema")
    except Exception as e:
        results.add_fail("TimestampField schema", str(e))


# ============================================================================
# VALIDATION UTILITY TESTS
# ============================================================================


def test_http_header_formats():
    """Test HTTPHeaderFormats validation"""
    try:
        # Valid Bearer token format
        valid_token = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9"
        assert HTTPHeaderFormats.validate_bearer_token(valid_token)

        results.add_pass("HTTPHeaderFormats Bearer token validation")
    except Exception as e:
        results.add_fail("HTTPHeaderFormats", str(e))


def test_data_format_validator():
    """Test DataFormatValidator utilities"""
    try:
        # Validate all formats
        data = {
            "symbol": "600000",
            "price": 150.50,
            "volume": 1000000,
        }

        validated = DataFormatValidator.validate_all_formats(data)
        assert validated["symbol"] == "600000"
        assert validated["price"] == Decimal("150.50")
        assert validated["volume"] == 1000000

        results.add_pass("DataFormatValidator.validate_all_formats")
    except Exception as e:
        results.add_fail("DataFormatValidator", str(e))


def test_response_format_validation():
    """Test DataFormatValidator.validate_response_format"""
    try:
        response = {
            "status": "success",
            "code": 200,
            "message": "OK",
            "timestamp": "2025-11-11T12:34:56.789Z",
        }

        is_valid = DataFormatValidator.validate_response_format(response)
        assert is_valid, "Response should be valid"

        results.add_pass("DataFormatValidator response format validation")
    except Exception as e:
        results.add_fail("DataFormatValidator response validation", str(e))


# ============================================================================
# PAGINATION REQUEST TESTS
# ============================================================================


def test_pagination_request_schema():
    """Test PaginationRequest schema"""
    try:
        pagination = PaginationRequest(page=2, page_size=50)
        assert pagination.page == 2
        assert pagination.page_size == 50

        # Test defaults
        pagination_default = PaginationRequest()
        assert pagination_default.page == 1
        assert pagination_default.page_size == 20

        results.add_pass("PaginationRequest schema")
    except Exception as e:
        results.add_fail("PaginationRequest schema", str(e))


# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================


def run_all_tests():
    """Run all test suites"""
    print("\n" + "=" * 70)
    print("DATA FORMAT CONVENTIONS AND SCHEMAS TEST SUITE")
    print("=" * 70)

    print("\n[1] Timestamp Format Tests")
    test_iso_timestamp_format()
    test_millisecond_timestamp_format()
    test_timestamp_format_enum()

    print("\n[2] Decimal Precision Tests")
    test_price_validation()
    test_percentage_validation()
    test_volume_validation()
    test_currency_validation()
    test_precision_rules_constants()

    print("\n[3] Special Field Format Tests")
    test_stock_symbol_validation()
    test_stock_symbol_invalid()
    test_date_validation()
    test_data_format_constants()

    print("\n[4] Response Schema Tests")
    test_success_response_schema()
    test_error_response_schema()
    test_pagination_info_schema()
    test_paginated_response_schema()
    test_validation_error_response()
    test_unauthorized_response()
    test_forbidden_response()
    test_not_found_response()
    test_server_error_response()

    print("\n[5] Field Schema Tests")
    test_stock_symbol_field_schema()
    test_price_field_schema()
    test_percentage_field_schema()
    test_volume_field_schema()
    test_currency_field_schema()
    test_date_field_schema()
    test_timestamp_field_schema()

    print("\n[6] Validation Utility Tests")
    test_http_header_formats()
    test_data_format_validator()
    test_response_format_validation()

    print("\n[7] Pagination Request Tests")
    test_pagination_request_schema()

    # Print summary
    results.print_summary()

    # Return exit code
    return 0 if results.failed == 0 else 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
