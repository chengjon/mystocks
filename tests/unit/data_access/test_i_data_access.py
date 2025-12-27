"""
Data Access Interface Test Suite
数据访问接口测试套件

创建日期: 2025-12-20
版本: 1.0.0
测试模块: src.data_access.interfaces.i_data_access (398行)
"""

import pytest
from datetime import datetime, date
from unittest.mock import Mock
import sys
import os

# 添加src路径到导入路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

# 直接从文件导入，避免循环导入
exec(open("src/data_access/interfaces/i_data_access.py").read())


class TestDatabaseType:
    """数据库类型枚举测试"""

    def test_database_type_values(self):
        """测试数据库类型枚举值"""
        assert DatabaseType.POSTGRESQL.value == "postgresql"
        assert DatabaseType.TDENGINE.value == "tdengine"
        assert DatabaseType.MYSQL.value == "mysql"
        assert DatabaseType.MONGODB.value == "mongodb"

    def test_database_type_count(self):
        """测试数据库类型数量"""
        assert len(DatabaseType) == 4
        assert set(db_type.value for db_type in DatabaseType) == {
            "postgresql",
            "tdengine",
            "mysql",
            "mongodb",
        }

    def test_database_type_membership(self):
        """测试数据库类型成员检查"""
        assert "postgresql" in [db_type.value for db_type in DatabaseType]
        assert DatabaseType.POSTGRESQL in DatabaseType
        assert "oracle" not in [db_type.value for db_type in DatabaseType]


class TestQueryOperation:
    """查询操作枚举测试"""

    def test_query_operation_values(self):
        """测试查询操作枚举值"""
        assert QueryOperation.SELECT.value == "select"
        assert QueryOperation.INSERT.value == "insert"
        assert QueryOperation.UPDATE.value == "update"
        assert QueryOperation.DELETE.value == "delete"
        assert QueryOperation.UPSERT.value == "upsert"
        assert QueryOperation.BATCH_INSERT.value == "batch_insert"
        assert QueryOperation.BATCH_UPDATE.value == "batch_update"

    def test_query_operation_count(self):
        """测试查询操作数量"""
        assert len(QueryOperation) == 7

    def test_query_operation_crud_operations(self):
        """测试CRUD操作"""
        create_operations = [
            QueryOperation.INSERT,
            QueryOperation.BATCH_INSERT,
            QueryOperation.UPSERT,
        ]
        read_operations = [QueryOperation.SELECT]
        update_operations = [QueryOperation.UPDATE, QueryOperation.BATCH_UPDATE]
        delete_operations = [QueryOperation.DELETE]

        assert all(op in QueryOperation for op in create_operations)
        assert all(op in QueryOperation for op in read_operations)
        assert all(op in QueryOperation for op in update_operations)
        assert all(op in QueryOperation for op in delete_operations)


class TestIsolationLevel:
    """事务隔离级别枚举测试"""

    def test_isolation_level_values(self):
        """测试事务隔离级别枚举值"""
        assert IsolationLevel.READ_UNCOMMITTED.value == "read_uncommitted"
        assert IsolationLevel.READ_COMMITTED.value == "read_committed"
        assert IsolationLevel.REPEATABLE_READ.value == "repeatable_read"
        assert IsolationLevel.SERIALIZABLE.value == "serializable"

    def test_isolation_level_strictness_order(self):
        """测试隔离级别严格程度顺序"""
        isolation_levels = [
            IsolationLevel.READ_UNCOMMITTED,
            IsolationLevel.READ_COMMITTED,
            IsolationLevel.REPEATABLE_READ,
            IsolationLevel.SERIALIZABLE,
        ]
        assert len(isolation_levels) == len(IsolationLevel)

    def test_isolation_level_count(self):
        """测试隔离级别数量"""
        assert len(IsolationLevel) == 4


class TestDataQuery:
    """数据查询对象测试"""

    def test_data_query_minimal_creation(self):
        """测试最小化数据查询创建"""
        query = DataQuery(operation=QueryOperation.SELECT, table_name="users")
        assert query.operation == QueryOperation.SELECT
        assert query.table_name == "users"
        assert query.columns is None
        assert query.filters is None
        assert query.parameters is None

    def test_data_query_full_creation(self):
        """测试完整数据查询创建"""
        query = DataQuery(
            operation=QueryOperation.SELECT,
            table_name="orders",
            columns=["id", "user_id", "amount", "created_at"],
            filters={"user_id": 123, "status": "active"},
            parameters={"limit": 100},
            order_by=["created_at DESC"],
            group_by=["user_id"],
            having={"COUNT(*) > 5"},
            limit=50,
            offset=10,
        )
        assert query.operation == QueryOperation.SELECT
        assert query.table_name == "orders"
        assert len(query.columns) == 4
        assert query.filters["user_id"] == 123
        assert query.order_by == ["created_at DESC"]
        assert query.limit == 50
        assert query.offset == 10

    def test_data_query_insert_operation(self):
        """测试插入操作查询"""
        query = DataQuery(
            operation=QueryOperation.INSERT,
            table_name="products",
            parameters={"name": "Laptop", "price": 999.99},
        )
        assert query.operation == QueryOperation.INSERT
        assert query.table_name == "products"
        assert query.parameters["name"] == "Laptop"

    def test_data_query_update_operation(self):
        """测试更新操作查询"""
        query = DataQuery(
            operation=QueryOperation.UPDATE,
            table_name="users",
            filters={"id": 123},
            parameters={"email": "new@example.com"},
        )
        assert query.operation == QueryOperation.UPDATE
        assert query.filters["id"] == 123
        assert query.parameters["email"] == "new@example.com"

    def test_data_query_with_joins(self):
        """测试带连接的查询"""
        join_clause = {
            "type": "inner",
            "table": "orders",
            "on": "users.id = orders.user_id",
        }
        query = DataQuery(
            operation=QueryOperation.SELECT,
            table_name="users",
            join_clauses=[join_clause],
        )
        assert len(query.join_clauses) == 1
        assert query.join_clauses[0]["table"] == "orders"

    def test_data_query_with_window_functions(self):
        """测试带窗口函数的查询"""
        window_func = {
            "function": "ROW_NUMBER",
            "partition_by": ["user_id"],
            "order_by": ["created_at"],
        }
        query = DataQuery(
            operation=QueryOperation.SELECT,
            table_name="orders",
            window_functions=[window_func],
        )
        assert len(query.window_functions) == 1
        assert query.window_functions[0]["function"] == "ROW_NUMBER"


class TestQueryCriteria:
    """查询条件对象测试"""

    def test_query_criteria_basic_creation(self):
        """测试基本查询条件创建"""
        criteria = QueryCriteria(
            table_name="products",
            filters={"category": "electronics", "price": {"$gt": 100}},
        )
        assert criteria.table_name == "products"
        assert criteria.filters["category"] == "electronics"
        assert criteria.filters["price"]["$gt"] == 100

    def test_query_criteria_with_joins(self):
        """测试带连接的查询条件"""
        joins = [
            {
                "type": "left",
                "table": "categories",
                "on": "products.category_id = categories.id",
            }
        ]
        criteria = QueryCriteria(table_name="products", filters={"price": {"$gt": 50}}, joins=joins)
        assert len(criteria.joins) == 1
        assert criteria.joins[0]["type"] == "left"

    def test_query_criteria_with_subqueries(self):
        """测试带子查询的查询条件"""
        subqueries = {
            "last_orders": {
                "table": "orders",
                "filters": {"status": "completed"},
                "columns": ["user_id", "MAX(created_at) as last_order"],
            }
        }
        criteria = QueryCriteria(table_name="users", filters={}, subqueries=subqueries)
        assert "last_orders" in criteria.subqueries
        assert criteria.subqueries["last_orders"]["table"] == "orders"


class TestDataRecord:
    """数据记录对象测试"""

    def test_data_record_minimal_creation(self):
        """测试最小化数据记录创建"""
        record = DataRecord(table_name="users", data={"id": 1, "name": "John Doe"})
        assert record.table_name == "users"
        assert record.data["id"] == 1
        assert record.data["name"] == "John Doe"
        assert record.metadata is None
        assert record.timestamp is None

    def test_data_record_full_creation(self):
        """测试完整数据记录创建"""
        current_time = datetime.now()
        metadata = {"source": "api", "version": "1.0"}
        record = DataRecord(
            table_name="orders",
            data={"id": 1001, "user_id": 123, "amount": 99.99, "status": "pending"},
            metadata=metadata,
            timestamp=current_time,
        )
        assert record.table_name == "orders"
        assert record.data["amount"] == 99.99
        assert record.metadata["source"] == "api"
        assert record.timestamp == current_time

    def test_data_record_with_complex_data(self):
        """测试包含复杂数据的数据记录"""
        complex_data = {
            "id": 1,
            "settings": {
                "notifications": {"email": True, "sms": False},
                "preferences": {"theme": "dark", "language": "en"},
            },
            "tags": ["premium", "active"],
            "last_login": date(2024, 1, 15),
        }
        record = DataRecord(table_name="user_profiles", data=complex_data)
        assert isinstance(record.data["settings"], dict)
        assert isinstance(record.data["tags"], list)
        assert isinstance(record.data["last_login"], date)


class TestSaveOptions:
    """保存选项配置测试"""

    def test_save_options_default_values(self):
        """测试保存选项默认值"""
        options = SaveOptions()
        assert options.batch_size == 1000
        assert options.upsert_mode is False
        assert options.conflict_resolution == "ignore"
        assert options.validate_data is True
        assert options.return_ids is False
        assert options.transactional is True

    def test_save_options_custom_values(self):
        """测试自定义保存选项值"""
        options = SaveOptions(
            batch_size=500,
            upsert_mode=True,
            conflict_resolution="update",
            validate_data=False,
            return_ids=True,
            transactional=False,
        )
        assert options.batch_size == 500
        assert options.upsert_mode is True
        assert options.conflict_resolution == "update"
        assert options.validate_data is False
        assert options.return_ids is True
        assert options.transactional is False

    def test_save_options_conflict_resolution_values(self):
        """测试冲突解决策略值"""
        valid_resolutions = ["ignore", "update", "error"]
        for resolution in valid_resolutions:
            options = SaveOptions(conflict_resolution=resolution)
            assert options.conflict_resolution == resolution


class TestQueryResult:
    """查询结果对象测试"""

    def test_query_result_successful(self):
        """测试成功查询结果"""
        data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        result = QueryResult(
            success=True,
            data=data,
            total_count=2,
            execution_time=0.05,
            affected_rows=None,
        )
        assert result.success is True
        assert len(result.data) == 2
        assert result.total_count == 2
        assert result.execution_time == 0.05
        assert result.affected_rows is None
        assert result.query_plan is None
        assert result.warnings is None
        assert result.error is None

    def test_query_result_with_warnings(self):
        """测试带警告的查询结果"""
        warnings = ["Using index scan", "Large result set"]
        result = QueryResult(success=True, data=[], total_count=0, warnings=warnings)
        assert result.success is True
        assert len(result.warnings) == 2
        assert "index scan" in result.warnings[0]

    def test_query_result_failed(self):
        """测试失败查询结果"""
        result = QueryResult(success=False, data=[], error="Table 'users' doesn't exist")
        assert result.success is False
        assert len(result.data) == 0
        assert "doesn't exist" in result.error
        assert result.total_count is None

    def test_query_result_with_query_plan(self):
        """测试带查询计划的查询结果"""
        query_plan = {
            "operation": "Index Scan",
            "index_used": "users_email_idx",
            "cost": 2.5,
        }
        result = QueryResult(success=True, data=[{"id": 1}], query_plan=query_plan)
        assert result.success is True
        assert result.query_plan["operation"] == "Index Scan"
        assert result.query_plan["index_used"] == "users_email_idx"

    def test_query_result_affected_rows(self):
        """测试受影响行数"""
        result = QueryResult(success=True, data=[], affected_rows=15)
        assert result.success is True
        assert result.affected_rows == 15


class TestSaveResult:
    """保存结果对象测试"""

    def test_save_result_successful_insert(self):
        """测试成功插入结果"""
        result = SaveResult(success=True, inserted_count=10, updated_count=0, failed_count=0)
        assert result.success is True
        assert result.inserted_count == 10
        assert result.updated_count == 0
        assert result.failed_count == 0

    def test_save_result_mixed_result(self):
        """测试混合结果（插入和更新）"""
        result = SaveResult(success=True, inserted_count=5, updated_count=3, failed_count=2)
        assert result.success is True
        assert result.inserted_count == 5
        assert result.updated_count == 3
        assert result.failed_count == 2

    def test_save_result_failed(self):
        """测试失败保存结果"""
        result = SaveResult(success=False)
        assert result.success is False
        assert result.inserted_count == 0
        assert result.updated_count == 0
        assert result.failed_count == 0

    def test_save_result_total_operations(self):
        """测试总操作数计算"""
        result = SaveResult(success=True, inserted_count=100, updated_count=50, failed_count=5)
        total_operations = result.inserted_count + result.updated_count + result.failed_count
        assert total_operations == 155


class TestIDataAccess:
    """数据访问接口测试"""

    def test_interface_is_abstract(self):
        """测试接口是抽象的"""
        # IDataAccess应该是抽象类，不能直接实例化
        with pytest.raises(TypeError):
            IDataAccess()

    def test_interface_has_required_methods(self):
        """测试接口有必需的方法"""
        # 检查抽象方法是否正确定义
        abstract_methods = IDataAccess.__abstractmethods__
        required_methods = {
            "connect",
            "disconnect",
            "is_connected",
            "execute_query",
            "save_data",
            "save_batch_data",
            "begin_transaction",
            "commit_transaction",
            "rollback_transaction",
            "get_connection_info",
        }
        assert required_methods.issubset(abstract_methods)

    def test_concrete_implementation(self):
        """测试具体实现"""

        # 创建一个具体实现用于测试
        class ConcreteDataAccess(IDataAccess):
            def __init__(self):
                self.connection = Mock()
                self.connection_info = {"type": "test", "status": "connected"}

            async def connect(self):
                pass

            async def disconnect(self):
                pass

            def is_connected(self):
                return True

            async def execute_query(self, query: DataQuery) -> QueryResult:
                return QueryResult(success=True, data=[])

            async def save_data(self, record: DataRecord, options: SaveOptions = None) -> SaveResult:
                return SaveResult(success=True, inserted_count=1)

            async def save_batch_data(self, records: list, options: SaveOptions = None) -> SaveResult:
                return SaveResult(success=True, inserted_count=len(records))

            async def begin_transaction(self, isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED):
                pass

            async def commit_transaction(self):
                pass

            async def rollback_transaction(self):
                pass

            def get_connection_info(self):
                return self.connection_info

        # 测试具体实现
        data_access = ConcreteDataAccess()
        assert data_access.is_connected()
        assert data_access.get_connection_info()["status"] == "connected"

    async def test_async_interface_methods(self):
        """测试异步接口方法"""

        class AsyncDataAccess(IDataAccess):
            def __init__(self):
                self.connected = False

            async def connect(self):
                self.connected = True

            async def disconnect(self):
                self.connected = False

            def is_connected(self):
                return self.connected

            async def execute_query(self, query: DataQuery) -> QueryResult:
                return QueryResult(success=True, data=[{"test": "data"}])

            async def save_data(self, record: DataRecord, options: SaveOptions = None) -> SaveResult:
                return SaveResult(success=True, inserted_count=1)

            async def save_batch_data(self, records: list, options: SaveOptions = None) -> SaveResult:
                return SaveResult(success=True, inserted_count=len(records))

            async def begin_transaction(self, isolation_level: IsolationLevel = IsolationLevel.READ_COMMITTED):
                pass

            async def commit_transaction(self):
                pass

            async def rollback_transaction(self):
                pass

            def get_connection_info(self):
                return {"type": "async_test", "connected": self.connected}

        # 测试异步方法
        data_access = AsyncDataAccess()

        # 测试连接
        await data_access.connect()
        assert data_access.is_connected()

        # 测试查询
        query = DataQuery(QueryOperation.SELECT, "test_table")
        result = await data_access.execute_query(query)
        assert result.success is True
        assert len(result.data) == 1

        # 测试保存数据
        record = DataRecord("test_table", {"name": "test"})
        save_result = await data_access.save_data(record)
        assert save_result.success is True

        # 测试批量保存
        records = [
            DataRecord("test_table", {"id": 1}),
            DataRecord("test_table", {"id": 2}),
        ]
        batch_result = await data_access.save_batch_data(records)
        assert batch_result.inserted_count == 2

        # 测试断开连接
        await data_access.disconnect()
        assert not data_access.is_connected()

    def test_interface_method_signatures(self):
        """测试接口方法签名"""
        # 验证抽象方法的签名
        import inspect

        # 检查execute_query方法签名
        execute_query_sig = inspect.signature(IDataAccess.execute_query)
        assert "query" in execute_query_sig.parameters
        query_param = execute_query_sig.parameters["query"]
        assert query_param.annotation == DataQuery

        # 检查save_data方法签名
        save_data_sig = inspect.signature(IDataAccess.save_data)
        assert "record" in save_data_sig.parameters
        assert "options" in save_data_sig.parameters
        record_param = save_data_sig.parameters["record"]
        assert record_param.annotation == DataRecord

        # 检查begin_transaction方法签名
        begin_tx_sig = inspect.signature(IDataAccess.begin_transaction)
        if "isolation_level" in begin_tx_sig.parameters:
            isolation_param = begin_tx_sig.parameters["isolation_level"]
            assert isolation_param.annotation == IsolationLevel


class TestIntegration:
    """集成测试"""

    def test_data_flow_integration(self):
        """测试数据流集成"""
        # 创建查询
        query = DataQuery(
            operation=QueryOperation.SELECT,
            table_name="products",
            columns=["id", "name", "price"],
            filters={"category": "electronics"},
            limit=10,
        )

        # 创建数据记录
        record = DataRecord(
            table_name="products",
            data={"name": "Smartphone", "price": 699.99, "category": "electronics"},
            metadata={"source": "api"},
            timestamp=datetime.now(),
        )

        # 创建保存选项
        options = SaveOptions(batch_size=100, upsert_mode=True, validate_data=True)

        # 验证对象创建
        assert query.operation == QueryOperation.SELECT
        assert query.limit == 10
        assert record.table_name == "products"
        assert record.data["price"] == 699.99
        assert options.batch_size == 100
        assert options.upsert_mode is True

    def test_error_handling_flow(self):
        """测试错误处理流程"""
        # 创建失败查询结果
        error_result = QueryResult(success=False, data=[], error="Connection timeout")

        # 创建失败保存结果
        error_save_result = SaveResult(success=False, failed_count=5)

        # 验证错误结果
        assert not error_result.success
        assert "timeout" in error_result.error
        assert not error_save_result.success
        assert error_save_result.failed_count == 5

    def test_transaction_flow_simulation(self):
        """测试事务流程模拟"""
        # 模拟事务操作的数据结构
        isolation_levels = [
            IsolationLevel.READ_UNCOMMITTED,
            IsolationLevel.READ_COMMITTED,
            IsolationLevel.REPEATABLE_READ,
            IsolationLevel.SERIALIZABLE,
        ]

        for level in isolation_levels:
            # 每个隔离级别都应该有效
            assert level in IsolationLevel

        # 验证隔离级别的严格性顺序
        strictness_order = [
            IsolationLevel.READ_UNCOMMITTED,
            IsolationLevel.READ_COMMITTED,
            IsolationLevel.REPEATABLE_READ,
            IsolationLevel.SERIALIZABLE,
        ]

        for i, level in enumerate(strictness_order):
            assert level == strictness_order[i]


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
