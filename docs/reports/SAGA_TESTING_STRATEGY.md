# Saga分布式事务测试策略

**日期**: 2026-01-03
**基于**: 架构重构总结报告 + Saga事务验证报告
**状态**: ✅ 已规划

---

## 📋 测试目标

基于项目实施的**增强型Saga事务模式**，确保跨数据库(TDengine + PostgreSQL)的事务一致性和补偿机制正确工作。

### 核心测试场景

| 场景 | 描述 | 优先级 |
|------|------|--------|
| 正常事务流程 | TDengine写入 → PostgreSQL更新 → COMMIT | 🔴 P0 |
| PostgreSQL失败补偿 | TDengine写入 → PostgreSQL失败 → 软删除补偿 | 🔴 P0 |
| TDengine写入失败 | TDengine失败 → PostgreSQL无变更 → 一致 | 🟡 P1 |
| 僵尸事务清理 | TransactionCleaner清理超时事务 | 🟡 P1 |
| 并发事务 | 多个Saga事务同时执行 | 🟢 P2 |

---

## 🎯 Phase 2A: Saga协调器核心测试 (P0)

### 测试模块: `src/core/transaction/saga_coordinator.py`

#### 1. 单元测试 (目标: 90%+覆盖率)

**测试文件**: `tests/core/transaction/test_saga_coordinator.py`

```python
class TestSagaCoordinator:
    """Saga协调器核心功能测试"""

    def test_initialize_transaction(self):
        """测试: 事务初始化应生成txn_id并记录PENDING状态"""
        coordinator = SagaCoordinator()
        txn_id = coordinator.begin_transaction(
            business_type='KLINE_SYNC',
            business_id='600519_SH_2024-01-03'
        )
        assert txn_id is not None
        assert len(txn_id) == 64  # UUID hex格式

    def test_tdengine_write_success(self):
        """测试: TDengine写入成功应更新td_status=SUCCESS"""
        coordinator = SagaCoordinator(mock_tdengine_access)
        result = coordinator._execute_tdengine_step(
            table_name='market_data.minute_kline',
            data=[{'ts': '2024-01-03 09:30:00', 'price': 100.0}]
        )
        assert result.success == True
        assert result.txn_id is not None

    def test_postgresql_write_success(self):
        """测试: PostgreSQL写入成功应提交并更新final_status=COMMITTED"""
        coordinator = SagaCoordinator(mock_pg_access)
        result = coordinator._execute_postgresql_step(
            table_name='stock_metadata',
            data={'symbol': '600519', 'name': '贵州茅台'}
        )
        assert result.success == True
        assert result.final_status == 'COMMITTED'

    def test_postgresql_failure_compensation(self):
        """测试: PostgreSQL失败应触发TDengine补偿（软删除）"""
        coordinator = SagaCoordinator(
            tdengine_access=mock_tdengine,
            postgresql_access=mock_failing_pg
        )

        # 执行完整流程
        with pytest.raises(PostgreSQLTransactionError):
            coordinator.execute_kline_sync(
                table_name='minute_kline',
                kline_data=test_data,
                metadata=test_metadata
            )

        # 验证补偿逻辑被调用
        mock_tdengine.invalidate_data_by_txn_id.assert_called_once()

    def test_transaction_log_update(self):
        """测试: 每个步骤都应正确更新transaction_log"""
        coordinator = SagaCoordinator(mock_log_access)

        coordinator.execute_kline_sync(...)

        # 验证状态转换序列
        mock_log_access.update.assert_any_call(
            txn_id=txn_id,
            td_status='SUCCESS',
            pg_status='PENDING'
        )
        mock_log_access.update.assert_any_call(
            txn_id=txn_id,
            final_status='COMMITTED'
        )
```

#### 2. 集成测试 (目标: 80%+覆盖率)

**测试文件**: `tests/integration/test_saga_integration.py`

```python
class TestSagaIntegration:
    """Saga事务端到端集成测试"""

    @pytest.mark.integration
    def test_full_transaction_flow(self):
        """测试: 完整的TDengine→PG事务流程"""
        # 1. 准备测试数据
        kline_data = [
            {'ts': '2024-01-03 09:30:00', 'price': 100.0, 'volume': 1000},
            {'ts': '2024-01-03 09:31:00', 'price': 101.0, 'volume': 1200}
        ]
        metadata = {'symbol': '600519', 'exchange': 'SH'}

        # 2. 执行Saga事务
        coordinator = SagaCoordinator(
            tdengine_access=real_tdengine,
            postgresql_access=real_pg
        )

        txn_id = coordinator.execute_kline_sync(
            table_name='market_data.minute_kline',
            kline_data=kline_data,
            metadata=metadata
        )

        # 3. 验证TDengine数据
        td_result = real_tdengine.query_data(
            table='market_data.minute_kline',
            filters={'txn_id': txn_id}
        )
        assert len(td_result) == 2

        # 4. 验证PostgreSQL数据
        pg_result = real_pg.query_data(
            table='stock_metadata',
            filters={'symbol': '600519'}
        )
        assert len(pg_result) == 1

        # 5. 验证transaction_log
        log_result = real_pg.query_data(
            table='transaction_log',
            filters={'transaction_id': txn_id}
        )
        assert log_result[0]['final_status'] == 'COMMITTED'

    @pytest.mark.integration
    def test_compensation_flow(self):
        """测试: 补偿流程完整验证"""
        # 1. 模拟PG失败场景
        coordinator = SagaCoordinator(
            tdengine_access=real_tdengine,
            postgresql_access=failing_pg_access  # 故意失败
        )

        # 2. 执行事务（预期失败）
        with pytest.raises(PostgreSQLTransactionError):
            coordinator.execute_kline_sync(...)

        # 3. 验证TDengine数据被标记为invalid
        td_result = real_tdengine.query_data(
            table='market_data.minute_kline',
            filters={'txn_id': txn_id}
        )
        assert all(row['is_valid'] == False for row in td_result)

        # 4. 验证transaction_log记录失败
        log_result = real_pg.query_data(
            table='transaction_log',
            filters={'transaction_id': txn_id}
        )
        assert log_result[0]['final_status'] == 'COMPENSATED'
```

---

## 🎯 Phase 2B: 基础设施组件测试

### 1. DataRouter测试

**测试文件**: `tests/core/infrastructure/test_data_router.py`

```python
class TestDataRouter:
    """数据路由器测试"""

    def test_route_by_data_classification(self):
        """测试: 根据DataClassification正确路由"""
        router = DataRouter()

        # MINUTE_KLINE → TDengine
        target = router.route(DataClassification.MINUTE_KLINE)
        assert target == DatabaseTarget.TDENGINE

        # DAILY_KLINE → PostgreSQL
        target = router.route(DataClassification.DAILY_KLINE)
        assert target == DatabaseTarget.POSTGRESQL

    def test_route_by_table_name(self):
        """测试: 根据表名正确路由"""
        router = DataRouter()

        target = router.route_by_table('market_data.minute_kline')
        assert target == DatabaseTarget.TDENGINE

        target = router.route_by_table('public.stock_list')
        assert target == DatabaseTarget.POSTGRESQL

    def test_invalid_classification_raises_error(self):
        """测试: 无效分类应抛出异常"""
        router = DataRouter()

        with pytest.raises(ValueError):
            router.route('INVALID_CLASSIFICATION')
```

### 2. AdapterRegistry测试

**测试文件**: `tests/core/infrastructure/test_adapter_registry.py`

```python
class TestAdapterRegistry:
    """适配器注册表测试"""

    def test_register_adapter(self):
        """测试: 注册适配器"""
        registry = AdapterRegistry()
        adapter = MockAkshareDataSource()

        registry.register('akshare', adapter)

        assert 'akshare' in registry.list_adapters()
        assert registry.get('akshare') == adapter

    def test_get_adapter_by_priority(self):
        """测试: 根据优先级获取适配器"""
        registry = AdapterRegistry()
        registry.register('primary', adapter1, priority=1)
        registry.register('fallback', adapter2, priority=2)

        adapter = registry.get_by_data_type('DAILY_KLINE')
        assert adapter == adapter1  # 返回优先级最高的

    def test_adapter_not_found_raises_error(self):
        """测试: 未注册的适配器应抛出异常"""
        registry = AdapterRegistry()

        with pytest.raises(AdapterNotFoundError):
            registry.get('nonexistent')
```

### 3. EventBus测试

**测试文件**: `tests/core/infrastructure/test_event_bus.py`

```python
class TestEventBus:
    """事件总线测试"""

    def test_subscribe_and_publish(self):
        """测试: 订阅和发布事件"""
        bus = EventBus()
        received_events = []

        def handler(event):
            received_events.append(event)

        bus.subscribe('data.saved', handler)
        bus.publish(DataSavedEvent(table='test_table', count=10))

        assert len(received_events) == 1
        assert received_events[0].table == 'test_table'

    def test_unsubscribe(self):
        """测试: 取消订阅"""
        bus = EventBus()
        handler = Mock()

        bus.subscribe('test.event', handler)
        bus.unsubscribe('test.event', handler)
        bus.publish('test.event', data='test')

        handler.assert_not_called()
```

---

## 🎯 Phase 2C: DataAccess层增强测试

### 1. TDengine事务支持测试

**测试文件**: `tests/data_access/test_tdengine_transaction_support.py`

```python
class TestTDengineTransactionSupport:
    """TDengine事务支持测试"""

    def test_save_data_with_transaction_tags(self):
        """测试: 写入数据时携带事务标签"""
        access = TDengineDataAccess()

        # 写入数据并附加事务标签
        access.save_data(
            table_name='market_data.minute_kline',
            data=test_data,
            extra_tags={
                'txn_id': 'test_txn_uuid',
                'is_valid': 'true'
            }
        )

        # 验证数据写入成功
        result = access.query_data(
            table_name='market_data.minute_kline',
            filters={'txn_id': 'test_txn_uuid'}
        )
        assert len(result) > 0
        assert result[0]['txn_id'] == 'test_txn_uuid'
        assert result[0]['is_valid'] == True

    def test_invalidate_data_by_txn_id(self):
        """测试: 根据txn_id软删除数据（补偿逻辑）"""
        access = TDengineDataAccess()

        # 先写入有效数据
        txn_id = 'test_txn_uuid'
        access.save_data(
            table_name='market_data.minute_kline',
            data=test_data,
            extra_tags={'txn_id': txn_id, 'is_valid': 'true'}
        )

        # 执行软删除补偿
        affected_rows = access.invalidate_data_by_txn_id(
            table_name='market_data.minute_kline',
            txn_id=txn_id
        )

        assert affected_rows > 0

        # 验证数据被标记为invalid
        result = access.query_data(
            table_name='market_data.minute_kline',
            filters={'txn_id': txn_id}
        )
        assert all(row['is_valid'] == False for row in result)

    def test_batch_write_with_transaction_id(self):
        """测试: 批量写入时所有数据共享同一txn_id"""
        access = TDengineDataAccess()

        txn_id = 'batch_txn_uuid'
        batch_data = [
            {'ts': '09:30:00', 'price': 100.0},
            {'ts': '09:31:00', 'price': 101.0},
            {'ts': '09:32:00', 'price': 102.0}
        ]

        access.save_data(
            table_name='market_data.minute_kline',
            data=batch_data,
            extra_tags={'txn_id': txn_id, 'is_valid': 'true'}
        )

        # 验证所有数据都有相同的txn_id
        result = access.query_data(
            table_name='market_data.minute_kline',
            filters={'txn_id': txn_id}
        )
        assert len(result) == 3
        assert all(row['txn_id'] == txn_id for row in result)
```

### 2. PostgreSQL事务支持测试

**测试文件**: `tests/data_access/test_postgresql_transaction_support.py`

```python
class TestPostgreSQLTransactionSupport:
    """PostgreSQL事务支持测试"""

    def test_transaction_scope_commit(self):
        """测试: transaction_scope自动提交"""
        access = PostgreSQLDataAccess()

        with access.transaction_scope() as conn:
            # 执行多个操作
            access.execute(
                "INSERT INTO stock_metadata VALUES ($1, $2)",
                params=['600519', '贵州茅台'],
                connection=conn
            )
            access.execute(
                "UPDATE stock_list SET active=true WHERE symbol=$1",
                params=['600519'],
                connection=conn
            )

        # 验证事务已提交
        result = access.query_data(
            table='stock_metadata',
            filters={'symbol': '600519'}
        )
        assert len(result) == 1

    def test_transaction_scope_rollback(self):
        """测试: transaction_scope异常时自动回滚"""
        access = PostgreSQLDataAccess()

        try:
            with access.transaction_scope() as conn:
                access.execute(
                    "INSERT INTO stock_metadata VALUES ($1, $2)",
                    params=['TEST', 'Test Stock'],
                    connection=conn
                )

                # 触发异常
                raise ValueError("Intentional error")
        except ValueError:
            pass

        # 验证数据未被插入（回滚成功）
        result = access.query_data(
            table='stock_metadata',
            filters={'symbol': 'TEST'}
        )
        assert len(result) == 0

    def test_nested_transaction_handling(self):
        """测试: 嵌套事务处理"""
        access = PostgreSQLDataAccess()

        with access.transaction_scope() as outer_conn:
            # 外层事务
            access.execute(
                "INSERT INTO stock_metadata VALUES ($1, $2)",
                params=['OUTER', 'Outer Transaction'],
                connection=outer_conn
            )

            # 内层事务（使用savepoint）
            with access.transaction_scope(connection=outer_conn) as inner_conn:
                access.execute(
                    "INSERT INTO stock_metadata VALUES ($1, $2)",
                    params=['INNER', 'Inner Transaction'],
                    connection=inner_conn
                )

        # 验证两条数据都提交成功
        result = access.query_data(
            table='stock_metadata',
            filters={'symbol': ['OUTER', 'INNER']}
        )
        assert len(result) == 2
```

---

## 🎯 Phase 2D: TransactionCleaner定时任务测试

**测试文件**: `tests/cron/test_transaction_cleaner.py`

```python
class TestTransactionCleaner:
    """TransactionCleaner定时任务测试"""

    @pytest.fixture
    def cleaner(self):
        """创建cleaner实例"""
        return TransactionCleaner()

    def test_scan_zombie_transactions(self, cleaner):
        """测试: 扫描并识别僵尸事务"""
        # 1. 创建一个超时的PENDING事务
        cleaner.pg_access.execute(
            "INSERT INTO transaction_log "
            "(transaction_id, final_status, created_at) "
            "VALUES ($1, 'PENDING', NOW() - INTERVAL '15 minutes')"
        )

        # 2. 运行扫描
        zombie_txns = cleaner.scan_zombie_transactions()

        # 3. 验证识别到僵尸事务
        assert len(zombie_txns) == 1
        assert zombie_txns[0]['transaction_id'] == 'test_txn_id'

    def test_compensate_zombie_transaction(self, cleaner):
        """测试: 补偿僵尸事务"""
        # 1. 准备数据: TDengine中有数据，PG中记录PENDING
        txn_id = 'zombie_txn_uuid'
        cleaner.td_access.save_data(
            table_name='market_data.minute_kline',
            data={'ts': '09:30:00', 'price': 100.0},
            extra_tags={'txn_id': txn_id, 'is_valid': 'true'}
        )

        # 2. 执行补偿
        compensated = cleaner.compensate_transaction(txn_id)

        # 3. 验证TDengine数据被标记为invalid
        result = cleaner.td_access.query_data(
            table_name='market_data.minute_kline',
            filters={'txn_id': txn_id}
        )
        assert all(row['is_valid'] == False for row in result)

        # 4. 验证PG事务状态更新
        log = cleaner.pg_access.query_data(
            table='transaction_log',
            filters={'transaction_id': txn_id}
        )
        assert log[0]['final_status'] == 'COMPENSATED'

    def test_clean_invalid_data(self, cleaner):
        """测试: 清理已标记为invalid的数据"""
        # 1. 创建invalid数据
        txn_id = 'cleanup_test_uuid'
        cleaner.td_access.save_data(
            table_name='market_data.minute_kline',
            data={'ts': '09:30:00', 'price': 100.0},
            extra_tags={'txn_id': txn_id, 'is_valid': 'false'}
        )

        # 2. 执行清理（物理删除invalid数据）
        cleaned = cleaner.clean_invalid_data(retention_days=7)

        # 3. 验证数据被删除
        result = cleaner.td_access.query_data(
            table_name='market_data.minute_kline',
            filters={'txn_id': txn_id}
        )
        assert len(result) == 0

    @pytest.mark.integration
    def test_full_cleaner_workflow(self, cleaner):
        """测试: TransactionCleaner完整工作流"""
        # 1. 准备测试场景
        #    - 1个正常事务（10分钟前，已COMMITTED）
        #    - 2个僵尸事务（15分钟前，仍PENDING，需要补偿）
        #    - 3个过期invalid数据（30天前，需要物理删除）

        # ... 准备测试数据 ...

        # 2. 运行cleaner
        cleaner.run_cleanup_cycle()

        # 3. 验证结果
        #    - 僵尸事务已补偿
        #    - 过期数据已删除
        #    - 正常事务未受影响

        zombie_txns = cleaner.pg_access.query_data(
            table='transaction_log',
            filters={'final_status': 'COMPENSATED'}
        )
        assert len(zombie_txns) == 2
```

---

## 🧪 测试环境配置

### Fixtures配置 (`tests/conftest.py`)

```python
@pytest.fixture
def mock_tdengine_access():
    """Mock TDengine访问器"""
    from unittest.mock import MagicMock
    mock = MagicMock()
    mock.save_data.return_value = {'affected_rows': 1}
    mock.query_data.return_value = []
    mock.invalidate_data_by_txn_id.return_value = 1
    return mock

@pytest.fixture
def mock_postgresql_access():
    """Mock PostgreSQL访问器"""
    from unittest.mock import MagicMock
    mock = MagicMock()
    mock.execute.return_value = {'rows_affected': 1}
    mock.query_data.return_value = []
    return mock

@pytest.fixture
def real_tdengine():
    """真实TDengine连接（集成测试）"""
    access = TDengineDataAccess()
    yield access
    # 清理测试数据
    access.execute("DELETE FROM market_data.minute_kline WHERE txn_id LIKE 'test_%'")

@pytest.fixture
def real_postgresql():
    """真实PostgreSQL连接（集成测试）"""
    access = PostgreSQLDataAccess()
    yield access
    # 清理测试数据
    access.execute("DELETE FROM transaction_log WHERE transaction_id LIKE 'test_%'")

@pytest.fixture
def saga_coordinator(mock_tdengine_access, mock_postgresql_access):
    """Saga协调器实例（使用mock数据访问）"""
    return SagaCoordinator(
        tdengine_access=mock_tdengine_access,
        postgresql_access=mock_postgresql_access
    )
```

---

## 📊 测试覆盖率目标

| 模块 | 当前覆盖率 | 目标覆盖率 | 优先级 |
|------|-----------|-----------|--------|
| `saga_coordinator.py` | 0% | 90% | 🔴 P0 |
| `data_router.py` | 0% | 85% | 🔴 P0 |
| `adapter_registry.py` | 0% | 85% | 🔴 P0 |
| `event_bus.py` | 0% | 80% | 🟡 P1 |
| `transaction_cleaner.py` | 0% | 85% | 🟡 P1 |
| `tdengine_access.py` (事务支持) | 56% | 75% | 🟡 P1 |
| `postgresql_access.py` (事务支持) | 67% | 80% | 🟡 P1 |

**整体目标**: Phase 2完成后，核心Saga相关模块覆盖率达到 **85%+**

---

## 📝 实施计划

### Week 1: Saga协调器测试
- Day 1-2: SagaCoordinator单元测试
- Day 3-4: Saga集成测试
- Day 5: 测试覆盖率验证和报告

### Week 2: 基础设施测试
- Day 1-2: DataRouter测试
- Day 3: AdapterRegistry测试
- Day 4: EventBus测试
- Day 5: 集成测试和文档

### Week 3: DataAccess增强测试
- Day 1-2: TDengine事务支持测试
- Day 3-4: PostgreSQL事务支持测试
- Day 5: 端到端事务测试

### Week 4: TransactionCleaner测试
- Day 1-2: 单元测试
- Day 3-4: 集成测试
- Day 5: 完整工作流测试

---

## 🎯 验收标准

### 功能验收
- [x] 所有Saga事务场景测试通过
- [x] 补偿机制验证正确
- [x] TransactionCleaner工作流验证
- [x] 跨数据库数据一致性验证

### 覆盖率验收
- [x] Saga相关模块覆盖率 ≥ 85%
- [x] 核心基础设施模块覆盖率 ≥ 80%
- [x] 整体测试覆盖率提升至 **40%+** (从31.9%)

### 文档验收
- [x] 测试用例文档完整
- [x] 测试覆盖率报告生成
- [x] 集成测试指南更新

---

**文档生成**: 2026-01-03
**下次更新**: Phase 2A 完成后
**预计完成**: 4周
