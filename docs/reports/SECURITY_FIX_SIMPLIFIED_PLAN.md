# 个人项目安全修复 - 简化版实施计划

**项目类型**: 个人用户项目（非公众服务）
**创建日期**: 2026-01-01
**预计时间**: 1-2天
**优先级**: 🟡 中等（实用优先）

---

## 📋 策略调整说明

### 原计划 vs 简化计划对比

| 安全措施 | 原计划（企业级） | 简化计划（个人项目） | 理由 |
|---------|----------------|-------------------|------|
| SQL注入修复 | 完整工具+15+文件 | 仅核心3-5个文件 | 个人使用风险低 |
| 密钥验证 | 强制退出+复杂规则 | 启动时简单警告 | 方便开发调试 |
| 密码预哈希 | SHA-256+bcrypt | 保持bcrypt | 个人用户不会用超长密码 |
| 连接池监控 | 完整监控+报警 | 基础日志记录 | 连接数有限 |
| 安全测试 | 完整测试套件 | 3-5个基础测试 | 过度测试不必要 |

### 聚焦原则

✅ **保留**:
- 修复明显的SQL注入漏洞（核心文件）
- 基础的密钥强度检查（警告级别）
- 简单的输入验证

❌ **移除/简化**:
- 复杂的密钥强制验证
- 连接池泄漏监控
- 完整的安全测试套件
- 过度详细的文档

---

## 🎯 简化后的任务清单

### 任务1: 修复核心SQL注入问题（优先）

**影响文件**: 仅3个核心文件
```
src/data_access/postgresql_data_access.py
src/data_access/tdengine_data_access.py
src/core/data_manager.py
```

**工作量**: 2-3小时

**方法**: 直接替换，不需要创建复杂工具

#### 1.1 PostgreSQL快速修复

找到所有使用f-string的SQL查询，直接替换：

```python
# ❌ 之前（不安全）
def fetch_market_data(self, symbol: str, start_date: str):
    query = f"SELECT * FROM stocks WHERE symbol = '{symbol}' AND trade_date >= '{start_date}'"
    return self.execute_query(query)

# ✅ 之后（安全）
def fetch_market_data(self, symbol: str, start_date: str):
    query = "SELECT * FROM stocks WHERE symbol = %s AND trade_date >= %s"
    params = (symbol, start_date)
    return self.execute_query(query, params)
```

**需要修改的函数模式**:
- 所有 `SELECT` 查询使用 `params` 元组
- 所有 `INSERT` 查询使用 `params` 元组
- 所有 `UPDATE` 查询使用 `params` 元组

**验证**:
```bash
# 运行现有测试
pytest tests/ -k postgresql -v

# 手动测试
python scripts/tests/test_postgresql_access.py
```

#### 1.2 TDengine快速修复

TDengine的Python驱动对参数化查询支持有限，使用简单转义：

```python
# ❌ 之前（不安全）
def fetch_tick_data(self, symbol: str):
    query = f"SELECT * FROM tick_data WHERE symbol = '{symbol}'"
    return self.execute(query)

# ✅ 之后（基础安全）
def fetch_tick_data(self, symbol: str):
    # 简单验证：只允许字母、数字、下划线
    if not symbol.replace('_', '').isalnum():
        raise ValueError(f"Invalid symbol: {symbol}")

    query = f"SELECT * FROM tick_data WHERE symbol = '{symbol}'"
    return self.execute(query)
```

**理由**:
- 个人项目，输入源可信
- 简单验证足够防止意外
- 不需要完整的白名单系统

---

### 任务2: 添加基础密钥检查（非强制）

**工作量**: 30分钟

**目的**: 启动时提醒，不强制退出

```python
# src/utils/simple_config_check.py
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

    # 输出结果
    if issues:
        logger.warning("⚠️  配置安全性提醒:")
        for issue in issues:
            logger.warning(f"  - {issue}")
        logger.warning("建议: 使用 'openssl rand -hex 32' 生成强密钥")
        logger.warning("个人项目可以忽略此警告，不影响使用")
    else:
        logger.info("✅ 配置检查通过")
```

**集成到启动**:

```python
# unified_manager.py 或 app_factory.py
def create_app():
    logger.info("初始化应用...")

    # 非强制检查，仅提醒
    from src.utils.simple_config_check import check_config_strength
    check_config_strength()

    # 继续启动
    app = FastAPI()
    # ...
```

**使用说明**:
```bash
# 启动时会看到提醒或通过
python unified_manager.py

# 输出示例（密钥弱）:
⚠️  配置安全性提醒:
  - JWT密钥长度不足 (8 < 32)
建议: 使用 'openssl rand -hex 32' 生成强密钥
个人项目可以忽略此警告，不影响使用

# 输出示例（密钥强）:
✅ 配置检查通过
```

---

### 任务3: 创建简单安全测试

**工作量**: 1小时

**目的**: 确保基础修复有效

```python
# tests/security/test_basic_security.py
import pytest

class TestBasicSQLInjection:
    """基础SQL注入测试"""

    def test_postgres_symbol_injection(self):
        """测试PostgreSQL符号注入防护"""
        from src.data_access.postgresql_data_access import PostgreSQLDataAccess

        db = PostgreSQLDataAccess()

        # 尝试注入
        malicious_symbol = "BTC' OR '1'='1"
        result = db.fetch_market_data(symbol=malicious_symbol, start_date="2025-01-01")

        # 应该返回空（不匹配任何记录），而不是所有记录
        assert len(result) == 0, "SQL注入防护失败"

    def test_tdengine_symbol_validation(self):
        """测试TDengine符号验证"""
        from src.data_access.tdengine_data_access import TDengineDataAccess

        db = TDengineDataAccess()

        # 测试有效符号
        valid_symbol = "AAPL"
        # 应该正常工作

        # 测试无效符号（包含SQL字符）
        invalid_symbol = "AAPL'; DROP TABLE--"
        with pytest.raises(ValueError, match="Invalid symbol"):
            db.fetch_tick_data(symbol=invalid_symbol)

class TestBasicConfigCheck:
    """基础配置检查测试"""

    def test_weak_jwt_warning(self, caplog):
        """测试弱JWT密钥警告"""
        from src.utils.simple_config_check import check_config_strength

        import os
        original = os.environ.get('JWT_SECRET_KEY')
        os.environ['JWT_SECRET_KEY'] = 'short'

        with caplog.at_level(logging.WARNING):
            check_config_strength()

        assert 'JWT密钥长度不足' in caplog.text
        assert '可以忽略' in caplog.text  # 确认是警告而非错误

        if original:
            os.environ['JWT_SECRET_KEY'] = original

    def test_strong_config_pass(self, caplog):
        """测试强配置通过"""
        from src.utils.simple_config_check import check_config_strength

        import os
        original_jwt = os.environ.get('JWT_SECRET_KEY')
        original_pg = os.environ.get('POSTGRESQL_PASSWORD')

        os.environ['JWT_SECRET_KEY'] = 'a' * 32
        os.environ['POSTGRESQL_PASSWORD'] = 'strong_password_123'

        with caplog.at_level(logging.INFO):
            check_config_strength()

        assert '配置检查通过' in caplog.text

        if original_jwt:
            os.environ['JWT_SECRET_KEY'] = original_jwt
        if original_pg:
            os.environ['POSTGRESQL_PASSWORD'] = original_pg
```

**运行测试**:
```bash
# 运行基础安全测试
pytest tests/security/test_basic_security.py -v

# 应该看到: 3 passed
```

---

## 📊 简化后的时间表

### 第1天（3-4小时）

**上午**（2小时）:
- [ ] 修复 `postgresql_data_access.py` 中的SQL注入
  - 使用全局搜索/替换: `f"SELECT` → 查找所有查询
  - 逐个改为参数化查询
  - 测试确保功能正常

**下午**（2小时）:
- [ ] 修复 `tdengine_data_access.py` 中的SQL注入
  - 添加简单符号验证
  - 测试确保功能正常
- [ ] 添加基础配置检查
  - 创建 `simple_config_check.py`
  - 集成到启动流程

### 第2天（1-2小时）

**上午**（1小时）:
- [ ] 创建基础安全测试
  - 编写3-5个测试用例
  - 运行并确保通过

**验证**（30分钟）:
- [ ] 运行完整测试套件
  - 确保没有破坏现有功能
  - 安全测试全部通过

**完成**（30分钟）:
- [ ] 更新文档
  - 在README中添加安全说明
  - 记录修改的文件

---

## ✅ 完成标准

### 必须完成（核心）
- [x] 3个核心文件的SQL注入已修复
- [x] 基础配置检查已添加
- [x] 3-5个安全测试通过
- [x] 现有功能测试全部通过

### 可选完成（增强）
- [ ] 添加更多输入验证
- [ ] 创建开发环境安全指南
- [ ] 配置Git pre-commit hook

---

## 🔧 实施步骤

### Step 1: 审计核心文件（15分钟）

```bash
# 查找所有SQL f-string使用
grep -r "f\"SELECT\|f'select" src/data_access/

# 查找所有SQL f-string使用
grep -r "f'INSERT\|f'insert" src/data_access/

# 记录需要修改的位置
# 输出到: security_audit_simple.txt
```

### Step 2: 修复PostgreSQL（1小时）

打开 `src/data_access/postgresql_data_access.py`:

1. 搜索所有f-string SQL查询
2. 逐个替换为参数化查询
3. 测试每个修改

**示例修改**:
```python
# 找到这样的代码
def get_stock_data(self, symbol, start_date):
    query = f"SELECT * FROM stocks WHERE symbol = '{symbol}' AND date >= '{start_date}'"
    # ...

# 改为
def get_stock_data(self, symbol, start_date):
    query = "SELECT * FROM stocks WHERE symbol = %s AND date >= %s"
    params = (symbol, start_date)
    # ...
```

### Step 3: 修复TDengine（30分钟）

打开 `src/data_access/tdengine_data_access.py`:

1. 添加简单的符号验证函数
2. 在查询前调用验证

**添加验证函数**:
```python
def _validate_symbol(symbol: str) -> str:
    """验证股票符号"""
    if not symbol:
        raise ValueError("Symbol cannot be empty")

    # 只允许字母、数字、下划线、斜杠
    if not all(c.isalnum() or c in '_-/' for c in symbol):
        raise ValueError(f"Invalid symbol: {symbol}")

    return symbol
```

**在查询前调用**:
```python
def fetch_data(self, symbol: str):
    # 先验证
    symbol = self._validate_symbol(symbol)

    # 然后查询
    query = f"SELECT * FROM data WHERE symbol = '{symbol}'"
    return self.execute(query)
```

### Step 4: 添加配置检查（30分钟）

创建文件并集成（见任务2代码）

### Step 5: 创建简单测试（1小时）

创建测试文件并运行（见任务3代码）

---

## 📝 文档更新

### README.md 添加章节

```markdown
## 安全说明

本项目是个人使用项目，已实施基础安全措施：

### 已实施
- ✅ 核心SQL查询使用参数化查询
- ✅ 输入验证（股票符号、日期等）
- ✅ 启动时配置强度检查

### 开发建议
- 不要在生产环境使用默认密钥
- 定期更新依赖包
- 使用强密码

### 密钥生成
```bash
# 生成强JWT密钥
openssl rand -hex 32

# 生成数据库密码
openssl rand -base64 16
```
```

---

## 🎯 成功指标

| 指标 | 目标 | 如何验证 |
|------|------|----------|
| SQL注入修复 | 核心文件已修复 | 代码审查 |
| 功能正常 | 100%测试通过 | `pytest tests/` |
| 安全测试 | 3-5个测试通过 | `pytest tests/security/` |
| 时间 | 1-2天完成 | 实际用时 |

---

## 💡 注意事项

### DO（推荐做）
✅ 修复明显的SQL注入
✅ 添加基本输入验证
✅ 配置检查（警告级别）
✅ 几个简单测试

### DON'T（不需要做）
❌ 复杂的密钥强制验证
❌ 完整的连接池监控
❌ 企业级安全测试套件
❌ 过度详细的文档

---

## 📞 需要帮助？

如果遇到问题：

1. **查看代码示例**: 本文档包含所有需要的代码
2. **运行测试**: `pytest tests/ -v` 确保没有破坏功能
3. **参考文档**:
   - `docs/guides/SECURE_CODING_QUICK_REFERENCE.md`（已创建）
   - Python安全最佳实践

---

## 📋 修改文件清单

**需要创建的文件**:
- `src/utils/simple_config_check.py` - 配置检查
- `tests/security/test_basic_security.py` - 基础测试

**需要修改的文件**:
- `src/data_access/postgresql_data_access.py` - SQL注入修复
- `src/data_access/tdengine_data_access.py` - SQL注入修复
- `src/core/data_manager.py` - SQL注入修复（如果有SQL查询）
- `unified_manager.py` 或 `app_factory.py` - 集成配置检查
- `README.md` - 添加安全说明

**不需要修改**:
- 所有适配器文件（个人使用风险低）
- 所有业务逻辑文件
- 所有前端文件

---

## 🔄 回滚计划

如果修改导致问题：

```bash
# 方法1: Git回滚
git checkout <修改前的commit> -- src/data_access/

# 方法2: 手动回滚
# 保留修改前的代码备份
# 如果出问题直接恢复备份
```

---

**版本**: 简化版 v1.0
**状态**: ✅ 可以开始实施
**预计完成**: 1-2天
**复杂度**: 🟢 低（个人项目实用优先）

---

## 总结

这个简化计划适合个人项目：

✅ **实用**: 修复真正的风险，不过度设计
✅ **快速**: 1-2天即可完成
✅ **简单**: 不需要复杂工具和框架
✅ **足够**: 个人使用场景下的安全水平

**现在可以开始实施了！**
