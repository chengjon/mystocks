# Deliverable: 全仓代码精简分阶段优化方案

## 1. 目标与边界

### 目标
- 降低重复入口与兼容层维护成本。
- 缩短调用链、减少认知负担。
- 在行为等价前提下精简代码结构。

### 边界
- 本方案不引入新功能。
- 不改变对外 API 契约（除非明确走版本变更流程）。
- 不以“关闭质量门”作为精简手段。

---

## 2. 优先级分层（P0/P1/P2）

### P0（先做，低风险高收益）
1. **Frontend API 入口收敛（先决策再迁移）**
   - 目标：明确唯一 canonical client，并统一到该入口。
   - 现状：仓库并行存在 `web/frontend/src/api/apiClient`、`web/frontend/src/api/unifiedApiClient.ts`、`web/frontend/src/services/httpClient.js`，且存在 `web/frontend/src/services/api-client` 调用链路。
   - 动作：
     - 先冻结“新增 API client 入口”。
     - 先完成 canonical 决策（`src/api/apiClient` 与 `src/services/api-client` 二选一，建议沿当前主流调用链并给出 sunset 计划）。
     - 批量迁移调用方并保留短期桥接层（带 deprecate 标记与移除窗口）。
2. **Backend legacy 文件清理前验证（扩展后缀）**
   - 目标：覆盖运行链路中的 `.old/.new/.bak/.backup*` 并行实现，而非仅 `.old.py`。
   - 动作：先做全量引用扫描（路由注册、动态导入、脚本调用、CI 命令）；无引用则归档删除，有引用先迁移再删除。

### P1（中期重构）
1. **Scripts 分层治理**（runtime/dev/archive）
2. **Tests 分级**（core-regression vs compat-legacy）
3. **Docs 主干降噪 + 历史归档索引**

### P2（收尾优化）
1. 配置与测试脚本目录语义清理（config 中测试脚本归位）。
2. 补充仓库“唯一入口清单”文档，减少后续重复建设。

---

## 3. 分阶段执行计划

## Phase A：基线与观测（1 个迭代）
- 输出兼容层资产清单（文件、导出符号、调用方数量）。
- 建立 canonical 入口清单（frontend/backend/scripts）。
- 为 legacy 入口增加迁移观测（日志/告警，不改行为）。

**交付物**
- `compatibility-inventory.md`
- `canonical-entrypoints.md`

## Phase B：调用迁移（1~2 个迭代）
- 批量替换调用方到 canonical 入口。
- 每次迁移后执行针对性回归（单测 + 关键页面/API）。

**交付物**
- 迁移 PR（按模块拆分）
- 迁移覆盖报告（调用数变化）

## Phase C：冗余删除与归档（1 个迭代）
- 删除零调用 legacy 入口。
- 归档历史脚本与文档（保留索引和追溯链）。

**交付物**
- 删除清单（含引用数=0证据）
- 归档索引页

## Phase D：稳定化与制度化（持续）
- 将“新入口唯一性”写入开发规范。
- CI 增加检测：禁止新增重复 API 入口模式。

---

## 4. 验收标准（Acceptance Criteria）

### 结构验收
- Frontend 仅存在一个 canonical API client 入口（其余仅允许短期过渡且有 sunset 标记），并完成 `src/api/*` 与 `src/services/api-client` 入口收敛决策与迁移闭环。
- Backend 不再存在运行链路上的 `.old/.new/.bak/.backup*` 并行实现。
- Scripts 目录按 runtime/dev/archive 清晰分层。

### 质量验收
- Python：`pytest`、`ruff check`、`black --check`、`mypy` 通过。
- Frontend：`npm run build`、必要单测通过。
- 前端类型错误门禁：对齐 `reports/analysis/tech-debt-baseline.json` 的 `frontend_type_errors` 基线，不得劣化。
- 运行态门禁：PM2 确认 `mystocks-backend` / `mystocks-frontend` 运行正常。
- E2E 门禁：关键链路 E2E 必须报告通过状态（与仓库既有基线口径一致）。
- Stylelint：当前作为“条件性门禁”——先补齐可执行脚本（如 `lint:style`）并稳定后，再升级为强制硬门禁。

### 行为验收
- 对外 API 返回结构与状态码保持兼容。
- 前端请求链路（认证/错误处理）行为不回退。

---

## 5. 回滚策略（Rollback Strategy）

1. **分 PR 小步提交**：每个模块独立 PR，可单独回滚。
2. **软删除优先**：先 deprecate + 观测，再硬删除。
3. **双轨窗口**：关键入口保留短期桥接，观察 1 个发布周期后移除。
4. **触发条件**：出现核心链路回归（登录失败、关键 API 异常、主页面不可用）立即回滚最近精简 PR。
5. **回滚执行**：
   - `git revert <commit>` 回退单 PR。
   - 恢复 legacy 导出/桥接入口（仅临时）。
   - 追加回归测试后再重新推进。

---

## 6. 执行清单（按依赖顺序）

1. [ ] 生成全仓兼容层清单（符号+引用数）。
2. [ ] 确认 canonical 入口并冻结新增重复入口。
3. [ ] 增加 legacy 入口观测（日志/告警）。
4. [ ] 迁移 frontend 调用到 `apiClient`。
5. [ ] 验证 backend `.old/.new/.bak/.backup*` 引用并完成迁移/删除。
6. [ ] 分层整理 scripts 与 docs 归档。
7. [ ] 分离 core 与 compat 测试套件。
8. [ ] 跑全量质量门并记录结果。
9. [ ] 删除零引用冗余层并提交最终收敛报告。

---

## 7. 风险与应对

- **隐式依赖风险**：通过引用扫描 + CI/脚本清单交叉校验。
- **行为漂移风险**：关键链路回归与契约测试并行执行。
- **迁移不彻底风险**：设置“零引用才可删”硬门槛。

---

## 8. 建议执行节奏

- 第 1 周：Phase A + Phase B（部分模块）
- 第 2 周：Phase B（完成）+ Phase C
- 第 3 周：Phase D（规范固化与CI守护）

> 若你确认，我可以下一步按该计划直接进入 **Phase A（只读基线清单生成）**，先给出“逐文件删除候选 + 引用计数 + 迁移目标”。
