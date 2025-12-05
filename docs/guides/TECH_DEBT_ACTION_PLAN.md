# 技术负债行动计划 (Technical Debt Action Plan)

**创建日期**: 2025-12-05
**优先级**: 🔴 立即开始
**总工作量**: 198 小时 (5-6 周全职)
**目标完成**: 2026-01-16 (6 周)

---

## 快速参考：优先级矩阵

```
立即处理 (This Week)          第1阶段 (Week 1-2)       第2阶段 (Week 3-4)
├─ 凭证轮换 (2h)            ├─ 异常处理 (20h)      ├─ 大型文件重构 (40h)
├─ Git Hook (1h)            ├─ TODO 项完成 (20h)   ├─ 缓存系统统一 (12h)
└─ 创建项目 (1h)            └─ 合计: 42小时        └─ 合计: 52小时

第3阶段 (Week 5-6)           第4阶段 (Week 7-8)
├─ TypeScript 迁移 (40h)     ├─ 依赖项审计 (6h)
├─ 组件重构 (24h)           ├─ 配置统一 (4h)
├─ 测试覆盖 (12h)           ├─ 代码提取 (12h)
└─ 合计: 76小时              └─ 合计: 28小时
```

---

## 阶段 0: 立即行动 (今天)

### 任务 0.1: 凭证轮换 (Critical 🔴)
**工作量**: 2 小时
**风险**: 如不处理 = 安全漏洞

```bash
# 步骤 1: 识别所有泄露的凭证
# 找到: TDENGINE_PASSWORD, POSTGRESQL_PASSWORD, JWT_SECRET_KEY

# 步骤 2: 在每个服务轮换密码
# - TDengine: 修改 taosdata 用户密码
# - PostgreSQL: 修改 postgres 用户密码
# - JWT: 生成新的随机密钥 (openssl rand -hex 32)

# 步骤 3: 更新 .env 文件
TDENGINE_PASSWORD=<新密码>
POSTGRESQL_PASSWORD=<新密码>
JWT_SECRET_KEY=<新密钥>

# 步骤 4: 更新 CI/CD 密钥
# - GitHub Actions secrets
# - 环境变量配置
```

**检查清单**:
- [ ] 所有凭证已轮换
- [ ] 本地 .env 文件已更新
- [ ] CI/CD 密钥已更新
- [ ] 旧凭证已撤销

---

### 任务 0.2: 设置 Pre-Commit Hook (High 🟠)
**工作量**: 1 小时
**风险**: 防止未来凭证泄露

```bash
# 创建 .git/hooks/pre-commit
#!/bin/bash

echo "🔍 检查敏感信息..."

# 检查待提交文件
if git diff --cached | grep -E "PASSWORD|SECRET|API_KEY|TOKEN"; then
    echo "❌ 检测到敏感信息，提交被阻止"
    echo "💡 提示: 如果需要提交凭证，请:"
    echo "   1. 添加到 .gitignore"
    echo "   2. 或在 .env.example 中使用占位符"
    exit 1
fi

echo "✅ 敏感信息检查通过"
exit 0

# 使 Hook 可执行
chmod +x .git/hooks/pre-commit
```

**检查清单**:
- [ ] Hook 文件已创建
- [ ] Hook 已测试 (尝试提交包含 PASSWORD 的文件应被拒绝)

---

### 任务 0.3: 创建技术负债项目 (Medium 🟡)
**工作量**: 1 小时
**工具**: GitHub Issues / 任务管理工具

```markdown
# 创建项目: Technical Debt Remediation

## 标签定义
- tech-debt:critical  - 需要立即处理
- tech-debt:high      - 第2周内处理
- tech-debt:medium    - 第3-4周处理
- tech-debt:low       - 第5-8周处理

## 项目板
Backlog → In Progress → In Review → Done

## 成员角色
- 项目负责人: @负责人
- 后端开发: @开发者1
- 前端开发: @开发者2
```

**检查清单**:
- [ ] 项目已创建
- [ ] 标签已定义
- [ ] 成员已分配

---

## 阶段 1: 严重问题 (Week 1-2)
**总工作量**: 42 小时
**目标**: 解决所有阻塞性问题和安全风险

---

### 任务 1.1: 异常处理重构 (Critical 🔴)
**工作量**: 20 小时
**影响**: 消除 786 个过度宽泛的异常捕获

#### 1.1.1 创建异常类层次结构 (3 小时)

```python
# src/exceptions/__init__.py

class MyStocksException(Exception):
    """基础异常类"""
    pass

class NetworkError(MyStocksException):
    """网络连接错误"""
    pass

class DataSourceError(MyStocksException):
    """数据源不可用"""
    pass

class ValidationError(MyStocksException):
    """数据验证失败"""
    pass

class DatabaseError(MyStocksException):
    """数据库操作失败"""
    pass

class CacheError(MyStocksException):
    """缓存操作失败"""
    pass

class BusinessLogicError(MyStocksException):
    """业务逻辑错误"""
    pass

class ConfigurationError(MyStocksException):
    """配置错误"""
    pass
```

**子任务**:
- [ ] 定义异常类文件
- [ ] 添加文档字符串
- [ ] 创建异常映射表
- [ ] 添加单元测试

#### 1.1.2 批量替换异常处理 (15 小时)

**受影响的文件** (按优先级):

| 文件 | 次数 | 预计时间 | 状态 |
|------|------|---------|------|
| stock_search.py | 80 | 4h | ⏳ |
| market_data_service.py | 65 | 3h | ⏳ |
| cache_manager.py | 55 | 3h | ⏳ |
| indicators.py | 45 | 2h | ⏳ |
| database.py | 40 | 2h | ⏳ |
| 其他 (6 个文件) | 506 | 1h | ⏳ |

**替换模式**:

```python
# ❌ 之前
try:
    result = await operation()
except Exception as e:
    logger.error(f"Failed: {e}")
    return None

# ✅ 之后
try:
    result = await operation()
except NetworkError as e:
    logger.warning(f"Network issue: {e}")
    return await fallback_to_cache()
except ValidationError as e:
    logger.error(f"Invalid data: {e}")
    raise HTTPException(status_code=400, detail="Invalid request")
except DatabaseError as e:
    logger.error(f"Database error: {e}")
    return await fallback_to_mock_data()
```

**子任务**:
- [ ] stock_search.py (4h)
- [ ] market_data_service.py (3h)
- [ ] cache_manager.py (3h)
- [ ] indicators.py (2h)
- [ ] database.py (2h)
- [ ] 其他文件 (1h)

#### 1.1.3 测试和验证 (2 小时)

**子任务**:
- [ ] 单元测试异常捕获
- [ ] 集成测试错误场景
- [ ] 端到端测试失败恢复
- [ ] 性能回归测试 (确保没有性能下降)

**完成标准**:
- ✅ 零个 `except Exception` 剩余
- ✅ 所有异常都捕获特定类型
- ✅ 测试覆盖率 >= 80%
- ✅ 代码审查通过

---

### 任务 1.2: 完成 TODO 项 (Critical 🔴)
**工作量**: 20 小时
**影响**: 完成关键功能，移除安全隐患

#### 1.2.1 认证系统升级 (4 小时)

**当前状态**:
```python
# web/backend/app/api/auth.py
users_db = {}  # TODO: Replace with real database storage

def register_user(email: str, password: str):
    users_db[email] = password  # ❌ 明文存储！
```

**目标实现**:
```python
from src.models import User
from src.services import UserService

async def register_user(email: str, password: str) -> User:
    # ✅ 使用 ORM，密码加密，错误处理
    user = await UserService.create_user(email, password)
    return user

async def login(email: str, password: str) -> TokenResponse:
    # ✅ 验证密码，生成 JWT
    user = await UserService.authenticate(email, password)
    token = generate_jwt_token(user.id)
    return TokenResponse(access_token=token)
```

**子任务**:
- [ ] 创建 User 模型 (Pydantic/SQLAlchemy)
- [ ] 实现密码加密 (bcrypt)
- [ ] 创建 UserService
- [ ] 迁移现有用户数据
- [ ] 测试认证流程

**PR 名称**: `feat: Implement production-grade authentication system`

#### 1.2.2 实现实际数据获取 (6 小时)

**当前状态**:
```python
# web/backend/app/tasks/market_data.py
# TODO: Implement actual data fetching logic
async def fetch_market_data():
    return mock_data  # ❌ 仅返回模拟数据
```

**目标实现**:
```python
async def fetch_market_data(symbols: List[str]):
    # ✅ 实际 API 调用
    data_source = get_data_source(mode='production')

    results = []
    for symbol in symbols:
        try:
            data = await data_source.get_kline_data(symbol)
            results.append(data)
        except DataSourceError as e:
            logger.warning(f"Failed to fetch {symbol}: {e}")
            results.append(await get_fallback_data(symbol))

    return results
```

**子任务**:
- [ ] 选择数据源 (akshare/baostock/tushare)
- [ ] 实现数据验证
- [ ] 设置错误恢复 (回退)
- [ ] 添加速率限制
- [ ] 性能测试

**PR 名称**: `feat: Replace mock data with real market data sources`

#### 1.2.3 缓存机制实现 (4 小时)

**当前状态**:
```python
# web/backend/app/api/dashboard.py
# TODO: Implement cache mechanism
def get_dashboard_data():
    return expensive_calculation()  # ❌ 每次都计算
```

**目标实现**:
```python
async def get_dashboard_data(force_refresh: bool = False):
    # ✅ 使用缓存，支持强制刷新
    cache_key = "dashboard:main"

    if not force_refresh:
        cached = await cache.get(cache_key)
        if cached:
            return cached

    data = await expensive_calculation()
    await cache.set(cache_key, data, ttl=3600)  # 1小时过期
    return data
```

**子任务**:
- [ ] 使用统一缓存接口
- [ ] 设置 TTL 和过期策略
- [ ] 添加缓存统计
- [ ] 性能基准测试

**PR 名称**: `feat: Add caching layer to dashboard`

#### 1.2.4 其他 TODO 项 (6 小时)

| TODO 位置 | 工作量 | 优先级 |
|-----------|--------|--------|
| monitoring.py - 历史数据对比 | 2h | 中 |
| monitoring.py - 指标检测 | 2h | 中 |
| system.py - TDengine 检查 | 1h | 中 |
| 其他零散 TODO | 1h | 低 |

**完成标准**:
- ✅ 所有 TODO 注释已解决
- ✅ 功能完全实现
- ✅ 测试覆盖率 >= 80%
- ✅ 性能基准达到目标

---

## 阶段 2: 高优先级 (Week 3-4)
**总工作量**: 52 小时
**目标**: 改进代码质量和可维护性

### 任务 2.1: 重构大型文件 (40 小时)

#### 2.1.1 data_adapter.py 拆分 (16 小时)

**当前**: 1,880 行单个文件
**目标**: 4 个专用模块，每个 < 500 行

```
src/services/data_adapter/
├── __init__.py              (导出接口)
├── adapter_interface.py      (100 lines - 接口定义)
├── stock_adapter.py          (300 lines - 股票数据)
├── indicator_adapter.py      (300 lines - 指标数据)
├── market_adapter.py         (300 lines - 市场数据)
├── error_handling.py         (200 lines - 错误处理)
└── metrics.py               (100 lines - 指标记录)
```

**分解步骤**:
1. 提取接口定义 (2h)
2. 分离数据适配器 (6h)
3. 提取错误处理 (3h)
4. 测试和验证 (5h)

**PR 名称**: `refactor: Split data_adapter.py into focused modules`

#### 2.1.2 API 文件模块化 (16 小时)

**需要拆分的文件**:
- indicators.py (1,167 lines) → 3 个模块 (6h)
- data.py (1,167 lines) → 3 个模块 (6h)
- system.py (1,135 lines) → 3 个模块 (4h)

**示例**: indicators.py 拆分

```
src/api/indicators/
├── __init__.py
├── routes.py        (路由定义, ~300 lines)
├── schemas.py       (Pydantic 模型, ~200 lines)
├── service.py       (业务逻辑, ~400 lines)
└── calculator.py    (计算逻辑, ~300 lines)
```

#### 2.1.3 Mock 数据整合 (8 小时)

**当前**: unified_mock_data.py (957 lines)
**目标**: 分散到各模块的 `mock` 子目录

```
src/mock/
├── stock_mock.py
├── indicator_mock.py
├── market_mock.py
└── __init__.py (导出所有 mock 工厂)
```

**完成标准**:
- ✅ 所有文件 < 500 行
- ✅ 单一职责原则
- ✅ 代码覆盖率 >= 80%
- ✅ 性能没有下降

---

### 任务 2.2: 缓存系统统一 (12 小时)

**当前**: 3 个独立的缓存实现
**目标**: 1 个统一的接口，多个后端实现

#### 2.2.1 设计统一接口 (3 小时)

```python
# src/core/cache/interfaces.py

class ICache(Protocol):
    """缓存接口"""

    async def get(self, key: str) -> Optional[Any]:
        """获取值"""
        ...

    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """设置值"""
        ...

    async def delete(self, key: str) -> None:
        """删除值"""
        ...

    async def clear(self) -> None:
        """清空缓存"""
        ...

    async def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        ...
```

#### 2.2.2 合并实现 (6 小时)

```python
# src/core/cache/
├── __init__.py
├── interfaces.py     (接口定义)
├── memory_cache.py   (内存实现)
├── redis_cache.py    (Redis 实现)
└── factory.py       (工厂模式)

# 使用示例
cache = CacheFactory.create('memory', ttl=3600)
value = await cache.get('key')
await cache.set('key', value, ttl=3600)
```

#### 2.2.3 迁移和测试 (3 小时)

**子任务**:
- [ ] 替换 CacheManager 调用
- [ ] 替换 IndicatorCache 调用
- [ ] 添加单元测试
- [ ] 性能基准测试 (目标: +20% 性能)

**完成标准**:
- ✅ 单一缓存接口
- ✅ 代码重复减少 40%
- ✅ 性能提升 20%
- ✅ 覆盖率 >= 90%

---

## 阶段 3: 中等优先级 (Week 5-6)
**总工作量**: 76 小时

### 任务 3.1: TypeScript 迁移 (40 小时)

### 任务 3.2: 组件重构 (24 小时)

### 任务 3.3: 测试覆盖 (12 小时)

---

## 阶段 4: 优先级低 (Week 7-8)
**总工作量**: 28 小时

### 任务 4.1: 依赖项审计 (6 小时)
### 任务 4.2: 配置文件统一 (4 小时)
### 任务 4.3: 代码提取 (12 小时)
### 任务 4.4: Lint 配置 (6 小时)

---

## 周进度报告模板

```markdown
# 技术负债改进 - 第 X 周进度报告

## 完成的任务
- [ ] 任务 1.1.1: 异常类定义 (3h)
- [ ] 任务 1.1.2: 文件 A 异常处理 (4h)

## 本周完成工时
**预计**: 20h | **实际**: 18h | **完成度**: 90%

## 阻塞问题
- (如果有)

## 下周计划
- 继续任务 1.1.2 (剩余 3h)
- 开始任务 1.2.1 (4h)

## 指标
- 文件数 > 500 行: 10 → 8
- Exception 捕获数: 786 → 600+
- TODO 注释: 20 → 15
```

---

## 成功标准

### 第 1 阶段 (Week 1-2) ✅
- [ ] 零个凭证泄露风险
- [ ] 零个 `except Exception` (全部替换为具体类型)
- [ ] 所有关键 TODO 已完成
- [ ] 安全性: 🟢 通过

### 第 2 阶段 (Week 3-4) ✅
- [ ] 所有文件 < 500 行
- [ ] 缓存系统统一
- [ ] 性能提升 20%+
- [ ] 代码质量: 🟢 提升 40%

### 第 3 阶段 (Week 5-6) ✅
- [ ] 前端完全使用 TypeScript
- [ ] 测试覆盖率 >= 70%
- [ ] E2E 测试通过率 >= 95%
- [ ] 代码库清爽度: 🟢 显著改进

### 第 4 阶段 (Week 7-8) ✅
- [ ] 依赖项安全检查通过
- [ ] 配置文件统一
- [ ] Lint 配置完整
- [ ] 技术负债: 🟢 减少 70%

---

## 资源分配

### 推荐配置
```
投入: 2 个全职开发者
  - 开发者 A: 后端 (异常处理、大型文件重构、依赖审计)
  - 开发者 B: 前端 (TypeScript 迁移、组件重构、测试)

时间表: 6 周连续
  - Week 1-2: 严重问题
  - Week 3-4: 高优先级
  - Week 5-6: 中等优先级
  - Week 7-8: 优先级低 (可与其他工作并行)

预算: ~150-180 小时开发 + 20 小时审查 = 170-200 小时
ROI: 每月生产力提升 300+ 小时
```

---

## 风险缓解

| 风险 | 缓解策略 |
|------|---------|
| 回归问题 | 完整的测试覆盖和代码审查 |
| 性能下降 | 性能基准测试在每个阶段 |
| 生产中断 | 在开发分支上工作，逐步合并 |
| 团队知识差距 | 代码审查 + 知识共享会议 |

---

## 监控和防止

### 建立质量门槛

```python
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: file-size-check
        name: Check file size
        entry: python scripts/check-file-size.py
        language: python
        files: '\.py$'
        stages: [commit]

      - id: exception-check
        name: Check for bare Exception
        entry: grep -r "except Exception"
        language: system
        files: '\.py$'
        stages: [commit]
```

### CI/CD 检查清单

```yaml
# .github/workflows/quality-check.yml
name: Quality Checks
on: [pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Check file sizes
        run: python scripts/check-file-size.py --max-lines 500

      - name: Check exceptions
        run: grep -r "except Exception" src/ && exit 1 || exit 0

      - name: Coverage
        run: pytest --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## 持续改进

### 每月检查
- [ ] 技术负债指标评估
- [ ] 新增负债分类
- [ ] 优先级调整
- [ ] 改进计划更新

### 每季度回顾
- [ ] 大型改进效果评估
- [ ] ROI 计算
- [ ] 流程改进
- [ ] 下一季度目标设定

---

**最后更新**: 2025-12-05
**下次审查**: 2025-12-12 (1 周后)
**维护者**: 技术负债协调员
