"""
TDD测试框架 - 财务适配器重构
遵循红-绿-重构循环，确保拆分后的功能完整性
"""

import pytest
import pandas as pd
import sys
import os

# 添加项目根路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


class TestPriceDataMethods:
    """价格数据适配器测试类 - 测试原有方法的功能"""

    def test_get_stock_daily_valid_params(self):
        """测试：获取股票日线数据 - 有效参数"""
        # TODO: 这个测试在重构前应该失败，因为没有拆分的模块
        # RED阶段：编写失败的测试
        from src.adapters.price_data_adapter import PriceDataAdapter

        adapter = PriceDataAdapter()
        symbol = "000001"
        start_date = "2024-01-01"
        end_date = "2024-01-31"

        # 期望返回DataFrame，包含特定列
        result = adapter.get_stock_daily(symbol, start_date, end_date)

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        expected_columns = ["open", "high", "low", "close", "volume"]
        for col in expected_columns:
            assert col in result.columns

    def test_get_stock_daily_invalid_symbol(self):
        """测试：获取股票日线数据 - 无效股票代码"""
        from src.adapters.price_data_adapter import PriceDataAdapter

        adapter = PriceDataAdapter()
        invalid_symbol = "INVALID"
        start_date = "2024-01-01"
        end_date = "2024-01-31"

        # 期望抛出 ValueError
        with pytest.raises(ValueError, match="Invalid symbol format"):
            adapter.get_stock_daily(invalid_symbol, start_date, end_date)

    def test_get_stock_daily_invalid_date_range(self):
        """测试：获取股票日线数据 - 无效日期范围"""
        from src.adapters.price_data_adapter import PriceDataAdapter

        adapter = PriceDataAdapter()
        symbol = "000001"
        start_date = "2024-01-31"
        end_date = "2024-01-01"  # 结束日期早于开始日期

        with pytest.raises(ValueError, match="End date must be after start date"):
            adapter.get_stock_daily(symbol, start_date, end_date)


class TestVolumeDataMethods:
    """成交量数据处理测试类"""

    def test_calculate_volume_ma(self):
        """测试：计算成交量移动平均"""
        # TODO: 重构前应该失败
        from src.adapters.volume_data_processor import VolumeDataProcessor

        processor = VolumeDataProcessor()
        test_data = pd.DataFrame({"volume": [1000, 2000, 3000, 4000, 5000]})

        result = processor.calculate_volume_ma(test_data, window=3)

        assert isinstance(result, pd.Series)
        assert len(result) == len(test_data)
        # 验证前两个应该是NaN
        assert pd.isna(result.iloc[0])
        assert pd.isna(result.iloc[1])
        # 验证第三个值应该是(1000+2000+3000)/3 = 2000
        assert result.iloc[2] == 2000

    def test_detect_volume_anomaly(self):
        """测试：检测成交量异常"""
        from src.adapters.volume_data_processor import VolumeDataProcessor

        processor = VolumeDataProcessor()
        test_data = pd.DataFrame(
            {
                "volume": [1000, 1200, 15000, 1800, 2000]  # 15000是异常值
            }
        )

        anomalies = processor.detect_volume_anomaly(test_data, threshold=5.0)

        assert isinstance(anomalies, list)
        assert len(anomalies) == 1
        assert anomalies[0] == 2  # 索引位置


class TestTDXIntegrationMethods:
    """通达信集成测试类"""

    def test_tdx_connection_success(self):
        """测试：通达信连接成功"""
        # 使用实际的连接逻辑，不依赖外部TDXClient
        from src.adapters.tdx_integration_client import TDXIntegrationClient

        # 使用默认配置（localhost:7709）应该成功
        client = TDXIntegrationClient()
        result = client.connect()

        assert result is True
        assert client.is_connected() is True

    def test_tdx_connection_failure(self):
        """测试：通达信连接失败"""
        from src.adapters.tdx_integration_client import TDXIntegrationClient

        # 使用无效的连接配置
        client = TDXIntegrationClient(host="invalid_host", port=9999)

        with pytest.raises(ConnectionError, match="Cannot connect to"):
            client.connect()


class TestDataValidationMethods:
    """数据校验测试类"""

    def test_validate_stock_symbol(self):
        """测试：股票代码校验"""
        # TODO: 重构前应该失败
        from src.adapters.data_validator import DataValidator

        validator = DataValidator()

        # 有效股票代码
        assert validator.validate_stock_symbol("000001") is True
        assert validator.validate_stock_symbol("600000") is True
        assert validator.validate_stock_symbol("300001") is True

        # 无效股票代码
        assert validator.validate_stock_symbol("INVALID") is False
        assert validator.validate_stock_symbol("") is False
        assert validator.validate_stock_symbol("123") is False

    def test_validate_date_format(self):
        """测试：日期格式校验"""
        from src.adapters.data_validator import DataValidator

        validator = DataValidator()

        # 有效日期格式
        assert validator.validate_date_format("2024-01-01") is True
        assert validator.validate_date_format("2024-12-31") is True

        # 无效日期格式
        assert validator.validate_date_format("2024-13-01") is False
        assert validator.validate_date_format("invalid-date") is False
        assert validator.validate_date_format("") is False

    def test_validate_price_data(self):
        """测试：价格数据校验"""
        from src.adapters.data_validator import DataValidator

        validator = DataValidator()

        # 有效价格数据
        valid_data = pd.DataFrame(
            {
                "open": [10.0, 10.5, 11.0],
                "high": [10.8, 11.2, 11.5],
                "low": [9.8, 10.2, 10.8],
                "close": [10.5, 11.0, 11.2],
                "volume": [1000, 1500, 2000],
            }
        )
        assert validator.validate_price_data(valid_data) is True

        # 无效价格数据（高价低于低价）
        invalid_data = pd.DataFrame(
            {
                "open": [10.0, 11.0, 12.0],
                "high": [9.5, 10.5, 11.5],  # high < open
                "low": [9.8, 10.2, 10.8],
                "close": [10.5, 11.0, 11.2],
                "volume": [1000, 1500, 2000],
            }
        )
        assert validator.validate_price_data(invalid_data) is False


class TestPerformanceBenchmarks:
    """性能基准测试类"""

    def test_get_stock_daily_performance(self):
        """测试：股票日线数据获取性能基准"""
        # TODO: 重构前应该失败
        from src.adapters.price_data_adapter import PriceDataAdapter
        import time

        adapter = PriceDataAdapter()
        symbol = "000001"
        start_date = "2024-01-01"
        end_date = "2024-01-31"

        # 性能测试：100次调用应在5秒内完成
        start_time = time.time()
        for _ in range(100):
            adapter.get_stock_daily(symbol, start_date, end_date)
        end_time = time.time()

        total_time = end_time - start_time
        assert total_time < 5.0, (
            f"Performance benchmark failed: {total_time:.2f}s > 5.0s"
        )


if __name__ == "__main__":
    # 运行测试以验证当前状态（应该全部失败）
    pytest.main([__file__, "-v", "--tb=short"])
