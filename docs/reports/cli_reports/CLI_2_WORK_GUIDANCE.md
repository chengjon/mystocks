# CLI-2 工作指导 - 阻塞问题解决方案

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、执行清单或整改建议，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值、时间线和建议动作如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


**发布时间**: 2025-12-28 T+3h
**发布者**: 主CLI (Manager)
**目标**: 解决3个阻塞问题,恢复E2E测试执行

---

## 🔴 问题优先级

| 问题 | 严重程度 | 影响范围 | 预计修复时间 |
|------|---------|---------|------------|
| 1. ModuleNotFoundError | 🔴 阻塞级 | 后端服务无法启动 | 15分钟 |
| 2. SyntaxError | 🔴 阻塞级 | 后端服务无法启动 | 10分钟 |
| 3. API响应格式 | 🟡 警告级 | E2E测试失败 (11/18) | 30分钟 |

**总计修复时间**: ~1小时

---

## 问题1: ModuleNotFoundError 修复指南

### 📍 问题定位

**错误信息** (来自 `/tmp/backend_new.log` line 95-96):
```
File "/opt/claude/mystocks_phase6_e2e/web/backend/app/schemas/backtest_schemas.py", line 15, in <module>
    from web.backend.app.mock.unified_mock_data import get_backtest_data
ModuleNotFoundError: No module named 'web.backend.app'
```

**根本原因**: 使用了错误的绝对导入路径 `from web.backend.app.mock.unified_mock_data`

### ✅ 修复步骤

#### 步骤1: 修复 backtest_schemas.py (5分钟)

**文件**: `web/backend/app/schemas/backtest_schemas.py`
**行号**: 第15行

**当前代码** (错误):
```python
from web.backend.app.mock.unified_mock_data import get_backtest_data
```

**修复为** (正确):
```python
from app.mock.unified_mock_data import get_backtest_data
```

**操作命令**:
```bash
cd /opt/claude/mystocks_phase6_e2e

# 使用你喜欢的编辑器打开文件
vim web/backend/app/schemas/backtest_schemas.py
# 或
nano web/backend/app/schemas/backtest_schemas.py

# 定位到第15行,修改导入语句
# 保存文件
```

**验证修复**:
```bash
# 验证Python可以正确导入模块
cd /opt/claude/mystocks_phase6_e2e/web/backend
python3 -c "from app.schemas.backtest_schemas import BacktestRequest; print('✅ Import successful')"
```

---

## 问题2: SyntaxError 修复指南

### 📍 问题定位

**错误信息** (来自 `/tmp/backend_new.log` line 244-246):
```
File "/opt/claude/mystocks_phase6_e2e/src/core/data_manager.py", line 290
    self.logger.info("数据管理器初始化完成")
SyntaxError: expected 'except' or 'finally' block
```

**根本原因**: try块缺少except或finally子句

### ✅ 修复步骤

#### 步骤2: 检查并修复 data_manager.py (10分钟)

**文件**: `src/core/data_manager.py`
**行号**: 第285-295行附近

**需要查看的问题代码结构** (示例):
```python
# 问题结构示例 (需要在实际文件中确认)
try:
    # 一些代码
    self.logger.info("数据管理器初始化完成")
    # ❌ 缺少 except 或 finally 块
```

**操作步骤**:
```bash
cd /opt/claude/mystocks_phase6_e2e

# 1. 查看问题代码上下文
sed -n '285,295p' src/core/data_manager.py

# 2. 检查是否有未闭合的 try 块
grep -n "^try:" src/core/data_manager.py | tail -5

# 3. 检查第290行前后代码
awk 'NR>=285 && NR<=295' src/core/data_manager.py
```

**修复方案** (根据实际代码结构调整):

**方案A - 添加except块** (推荐):
```python
try:
    # 原有代码
    self.logger.info("数据管理器初始化完成")
except Exception as e:
    self.logger.error(f"数据管理器初始化失败: {e}")
    raise
```

**方案B - 添加finally块**:
```python
try:
    # 原有代码
    self.logger.info("数据管理器初始化完成")
finally:
    # 清理代码
    pass
```

**方案C - 如果try块不需要,移除try-except**:
```python
# 直接执行代码,不使用try-except
self.logger.info("数据管理器初始化完成")
```

**验证修复**:
```bash
# 验证Python语法正确
cd /opt/claude/mystocks_phase6_e2e
python3 -m py_compile src/core/data_manager.py
echo "✅ Syntax check passed"
```

---

## 问题3: API响应格式修复指南

### 📍 问题定位

**测试期望** (来自 `docs/reports/completion_reports/PHASE6_E2E_STATUS_SUMMARY.md`):
```json
{
  "databases": [
    {"name": "TDengine", ...},
    {"name": "PostgreSQL", ...}
  ]
}
```

**实际API返回**:
```json
{
  "data": {
    "tdengine": {...},
    "postgresql": {...},
    "summary": {...}
  }
}
```

### ✅ 修复步骤

#### 步骤3: 修改API端点响应格式 (30分钟)

**文件**: `web/backend/app/api/system.py`
**端点**: `GET /api/system/database/health`

**操作步骤**:
```bash
cd /opt/claude/mystocks_phase6_e2e/web/backend

# 1. 查找database/health端点
grep -n "database/health" app/api/system.py

# 2. 查看当前响应格式
# 假设端点在第XXX行
```

**修复代码模式** (需要根据实际代码调整):

```python
# 当前可能的实现
@router.get("/database/health")
async def get_database_health():
    """返回数据库健康状态"""
    tdengine_health = check_tdengine()
    postgresql_health = check_postgresql()

    return {
        "data": {
            "tdengine": tdengine_health,
            "postgresql": postgresql_health,
            "summary": {
                "overall_healthy": all([tdengine_health["healthy"], postgresql_health["healthy"]])
            }
        }
    }

# 修改为测试期望的格式
@router.get("/database/health")
async def get_database_health():
    """返回数据库健康状态 (E2E测试兼容格式)"""
    tdengine_health = check_tdengine()
    postgresql_health = check_postgresql()

    # 生成databases数组格式
    databases = [
        {
            "name": "TDengine",
            "healthy": tdengine_health.get("healthy", False),
            "host": tdengine_health.get("host", "127.0.0.1"),
            "port": tdengine_health.get("port", 6030),
            # ... 其他字段
        },
        {
            "name": "PostgreSQL",
            "healthy": postgresql_health.get("healthy", False),
            "host": postgresql_health.get("host", "127.0.0.1"),
            "port": postgresql_health.get("port", 5432),
            # ... 其他字段
        }
    ]

    return {
        "databases": databases,
        "summary": {
            "overall_healthy": all([tdengine_health["healthy"], postgresql_health["healthy"]]),
            "total": 2,
            "healthy_count": sum([db["healthy"] for db in databases])
        }
    }
```

**验证修复**:
```bash
# 重启后端服务
cd /opt/claude/mystocks_phase6_e2e/web/backend

# 停止现有服务
pkill -f "uvicorn.*app.main"

# 启动服务
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8020 --reload > /tmp/backend_new.log 2>&1 &

# 等待服务启动 (10秒)
sleep 10

# 测试API端点
curl -s http://localhost:8020/api/system/database/health | jq

# 验证响应包含databases数组
curl -s http://localhost:8020/api/system/database/health | jq '.databases'
```

---

## 🔄 完整修复工作流程

### 按顺序执行以下步骤:

```bash
# ============================================
# 步骤1: 修复 ModuleNotFoundError (15分钟)
# ============================================
cd /opt/claude/mystocks_phase6_e2e

# 1.1 修复 backtest_schemas.py
vim web/backend/app/schemas/backtest_schemas.py
# 第15行: from web.backend.app.mock.unified_mock_data
# 改为: from app.mock.unified_mock_data

# 1.2 验证修复
cd web/backend
python3 -c "from app.schemas.backtest_schemas import BacktestRequest; print('✅ Import OK')"

# ============================================
# 步骤2: 修复 SyntaxError (10分钟)
# ============================================
cd /opt/claude/mystocks_phase6_e2e

# 2.1 查看问题代码
sed -n '285,295p' src/core/data_manager.py

# 2.2 修复try-except结构
vim src/core/data_manager.py
# 添加except或finally块到第290行附近

# 2.3 验证语法
python3 -m py_compile src/core/data_manager.py
echo "✅ Syntax check passed"

# ============================================
# 步骤3: 修复API响应格式 (30分钟)
# ============================================
cd /opt/claude/mystocks_phase6_e2e/web/backend

# 3.1 查找并修改database/health端点
vim app/api/system.py
# 修改响应格式,添加databases数组

# 3.2 重启后端服务
pkill -f "uvicorn.*app.main"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8020 --reload > /tmp/backend_new.log 2>&1 &
sleep 10

# 3.3 验证API响应格式
curl -s http://localhost:8020/api/system/database/health | jq '.databases'

# ============================================
# 步骤4: 运行E2E测试验证 (15分钟)
# ============================================
cd /opt/claude/mystocks_phase6_e2e

# 4.1 运行架构优化E2E测试
pytest tests/e2e/test_architecture_optimization_e2e.py -v

# 4.2 检查通过率
# 目标: 从7/18 (38.9%) 提升到 ≥17/18 (94.4%)
```

---

## 📊 修复验证清单

完成修复后,请验证以下项目:

- [ ] **问题1修复**: `from app.mock.unified_mock_data import get_backtest_data`
- [ ] **问题1验证**: Python导入无错误
- [ ] **问题2修复**: try-except结构完整
- [ ] **问题2验证**: `python3 -m py_compile` 通过
- [ ] **问题3修复**: API返回 `databases` 数组
- [ ] **问题3验证**: `curl /api/system/database/health | jq '.databases'` 显示数组
- [ ] **后端服务**: 成功启动在 http://localhost:8020
- [ ] **E2E测试**: 通过率 ≥17/18 (94.4%)

---

## 🎯 修复后目标

| 指标 | 修复前 | 修复后目标 |
|------|--------|----------|
| 后端服务启动 | ❌ 失败 | ✅ 成功 |
| ModuleNotFoundError | ❌ 存在 | ✅ 已修复 |
| SyntaxError | ❌ 存在 | ✅ 已修复 |
| API响应格式 | ❌ 不匹配 | ✅ 匹配测试期望 |
| E2E测试通过率 | 7/18 (38.9%) | ≥17/18 (94.4%) |

---

## 📞 遇到问题时的处理

### 如果修复1后仍有导入错误:
```bash
# 检查PYTHONPATH
echo $PYTHONPATH

# 设置正确的PYTHONPATH
export PYTHONPATH=/opt/claude/mystocks_phase6_e2e/web/backend:$PYTHONPATH

# 或从web/backend目录运行
cd /opt/claude/mystocks_phase6_e2e/web/backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8020
```

### 如果修复2后仍有语法错误:
```bash
# 查看详细的语法错误信息
python3 -m py_compile src/core/data_manager.py -v

# 或使用pylint检查
pylint src/core/data_manager.py
```

### 如果API修复后测试仍失败:
```bash
# 查看详细的测试失败信息
pytest tests/e2e/test_architecture_optimization_e2e.py -v --tb=short

# 查看API实际响应
curl -s http://localhost:8020/api/system/database/health | jq '.'
```

---

## ✅ 完成后汇报

修复完成后,请更新 `docs/reports/completion_reports/PHASE6_E2E_STATUS_SUMMARY.md`:

```markdown
## 问题修复情况 (T+4h)

### 1. ModuleNotFoundError ✅
- 修复文件: `web/backend/app/schemas/backtest_schemas.py`
- 修复内容: 导入路径从 `from web.backend.app.mock` 改为 `from app.mock`
- 验证结果: ✅ Python导入成功

### 2. SyntaxError ✅
- 修复文件: `src/core/data_manager.py`
- 修复内容: 添加except块到try语句
- 验证结果: ✅ 语法检查通过

### 3. API响应格式 ✅
- 修复文件: `web/backend/app/api/system.py`
- 修复内容: database/health端点返回databases数组
- 验证结果: ✅ API响应格式匹配测试期望

## E2E测试结果

- 运行命令: `pytest tests/e2e/test_architecture_optimization_e2e.py -v`
- 通过率: XX/18 (XX%)
- 状态: ✅ 达到目标 (≥80%)
```

---

**请按照此指导独立完成修复,不要请求主CLI执行这些步骤。**

**主CLI的角色是提供指导,Worker CLI (你) 负责执行。**

---

*文档生成: 2025-12-28 T+3h*
*预计完成时间: 2025-12-28 T+4h*
