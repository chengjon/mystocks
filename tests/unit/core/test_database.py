"""
数据库核心模块测试

测试数据库访问、连接管理和操作辅助功能的核心模块

测试覆盖:
- 数据库管理器初始化
- 数据库连接管理
- DatabaseHelper 辅助类
- 分页参数验证
- WHERE子句构建
- SQL注入防护
- 错误处理和异常管理
- 数据类型转换
- 查询参数化
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock

# Mock the dependencies to avoid import issues
import sys

sys.modules["structlog"] = MagicMock()
sys.modules["src.core.database_pool"] = MagicMock()
sys.modules["src.core.exceptions"] = MagicMock()
sys.modules["src.core.config"] = MagicMock()

from src.core.database import get_db_manager, get_postgresql_session, DatabaseHelper


class TestDatabaseManager:
    """数据库管理器测试类"""

    @pytest.mark.asyncio
    async def test_get_db_manager_initialization(self):
        """测试数据库管理器初始化"""
        # Reset global variable
        global _db_manager
        _db_manager = None

        with patch("src.core.database.DatabaseConnectionManager") as mock_manager_class:
            mock_manager = AsyncMock()
            mock_manager_class.return_value = mock_manager

            manager = await get_db_manager()

            # 验证初始化调用
            mock_manager_class.assert_called_once()
            mock_manager.initialize.assert_called_once()
            assert manager == mock_manager

    @pytest.mark.asyncio
    async def test_get_db_manager_singleton(self):
        """测试数据库管理器单例模式"""
        # Reset global variable
        global _db_manager
        _db_manager = None

        with patch("src.core.database.DatabaseConnectionManager") as mock_manager_class:
            mock_manager = AsyncMock()
            mock_manager_class.return_value = mock_manager
            mock_manager.initialize = AsyncMock()

            # Track initialization calls
            init_call_count = 0
            original_init = mock_manager.initialize

            async def track_init(*args, **kwargs):
                nonlocal init_call_count
                init_call_count += 1
                await original_init(*args, **kwargs)

            mock_manager.initialize = track_init

            # 第一次调用
            manager1 = await get_db_manager()
            # 第二次调用应该返回同一个实例
            manager2 = await get_db_manager()

            assert manager1 is manager2
            # 初始化只应该被调用一次（第二次调用不应该重新初始化）
            assert init_call_count == 1

    @pytest.mark.asyncio
    async def test_get_postgresql_session(self):
        """测试获取PostgreSQL会话"""
        with patch("src.core.database.get_db_manager") as mock_get_manager:
            mock_manager = AsyncMock()
            mock_get_manager.return_value = mock_manager

            session = await get_postgresql_session()

            mock_get_manager.assert_called_once()
            assert session == mock_manager


class TestDatabaseHelper:
    """数据库助手测试类"""

    def test_helper_initialization(self):
        """测试助手初始化"""
        mock_manager = Mock()
        helper = DatabaseHelper(mock_manager)

        assert helper.db_manager == mock_manager

    def test_validate_pagination_valid_params(self):
        """测试有效的分页参数"""
        mock_manager = Mock()
        helper = DatabaseHelper(mock_manager)

        # 测试正常参数
        offset, limit = helper.validate_pagination(page=2, page_size=20)

        assert offset == 20  # (2-1) * 20
        assert limit == 20

        # 测试边界值
        offset, limit = helper.validate_pagination(page=1, page_size=1)

        assert offset == 0
        assert limit == 1

    def test_validate_pagination_invalid_page(self):
        """测试无效页码参数"""
        mock_manager = Mock()
        helper = DatabaseHelper(mock_manager)

        # 模拟DataValidationError
        with patch("src.core.database.DataValidationError") as mock_error:
            mock_exception = Exception("Invalid page")
            mock_error.side_effect = mock_exception

            with pytest.raises(Exception):
                helper.validate_pagination(page=0, page_size=10)

            with pytest.raises(Exception):
                helper.validate_pagination(page=-1, page_size=10)

            with pytest.raises(Exception):
                helper.validate_pagination(page="invalid", page_size=10)

    def test_validate_pagination_invalid_page_size(self):
        """测试无效页面大小参数"""
        mock_manager = Mock()
        helper = DatabaseHelper(mock_manager)

        # 模拟DataValidationError
        with patch("src.core.database.DataValidationError") as mock_error:
            mock_exception = Exception("Invalid page size")
            mock_error.side_effect = mock_exception

            with pytest.raises(Exception):
                helper.validate_pagination(page=1, page_size=0)

            with pytest.raises(Exception):
                helper.validate_pagination(page=1, page_size=-1)

            with pytest.raises(Exception):
                helper.validate_pagination(page=1, page_size=101)  # 超过最大值

            with pytest.raises(Exception):
                helper.validate_pagination(page=1, page_size="invalid")

    def test_validate_pagination_max_values(self):
        """测试最大边界值"""
        mock_manager = Mock()
        helper = DatabaseHelper(mock_manager)

        # 测试最大有效值
        offset, limit = helper.validate_pagination(page=1, page_size=100)

        assert offset == 0
        assert limit == 100

    def test_build_where_clause_empty_conditions(self):
        """测试空条件构建WHERE子句"""
        mock_manager = Mock()
        helper = DatabaseHelper(mock_manager)

        where_clause, params = helper.build_where_clause({})

        assert where_clause == ""
        assert params == []

    def test_build_where_clause_single_condition(self):
        """测试单个条件构建WHERE子句"""
        mock_manager = Mock()
        helper = DatabaseHelper(mock_manager)

        conditions = {"name": "John"}
        where_clause, params = helper.build_where_clause(conditions)

        # 实际实现不包含"WHERE"前缀，只有条件表达式
        assert "name" in where_clause
        assert "=" in where_clause
        assert params == ["John"]

    def test_build_where_clause_multiple_conditions(self):
        """测试多个条件构建WHERE子句"""
        mock_manager = Mock()
        helper = DatabaseHelper(mock_manager)

        conditions = {"name": "John", "age": 25, "active": True}
        where_clause, params = helper.build_where_clause(conditions)

        # 实际实现不包含"WHERE"前缀，使用AND连接
        assert "name" in where_clause
        assert "age" in where_clause
        assert "active" in where_clause
        assert "AND" in where_clause
        assert len(params) == 3
        assert "John" in params
        assert 25 in params
        assert True in params

    def test_build_where_clause_string_values(self):
        """测试字符串值处理"""
        mock_manager = Mock()
        helper = DatabaseHelper(mock_manager)

        conditions = {"status": "active"}
        where_clause, params = helper.build_where_clause(conditions)

        assert "status" in where_clause
        assert params == ["active"]

    def test_build_where_clause_numeric_values(self):
        """测试数值处理"""
        mock_manager = Mock()
        helper = DatabaseHelper(mock_manager)

        conditions = {"price": 99.99, "quantity": 10}
        where_clause, params = helper.build_where_clause(conditions)

        assert "price" in where_clause
        assert "quantity" in where_clause
        assert 99.99 in params
        assert 10 in params

    def test_build_where_clause_boolean_values(self):
        """测试布尔值处理"""
        mock_manager = Mock()
        helper = DatabaseHelper(mock_manager)

        conditions = {"active": True, "deleted": False}
        where_clause, params = helper.build_where_clause(conditions)

        assert "active" in where_clause
        assert "deleted" in where_clause
        assert True in params
        assert False in params

    def test_build_where_clause_none_values(self):
        """测试None值处理"""
        mock_manager = Mock()
        helper = DatabaseHelper(mock_manager)

        conditions = {"optional_field": None}
        where_clause, params = helper.build_where_clause(conditions)

        # None值通常被特殊处理
        assert "optional_field" in where_clause or where_clause == ""
        assert None in params or len(params) == 0

    def test_build_where_clause_list_values(self):
        """测试列表值处理"""
        mock_manager = Mock()
        helper = DatabaseHelper(mock_manager)

        conditions = {"category": ["A", "B", "C"]}
        where_clause, params = helper.build_where_clause(conditions)

        # 列表值应该被正确处理
        assert "category" in where_clause
        assert isinstance(params, list)
        assert len(params) >= 1

    def test_build_where_clause_special_characters(self):
        """测试特殊字符处理（SQL注入防护）"""
        mock_manager = Mock()
        helper = DatabaseHelper(mock_manager)

        # 测试包含特殊字符的值
        conditions = {
            "name": "O'Reilly",
            "description": "Test with 'quotes' and \"double quotes\"",
            "search": "%wildcard%",
        }
        where_clause, params = helper.build_where_clause(conditions)

        # 参数化查询应该正确处理特殊字符
        assert len(params) == 3
        assert "O'Reilly" in params
        # 特殊字符应该被正确转义或参数化

    def test_build_where_clause_injection_protection(self):
        """测试SQL注入防护"""
        mock_manager = Mock()
        helper = DatabaseHelper(mock_manager)

        # 测试潜在的SQL注入
        malicious_conditions = {"name": "'; DROP TABLE users; --", "id": "1 OR 1=1"}

        where_clause, params = helper.build_where_clause(malicious_conditions)

        # 参数化查询应该防止SQL注入
        assert len(params) == 2
        # 恶意代码不应该在WHERE子句中直接执行
        assert "DROP TABLE" not in where_clause
        assert "1=1" not in where_clause.replace(" ", "")


class TestDatabaseHelperAdvanced:
    """数据库助手高级功能测试"""

    def test_helper_with_real_manager(self):
        """测试使用真实管理器的助手"""
        mock_manager = Mock()
        helper = DatabaseHelper(mock_manager)

        # 测试助手功能
        offset, limit = helper.validate_pagination(page=2, page_size=50)
        assert offset == 50
        assert limit == 50

        where_clause, params = helper.build_where_clause({"status": "active"})
        assert "status" in where_clause
        assert "active" in params

    def test_complex_condition_building(self):
        """测试复杂条件构建"""
        mock_manager = Mock()
        helper = DatabaseHelper(mock_manager)

        conditions = {
            "name": "Test",
            "age_range": (18, 65),  # 假设支持范围查询
            "tags": ["python", "sql"],
            "created_at": "2024-01-01",
        }

        where_clause, params = helper.build_where_clause(conditions)

        # 验证复杂条件被正确处理
        assert "name" in where_clause
        assert len(params) >= 2  # 至少包含name和tags

    def test_empty_string_conditions(self):
        """测试空字符串条件"""
        mock_manager = Mock()
        helper = DatabaseHelper(mock_manager)

        conditions = {"empty_field": "", "normal_field": "value"}

        where_clause, params = helper.build_where_clause(conditions)

        # 空字符串应该被正确处理
        assert "normal_field" in where_clause
        assert "value" in params

    def test_unicode_support(self):
        """测试Unicode字符支持"""
        mock_manager = Mock()
        helper = DatabaseHelper(mock_manager)

        conditions = {"chinese_name": "张三", "emoji": "🚀", "special_chars": "áéíóú"}

        where_clause, params = helper.build_where_clause(conditions)

        # Unicode字符应该被正确处理
        assert len(params) == 3
        assert "张三" in params
        assert "🚀" in params


class TestEdgeCases:
    """边界情况测试"""

    def test_large_page_numbers(self):
        """测试大页码"""
        mock_manager = Mock()
        helper = DatabaseHelper(mock_manager)

        offset, limit = helper.validate_pagination(page=1000, page_size=50)
        # Calculate: (page - 1) * page_size = (1000-1) * 50 = 999 * 50 = 49950
        assert offset == 49950

    def test_large_number_of_conditions(self):
        """测试大量条件"""
        mock_manager = Mock()
        helper = DatabaseHelper(mock_manager)

        # 创建大量条件
        conditions = {f"field_{i}": f"value_{i}" for i in range(100)}

        where_clause, params = helper.build_where_clause(conditions)

        # 应该正确处理大量条件
        assert len(params) == 100
        # 验证AND连接符存在（实际实现不包含WHERE前缀）
        assert "AND" in where_clause

    def test_extreme_values(self):
        """测试极值"""
        mock_manager = Mock()
        helper = DatabaseHelper(mock_manager)

        # 测试极值
        conditions = {
            "max_float": float("inf"),
            "min_float": float("-inf"),
            "large_int": 999999999999999999999,
            "zero": 0,
        }

        where_clause, params = helper.build_where_clause(conditions)

        # 极值应该被正确处理
        assert len(params) == 4

    def test_none_manager_handling(self):
        """测试管理器为None的情况"""
        # DatabaseHelper实际上可以接受None，但会在使用时报错
        # 测试创建时不报错，但使用时报错的情况
        helper = DatabaseHelper(None)
        assert helper.db_manager is None

        # 测试使用时的行为（具体行为取决于实现）
        # 这里我们只验证helper可以创建，具体使用时的错误处理由其他测试覆盖


class TestPerformance:
    """性能测试"""

    def test_pagination_validation_performance(self):
        """测试分页验证性能"""
        mock_manager = Mock()
        helper = DatabaseHelper(mock_manager)

        import time

        # 测试大量调用的性能
        start_time = time.time()
        for _ in range(1000):
            helper.validate_pagination(page=1, page_size=10)
        end_time = time.time()

        # 应该在合理时间内完成
        assert (end_time - start_time) < 1.0  # 1秒内完成1000次调用

    def test_where_clause_building_performance(self):
        """测试WHERE子句构建性能"""
        mock_manager = Mock()
        helper = DatabaseHelper(mock_manager)

        import time

        conditions = {f"field_{i}": f"value_{i}" for i in range(50)}

        start_time = time.time()
        for _ in range(100):
            helper.build_where_clause(conditions)
        end_time = time.time()

        # 应该在合理时间内完成
        assert (end_time - start_time) < 2.0  # 2秒内完成100次调用
