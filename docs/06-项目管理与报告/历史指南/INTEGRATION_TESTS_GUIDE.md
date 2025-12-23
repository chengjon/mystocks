# 集成测试指南

> **创建日期**: 2025-11-21
> **版本**: 1.0.0
> **覆盖范围**: Phase 3 数据源架构集成测试

---

## 概述

本指南介绍MyStocks项目的集成测试体系，专注于验证Phase 3三层数据源架构的集成功能。

---

## 集成测试文件

### 1. test_datasource_switching.py

**目的**: 验证Mock ↔ Real数据源切换功能

**测试场景**:
- ✅ 时序数据源: mock ↔ tdengine切换
- ✅ 关系数据源: mock ↔ postgresql切换
- ✅ 业务数据源: mock ↔ composite切换
- ✅ 所有数据源Mock模式
- ✅ 所有数据源Real模式
- ✅ 混合模式 (部分Mock, 部分Real)

**运行方式**:
```bash
# 运行所有切换测试
pytest tests/integration/test_datasource_switching.py -v -s

# 运行单个测试
pytest tests/integration/test_datasource_switching.py::TestDataSourceSwitching::test_all_sources_mock_mode -v -s
```

**测试结果示例**:
```
✅ 时序数据源切换测试通过
   Mock健康状态: mock
   Real健康状态: healthy

✅ 关系数据源切换测试通过
   Mock健康状态: mock
   Real健康状态: healthy

✅ 业务数据源切换测试通过
   Mock健康状态: mock
   Real健康状态: healthy
```

---

### 2. test_three_layer_integration.py

**目的**: 验证TDengine + PostgreSQL + Composite三层协同工作

**测试场景**:
- ✅ Layer 1 (TDengine): 时序数据查询
- ✅ Layer 2 (PostgreSQL): 关系数据查询
- ✅ Layer 3 (Composite): 整合时序+关系数据
- ✅ 跨层数据流动
- ✅ 并行查询优化
- ✅ 错误传播处理
- ✅ 所有层健康检查

**运行方式**:
```bash
# 运行所有三层集成测试
pytest tests/integration/test_three_layer_integration.py -v -s

# 运行单个测试
pytest tests/integration/test_three_layer_integration.py::TestThreeLayerIntegration::test_all_layers_health_check -v -s
```

**测试结果示例**:
```
✅ 三层健康检查汇总:
   Layer 1 (TDengine):   healthy  - 3.3.6.13
   Layer 2 (PostgreSQL): healthy  - 17.6
   Layer 3 (Composite):  healthy
```

---

## 三层架构说明

### 架构图

```
┌─────────────────────────────────────────────────────────┐
│            业务层 (Layer 3)                              │
│   CompositeBusinessDataSource (11个业务方法)             │
│   - 仪表盘汇总、板块表现、策略回测、风险管理、交易分析      │
└──────────────┬────────────────────┬────────────────────┘
               │                    │
    ┌──────────▼─────────┐  ┌──────▼──────────┐
    │  时序层 (Layer 1)   │  │ 关系层 (Layer 2) │
    │  TDengine          │  │ PostgreSQL       │
    │  11个方法          │  │ 23个方法         │
    └────────────────────┘  └─────────────────┘
```

### 数据流向

1. **Layer 1 (TDengine)**:
   - 高频时序数据 (tick, 分钟K线)
   - 实时行情数据
   - 技术指标计算

2. **Layer 2 (PostgreSQL)**:
   - 用户配置数据 (自选股、策略、偏好)
   - 股票基础信息 (名称、行业、概念)
   - 风险预警配置

3. **Layer 3 (Composite)**:
   - 整合Layer 1 + Layer 2数据
   - 业务逻辑封装
   - 并行查询优化

---

## 环境变量配置

### Mock模式 (开发/测试)

```bash
export TIMESERIES_DATA_SOURCE=mock
export RELATIONAL_DATA_SOURCE=mock
export BUSINESS_DATA_SOURCE=mock
```

### Real模式 (生产)

```bash
export TIMESERIES_DATA_SOURCE=tdengine
export RELATIONAL_DATA_SOURCE=postgresql
export BUSINESS_DATA_SOURCE=composite
```

### 混合模式 (调试)

```bash
# 时序使用Mock, 关系使用Real
export TIMESERIES_DATA_SOURCE=mock
export RELATIONAL_DATA_SOURCE=postgresql
export BUSINESS_DATA_SOURCE=mock
```

---

## 运行所有集成测试

```bash
# 运行所有集成测试
pytest tests/integration/ -v -s

# 运行特定测试文件
pytest tests/integration/test_datasource_switching.py -v -s
pytest tests/integration/test_three_layer_integration.py -v -s

# 运行并生成覆盖率报告
pytest tests/integration/ --cov=src/data_sources --cov-report=html -v
```

---

## 测试验证结果

### 测试统计 (2025-11-21)

| 测试文件 | 测试场景 | 通过 | 失败 | 状态 |
|---------|---------|------|------|------|
| **test_datasource_switching.py** | 6 | 6 | 0 | ✅ 全部通过 |
| **test_three_layer_integration.py** | 7 | 7 | 0 | ✅ 全部通过 |
| **总计** | **13** | **13** | **0** | **100%** |

### 验证的功能点

✅ **数据源切换**:
- Mock ↔ TDengine时序数据源切换
- Mock ↔ PostgreSQL关系数据源切换
- Mock ↔ Composite业务数据源切换
- 全Mock模式
- 全Real模式
- 混合模式

✅ **三层集成**:
- TDengine时序数据查询
- PostgreSQL关系数据查询
- Composite业务数据整合
- 跨层数据流动
- 并行查询优化
- 错误传播处理
- 健康检查汇总

---

## 故障排查

### 常见问题

**问题1**: 测试报告"数据库连接失败"

**解决方案**:
```bash
# 检查TDengine连接
python -c "from src.data_access import TDengineDataAccess; td = TDengineDataAccess(); print('TDengine连接正常')"

# 检查PostgreSQL连接
python -c "from src.data_access import PostgreSQLDataAccess; pg = PostgreSQLDataAccess(); print('PostgreSQL连接正常')"
```

**问题2**: 测试超时

**解决方案**:
- 增加pytest超时时间: `pytest --timeout=120`
- 检查数据库是否响应缓慢
- 确认网络连接正常

**问题3**: ImportError

**解决方案**:
```bash
# 确认项目根目录在Python路径中
export PYTHONPATH=/opt/claude/mystocks_spec:$PYTHONPATH

# 或在测试文件中添加:
import sys
sys.path.insert(0, '/opt/claude/mystocks_spec')
```

---

## 下一步测试计划

### 待添加的集成测试

1. **数据一致性测试**:
   - TDengine与PostgreSQL数据一致性验证
   - 双写一致性测试
   - 数据同步延迟测试

2. **事务完整性测试**:
   - PostgreSQL事务commit/rollback测试
   - 跨数据源事务一致性
   - 事务隔离级别验证

3. **性能基准测试**:
   - 单层查询性能
   - 三层集成查询性能
   - 并行查询vs串行查询对比
   - 连接池性能测试

4. **压力测试**:
   - 高并发查询测试
   - 连接池耗尽测试
   - 数据库故障恢复测试

5. **API端到端测试**:
   - FastAPI端点集成测试
   - WebSocket实时推送测试
   - 前后端数据对接测试

---

## 最佳实践

1. **环境隔离**: 使用不同的环境变量配置开发/测试/生产环境
2. **测试数据**: 使用Mock数据源避免污染生产数据
3. **并行测试**: 使用pytest-xdist加速测试执行
4. **持续集成**: 在CI/CD流程中自动运行集成测试
5. **覆盖率监控**: 定期检查测试覆盖率，目标80%+

---

## 参考文档

- [Phase 3完成报告](../architecture/Phase3_完成报告.md)
- [Phase 3验证总结](../architecture/Phase3_验证总结.md)
- [TDengine Schema设计](../architecture/TDengine_Schema_Design.md)
- [PostgreSQL Schema设计](../architecture/PostgreSQL_Schema_Design.md)

---

**文档维护**: 每次添加新的集成测试后更新本文档
**最后更新**: 2025-11-21
**维护人**: Claude Code
