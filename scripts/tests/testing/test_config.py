#!/usr/bin/env python3
"""
配置模块测试套件
提供完整的配置功能测试
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from unittest.mock import patch

# 导入被测试的模块
from src.core.config import DatabaseConfig, get_database_config


class TestDatabaseConfig:
    """DatabaseConfig 测试类"""

    def test_database_config_initialization_with_defaults(self):
        """测试使用默认值的初始化"""
        with patch.dict(os.environ, {}, clear=True):
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

    def test_database_config_initialization_with_env_vars(self):
        """测试使用环境变量的初始化"""
        env_vars = {
            "DB_POSTGRESQL_HOST": "custom-host",
            "DB_POSTGRESQL_PORT": "5433",
            "DB_POSTGRESQL_USERNAME": "custom-user",
            "DB_POSTGRESQL_PASSWORD": "custom-pass",
            "DB_POSTGRESQL_DATABASE": "custom-db",
            "DB_TDENGINE_HOST": "td-custom-host",
            "DB_TDENGINE_PORT": "6031",
            "DB_TDENGINE_USERNAME": "td-custom-user",
            "DB_TDENGINE_PASSWORD": "td-custom-pass",
            "DB_TDENGINE_DATABASE": "td-custom-db",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = DatabaseConfig()

            # PostgreSQL自定义值
            assert config.postgresql_host == "custom-host"
            assert config.postgresql_port == 5433
            assert config.postgresql_username == "custom-user"
            assert config.postgresql_password == "custom-pass"
            assert config.postgresql_database == "custom-db"

            # TDengine自定义值
            assert config.tdengine_host == "td-custom-host"
            assert config.tdengine_port == 6031
            assert config.tdengine_username == "td-custom-user"
            assert config.tdengine_password == "td-custom-pass"
            assert config.tdengine_database == "td-custom-db"

    def test_get_postgresql_url_default(self):
        """测试获取默认PostgreSQL连接字符串"""
        with patch.dict(os.environ, {}, clear=True):
            config = DatabaseConfig()
            url = config.get_postgresql_url()

            expected_url = "postgresql://postgres:postgres@localhost:5432/mystocks"
            assert url == expected_url

    def test_get_postgresql_url_custom(self):
        """测试获取自定义PostgreSQL连接字符串"""
        env_vars = {
            "DB_POSTGRESQL_USERNAME": "myuser",
            "DB_POSTGRESQL_PASSWORD": "mypass",
            "DB_POSTGRESQL_HOST": "myhost",
            "DB_POSTGRESQL_PORT": "5433",
            "DB_POSTGRESQL_DATABASE": "mydb",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = DatabaseConfig()
            url = config.get_postgresql_url()

            expected_url = "postgresql://myuser:mypass@myhost:5433/mydb"
            assert url == expected_url

    def test_get_tdengine_url_default(self):
        """测试获取默认TDengine连接字符串"""
        with patch.dict(os.environ, {}, clear=True):
            config = DatabaseConfig()
            url = config.get_tdengine_url()

            expected_url = "taosws://root:taosdata@localhost:6030/"
            assert url == expected_url

    def test_get_tdengine_url_custom(self):
        """测试获取自定义TDengine连接字符串"""
        env_vars = {
            "DB_TDENGINE_USERNAME": "tduser",
            "DB_TDENGINE_PASSWORD": "tdpass",
            "DB_TDENGINE_HOST": "tdhost",
            "DB_TDENGINE_PORT": "6031",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = DatabaseConfig()
            url = config.get_tdengine_url()

            expected_url = "taosws://tduser:tdpass@tdhost:6031/"
            assert url == expected_url

    def test_validate_config_success(self):
        """测试有效配置验证"""
        env_vars = {
            "DB_POSTGRESQL_HOST": "localhost",
            "DB_POSTGRESQL_USERNAME": "user",
            "DB_POSTGRESQL_PASSWORD": "pass",
            "DB_POSTGRESQL_DATABASE": "db",
            "DB_POSTGRESQL_PORT": "5432",
            "DB_TDENGINE_HOST": "localhost",
            "DB_TDENGINE_USERNAME": "root",
            "DB_TDENGINE_PASSWORD": "pass",
            "DB_TDENGINE_DATABASE": "db",
            "DB_TDENGINE_PORT": "6030",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = DatabaseConfig()
            result = config.validate_config()
            assert result is True

    def test_validate_config_postgresql_missing_host(self):
        """测试PostgreSQL缺少主机名"""
        env_vars = {
            "DB_POSTGRESQL_HOST": "",  # 空主机名
            "DB_POSTGRESQL_USERNAME": "user",
            "DB_POSTGRESQL_PASSWORD": "pass",
            "DB_POSTGRESQL_DATABASE": "db",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = DatabaseConfig()
            with pytest.raises(ValueError, match="PostgreSQL配置不完整"):
                config.validate_config()

    def test_validate_config_postgresql_missing_username(self):
        """测试PostgreSQL缺少用户名"""
        env_vars = {
            "DB_POSTGRESQL_HOST": "localhost",
            "DB_POSTGRESQL_USERNAME": "",  # 空用户名
            "DB_POSTGRESQL_PASSWORD": "pass",
            "DB_POSTGRESQL_DATABASE": "db",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = DatabaseConfig()
            with pytest.raises(ValueError, match="PostgreSQL配置不完整"):
                config.validate_config()

    def test_validate_config_postgresql_missing_password(self):
        """测试PostgreSQL缺少密码"""
        env_vars = {
            "DB_POSTGRESQL_HOST": "localhost",
            "DB_POSTGRESQL_USERNAME": "user",
            "DB_POSTGRESQL_PASSWORD": "",  # 空密码
            "DB_POSTGRESQL_DATABASE": "db",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = DatabaseConfig()
            with pytest.raises(ValueError, match="PostgreSQL配置不完整"):
                config.validate_config()

    def test_validate_config_postgresql_missing_database(self):
        """测试PostgreSQL缺少数据库名"""
        env_vars = {
            "DB_POSTGRESQL_HOST": "localhost",
            "DB_POSTGRESQL_USERNAME": "user",
            "DB_POSTGRESQL_PASSWORD": "pass",
            "DB_POSTGRESQL_DATABASE": "",  # 空数据库名
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = DatabaseConfig()
            with pytest.raises(ValueError, match="PostgreSQL配置不完整"):
                config.validate_config()

    def test_validate_config_tdengine_missing_host(self):
        """测试TDengine缺少主机名"""
        env_vars = {
            "DB_POSTGRESQL_HOST": "localhost",
            "DB_POSTGRESQL_USERNAME": "user",
            "DB_POSTGRESQL_PASSWORD": "pass",
            "DB_POSTGRESQL_DATABASE": "db",
            "DB_TDENGINE_HOST": "",  # 空主机名
            "DB_TDENGINE_USERNAME": "root",
            "DB_TDENGINE_PASSWORD": "pass",
            "DB_TDENGINE_DATABASE": "db",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = DatabaseConfig()
            with pytest.raises(ValueError, match="TDengine配置不完整"):
                config.validate_config()

    def test_validate_config_tdengine_missing_username(self):
        """测试TDengine缺少用户名"""
        env_vars = {
            "DB_POSTGRESQL_HOST": "localhost",
            "DB_POSTGRESQL_USERNAME": "user",
            "DB_POSTGRESQL_PASSWORD": "pass",
            "DB_POSTGRESQL_DATABASE": "db",
            "DB_TDENGINE_HOST": "localhost",
            "DB_TDENGINE_USERNAME": "",  # 空用户名
            "DB_TDENGINE_PASSWORD": "pass",
            "DB_TDENGINE_DATABASE": "db",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = DatabaseConfig()
            with pytest.raises(ValueError, match="TDengine配置不完整"):
                config.validate_config()

    def test_validate_config_tdengine_missing_password(self):
        """测试TDengine缺少密码"""
        env_vars = {
            "DB_POSTGRESQL_HOST": "localhost",
            "DB_POSTGRESQL_USERNAME": "user",
            "DB_POSTGRESQL_PASSWORD": "pass",
            "DB_POSTGRESQL_DATABASE": "db",
            "DB_TDENGINE_HOST": "localhost",
            "DB_TDENGINE_USERNAME": "root",
            "DB_TDENGINE_PASSWORD": "",  # 空密码
            "DB_TDENGINE_DATABASE": "db",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = DatabaseConfig()
            with pytest.raises(ValueError, match="TDengine配置不完整"):
                config.validate_config()

    def test_validate_config_tdengine_missing_database(self):
        """测试TDengine缺少数据库名"""
        env_vars = {
            "DB_POSTGRESQL_HOST": "localhost",
            "DB_POSTGRESQL_USERNAME": "user",
            "DB_POSTGRESQL_PASSWORD": "pass",
            "DB_POSTGRESQL_DATABASE": "db",
            "DB_TDENGINE_HOST": "localhost",
            "DB_TDENGINE_USERNAME": "root",
            "DB_TDENGINE_PASSWORD": "pass",
            "DB_TDENGINE_DATABASE": "",  # 空数据库名
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = DatabaseConfig()
            with pytest.raises(ValueError, match="TDengine配置不完整"):
                config.validate_config()

    def test_validate_config_postgresql_port_too_low(self):
        """测试PostgreSQL端口过低"""
        env_vars = {
            "DB_POSTGRESQL_HOST": "localhost",
            "DB_POSTGRESQL_USERNAME": "user",
            "DB_POSTGRESQL_PASSWORD": "pass",
            "DB_POSTGRESQL_DATABASE": "db",
            "DB_POSTGRESQL_PORT": "0",  # 端口0无效
            "DB_TDENGINE_HOST": "localhost",
            "DB_TDENGINE_USERNAME": "root",
            "DB_TDENGINE_PASSWORD": "pass",
            "DB_TDENGINE_DATABASE": "db",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = DatabaseConfig()
            with pytest.raises(ValueError, match="PostgreSQL端口必须在1-65535之间"):
                config.validate_config()

    def test_validate_config_postgresql_port_too_high(self):
        """测试PostgreSQL端口过高"""
        env_vars = {
            "DB_POSTGRESQL_HOST": "localhost",
            "DB_POSTGRESQL_USERNAME": "user",
            "DB_POSTGRESQL_PASSWORD": "pass",
            "DB_POSTGRESQL_DATABASE": "db",
            "DB_POSTGRESQL_PORT": "65536",  # 端口65536无效
            "DB_TDENGINE_HOST": "localhost",
            "DB_TDENGINE_USERNAME": "root",
            "DB_TDENGINE_PASSWORD": "pass",
            "DB_TDENGINE_DATABASE": "db",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = DatabaseConfig()
            with pytest.raises(ValueError, match="PostgreSQL端口必须在1-65535之间"):
                config.validate_config()

    def test_validate_config_tdengine_port_too_low(self):
        """测试TDengine端口过低"""
        env_vars = {
            "DB_POSTGRESQL_HOST": "localhost",
            "DB_POSTGRESQL_USERNAME": "user",
            "DB_POSTGRESQL_PASSWORD": "pass",
            "DB_POSTGRESQL_DATABASE": "db",
            "DB_TDENGINE_HOST": "localhost",
            "DB_TDENGINE_USERNAME": "root",
            "DB_TDENGINE_PASSWORD": "pass",
            "DB_TDENGINE_DATABASE": "db",
            "DB_TDENGINE_PORT": "0",  # 端口0无效
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = DatabaseConfig()
            with pytest.raises(ValueError, match="TDengine端口必须在1-65535之间"):
                config.validate_config()

    def test_validate_config_tdengine_port_too_high(self):
        """测试TDengine端口过高"""
        env_vars = {
            "DB_POSTGRESQL_HOST": "localhost",
            "DB_POSTGRESQL_USERNAME": "user",
            "DB_POSTGRESQL_PASSWORD": "pass",
            "DB_POSTGRESQL_DATABASE": "db",
            "DB_TDENGINE_HOST": "localhost",
            "DB_TDENGINE_USERNAME": "root",
            "DB_TDENGINE_PASSWORD": "pass",
            "DB_TDENGINE_DATABASE": "db",
            "DB_TDENGINE_PORT": "65536",  # 端口65536无效
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = DatabaseConfig()
            with pytest.raises(ValueError, match="TDengine端口必须在1-65535之间"):
                config.validate_config()

    def test_validate_config_boundary_ports(self):
        """测试边界端口值"""
        env_vars = {
            "DB_POSTGRESQL_HOST": "localhost",
            "DB_POSTGRESQL_USERNAME": "user",
            "DB_POSTGRESQL_PASSWORD": "pass",
            "DB_POSTGRESQL_DATABASE": "db",
            "DB_POSTGRESQL_PORT": "1",  # 最小有效端口
            "DB_TDENGINE_HOST": "localhost",
            "DB_TDENGINE_USERNAME": "root",
            "DB_TDENGINE_PASSWORD": "pass",
            "DB_TDENGINE_DATABASE": "db",
            "DB_TDENGINE_PORT": "65535",  # 最大有效端口
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = DatabaseConfig()
            result = config.validate_config()
            assert result is True
            assert config.postgresql_port == 1
            assert config.tdengine_port == 65535

    def test_port_conversion_from_string(self):
        """测试从字符串转换端口号"""
        env_vars = {
            "DB_POSTGRESQL_PORT": "3306",  # 字符串格式的端口
            "DB_TDENGINE_PORT": "9042",  # 字符串格式的端口
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = DatabaseConfig()
            assert config.postgresql_port == 3306
            assert config.tdengine_port == 9042
            assert isinstance(config.postgresql_port, int)
            assert isinstance(config.tdengine_port, int)


class TestGetDatabaseConfig:
    """全局配置函数测试类"""

    def test_get_database_config_singleton(self):
        """测试配置单例模式"""
        with patch.dict(os.environ, {}, clear=True):
            # 清除全局状态
            import src.core.config

            src.core.config._db_config = None

            config1 = get_database_config()
            config2 = get_database_config()

            # 应该返回同一个实例
            assert config1 is config2
            assert isinstance(config1, DatabaseConfig)

    def test_get_database_config_lazily_initialized(self):
        """测试配置的延迟初始化"""
        with patch.dict(os.environ, {}, clear=True):
            # 清除全局状态
            import src.core.config

            src.core.config._db_config = None

            # 第一次调用应该创建实例
            config1 = get_database_config()
            assert isinstance(config1, DatabaseConfig)

            # 第二次调用应该返回已存在的实例
            config2 = get_database_config()
            assert config1 is config2

    def test_get_database_config_different_env_vars(self):
        """测试不同环境变量下的配置"""
        # 第一次调用
        env_vars1 = {"DB_POSTGRESQL_PORT": "5432"}
        with patch.dict(os.environ, env_vars1, clear=True):
            import src.core.config

            src.core.config._db_config = None

            config1 = get_database_config()
            assert config1.postgresql_port == 5432

        # 第二次调用（在不同环境中，但应该使用缓存的实例）
        env_vars2 = {"DB_POSTGRESQL_PORT": "5433"}
        with patch.dict(os.environ, env_vars2, clear=True):
            # 注意：因为已经有缓存的实例，不会重新读取环境变量
            config2 = get_database_config()
            assert config2 is config1  # 应该是同一个实例
            # 仍然是第一次的值，因为使用了缓存
            assert config2.postgresql_port == 5432


class TestDatabaseConfigEdgeCases:
    """DatabaseConfig 边界情况测试类"""

    def test_special_characters_in_credentials(self):
        """测试凭证中的特殊字符"""
        env_vars = {
            "DB_POSTGRESQL_PASSWORD": "p@ss#word!123",
            "DB_POSTGRESQL_USERNAME": "user@domain.com",
            "DB_TDENGINE_PASSWORD": "taos$%^&*()",
            "DB_TDENGINE_USERNAME": "user_name",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = DatabaseConfig()

            # 测试包含特殊字符的连接字符串
            pg_url = config.get_postgresql_url()
            assert "p@ss#word!123" in pg_url
            assert "user@domain.com" in pg_url

            td_url = config.get_tdengine_url()
            assert "taos$%^&*()" in td_url
            assert "user_name" in td_url

    def test_extreme_port_values(self):
        """测试极端端口值"""
        env_vars = {
            "DB_POSTGRESQL_PORT": "65535",  # 最大端口
            "DB_TDENGINE_PORT": "1",  # 最小端口
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = DatabaseConfig()

            # 验证极端端口值
            assert config.postgresql_port == 65535
            assert config.tdengine_port == 1

            # 验证配置有效性
            result = config.validate_config()
            assert result is True

    def test_whitespace_in_env_vars(self):
        """测试环境变量中的空白字符"""
        env_vars = {
            "DB_POSTGRESQL_HOST": "  localhost  ",
            "DB_POSTGRESQL_USERNAME": "  postgres  ",
            "DB_POSTGRESQL_DATABASE": "  mystocks  ",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = DatabaseConfig()

            # 注意：当前的实现不会自动去除空白字符
            assert config.postgresql_host == "  localhost  "
            assert config.postgresql_username == "  postgres  "
            assert config.postgresql_database == "  mystocks  "

    def test_unicode_in_env_vars(self):
        """测试环境变量中的Unicode字符"""
        env_vars = {
            "DB_POSTGRESQL_DATABASE": "测试数据库",
            "DB_TDENGINE_DATABASE": "时序数据库",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = DatabaseConfig()

            # Unicode字符应该被正确处理
            assert config.postgresql_database == "测试数据库"
            assert config.tdengine_database == "时序数据库"

            # 在连接字符串中也应该包含Unicode字符
            pg_url = config.get_postgresql_url()
            assert "测试数据库" in pg_url


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
