# MyStocks Ruff 技术债务治理计划

> 生成日期: 2026-07-12 | **审核修正**: 2026-07-14
> 基准: `ruff check --select E,F,W,PT`（限定规则族）
> 总问题: 6,482 条（仅限 E/F/W/PT 规则族；全规则 `--select ALL` 为 224,093）
> 可自动修复: 1,381 条（安全规则）
> **作用域说明**: 本计划仅覆盖 **E/F/W/PT** 四个规则族。D（文档串 64k）、ANN（注解 21k）、RUF（unicode 19k）、T201（print 19k）、S101（assert 11k）等占总量 98% 的问题不在本轮范围内，需另行规划。

---

## 一、现状总览

### 问题分布

| 类别 | 数量 | 占比 | 可自动修 | 备注 |
|------|------|------|----------|------|
| archive/legacy-dot-archive | ~1,800 | 28% | ✅ no-op (已归档) | 归档代码，不修 |
| archive/legacy-root-archived | ~1,200 | 18% | ✅ no-op (已归档) | 归档代码，不修 |
| web/backend/tests/ | ~1,100 | 17% | ⚠️ 需评估 | 测试代码风格问题 |
| web/backend/app/ | ~900 | 14% | ⚠️ 需评估 | 生产代码 |
| web/frontend/scripts/ | ~700 | 11% | ⚠️ 需评估 | 脚本 |
| web/frontend/core.py | ~8 | <1% | ❌ 手动修 | 实际语法 bug |
| src/adapters/akshare/ | ~200 | 3% | ✅ per-file-ignores 已处理 | 运行时注入，非 bug |
| 其他 (src/interfaces, src/models 等) | ~500 | 8% | ⚠️ 需评估 | 生产代码 |

### 规则统计 (TOP 10)

| 规则 | 数量 | 说明 | 处理方式 |
|------|------|------|----------|
| F821 | **1,474** | 未定义名称（主为 akshare 注入模式） | ✅ per-file-ignores 范围需扩大 |
| F841 | **567** | 赋值但未使用变量 | ⚠️ 分区处理 |
| E722 | **165** | 裸 except | ⚠️ 需手动评估 |
| F401 | **111** | 未使用导入 | ⚠️ 分区处理 |
| invalid-syntax | **110** | 语法错误（Python 3.12 特性回退 3.9 兼容性） | ❌ 手动修复 |
| PT018 | **51** | 断言应拆分 | ✅ ruff --fix |
| W291 | **38** | 尾部空白 | ✅ ruff --fix (safe) |
| E701 | **24** | 多语句在一行 (冒号) | ✅ ruff --fix (unsafe) |
| F541 | **0** | f-string 无占位符（已被 fix=true 自动清空） | ✅ 无需处理 |
| PT022 | **0** | fixture 用 yield 代替 return | ✅ 无需处理 |
| **小计** | **~2,540** | — | 占总量 39% |
| 其他 E/F/W/PT | **~3,942** | 混合 | 按需 |

---

## 二、治理策略

### 核心原则

**生产代码修、归档代码不修、测试代码选择性修、脚本修**

### Phase 0: 归档代码排除 (预计 1 小时)

**目标**: 将 archive/ 下所有已归档代码从 ruff 扫描中排除

```
修改 pyproject.toml:
```toml
# 注意: 当前 exclude 中已含 ".archive"（带点号）
# 需新增 "archive/"（不带点号）以排除 docs/archive/
[tool.ruff]
exclude = [
    ".git",
    "archive",        # 新增：排除 docs/archive/ 下所有代码
    ".archive",
    "__pycache__",
    # ... 其他已有排除项
]
```
```

**验证**: ruff check 不再扫描 archive/，问题数降至 ~3,500

---

### Phase 1: 自动修复 Safe 规则 (预计 2 小时)

**目标**: 用 `ruff check --fix` 修所有安全规则

```
cd /opt/claude/mystocks_spec

# 1.1 安全自动修复 (不改变逻辑)
# 注意：F541 已被 fix=true 自动清空无需处理；PT022 不存在
ruff check --fix --select F401,W291,F841,E701 web/backend/app/ web/frontend/
# 拆分 PT018 断言（可用 --fix 处理）
ruff check --fix --select PT018 web/backend/tests/

# 1.2 拆分 PT018 断言 (手动确认每处)  
ruff check --select PT018 web/backend/tests/ > pt18_list.txt
# 然后逐个评估

# 1.3 修复 web/frontend/core.py 的 invalid-syntax (手动)
# 文件: web/frontend/core.py 第 309, 339, 341, 343 行
# 问题: logger.info("{...}") 应为 logger.info("...", args)
```

**预期修复**: ~1,500 条 → ~2,000 条剩余

---

### Phase 2: 后端生产代码修复 (预计 4 小时)

**目标**: 修 web/backend/app/ 下所有 active 生产代码

```
优先级排序:
  P0: E722 裸 except → 加 Exception 类型
  P1: F401 未用导入 → 删除
  P2: F841 未用变量 → 删除
  P3: E701 多语句一行 → ruff --fix --unsafe-fixes
  P4: PT018 断言拆分
```

**文件清单 (按问题数排序，基于 `ruff check --select E,F,W,PT --statistics`)**:
```
TOP-1 问题文件:
  src/interfaces/adapters/openstock/realtime_data.py    (F821 × 40+, akshare 注入)
  src/monitoring/async_monitoring_manager.py            (E722 × 12)
  web/backend/app/api/market/market_data_request.py     (E722 × 8)
  web/backend/app/services/ai_analytics_service.py      (F401 × 12)
  web/backend/app/api/auth/dependencies.py              (F841 × 6)
  ... 约 30 个文件
```

---

### Phase 3: 测试代码治理 (预计 3 小时)

**目标**: 修 tests/ 下 F401/F841/PT018 等不影响运行的代码风格

```
策略:
  - F401 未用导入: ruff --fix --select F401 web/backend/tests/
  - F841 未用变量: ruff --fix --select F841 web/backend/tests/
  - PT018 断言拆分: ruff --fix --select PT018 web/backend/tests/
  - 未覆盖的用 autoflake --in-place --remove-all-unused-imports 补充

手段:
  # 推荐方案：直接用 ruff 安全修复
  ruff check --fix --select F401,F841,PT018 web/backend/tests/
  
  # 替代方案（ruff 未覆盖时）：autoflake
  # autoflake --in-place --remove-all-unused-imports -r web/backend/tests/
  # 然后用 ruff 验证
```

**注意**: 测试代码修复需同步运行 `pytest tests/` 确认无回归

---

### Phase 4: 前端代码治理 (预计 2 小时)

**目标**: 修 web/frontend/ 下 active 代码 (不含 archive/)

```
重点文件:
  web/frontend/core.py          ← 8 个 invalid-syntax (手动修)
  web/frontend/scripts/         ← F541/F401 (ruff --fix)
  web/frontend/src/views/       ← PT018/F841 (手动评估)
```

**web/frontend/core.py 修复方案**:
```python
# 修复前 (第 309 行):
logger.info("⏱️ 自动刷新已启动，间隔: {self.dashboard_refresh_interval}秒")

# 修复后:
logger.info("⏱️ 自动刷新已启动，间隔: %s秒", self.dashboard_refresh_interval)

# 修复前 (第 339 行):
logger.info("✅ 监控数据已刷新 ({self.performance_metrics['update_count']})")

# 修复后:
logger.info("✅ 监控数据已刷新 (%s)", self.performance_metrics['update_count'])
```

---

### Phase 5: per-file-ignores 补完 (预计 1 小时)

**目标**: 为合理的"假阳性"添加 per-file-ignores

```
已配置:
  - tests/**/*.py → S101, ARG001, ARG002
  - src/adapters/akshare/**/*.py → F821

待评估（F821 实际 1,474 条，远多于计划的 ~200，需扩大覆盖）:
  - `src/adapters/akshare/**/*.py` → ✅ 已配置 F821
  - `src/interfaces/adapters/**/*.py` → 🔍 需评估（大量 akshare re-export）
  - `web/backend/app/api/akshare_market/**/*.py` → 🔍 需评估（注入模式）
  - `web/backend/app/services/data_source_factory/**/*.py` → 🔍 需评估（动态注入）
```

---

### Phase 6: CI 集成 (预计 1 小时)

**目标**: ruff 进入 CI 门禁

```
修改:
  .github/workflows/p0-quality-gate.yml → 加 ruff check
  scripts/ci/run_local_ci.py → 加 ruff check (本轮修改文件)

配置:
  [tool.ruff]
  # 收紧规则
  select = ["E", "W", "F", "PT", "I"]
  fix = false  # CI 中不自动修
```

---

## 三、预期产出

| 阶段 | 修复条数 | 剩余 | 耗时 | 验证方式 |
|------|----------|------|------|----------|
| Phase 0: archive 排除 | 3,000 (不修) | 3,500 | 1h | `ruff check` 不再扫描 archive/ |
| Phase 1: 自动修 Safe | 1,500 | 2,000 | 2h | `ruff check` + `git diff` 逐行审查 |
| Phase 2: 后端生产代码 | 900 | 1,100 | 4h | `ruff check` + `python -c "import <modified_module>"` |
| Phase 3: 测试代码 | 600 | 500 | 3h | `pytest tests/` |
| Phase 4: 前端代码 | 300 | 200 | 2h | `ruff check` + 手动 UI 冒烟 |
| Phase 5: ignores | 50 (忽略) | 150 | 1h | `ruff check` + 季度审核任务 |
| Phase 6: CI 集成 | — | — | 1h | CI 门禁通过 |
| **总计** | **~6,350** | **~150** | **14h** | |

修复率: **98%**

---

## 四、验收标准

```
✅ ruff check src/ web/ 通过 (不含 archive/)
✅ pytest tests/ 全绿 (测试代码修复后)
✅ python3 smoke_test.py 23/23 通过
✅ 每阶段独立提交，失败可 git revert 回滚
✅ per-file-ignores 登记至季度审核任务卡
✅ archive/ 代码从扫描中排除，不产生噪音
```

---

## 五、风险与对策

| 风险 | 概率 | 对策 |
|------|------|------|
| ruff --fix 改坏代码 | 中 | 每次 fix 后独立提交 → 跑 git diff + pytest；失败则 `git revert <commit>` |
| per-file-ignores 掩盖真 bug | 中 | 每个 ignore 写注释说明原因；登记至季度审核任务卡 |
| 测试 fixture yield→return 破坏 teardown | 中 | 修后跑 pytest 确认 |
| 修 F401 删除实际使用的导入 | 低 | 用 pyright 交叉验证 + `python -c "import <module>"` |

---

## 六、开始执行

```bash
# 1. 确认基准
cd /opt/claude/mystocks_spec
ruff check --statistics > ruff_baseline.txt

# 2. 逐 Phase 执行
# Phase 0
vim pyproject.toml  # 添加 archive/** 到 exclude
ruff check --statistics > ruff_after_p0.txt

# Phase 1
ruff check --fix --select F401,F541,W291,F841,PT022 web/backend/app/ web/frontend/
ruff check --statistics > ruff_after_p1.txt

# Phase 2-4: 按文件逐一处理
# Phase 5: 补 per-file-ignores
# Phase 6: CI 集成
```