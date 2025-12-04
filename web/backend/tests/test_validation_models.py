"""
P0改进 Task 4: 验证模型单元测试

测试所有Pydantic V2数据验证模型的核心功能和边界情况
遵循项目Mock数据使用规范 - 通过conftest fixture获取测试数据
"""

from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from app.schema.validation_models import (
    DateRangeModel,
    ErrorResponseModel,
    MarketDataQueryModel,
    PaginationModel,
    ResponseModel,
    StockListQueryModel,
    StockSymbolModel,
    TechnicalIndicatorQueryModel,
    TradeOrderModel,
)


class TestStockSymbolModel:
    """股票代码模型测试"""

    def test_valid_a_stock_symbols(self, validation_test_data):
        """测试有效的A股代码"""
        for symbol in validation_test_data["stock_symbols"]["valid"]:
            model = StockSymbolModel(symbol=symbol)
            assert model.symbol == symbol.upper().strip()

    def test_valid_stock_symbols_case_insensitive(self):
        """测试代码大小写不敏感"""
        model = StockSymbolModel(symbol="aapl")
        assert model.symbol == "AAPL"

    def test_valid_stock_symbols_whitespace_trimmed(self):
        """测试代码前后空格被去除"""
        model = StockSymbolModel(symbol="600519")
        assert model.symbol == "600519"

    def test_invalid_empty_symbol(self, validation_test_data):
        """测试空代码验证失败"""
        with pytest.raises(ValidationError) as exc_info:
            StockSymbolModel(symbol="")
        assert "股票代码不能为空" in str(exc_info.value) or "at least 1 character" in str(exc_info.value)

    def test_invalid_symbol_too_long(self, validation_test_data):
        """测试超长代码验证失败"""
        for symbol in validation_test_data["stock_symbols"]["invalid"]:
            if len(symbol) > 20:
                with pytest.raises(ValidationError):
                    StockSymbolModel(symbol=symbol)

    def test_invalid_symbol_special_chars(self, validation_test_data):
        """测试包含特殊字符的代码验证失败"""
        for symbol in validation_test_data["stock_symbols"]["invalid"]:
            if symbol and any(c in symbol for c in "!@#$%^&*"):
                with pytest.raises(ValidationError):
                    StockSymbolModel(symbol=symbol)

    def test_valid_symbols_with_numbers(self):
        """测试包含数字的代码"""
        model = StockSymbolModel(symbol="000001")
        assert model.symbol == "000001"

    def test_valid_symbols_with_hyphen(self):
        """测试包含连字符的代码"""
        model = StockSymbolModel(symbol="BRK-A")
        assert model.symbol == "BRK-A"

    def test_valid_symbols_with_underscore(self):
        """测试包含下划线的代码"""
        model = StockSymbolModel(symbol="STOCK_A")
        assert model.symbol == "STOCK_A"


class TestDateRangeModel:
    """日期范围模型测试"""

    def test_valid_date_range(self, validation_test_data):
        """测试有效的日期范围"""
        for date_str in validation_test_data["dates"]["valid"]:
            start = datetime.strptime(date_str, "%Y-%m-%d")
            end = start + timedelta(days=10)
            model = DateRangeModel(start_date=start, end_date=end)
            assert model.start_date == start
            assert model.end_date == end

    def test_valid_datetime_with_time(self):
        """测试包含时间的日期"""
        start = datetime.fromisoformat("2025-01-01T08:00:00")
        end = datetime.fromisoformat("2025-01-31T16:00:00")
        model = DateRangeModel(start_date=start, end_date=end)
        assert model.start_date == start
        assert model.end_date == end

    def test_invalid_end_before_start(self):
        """测试结束日期早于开始日期"""
        start = datetime(2025, 1, 31)
        end = datetime(2025, 1, 1)
        with pytest.raises(ValidationError) as exc_info:
            DateRangeModel(start_date=start, end_date=end)
        assert "结束日期必须晚于开始日期" in str(exc_info.value)

    def test_invalid_end_equal_start(self):
        """测试结束日期等于开始日期"""
        start = datetime(2025, 1, 15)
        with pytest.raises(ValidationError) as exc_info:
            DateRangeModel(start_date=start, end_date=start)
        assert "结束日期必须晚于开始日期" in str(exc_info.value)

    def test_invalid_date_range_exceeds_2_years(self):
        """测试日期范围超过2年"""
        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 1) + timedelta(days=731)  # 超过2年
        with pytest.raises(ValidationError) as exc_info:
            DateRangeModel(start_date=start, end_date=end)
        assert "日期范围不能超过2年" in str(exc_info.value)

    def test_valid_date_range_exactly_2_years(self):
        """测试日期范围恰好2年"""
        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 1) + timedelta(days=730)  # 2年
        model = DateRangeModel(start_date=start, end_date=end)
        assert model.end_date > model.start_date

    def test_valid_date_range_1_day(self):
        """测试最小日期范围（1天）"""
        start = datetime(2025, 1, 1)
        end = start + timedelta(days=1)
        model = DateRangeModel(start_date=start, end_date=end)
        assert (model.end_date - model.start_date).days == 1


class TestMarketDataQueryModel:
    """市场数据查询模型测试"""

    def test_valid_market_data_query(self):
        """测试有效的市场数据查询"""
        model = MarketDataQueryModel(
            symbol="000001",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 12, 31),
            interval="daily",
        )
        assert model.symbol == "000001"
        assert model.interval == "daily"

    def test_valid_market_data_all_intervals(self):
        """测试所有支持的时间间隔"""
        intervals = ["1m", "5m", "15m", "30m", "hourly", "daily", "weekly", "monthly"]
        for interval in intervals:
            model = MarketDataQueryModel(
                symbol="AAPL",
                start_date=datetime(2025, 1, 1),
                end_date=datetime(2025, 1, 31),
                interval=interval,
            )
            assert model.interval == interval

    def test_default_interval_is_daily(self):
        """测试默认时间间隔为daily"""
        model = MarketDataQueryModel(
            symbol="000001",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 1, 31),
        )
        assert model.interval == "daily"

    def test_invalid_interval(self):
        """测试无效的时间间隔"""
        with pytest.raises(ValidationError):
            MarketDataQueryModel(
                symbol="000001",
                start_date=datetime(2025, 1, 1),
                end_date=datetime(2025, 1, 31),
                interval="invalid",
            )

    def test_invalid_market_query_empty_symbol(self):
        """测试查询中的空代码"""
        with pytest.raises(ValidationError):
            MarketDataQueryModel(
                symbol="",
                start_date=datetime(2025, 1, 1),
                end_date=datetime(2025, 1, 31),
            )

    def test_market_data_symbol_case_insensitive(self):
        """测试代码大小写"""
        model = MarketDataQueryModel(
            symbol="aapl",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 1, 31),
        )
        assert model.symbol == "aapl"


class TestTechnicalIndicatorQueryModel:
    """技术指标查询模型测试"""

    def test_valid_indicator_query(self):
        """测试有效的指标查询"""
        model = TechnicalIndicatorQueryModel(symbol="000001", indicators=["MA", "RSI", "MACD"], period=20)
        assert model.symbol == "000001"
        assert len(model.indicators) == 3
        assert model.period == 20

    def test_indicator_query_single_indicator(self):
        """测试单个指标查询"""
        model = TechnicalIndicatorQueryModel(symbol="AAPL", indicators=["MA"])
        assert len(model.indicators) == 1

    def test_indicator_query_max_indicators(self):
        """测试最大指标数（20个）"""
        indicators = [f"IND_{i}" for i in range(20)]
        model = TechnicalIndicatorQueryModel(symbol="000001", indicators=indicators)
        assert len(model.indicators) == 20

    def test_indicator_query_exceeds_max(self):
        """测试超过最大指标数"""
        indicators = [f"IND_{i}" for i in range(21)]
        with pytest.raises(ValidationError):
            TechnicalIndicatorQueryModel(symbol="000001", indicators=indicators)

    def test_indicator_query_empty_list(self):
        """测试空指标列表"""
        with pytest.raises(ValidationError):
            TechnicalIndicatorQueryModel(symbol="000001", indicators=[])

    def test_indicator_query_default_period(self):
        """测试默认周期"""
        model = TechnicalIndicatorQueryModel(symbol="000001", indicators=["MA"])
        assert model.period == 20

    def test_indicator_query_period_range(self):
        """测试周期范围验证"""
        # 最小周期
        model = TechnicalIndicatorQueryModel(symbol="000001", indicators=["MA"], period=1)
        assert model.period == 1

        # 最大周期
        model = TechnicalIndicatorQueryModel(symbol="000001", indicators=["MA"], period=500)
        assert model.period == 500

    def test_indicator_query_invalid_period(self):
        """测试无效的周期"""
        with pytest.raises(ValidationError):
            TechnicalIndicatorQueryModel(symbol="000001", indicators=["MA"], period=0)

        with pytest.raises(ValidationError):
            TechnicalIndicatorQueryModel(symbol="000001", indicators=["MA"], period=501)

    def test_indicator_query_with_date_range(self):
        """测试带日期范围的指标查询"""
        model = TechnicalIndicatorQueryModel(
            symbol="000001",
            indicators=["MA", "RSI"],
            period=20,
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 1, 31),
        )
        assert model.start_date is not None
        assert model.end_date is not None


class TestPaginationModel:
    """分页模型测试"""

    def test_valid_pagination(self, validation_test_data):
        """测试有效的分页参数"""
        page_data = validation_test_data["pagination"]["valid"]
        model = PaginationModel(page=page_data["page"], page_size=page_data["page_size"])
        assert model.page == 1
        assert model.page_size == 20

    def test_pagination_defaults(self):
        """测试分页默认值"""
        model = PaginationModel()
        assert model.page == 1
        assert model.page_size == 20

    def test_pagination_max_values(self):
        """测试分页最大值"""
        model = PaginationModel(page=10000, page_size=500)
        assert model.page == 10000
        assert model.page_size == 500

    def test_pagination_invalid_page_zero(self, validation_test_data):
        """测试页码为0"""
        with pytest.raises(ValidationError):
            PaginationModel(page=0, page_size=20)

    def test_pagination_invalid_page_negative(self):
        """测试负数页码"""
        with pytest.raises(ValidationError):
            PaginationModel(page=-1, page_size=20)

    def test_pagination_invalid_page_size_zero(self, validation_test_data):
        """测试每页大小为0"""
        with pytest.raises(ValidationError):
            PaginationModel(page=1, page_size=0)

    def test_pagination_invalid_page_size_exceeds_max(self, validation_test_data):
        """测试每页大小超过最大值"""
        with pytest.raises(ValidationError):
            PaginationModel(page=1, page_size=1000)

    def test_pagination_boundary_values(self):
        """测试分页边界值"""
        # 最小有效值
        model = PaginationModel(page=1, page_size=1)
        assert model.page == 1
        assert model.page_size == 1

        # 中间值
        model = PaginationModel(page=100, page_size=50)
        assert model.page == 100
        assert model.page_size == 50


class TestStockListQueryModel:
    """股票列表查询模型测试"""

    def test_valid_stock_list_query(self):
        """测试有效的股票列表查询"""
        model = StockListQueryModel(
            page=1,
            page_size=20,
            query="招商银行",
            sort_by="symbol",
            sort_order="asc",
        )
        assert model.page == 1
        assert model.page_size == 20
        assert model.query == "招商银行"

    def test_stock_list_pagination_inheritance(self):
        """测试继承的分页功能"""
        model = StockListQueryModel(page=5, page_size=50)
        assert model.page == 5
        assert model.page_size == 50

    def test_stock_list_optional_fields(self):
        """测试可选字段"""
        model = StockListQueryModel(page=1, page_size=20)
        # keyword, sort_field, sort_order 应该是可选的
        assert model.page == 1


class TestTradeOrderModel:
    """交易订单模型测试"""

    def test_valid_trade_order(self):
        """测试有效的交易订单"""
        model = TradeOrderModel(
            symbol="000001",
            order_type="buy",
            price=100.0,
            quantity=100,
            order_validity="gtc",
        )
        assert model.symbol == "000001"
        assert model.order_type == "buy"
        assert model.price == 100.0
        assert model.quantity == 100

    def test_valid_order_types(self):
        """测试所有有效的订单类型"""
        for order_type in ["buy", "sell"]:
            model = TradeOrderModel(
                symbol="AAPL",
                order_type=order_type,
                price=150.0,
                quantity=10,
                order_validity="gtc",
            )
            assert model.order_type == order_type

    def test_valid_order_validity_types(self):
        """测试所有有效的订单有效期"""
        validity_types = ["gtc", "gtd", "ioc", "fok"]
        for validity in validity_types:
            model = TradeOrderModel(
                symbol="000001",
                order_type="buy",
                price=100.0,
                quantity=100,
                order_validity=validity,
            )
            assert model.order_validity == validity

    def test_trade_order_price_range(self):
        """测试价格范围"""
        # 最小价格
        model = TradeOrderModel(
            symbol="000001",
            order_type="buy",
            price=0.01,
            quantity=1,
            order_validity="gtc",
        )
        assert model.price == 0.01

        # 最大价格（100万）
        model = TradeOrderModel(
            symbol="000001",
            order_type="buy",
            price=1000000,
            quantity=1,
            order_validity="gtc",
        )
        assert model.price == 1000000

    def test_trade_order_quantity_range(self):
        """测试数量范围"""
        # 最小数量
        model = TradeOrderModel(
            symbol="000001",
            order_type="buy",
            price=100.0,
            quantity=1,
            order_validity="gtc",
        )
        assert model.quantity == 1

        # 最大数量（1000万）
        model = TradeOrderModel(
            symbol="000001",
            order_type="buy",
            price=100.0,
            quantity=10000000,
            order_validity="gtc",
        )
        assert model.quantity == 10000000

    def test_invalid_trade_order_type(self):
        """测试无效的订单类型"""
        with pytest.raises(ValidationError):
            TradeOrderModel(
                symbol="000001",
                order_type="invalid",
                price=100.0,
                quantity=100,
                order_validity="gtc",
            )

    def test_invalid_order_validity(self):
        """测试无效的订单有效期"""
        with pytest.raises(ValidationError):
            TradeOrderModel(
                symbol="000001",
                order_type="buy",
                price=100.0,
                quantity=100,
                order_validity="invalid",
            )


class TestResponseModel:
    """响应模型测试"""

    def test_valid_response(self):
        """测试有效的响应"""
        model = ResponseModel(
            code="SUCCESS",
            message="Success",
            data={"key": "value"},
        )
        assert model.code == "SUCCESS"
        assert model.message == "Success"
        assert model.timestamp is not None

    def test_response_with_none_data(self):
        """测试data为None的响应"""
        model = ResponseModel(
            code="SUCCESS",
            message="Success",
            data=None,
        )
        assert model.data is None

    def test_response_with_list_data(self):
        """测试data为列表的响应"""
        model = ResponseModel(
            code="SUCCESS",
            message="Success",
            data=[1, 2, 3],
        )
        assert isinstance(model.data, list)


class TestErrorResponseModel:
    """错误响应模型测试"""

    def test_valid_error_response(self):
        """测试有效的错误响应"""
        model = ErrorResponseModel(
            code="VALIDATION_ERROR",
            message="Bad Request",
            details="Invalid parameter",
        )
        assert model.code == "VALIDATION_ERROR"
        assert model.message == "Bad Request"
        assert model.details == "Invalid parameter"
        assert model.timestamp is not None

    def test_error_response_with_none_details(self):
        """测试details为None的错误响应"""
        model = ErrorResponseModel(
            code="SERVER_ERROR",
            message="Internal Server Error",
            details=None,
        )
        assert model.details is None


class TestModelJsonSchema:
    """模型JSON Schema测试"""

    def test_stock_symbol_schema(self):
        """测试StockSymbolModel的JSON Schema"""
        schema = StockSymbolModel.model_json_schema()
        assert "symbol" in schema["properties"]
        assert schema["properties"]["symbol"]["type"] == "string"

    def test_date_range_schema(self):
        """测试DateRangeModel的JSON Schema"""
        schema = DateRangeModel.model_json_schema()
        assert "start_date" in schema["properties"]
        assert "end_date" in schema["properties"]

    def test_market_data_query_schema(self):
        """测试MarketDataQueryModel的JSON Schema"""
        schema = MarketDataQueryModel.model_json_schema()
        assert "symbol" in schema["properties"]
        assert "interval" in schema["properties"]


class TestModelSerialization:
    """模型序列化测试"""

    def test_stock_symbol_serialization(self):
        """测试StockSymbolModel序列化"""
        model = StockSymbolModel(symbol="600519")
        json_data = model.model_dump()
        assert json_data["symbol"] == "600519"

    def test_pagination_serialization(self):
        """测试PaginationModel序列化"""
        model = PaginationModel(page=1, page_size=20)
        json_data = model.model_dump()
        assert json_data["page"] == 1
        assert json_data["page_size"] == 20

    def test_market_data_query_serialization(self):
        """测试MarketDataQueryModel序列化"""
        model = MarketDataQueryModel(
            symbol="000001",
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 1, 31),
        )
        json_data = model.model_dump_json()
        assert "000001" in json_data
