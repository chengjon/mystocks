# AkShare 市场扩充接口故障排查

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

> **故障排查说明**:
> 本文件面向 `expand-akshare-data-sources` 的当前实现，用于快速定位“函数缺失 / 路由不通 / registry 漏配 / focused tests 失败”等常见问题。

## 1. 本地 `akshare` 缺少 canonical 同名函数

症状：

- 本地能 import `akshare`
- 但 `getattr(ak, "<function_name>")` 失败

排查：

```bash
python - <<'PY'
import akshare as ak
for name in [
    "stock_hot_follow_xq",
    "stock_board_change_em",
    "stock_changes_em",
]:
    print(name, hasattr(ak, name))
PY
```

处理原则：

- 默认只实现本地可确认存在的同名函数
- 仅当 gate 中存在已批准的官方改名映射时，才允许以 canonical 名称暴露运行时能力
- 当前已批准映射有三条：
  - `stock_dt_pool_em -> stock_zt_pool_dtgc_em`
  - `stock_strong_pool_em -> stock_zt_pool_strong_em`
  - `stock_new_em -> stock_zt_pool_sub_new_em`
- 当前已退役条目：
  - `stock_weak_pool_em`
- 除上述特例外，若同名函数不存在，不用相近函数替代并冒充完成

标准入口优先使用 wrapper：

```bash
python scripts/dev/quality_gate/run_akshare_market_gates.py \
  --output-dir /tmp/akshare-market-gates
```

如需只聚焦“本地有没有这个同名函数”，再单独运行探测叶子脚本：

```bash
python scripts/dev/quality_gate/collect_akshare_market_function_availability.py \
  --output /tmp/akshare-market-function-availability.json
```

读结果时重点看：

- `summary.available_functions`
- `summary.missing_functions`
- `summary.retired_functions`
- `summary.help_candidate_functions`
- `module_version`

说明：

- `help_candidate_functions` 只表示“当前本地 `akshare` 包里存在相近名字 / 相近语义的候选函数”
- 它不能直接把 `stock_news_main_cx` 自动等价成 OpenSpec 里的缺失同名函数
- `stock_zt_pool_dtgc_em`、`stock_zt_pool_strong_em` 与 `stock_zt_pool_sub_new_em` 现在是已批准映射，分别只对 `stock_dt_pool_em`、`stock_strong_pool_em` 与 `stock_new_em` 生效；其余候选仍停留在 advisory 状态
- `retired_functions` 表示该 canonical target 已被业务正式移出当前 runtime scope，不再要求 registry / adapter / route / focused tests 工件
- 若要把其它候选从 advisory 升级为“接受官方改名函数”，必须单独走一批方案变更与门禁回写
- `stock_zt_pool_previous_em`、`stock_zt_pool_zbgc_em` 属于已考虑的邻接 pool 能力，但当前 OpenSpec 第 6 节没有对应任务项

## 2. 路由存在但 commit hook 报 `UnifiedResponse` guard

症状：

- 提交时 `UnifiedResponse contract guard` 失败

当前推荐做法：

- 新增端点优先放入独立、guard-compliant 的路由文件
- 为新端点显式声明 `response_model=UnifiedResponse[Dict[str, Any]]`
- 避免为了一次小批次顺手改整份历史旧路由文件

## 3. focused tests 通过，但历史 `part1.py` 大面积失败

症状：

- `tests/adapters/test_akshare_adapter/test_akshare_market_data_adapter_methods/part1.py` 大面积报 async / fixture 基线问题

处理原则：

- 视为历史坏基线
- 不在一次小批次里为了新接口重构整份旧文件
- 当前 change 的验证证据应优先放在 focused tests

## 4. route test 返回 404

先确认：

1. `web/backend/app/api/akshare_market/sentiment_monitor.py` 存在
2. `web/backend/app/api/akshare_market/__init__.py` 已 `include_router(sentiment_monitor_router)`
3. 实际请求路径是 `/api/akshare/market/...`

## 5. 推荐验证命令

```bash
python scripts/dev/quality_gate/run_akshare_market_gates.py \
  --output-dir /tmp/akshare-market-gates
```

默认产物：

- `/tmp/akshare-market-gates/akshare-market-function-availability.json`
- `/tmp/akshare-market-gates/akshare-market-repo-truth-gate.json`
- `/tmp/akshare-market-gates/akshare-market-gates-summary.json`

如需拆分定位，再分别运行：

```bash
python scripts/dev/quality_gate/collect_akshare_market_function_availability.py \
  --output /tmp/akshare-market-function-availability.json
```

```bash
python scripts/dev/quality_gate/validate_akshare_market_repo_truth.py \
  --output /tmp/akshare-market-repo-truth-gate.json
```

```bash
pytest \
  tests/unit/adapters/test_akshare_stock_sentiment_incremental.py \
  tests/backend/test_akshare_market_additional_routes.py \
  tests/api/file_tests/test_akshare_market_api.py \
  -q --no-cov
```

```bash
python -m py_compile \
  src/adapters/akshare/market_adapter/stock_sentiment.py \
  web/backend/app/api/akshare_market/__init__.py \
  web/backend/app/api/akshare_market/sentiment_monitor.py
```
