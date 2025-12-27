"""
Data Format Conventions Module

This module defines all data format standards for the MyStocks API, including:
- Timestamp formats (REST vs WebSocket)
- Decimal precision rules for different data types
- Special field formats (stock symbols, dates, durations)
- Validation utilities and constants

Used across all API endpoints and data models to ensure consistency.
Reference: docs/api/API_SPECIFICATION.md
"""

from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Union, Optional, Any
from pydantic import BaseModel, Field, validator
import re


# ============================================================================
# TIMESTAMP FORMATS
# ============================================================================


class TimestampFormat(str, Enum):
    """Supported timestamp formats"""

    ISO_8601 = "ISO_8601"  # For REST API: "2025-11-11T12:34:56.789Z"
    MILLISECONDS = "MILLISECONDS"  # For WebSocket: 1699267200000 (UTC ms)
    SECONDS = "SECONDS"  # Alternative: 1699267200 (UTC seconds)


def get_current_iso_timestamp() -> str:
    """Get current timestamp in ISO 8601 format (REST API standard)"""
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def get_current_ms_timestamp() -> int:
    """Get current timestamp in milliseconds (WebSocket standard)"""
    return int(datetime.utcnow().timestamp() * 1000)


def get_current_seconds_timestamp() -> int:
    """Get current timestamp in seconds"""
    return int(datetime.utcnow().timestamp())


def parse_iso_timestamp(timestamp_str: str) -> datetime:
    """Parse ISO 8601 timestamp string"""
    if timestamp_str.endswith("Z"):
        timestamp_str = timestamp_str[:-1] + "+00:00"
    return datetime.fromisoformat(timestamp_str)


def parse_ms_timestamp(timestamp_ms: int) -> datetime:
    """Parse millisecond timestamp"""
    return datetime.utcfromtimestamp(timestamp_ms / 1000)


# ============================================================================
# DECIMAL PRECISION RULES
# ============================================================================


class DecimalPrecision(str, Enum):
    """Decimal precision specifications for different data types"""

    PRICE = "2"  # Stock prices: 1850.50
    PERCENTAGE = "2-4"  # Percentages: 1.50%, 15.25%
    RATIO = "4"  # Ratios/indices: 12.3456
    VOLUME = "0"  # Trading volume: 1000000 (integer)
    CURRENCY = "2"  # Currency amounts: 123456789.50
    PRECISION = "6"  # High precision: 0.123456


def round_to_precision(value: Union[float, Decimal], decimal_places: int) -> Decimal:
    """Round value to specified decimal places"""
    if isinstance(value, float):
        value = Decimal(str(value))
    return value.quantize(Decimal(10) ** -decimal_places)


class PrecisionRules:
    """Static precision rules for different data types"""

    PRICE = 2  # Stock price precision
    PERCENTAGE = 2  # Percentage precision (for normal percentages)
    PERCENTAGE_HIGH = 4  # High precision percentages
    RATIO = 4  # Ratio/index precision
    VOLUME = 0  # Volume is integer
    CURRENCY = 2  # Currency precision
    MARKET_CAP = 2  # Market cap precision


def validate_price(value: Union[float, Decimal]) -> Decimal:
    """Validate and round price to standard precision (2 decimals)"""
    if isinstance(value, str):
        value = Decimal(value)
    elif isinstance(value, float):
        value = Decimal(str(value))

    if value < 0:
        raise ValueError(f"Price cannot be negative: {value}")

    return round_to_precision(value, PrecisionRules.PRICE)


def validate_percentage(value: Union[float, Decimal], high_precision: bool = False) -> Decimal:
    """Validate and round percentage to standard precision"""
    if isinstance(value, str):
        value = Decimal(value)
    elif isinstance(value, float):
        value = Decimal(str(value))

    precision = PrecisionRules.PERCENTAGE_HIGH if high_precision else PrecisionRules.PERCENTAGE
    return round_to_precision(value, precision)


def validate_volume(value: Union[int, float]) -> int:
    """Validate volume (must be integer)"""
    volume = int(value)
    if volume < 0:
        raise ValueError(f"Volume cannot be negative: {volume}")
    return volume


def validate_currency(value: Union[float, Decimal]) -> Decimal:
    """Validate and round currency to standard precision (2 decimals)"""
    if isinstance(value, str):
        value = Decimal(value)
    elif isinstance(value, float):
        value = Decimal(str(value))

    return round_to_precision(value, PrecisionRules.CURRENCY)


# ============================================================================
# SPECIAL FIELD FORMATS
# ============================================================================


class StockSymbolFormat(str):
    """Stock symbol format: 6-digit code without prefix"""

    PATTERN = re.compile(r"^\d{6}$")

    @classmethod
    def validate(cls, value: str) -> str:
        """Validate stock symbol format"""
        if not isinstance(value, str):
            raise TypeError(f"Stock symbol must be string, got {type(value)}")

        if not cls.PATTERN.match(value):
            raise ValueError(f"Invalid stock symbol format: {value}. Expected 6 digits.")

        return value


class DateFormat:
    """Date format: YYYY-MM-DD"""

    PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

    @classmethod
    def validate(cls, value: Union[str, date]) -> str:
        """Validate and convert date to string format"""
        if isinstance(value, date):
            return value.strftime("%Y-%m-%d")

        if not isinstance(value, str):
            raise TypeError(f"Date must be string or date object, got {type(value)}")

        if not cls.PATTERN.match(value):
            raise ValueError(f"Invalid date format: {value}. Expected YYYY-MM-DD.")

        return value


class DurationFormat:
    """Duration format: ISO 8601 duration (e.g., "PT1H30M" for 1.5 hours)"""

    PATTERN = re.compile(r"^P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?)?$")

    @classmethod
    def validate(cls, value: str) -> str:
        """Validate ISO 8601 duration format"""
        if not isinstance(value, str):
            raise TypeError(f"Duration must be string, got {type(value)}")

        if not cls.PATTERN.match(value):
            raise ValueError(f"Invalid duration format: {value}. Expected ISO 8601 format (e.g., 'PT1H30M').")

        return value

    @classmethod
    def to_seconds(cls, value: str) -> float:
        """Convert ISO 8601 duration to seconds"""
        # Simple implementation - can be extended
        match = cls.PATTERN.match(value)
        if not match:
            raise ValueError(f"Invalid duration format: {value}")

        days, hours, minutes, seconds = match.groups()
        total_seconds = 0.0

        if days:
            total_seconds += int(days) * 86400
        if hours:
            total_seconds += int(hours) * 3600
        if minutes:
            total_seconds += int(minutes) * 60
        if seconds:
            total_seconds += float(seconds)

        return total_seconds


class BooleanFormat:
    """Boolean format: true/false (JSON standard)"""

    @classmethod
    def validate(cls, value: Any) -> bool:
        """Convert to boolean if necessary"""
        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            if value.lower() in ("true", "1", "yes", "on"):
                return True
            elif value.lower() in ("false", "0", "no", "off"):
                return False
            else:
                raise ValueError(f"Invalid boolean value: {value}")

        if isinstance(value, int):
            return bool(value)

        raise TypeError(f"Cannot convert {type(value)} to boolean")


class NullFormat:
    """Null format: null in JSON (None in Python)"""

    @classmethod
    def validate(cls, value: Optional[Any]) -> Optional[Any]:
        """Ensure value is None if null"""
        if value is None or (isinstance(value, str) and value.lower() == "null"):
            return None
        return value


# ============================================================================
# BASE PYDANTIC MODELS WITH FORMAT VALIDATION
# ============================================================================


class FormattedDecimal(BaseModel):
    """Base model for Decimal fields with automatic precision handling"""

    value: Decimal

    class Config:
        json_encoders = {Decimal: lambda v: float(v)}
        arbitrary_types_allowed = True


class PriceField(BaseModel):
    """Price field with 2-decimal precision validation"""

    value: Decimal = Field(..., ge=0)

    @validator("value", pre=True)
    def validate_price_precision(cls, v):
        return validate_price(v)

    class Config:
        json_encoders = {Decimal: lambda v: float(v)}
        arbitrary_types_allowed = True


class PercentageField(BaseModel):
    """Percentage field with 2-4 decimal precision"""

    value: Decimal
    high_precision: bool = False

    @validator("value", pre=True)
    def validate_percentage_precision(cls, v):
        return validate_percentage(v)

    class Config:
        json_encoders = {Decimal: lambda v: float(v)}
        arbitrary_types_allowed = True


class VolumeField(BaseModel):
    """Volume field (integer only)"""

    value: int = Field(..., ge=0)

    @validator("value", pre=True)
    def validate_volume_value(cls, v):
        return validate_volume(v)


class CurrencyField(BaseModel):
    """Currency field with 2-decimal precision"""

    value: Decimal = Field(...)

    @validator("value", pre=True)
    def validate_currency_value(cls, v):
        return validate_currency(v)

    class Config:
        json_encoders = {Decimal: lambda v: float(v)}
        arbitrary_types_allowed = True


class StockSymbolField(BaseModel):
    """Stock symbol field (6-digit code)"""

    value: str = Field(..., min_length=6, max_length=6)

    @validator("value")
    def validate_symbol(cls, v):
        return StockSymbolFormat.validate(v)


class DateField(BaseModel):
    """Date field (YYYY-MM-DD format)"""

    value: Union[str, date]

    @validator("value", pre=True)
    def validate_date(cls, v):
        return DateFormat.validate(v)


class TimestampField(BaseModel):
    """Timestamp field with format specification"""

    value: Union[str, int]
    format: TimestampFormat = TimestampFormat.ISO_8601

    @validator("value", pre=True)
    def validate_timestamp(cls, v, values):
        format_type = values.get("format", TimestampFormat.ISO_8601)

        if format_type == TimestampFormat.ISO_8601:
            if not isinstance(v, str):
                raise ValueError(f"ISO 8601 timestamp must be string, got {type(v)}")
            parse_iso_timestamp(v)  # Validate by parsing
            return v
        elif format_type == TimestampFormat.MILLISECONDS:
            if not isinstance(v, int):
                raise ValueError(f"Millisecond timestamp must be int, got {type(v)}")
            if v < 0:
                raise ValueError(f"Timestamp cannot be negative: {v}")
            return v

        return v


# ============================================================================
# HTTP HEADER FORMATS
# ============================================================================


class HTTPHeaderFormats:
    """Standard HTTP header value formats"""

    # Content-Type for JSON responses
    JSON = "application/json"

    # Authorization header format: "Bearer <token>"
    BEARER_TOKEN_PATTERN = re.compile(r"^Bearer\s+[A-Za-z0-9\-._~+/]+=*$")

    # CSRF token format (UUID)
    CSRF_TOKEN_PATTERN = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")

    @classmethod
    def validate_bearer_token(cls, token: str) -> bool:
        """Validate Bearer token format"""
        return bool(cls.BEARER_TOKEN_PATTERN.match(token))

    @classmethod
    def validate_csrf_token(cls, token: str) -> bool:
        """Validate CSRF token format (UUID)"""
        return bool(cls.CSRF_TOKEN_PATTERN.match(token.lower()))


# ============================================================================
# DATA FORMAT CONSTANTS
# ============================================================================


class DataFormatConstants:
    """Global data format constants"""

    # Date/Time
    TIMEZONE = "UTC"
    ISO_8601_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M:%S"

    # Numeric
    MIN_PRICE = Decimal("0.00")
    MAX_PRICE = Decimal("99999.99")
    MIN_PERCENTAGE = Decimal("-100.00")
    MAX_PERCENTAGE = Decimal("100.00")

    # Stock
    STOCK_SYMBOL_LENGTH = 6
    STOCK_CODE_A_RANGE = ("600000", "609999")  # Shanghai A-shares
    STOCK_CODE_B_RANGE = ("900000", "909999")  # Shanghai B-shares
    STOCK_CODE_SZ_A_RANGE = ("000000", "004999")  # Shenzhen A-shares
    STOCK_CODE_SZ_B_RANGE = ("200000", "209999")  # Shenzhen B-shares
    STOCK_CODE_CY_RANGE = ("300000", "399999")  # ChiNext/GEM

    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MIN_PAGE_SIZE = 1
    MAX_PAGE_SIZE = 100

    # Rate limiting
    DEFAULT_RATE_LIMIT = 1000  # requests per hour
    DEFAULT_BURST_LIMIT = 100  # requests per second

    # Timeout values (seconds)
    DEFAULT_TIMEOUT = 30
    WEBSOCKET_TIMEOUT = 60
    STREAMING_TIMEOUT = 300


# ============================================================================
# VALIDATION UTILITIES
# ============================================================================


class DataFormatValidator:
    """Comprehensive data format validation utilities"""

    @staticmethod
    def validate_all_formats(data: dict) -> dict:
        """Validate all data format conventions in a dictionary"""
        validated = {}

        for key, value in data.items():
            # Auto-detect and validate based on key patterns
            if "price" in key.lower():
                validated[key] = validate_price(value)
            elif "percent" in key.lower() or "rate" in key.lower():
                validated[key] = validate_percentage(value)
            elif "volume" in key.lower():
                validated[key] = validate_volume(value)
            elif "symbol" in key.lower() or "code" in key.lower():
                validated[key] = StockSymbolFormat.validate(value)
            elif "date" in key.lower():
                validated[key] = DateFormat.validate(value)
            elif "timestamp" in key.lower() or "time" in key.lower():
                # Keep as-is, format is context-dependent
                validated[key] = value
            else:
                validated[key] = value

        return validated

    @staticmethod
    def validate_response_format(response: dict) -> bool:
        """Validate that response follows standard format"""
        required_fields = ["status", "code", "message", "timestamp"]

        if "data" in response and isinstance(response["data"], dict):
            if "pagination" in response["data"]:
                required_fields.extend(["page", "page_size", "total", "pages"])

        return all(field in response for field in required_fields)

    @staticmethod
    def validate_websocket_message(message: dict) -> bool:
        """Validate that WebSocket message follows standard format"""
        required_fields = ["type", "timestamp"]

        if message.get("type") == "request":
            required_fields.extend(["request_id", "action"])
        elif message.get("type") == "response":
            required_fields.extend(["request_id", "success"])
        elif message.get("type") == "error":
            required_fields.extend(["error_code", "error_message"])

        return all(field in message for field in required_fields)


if __name__ == "__main__":
    # Example usage
    print("Data Format Conventions Module")
    print("=" * 50)

    # Example: Price validation
    price = validate_price(123.456)
    print(f"Price validation: 123.456 → {price}")

    # Example: Percentage validation
    percentage = validate_percentage(15.2569, high_precision=True)
    print(f"Percentage validation: 15.2569 → {percentage}")

    # Example: Timestamp formats
    iso_ts = get_current_iso_timestamp()
    ms_ts = get_current_ms_timestamp()
    print(f"Current ISO timestamp: {iso_ts}")
    print(f"Current millisecond timestamp: {ms_ts}")

    # Example: Stock symbol validation
    symbol = StockSymbolFormat.validate("600000")
    print(f"Stock symbol validation: 600000 → {symbol}")

    print("\n✅ Data format conventions module initialized successfully")
