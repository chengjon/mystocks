## 1. OpenSpec And Catalog

> **使用说明**:
> 本文件用于记录当前 OpenSpec 变更的执行清单、操作步骤或协作约束，帮助跟踪实施过程。
> 其中勾选状态、执行顺序和局部说明仅代表任务推进视角，不应脱离 proposal、design、正式 specs、`architecture/STANDARDS.md` 与实际验证结果单独解读为最终事实。


- [x] 1.1 创建标准 OpenSpec change 目录与文件
- [x] 1.2 新增 `governance/function-tree/catalog.yaml`
- [x] 1.3 新增 `governance/function-tree/schema.json`
- [x] 1.4 补齐 catalog focused tests

## 2. Task Card And Reviewer Mirror

- [x] 2.1 扩展 `governance/mainline/schemas/ai-task-card.schema.json`
- [x] 2.2 扩展 `governance/mainline/templates/ai-task-card.yaml`
- [x] 2.3 更新 `.github/pull_request_template.md`
- [x] 2.4 更新 `governance/mainline/spec/ai-development-mainline-governance-spec.md`
- [x] 2.5 补齐 task card schema focused tests

## 3. Scope Gate Enforcement

- [x] 3.1 扩展 `governance/mainline/scripts/mainline_scope_gate.py` 读取 catalog
- [x] 3.2 实现 node/entrypoint/match/cross-domain/self-bootstrap 校验
- [x] 3.3 补齐 scope gate focused tests

## 4. Human-Readable Sync

- [x] 4.1 为 `docs/FUNCTION_TREE.md` 中被镜像业务域补齐稳定 ID
- [x] 4.2 更新 `docs/guides/governance/FEATURE_MANAGEMENT_WORKFLOW.md`
- [x] 4.3 更新 `docs/guides/ai-tools/AI_QUICK_START.md`
- [x] 4.4 补齐文档同步 focused tests

## 5. Validation

- [x] 5.1 运行 focused governance tests
- [x] 5.2 运行 `openspec validate govern-function-tree-as-code --strict`
- [x] 5.3 运行 `git diff --check`
- [x] 5.4 在 `TASK-REPORT.md` 记录命令与结果
