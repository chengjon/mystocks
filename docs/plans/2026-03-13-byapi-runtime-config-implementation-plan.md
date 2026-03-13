# Byapi Runtime Config Implementation Plan

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
