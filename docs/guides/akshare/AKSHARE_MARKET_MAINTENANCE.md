# AkShare 市场扩充接口维护手册

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

> **维护手册说明**:
> 本文件用于约束后续如何继续维护 `expand-akshare-data-sources`，重点是版本兼容、接口补齐和 repo-truth 文档同步。

## 1. 版本兼容原则

当前维护原则非常保守：

- 以当前本地安装的 `akshare` 版本为准
- 只对“已确认存在的同名函数”建 adapter / API / registry / tests 闭环
- 发现同名函数缺失时，先记为 gap，再决定是否升级 `akshare` 或调整 OpenSpec scope

## 2. 新增一个接口时必须同步的文件

最小闭环：

1. `src/adapters/akshare/market_adapter/*.py`
2. `web/backend/app/api/akshare_market/*.py`
3. `config/data_sources_registry.yaml`
4. focused tests
5. `openspec/changes/expand-akshare-data-sources/tasks.md`
6. `docs/api/AKSHARE_MARKET_ENDPOINTS_REPO_TRUTH.md`
7. 本 guide family

## 3. 推荐扩展顺序

1. 先确认本地 `akshare` 是否存在同名函数
2. 再写 adapter 方法
3. 再加独立 / guard-compliant 路由
4. 再补 registry
5. 再补 focused tests
6. 最后回写 OpenSpec 与文档

## 4. 维护 checklist

- [ ] 同名 AkShare 函数在本地环境存在
- [ ] adapter 返回列名已标准化
- [ ] 新路由通过 `UnifiedResponse` guard
- [ ] registry 已补 `quality_rules`
- [ ] focused tests 通过
- [ ] OpenSpec 勾选只覆盖当前仓库事实
- [ ] 文档已说明“已实现 / 未实现 / 历史快照”边界
