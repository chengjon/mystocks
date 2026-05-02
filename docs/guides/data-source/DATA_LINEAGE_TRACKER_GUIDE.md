# DataLineageTracker 使用说明

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

## 适用范围

本指南说明 `src/governance/lineage/tracker.py` 中新增的 `DataLineageTracker`。

它的定位是：

- 为 `optimize-data-source-v2` 提案补齐 governance-side 的专题血缘图能力
- 使用 `networkx.DiGraph` 在进程内构建 `source -> dataset -> transform -> destination` 链路
- 可选接入 `Neo4jLineageStore` 做持久化

它**不替换**仓库里现有的通用异步血缘系统：

- `src/data_governance/lineage.py`
- `src/core/data_source/lineage_integration.py`
- `web/backend/app/api/data_lineage.py`

当前 repo-truth 是两套能力并存：

- `src.data_governance.lineage`
  - 现有通用血缘模型、异步存储和 API 暴露
- `src.governance.lineage.tracker`
  - 本 change 新增的 governance-side 轻量专题血缘追踪器

## 核心对象

### `DataLineageTracker`

主要职责：

- `record_lineage()`
  - 记录单条数据链路
- `trace_lineage()`
  - 回溯指定 `data_id` 的 upstream / downstream / full_paths

### `Neo4jLineageStore`

主要职责：

- 作为可选持久化后端
- 当未提供 `uri/user/password` 或运行环境没有可用 Neo4j driver 时，默认 no-op
- 不能阻塞本地 `networkx` 主链路

## 最小示例

```python
from src.governance.lineage.tracker import DataLineageTracker

tracker = DataLineageTracker()

tracker.record_lineage(
    data_id="dataset.daily.000001",
    source={"id": "source.akshare", "type": "source", "name": "AkShare"},
    transformations=[
        {"id": "transform.normalize", "type": "transform", "name": "Normalize"},
        {"id": "transform.factorize", "type": "transform", "name": "Factorize"},
    ],
    destinations=[
        {"id": "storage.postgresql.daily_kline", "type": "storage", "name": "PostgreSQL"},
        {"id": "api.market.daily_kline", "type": "api", "name": "Market API"},
    ],
)

trace = tracker.trace_lineage("dataset.daily.000001")
```

预期链路结构：

```text
source.akshare
  -> dataset.daily.000001
  -> transform.normalize
  -> transform.factorize
  -> storage.postgresql.daily_kline
```

## `trace_lineage()` 返回语义

返回结构：

```python
{
    "data_id": "dataset.daily.000001",
    "upstream": ["source.akshare"],
    "downstream": ["api.market.daily_kline", "storage.postgresql.daily_kline"],
    "full_paths": [
        [
            "source.akshare",
            "dataset.daily.000001",
            "transform.normalize",
            "transform.factorize",
            "storage.postgresql.daily_kline",
        ]
    ],
    "exists": True,
}
```

其中：

- `upstream`
  - 指向该 `data_id` 的 root ancestors
- `downstream`
  - 从该 `data_id` 可达的 leaf descendants
- `full_paths`
  - 覆盖 `data_id` 的简单路径集合
- `exists`
  - 节点是否在当前图中存在

## 当前边界

- 当前 `Neo4jLineageStore` 是可选、非阻塞实现
- 当前测试覆盖了：
  - `networkx` 图构建
  - `trace_lineage()` 回溯
  - destination metadata dict 处理
  - 可选 store no-op / persist 调用
  - repo-local tracker + store 组合链路
- 当前**没有**证明：
  - live Neo4j 服务联通
  - 现有 `data_lineage` API 自动切到这条新 tracker
  - 生产环境大规模血缘图性能
