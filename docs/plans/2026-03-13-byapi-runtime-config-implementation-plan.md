# Byapi Runtime Config Implementation Plan

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、任务方案或执行矩阵，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值和时间线如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 让 `ByapiAdapter` 默认走 `https` 并优先读取运行时环境变量，恢复当前 Byapi 可用性而不把密钥写入仓库。

**Architecture:** 仅修改 `ByapiAdapter` 的初始化默认值解析逻辑，保持显式传参优先。测试覆盖默认行为和环境变量覆盖，运行时用临时环境变量做真实探针。

**Tech Stack:** Python, pytest, requests

---

### Task 1: 更新 Byapi 单测为新默认行为

**Files:**
- Modify: `tests/unit/adapters/test_byapi_adapter_basic.py`
- Modify: `tests/adapters/test_byapi_adapter.py`

**Step 1: Write the failing test**

- 让默认初始化期望值改为 `https://api.biyingapi.com`
- 增加“默认读取 `BYAPI_KEY` / `BYAPI_BASE_URL`”测试

**Step 2: Run test to verify it fails**

Run:

```bash
PYTHONPATH=/opt/claude/mystocks_spec PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest --noconftest -p no:cacheprovider -o addopts='' tests/unit/adapters/test_byapi_adapter_basic.py -q
```

**Step 3: Write minimal implementation**

- 修改 `src/adapters/byapi_adapter.py`

**Step 4: Run test to verify it passes**

Run the same test command.

### Task 2: 真实验证 Byapi / Tushare

**Files:**
- Modify: `src/adapters/byapi_adapter.py`

**Step 1: Verify Byapi with temporary env**

```bash
BYAPI_KEY=... python - <<'PY'
from src.adapters.byapi_adapter import ByapiAdapter
df = ByapiAdapter().get_stock_list()
print(len(df))
PY
```

**Step 2: Verify Tushare with temporary env**

```bash
TUSHARE_TOKEN=... python - <<'PY'
from src.adapters.tushare_adapter import TushareDataSource
ds = TushareDataSource()
print(type(ds).__name__)
PY
```

**Step 3: Run focused regression**

```bash
PYTHONPATH=/opt/claude/mystocks_spec PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest --noconftest -p no:cacheprovider -o addopts='' tests/unit/adapters/test_byapi_adapter_basic.py tests/unit/adapters/test_tushare_adapter_basic.py -q
```
