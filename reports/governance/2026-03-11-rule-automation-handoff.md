# 规则自动化治理线交接记录（2026-03-11）

## 一、交接背景

这条工作线最近的核心目标，不是业务功能开发，而是把 `architecture/STANDARDS.md` 里“已经写明、但之前没有自动化拦截”的工程规则，逐步补成：

- `scripts/compliance/*.py` 静态门禁脚本
- `.pre-commit-config.yaml` 本地 pre-commit hook
- `.githooks/pre-commit` staged 增量门禁
- `.github/workflows/code-quality.yml` / `.github/workflows/frontend-testing.yml` CI 门禁
- `tests/unit/scripts/*` + `tests/unit/test_pre_commit_config.py` 回归测试

换句话说，这条线最近做的是 **“规范自动化补洞”**，不是主线业务重构。

当前用户明确表示正在做主线架构重组，因此这里输出一份可独立接手的交接记录，避免后续与主线重组互相踩改。

---

## 二、这条工作线最近已完成的内容

### 1. 已完成自动化的规则

最近连续补齐并验证通过的规则如下：

1. ArtDeco token 使用门禁
2. `/health/ready` + `App.vue` 启动期 readiness 门禁
3. `App.vue` 路由纯净度门禁
4. 业务 Tab `Request ID / TRACE_ID` 显位门禁
5. 后端单例 `global ... = None` 门禁
6. `UnifiedResponse` API 响应契约门禁
7. Vue / TS / 测试文件大小阈值门禁
8. PM2 一等公民门禁

其中，最近三项是本轮最新补齐：

- `UnifiedResponse` API 响应契约门禁
- Vue / TS / 测试文件大小阈值门禁
- PM2 一等公民门禁

### 2. 当前治理线的核心脚本

当前这条线的核心门禁脚本位于：

- `scripts/compliance/readiness_contract_gate.py`
- `scripts/compliance/app_route_purity_gate.py`
- `scripts/compliance/request_id_visibility_gate.py`
- `scripts/compliance/backend_singleton_none_guard.py`
- `scripts/compliance/unified_response_contract_guard.py`
- `scripts/compliance/file_size_guardrail.py`
- `scripts/compliance/pm2_first_class_gate.py`
- `scripts/compliance/route_layout_pm2_gate.py`
- `scripts/compliance/production_python_guardrails.py`

### 3. 当前治理线的核心接线文件

这几个文件是这条线最容易与主线架构重组产生冲突的“治理汇总入口”：

- `.pre-commit-config.yaml`
- `.githooks/pre-commit`
- `.github/workflows/code-quality.yml`
- `.github/workflows/frontend-testing.yml`
- `tests/unit/test_pre_commit_config.py`
- `reports/governance/2026-03-10-rule-automation-gap-scan.md`

如果主线架构重组期间要大改 CI / hook / 验收流程，优先关注这些文件是否存在冲突。

---

## 三、本轮最新完成项的详细说明

### 1. `UnifiedResponse` API 响应契约门禁

目标：

- 对增量修改的 `web/backend/app/api/**/*.py` 做静态检查
- 普通 HTTP 路由要求声明：
  - `response_model=UnifiedResponse[...]`
  - 或 `response_model=UnifiedPaginatedResponse[...]`
- 对以下原始响应类型做豁免：
  - SSE / 流式响应
  - `Response`
  - `PlainTextResponse`
  - `FileResponse`
  - `StreamingResponse`
  - `204 no-content`

关键文件：

- `scripts/compliance/unified_response_contract_guard.py`
- `tests/unit/scripts/test_unified_response_contract_guard.py`
- `tests/unit/scripts/test_unified_response_contract_guard_integration.py`

接线：

- `.pre-commit-config.yaml`
- `.githooks/pre-commit`
- `.github/workflows/code-quality.yml`

### 2. Vue / TS / 测试文件大小阈值门禁

目标：

- 复用现有 canonical 脚本 `scripts/compliance/file_size_guardrail.py`
- 升级为支持 **增量路径扫描** + **scope root 扫描**
- 只卡本次改动中的：
  - `web/frontend/**/*.(vue|ts|js)`
  - `tests/**/*.(ts|js)`
- 不误伤历史大文件债务

当前阈值：

- `.py`: `800`
- `.ts`: `500`
- `.vue`: `500`
- `.spec.ts`: `1000`
- `.spec.js`: `1000`

关键文件：

- `scripts/compliance/file_size_guardrail.py`
- `tests/unit/scripts/test_file_size_guardrail.py`
- `tests/unit/scripts/test_file_size_guardrail_integration.py`
- `tests/unit/scripts/test_monitor_file_size.py`

接线：

- `.pre-commit-config.yaml`
- `.githooks/pre-commit`
- `.github/workflows/code-quality.yml`

### 3. PM2 一等公民门禁

目标：

- 对增量修改的 workflow / 脚本 / 编排文件进行静态检查
- 如果文件里既出现：
  - `playwright test` / `npm run test:e2e` 等验收命令
- 又出现：
  - `uvicorn`
  - `npm run dev`
  - `vite preview`
  - 类似的碎片化运行时启动
- 但没有走：
  - `scripts/run_e2e_pm2.sh`
  - 或显式 `pm2 start` + `pm2 list/status/服务标识`

则阻断

关键文件：

- `scripts/compliance/pm2_first_class_gate.py`
- `tests/unit/scripts/test_pm2_first_class_gate.py`
- `tests/unit/scripts/test_pm2_first_class_gate_integration.py`

接线：

- `.pre-commit-config.yaml`
- `.githooks/pre-commit`
- `.github/workflows/code-quality.yml`

备注：

- `scripts/run_e2e_pm2.sh` 已被识别为 canonical PM2 runner

---

## 四、当前验证状态

### 1. 最近一轮综合治理回归

最近一轮治理回归结果：

- `88 passed`

对应回归命令包含：

- `tests/unit/test_pre_commit_config.py`
- `tests/unit/scripts/test_monitor_file_size.py`
- `tests/unit/scripts/test_file_size_guardrail.py`
- `tests/unit/scripts/test_file_size_guardrail_integration.py`
- `tests/unit/scripts/test_artdeco_token_gate_integration.py`
- `tests/unit/scripts/test_route_layout_pm2_gate.py`
- `tests/unit/scripts/test_route_layout_pm2_gate_integration.py`
- `tests/unit/scripts/test_production_python_guardrails.py`
- `tests/unit/scripts/test_production_python_guardrail_integration.py`
- `tests/unit/scripts/test_directory_governance_integration.py`
- `tests/unit/scripts/test_readiness_contract_gate.py`
- `tests/unit/scripts/test_readiness_contract_gate_integration.py`
- `tests/unit/scripts/test_app_route_purity_gate.py`
- `tests/unit/scripts/test_app_route_purity_gate_integration.py`
- `tests/unit/scripts/test_request_id_visibility_gate.py`
- `tests/unit/scripts/test_request_id_visibility_gate_integration.py`
- `tests/unit/scripts/test_backend_singleton_none_guard.py`
- `tests/unit/scripts/test_backend_singleton_none_guard_integration.py`
- `tests/unit/scripts/test_unified_response_contract_guard.py`
- `tests/unit/scripts/test_unified_response_contract_guard_integration.py`
- `tests/unit/scripts/test_pm2_first_class_gate.py`
- `tests/unit/scripts/test_pm2_first_class_gate_integration.py`

### 2. 烟测结果

本轮额外做过的脚本烟测包括：

- `python scripts/compliance/unified_response_contract_guard.py --format json --root-dir . --path web/backend/app/api/algorithms/_naive_bayes_router.py`
  - 结果：`errors: 0`
- `python scripts/compliance/file_size_guardrail.py --format json --root-dir . --scope-root web/frontend --scope-root tests --path web/frontend/src/components/artdeco/core/ArtDecoIcon.vue`
  - 结果：`oversized_count: 0`
- `python scripts/compliance/pm2_first_class_gate.py --format json --root-dir . --path scripts/run_e2e_pm2.sh`
  - 结果：`errors: 0`

### 3. 配置语法

最近已验证 YAML 可正常解析：

- `.pre-commit-config.yaml`
- `.github/workflows/code-quality.yml`

---

## 五、当前未完成、但已明确的下一步任务

当前 `reports/governance/2026-03-10-rule-automation-gap-scan.md` 中剩余的优先级如下：

1. 分层依赖 / 循环依赖门禁
2. 重构后废弃导入 / 残留模块引用清理门禁
3. Mock 驱动开发门禁

### 下一步建议顺序

#### 任务 A：分层依赖 / 循环依赖门禁

建议优先级：最高

原因：

- 这是 `architecture/STANDARDS.md` 的“单体骨架”核心约束
- 与主线架构重组最直接相关
- 越晚补，越容易在重组后形成新的跨层依赖债务

建议实现方式：

- 增量检查改动中的 Python / TS 模块依赖
- 先做静态层级约束，再逐步补循环依赖检测
- 初期只做 `src/` + `web/backend/app/` 的 Python 侧，避免一次覆盖过大

#### 任务 B：废弃导入 / 残留模块引用清理门禁

建议优先级：高

原因：

- 主线重构期间最容易引入“旧模块已删、引用未清”
- 这类问题往往直接表现为后端重启失败 / CI import error / 运行时死循环

建议实现方式：

- 先做“改动文件指向不存在模块/路径”的增量门禁
- 再做“已标记废弃模块名单”的 residual import guard

#### 任务 C：Mock 驱动开发门禁

建议优先级：中

原因：

- 与前端独立验收直接相关
- 但在当前主线架构重组期间，优先级略低于分层依赖和残留导入

建议实现方式：

- 先选定一类页面或一组前端视图做增量检查
- 不建议一上来做全仓硬拦截

---

## 六、为了避免与当前主线架构重组互相影响，建议这样处理

### 1. 建议暂缓大改的文件

如果不是明确在改治理线，尽量避免顺手修改这些文件：

- `.pre-commit-config.yaml`
- `.githooks/pre-commit`
- `.github/workflows/code-quality.yml`
- `.github/workflows/frontend-testing.yml`
- `tests/unit/test_pre_commit_config.py`
- `reports/governance/2026-03-10-rule-automation-gap-scan.md`

因为这些文件是多道治理门禁的汇总入口，主线重构一旦顺手改，很容易造成冲突或回退掉之前的自动化。

### 2. 如果主线重构必须改 CI / 验收流程

建议遵守下面的处理顺序：

1. 先看 `reports/governance/2026-03-10-rule-automation-gap-scan.md`
2. 再看本交接记录
3. 确认是否会影响：
   - pre-commit
   - githook
   - code-quality workflow
   - frontend-testing workflow
4. 若影响其中任一项，最后补一轮治理回归

### 3. 当前这条治理线与主线重构的低冲突边界

如果要继续推进治理线，但又想避免影响主线重组，建议优先做：

- 纯新增 `scripts/compliance/*.py`
- 纯新增 `tests/unit/scripts/test_*.py`
- 最后再一次性接入 `.pre-commit-config.yaml` / `.githooks/pre-commit` / workflow

这样冲突面最小。

---

## 七、建议接手时优先阅读的文件

按顺序建议先读：

1. `architecture/STANDARDS.md`
2. `reports/governance/2026-03-10-rule-automation-gap-scan.md`
3. `reports/governance/2026-03-11-rule-automation-handoff.md`
4. `.pre-commit-config.yaml`
5. `.githooks/pre-commit`
6. `.github/workflows/code-quality.yml`
7. `tests/unit/test_pre_commit_config.py`

如果要继续扩展某一条治理规则，再读对应的：

- `scripts/compliance/*.py`
- `tests/unit/scripts/test_*`

---

## 八、交接结论

当前这条工作线的状态可以概括为：

- 已把一批关键架构规范成功转成自动化门禁
- 当前治理清单已经收敛出明确的剩余三项
- 下一步最值得继续的是：
  1. 分层依赖 / 循环依赖门禁
  2. 废弃导入 / 残留模块引用清理门禁
  3. Mock 驱动开发门禁

在主线架构重组期间，建议把这条线视为 **“独立治理支线”**：

- 需要继续做时再单独推进
- 不需要时只保留已接好的门禁，不必主动扩写
- 避免无意改动治理汇总入口，防止互相干扰

