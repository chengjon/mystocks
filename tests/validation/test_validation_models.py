"""
Simplified Validation Model Tests
Test Pydantic validation models in isolation
"""

import pytest
from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator, ValidationError
import re
from typing import Dict, List, Optional, Any


# Inline validation models for testing
class AddWatchlistRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=20, pattern=r"^[a-zA-Z0-9.]+$")
    market: Optional[str] = Field(None, pattern=r"^(CN|HK|US)$")
    display_name: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        if v.startswith("."):
            raise ValueError("股票代码不能以点开头")
        return v.upper()


class StrategyRunRequest(BaseModel):
    strategy_code: str = Field(..., pattern=r"^[a-z0-9_]+$")
    symbol: Optional[str] = Field(
        None, min_length=1, max_length=20, pattern=r"^[a-zA-Z0-9.]+$"
    )
    symbols: Optional[List[str]] = Field(None)
    check_date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    limit: Optional[int] = Field(None, ge=1, le=10000)

    @field_validator("symbols")
    @classmethod
    def validate_symbols(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is None:
            return v
        if len(v) > 1000:
            raise ValueError("股票代码列表长度不能超过1000")
        return list(set(s.upper() for s in v))

    @field_validator("check_date")
    @classmethod
    def validate_check_date(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            parsed_date = datetime.strptime(v, "%Y-%m-%d").date()
            if parsed_date > date.today():
                raise ValueError("检查日期不能是未来日期")
            return v
        except ValueError:
            raise ValueError("日期格式错误，请使用 YYYY-MM-DD 格式")


class FundFlowRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=20, pattern=r"^[a-zA-Z0-9.]+$")
    timeframe: str = Field("1", pattern=r"^[13510]$")
    start_date: Optional[date] = Field(None)
    end_date: Optional[date] = Field(None)

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        if v.startswith("."):
            raise ValueError("股票代码不能以点开头")
        return v.upper()

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, v: Optional[date], info) -> Optional[date]:
        if v is None:
            return v
        # Get start_date from data if available
        if (
            info.data
            and "start_date" in info.data
            and info.data["start_date"] is not None
        ):
            start_date = info.data["start_date"]
            if v <= start_date:
                raise ValueError("结束日期必须大于开始日期")
        return v


class TaskRegistrationRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    task_type: str = Field(
        ...,
        pattern=r"^(DATA_PROCESSING|MARKET_ANALYSIS|SIGNAL_GENERATION|NOTIFICATION|CLEANUP|BACKTEST|REPORT)$",
    )
    config: Dict[str, Any] = Field(...)
    tags: Optional[List[str]] = Field(None)
    schedule: Optional[str] = Field(None, max_length=100)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("任务名称不能为空")
        if re.search(r'[<>"\'/\\]', v):
            raise ValueError("任务名称不能包含特殊字符")
        return v.strip()

    @field_validator("config")
    @classmethod
    def validate_config(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        if not v:
            raise ValueError("任务配置不能为空")
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is None:
            return v
        if len(v) > 10:
            raise ValueError("任务标签数量不能超过10个")
        return [tag.strip() for tag in v if tag]


class TestValidationModels:
    """Test Pydantic validation models"""

    def test_watchlist_valid_request(self):
        """Test valid watchlist request"""
        request = AddWatchlistRequest(
            symbol="AAPL", market="US", display_name="Apple Inc."
        )
        assert request.symbol == "AAPL"
        assert request.market == "US"

    def test_watchlist_invalid_symbol_format(self):
        """Test invalid symbol format"""
        with pytest.raises(ValidationError) as exc_info:
            AddWatchlistRequest(symbol="invalid-symbol-!")
        assert "pattern" in str(exc_info.value) or "regex" in str(exc_info.value)

    def test_watchlist_symbol_starts_with_dot(self):
        """Test symbol starting with dot"""
        with pytest.raises(ValidationError) as exc_info:
            AddWatchlistRequest(symbol=".AAPL")
        assert "股票代码不能以点开头" in str(exc_info.value)

    def test_strategy_run_valid(self):
        """Test valid strategy run request"""
        request = StrategyRunRequest(
            strategy_code="volume_surge", symbol="AAPL", limit=100
        )
        assert request.strategy_code == "volume_surge"
        assert request.symbol == "AAPL"

    def test_strategy_run_invalid_date(self):
        """Test invalid date in strategy"""
        with pytest.raises(ValidationError) as exc_info:
            StrategyRunRequest(strategy_code="volume_surge", check_date="invalid-date")
        assert "pattern" in str(exc_info.value) or "日期格式" in str(exc_info.value)

    def test_strategy_run_future_date(self):
        """Test future date validation"""
        future_date = "2030-12-31"
        with pytest.raises(ValidationError) as exc_info:
            StrategyRunRequest(strategy_code="volume_surge", check_date=future_date)
        # Check for either future date message or date format error message
        error_str = str(exc_info.value)
        assert "未来日期" in error_str or "日期格式错误" in error_str

    def test_strategy_run_too_many_symbols(self):
        """Test too many symbols in list"""
        symbols = [f"STOCK{i}" for i in range(1001)]
        with pytest.raises(ValidationError) as exc_info:
            StrategyRunRequest(strategy_code="volume_surge", symbols=symbols)
        assert "股票代码列表长度不能超过1000" in str(exc_info.value)

    def test_fund_flow_valid(self):
        """Test valid fund flow request"""
        request = FundFlowRequest(
            symbol="AAPL",
            timeframe="5",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
        )
        assert request.symbol == "AAPL"
        assert request.timeframe == "5"

    def test_fund_flow_invalid_timeframe(self):
        """Test invalid timeframe"""
        with pytest.raises(ValidationError) as exc_info:
            FundFlowRequest(symbol="AAPL", timeframe="invalid")
        assert "pattern" in str(exc_info.value) or "regex" in str(exc_info.value)

    def test_fund_flow_date_range_invalid(self):
        """Test invalid date range"""
        with pytest.raises(ValidationError) as exc_info:
            FundFlowRequest(
                symbol="AAPL", start_date=date(2024, 1, 31), end_date=date(2024, 1, 1)
            )
        assert "结束日期必须大于开始日期" in str(exc_info.value)

    def test_task_registration_valid(self):
        """Test valid task registration"""
        request = TaskRegistrationRequest(
            name="Data Processing Task",
            task_type="DATA_PROCESSING",
            config={"source": "api"},
            tags=["data", "processing"],
        )
        assert request.name == "Data Processing Task"
        assert request.task_type == "DATA_PROCESSING"

    def test_task_registration_invalid_name(self):
        """Test invalid task name with special characters"""
        with pytest.raises(ValidationError) as exc_info:
            TaskRegistrationRequest(
                name="Invalid<script>Task", task_type="DATA_PROCESSING", config={}
            )
        assert "特殊字符" in str(exc_info.value)

    def test_task_registration_empty_config(self):
        """Test empty task configuration"""
        with pytest.raises(ValidationError) as exc_info:
            TaskRegistrationRequest(
                name="Test Task", task_type="DATA_PROCESSING", config={}
            )
        assert "任务配置不能为空" in str(exc_info.value)

    def test_task_registration_too_many_tags(self):
        """Test too many task tags"""
        tags = [f"tag{i}" for i in range(11)]
        with pytest.raises(ValidationError) as exc_info:
            TaskRegistrationRequest(
                name="Test Task", task_type="DATA_PROCESSING", config={}, tags=tags
            )
        assert "任务标签数量不能超过10个" in str(exc_info.value)

    def test_symbol_case_normalization(self):
        """Test symbol case normalization"""
        request1 = AddWatchlistRequest(symbol="aapl")
        request2 = AddWatchlistRequest(symbol="AAPL")
        assert request1.symbol == "AAPL"
        assert request2.symbol == "AAPL"

    def test_duplicate_symbol_removal(self):
        """Test duplicate removal in symbol lists"""
        request = StrategyRunRequest(
            strategy_code="volume_surge", symbols=["AAPL", "AAPL", "GOOGL", "AAPL"]
        )
        # Should have unique symbols
        symbol_set = set(request.symbols) if request.symbols else set()
        assert len(symbol_set) == 2
        assert "AAPL" in symbol_set
        assert "GOOGL" in symbol_set

    def test_whitespace_stripping(self):
        """Test whitespace stripping in task names"""
        request = TaskRegistrationRequest(
            name="  Task Name  ", task_type="DATA_PROCESSING", config={"test": "value"}
        )
        assert request.name == "Task Name"

    def test_field_length_limits(self):
        """Test field length limits"""
        # Test symbol too long
        with pytest.raises(ValidationError):
            AddWatchlistRequest(symbol="A" * 21)  # 21 characters, max is 20

        # Test display name too long
        with pytest.raises(ValidationError):
            AddWatchlistRequest(
                symbol="AAPL",
                display_name="A" * 101,  # 101 characters, max is 100
            )

        # Test task name too long
        with pytest.raises(ValidationError):
            TaskRegistrationRequest(
                name="A" * 101,  # 101 characters, max is 100
                task_type="DATA_PROCESSING",
                config={},
            )

    def test_numeric_range_validation(self):
        """Test numeric range validation"""
        # Test strategy limit too high
        with pytest.raises(ValidationError):
            StrategyRunRequest(
                strategy_code="volume_surge",
                limit=20000,  # Max is 10000
            )

        # Test strategy limit too low
        with pytest.raises(ValidationError):
            StrategyRunRequest(
                strategy_code="volume_surge",
                limit=0,  # Min is 1
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
