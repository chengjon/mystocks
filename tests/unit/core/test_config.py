#!/usr/bin/env python3
"""
数据库配置模块单元测试 - 源代码覆盖率测试

测试DatabaseConfig类的所有功能，包括环境变量管理和配置验证
"""

import os
import sys

import pytest

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core.config import DatabaseConfig, get_database_config


class TestDatabaseConfig:
    """测试数据库配置类"""

    @pytest.fixture
    def clean_env(self):
        """清理环境变量的fixture"""
        # 保存原始环境变量
        original_env = {}
        config_vars = [
            "DB_POSTGRESQL_HOST",
            "DB_POSTGRESQL_PORT",
            "DB_POSTGRESQL_USERNAME",
            "DB_POSTGRESQL_PASSWORD",
            "DB_POSTGRESQL_DATABASE",
            "DB_TDENGINE_HOST",
            "DB_TDENGINE_PORT",
            "DB_TDENGINE_USERNAME",
            "DB_TDENGINE_PASSWORD",
            "DB_TDENGINE_DATABASE",
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
        config = DatabaseConfig()

        # PostgreSQL默认值
        assert config.postgresql_host == "localhost"
        assert config.postgresql_port == 5432
        assert config.postgresql_username == "postgres"
        assert config.postgresql_password == "postgres"
        assert config.postgresql_database == "mystocks"

        # TDengine默认值
        assert config.tdengine_host == "localhost"
        assert config.tdengine_port == 6030
        assert config.tdengine_username == "root"
        assert config.tdengine_password == "taosdata"
        assert config.tdengine_database == "mystocks"

    def test_environment_variable_override(self, clean_env):
        """测试环境变量覆盖"""
        # 设置环境变量
        os.environ["DB_POSTGRESQL_HOST"] = "custom-host"
        os.environ["DB_POSTGRESQL_PORT"] = "55432"
        os.environ["DB_POSTGRESQL_USERNAME"] = "custom-user"
        os.environ["DB_POSTGRESQL_PASSWORD"] = "custom-pass"
        os.environ["DB_POSTGRESQL_DATABASE"] = "custom-db"

        config = DatabaseConfig()

        assert config.postgresql_host == "custom-host"
        assert config.postgresql_port == 55432
        assert config.postgresql_username == "custom-user"
        assert config.postgresql_password == "custom-pass"
        assert config.postgresql_database == "custom-db"

    def test_tdengine_environment_variable_override(self, clean_env):
        """测试TDengine环境变量覆盖"""
        os.environ["DB_TDENGINE_HOST"] = "tdengine-host"
        os.environ["DB_TDENGINE_PORT"] = "7030"
        os.environ["DB_TDENGINE_USERNAME"] = "tduser"
        os.environ["DB_TDENGINE_PASSWORD"] = "tdpass"
        os.environ["DB_TDENGINE_DATABASE"] = "tddb"

        config = DatabaseConfig()

        assert config.tdengine_host == "tdengine-host"
        assert config.tdengine_port == 7030
        assert config.tdengine_username == "tduser"
        assert config.tdengine_password == "tdpass"
        assert config.tdengine_database == "tddb"

    def test_get_postgresql_url_default(self, clean_env):
        """测试获取默认PostgreSQL连接字符串"""
        config = DatabaseConfig()
        url = config.get_postgresql_url()

        expected = "postgresql://postgres:postgres@localhost:5432/mystocks"
        assert url == expected

    def test_get_postgresql_url_custom(self, clean_env):
        """测试获取自定义PostgreSQL连接字符串"""
        os.environ["DB_POSTGRESQL_USERNAME"] = "myuser"
        os.environ["DB_POSTGRESQL_PASSWORD"] = "mypass"
        os.environ["DB_POSTGRESQL_HOST"] = "myhost"
        os.environ["DB_POSTGRESQL_PORT"] = "1234"
        os.environ["DB_POSTGRESQL_DATABASE"] = "mydb"

        config = DatabaseConfig()
        url = config.get_postgresql_url()

        expected = "postgresql://myuser:mypass@myhost:1234/mydb"
        assert url == expected

    def test_get_tdengine_url_default(self, clean_env):
        """测试获取默认TDengine连接字符串"""
        config = DatabaseConfig()
        url = config.get_tdengine_url()

        expected = "taosws://root:taosdata@localhost:6030/"
        assert url == expected

    def test_get_tdengine_url_custom(self, clean_env):
        """测试获取自定义TDengine连接字符串"""
        os.environ["DB_TDENGINE_USERNAME"] = "tduser"
        os.environ["DB_TDENGINE_PASSWORD"] = "tdpass"
        os.environ["DB_TDENGINE_HOST"] = "tdhost"
        os.environ["DB_TDENGINE_PORT"] = "8080"

        config = DatabaseConfig()
        url = config.get_tdengine_url()

        expected = "taosws://tduser:tdpass@tdhost:8080/"
        assert url == expected

    def test_validate_config_success_default(self, clean_env):
        """测试配置验证成功 - 默认配置"""
        config = DatabaseConfig()
        result = config.validate_config()
        assert result is True

    def test_validate_config_success_custom(self, clean_env):
        """测试配置验证成功 - 自定义配置"""
        os.environ["DB_POSTGRESQL_HOST"] = "test-host"
        os.environ["DB_POSTGRESQL_USERNAME"] = "test-user"
        os.environ["DB_POSTGRESQL_PASSWORD"] = "test-pass"
        os.environ["DB_POSTGRESQL_DATABASE"] = "test-db"
        os.environ["DB_TDENGINE_HOST"] = "td-test-host"
        os.environ["DB_TDENGINE_USERNAME"] = "td-test-user"
        os.environ["DB_TDENGINE_PASSWORD"] = "td-test-pass"
        os.environ["DB_TDENGINE_DATABASE"] = "td-test-db"

        config = DatabaseConfig()
        result = config.validate_config()
        assert result is True

    def test_validate_config_missing_postgresql_host(self, clean_env):
        """测试配置验证失败 - 缺少PostgreSQL主机"""
        os.environ["DB_POSTGRESQL_HOST"] = ""
        config = DatabaseConfig()

        with pytest.raises(ValueError, match="PostgreSQL配置不完整"):
            config.validate_config()

    def test_validate_config_missing_postgresql_username(self, clean_env):
        """测试配置验证失败 - 缺少PostgreSQL用户名"""
        os.environ["DB_POSTGRESQL_USERNAME"] = ""
        config = DatabaseConfig()

        with pytest.raises(ValueError, match="PostgreSQL配置不完整"):
            config.validate_config()

    def test_validate_config_missing_postgresql_password(self, clean_env):
        """测试配置验证失败 - 缺少PostgreSQL密码"""
        os.environ["DB_POSTGRESQL_PASSWORD"] = ""
        config = DatabaseConfig()

        with pytest.raises(ValueError, match="PostgreSQL配置不完整"):
            config.validate_config()

    def test_validate_config_missing_postgresql_database(self, clean_env):
        """测试配置验证失败 - 缺少PostgreSQL数据库"""
        os.environ["DB_POSTGRESQL_DATABASE"] = ""
        config = DatabaseConfig()

        with pytest.raises(ValueError, match="PostgreSQL配置不完整"):
            config.validate_config()

    def test_validate_config_missing_tdengine_host(self, clean_env):
        """测试配置验证失败 - 缺少TDengine主机"""
        os.environ["DB_TDENGINE_HOST"] = ""
        config = DatabaseConfig()

        with pytest.raises(ValueError, match="TDengine配置不完整"):
            config.validate_config()

    def test_validate_config_missing_tdengine_username(self, clean_env):
        """测试配置验证失败 - 缺少TDengine用户名"""
        os.environ["DB_TDENGINE_USERNAME"] = ""
        config = DatabaseConfig()

        with pytest.raises(ValueError, match="TDengine配置不完整"):
            config.validate_config()

    def test_validate_config_missing_tdengine_password(self, clean_env):
        """测试配置验证失败 - 缺少TDengine密码"""
        os.environ["DB_TDENGINE_PASSWORD"] = ""
        config = DatabaseConfig()

        with pytest.raises(ValueError, match="TDengine配置不完整"):
            config.validate_config()

    def test_validate_config_missing_tdengine_database(self, clean_env):
        """测试配置验证失败 - 缺少TDengine数据库"""
        os.environ["DB_TDENGINE_DATABASE"] = ""
        config = DatabaseConfig()

        with pytest.raises(ValueError, match="TDengine配置不完整"):
            config.validate_config()

    def test_validate_config_invalid_postgresql_port_low(self, clean_env):
        """测试配置验证失败 - PostgreSQL端口过低"""
        os.environ["DB_POSTGRESQL_PORT"] = "0"
        config = DatabaseConfig()

        with pytest.raises(ValueError, match="PostgreSQL端口必须在1-65535之间"):
            config.validate_config()

    def test_validate_config_invalid_postgresql_port_high(self, clean_env):
        """测试配置验证失败 - PostgreSQL端口过高"""
        os.environ["DB_POSTGRESQL_PORT"] = "65536"
        config = DatabaseConfig()

        with pytest.raises(ValueError, match="PostgreSQL端口必须在1-65535之间"):
            config.validate_config()

    def test_validate_config_invalid_tdengine_port_low(self, clean_env):
        """测试配置验证失败 - TDengine端口过低"""
        os.environ["DB_TDENGINE_PORT"] = "0"
        config = DatabaseConfig()

        with pytest.raises(ValueError, match="TDengine端口必须在1-65535之间"):
            config.validate_config()

    def test_validate_config_invalid_tdengine_port_high(self, clean_env):
        """测试配置验证失败 - TDengine端口过高"""
        os.environ["DB_TDENGINE_PORT"] = "70000"
        config = DatabaseConfig()

        with pytest.raises(ValueError, match="TDengine端口必须在1-65535之间"):
            config.validate_config()

    def test_validate_config_valid_port_ranges(self, clean_env):
        """测试配置验证成功 - 有效端口范围"""
        os.environ["DB_POSTGRESQL_PORT"] = "1"
        os.environ["DB_TDENGINE_PORT"] = "65535"

        config = DatabaseConfig()
        assert config.postgresql_port == 1
        assert config.tdengine_port == 65535

        result = config.validate_config()
        assert result is True

    def test_port_conversion_to_int(self, clean_env):
        """测试端口转换为整数"""
        os.environ["DB_POSTGRESQL_PORT"] = "3306"
        os.environ["DB_TDENGINE_PORT"] = "9090"

        config = DatabaseConfig()
        assert isinstance(config.postgresql_port, int)
        assert isinstance(config.tdengine_port, int)
        assert config.postgresql_port == 3306
        assert config.tdengine_port == 9090

    def test_special_characters_in_password(self, clean_env):
        """测试密码中的特殊字符"""
        os.environ["DB_POSTGRESQL_PASSWORD"] = "p@ssw0rd!#$"
        os.environ["DB_TDENGINE_PASSWORD"] = "t@d@t@_p@ss!"

        config = DatabaseConfig()
        assert config.postgresql_password == "p@ssw0rd!#$"
        assert config.tdengine_password == "t@d@t@_p@ss!"

        # 验证连接字符串包含特殊字符
        postgresql_url = config.get_postgresql_url()
        assert "p@ssw0rd!#$" in postgresql_url

        tdengine_url = config.get_tdengine_url()
        assert "t@d@t@_p@ss!" in tdengine_url

    def test_database_names_with_special_characters(self, clean_env):
        """测试数据库名称中的特殊字符"""
        os.environ["DB_POSTGRESQL_DATABASE"] = "my_test-db_2023"
        os.environ["DB_TDENGINE_DATABASE"] = "td_test-db_2023"

        config = DatabaseConfig()
        assert config.postgresql_database == "my_test-db_2023"
        assert config.tdengine_database == "td_test-db_2023"

        postgresql_url = config.get_postgresql_url()
        tdengine_url = config.get_tdengine_url()

        assert "my_test-db_2023" in postgresql_url
        # TDengine URL格式中不包含数据库名称，连接时指定

    def test_unicode_support(self, clean_env):
        """测试Unicode支持"""
        os.environ["DB_POSTGRESQL_HOST"] = "本地主机"
        os.environ["DB_POSTGRESQL_USERNAME"] = "用户"
        os.environ["DB_POSTGRESQL_DATABASE"] = "测试数据库"

        config = DatabaseConfig()
        assert config.postgresql_host == "本地主机"
        assert config.postgresql_username == "用户"
        assert config.postgresql_database == "测试数据库"


class TestGlobalConfigFunction:
    """测试全局配置函数"""

    def test_get_database_config_singleton(self, clean_env):
        """测试全局配置单例模式"""
        config1 = get_database_config()
        config2 = get_database_config()

        # 应该返回同一个实例
        assert config1 is config2

    def test_get_database_config_returns_instance(self, clean_env):
        """测试返回正确的实例类型"""
        config = get_database_config()
        assert isinstance(config, DatabaseConfig)

    def test_get_database_config_with_environment(self, clean_env):
        """测试环境变量对全局配置的影响"""
        os.environ["DB_POSTGRESQL_HOST"] = "global-test-host"

        config = get_database_config()
        assert config.postgresql_host == "global-test-host"

    def test_multiple_calls_consistency(self, clean_env):
        """测试多次调用的一致性"""
        # 第一次调用
        config1 = get_database_config()

        # 修改环境变量
        os.environ["DB_POSTGRESQL_HOST"] = "consistency-test"

        # 第二次调用（应该返回缓存的实例）
        config2 = get_database_config()

        # 应该是同一个实例，但环境变量的修改不会影响已创建的实例
        assert config1 is config2
        assert config1.postgresql_host == "localhost"  # 原始默认值


class TestConfigIntegration:
    """测试配置集成功能"""

    def test_complete_workflow(self, clean_env):
        """测试完整的配置工作流程"""
        # 1. 设置环境变量
        os.environ["DB_POSTGRESQL_HOST"] = "workflow-host"
        os.environ["DB_POSTGRESQL_PORT"] = "5433"
        os.environ["DB_POSTGRESQL_USERNAME"] = "workflow-user"
        os.environ["DB_POSTGRESQL_PASSWORD"] = "workflow-pass"
        os.environ["DB_POSTGRESQL_DATABASE"] = "workflow-db"

        os.environ["DB_TDENGINE_HOST"] = "td-workflow-host"
        os.environ["DB_TDENGINE_PORT"] = "6031"
        os.environ["DB_TDENGINE_USERNAME"] = "td-workflow-user"
        os.environ["DB_TDENGINE_PASSWORD"] = "td-workflow-pass"
        os.environ["DB_TDENGINE_DATABASE"] = "td-workflow-db"

        # 2. 创建配置实例
        config = DatabaseConfig()

        # 3. 验证配置
        assert config.postgresql_host == "workflow-host"
        assert config.postgresql_port == 5433
        assert config.tdengine_host == "td-workflow-host"
        assert config.tdengine_port == 6031

        # 4. 验证连接字符串
        postgresql_url = config.get_postgresql_url()
        tdengine_url = config.get_tdengine_url()

        assert "workflow-user" in postgresql_url
        assert "workflow-host" in postgresql_url
        assert "5433" in postgresql_url
        assert "workflow-db" in postgresql_url

        assert "td-workflow-user" in tdengine_url
        assert "td-workflow-host" in tdengine_url
        assert "6031" in tdengine_url

        # 5. 验证配置
        result = config.validate_config()
        assert result is True

    def test_config_persistence(self, clean_env):
        """测试配置持久化"""
        # 创建配置并验证
        config = DatabaseConfig()
        original_pg_host = config.postgresql_host
        original_td_host = config.tdengine_host

        assert original_pg_host == "localhost"
        assert original_td_host == "localhost"

        # 修改环境变量应该不会影响已创建的实例
        os.environ["DB_POSTGRESQL_HOST"] = "new-host"
        os.environ["DB_TDENGINE_HOST"] = "new-td-host"

        # 实例不应该改变
        assert config.postgresql_host == original_pg_host
        assert config.tdengine_host == original_td_host


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
