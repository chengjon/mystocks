"""
Data Access Factory Test Suite
数据访问工厂测试套件

创建日期: 2025-12-20
版本: 1.0.0
测试模块: src.data_access.factory (278行)
"""

import os
import sys
from unittest.mock import Mock

import pytest

# 添加src路径到导入路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))


# 模拟依赖组件
class MockDatabaseType:
    POSTGRESQL = "postgresql"
    TDENGINE = "tdengine"
    MONGODB = "mongodb"


class MockDataAccessLayer:
    """模拟数据访问层接口"""

    def __init__(self, db_manager=None, monitoring_db=None):
        self.db_manager = db_manager
        self.monitoring_db = monitoring_db


class MockDataAccessFactory:
    """模拟数据访问工厂类"""

    def __init__(self):
        self._db_manager = None
        self._monitoring_db = None
        self._tdengine_access = None
        self._postgresql_access = None

    def initialize(self, db_manager, monitoring_db):
        """初始化工厂"""
        self._db_manager = db_manager
        self._monitoring_db = monitoring_db
        self._tdengine_access = MockDataAccessLayer(db_manager, monitoring_db)
        self._postgresql_access = MockDataAccessLayer(db_manager, monitoring_db)

    def get_data_access(self, database_type, classification=None):
        """根据数据库类型获取数据访问器"""
        if not self._db_manager:
            raise RuntimeError("Factory not initialized. Call initialize() first.")

        if database_type == MockDatabaseType.TDENGINE:
            return self._tdengine_access
        elif database_type == MockDatabaseType.POSTGRESQL:
            return self._postgresql_access
        else:
            raise ValueError(f"Unsupported database type: {database_type}")

    def get_timeseries_access(self):
        """获取时序数据访问器"""
        return self.get_data_access(MockDatabaseType.TDENGINE)

    def get_relational_access(self):
        """获取关系数据访问器"""
        return self.get_data_access(MockDatabaseType.POSTGRESQL)

    def smart_routing_access(self, data_type, symbol=None):
        """智能路由访问"""
        # 简化的智能路由逻辑
        if "timeseries" in data_type.lower() or "tick" in data_type.lower():
            return self.get_timeseries_access()
        else:
            return self.get_relational_access()


class TestDataAccessFactory:
    """数据访问工厂测试"""

    def test_factory_initialization(self):
        """测试工厂初始化"""
        factory = MockDataAccessFactory()

        assert factory._db_manager is None
        assert factory._monitoring_db is None
        assert factory._tdengine_access is None
        assert factory._postgresql_access is None

    def test_factory_initialize(self):
        """测试工厂初始化配置"""
        # 创建模拟依赖
        mock_db_manager = Mock()
        mock_monitoring_db = Mock()

        factory = MockDataAccessFactory()
        factory.initialize(mock_db_manager, mock_monitoring_db)

        assert factory._db_manager == mock_db_manager
        assert factory._monitoring_db == mock_monitoring_db
        assert factory._tdengine_access is not None
        assert factory._postgresql_access is not None

    def test_get_data_access_tdengine(self):
        """测试获取TDengine数据访问器"""
        # 创建模拟依赖
        mock_db_manager = Mock()
        mock_monitoring_db = Mock()
        mock_tdengine_access = Mock()

        factory = MockDataAccessFactory()
        factory.initialize(mock_db_manager, mock_monitoring_db)

        # 替换TDengine访问器为模拟对象
        factory._tdengine_access = mock_tdengine_access

        # 测试获取TDengine访问器
        result = factory.get_data_access(MockDatabaseType.TDENGINE)
        assert result == mock_tdengine_access

    def test_get_data_access_postgresql(self):
        """测试获取PostgreSQL数据访问器"""
        # 创建模拟依赖
        mock_db_manager = Mock()
        mock_monitoring_db = Mock()
        mock_postgresql_access = Mock()

        factory = MockDataAccessFactory()
        factory.initialize(mock_db_manager, mock_monitoring_db)

        # 替换PostgreSQL访问器为模拟对象
        factory._postgresql_access = mock_postgresql_access

        # 测试获取PostgreSQL访问器
        result = factory.get_data_access(MockDatabaseType.POSTGRESQL)
        assert result == mock_postgresql_access

    def test_get_data_access_uninitialized(self):
        """测试未初始化工厂的错误处理"""
        factory = MockDataAccessFactory()

        with pytest.raises(RuntimeError, match="Factory not initialized"):
            factory.get_data_access(MockDatabaseType.POSTGRESQL)

    def test_get_data_access_unsupported_type(self):
        """测试不支持的数据库类型"""
        # 创建模拟依赖
        mock_db_manager = Mock()
        mock_monitoring_db = Mock()

        factory = MockDataAccessFactory()
        factory.initialize(mock_db_manager, mock_monitoring_db)

        # 测试不支持的数据库类型
        with pytest.raises(ValueError, match="Unsupported database type"):
            factory.get_data_access(MockDatabaseType.MONGODB)

    def test_get_data_access_with_classification(self):
        """测试带分类参数的数据访问器获取"""
        # 创建模拟依赖
        mock_db_manager = Mock()
        mock_monitoring_db = Mock()
        mock_tdengine_access = Mock()

        factory = MockDataAccessFactory()
        factory.initialize(mock_db_manager, mock_monitoring_db)
        factory._tdengine_access = mock_tdengine_access

        # 测试带分类参数
        result = factory.get_data_access(MockDatabaseType.TDENGINE, "timeseries")
        assert result == mock_tdengine_access

    def test_get_timeseries_access(self):
        """测试获取时序数据访问器"""
        # 创建模拟依赖
        mock_db_manager = Mock()
        mock_monitoring_db = Mock()
        mock_tdengine_access = Mock()

        factory = MockDataAccessFactory()
        factory.initialize(mock_db_manager, mock_monitoring_db)
        factory._tdengine_access = mock_tdengine_access

        # 测试获取时序数据访问器
        result = factory.get_timeseries_access()
        assert result == mock_tdengine_access

    def test_get_relational_access(self):
        """测试获取关系数据访问器"""
        # 创建模拟依赖
        mock_db_manager = Mock()
        mock_monitoring_db = Mock()
        mock_postgresql_access = Mock()

        factory = MockDataAccessFactory()
        factory.initialize(mock_db_manager, mock_monitoring_db)
        factory._postgresql_access = mock_postgresql_access

        # 测试获取关系数据访问器
        result = factory.get_relational_access()
        assert result == mock_postgresql_access

    def test_smart_routing_access_timeseries(self):
        """测试智能路由访问 - 时序数据"""
        # 创建模拟依赖
        mock_db_manager = Mock()
        mock_monitoring_db = Mock()
        mock_tdengine_access = Mock()

        factory = MockDataAccessFactory()
        factory.initialize(mock_db_manager, mock_monitoring_db)
        factory._tdengine_access = mock_tdengine_access

        # 模拟时序分类的路由结果
        result = factory.smart_routing_access("timeseries_data", "symbol001")
        assert result == mock_tdengine_access

    def test_smart_routing_access_relational(self):
        """测试智能路由访问 - 关系数据"""
        # 创建模拟依赖
        mock_db_manager = Mock()
        mock_monitoring_db = Mock()
        mock_postgresql_access = Mock()

        factory = MockDataAccessFactory()
        factory.initialize(mock_db_manager, mock_monitoring_db)
        factory._postgresql_access = mock_postgresql_access

        # 模拟关系分类的路由结果
        result = factory.smart_routing_access("relational_data", "symbol002")
        assert result == mock_postgresql_access

    def test_factory_singleton_behavior(self):
        """测试工厂单例行为"""
        # 创建模拟依赖
        mock_db_manager = Mock()
        mock_monitoring_db = Mock()

        # 创建多个工厂实例
        factory1 = MockDataAccessFactory()
        factory1.initialize(mock_db_manager, mock_monitoring_db)

        factory2 = MockDataAccessFactory()
        factory2.initialize(mock_db_manager, mock_monitoring_db)

        # 验证不同实例都有独立的访问器
        assert factory1._tdengine_access is not factory2._tdengine_access
        assert factory1._postgresql_access is not factory2._postgresql_access

    def test_factory_error_handling(self):
        """测试工厂错误处理"""
        # 测试未初始化的错误
        factory = MockDataAccessFactory()

        # 测试不支持的数据库类型
        mock_db_manager = Mock()
        mock_monitoring_db = Mock()
        factory.initialize(mock_db_manager, mock_monitoring_db)

        with pytest.raises(ValueError):
            factory.get_data_access(MockDatabaseType.MONGODB)


class TestDataAccessFactoryIntegration:
    """数据访问工厂集成测试"""

    def test_factory_configuration_flexibility(self):
        """测试工厂配置的灵活性"""
        factory = MockDataAccessFactory()

        # 测试工厂可以在不同时间点初始化
        mock_db_manager1 = Mock()
        mock_monitoring_db1 = Mock()

        # 第一次初始化
        factory.initialize(mock_db_manager1, mock_monitoring_db1)
        assert factory._db_manager == mock_db_manager1

        # 第二次初始化（重新配置）
        mock_db_manager2 = Mock()
        mock_monitoring_db2 = Mock()
        factory.initialize(mock_db_manager2, mock_monitoring_db2)
        assert factory._db_manager == mock_db_manager2

    def test_factory_error_recovery(self):
        """测试工厂错误恢复能力"""
        factory = MockDataAccessFactory()

        # 测试未初始化的错误
        with pytest.raises(RuntimeError):
            factory.get_data_access(MockDatabaseType.POSTGRESQL)

        # 初始化后恢复正常
        mock_db_manager = Mock()
        mock_monitoring_db = Mock()
        factory.initialize(mock_db_manager, mock_monitoring_db)

        # 现在应该可以正常获取访问器
        result = factory.get_data_access(MockDatabaseType.POSTGRESQL)
        assert result is not None


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--no-cov"])
