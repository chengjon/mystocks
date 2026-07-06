# CI 基线失败登记

> **用途**：记录已知、与本仓库代码改动无关、后置治理的 CI 失败。新增条目仅要求写清根因 + 触发 PR，**不新增治理流程**。
> **维护规则**：每次合并 PR 时若 CI 出现新的非自身原因失败，加一行；条目被修复时画删除线 + 修复 PR 链接，不要直接删行。
> **最后更新**：2026-07-06

---

## 当前活跃条目

### 1. `api-discovery-test` — PostgreSQL service container `role "root" does not exist`

- **现象**：workflow `API Automation & Discovery Tests` 在 service container PostgreSQL 17 启动后持续报 `FATAL: role "root" does not exist`，每 10 秒重试一次直到 job 超时，最终 failure。
- **根因**：GitHub Actions service container 默认以 `root` 用户连接 PostgreSQL，但官方 postgres 镜像初始化的角色是 `postgres`，service container 配置里没设置 `POSTGRES_USER=root` 或等价 connection override。
- **关联 PR**：
  - PR #490（合并时 11 项失败之一）
  - PR #493（合并时 2 项失败之一）
- **影响范围**：任何触发该 workflow 的 PR 都会失败；与本 PR 改动无关。
- **建议修复方向**：workflow yaml 加 `env: POSTGRES_USER: postgres`（或 `POSTGRES_USER: root`）+ 对应 `PGUSER`/`USER` 在连接客户端侧；属 CI 基础设施修复，与代码改动无关。
- **优先级**：低（不阻塞任何业务路径，所有受影响 PR 可走 admin merge）

---

### 2. `stable-suite` — PostgreSQL 15 service container `role "root" does not exist`

- **现象**：workflow `stable-suite` 同样的 service container 故障，PostgreSQL 15。
- **根因**：与 #1 相同，不同 workflow、不同 PG 版本，相同 service container 配置缺陷。
- **关联 PR**：PR #493（合并时 2 项失败之一）
- **影响范围**：任何触发该 workflow 的 PR 都会失败；与本 PR 改动无关。
- **建议修复方向**：同 #1，service container 增加 `POSTGRES_USER` 配置。
- **优先级**：低（与 #1 同源，建议同时修复）

---

## 历史记录（已修复 / 已归档）

_（暂无；条目被修复时在此处画删除线 + 修复 PR 链接，不要直接删行。）_

---

## 添加新条目的规则

1. 只在 PR 合并后、CI 仍有失败时新增。
2. 必须写：现象 / 根因 / 关联 PR / 影响范围 / 建议修复方向 / 优先级。
3. **不**为新条目创建 OpenSpec 提案、任务卡、治理流程。
4. 修复完成后在「历史记录」区画删除线 + 引用修复 PR，保留审计痕迹。
