# Phase 2: 测试提升 - 执行计划

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、执行清单或整改建议，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值、时间线和建议动作如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


**日期**: 2026-01-07  
**任务**: 修复现有测试，提升覆盖率到30%  
**预计时间**: 19小时  
**状态**: 🔄 开始执行

---

## 📊 问题概述

### 识别的主要问题

| 问题 | 影响文件 | 失败测试数 | 优先级 |
|------|---------|-----------|--------|
| **TDengineDataAccess API不匹配** | tests/data_access/test_tdengine_access.py | 17个 | P0 |
| **PostgreSQL连接失败** | tests/data_access/test_postgresql_access.py | 13个 | P0 |
| **adapters层mock配置不正确** | tests/adapters/test_akshare_adapter.py | 1个 | P1 |

### 当前测试状态

| 指标 | 数值 |
|------|------|
| **测试文件总数** | ~75个 |
| **测试通过率** | 45.3% (34/75) |
| **测试失败率** | 54.7% (41/75) |
| **测试覆盖率** | 12.81% |

---

## 🎯 Phase 2目标

### 量化目标

| 指标 | 当前值 | 目标值 | 改进 |
|------|-------|--------|------|
| **测试通过率** | 45.3% | 93.3% | +47.9% |
| **测试覆盖率** | 12.81% | 30% | +2.3x |
| **data_access层覆盖率** | 未知 | ≥50% | +50% |
| **adapters层覆盖率** | 未知 | ≥50% | +50% |
| **core层覆盖率** | 未知 | ≥50% | +50% |

---

## 📋 Task 2.1: 修复data_access层测试（优先级P0）

**预计时间**: 8小时（原20小时）  

### Task 2.1.1: 修复TDengineDataAccess API不匹配 (4小时)

**问题**: 测试期望的方法与实际API不匹配

**缺失方法列表**:
- `check_connection()` - 检查连接状态
- `create_stable()` - 创建超表
- `create_table()` - 创建表
- `insert_dataframe()` - 插入DataFrame
- `query_by_time_range()` - 按时间范围查询
- `query_latest()` - 查询最新数据
- `delete_by_time_range()` - 按时间范围删除
- `aggregate_to_kline()` - 聚合到K线
- `get_table_info()` - 获取表信息

**修复策略**:
1. 为TDengineDataAccess添加缺失的方法
2. 适配现有实现（save_data、load_data等）
3. 运行测试验证

### Task 2.1.2: 修复PostgreSQL连接问题 (2小时)

**问题**: PostgreSQL服务未启动或端口配置错误

**错误**:
```python
ConnectionError: PostgreSQL连接失败: connection to server at "localhost" (127.0.0.1), port 5438 failed: Connection refused
```

**修复策略**:
1. 检查PostgreSQL服务状态
2. 更新端口配置或启动服务
3. 使用环境变量配置

**配置检查**:
```bash
# 检查环境变量
echo $POSTGRESQL_HOST
echo $POSTGRESQL_PORT
echo $POSTGRESQL_DATABASE

# 检查服务状态
docker ps | grep postgres
# 或
pg_isready -h localhost -p 5438
```

### Task 2.1.3: 修复其他data_access测试 (2小时)

**文件**: 
- tests/data_access/test_database_connection_manager.py
- tests/unit/data_access/test_postgresql_access.py
- tests/unit/data_access/test_i_data_access.py
- tests/unit/data_access/test_data_access.py

**修复策略**:
- 验证测试通过的文件
- 修复测试失败的文件
- 更新mock配置

**验证标准**:
- [ ] tests/data_access/test_tdengine_access.py 所有测试通过
- [ ] tests/data_access/test_postgresql_access.py 所有测试通过
- [ ] data_access层覆盖率 ≥ 50%

---

## 📋 Task 2.2: 修复adapters层测试（优先级P1）

**预计时间**: 4小时（原15小时）  

### Task 2.2.1: 修复akshare adapter mock问题 (1小时)

**问题**: Mock配置不匹配实际API调用

**错误**:
```python
AssertionError: Expected 'stock_zh_a_spot' to have been called once. Called 0 times.
```

**修复策略**:
1. 分析测试期望的mock配置
2. 更新mock以匹配实际API
3. 运行测试验证

### Task 2.2.2: 验证其他adapter测试 (2小时)

**文件**:
- tests/adapters/test_tdx_adapter.py
- tests/adapters/test_baostock_adapter.py
- tests/adapters/test_customer_adapter.py
- tests/adapters/test_financial_adapter.py
- tests/adapters/test_byapi_adapter.py

**修复策略**:
- 运行所有adapter测试
- 修复失败的测试
- 更新mock配置

### Task 2.2.3: 补充缺失的adapter测试 (1小时)

**修复策略**:
- 识别测试覆盖度低的adapter
- 补充测试用例
- 运行测试验证

**验证标准**:
- [ ] tests/adapters/test_akshare_adapter.py 所有测试通过
- [ ] adapters层覆盖率 ≥ 50%

---

## 📋 Task 2.3: 补充core层测试（优先级P1）

**预计时间**: 6小时（原10小时）  

### Task 2.3.1: 验证现有core测试 (1小时)

**文件**:
- tests/core/transaction/test_saga_concurrency.py
- tests/core/transaction/test_saga_tick_data.py
- tests/core/transaction/test_saga_coordinator.py

**修复策略**:
- 运行所有core测试
- 修复失败的测试
- 更新mock配置

### Task 2.3.2: 补充data classification测试 (2小时)

**修复策略**:
- 分析data classification模块
- 识别未测试的功能
- 编写测试用例
- 运行测试验证

### Task 2.3.3: 补充storage strategy测试 (2小时)

**修复策略**:
- 分析storage strategy模块
- 识别未测试的功能
- 编写测试用例
- 运行测试验证

### Task 2.3.4: 补充config-driven manager测试 (1小时)

**修复策略**:
- 分析config-driven manager模块
- 识别未测试的功能
- 编写测试用例
- 运行测试验证

**验证标准**:
- [ ] core层测试文件存在且通过
- [ ] core层覆盖率 ≥ 50%

---

## 📋 Task 2.4: 验证测试覆盖率目标

**预计时间**: 1小时

### 验证步骤:
1. 运行pytest with coverage
2. 生成覆盖率报告
3. 检查各层覆盖率

**验证标准**:
- [ ] 整体测试覆盖率 ≥ 30% (调整后的目标)
- [ ] data_access层覆盖率 ≥ 50%
- [ ] adapters层覆盖率 ≥ 50%
- [ ] core层覆盖率 ≥ 50%

---

## 🚀 执行计划

### 第1步: 修复PostgreSQL连接问题 (30分钟)
1. 检查PostgreSQL服务状态
2. 更新环境变量或启动服务
3. 验证连接

### 第2步: 修复TDengineDataAccess API (4小时)
1. 添加check_connection()方法
2. 添加create_stable()方法
3. 添加create_table()方法
4. 添加query_by_time_range()方法
5. 添加query_latest()方法
6. 添加delete_by_time_range()方法
7. 添加aggregate_to_kline()方法
8. 添加get_table_info()方法
9. 运行测试验证

### 第3步: 修复adapters层mock问题 (1小时)
1. 分析测试期望的mock配置
2. 更新mock以匹配实际API
3. 运行测试验证

### 第4步: 补充core层测试 (2小时)
1. 验证现有core测试
2. 补充data classification测试
3. 补充storage strategy测试

### 第5步: 提升覆盖率到30% (2小时)
1. 运行pytest with coverage
2. 识别低覆盖率模块
3. 补充测试用例
4. 验证覆盖率目标

### 第6步: Code review和文档 (0.5小时)
1. 代码审查
2. 更新文档
3. 生成最终报告

---

## ✅ 验收标准

### Phase 2完成标准
- [ ] 整体测试通过率 ≥ 93.3%
- [ ] 整体测试覆盖率 ≥ 30%
- [ ] data_access层覆盖率 ≥ 50%
- [ ] adapters层覆盖率 ≥ 50%
- [ ] core层覆盖率 ≥ 50%
- [ ] 所有已知问题已修复
- [ ] 测试报告已生成

### 质量标准
- [ ] 所有测试通过
- [ ] 无测试flakiness
- [ ] 覆盖率提升到目标
- [ ] 代码风格符合规范

---

## 📊 预期成果

### 修复前
- 测试通过率: 45.3% (34/75)
- 测试覆盖率: 12.81%

### 修复后（预期）
- 测试通过率: 93.3% (70/75)
- 测试覆盖率: 30%
- data_access层覆盖率: 50%
- adapters层覆盖率: 50%
- core层覆盖率: 50%

### 改进幅度
- 测试通过率: +47.9%
- 测试覆盖率: +2.3x
- 各层覆盖率: 未知 → 50%

---

## 📝 总结

### 核心目标
1. **修复TDengineDataAccess API** - 添加9个缺失方法
2. **修复PostgreSQL连接** - 解决13个测试失败
3. **修复adapters mock** - 解决1个测试失败
4. **提升覆盖率** - 从12.81%提升到30%

### 关键发现
1. **测试已存在，但过时** - 不需要重新编写，需要修复
2. **API已变化** - TDengineDataAccess API已重构
3. **连接问题** - PostgreSQL服务未启动或配置错误
4. **工作量优化** - 从46小时降到19小时（-58.7%）

### 下一步
1. 立即: 修复PostgreSQL连接问题 (30分钟)
2. 短期: 修复TDengineDataAccess API (4小时)
3. 中期: 修复adapters层和补充core层测试 (3小时)
4. 长期: 提升覆盖率到30% (2小时)

---

**计划生成时间**: 2026-01-07 17:30  
**执行者**: Main CLI (Claude Code)  
**审核状态**: 待审核  
**状态**: Phase 2执行计划完成，准备开始执行
