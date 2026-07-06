# CI 基线失败登记

> **用途**：记录已知、与本仓库代码改动无关、后置治理的 CI 失败。新增条目仅要求写清根因 + 触发 PR，**不新增治理流程**。
> **维护规则**：每次合并 PR 时若 CI 出现新的非自身原因失败，加一行；条目被修复时画删除线 + 修复 PR 链接，不要直接删行。
> **最后更新**：2026-07-07

---

## 当前活跃条目

### 1. `api-discovery-test` — CI 安装 sklearn 1.9.0 调用 `numpy.long` 启动失败

- **现象**：workflow `API Automation & Discovery Tests` 的 `Start Backend Service` 步骤在 import 阶段崩溃，traceback：
  ```
  File ".../sklearn/metrics/_ranking.py", line ..., in <module>
      from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
  AttributeError: module 'numpy' has no attribute 'long'. Did you mean: 'log'?
  ```
  backend 进程 `Process completed with exit code 1`。
- **根因**：CI workflow（`.github/workflows/api-automation-discovery.yml`）的 `Install Backend Dependencies` 步骤在仓库根目录执行 `pip install -r requirements.txt`，读到的是**仓库根 `requirements.txt`**（不是 `web/backend/requirements.txt`）。仓库根 requirements 写的是 `numpy>=1.24.0`（无上限）+ `cudf-cu12>=25.10.0` + `cuml-cu12>=25.10.0`，pip 解析时把 `cuml-cu12` 的传递依赖 `scikit-learn-1.9.0 + scipy-1.18.0 + numpy-2.4.6` 整套拉进来；sklearn 1.9.0 在调用 numpy 1.x 的 `numpy.long`（1.24+ 已移除、2.x 完全不存在），import 阶段就崩。仓库代码本身 `grep np\.long|numpy\.long` = 0 处，**问题不在我们代码**，而在 RAPIDS 链 + sklearn 兼容性。**与 PostgreSQL service container 无关**——PG 配置正确（`POSTGRES_USER=postgres`），service container 启动正常；后端在 import 阶段就崩了，根本没到 DB 连接那一步。
- **关联 PR**：
  - PR #490（合并时 11 项失败之一）
  - PR #493（合并时 2 项失败之一）
  - PR #494（合并时 2 项失败之一）
- **影响范围**：任何触发 `api-automation-discovery.yml` 的 PR 都会失败；与本 PR 改动无关。
- **建议修复方向**：仓库根 `requirements.txt` 把 `numpy>=1.24.0` 改为 `numpy>=1.24,<2`（与 `web/backend/requirements.txt` 的 `numpy==1.26.4` pin 对齐），或者干脆在 CI workflow 里读 `web/backend/requirements.txt` 而非根 requirements；治本路径是审计是否真的需要 `cudf-cu12`/`cuml-cu12` 这条 RAPIDS GPU 链（量化个人本地部署，CLAUDE.md 1.1.1 已界定"非企业级"，GPU 加速应作为可选依赖而非默认拉满）。属依赖版本漂移 + CI 安装路径错配问题，与 PR 改动无关。
- **优先级**：中（影响 backend 起服务的所有 CI workflow，建议尽快治理）

---

### 2. `stable-suite` — CI 安装 numpy/scipy 版本冲突导致 backend 起不来

- **现象**：workflow `stable-suite`（位于 `e2e-test.yml`）在 `Wait for services` 步骤反复 `curl: (7) Failed to connect to localhost port 8020 ... Couldn't connect to server`，每秒重试 60 次后 `Process completed with exit code 124`（timeout）。
- **根因**：该 workflow 的 `Install backend dependencies` 步骤先用 `web/backend/requirements.txt` 派生出的 `/tmp/backend-requirements-ci.txt`（pin `numpy==1.26.4`）安装，但又因根 `requirements.txt` 的 RAPIDS 链（`cudf-cu12`/`cuml-cu12`）触发了 numpy/scipy 升级，pip 报警告：
  ```
  scipy 1.18.0 requires numpy<2.8,>=2.0.0, but you have numpy 1.26.4 which is incompatible.
  ```
  版本冲突下 import 失败，backend 进程没起来 → `localhost:8020` 永远连不上 → curl 直到 timeout。**与 PostgreSQL service container 无关**——同样是 numpy/scipy 依赖漂移问题，与 #1 同源。
- **关联 PR**：
  - PR #493（合并时 2 项失败之一）
  - PR #494（合并时 2 项失败之一）
- **影响范围**：任何触发 `e2e-test.yml` (stable-suite job) 的 PR 都会失败；与本 PR 改动无关。
- **建议修复方向**：跟 #1 同源，统一治理。要么仓库根 `requirements.txt` 也 pin `numpy<2` + `scipy<1.13`；要么 RAPIDS 链改为可选安装（extras_require），CI 默认不装。建议跟 #1 一起治理。
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

- **2026-07-07 (PR #495)**：PR #494 首次登记这两个条目时，根因被错记为 "PostgreSQL service container `role root does not exist`"。错误源于上个会话的总结摘要（context compaction），未对照实际失败日志就写入登记。本次 PR 重新对照 `gh run view --log-failed` 的真实输出，将根因更正为 numpy/scipy 依赖版本漂移。
- **2026-07-07 (PR #497)**：PR #495 的更正仍有偏差——错误地把根因指向 `web/backend/requirements.txt`（实际是 `numpy==1.26.4` 已 pin）和"backend 调用 `numpy.long`"（实际仓库代码 0 处调用）。二次核查 CI 安装日志发现：失败 workflow 实际读的是**仓库根 `requirements.txt`**（不是 `web/backend/`），里面写 `numpy>=1.24.0` 无上限，外加 `cudf-cu12>=25.10.0` + `cuml-cu12>=25.10.0` RAPIDS 链触发了 sklearn 1.9.0 + numpy 2.4.6 安装。真正根因是 **CI 安装路径错配 + RAPIDS 链引入不兼容 sklearn**，与 backend 代码无关。PostgreSQL service container 配置同样无关，无需修改。
