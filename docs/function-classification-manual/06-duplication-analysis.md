# 代码重复分析

**总重复案例数**: 20

## 严重性分布

| 严重性 | 案例数 | 描述 |
|--------|--------|------|
| CRITICAL | 1 | 几乎完全相同，需立即处理 |
| HIGH | 12 | 高度相似，建议优先处理 |
| MEDIUM | 7 | 显著相似，建议考虑合并 |
| LOW | 0 | 部分相似，可选优化 |

## CRITICAL - 立即处理

### DUP-63cd6c5e

**描述**: 函数 'check_permission' 在多处实现中高度相似
**Token 相似度**: 96.6%
**AST 相似度**: 100.0%

**重复位置**:

- `web/backend/app/api/auth.py:191-200`
- `web/backend/app/core/security.py:136-143`

**合并建议**:

建议立即合并：代码几乎完全相同。
1. 提取公共函数到共享工具模块
2. 在原位置调用公共函数
3. 删除重复代码

---

## HIGH - 优先处理

### DUP-40cc37bc

**描述**: 函数 'setup_logging' 在多处实现中高度相似
**Token 相似度**: 84.0%
**AST 相似度**: 91.1%

**重复位置**:

- `run_realtime_market_saver.py:29-39`
- `db_manager/validate_mystocks_architecture.py:31-38`

**合并建议**:

建议优先合并：代码高度相似。
1. 识别差异部分并参数化
2. 创建统一函数接受可变参数
3. 重构调用点使用新函数

---

### DUP-047d1d49

**描述**: 函数 'health_check' 在多处实现中高度相似
**Token 相似度**: 81.0%
**AST 相似度**: 91.9%

**重复位置**:

- `web/backend/app/main.py:86-92`
- `web/backend/app/api/market.py:346-352`

**合并建议**:

建议优先合并：代码高度相似。
1. 识别差异部分并参数化
2. 创建统一函数接受可变参数
3. 重构调用点使用新函数

---

### DUP-bc8ece80

**描述**: 函数 'run_tests' 在多处实现中高度相似
**Token 相似度**: 92.1%
**AST 相似度**: 98.3%

**重复位置**:

- `tests/acceptance/test_us2_config_driven.py:538-578`
- `tests/unit/test_postgresql_table_creation.py:223-260`

**合并建议**:

建议优先合并：代码高度相似。
1. 识别差异部分并参数化
2. 创建统一函数接受可变参数
3. 重构调用点使用新函数

---

### DUP-bc8ece80

**描述**: 函数 'run_tests' 在多处实现中高度相似
**Token 相似度**: 92.1%
**AST 相似度**: 98.3%

**重复位置**:

- `tests/acceptance/test_us2_config_driven.py:538-578`
- `tests/unit/test_mysql_table_creation.py:245-282`

**合并建议**:

建议优先合并：代码高度相似。
1. 识别差异部分并参数化
2. 创建统一函数接受可变参数
3. 重构调用点使用新函数

---

### DUP-bc8ece80

**描述**: 函数 'run_tests' 在多处实现中高度相似
**Token 相似度**: 91.3%
**AST 相似度**: 97.1%

**重复位置**:

- `tests/acceptance/test_us2_config_driven.py:538-578`
- `tests/unit/test_tdengine_table_creation.py:189-225`

**合并建议**:

建议优先合并：代码高度相似。
1. 识别差异部分并参数化
2. 创建统一函数接受可变参数
3. 重构调用点使用新函数

---

### DUP-5c30cb7f

**描述**: 函数 'run_tests' 在多处实现中高度相似
**Token 相似度**: 93.9%
**AST 相似度**: 100.0%

**重复位置**:

- `tests/unit/test_postgresql_table_creation.py:223-260`
- `tests/unit/test_mysql_table_creation.py:245-282`

**合并建议**:

建议优先合并：代码高度相似。
1. 识别差异部分并参数化
2. 创建统一函数接受可变参数
3. 重构调用点使用新函数

---

### DUP-5c30cb7f

**描述**: 函数 'run_tests' 在多处实现中高度相似
**Token 相似度**: 81.1%
**AST 相似度**: 87.5%

**重复位置**:

- `tests/unit/test_postgresql_table_creation.py:223-260`
- `tests/unit/test_config_validation.py:281-317`

**合并建议**:

建议优先合并：代码高度相似。
1. 识别差异部分并参数化
2. 创建统一函数接受可变参数
3. 重构调用点使用新函数

---

### DUP-5c30cb7f

**描述**: 函数 'run_tests' 在多处实现中高度相似
**Token 相似度**: 93.8%
**AST 相似度**: 98.8%

**重复位置**:

- `tests/unit/test_postgresql_table_creation.py:223-260`
- `tests/unit/test_tdengine_table_creation.py:189-225`

**合并建议**:

建议优先合并：代码高度相似。
1. 识别差异部分并参数化
2. 创建统一函数接受可变参数
3. 重构调用点使用新函数

---

### DUP-142fe70f

**描述**: 函数 'run_tests' 在多处实现中高度相似
**Token 相似度**: 81.1%
**AST 相似度**: 87.5%

**重复位置**:

- `tests/unit/test_mysql_table_creation.py:245-282`
- `tests/unit/test_config_validation.py:281-317`

**合并建议**:

建议优先合并：代码高度相似。
1. 识别差异部分并参数化
2. 创建统一函数接受可变参数
3. 重构调用点使用新函数

---

### DUP-142fe70f

**描述**: 函数 'run_tests' 在多处实现中高度相似
**Token 相似度**: 93.0%
**AST 相似度**: 98.8%

**重复位置**:

- `tests/unit/test_mysql_table_creation.py:245-282`
- `tests/unit/test_tdengine_table_creation.py:189-225`

**合并建议**:

建议优先合并：代码高度相似。
1. 识别差异部分并参数化
2. 创建统一函数接受可变参数
3. 重构调用点使用新函数

---

### DUP-d5c78093

**描述**: 函数 'run_tests' 在多处实现中高度相似
**Token 相似度**: 80.0%
**AST 相似度**: 86.2%

**重复位置**:

- `tests/unit/test_config_validation.py:281-317`
- `tests/unit/test_tdengine_table_creation.py:189-225`

**合并建议**:

建议优先合并：代码高度相似。
1. 识别差异部分并参数化
2. 创建统一函数接受可变参数
3. 重构调用点使用新函数

---

### DUP-2c09fbdb

**描述**: 函数 'get_api_documentation' 在多处实现中高度相似
**Token 相似度**: 89.4%
**AST 相似度**: 100.0%

**重复位置**:

- `adapters/byapi/byapi_mapping_updated.py:2410-2430`
- `adapters/byapi/byapi_mapping_optimized.py:125-137`

**合并建议**:

建议优先合并：代码高度相似。
1. 识别差异部分并参数化
2. 创建统一函数接受可变参数
3. 重构调用点使用新函数

---

## MEDIUM - 建议处理

### DUP-894b0043

**描述**: 函数 'main' 在多处实现中高度相似
**Token 相似度**: 65.2%
**AST 相似度**: 50.1%

**重复位置**:

- `test_us2_acceptance.py:273-319`
- `test_config_driven_table_manager.py:185-244`

**合并建议**:

建议考虑合并：代码存在显著相似性。
1. 分析差异是否可以通过配置或参数处理
2. 评估合并的成本收益
3. 如果合适，创建抽象基类或模板方法

---

### DUP-3199e008

**描述**: 函数 'main' 在多处实现中高度相似
**Token 相似度**: 60.5%
**AST 相似度**: 66.3%

**重复位置**:

- `examples/tdx_import_example.py:218-241`
- `db_manager/fixed_example.py:75-104`

**合并建议**:

建议考虑合并：代码存在显著相似性。
1. 分析差异是否可以通过配置或参数处理
2. 评估合并的成本收益
3. 如果合适，创建抽象基类或模板方法

---

### DUP-80afce14

**描述**: 函数 'main' 在多处实现中高度相似
**Token 相似度**: 66.7%
**AST 相似度**: 72.0%

**重复位置**:

- `utils/validate_test_naming.py:180-199`
- `utils/validate_gitignore.py:259-272`

**合并建议**:

建议考虑合并：代码存在显著相似性。
1. 分析差异是否可以通过配置或参数处理
2. 评估合并的成本收益
3. 如果合适，创建抽象基类或模板方法

---

### DUP-dde9a59e

**描述**: 函数 'get_auth_token' 在多处实现中高度相似
**Token 相似度**: 63.3%
**AST 相似度**: 55.5%

**重复位置**:

- `test_tdx_api.py:26-40`
- `utils/check_api_health.py:120-132`

**合并建议**:

建议考虑合并：代码存在显著相似性。
1. 分析差异是否可以通过配置或参数处理
2. 评估合并的成本收益
3. 如果合适，创建抽象基类或模板方法

---

### DUP-047d1d49

**描述**: 函数 'health_check' 在多处实现中高度相似
**Token 相似度**: 70.0%
**AST 相似度**: 80.0%

**重复位置**:

- `web/backend/app/main.py:86-92`
- `web/backend/app/api/wencai.py:389-402`

**合并建议**:

建议考虑合并：代码存在显著相似性。
1. 分析差异是否可以通过配置或参数处理
2. 评估合并的成本收益
3. 如果合适，创建抽象基类或模板方法

---

### DUP-069e9ff3

**描述**: 函数 'health_check' 在多处实现中高度相似
**Token 相似度**: 63.6%
**AST 相似度**: 72.7%

**重复位置**:

- `web/backend/app/api/market.py:346-352`
- `web/backend/app/api/wencai.py:389-402`

**合并建议**:

建议考虑合并：代码存在显著相似性。
1. 分析差异是否可以通过配置或参数处理
2. 评估合并的成本收益
3. 如果合适，创建抽象基类或模板方法

---

### DUP-bc8ece80

**描述**: 函数 'run_tests' 在多处实现中高度相似
**Token 相似度**: 79.5%
**AST 相似度**: 86.6%

**重复位置**:

- `tests/acceptance/test_us2_config_driven.py:538-578`
- `tests/unit/test_config_validation.py:281-317`

**合并建议**:

建议考虑合并：代码存在显著相似性。
1. 分析差异是否可以通过配置或参数处理
2. 评估合并的成本收益
3. 如果合适，创建抽象基类或模板方法

---
