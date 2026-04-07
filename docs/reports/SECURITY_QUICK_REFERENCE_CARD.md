# 安全修复快速参考卡

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或专题文档，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


**个人项目 - 1-2天完成**

---

## 🎯 3个核心任务

### 任务1: 修复SQL注入（2小时）

**需要修改的文件**（仅3个）:
```
src/data_access/postgresql_data_access.py
src/data_access/tdengine_data_access.py
src/core/data_manager.py
```

**PostgreSQL修复模式**:
```python
# ❌ 之前
query = f"SELECT * FROM stocks WHERE symbol = '{symbol}'"
result = self.execute(query)

# ✅ 之后
query = "SELECT * FROM stocks WHERE symbol = %s"
params = (symbol,)
result = self.execute(query, params)
```

**TDengine修复模式**:
```python
# 添加简单验证函数
def _validate_symbol(symbol: str) -> str:
    if not all(c.isalnum() or c in '_-/' for c in symbol):
        raise ValueError(f"Invalid symbol: {symbol}")
    return symbol

# 查询前调用
symbol = self._validate_symbol(symbol)
query = f"SELECT * FROM data WHERE symbol = '{symbol}'"
```

### 任务2: 添加配置检查（30分钟）

**创建文件**: `src/utils/simple_config_check.py`

```python
import os
import logging

logger = logging.getLogger(__name__)

def check_config_strength():
    """检查配置强度，仅警告不强制"""

    issues = []

    # 检查JWT密钥
    jwt_secret = os.getenv('JWT_SECRET_KEY', '')
    if len(jwt_secret) < 32:
        issues.append(f"JWT密钥长度不足 ({len(jwt_secret)} < 32)")

    # 检查数据库密码
    pg_password = os.getenv('POSTGRESQL_PASSWORD', '')
    if len(pg_password) < 8:
        issues.append(f"PostgreSQL密码过短 ({len(pg_password)} < 8)")

    if issues:
        logger.warning("⚠️  配置安全性提醒:")
        for issue in issues:
            logger.warning(f"  - {issue}")
        logger.warning("建议: 使用 'openssl rand -hex 32' 生成强密钥")
        logger.warning("个人项目可以忽略此警告，不影响使用")
    else:
        logger.info("✅ 配置检查通过")
```

**集成到启动**（在 `unified_manager.py` 或 `app_factory.py`）:

```python
from src.utils.simple_config_check import check_config_strength

# 在应用启动开始处添加
check_config_strength()
```

### 任务3: 创建基础测试（1小时）

**创建文件**: `tests/security/test_basic_security.py`

```python
import pytest

def test_postgres_injection():
    """测试PostgreSQL注入防护"""
    from src.data_access.postgresql_data_access import PostgreSQLDataAccess

    db = PostgreSQLDataAccess()

    # 尝试注入
    malicious_symbol = "BTC' OR '1'='1"
    result = db.fetch_market_data(symbol=malicious_symbol, start_date="2025-01-01")

    # 应该返回空，而不是所有记录
    assert len(result) == 0

def test_tdengine_validation():
    """测试TDengine符号验证"""
    from src.data_access.tdengine_data_access import TDengineDataAccess

    db = TDengineDataAccess()

    # 有效符号应该工作
    valid_symbol = "AAPL"

    # 无效符号应该抛出异常
    invalid_symbol = "AAPL'; DROP TABLE--"
    with pytest.raises(ValueError, match="Invalid symbol"):
        db.fetch_tick_data(symbol=invalid_symbol)
```

**运行测试**:
```bash
pytest tests/security/test_basic_security.py -v
```

---

## 📋 实施步骤

### Day 1 上午（2小时）

```bash
# 1. 审计SQL查询
grep -r "f\"SELECT\|f'select" src/data_access/

# 2. 修复 postgresql_data_access.py
#    - 打开文件
#    - 搜索 f"SELECT 或 f'select
#    - 逐个改为参数化查询

# 3. 测试
pytest tests/ -k postgresql -v
```

### Day 1 下午（2小时）

```bash
# 1. 修复 tdengine_data_access.py
#    - 添加 _validate_symbol 函数
#    - 在查询前调用验证

# 2. 添加配置检查
#    - 创建 simple_config_check.py
#    - 在启动处集成

# 3. 测试
python unified_manager.py  # 查看配置检查输出
```

### Day 2 上午（1小时）

```bash
# 1. 创建测试
#    - 创建 test_basic_security.py
#    - 运行测试

pytest tests/security/test_basic_security.py -v

# 2. 运行完整测试套件
pytest tests/ -v

# 3. 更新README（添加安全说明章节）
```

---

## ✅ 完成检查清单

- [ ] PostgreSQL所有f-string查询已改为参数化
- [ ] TDengine添加了符号验证
- [ ] 配置检查已集成到启动
- [ ] 安全测试通过
- [ ] 所有现有测试通过
- [ ] README已更新

---

## 🚀 快速命令

```bash
# 查找SQL注入问题
grep -rn "f\"" src/data_access/ | grep -E "(SELECT|INSERT|UPDATE|DELETE)"

# 运行测试
pytest tests/security/ -v

# 生成强密钥
openssl rand -hex 32

# 检查配置
python -c "from src.utils.simple_config_check import check_config_strength; check_config_strength()"
```

---

## 📞 遇到问题？

**问题1**: 测试失败
```bash
# 查看详细错误
pytest tests/security/test_basic_security.py -v -s
```

**问题2**: 功能不正常
```bash
# 回滚修改
git checkout HEAD -- src/data_access/postgresql_data_access.py
```

**问题3**: 不确定如何修改
```bash
# 查看完整文档
cat docs/reports/SECURITY_FIX_SIMPLIFIED_PLAN.md
```

---

## 🎯 预期结果

**完成后**:
- ✅ 3个核心文件SQL注入已修复
- ✅ 启动时显示配置检查
- ✅ 2-3个安全测试通过
- ✅ 所有功能测试通过
- ✅ README有安全说明

**不包含**（个人项目不需要）:
- ❌ 复杂的连接池监控
- ❌ 强制密钥验证
- ❌ 完整的安全测试套件
- ❌ 详细的审计日志

---

**时间估计**: 1-2天
**难度**: 🟢 低
**优先级**: 🟡 中等（个人项目）

**开始吧！**
