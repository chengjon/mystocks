"""
TDX Connection Manager Test Suite
TDX连接管理器测试套件

创建日期: 2025-12-20
版本: 1.0.0
测试模块: src.adapters.tdx_connection_manager (158行)
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import sys
import os
import time
from typing import Dict, Optional, Any, Callable
from functools import wraps

# 添加src路径到导入路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))


class MockTdxConnection:
    """模拟TDX连接"""

    def __init__(self, should_fail_connect=False, should_fail_operation=False):
        self.should_fail_connect = should_fail_connect
        self.should_fail_operation = should_fail_operation
        self.is_connected = False
        self.call_count = 0
        self.last_operation = None

    def connect(self, host, port):
        """模拟连接"""
        self.call_count += 1
        self.last_operation = "connect"

        if self.should_fail_connect:
            raise ConnectionError("连接失败")

        self.is_connected = True
        return True

    def disconnect(self):
        """模拟断开连接"""
        self.call_count += 1
        self.last_operation = "disconnect"
        self.is_connected = False

    def get_security_count(self, market_code):
        """模拟获取股票数量"""
        self.call_count += 1
        self.last_operation = f"get_security_count_{market_code}"

        if self.should_fail_operation:
            raise RuntimeError("获取数量失败")

        return 1000

    def get_instrument_info(self, code):
        """模拟获取股票信息"""
        self.call_count += 1
        self.last_operation = f"get_instrument_info_{code}"

        if self.should_fail_operation:
            raise RuntimeError("获取信息失败")

        return {
            'code': code,
            'name': f'{code}股票',
            'market': 'SH' if code.startswith('6') else 'SZ'
        }


class TestTdxConnectionManager:
    """TDX连接管理器测试"""

    def test_connection_manager_initialization(self):
        """测试连接管理器初始化"""
        from adapters.tdx_connection_manager import TdxConnectionManager

        manager = TdxConnectionManager()

        # 验证初始状态
        assert manager.connection is None
        assert manager._connection_attempts == 0

        # 验证市场代码映射
        expected_codes = {'SH': 0, 'SZ': 1}
        assert manager.market_codes == expected_codes

        # 验证重试配置
        expected_retry = {
            'max_retries': 3,
            'retry_delay': 1.0,
            'backoff_factor': 2.0
        }
        assert manager.retry_config == expected_retry

        # 验证日志器
        assert hasattr(manager, 'logger')

    def test_market_codes_completeness(self):
        """测试市场代码完整性"""
        from adapters.tdx_connection_manager import TdxConnectionManager

        manager = TdxConnectionManager()

        # 验证包含主要交易所
        assert 'SH' in manager.market_codes  # 上交所
        assert 'SZ' in manager.market_codes  # 深交所

        # 验证代码值
        assert manager.market_codes['SH'] == 0
        assert manager.market_codes['SZ'] == 1

    def test_retry_config_values(self):
        """测试重试配置值"""
        from adapters.tdx_connection_manager import TdxConnectionManager

        manager = TdxConnectionManager()

        # 验证重试次数
        assert manager.retry_config['max_retries'] == 3

        # 验证重试延迟
        assert manager.retry_config['retry_delay'] == 1.0

        # 验证退避因子
        assert manager.retry_config['backoff_factor'] == 2.0

    def test_create_connection_success(self):
        """测试创建连接成功"""
        from adapters.tdx_connection_manager import TdxConnectionManager

        manager = TdxConnectionManager()
        mock_connection = MockTdxConnection(should_fail_connect=False, should_fail_operation=False)

        with patch.object(manager, '_connect_to_tdx_server', return_value=mock_connection):
            result = manager.create_connection()

        assert result == mock_connection
        assert manager.connection == mock_connection

  def test_create_connection_with_retry_failure(self):
        """测试创建连接失败重试机制"""
        from adapters.tdx_connection_manager import TdxConnectionManager

        manager = TdxConnectionManager()
        manager.retry_config['max_retries'] = 2  # 降低重试次数以加快测试

        call_count = 0
        def failing_connection():
            nonlocal call_count
            call_count += 1
            raise ConnectionError("连接失败")

        with patch.object(manager, '_connect_to_tdx_server', side_effect=failing_connection):
            with pytest.raises(ConnectionError, match="连接失败"):
                manager.create_connection()

        assert call_count == 2  # max_retries = 2

    def test_create_connection_success_after_retry(self):
        """测试重试后创建连接成功"""
        from adapters.tdx_connection_manager import TdxConnectionManager

        manager = TdxConnectionManager()

        call_count = 0
        def side_effect():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # 第一次连接失败
                raise ConnectionError("连接失败")
            else:
                # 第二次连接成功
                return MockTdxConnection(should_fail_connect=False)

        with patch.object(manager, '_connect_to_tdx_server', side_effect=side_effect):
            result = manager.create_connection()

        assert result is not None
        assert manager.connection is not None
        assert call_count == 2

    def test_close_connection_success(self):
        """测试成功关闭连接"""
        from adapters.tdx_connection_manager import TdxConnectionManager

        manager = TdxConnectionManager()
        mock_connection = MockTdxConnection()
        manager.connection = mock_connection

        manager.close_connection()

        assert manager.connection is None

    def test_close_connection_no_connection(self):
        """测试关闭不存在的连接"""
        from adapters.tdx_connection_manager import TdxConnectionManager

        manager = TdxConnectionManager()
        manager.connection = None

        # 应该不抛出异常
        manager.close_connection()

        assert manager.connection is None

    def test_check_connection_health_true(self):
        """测试连接健康检查 - 健康"""
        from adapters.tdx_connection_manager import TdxConnectionManager

        manager = TdxConnectionManager()
        healthy_connection = {
            'status': 'connected',
            'created_at': time.time()  # 当前时间，不会超时
        }
        manager.connection = healthy_connection

        result = manager.check_connection_health()

        assert result is True

    def test_check_connection_health_false_no_connection(self):
        """测试连接健康检查 - 无连接"""
        from adapters.tdx_connection_manager import TdxConnectionManager

        manager = TdxConnectionManager()
        manager.connection = None

        result = manager.check_connection_health()

        assert result is False

    def test_check_connection_health_false_stale(self):
        """测试连接健康检查 - 连接过期"""
        from adapters.tdx_connection_manager import TdxConnectionManager

        manager = TdxConnectionManager()
        stale_connection = {
            'status': 'connected',
            'created_at': time.time() - 40  # 40秒前，超过30秒阈值
        }
        manager.connection = stale_connection

        result = manager.check_connection_health()

        assert result is False

    def test_check_connection_health_false_wrong_status(self):
        """测试连接健康检查 - 错误状态"""
        from adapters.tdx_connection_manager import TdxConnectionManager

        manager = TdxConnectionManager()
        wrong_status_connection = {
            'status': 'disconnected',
            'created_at': time.time()
        }
        manager.connection = wrong_status_connection

        result = manager.check_connection_health()

        assert result is False

    def test_get_market_code_sh(self):
        """测试获取上交所代码"""
        from adapters.tdx_connection_manager import TdxConnectionManager

        manager = TdxConnectionManager()

        result = manager.get_market_code('SH')

        assert result == 0

    def test_get_market_code_sz(self):
        """测试获取深交所代码"""
        from adapters.tdx_connection_manager import TdxConnectionManager

        manager = TdxConnectionManager()

        result = manager.get_market_code('SZ')

        assert result == 1

    def test_get_market_code_invalid(self):
        """测试获取无效市场代码"""
        from adapters.tdx_connection_manager import TdxConnectionManager

        manager = TdxConnectionManager()

        with pytest.raises(ValueError, match="Invalid symbol format"):
            manager.get_market_code('INVALID')

    def test_get_market_code_empty(self):
        """测试获取空股票代码"""
        from adapters.tdx_connection_manager import TdxConnectionManager

        manager = TdxConnectionManager()

        with pytest.raises(ValueError, match="Invalid symbol format"):
            manager.get_market_code('')

    def test_get_market_code_short(self):
        """测试获取过短股票代码"""
        from adapters.tdx_connection_manager import TdxConnectionManager

        manager = TdxConnectionManager()

        with pytest.raises(ValueError, match="Invalid symbol format"):
            manager.get_market_code('123')

    def test_get_connection_status_with_connection(self):
        """测试获取连接状态 - 有连接"""
        from adapters.tdx_connection_manager import TdxConnectionManager

        manager = TdxConnectionManager()
        test_connection = {
            'id': 'conn_123',
            'status': 'connected',
            'created_at': time.time()
        }
        manager.connection = test_connection

        status = manager.get_connection_status()

        assert status['connected'] is True
        assert status['connection_id'] == 'conn_123'
        assert status['status'] == 'connected'
        assert status['connection_attempts'] == 0
        assert 'last_check' in status

    def test_get_connection_status_without_connection(self):
        """测试获取连接状态 - 无连接"""
        from adapters.tdx_connection_manager import TdxConnectionManager

        manager = TdxConnectionManager()
        manager.connection = None

        status = manager.get_connection_status()

        assert status['connected'] is False
        assert status['connection_id'] is None
        assert status['status'] is None
        assert status['connection_attempts'] == 0
        assert 'last_check' in status

    def test_retry_decorator_success(self):
        """测试重试装饰器 - 函数成功"""
        from adapters.tdx_connection_manager import TdxConnectionManager

        manager = TdxConnectionManager()

        @manager._retry_api_call
        def test_function():
            return "success"

        result = test_function()

        assert result == "success"

    def test_retry_decorator_failure(self):
        """测试重试装饰器 - 函数失败"""
        from adapters.tdx_connection_manager import TdxConnectionManager

        manager = TdxConnectionManager()
        manager.retry_config['max_retries'] = 2  # 降低重试次数

        call_count = 0
        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RuntimeError("测试失败")
            return "success"

        with patch('time.sleep'):  # Mock time.sleep以加快测试
            result = manager._retry_api_call(failing_function)()

        assert result == "success"
        assert call_count == 3

    def test_retry_decorator_max_retries(self):
        """测试重试装饰器 - 达到最大重试次数"""
        from adapters.tdx_connection_manager import TdxConnectionManager

        manager = TdxConnectionManager()
        manager.retry_config['max_retries'] = 1  # 降低重试次数

        def always_failing_function():
            raise RuntimeError("总是失败")

        with patch('time.sleep'):  # Mock time.sleep以加快测试
            with pytest.raises(RuntimeError, match="总是失败"):
                manager._retry_api_call(always_failing_function)()

    def test_connection_manager_str_representation(self):
        """测试管理器字符串表示"""
        from adapters.tdx_connection_manager import TdxConnectionManager

        manager = TdxConnectionManager()

        str_repr = str(manager)

        assert "TdxConnectionManager" in str_repr
        assert "connection_attempts" in str_repr


class TestTdxConnectionManagerIntegration:
    """TDX连接管理器集成测试"""

    def test_complete_connection_lifecycle(self):
        """测试完整的连接生命周期"""
        from adapters.tdx_connection_manager import TdxConnectionManager

        manager = TdxConnectionManager()
        mock_connection = {
            'id': 'test_conn',
            'status': 'connected',
            'created_at': time.time()
        }

        with patch.object(manager, '_connect_to_tdx_server', return_value=mock_connection):
            # 1. 创建连接
            connection = manager.create_connection()
            assert connection == mock_connection
            assert manager.check_connection_health() is True

            # 2. 获取连接状态
            status = manager.get_connection_status()
            assert status['connected'] is True
            assert status['connection_id'] == 'test_conn'

            # 3. 关闭连接
            manager.close_connection()
            assert manager.check_connection_health() is False
            assert manager.connection is None

    def test_connection_health_and_recovery(self):
        """测试连接健康检查和恢复"""
        from adapters.tdx_connection_manager import TdxConnectionManager

        manager = TdxConnectionManager()

        # 创建健康连接
        healthy_connection = {
            'status': 'connected',
            'created_at': time.time()
        }
        manager.connection = healthy_connection

        # 初始健康检查
        assert manager.check_connection_health() is True

        # 模拟连接过期
        stale_connection = {
            'status': 'connected',
            'created_at': time.time() - 40  # 过期连接
        }
        manager.connection = stale_connection
        assert manager.check_connection_health() is False

        # 重新创建连接
        new_connection = {
            'status': 'connected',
            'created_at': time.time()
        }
        with patch.object(manager, '_connect_to_tdx_server', return_value=new_connection):
            manager.create_connection()
            assert manager.check_connection_health() is True

    def test_retry_decorator_timing(self):
        """测试重试装饰器时间控制"""
        from adapters.tdx_connection_manager import TdxConnectionManager

        manager = TdxConnectionManager()
        manager.retry_config['max_retries'] = 2

        call_count = 0
        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RuntimeError("失败")
            return "success"

        with patch('time.sleep') as mock_sleep:
            result = manager._retry_api_call(failing_function)()
            assert result == "success"
            assert call_count == 3

        # 验证time.sleep调用次数
        assert mock_sleep.call_count == 2  # 前两次失败会sleep

        # 验证延迟时间递增
        if len(mock_sleep.call_args_list) >= 2:
            first_delay = mock_sleep.call_args_list[0][0][0]
            second_delay = mock_sleep.call_args_list[1][0][0]
            assert first_delay == 1.0  # retry_delay
            assert second_delay == 2.0  # retry_delay * backoff_factor

    def test_backoff_factor_configuration(self):
        """测试退避因子配置"""
        from adapters.tdx_connection_manager import TdxConnectionManager

        manager = TdxConnectionManager()
        assert manager.retry_config['backoff_factor'] == 2.0

        # 验证退避递增公式
        expected_delays = []
        for i in range(manager.retry_config['max_retries']):
            delay = manager.retry_config['retry_delay'] * (manager.retry_config['backoff_factor'] ** i)
            expected_delays.append(delay)

        assert expected_delays == [1.0, 2.0, 4.0]


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--no-cov"])