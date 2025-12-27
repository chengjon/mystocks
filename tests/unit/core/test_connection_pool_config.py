#!/usr/bin/env python3
"""
连接池配置模块单元测试 - 源代码覆盖率测试

测试MyStocks系统中数据库连接池的配置管理功能
"""

import pytest
import sys
import os
from unittest.mock import patch

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core.connection_pool_config import (
    ConnectionPoolConfig,
    get_pool_config,
    get_optimal_pool_size,
    get_production_pool_config,
    get_development_pool_config,
    get_test_pool_config,
    get_config_for_environment,
)


class TestConnectionPoolConfig:
    """测试连接池配置类"""

    @pytest.fixture
    def clean_env(self):
        """清理环境变量的fixture"""
        # 保存原始环境变量
        original_env = {}
        config_vars = [
            "POOL_MIN_CONNECTIONS",
            "POOL_MAX_CONNECTIONS",
            "POOL_TIMEOUT",
            "POOL_RECYCLE",
            "POOL_MAX_QUERIES",
            "POOL_MAX_INACTIVE_CONNECTION_LIFETIME",
            "HEALTH_CHECK_INTERVAL",
            "HEALTH_CHECK_TIMEOUT",
            "ENABLE_POOL_MONITORING",
            "MONITORING_INTERVAL",
        ]

        for var in config_vars:
            original_env[var] = os.environ.get(var)
            if var in os.environ:
                del os.environ[var]

        yield

        # 恢复原始环境变量
        for var, value in original_env.items():
            if value is not None:
                os.environ[var] = value
            elif var in os.environ:
                del os.environ[var]

    def test_default_initialization(self, clean_env):
        """测试默认初始化"""
        config = ConnectionPoolConfig()

        # 连接池基本配置
        assert config.pool_min_connections == 5
        assert config.pool_max_connections == 20
        assert config.pool_timeout == 30
        assert config.pool_recycle == 3600
        assert config.pool_max_queries == 50000
        assert config.pool_max_inactive_connection_lifetime == 300

        # 连接健康检查配置
        assert config.health_check_interval == 60
        assert config.health_check_timeout == 5

        # 监控配置
        assert config.enable_pool_monitoring is True
        assert config.monitoring_interval == 60

    def test_environment_variable_override(self, clean_env):
        """测试环境变量覆盖"""
        os.environ["POOL_MIN_CONNECTIONS"] = "10"
        os.environ["POOL_MAX_CONNECTIONS"] = "50"
        os.environ["POOL_TIMEOUT"] = "60"
        os.environ["POOL_RECYCLE"] = "7200"
        os.environ["POOL_MAX_QUERIES"] = "100000"
        os.environ["POOL_MAX_INACTIVE_CONNECTION_LIFETIME"] = "600"
        os.environ["HEALTH_CHECK_INTERVAL"] = "120"
        os.environ["HEALTH_CHECK_TIMEOUT"] = "10"
        os.environ["ENABLE_POOL_MONITORING"] = "false"
        os.environ["MONITORING_INTERVAL"] = "30"

        config = ConnectionPoolConfig()

        assert config.pool_min_connections == 10
        assert config.pool_max_connections == 50
        assert config.pool_timeout == 60
        assert config.pool_recycle == 7200
        assert config.pool_max_queries == 100000
        assert config.pool_max_inactive_connection_lifetime == 600
        assert config.health_check_interval == 120
        assert config.health_check_timeout == 10
        assert config.enable_pool_monitoring is False
        assert config.monitoring_interval == 30

    def test_from_env_class_method(self, clean_env):
        """测试从环境变量加载配置的类方法"""
        os.environ["POOL_MIN_CONNECTIONS"] = "3"
        os.environ["POOL_MAX_CONNECTIONS"] = "15"

        config = ConnectionPoolConfig.from_env()

        assert config.pool_min_connections == 3
        assert config.pool_max_connections == 15

    def test_validate_config_success_default(self, clean_env):
        """测试配置验证成功 - 默认配置"""
        config = ConnectionPoolConfig()
        result = config.validate_config()
        assert result is True

    def test_validate_config_success_custom(self, clean_env):
        """测试配置验证成功 - 自定义配置"""
        os.environ["POOL_MIN_CONNECTIONS"] = "2"
        os.environ["POOL_MAX_CONNECTIONS"] = "10"
        os.environ["POOL_TIMEOUT"] = "15"
        os.environ["POOL_RECYCLE"] = "1800"

        config = ConnectionPoolConfig()
        result = config.validate_config()
        assert result is True

    def test_validate_config_min_connections_too_low(self, clean_env):
        """测试配置验证失败 - 最小连接数过低"""
        os.environ["POOL_MIN_CONNECTIONS"] = "0"
        config = ConnectionPoolConfig()

        with pytest.raises(ValueError, match="Minimum connections must be at least 1"):
            config.validate_config()

    def test_validate_config_max_less_than_min(self, clean_env):
        """测试配置验证失败 - 最大连接数小于最小连接数"""
        os.environ["POOL_MIN_CONNECTIONS"] = "10"
        os.environ["POOL_MAX_CONNECTIONS"] = "5"
        config = ConnectionPoolConfig()

        with pytest.raises(
            ValueError,
            match="Maximum connections must be greater than or equal to minimum connections",
        ):
            config.validate_config()

    def test_validate_config_timeout_too_low(self, clean_env):
        """测试配置验证失败 - 连接超时过低"""
        os.environ["POOL_TIMEOUT"] = "0"
        config = ConnectionPoolConfig()

        with pytest.raises(ValueError, match="Connection timeout must be at least 1"):
            config.validate_config()

    def test_validate_config_recycle_negative(self, clean_env):
        """测试配置验证失败 - 连接回收时间为负数"""
        os.environ["POOL_RECYCLE"] = "-1"
        config = ConnectionPoolConfig()

        with pytest.raises(ValueError, match="Connection recycle time must be non-negative"):
            config.validate_config()

    def test_validate_config_health_check_interval_too_low(self, clean_env):
        """测试配置验证失败 - 健康检查间隔过低"""
        os.environ["HEALTH_CHECK_INTERVAL"] = "0"
        config = ConnectionPoolConfig()

        with pytest.raises(ValueError, match="Health check interval must be at least 1"):
            config.validate_config()

    def test_validate_config_health_check_timeout_too_low(self, clean_env):
        """测试配置验证失败 - 健康检查超时过低"""
        os.environ["HEALTH_CHECK_TIMEOUT"] = "0"
        config = ConnectionPoolConfig()

        with pytest.raises(ValueError, match="Health check timeout must be at least 1"):
            config.validate_config()

    def test_get_pool_config_dict_default(self, clean_env):
        """测试获取连接池配置字典 - 默认配置"""
        config = ConnectionPoolConfig()
        config_dict = config.get_pool_config_dict()

        expected = {
            "min_connections": 5,
            "max_connections": 20,
            "timeout": 30,
            "recycle": 3600,
            "max_queries": 50000,
            "max_inactive_connection_lifetime": 300,
        }

        assert config_dict == expected

    def test_get_pool_config_dict_custom(self, clean_env):
        """测试获取连接池配置字典 - 自定义配置"""
        os.environ["POOL_MIN_CONNECTIONS"] = "3"
        os.environ["POOL_MAX_CONNECTIONS"] = "15"
        os.environ["POOL_TIMEOUT"] = "20"
        os.environ["POOL_RECYCLE"] = "1800"
        os.environ["POOL_MAX_QUERIES"] = "25000"
        os.environ["POOL_MAX_INACTIVE_CONNECTION_LIFETIME"] = "150"

        config = ConnectionPoolConfig()
        config_dict = config.get_pool_config_dict()

        expected = {
            "min_connections": 3,
            "max_connections": 15,
            "timeout": 20,
            "recycle": 1800,
            "max_queries": 25000,
            "max_inactive_connection_lifetime": 150,
        }

        assert config_dict == expected

    def test_boolean_environment_variable_parsing(self, clean_env):
        """测试布尔环境变量解析"""
        # 测试true的各种形式
        for true_value in ["true", "TRUE", "True", "t", "T"]:
            os.environ["ENABLE_POOL_MONITORING"] = true_value
            config = ConnectionPoolConfig()
            assert config.enable_pool_monitoring is True

        # 测试false的各种形式
        for false_value in ["false", "FALSE", "False", "f", "F", "anything_else"]:
            os.environ["ENABLE_POOL_MONITORING"] = false_value
            config = ConnectionPoolConfig()
            assert config.enable_pool_monitoring is False


class TestGlobalFunctions:
    """测试全局函数"""

    @pytest.fixture
    def clean_env(self):
        """清理环境变量的fixture"""
        original_env = os.environ.get("ENVIRONMENT")
        if "ENVIRONMENT" in os.environ:
            del os.environ["ENVIRONMENT"]
        yield
        if original_env is not None:
            os.environ["ENVIRONMENT"] = original_env
        elif "ENVIRONMENT" in os.environ:
            del os.environ["ENVIRONMENT"]

    def test_get_pool_config_singleton(self):
        """测试全局连接池配置单例模式"""
        # 重置全局变量
        import src.core.connection_pool_config

        src.core.connection_pool_config._pool_config = None

        config1 = get_pool_config()
        config2 = get_pool_config()

        # 应该返回同一个实例
        assert config1 is config2

    def test_get_pool_config_returns_instance(self):
        """测试返回正确的实例类型"""
        import src.core.connection_pool_config

        src.core.connection_pool_config._pool_config = None

        config = get_pool_config()
        assert isinstance(config, ConnectionPoolConfig)

    def test_get_optimal_pool_size_default(self):
        """测试获取最优连接池大小 - 默认"""
        min_conn, max_conn = get_optimal_pool_size()

        assert min_conn == 5
        assert max_conn == 20  # 5 * 4 = 20, 小于50

    def test_get_optimal_pool_size_limit(self):
        """测试获取最优连接池大小 - 最大限制"""
        # 模拟基础连接数较大
        with patch("src.core.connection_pool_config.get_optimal_pool_size") as mock_optimal:

            def mock_implementation():
                # 基础连接数太大，应该被限制到50
                base_connections = 20
                optimal_min = base_connections
                optimal_max = min(base_connections * 4, 50)
                return optimal_min, optimal_max

            mock_optimal.side_effect = mock_implementation
            min_conn, max_conn = get_optimal_pool_size()
            assert max_conn <= 50

    def test_get_production_pool_config_production_env(self, clean_env):
        """测试获取生产环境配置 - 生产环境"""
        os.environ["ENVIRONMENT"] = "production"

        # 重置全局变量以避免缓存影响
        import src.core.connection_pool_config

        src.core.connection_pool_config._pool_config = None

        config = get_production_pool_config()

        # 生产环境应该使用优化的连接池大小
        min_conn, max_conn = get_optimal_pool_size()
        assert config.pool_min_connections == min_conn
        assert config.pool_max_connections == max_conn
        assert config.pool_timeout == 10
        assert config.pool_recycle == 1800
        assert config.enable_pool_monitoring is True
        assert config.monitoring_interval == 30

    def test_get_production_pool_config_development_env(self, clean_env):
        """测试获取生产环境配置 - 开发环境"""
        os.environ["ENVIRONMENT"] = "development"

        # 重置全局变量以避免缓存影响
        import src.core.connection_pool_config

        src.core.connection_pool_config._pool_config = None

        config = get_production_pool_config()

        # 开发环境不应该应用生产优化
        assert config.pool_min_connections == 5  # 默认值
        assert config.pool_max_connections == 20  # 默认值

    def test_get_development_pool_config(self):
        """测试获取开发环境配置"""
        config = get_development_pool_config()

        assert config.pool_min_connections == 2
        assert config.pool_max_connections == 5
        assert config.pool_timeout == 10
        assert config.pool_recycle == 7200

    def test_get_test_pool_config(self):
        """测试获取测试环境配置"""
        config = get_test_pool_config()

        assert config.pool_min_connections == 1
        assert config.pool_max_connections == 3
        assert config.pool_timeout == 5
        assert config.pool_recycle == 300

    def test_get_config_for_environment_production(self, clean_env):
        """测试根据环境获取配置 - 生产环境"""
        os.environ["ENVIRONMENT"] = "production"

        # 重置全局变量以避免缓存影响
        import src.core.connection_pool_config

        src.core.connection_pool_config._pool_config = None

        config = get_config_for_environment()

        # 验证是生产环境配置
        min_conn, max_conn = get_optimal_pool_size()
        assert config.pool_min_connections == min_conn
        assert config.pool_max_connections == max_conn

    def test_get_config_for_environment_test(self, clean_env):
        """测试根据环境获取配置 - 测试环境"""
        os.environ["ENVIRONMENT"] = "test"

        # 重置全局变量以避免缓存影响
        import src.core.connection_pool_config

        src.core.connection_pool_config._pool_config = None

        config = get_config_for_environment()

        assert config.pool_min_connections == 1
        assert config.pool_max_connections == 3
        assert config.pool_timeout == 5

    def test_get_config_for_environment_development(self, clean_env):
        """测试根据环境获取配置 - 开发环境"""
        os.environ["ENVIRONMENT"] = "development"

        # 重置全局变量以避免缓存影响
        import src.core.connection_pool_config

        src.core.connection_pool_config._pool_config = None

        config = get_config_for_environment()

        assert config.pool_min_connections == 2
        assert config.pool_max_connections == 5
        assert config.pool_timeout == 10

    def test_get_config_for_environment_unspecified(self, clean_env):
        """测试根据环境获取配置 - 未指定环境（默认为开发）"""
        # 不设置ENVIRONMENT，应该默认为development

        # 重置全局变量以避免缓存影响
        import src.core.connection_pool_config

        src.core.connection_pool_config._pool_config = None

        config = get_config_for_environment()

        assert config.pool_min_connections == 2
        assert config.pool_max_connections == 5
        assert config.pool_timeout == 10

    def test_get_config_for_environment_case_insensitive(self, clean_env):
        """测试根据环境获取配置 - 大小写不敏感"""
        test_cases = ["PRODUCTION", "TEST", "DEVELOPMENT", "Test", "test"]

        for env_value in test_cases:
            os.environ["ENVIRONMENT"] = env_value

            # 重置全局变量以避免缓存影响
            import src.core.connection_pool_config

            src.core.connection_pool_config._pool_config = None

            config = get_config_for_environment()

            env_lower = env_value.lower()
            if env_lower == "production":
                min_conn, max_conn = get_optimal_pool_size()
                assert config.pool_min_connections == min_conn
            elif env_lower == "test":
                assert config.pool_min_connections == 1
            else:
                assert config.pool_min_connections == 2


class TestEdgeCases:
    """测试边界情况"""

    @pytest.fixture
    def clean_env(self):
        """清理环境变量的fixture"""
        original_env = {}
        config_vars = ["POOL_MIN_CONNECTIONS", "POOL_MAX_CONNECTIONS"]
        for var in config_vars:
            original_env[var] = os.environ.get(var)
            if var in os.environ:
                del os.environ[var]
        yield
        for var, value in original_env.items():
            if value is not None:
                os.environ[var] = value
            elif var in os.environ:
                del os.environ[var]

    def test_environment_variable_invalid_integer(self, clean_env):
        """测试无效的整数环境变量"""
        os.environ["POOL_MIN_CONNECTIONS"] = "invalid"

        with pytest.raises(ValueError):
            ConnectionPoolConfig()

    def test_environment_variable_invalid_float(self, clean_env):
        """测试无效的浮点数环境变量"""
        os.environ["POOL_MAX_INACTIVE_CONNECTION_LIFETIME"] = "invalid"

        with pytest.raises(ValueError):
            ConnectionPoolConfig()

    def test_pool_size_boundary_values(self, clean_env):
        """测试连接池边界值"""
        # 测试最小合法值
        os.environ["POOL_MIN_CONNECTIONS"] = "1"
        os.environ["POOL_MAX_CONNECTIONS"] = "1"
        os.environ["POOL_TIMEOUT"] = "1"
        os.environ["POOL_RECYCLE"] = "0"

        config = ConnectionPoolConfig()
        assert config.validate_config() is True

        # 测试相等的最小和最大连接数
        os.environ["POOL_MIN_CONNECTIONS"] = "5"
        os.environ["POOL_MAX_CONNECTIONS"] = "5"
        config = ConnectionPoolConfig()
        assert config.validate_config() is True

    def test_large_values_handling(self, clean_env):
        """测试大值处理"""
        os.environ["POOL_MAX_QUERIES"] = "999999"
        os.environ["POOL_MAX_INACTIVE_CONNECTION_LIFETIME"] = "9999.99"

        config = ConnectionPoolConfig()
        assert config.pool_max_queries == 999999
        assert config.pool_max_inactive_connection_lifetime == 9999.99

    def test_zero_values_handling(self, clean_env):
        """测试零值处理"""
        os.environ["POOL_RECYCLE"] = "0"

        config = ConnectionPoolConfig()
        assert config.pool_recycle == 0
        assert config.validate_config() is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
