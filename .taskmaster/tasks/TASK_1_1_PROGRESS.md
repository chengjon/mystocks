# Task 1.1: 修复SQL注入漏洞 - 详细执行进度

**任务ID**: 1.1
**优先级**: 🔴 Critical (必须)
**创建时间**: 2025-11-06
**预计工时**: 3小时
**当前进度**: 30% (识别和文档化完成)

---

## 📋 任务概述

修复当前系统中发现的SQL注入漏洞，确保所有数据库查询使用参数化查询而非字符串拼接。

---

## 🔍 第一阶段完成：漏洞识别和分析 (30分钟)

### 已完成工作

#### 1. 全面代码扫描 ✅
- 扫描范围: 超过100个Python文件
- 搜索模式:
  - `execute(f"` - f-string SQL执行
  - `execute(.*\{.*\}` - 字符串格式化SQL
  - 字符串拼接SQL语句

#### 2. 发现的漏洞 ✅
识别到 **5个SQL注入漏洞**，其中 **3个CRITICAL**，**2个MEDIUM**：

| 漏洞ID | 文件 | 行号 | 严重级 | 类型 |
|--------|------|------|--------|------|
| SQL-INJ-001 | data_access.py | 1209-1210 | CRITICAL | WHERE IN 条件注入 |
| SQL-INJ-002 | data_access.py | 1215, 1224 | CRITICAL | WHERE = 条件注入 |
| SQL-INJ-003 | data_access.py | 1257-1271 | CRITICAL | DELETE 条件注入 |
| SQL-INJ-004 | data_access.py | 601, 622, 1200, 1259 | MEDIUM | 动态表名风险 |
| SQL-INJ-005 | data_access/postgresql_access.py | 291, 502, 510 | MEDIUM | 动态列名风险 |

#### 3. 详细漏洞文档 ✅
生成文件: `SQL_INJECTION_VULNERABILITY_REPORT.md`
- 漏洞描述: 每个漏洞的详细说明
- 攻击向量: 实际的注入攻击案例
- 影响评估: 业务和安全影响
- 修复方案: 代码示例和最佳实践
- 测试清单: 验收标准

#### 4. 安全测试套件 ✅
生成文件: `tests/test_security_sql_injection.py`
- 测试用例数: 13个
- 测试状态: ✅ 全部通过
- 覆盖范围:
  - 漏洞验证: 证明漏洞确实存在
  - 安全模式: 演示正确的修复方式
  - OWASP合规: 参数化查询验证

---

## 漏洞详细说明

### CRITICAL 1: WHERE IN 条件注入
**文件**: data_access.py:1209-1210

**易受攻击的代码**:
```python
values = "','".join(value)  # 用户输入直接拼��
conditions.append(f"{key} IN ('{values}')")  # 无参数化
```

**攻击示例**:
```python
filters = {"id": ["1", "' OR '1'='1", "2"]}
# 产生: id IN ('1',' OR '1'='1','2')
# 结果: 返回所有记录 (恶意条件永远为真)
```

**风险**: 数据泄露，未授权访问

---

### CRITICAL 2: WHERE = 条件注入
**文件**: data_access.py:1215, 1224

**易受攻击的代码**:
```python
elif isinstance(value, str):
    conditions.append(f"{key} = '{value}'")  # 无转义，无参数化
```

**攻击示例**:
```python
filters = {"stock_code": "600000' OR '1'='1"}
# 产生: stock_code = '600000' OR '1'='1'
# 结果: 返回所有记录
```

**风险**: 身份认证绕过，权限提升

---

### CRITICAL 3: DELETE 条件注入
**文件**: data_access.py:1257-1271

**易受攻击的代码**:
```python
def _build_delete_query(self, table_name: str, filters: Dict) -> str:
    base_query = f"DELETE FROM {table_name}"
    for key, value in filters.items():
        if isinstance(value, str):
            conditions.append(f"{key} = '{value}'")  # 无参数化
```

**攻击示例**:
```python
filters = {"id": "1' OR '1'='1"}
# 产生: DELETE FROM users WHERE id = '1' OR '1'='1'
# 结果: 删除所有用户记录 (数据灾难!)
```

**风险**: 完全数据丢失，业务中断，监管违规

---

## 下一步计划

### 第2阶段：代码修复 (2小时)

需要修复的文件和方法:

#### 修复1: _build_analysis_query (data_access.py:1200)
```python
# ❌ 当前易受攻击的代码
def _build_analysis_query(self, table_name: str, filters: Dict = None) -> str:
    base_query = f"SELECT * FROM {table_name}"
    conditions = []
    if filters:
        for key, value in filters.items():
            if isinstance(value, str):
                conditions.append(f"{key} = '{value}'")  # VULNERABLE

# ✅ 修复方案 - 使用参数化查询
def _build_analysis_query(self, table_name: str, filters: Dict = None):
    # 步骤1: 白名单验证表名
    ALLOWED_TABLES = {"daily_kline", "users", "symbols_info", ...}
    if table_name not in ALLOWED_TABLES:
        raise ValueError(f"Invalid table: {table_name}")

    # 步骤2: 构建带参数的查询
    base_query = f"SELECT * FROM {table_name}"
    conditions = []
    bind_params = {}

    if filters:
        for idx, (key, value) in enumerate(filters.items()):
            param_name = f"param_{idx}"
            conditions.append(f"{key} = :{param_name}")
            bind_params[param_name] = value

    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)

    # 步骤3: 返回SQLAlchemy text对象和参数
    from sqlalchemy import text
    return text(base_query), bind_params
```

#### 修复2: _build_delete_query (data_access.py:1257)
```python
# ❌ 当前易受攻击的代码
def _build_delete_query(self, table_name: str, filters: Dict) -> str:
    base_query = f"DELETE FROM {table_name}"
    conditions = []
    for key, value in filters.items():
        if isinstance(value, str):
            conditions.append(f"{key} = '{value}'")  # VULNERABLE

# ✅ 修复方案
def _build_delete_query(self, table_name: str, filters: Dict):
    # 白名单验证
    ALLOWED_TABLES = {"daily_kline", "users", ...}
    if table_name not in ALLOWED_TABLES:
        raise ValueError(f"Invalid table: {table_name}")

    # 参数化DELETE
    base_query = f"DELETE FROM {table_name}"
    conditions = []
    params = []

    for key, value in filters.items():
        conditions.append(f"{key} = %s")
        params.append(value)

    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)

    return base_query, tuple(params)
```

#### 修复3: WHERE IN 条件 (data_access.py:1209-1210)
```python
# ❌ 当前易受攻击的代码
if isinstance(value, list):
    if isinstance(value[0], str):
        values = "','".join(value)  # VULNERABLE
        conditions.append(f"{key} IN ('{values}')")

# ✅ 修复方案 - 每个值一个占位符
def _build_where_in_clause(column_name: str, values: list):
    # 为每个值创建占位符
    placeholders = ", ".join(["%s"] * len(values))
    condition = f"{column_name} IN ({placeholders})"
    return condition, tuple(values)

# 使用示例:
# condition, params = _build_where_in_clause("id", ["1", "2", "3"])
# query = f"SELECT * FROM users WHERE {condition}"
# cursor.execute(query, params)
```

### 第3阶段：验证测试 (30分钟)

#### 测试执行:
```bash
# 1. 运行所有SQL注入安全测试
python -m pytest tests/test_security_sql_injection.py -v

# 2. 运行安全扫描工具
pip install bandit safety
bandit -r web/backend/app/ -f json > bandit_report.json
safety check --json > safety_report.json

# 3. 验证数据库连接仍正常
python -c "from data_access import DataAccessLayer; dal = DataAccessLayer(); dal.test_connection()"
```

#### 验收标准:
- [ ] 所有13个SQL注入测试通过
- [ ] Bandit扫描: 0个CRITICAL发现
- [ ] Safety检查: 无相关安全警告
- [ ] 数据库连接正常
- [ ] 性能无下降 (查询时间±10%)

---

## 当前完成清单

### 已完成 ✅
- [x] 漏洞识别和分析 (30min)
- [x] 安全测试套件创建 (test_security_sql_injection.py)
- [x] 详细漏洞报告 (SQL_INJECTION_VULNERABILITY_REPORT.md)
- [x] 修复方案文档 (包含代码示例)

### 待完成 ⏳
- [ ] 修复 data_access.py 中的3个CRITICAL漏洞 (2h)
- [ ] 修复 data_access/postgresql_access.py 中的MEDIUM漏洞 (30min)
- [ ] 运行安全测试套件验证 (20min)
- [ ] 运行bandit/safety扫描 (10min)
- [ ] 代码审查和合并 (20min)

---

## 关键技术点

### 参数化查询方式

#### 方式1: SQLAlchemy (推荐用于web backend)
```python
from sqlalchemy import text
query = text("SELECT * FROM users WHERE id = :user_id")
result = session.execute(query, {"user_id": user_id})
```

#### 方式2: psycopg2 (用于直接数据库访问)
```python
sql = "SELECT * FROM users WHERE id = %s"
cursor.execute(sql, (user_id,))
```

#### 方式3: WHERE IN 多值
```python
# 为每个值创建占位符
values = [1, 2, 3]
placeholders = ", ".join(["%s"] * len(values))
sql = f"SELECT * FROM users WHERE id IN ({placeholders})"
cursor.execute(sql, values)
```

### 白名单验证
```python
ALLOWED_TABLES = {"daily_kline", "users", "symbols_info"}
ALLOWED_COLUMNS = {"id", "symbol", "date", "close", "volume"}

if table_name not in ALLOWED_TABLES:
    raise ValueError(f"Invalid table: {table_name}")
if column_name not in ALLOWED_COLUMNS:
    raise ValueError(f"Invalid column: {column_name}")
```

---

## 资源和参考

### OWASP标准
- OWASP A03:2021 – Injection (SQL Injection)
- OWASP SQL Injection Prevention Cheat Sheet

### 工具
- **Bandit**: Python安全扫描工具
- **Safety**: Python依赖安全检查
- **SQLMap**: SQL注入测试工具 (可用于验证修复)

### 文档
- SQLAlchemy Parameterized Queries: https://docs.sqlalchemy.org/
- psycopg2 Manual: https://www.psycopg.org/psycopg2/docs/

---

## 估时和日程

| 阶段 | 工作内容 | 完成时间 |
|------|---------|---------|
| 1 ✅ | 漏洞识别分析 | 30分钟 |
| 2 ⏳ | 代码修复 | 2小时 |
| 3 ⏳ | 验证和测试 | 30分钟 |
| **总计** | | **3小时** |

---

## 成功标准

- [ ] ✅ SQL注入测试全部通过 (13/13)
- [ ] ✅ 所有数据库查询使用参数化
- [ ] ✅ 零个字符串拼接的SQL语句
- [ ] ✅ Bandit扫描零CRITICAL项
- [ ] ✅ 代码审查通过
- [ ] ✅ 数据库连接和查询性能正常

---

## 风险评估

### 当前状态
- 系统处于高风险状态，存在3个CRITICAL SQL注入漏洞
- 这些漏洞可能被外部攻击者或恶意内部人员利用
- 建议: 在生产环境中禁用这些API直到修复完成

### 修复后
- 风险降低至极低 (采用行业最佳实践)
- 完全符合OWASP和PCI DSS要求
- 通过正式安全审查

---

**下一步**: 开始第2阶段 - 代码修复，预计2小时完成所有CRITICAL漏洞的修复。
