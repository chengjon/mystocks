# TDengine Saga 事务修复与 taospy 驱动问题排查报告

## 1. 核心问题描述

在实现跨数据库（PostgreSQL + TDengine）的 Saga 分布式事务时，遇到了核心阻塞性问题：TDengine 的 **Saga 补偿机制失效**。

- **原始设计**：利用 TDengine 的 `TAGS` 存储事务 ID (`txn_id`) 和有效性标记 (`is_valid`)，通过修改 Tag 来实现逻辑删除（补偿）。
- **技术限制**：TDengine 不支持直接对超级表（STABLE）执行 `UPDATE ... SET TAG ...` 操作，导致无法在事务失败时批量标记数据失效。

## 2. 解决方案：Schema 迁移

为了规避 Tag 更新限制，我们实施了 Schema 迁移方案：

- **变更内容**：将 `txn_id` 和 `is_valid` 从 **TAGS** 迁移为 **数据列 (Columns)**。
- **优势**：
  - 数据列支持在写入时直接指定。
  - 虽然 TDengine 对普通列的更新支持有限，但我们可以采用 **"Copy-on-Write" (查询 -> 标记 -> 重写)** 策略，利用 TDengine 的自动去重机制（基于时间戳 + Tags）覆盖旧数据，从而实现软删除。

## 3. taospy 驱动 Bug 排查与修复

在实施新方案并运行测试时，遇到了极具迷惑性的错误，排查过程如下：

### 3.1 异常现象
测试脚本报错：`k线插入错误: Invalid isoformat string: 'T'`。

### 3.2 排查过程
1.  **初步怀疑**：时间戳格式问题。
    - **尝试**：将 `pandas.Timestamp` 转换为纯 Python `datetime` 对象，甚至格式化为字符串。
    - **结果**：无效，错误依旧。
2.  **二次怀疑**：WebSocket 驱动 (`taosws`) 问题。
    - **尝试**：强制切换回原生驱动 (`taos`/`taospy`)。
    - **结果**：无效，且错误信息变为 `Invalid isoformat string: 'A'`（当测试符号改为 `AAAA001` 时）。
3.  **根因定位**：
    - 观察到错误字符 `'T'` 和 `'A'` 分别对应测试用的 Symbol (`TEST001` 和 `AAAA001`) 的首字母。
    - **结论**：`taospy` 原生驱动的 `cursor.execute(sql, params)` 方法在处理参数绑定时存在严重 Bug。它错误地尝试解析第一个字符串参数（本例中为 `symbol` 标签），误判其为日期格式并尝试进行 ISO 格式转换，导致报错。

### 3.3 最终修复
为了绕过驱动层的参数解析 Bug，我们在 `TDengineDataAccess` 中采取了**直接构建 SQL** 的策略：

- **弃用**：`cursor.execute(sql, params)`
- **采用**：使用 f-string 构建完整的 SQL 字符串，手动处理类型转换和引号转义。

```python
# 修复前 (触发驱动 Bug)
cursor.execute("INSERT INTO ... VALUES (?, ...)", params)

# 修复后 (绕过驱动解析)
sql = f"INSERT INTO ... VALUES ('{ts_str}', {price}, ...)"
cursor.execute(sql)
```

## 4. 架构一致性修复

在排查过程中，还发现项目存在架构不一致问题：
- **问题**：存在两套数据访问层代码 (`src/data_access/` 和 `src/storage/access/`)。
- **修复**：确认 `DataManager`使用的是 `src/data_access/`，因此将所有修复（Schema 变更、SQL 构建逻辑）统一合并到了 `src/data_access/tdengine_access.py` 中，解决了代码修改不生效的问题。

## 5. 验证结果

运行 `tests/test_saga_transaction.py` 验证通过：
1.  **成功场景**：数据正确写入 TDengine，`is_valid=true`。
2.  **失败补偿**：PG 元数据更新失败触发 Saga 回滚，TDengine 对应数据被成功标记为 `is_valid=false`。

---
**状态**：✅ 已修复 (P0)
**日期**：2026-01-03
