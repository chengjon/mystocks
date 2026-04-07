# MyStocks 全面代码审核方案（一页式检查清单）

> **使用说明**:
> 本文件是审核执行清单与协作入口，不是仓库共享规则的唯一事实来源。
> 仓库级共享规则与审批门禁以 `architecture/STANDARDS.md` 为准；涉及执行流程、命令与协作约束，再参考根目录 `AGENTS.md` 与根目录 `CLAUDE.md`。

> **用途**：对仓库进行一次结构化、可复现的全面审核；按轮次执行并归档证据。  
> **维护**：随 `AGENTS.md`、`architecture/STANDARDS.md`、`.github/workflows/*.yml` 变更同步更新本清单。

**说明**：若需纳入 `docs/guides/` 正式文档索引，可将本文件复制为 `docs/guides/full-codebase-audit-checklist.md`（以本机权限为准）。

---

## 1. 使用方式

- **轮次**：建议按 **A → F** 顺序；每轮输出三类结论：**通过** / **待办** / **风险**。
- **证据**：每条尽量附命令输出片段或文件路径，避免纯主观结论。
- **基线对比**：类型错误、E2E、Python 门禁须区分「**本次新增**」与「**历史存量**」（见 `docs/standards/technical-debt-governance-charter-v1.md`）。
- **CI 为权威**：下列「与 CI 同源」的门禁以 `.github/workflows/code-quality.yml`、`frontend-testing.yml` 实现为准；清单仅列名称与脚本入口，参数与 diff 范围逻辑以工作流内联脚本为准。

---

## 2. 审核维度总览（优先级）

| 顺序 | 维度 | 说明 |
|------|------|------|
| 1 | 治理与架构红线 | 与 `STANDARDS.md`、主线任务卡、OpenSpec 一致 |
| 2 | 安全与配置 | 密钥、CORS、依赖审计、静态扫描（含 hardcoding-governance job） |
| 3 | 数据与核心业务 | 双库路由、API 注册、数据源集成规范 |
| 4 | 质量门 | **与 CI 同源**的目录治理、合规门禁、本地 black/ruff/mypy 等；见第 6 节 |
| 5 | 测试与 E2E | **路由/Layout 变更必须 PM2 全量冒烟**；其余与 `frontend-testing` 一致 |
| 6 | 文档与可复现 | 环境、Worktree、运维路径 |

---

## 3. A. 治理与架构红线

| 检查项 | 要看什么 | 参考路径 / 动作 |
|--------|----------|------------------|
| 统一标准 | Proposal-First、六步走、Docker/PM2 环境一致性 | `architecture/STANDARDS.md` |
| 自动化防护网 | 路由/Layout 修改的 E2E 要求（见第 7 节，**强制**） | `architecture/STANDARDS.md`（§6 与脚本 `scripts/run_e2e_pm2.sh`） |
| 主线任务卡 | PR 是否具备任务卡、字段是否完整 | `governance/mainline/templates/ai-task-card.yaml`、`governance/mainline/task-cards/`、`governance/mainline/spec/ai-development-mainline-governance-spec.md` |
| 范围门禁 | 任务卡与改动路径是否一致 | `python governance/mainline/scripts/mainline_scope_gate.py`（参数以 CI/该脚本 `--help` 为准） |
| 大变更流程 | 新能力/破坏性变更是否走 OpenSpec | `openspec/AGENTS.md`；`openspec list` / `openspec validate` |

---

## 4. B. 安全与配置

| 检查项 | 要看什么 | 建议动作 / CI 对照 |
|--------|----------|-------------------|
| 密钥与硬编码 | 无提交 `.env`、无违规硬编码 | 对照 `code-quality.yml` 中 **Hardcoding Governance Gate**（`detect-secrets`、`gitleaks`、`scripts/security/validate_hardcoding_exceptions.py`、`scripts/security/hardcoding_scan.py` 等） |
| CORS / 后端配置 | 与文档端口、环境变量口径一致 | `web/backend/app/core/config.py`；对照 `AGENTS.md` / `CLAUDE.md` |
| 前端依赖审计 | 已知漏洞 | `frontend-testing.yml` 中 `frontend-security` job：`npm audit`、`audit-ci`（若存在 `audit-ci.json`） |
| Python 安全扫描 | 常见安全问题 | `bandit`（亦在 hardcoding job 与常规质量步骤中出现）；可与 `bandit -r src/` 本地对照 |
| Workflow Token 权限 | 触发 Issue / PR / 自动推送的 workflow 显式声明最小 `permissions`，且 `gh` / `github-script` 变更操作具备对应写权限 | 检查 `.github/workflows/*.yml` 的 `permissions:`、`gh issue create`、`github.rest.issues.*`、`github.rest.pulls.*`、`git push` |

---

## 5. C. 数据与核心业务路径

| 检查项 | 要看什么 | 参考路径 |
|--------|----------|----------|
| 双库路由 | TDengine vs PostgreSQL 职责清晰、`DataClassification` 一致 | `src/core/unified_manager.py`、适配器与 `src/data_access/`（抽样） |
| API 注册 | 新路由经统一注册，避免在 `main.py` 堆叠前缀 | `web/backend/app/api/VERSION_MAPPING.py` |
| 数据源集成 | 新接口符合项目约定 | `docs/guides/data-source/NEW_API_SOURCE_INTEGRATION_GUIDE.md` |

---

## 6. D. 质量门（与 CI 对齐）

> **表述约定**：本节「与 CI 对齐」指与 `.github/workflows/code-quality.yml`（及 `typescript-type-check.yml` 等专项工作流）中**步骤名称与脚本**一致；审核时应打开工作流文件核对是否有新增步骤。
>
> **状态说明**：
> - **硬门禁**：CI 默认失败即阻塞合并。
> - **软门禁 / 报告项**：步骤存在，但可能 `continue-on-error: true`，用于提示、审计或报告，不应误记为硬阻塞。

### 6.1 `code-quality.yml` 中与合规相关的门禁（按工作流出现顺序摘录）

| 工作流步骤名 | 属性 | 脚本 / 入口（仓库内） |
|--------------|------|------------------------|
| Directory Governance Check | 硬门禁 | `scripts/maintenance/check_structure.py` |
| Production Python Guardrails | 硬门禁 | `scripts/compliance/production_python_guardrails.py` |
| Observability Readiness Gate | 硬门禁 | `scripts/compliance/readiness_contract_gate.py` |
| Backend Singleton None Guard | 硬门禁 | `scripts/compliance/backend_singleton_none_guard.py` |
| UnifiedResponse Contract Guard | 硬门禁 | `scripts/compliance/unified_response_contract_guard.py` |
| Frontend/Test File Size Guard | 硬门禁 | `scripts/compliance/file_size_guardrail.py` |
| PM2 First-Class Gate | 硬门禁 | `scripts/compliance/pm2_first_class_gate.py` |
| Hardcoding Governance Gate（独立 job） | 硬门禁 | `detect-secrets`、`gitleaks`、`bandit`、`scripts/security/validate_hardcoding_exceptions.py`、`scripts/security/hardcoding_scan.py` 等 |

同一工作流内通常还包含 **Black / isort / Pylint / Flake8 / MyPy / pytest / bandit** 等质量步骤；完整列表以 `code-quality.yml` 全文为准。

### 6.1.1 `code-quality.yml` 后半段的质量汇总与总门禁

| Job / 步骤 | 属性 | 用途 |
|------------|------|------|
| `test-coverage` | 软门禁 / 报告项 | 生成覆盖率产物与报告，供后续质量汇总使用 |
| `performance-benchmark` | 软门禁 / 报告项 | 生成性能基准与内存分析结果 |
| `complexity-analysis` | 软门禁 / 报告项 | 生成复杂度产物，供质量报告汇总 |
| `security-compliance` | 软门禁 / 报告项 | 运行安全规范检查、Bandit、Semgrep 等产物生成 |
| `quality-report` | 报告项 | 汇总前述产物到 `quality-reports/` |
| `quality-gate` | 硬门禁 | 基于汇总产物做最终质量判定（如覆盖率、复杂度、Pylint 错误数等） |

**审核提示**：
- 若审的是“是否可合并/可发布”，不要只看单个扫描步骤；还应检查 `quality-gate` 的最终结论。
- 若审的是“全面代码审核报告”，建议把 `quality-reports/quality-summary.md` 作为证据附件之一。

### 6.1.2 Workflow 编排完整性（建议纳入仓库级审核固定项）

| 检查项 | 要看什么 | 审核提示 |
|--------|----------|----------|
| `needs` / `outputs` 链路 | `steps.*.outputs`、`needs.*.outputs`、`needs.*.result` 均指向真实存在的 step / job / output，且不存在自引用 `needs.<self>` | 这是典型“YAML 可解析但运行时取空值/直接失败”的问题 |
| Artifact 产物链路 | `upload-artifact` / `download-artifact` 名称一致；`pattern` 下载要么 `merge-multiple: true`，要么下游显式按 artifact 子目录读取 | 重点检查汇总 job、final-report、quality-gate、summary 类 job |
| Workflow 标识唯一性 | `.github/workflows/*.yml` 的顶层 `name:` 应唯一，避免 Actions UI、运行历史、告警链接混淆 | 不阻塞执行，但属于仓库级治理质量项，建议在全面审核中固定检查 |
| 官方 Action 版本漂移 | `actions/checkout`、`setup-node`、`setup-python`、`cache` 等基础官方 action 不应长期停留在过旧 major | 建议至少按仓库统一到当前稳定主版本，避免平台兼容噪音与维护分裂 |
| 官方 Action 命名空间正确性 | 第三方/官方 action 的 `uses:` 应指向真实维护方命名空间，例如 Docker 生态应使用 `docker/*` 而非误写成 `actions/*` | 这是典型“YAML 可解析，但运行时拉取 action 失败”的问题 |
| 可变分支 Ref 禁止 | `uses:` 不应指向 `@main`、`@master` 等可变分支，应固定到 tag 或 commit SHA | 这是典型“同一 commit 不同时间跑出不同结果”的供应链稳定性问题 |
| 模板与 Webhook 生成 | 生成 `.md` / `.json` 报告、Webhook payload 时，避免把需要展开的模板写成单引号 heredoc；JSON 负载需安全序列化 | 尤其关注 `curl -d`、多行消息、含引号正文 |
| `GITHUB_ENV` / `if` 上下文 | 多行值写入 `GITHUB_ENV` 必须使用 heredoc；`if:` 中不要直接引用 `secrets.*`，应改用 `env` 或 step 内判断 | 这是典型“本地 shell 看起来能跑、Actions 运行时失效”的问题 |
| Python heredoc / 子进程环境 | `python - <<'PY'`、`python << 'EOF'` 的正文在 YAML 解析后不能残留前导缩进；若 Python 通过 `os.environ[...]` 读取 shell 变量，必须来自 `env:` / `GITHUB_ENV` / `export` | 这是典型“YAML 可解析，但运行时直接 `IndentationError` 或 KeyError”的问题 |
| 自动提交 / 自动 PR | 存在 `git push`、`github.rest.pulls.create` 时，工作流应显式处理分支、重复 PR、以及 detached HEAD | 重点检查 `checkout` 后是否创建/切换目标分支，是否复用已有 PR |
| Shell 失败语义 | 避免在默认 `bash -e` 步骤中使用不可达的 `$?` 后置判断；对需要自定义报错的命令使用 `if ! cmd; then ... fi` | 重点检查 `npm run ...`、`pytest`、`python ...` 后紧跟 `$?` 的模式 |
| 脚本语法静态校验 | 对 workflow 内嵌脚本做“比 YAML 更深一层”的静态校验：`run:` 片段可做 `bash -n`，`github-script` 可做 `node --check`，Python heredoc 可单独做语法编译检查 | 这类问题往往 YAML 可解析，但 shell / JS / Python 真正执行时才报错 |
| 内联脚本复杂度 | 多行 `python -c` / `node -e` 属高风险坏味道；超过简单单行表达式时，优先改为 heredoc 或仓库脚本文件 | 这类写法转义脆弱、难以稳定做静态验证，仓库级审核应主动标记风险 |

### 6.1.3 建议的工作流静态校验证据

| 校验层 | 建议证据 | 备注 |
|--------|----------|------|
| YAML 结构 | `python -c "import yaml, pathlib; ... yaml.safe_load(...)"` 或 `actionlint` / `yamllint` 输出 | 至少确认 `.github/workflows/*.yml` 全部可解析 |
| Shell 语法 | 对 `run:` 片段执行 `bash -n` 的结果；若仓库装有 `shellcheck`，可附加其输出 | 重点覆盖 heredoc、命令替换、数组、`if/fi` 配对 |
| GitHub Script 语法 | 对 `actions/github-script` 的 `with.script` 执行 `node --check` 的结果 | 重点覆盖模板字符串、对象字面量、`await` / `async` 包装 |
| Python heredoc 语法 | 将 `python - <<'PY'` / `python << 'EOF'` 提取后做编译检查（如 `python -m py_compile`） | 重点覆盖缩进、字符串字面量、f-string、异常块 |

**审核提示**：
- 若仓库环境没有 `actionlint`，可接受 “YAML 解析 + `bash -n` + `node --check` + Python heredoc 编译检查” 组合作为替代证据。
- 结论中建议明确区分“工作流文件可解析”与“内嵌脚本可执行”两层，不应混为一条“YAML 正常”。

### 6.2 `frontend-testing.yml` 中与前端相关的门禁（`frontend-test` / `frontend-security` 等）

| 类别 | 属性 | 命令或脚本 |
|------|------|------------|
| 常规 | 硬门禁 | `npm run lint` |
| 路由纯净度 | 硬门禁 | `scripts/compliance/app_route_purity_gate.py` |
| Request ID 显化（变更文件） | 软门禁 / 报告项 | `scripts/compliance/request_id_visibility_gate.py` |
| ArtDeco（变更范围） | 软门禁 / 报告项 | `npm run lint:artdeco:changed`、`npm run lint:artdeco:guidance:changed` |
| E2E 选择器策略 | 硬门禁 | `npm run test:e2e:selectors` |
| 类型错误上限 | 硬门禁 | `npm run test:type-ceiling` |
| 契约/配置冒烟 | 硬门禁 | 如 `npx vitest run tests/unit/port-config-consistency.spec.ts` |
| 单元测试 | 硬门禁 | `npm run test:unit:stable`、`npm run test` |
| Playwright 与 E2E | 硬门禁 | `npm run test:e2e:validate`、`npm run test:e2e:stable`、`npm run test:e2e:axe`、`npm run test:e2e:lighthouse` |
| 构建 | 硬门禁 | `npm run build:no-types`（工作流内配置） |
| 安全 | `npm audit` 为软门禁 / 报告项；`audit-ci` 为条件硬门禁 | `npm audit`、`audit-ci`（见 `frontend-security` job） |

### 6.3 `typescript-type-check.yml` 专项门禁

| 类别 | 属性 | 命令或脚本 |
|------|------|------------|
| `tsc` 原始输出 | 软门禁 / 报告项 | `npx tsc --noEmit ...`（原始步骤 `continue-on-error`，用于生成产物与错误统计） |
| `vue-tsc` 原始输出 | 软门禁 / 报告项 | `npx vue-tsc --noEmit ...`（原始步骤 `continue-on-error`，用于生成产物与错误统计） |
| ESLint TypeScript 汇总 | 报告项 | `npx eslint src --ext .ts,.tsx,.vue ...`（结果上传供最终 gate 汇总） |
| No New Debt Gate | 硬门禁 | diff 范围内禁止新增裸 `TODO/FIXME/HACK`、禁止无审批抑制注释 / `as any` |
| Type Check Quality Gate | 硬门禁 | `node scripts/check-type-error-ceiling.js --input-file ...` + 基线 `reports/analysis/tech-debt-baseline.json` + 产物汇总判定 |

**审核提示**：
- 不要把 `tsc` / `vue-tsc` 原始步骤的 `continue-on-error` 误解为“类型检查不重要”；真正阻塞结论由最后的 **Type Check Quality Gate** 决定。
- 审核类型问题时，至少同时核对：`frontend_type_errors` 基线、`test:type-ceiling` 口径、`No New Debt Gate` 是否通过。

### 6.4 本地常用命令（不能替代上表 CI 步骤；用于开发机快速反馈）

**Python（仓库根目录）**

```bash
black --check .
ruff check src/
mypy src/ --no-error-summary
pytest
```

**前端（`web/frontend`）**

```bash
npm run lint
npm run type-check
npm run test:type-ceiling
npx stylelint "src/**/*.{vue,scss,css}"
```

**可选补充（不等同于当前 CI 硬门禁）**

```bash
bandit -r src/
safety check
```

### 6.5 技术债基线

- **权威文件**：`reports/analysis/tech-debt-baseline.json`（见 `AGENTS.md`、`.github/workflows/typescript-type-check.yml`）。
- 若本地不存在：使用 `scripts/dev/quality_gate/collect_tech_debt_baseline.py`（见脚本 `--help`）生成或更新，再与 `npm run test:type-ceiling` 结果对照。
- **KPI/周报类门禁**（若启用）：`scripts/dev/quality_gate/tech_debt_governance_gate.py`。

### 6.6 代码体量与 Mock 扫描（建议定期，如每月）

```bash
python -m src.monitoring.code_inventory.cli --no-validation --scan-dirs src scripts web/backend/app
```

---

## 7. E. 测试与端到端（**与仓库强制规则一致**）

### 7.1 路由或 Layout 变更（强制）

- **架构要求**：凡涉及**路由或 Layout** 的修改，必须通过 **`bash scripts/run_e2e_pm2.sh`** 进行全量冒烟测试。权威条文见 `architecture/STANDARDS.md`（自动化防护网 / Safety Net）。
- **CI 对应**：`.github/workflows/frontend-testing.yml` 中 **`route-layout-pm2-detect`** 判定是否需要门禁；若需要，则 **`route-layout-pm2-gate`** 执行 **`bash scripts/run_e2e_pm2.sh`**（与本地强制命令一致）。
- **审核结论**：若 MR/变更触及路由或 Layout，**不得**仅以 `npm run test:e2e:business-smoke` 或普通 Playwright 子集作为已满足 E2E 的证据；必须确认 PM2 全量冒烟脚本已执行且通过（或与 CI 中 Route/Layout PM2 Gate 等价）。

### 7.2 一般前端变更（与 `frontend-test` job 一致）

在**非**上述「路由/Layout 强制」场景下，仍应参照 `frontend-testing.yml` 中 `frontend-test` 的完整步骤（见第 6.2 节），包括但不限于：`test:e2e:validate`、`test:e2e:stable`、axe、Lighthouse 等（以工作流 `if` 条件与 scope 检测为准）。

### 7.2.1 独立 `e2e-testing.yml` 工作流（辅助参考，避免口径混淆）

- 仓库中另有独立的 `.github/workflows/e2e-testing.yml`，用于更重的 E2E 流水线与定时任务。
- 该工作流使用 **CI 专用端口口径**：前端 `5173/5174`、后端 `8000/8001`，并通过 `PLAYWRIGHT_BASE_URL=http://localhost:5173`、`PLAYWRIGHT_API_URL=http://localhost:8000` 运行。
- 它会执行多浏览器、多分片的 Playwright 流水线，并汇总 `test-summary.json` / `test-report.md` 等产物。
- **审核时不要混淆两套口径**：
  - 本地 / `AGENTS.md` 强制状态确认口径：`3020/8020`
  - 独立 E2E CI 工作流口径：`5173/8000`
- 若引用该工作流结果作为证据，需显式注明“来自 `e2e-testing.yml` 的 CI 端口口径”，避免误报为本地 PM2 服务状态。

### 7.3 报告口径

- **必须按实际执行结果**报告通过/失败/跳过数量，勿使用固定「18/18」类文案（见 `AGENTS.md`）。
- 单元 / 集成：`pytest`；按需 `pytest -m integration`。
- 本地服务（若适用）：与 `AGENTS.md` 一致时确认 `http://localhost:8020`、`http://localhost:3020` 及 PM2 进程。

### 7.4 强制状态确认模板（按 `AGENTS.md` 落地）

凡审核过程涉及**前端构建、类型检查、E2E 或服务启动**，结论区建议至少补齐以下字段：

| 检查项 | 报告要求 |
|--------|----------|
| 结构性语法错误 | 明确写 `0` 或非 `0`；非 `0` 视为阻塞 |
| 类型推断错误 | 对照 `reports/analysis/tech-debt-baseline.json` 的 `frontend_type_errors`；说明是存量还是本次新增 |
| PM2 服务 | 报告 `mystocks-backend`、`mystocks-frontend` 是否运行，并附 `http://localhost:8020`、`http://localhost:3020` |
| E2E 测试 | 报告执行命令、浏览器项目、通过/失败/跳过数量；若仅跑 smoke/stable 子集必须写明 |

**推荐写法（示例骨架）**：

```text
状态确认
- 结构性语法错误: 0
- 类型推断错误: 当前 X，基线 Y；新增/存量判定: ...
- PM2 服务: mystocks-backend=running (http://localhost:8020), mystocks-frontend=running (http://localhost:3020)
- E2E: 执行命令 `...`; project=chromium; passed=X failed=Y skipped=Z
```

---

## 8. F. 文档与可复现

| 检查项 | 路径 |
|--------|------|
| 本地环境 | `docs/standards/LOCAL_ENV_SETUP.md` |
| 多 CLI / Worktree（权威入口） | `docs/guides/multi-cli-tasks/MULTI_CLI_WORKTREE_MANAGEMENT.md`（历史副本可能仍存在于 `.multi-cli-tasks/guides/`；以 `docs/guides/` 下为准） |
| 技术债治理 | `docs/standards/technical-debt-governance-charter-v1.md` |

---

## 9. 建议的审核交付物

1. **执行矩阵**：A–F 每栏填写「结论 + 证据（命令/路径/CI Job 名）」。
2. **风险登记**：P0（阻塞发布）/ P1 / P2，含建议修复顺序。
3. **与基线对比**：类型错误、E2E、Python 门禁——明确增量与存量。
4. **路由/Layout 变更专项**：显式回答是否已执行 `scripts/run_e2e_pm2.sh`（或 CI Route/Layout PM2 Gate 等价物）。
5. **状态确认**：若本轮涉及前端构建、类型检查、E2E 或服务启动，附第 7.4 节模板化结果。

---

## 10. 变更记录

| 日期 | 说明 |
|------|------|
| 2026-03-29 | 初版：一页式清单与仓库路径对齐 |
| 2026-03-29 | 修订：E2E 与 `STANDARDS.md` / Route-Layout PM2 Gate 对齐；补充 `code-quality.yml` 与 `frontend-testing.yml` 同源门禁；修正数据源与 Worktree 文档路径 |
| 2026-03-29 | 修订：补充 `typescript-type-check.yml` 最终 gate 结构、`code-quality.yml` 汇总质量门、以及 `AGENTS.md` 强制状态确认模板 |
| 2026-03-30 | 修订：补充 workflow token 权限、artifact/outputs 链路、Webhook/报告模板、自动提交/PR 分支处理等“运行时编排完整性”审核项 |
| 2026-03-30 | 修订：补充 `secrets.*` in `if`、多行 `GITHUB_ENV`、以及 `bash -e` 下 `$?` 不可达判断等脚本运行语义检查项 |
| 2026-03-30 | 修订：补充 Python heredoc 缩进与 shell 变量传子进程环境的审核项，覆盖 `IndentationError` / `os.environ` 缺值类故障 |
| 2026-03-30 | 修订：补充 `bash -n` / `node --check` / Python heredoc 语法编译等“嵌入脚本静态校验”审核项 |
| 2026-03-30 | 修订：新增工作流静态校验证据建议，明确 YAML / Shell / GitHub Script / Python heredoc 四层证据口径 |
| 2026-03-30 | 修订：新增“多行 `python -c` / `node -e` 为高风险坏味道”的审核项，建议优先改为 heredoc 或仓库脚本 |
| 2026-03-30 | 修订：新增 workflow 顶层 `name:` 唯一性检查，避免 Actions UI 与历史记录混淆 |
| 2026-03-30 | 修订：新增基础官方 action 主版本漂移检查，覆盖 `checkout/setup-node/setup-python/cache` 的统一升级要求 |
| 2026-03-30 | 修订：新增官方/第三方 action 命名空间正确性检查，覆盖 `docker/*` 等生态 action 的 `uses:` 指向校验 |
| 2026-03-30 | 修订：新增 `uses: ...@main/@master` 可变分支 ref 禁止项，要求固定到 tag 或 SHA |
