# AkShare 市场扩充接口故障排查

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

> **故障排查说明**:
> 本文件面向 `expand-akshare-data-sources` 的当前实现，用于快速定位“函数缺失 / 路由不通 / registry 漏配 / focused tests 失败”等常见问题。

## 1. 本地 `akshare` 缺少同名函数

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

- 只实现本地可确认存在的同名函数
- 若同名函数不存在，不用相近函数替代并冒充完成

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
