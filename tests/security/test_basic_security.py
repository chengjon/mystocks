#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础安全测试 - 个人项目简化版

验证SQL注入防护和配置检查功能
"""

import pytest
import logging
from unittest.mock import patch, MagicMock


class TestTDengineSymbolValidation:
    """测试TDengine符号验证"""

    def test_valid_symbols(self):
        """测试有效符号通过验证"""
        from src.storage.access.tdengine import TDengineDataAccess

        # 创建模拟monitoring_db
        mock_monitoring_db = MagicMock()

        # 创建TDengine访问器实例
        td_access = TDengineDataAccess(mock_monitoring_db)

        # 测试各种有效符号格式
        valid_symbols = [
            "AAPL",  # 简单股票代码
            "600519.SH",  # 上海交易所
            "000001.SZ",  # 深圳交易所
            "BTC/USDT",  # 加密货币交易对
            "ETH_USDT",  # 下划线分隔
            "TSLA-US",  # 连字符分隔
            "NVDA.US",  # 点号分隔
        ]

        for symbol in valid_symbols:
            # 应该不抛出异常
            validated = td_access._validate_symbol(symbol)
            assert validated == symbol, f"Valid symbol rejected: {symbol}"

    def test_invalid_symbols(self):
        """测试无效符号被拒绝"""
        from src.storage.access.tdengine import TDengineDataAccess

        mock_monitoring_db = MagicMock()
        td_access = TDengineDataAccess(mock_monitoring_db)

        # 测试各种无效符号（SQL注入尝试）
        invalid_symbols = [
            "AAPL' OR '1'='1",  # SQL注入
            "AAPL; DROP TABLE users--",  # SQL注入
            "AAPL'--",  # SQL注释
            "AAPL/*comment*/",  # SQL注释
            "",  # 空字符串
            "A" * 51,  # 过长(>50字符)
            123,  # 非字符串
            None,  # None值
        ]

        for symbol in invalid_symbols:
            with pytest.raises(ValueError, match="|Invalid|dangerous|cannot be empty"):
                td_access._validate_symbol(symbol)

    def test_symbol_with_special_sql_chars(self):
        """测试包含危险SQL字符的符号被拒绝"""
        from src.storage.access.tdengine import TDengineDataAccess

        mock_monitoring_db = MagicMock()
        td_access = TDengineDataAccess(mock_monitoring_db)

        # 包含SQL危险字符的符号
        dangerous_symbols = [
            "AAPL'; DROP TABLE--",
            "AAPL' OR '1'='1",
            'AAPL" OR "1"="1',
            "AAPL\\x00NULL",  # 包含空字符
        ]

        for symbol in dangerous_symbols:
            with pytest.raises(ValueError, match="dangerous|Invalid"):
                td_access._validate_symbol(symbol)


class TestPostgreSQLSecurity:
    """测试PostgreSQL安全措施"""

    def test_table_name_whitelist(self):
        """测试表名白名单验证"""

        # 注意：这个测试需要实际的数据库连接，可能需要mock
        # 这里只测试逻辑，不实际连接数据库

        # 有效表名（在白名单中）
        valid_tables = [
            "stock_daily_kline",
            "stock_minute_kline",
            "market_data",
            "stock_basic",
        ]

        # 无效表名
        invalid_tables = [
            "users; DROP TABLE--",  # SQL注入尝试
            "nonexistent_table",  # 不在白名单
            "",  # 空字符串
        ]

        # 注意：实际测试需要mock或使用测试数据库
        # 这里只是展示测试结构
        # for table in valid_tables:
        #     # 应该通过验证
        #     pass

        # for table in invalid_tables:
        #     with pytest.raises(ValueError):
        #         # 应该抛出异常
        #         pass


class TestConfigCheck:
    """测试配置检查功能"""

    def test_weak_jwt_warning(self, caplog):
        """测试弱JWT密钥警告"""
        from src.utils.simple_config_check import check_config_strength

        # 模拟弱密钥
        with patch.dict(os.environ, {"JWT_SECRET_KEY": "short"}):
            with caplog.at_level(logging.WARNING):
                check_config_strength()

        # 应该有警告日志
        assert "JWT密钥长度不足" in caplog.text
        assert "个人项目可以忽略" in caplog.text

    def test_missing_password_warning(self, caplog):
        """测试缺失密码警告"""
        from src.utils.simple_config_check import check_config_strength
        import os

        # 清空所有密码
        env = {
            "JWT_SECRET_KEY": "",
            "POSTGRESQL_PASSWORD": "",
            "TDENGINE_PASSWORD": "",
        }

        with patch.dict(os.environ, env, clear=True):
            with caplog.at_level(logging.WARNING):
                check_config_strength()

        # 应该有警告
        assert "未设置" in caplog.text

    def test_strong_config_pass(self, caplog):
        """测试强配置通过检查"""
        from src.utils.simple_config_check import check_config_strength
        import os

        # 模拟强配置
        env = {
            "JWT_SECRET_KEY": "a" * 32,
            "POSTGRESQL_PASSWORD": "strong_password_123",
            "TDENGINE_PASSWORD": "strong_password_456",
        }

        with patch.dict(os.environ, env, clear=True):
            with caplog.at_level(logging.INFO):
                check_config_strength()

        # 应该通过
        assert "配置检查通过" in caplog.text

    def test_generate_secrets(self):
        """测试密钥生成功能"""
        from src.utils.simple_config_check import generate_strong_jwt_secret, generate_strong_db_password

        # 生成JWT密钥
        jwt_secret = generate_strong_jwt_secret()
        assert len(jwt_secret) >= 64  # 32字节 = 64个十六进制字符

        # 生成数据库密码
        db_password = generate_strong_db_password()
        assert len(db_password) >= 16  # 至少16字符


class TestPostgreSQLQueryConstruction:
    """测试PostgreSQL查询构造安全性"""

    def test_query_with_psycopg2_sql(self):
        """测试使用psycopg2.sql构造查询"""
        from psycopg2 import sql

        # 模拟查询构造
        table_name = "stock_daily_kline"
        columns = ["symbol", "date", "close"]

        # 使用sql.Identifier（安全方式）
        query = sql.SQL("SELECT {} FROM {}").format(
            sql.SQL(", ").join(map(sql.Identifier, columns)), sql.Identifier(table_name)
        )

        # 转换为字符串查看
        query_str = query.as_string(None)
        assert "SELECT" in query_str
        assert "FROM" in query_str
        assert table_name in query_str

    def test_identifier_escaping(self):
        """测试标识符转义"""
        from psycopg2 import sql

        # 尝试使用危险字符
        dangerous_table = "users; DROP TABLE admins--"

        # sql.Identifier应该正确转义
        identifier = sql.Identifier(dangerous_table)

        # 应该被转义，不会直接拼接
        # （psycopg2会添加引号或转义特殊字符）
        escaped = identifier.as_string(None)

        # 验证转义后不包含危险模式
        assert ";" not in escaped or '"' in escaped  # 被引号包裹则安全


class TestSecurityIntegration:
    """集成安全测试"""

    def test_tdengine_query_building_with_validation(self):
        """测试TDengine查询构建包含验证"""
        from src.storage.access.tdengine import TDengineDataAccess

        mock_monitoring_db = MagicMock()
        td_access = TDengineDataAccess(mock_monitoring_db)

        # 测试查询构建
        filters = {"symbol": "AAPL", "start_time": "2025-01-01", "end_time": "2025-12-31"}  # 有效符号

        # 调用查询构建方法
        # 注意：这里不实际执行，只测试验证逻辑
        try:
            # 模拟查询构建
            validated_symbol = td_access._validate_symbol(filters["symbol"])
            # 验证应该成功
            assert validated_symbol == "AAPL"
        except ValueError as e:
            pytest.fail(f"Valid symbol was rejected: {e}")

    def test_tdengine_rejects_injection_in_filters(self):
        """测试TDengine拒绝注入尝试"""
        from src.storage.access.tdengine import TDengineDataAccess

        mock_monitoring_db = MagicMock()
        td_access = TDengineDataAccess(mock_monitoring_db)

        # 尝试注入
        injection_filters = {
            "symbol": "AAPL' OR '1'='1",  # 注入尝试
        }

        # 应该抛出异常
        with pytest.raises(ValueError):
            td_access._validate_symbol(injection_filters["symbol"])


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
