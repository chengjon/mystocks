# expand-akshare-data-sources 工作交接文档

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **交接目的**:
> 本文档面向新的工作条线，用于接手 `expand-akshare-data-sources` 的后续开发与对账。
> 它不是仓库共享规则的唯一事实来源；共享规则仍以 `architecture/STANDARDS.md`、`openspec/AGENTS.md` 和当前代码为准。

> **适用环境**:
> 当前主工作环境是 `WSL 上的 Ubuntu 24.04.4 LTS`。

**最后更新**: 2026-05-03  
**对应 OpenSpec change**: `expand-akshare-data-sources`  
**当前进度**: `61/77 tasks`

---

## 1. 当前状态概览

当前 change 的 repo-truth 状态是：

- 第 `1-5` 节已完成
- 第 `6` 节只完成了本地 `akshare` 当前可确认存在的子集
- 第 `7` 节只完成了聚合入口、已实现路由注册和专题文档
- 第 `8` 节仍未收口
- 第 `9` 节专题文档家族已落地

当前最重要的现实边界：

- 这条线现在不是“把所有 6.x 一口气勾完”
- 而是“只要本地 `akshare` 真有同名函数，就按 adapter + API + registry + tests + docs + tasks 逐个闭环”
- 如果本地 `akshare` 没有同名函数，就继续保持未完成，不能拿相近接口顶替

---

## 2. 当前已完成范围

### 2.1 已完整闭合的阶段

- 第 `1` 节：市场总貌
- 第 `2` 节：个股信息
- 第 `3` 节：资金流向
- 第 `4` 节：预测和分析
- 第 `5` 节：板块和行业

### 2.2 第 6 节当前已实现子集

当前 repo 内已闭合的第 6 节子项是：

- `6.1` `stock_hot_follow_xq`
- `6.2` `stock_board_change_em`
- `6.4` `stock_zt_pool_em`
- `6.8` `stock_changes_em`

这些实现的主落点是：

- adapter: `src/adapters/akshare/market_adapter/stock_sentiment.py`
- API: `web/backend/app/api/akshare_market/sentiment_monitor.py`
- registry: `config/data_sources_registry.yaml`
- focused tests:
  - `tests/unit/adapters/test_akshare_stock_sentiment_incremental.py`
  - `tests/backend/test_akshare_market_additional_routes.py`
  - `tests/api/file_tests/test_akshare_market_api.py`

### 2.3 第 6 节当前仍未完成子集

截至本次交接，本地 `akshare` 环境仍未检出以下同名函数：

- `6.3` `stock_news_main_em`
- `6.5` `stock_dt_pool_em`
- `6.6` `stock_strong_pool_em`
- `6.7` `stock_weak_pool_em`
- `6.9` `stock_new_em`

因此这几项当前继续保持未完成。

---

## 3. 本地 akshare 可用性快照

2026-05-03 在当前 `WSL 上的 Ubuntu 24.04.4 LTS` 环境复核结果：

```text
stock_hot_follow_xq=True
stock_board_change_em=True
stock_news_main_em=False
stock_zt_pool_em=True
stock_dt_pool_em=False
stock_strong_pool_em=False
stock_weak_pool_em=False
stock_changes_em=True
stock_new_em=False
```

这意味着：

- 新条线接手后，第一步不是写代码，而是先重新确认本地 `akshare` 版本是否发生变化
- 只有 `False` 变成 `True` 的接口，才进入实现批次

---

## 4. 新条线优先阅读的文件

### 4.1 台账与真相源

- `openspec/changes/expand-akshare-data-sources/tasks.md`
- `docs/api/AKSHARE_MARKET_ENDPOINTS_REPO_TRUTH.md`
- `docs/guides/akshare/AKSHARE_MARKET_EXTENSION_GUIDE.md`

### 4.2 代码入口

- `src/adapters/akshare/market_adapter/adapter.py`
- `src/adapters/akshare/market_adapter/stock_sentiment.py`
- `web/backend/app/api/akshare_market/sentiment_monitor.py`
- `config/data_sources_registry.yaml`

### 4.3 测试入口

- `tests/unit/adapters/test_akshare_stock_sentiment_incremental.py`
- `tests/backend/test_akshare_market_additional_routes.py`
- `tests/api/file_tests/test_akshare_market_api.py`

---

## 5. 近期最相关提交

建议新条线先看这几笔提交，按从近到远阅读：

- `c80288668` `akshare: use examples for zt pool query`
- `fbbe42438` `akshare: add zt pool endpoint`
- `a2c2bd95d` `openspec: fix akshare route ledger paths`
- `584355dfd` `docs: add akshare market guide family`
- `5d41acfd6` `akshare: add sentiment and change endpoints`
- `0d780e2f0` `openspec: clarify akshare remaining ledger`

这几笔基本覆盖了：

- 第 6 节当前 repo-truth 子集
- 专题文档入口
- 台账与实际代码对齐的关键修正

---

## 6. 新条线必须遵守的 repo-truth 规则

### 6.1 只认同名函数

如果本地 `akshare` 没有目标同名函数：

- 不要用“语义接近”的其他 AkShare 函数替代
- 不要拿 `byapi`、`wencai`、历史脚本或别的 provider 旁证来勾任务
- 只允许把任务保持未完成，或补充 repo-truth 注释

### 6.2 每个接口必须 6 件套闭环

每实现一个新接口，至少同时更新：

1. adapter 方法
2. API 路由
3. `config/data_sources_registry.yaml`
4. focused tests
5. 专题文档
6. OpenSpec 台账

### 6.3 不要提前勾大项

在 `6.3 / 6.5 / 6.6 / 6.7 / 6.9` 仍未实现前：

- 不要勾 `6.10`
- 不要勾 `6.11`
- 不要勾 `6.12`

同理，当前也不能把下面几项强行收口：

- `7.2`
- `7.4`
- `7.5`
- `8.1-8.5`

### 6.4 当前缓存与批量能力还不能拔高

尤其注意：

- `tests/api/file_tests/test_akshare_market_api.py` 里的 `test_smart_cache_integration()` 仍是 placeholder 性质
- 它不能当作 `7.4` 已完成的证据
- 当前也没有面向第 6 节剩余接口的多股票批量请求闭环，因此 `7.5` 也不能提前勾选

---

## 7. 推荐接手顺序

### 7.1 第一步：先确认本地函数可用性

推荐先跑一遍：

```bash
python - <<'PY'
import akshare as ak
names = [
    'stock_hot_follow_xq',
    'stock_board_change_em',
    'stock_news_main_em',
    'stock_zt_pool_em',
    'stock_dt_pool_em',
    'stock_strong_pool_em',
    'stock_weak_pool_em',
    'stock_changes_em',
    'stock_new_em',
]
for name in names:
    print(f"{name}={hasattr(ak, name)}")
PY
```

### 7.2 第二步：如果有新函数可用，只做单接口微批次

建议一次只做一个接口，例如：

- 先只做 `stock_dt_pool_em`
- 单独跑 targeted tests
- 单独更新 docs / tasks
- 单独提交

不要把多个新接口混成一个大批次。

### 7.3 第三步：只有第 6 节全部闭合后，才看 6.10-6.12 / 7.x / 8.x

推荐顺序：

1. 先清 `6.3 / 6.5 / 6.6 / 6.7 / 6.9`
2. 再收 `6.10 / 6.11 / 6.12`
3. 再判断 `7.2 / 7.4 / 7.5`
4. 最后再推进 `8.x`

---

## 8. 推荐验证命令

每个新增接口至少跑：

```bash
pytest tests/unit/adapters/test_akshare_stock_sentiment_incremental.py -q --no-cov
pytest tests/backend/test_akshare_market_additional_routes.py -q --no-cov
pytest tests/api/file_tests/test_akshare_market_api.py -q --no-cov
python -m py_compile src/adapters/akshare/market_adapter/stock_sentiment.py web/backend/app/api/akshare_market/sentiment_monitor.py
openspec validate expand-akshare-data-sources --strict
```

如果只改了某一个新增路由，优先先跑更窄的 targeted test，再补整组。

---

## 9. 提交流程与工作树注意事项

当前仓库工作树很脏，存在大量既有 staged / unstaged 改动。

因此新条线必须：

- 不要 reset / revert 别人的改动
- 只做路径限定提交
- 提交前先 stage 自己这批路径
- 再跑 `gitnexus_detect_changes(scope=\"staged\")`

注意：

- staged-scope 的 GitNexus 结果当前会持续被仓库里其他既有 staged 内容污染
- 但最近多批次的 risk level 一直是 `low`
- 所以它目前只能作为风险提醒，不能当作“只包含你这批文件”的精确清单

---

## 10. 交接结论

这条新线当前最合适的目标，不是“想办法把 61/77 快速刷完”，而是：

- 先重新确认本地 `akshare` 版本
- 若有新的同名函数出现，再逐个做 end-to-end 微批次闭环
- 若函数仍不存在，就继续保持台账未完成，不要伪造完成度

一句话概括：

**`expand-akshare-data-sources` 现在已经从“大范围接入”阶段进入“本地 akshare 函数可用性驱动的精细收口阶段”。**
