# CI 基线失败登记

> **用途**：记录已知、与本仓库代码改动无关、后置治理的 CI 失败。新增条目仅要求写清根因 + 触发 PR，**不新增治理流程**。
> **维护规则**：每次合并 PR 时若 CI 出现新的非自身原因失败，加一行；条目被修复时画删除线 + 修复 PR 链接，不要直接删行。
> **最后更新**：2026-07-07

---

## 当前活跃条目

### 1. `api-discovery-test` — `numpy.long` AttributeError 启动失败

- **现象**：workflow `API Automation & Discovery Tests` 的 `Start Backend Service` 步骤在 import 阶段崩溃，traceback：
  ```
  File ".../sklearn/metrics/_ranking.py", line ..., in <module>
      from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
  AttributeError: module 'numpy' has no attribute 'long'. Did you mean: 'log'?
  ```
  backend 进程 `Process completed with exit code 1`。
- **根因**：`web/backend/requirements.txt` 写的是 `numpy>=1.24.0`（无上限），CI 里 pip 解析到 `numpy-2.5.1` 安装；但当前 backend 调用链（经 sklearn 旧版本）仍使用 numpy 1.x 的 `numpy.long`，该属性在 numpy 1.20 弃用、1.24+ 移除、2.x 完全不存在。**与 PostgreSQL service container 无关**——PG 配置正确（`POSTGRES_USER=postgres`），service container 启动正常；后端在 import 阶段就崩了，根本没到 DB 连接那一步。
- **关联 PR**：
  - PR #490（合并时 11 项失败之一）
  - PR #493（合并时 2 项失败之一）
  - PR #494（合并时 2 项失败之一）
- **影响范围**：任何触发 `api-automation-discovery.yml` 的 PR 都会失败；与本 PR 改动无关。
- **建议修复方向**：在 `web/backend/requirements.txt` 锁定 `numpy>=1.24,<2`（或更严格的 `numpy==1.26.*`）+ 同步锁 sklearn 兼容版本；治本则迁移代码里的 `numpy.long` 调用。属依赖版本漂移问题，与 PR 改动无关。
- **优先级**：中（影响 backend 起服务的所有 CI workflow，建议尽快治理）

---

### 2. `stable-suite` — numpy/scipy 版本冲突导致 backend 起不来

- **现象**：workflow `stable-suite`（位于 `e2e-test.yml`）在 `Wait for services` 步骤反复 `curl: (7) Failed to connect to localhost port 8020 ... Couldn't connect to server`，每秒重试 60 次后 `Process completed with exit code 124`（timeout）。
- **根因**：该 workflow 的 `Install backend dependencies` 步骤先装了 `numpy==1.26.4`（来自 `/tmp/backend-requirements-ci.txt` pin），随后又装了 `scipy 1.18.0`，pip 报警告：
  ```
  scipy 1.18.0 requires numpy<2.8,>=2.0.0, but you have numpy 1.26.4 which is incompatible.
  ```
  版本冲突下 import 失败，backend 进程没起来 → `localhost:8020` 永远连不上 → curl 直到 timeout。**与 PostgreSQL service container 无关**——同样是 numpy/scipy 依赖漂移问题。
- **关联 PR**：
  - PR #493（合并时 2 项失败之一）
  - PR #494（合并时 2 项失败之一）
- **影响范围**：任何触发 `e2e-test.yml` (stable-suite job) 的 PR 都会失败；与本 PR 改动无关。
- **建议修复方向**：统一 numpy/scipy 版本契约。要么 `numpy>=2, scipy>=1.18` 并升级代码移除 `numpy.long`；要么 `numpy<2, scipy<1.13` 并 pin 到老版本。建议跟 #1 一起治理。
- **优先级**：中（与 #1 同源，建议同时修复）

---

## 历史记录（已修复 / 已归档）

_（暂无；条目被修复时在此处画删除线 + 修复 PR 链接，不要直接删行。）_

---

## 添加新条目的规则

1. 只在 PR 合并后、CI 仍有失败时新增。
2. 必须写：现象 / 根因 / 关联 PR / 影响范围 / 建议修复方向 / 优先级。
3. **不**为新条目创建 OpenSpec 提案、任务卡、治理流程。
4. 修复完成后在「历史记录」区画删除线 + 引用修复 PR，保留审计痕迹。

---

## 勘误记录

- **2026-07-07 (PR #495)**：PR #494 首次登记这两个条目时，根因被错记为 "PostgreSQL service container `role root does not exist`"。错误源于上个会话的总结摘要（context compaction），未对照实际失败日志就写入登记。本次 PR 重新对照 `gh run view --log-failed` 的真实输出，将根因更正为 numpy/scipy 依赖版本漂移：失败签名分别是 `AttributeError: module 'numpy' has no attribute 'long'`（#1）和 `scipy 1.18.0 requires numpy>=2.0.0, but you have numpy 1.26.4`（#2）。PostgreSQL service container 配置（`POSTGRES_USER=postgres`）实际是正确的，无需修改。
