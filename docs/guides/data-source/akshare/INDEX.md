# AkShare Guide Family

> **导航说明**:
> 本目录用于承载 `expand-akshare-data-sources` 相关的 AkShare 专题文档，不是仓库共享规则或当前实现边界的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 [`architecture/STANDARDS.md`](../../../../architecture/STANDARDS.md)；若涉及当前实现状态，请再结合当前代码、OpenSpec 台账与验证结果核对。

## Current Entry Order

1. [`AKSHARE_MARKET_EXTENSION_GUIDE.md`](./AKSHARE_MARKET_EXTENSION_GUIDE.md)
   - 当前 AkShare 市场扩充接口的使用入口、已实现范围、更新频率与缓存边界
2. [`AKSHARE_MARKET_TROUBLESHOOTING.md`](./AKSHARE_MARKET_TROUBLESHOOTING.md)
   - 常见故障排查、同名函数探测与 repo-truth 门禁命令
3. [`AKSHARE_MARKET_MAINTENANCE.md`](./AKSHARE_MARKET_MAINTENANCE.md)
   - 版本兼容、增量扩展、门禁脚本入口和维护 checklist

## Gate Scripts

当前这条线的标准门禁命令是 wrapper：

```bash
python scripts/dev/quality_gate/run_akshare_market_gates.py \
  --output-dir /tmp/akshare-market-gates
```

默认会产出：

- `akshare-market-function-availability.json`
- `akshare-market-repo-truth-gate.json`
- `akshare-market-gates-summary.json`

如需拆分诊断，再分别运行两个叶子脚本。它们都只做校验和审计，不生成业务代码。

## Relationship To Historical Docs

- [`docs/api/AKSHARE_INTERFACE_MAPPING.md`](../../../api/AKSHARE_INTERFACE_MAPPING.md)
  - 历史快照 / 设计映射，不应直接当作当前实现事实
- [`docs/reports/AKSHARE_DATA_SOURCE_API_SUMMARY.md`](../../../reports/AKSHARE_DATA_SOURCE_API_SUMMARY.md)
  - 历史总结，不是当前 repo-truth
- [`docs/api/AKSHARE_MARKET_ENDPOINTS_REPO_TRUTH.md`](../../../api/AKSHARE_MARKET_ENDPOINTS_REPO_TRUTH.md)
  - 当前 change 范围下的专题 API 真相源
