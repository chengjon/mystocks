# 安全审计报告 - 个人项目简化版

**审计日期**: 2026-01-01
**审计范围**: 核心数据访问文件（3个）
**审计方法**: SQL注入风险扫描

---

## 📊 审计结果总结

| 文件 | 风险数量 | 风险等级 | 现有保护 |
|------|---------|---------|---------|
| `src/storage/access/postgresql.py` | 1 | 🟡 中 | 白名单验证 |
| `src/data_access/postgresql_access.py` | 3 | 🟠 高 | 部分验证 |
| `src/storage/access/tdengine.py` | 4 | 🟠 高 | 无 |

**总计**: 8个SQL注入风险点

---

## 🔍 详细发现

### 文件1: `src/storage/access/postgresql.py`

**位置**: 第640行
```python
base_query = f"SELECT * FROM {table_name}"
```

**风险等级**: 🟡 中等
**现有保护**: ✅ 有白名单验证（第637-638行）
```python
ALLOWED_TABLES = {"stock_daily_kline", "stock_minute_kline", ...}
if table_name not in ALLOWED_TABLES:
    raise ValueError(f"Invalid table name: {table_name}")
```

**评估**: 白名单验证有效，但仍有改进空间
**建议**: 使用psycopg2.sql.Identifier进一步加固

**优先级**: 🟢 低（已有基础保护）

---

### 文件2: `src/data_access/postgresql_access.py`

#### 风险点1: 第383行
```python
sql = f"SELECT {cols} FROM {table_name}"
```

**风险等级**: 🟠 中高
**现有保护**: ❌ 无验证
**攻击向量**: `table_name` 和 `cols` 参数可能被注入

**示例攻击**:
```python
table_name = "stocks; DROP TABLE users--"
cols = "* FROM users--"
# 结果: SELECT * FROM users-- FROM stocks; DROP TABLE users--
```

**优先级**: 🔴 高（需立即修复）

---

#### 风险点2: 第711行
```python
sql = f"SELECT * FROM {table_name} WHERE {filters['where']}"
```

**风险等级**: 🔴 高
**现有保护**: ⚠️ 部分危险模式检测（第392-396行）
```python
dangerous_patterns = ["'", ";", "--", "/*", "*/", "xp_", "sp_"]
```

**评估**: 危险模式检测不够全面，可能被绕过
**建议**: 使用参数化查询

**优先级**: 🔴 高（需立即修复）

---

#### 风险点3: 第717行
```python
sql = f"SELECT * FROM {table_name}"
```

**风险等级**: 🟡 中等
**现有保护**: ❌ 无（但table_name通常来自内部配置）

**评估**: 风险较低，但应添加验证
**建议**: 添加白名单验证或使用psycopg2.sql.Identifier

**优先级**: 🟡 中（建议修复）

---

### 文件3: `src/storage/access/tdengine.py`

#### 风险点1: 第510行
```python
base_query = f"SELECT * FROM {table_name}"
```

**风险等级**: 🟡 中等
**现有保护**: ❌ 无
**评估**: TDengine对参数化查询支持有限，需使用验证

**优先级**: 🟡 中（需添加验证）

---

#### 风险点2-4: 第518-524行
```python
if isinstance(value, list):
    symbols = "','".join(value)  # ⚠️ 无验证
    conditions.append(f"symbol IN ('{symbols}')")
else:
    conditions.append(f"symbol = '{value}'")  # ⚠️ 无验证
```

**风险等级**: 🔴 高
**现有保护**: ❌ 无

**示例攻击**:
```python
symbol = "AAPL' OR '1'='1"
# 结果: symbol = 'AAPL' OR '1'='1'  -- 返回所有数据
```

**优先级**: 🔴 高（需立即修复）

---

## 🎯 修复优先级

### 🔴 立即修复（高风险）

1. **`src/data_access/postgresql_access.py:383`** - 列名和表名注入
2. **`src/data_access/postgresql_access.py:711`** - WHERE子句注入
3. **`src/storage/access/tdengine.py:518-524`** - 符号注入

### 🟡 建议修复（中风险）

4. **`src/storage/access/postgresql.py:640`** - 添加额外保护
5. **`src/data_access/postgresql_access.py:717`** - 添加验证

---

## 🔧 修复策略

### PostgreSQL修复

使用psycopg2的参数化查询和sql.Identifier：

```python
from psycopg2 import sql

# 修复前
query = f"SELECT {cols} FROM {table_name} WHERE symbol = '{symbol}'"

# 修复后
query = sql.SQL("SELECT {} FROM {} WHERE symbol = %s").format(
    sql.SQL(", ").join(map(sql.Identifier, cols.split(", "))),
    sql.Identifier(table_name)
)
params = (symbol,)
```

### TDengine修复

由于TDengine Python驱动限制，使用白名单验证：

```python
def _validate_symbol(symbol: str) -> str:
    """验证股票符号"""
    if not isinstance(symbol, str):
        raise ValueError("Symbol must be string")

    # 只允许字母、数字、下划线、斜杠、点号
    if not symbol or len(symbol) > 20:
        raise ValueError(f"Invalid symbol length: {symbol}")

    if not all(c.isalnum() or c in '_-./' for c in symbol):
        raise ValueError(f"Invalid symbol: {symbol}")

    return symbol

# 使用验证
symbol = _validate_symbol(symbol)
query = f"SELECT * FROM {table_name} WHERE symbol = '{symbol}'"
```

---

## 📝 修复清单

### 文件: `src/data_access/postgresql_access.py`

- [ ] 第383行: 添加列名验证和表名验证
- [ ] 第711行: 改为参数化查询
- [ ] 第717行: 添加表名白名单验证

### 文件: `src/storage/access/tdengine.py`

- [ ] 添加`_validate_symbol()`函数
- [ ] 第510行: 添加表名验证
- [ ] 第518-524行: 在拼接前验证所有符号
- [ ] 第522行: 使用验证函数

---

## ✅ 验证计划

修复后，运行以下测试：

```bash
# 1. 单元测试
pytest tests/unit/data_access/test_postgresql_access*.py -v

# 2. TDengine测试
pytest tests/unit/data_access/test_tdengine_access*.py -v

# 3. 集成测试
pytest tests/integration/ -v

# 4. 创建安全测试
pytest tests/security/test_basic_security.py -v
```

---

## 📊 风险评估总结

### 修复前
- **高风险点**: 3个
- **中风险点**: 5个
- **总风险点**: 8个

### 修复后（预期）
- **高风险点**: 0个
- **中风险点**: 0个
- **低风险点**: 0个（全部已修复）

---

## 📅 预计时间

- **审计**: ✅ 已完成（30分钟）
- **修复PostgreSQL**: 1小时
- **修复TDengine**: 1小时
- **测试验证**: 30分钟

**总计**: 约3小时

---

**审计人员**: Claude Code (Security Agent)
**审计方法**: 静态代码分析 + 模式匹配
**下一步**: 开始修复高风险点
