# MyStocks 脏工作区清理指南审核意见

> **审核对象**: `docs/guides/governance/DIRTY_WORKTREE_CLEANUP_GUIDE.md`
>
> **审核日期**: 2026-05-27
>
> **上游参考**: `/opt/claude/quantix-rust/docs/guides/DIRTY_WORKTREE_CLEANUP_GUIDE_REVIEW.md`
>
> **适用项目**: MyStocks (`/opt/claude/mystocks_spec`)
>
> **当前结论**: MyStocks 版指南已采纳上游 review 的主要结构修正；剩余工作应通过 OpenSpec change `implement-dirty-worktree-cleanup-governance` 按切片执行，而不是在根脏工作树中直接清理。

---

## 一、总体判断

MyStocks 当前指南已经从早期草案升级为可执行版，重点问题已有明显改善：

- 总流程已统一为步骤 0-9，并覆盖 `Freeze & Inventory`、`Recovery Snapshot`、`Classification`、`Clean Review Worktree`、`Slice Extraction`、`Slice Validation`、`PR & Commit Strategy`、`Root Tracked Realignment`、`Residual Untracked Disposition`、`Final Cleanup`。
- `Slice Validation` 已成为独立章节，不再只等同于 product-code rules。
- `phase0-manifest.json`、`restore-instructions.md`、`git apply --check` 替代验证、review worktree 清理、多分支脏线、`--porcelain=v1` 都已有项目级落点。
- MyStocks 特有约束已纳入：PM2 服务、GitNexus staged-scope 检查、frontend 类型/E2E 实际结果报告、`architecture/STANDARDS.md` 删除判定口径。

当前 review 的主要作用不是重新否定指南，而是把上游 quantix review 中可复用的治理细节转成本项目后续执行检查项。

---

## 二、严重问题复核

### 2.1 编号体系错位

**上游问题**: 总流程定义 0-9，但后续章节编号漂移，且 `Explicit Approval Protocol`、`Generated And Runtime Artifacts` 作为无编号平行章节存在。

**MyStocks 当前状态**: 已采纳。

当前指南已使用步骤 0-9 作为主流程：

| 步骤 | 当前章节 |
|---|---|
| 0 | 冻结与清点 |
| 1 | 快照保全 |
| 2 | 脏线分类 |
| 3 | 创建干净审查工作树 |
| 4 | 切片提取 |
| 5 | 切片验证 |
| 6 | PR 与提交策略 |
| 7 | 根工作树对齐 |
| 8 | 残余未追踪文件处置 |
| 9 | 最终清理 |

**仍需保持的约束**:

- 不再新增无编号的平行主流程章节。
- 审批协议、生成产物处置、产品代码规则都应作为对应步骤内的子控制项。
- OpenSpec tasks 中已补充“确认 0-9 step map 为权威序列”的检查项。

---

## 三、中等问题复核

### 3.1 分类信息双重存在

**上游问题**: Inventory bucket 表和 Classification class 表重复且粒度不同，增加维护成本。

**MyStocks 当前状态**: 部分采纳，仍需执行期收口。

当前指南保留了“当前状态评估/脏线分类预估”和步骤 2 的分类体系。两者并非完全重复，但存在后续 drift 风险：

- “当前状态评估”适合描述 2026-05-27 的观察快照。
- “步骤 2：脏线分类”应成为执行时唯一的 canonical classification manifest。

**建议**:

- 将 3.3 的分类表明确标注为“初始观察，不作为执行真相源”。
- 在步骤 2 产出一个 canonical manifest，后续 summary table 只能从该 manifest 派生。
- OpenSpec tasks 已补充 `3.1 Create a single canonical classification manifest`。

### 3.2 原则到步骤的映射引用准确性

**上游问题**: 映射表引用旧编号，且“不混提交”与 PR/commit strategy 的关系更直接。

**MyStocks 当前状态**: 已采纳。

当前映射已指向步骤 4、5、6、7 等新的主流程编号。后续若新增章节，必须先更新 0-9 主流程，再更新映射表，避免第二次漂移。

### 3.3 Slice Validation 语义漂移

**上游问题**: Slice validation 被缩窄为 Product Code Rules，遗漏文档、配置、生成物等切片验证。

**MyStocks 当前状态**: 已采纳。

当前指南已有步骤 5 `切片验证 (Slice Validation)`，并包含代码、影响分析、文档、配置等验证小节。

**建议**:

- 在后续执行中继续把 frontend/backend/Python/docs/OpenSpec/root config 作为不同验证子门禁。
- 不要把“代码测试通过”误写成所有切片都通过。

### 3.4 `git stash --include-untracked` 重复出现在禁令列表

**上游问题**: 同一高风险命令出现在多个禁令列表，造成维护重复。

**MyStocks 当前状态**: 基本采纳。

当前指南在高风险操作黑名单中集中列出 `git stash push --include-untracked`，OpenSpec tasks 也已要求该命令只保留在单一 high-risk/blocked-command list 中。

**建议**:

- 后续不要在其他章节重复建立第二份禁令表。
- 如需引用，链接到高风险操作黑名单，而不是复制整行。

---

## 四、轻微问题与改进建议复核

### 4.1 缺少关闭 clean review worktree 的清理步骤

**MyStocks 当前状态**: 已采纳。

当前 Final Cleanup 已包含：

- `git worktree remove .worktrees/<worktree-name>`
- `git branch -d <branch-name>`
- 清理步骤 3 创建的 `.worktrees/dirty-cleanup-review-base-2026-05-27`

**建议**: 最终报告必须列出 removed worktrees、retained exceptions 和仍保留原因。

### 4.2 `phase0-manifest.json` 未定义

**MyStocks 当前状态**: 已采纳，OpenSpec 已加严。

当前指南已有 `phase0-manifest.json` 示例。OpenSpec tasks 进一步要求最小字段：

- `created_at`
- `repo_path`
- `original_head`
- `original_branch`
- `tracked_diff_sha256`
- `tracked_diff_bytes`
- `untracked_archive_sha256`
- `untracked_archive_bytes`
- `inventory_errors`
- `missing_required_files`

### 4.3 `git apply --check` 验证限制未说明

**MyStocks 当前状态**: 已采纳。

当前指南已说明在当前脏树不适合执行时使用临时 clone 验证，并指出 `new file mode` 与本地状态不一致可能导致失败。

**建议**: 后续快照报告中要写清楚 `git apply --check` 是 sanity check，不等于完整恢复演练；涉及 binary、file mode、new file、deleted file、index divergence 时要额外验证。

### 4.4 恢复说明模板缺失

**MyStocks 当前状态**: 已采纳。

当前指南已包含 `restore-instructions.md` 模板，覆盖已追踪修改、未追踪文件、救援分支和 stash 恢复。

**建议**: OpenSpec recovery task 执行时必须生成真实文件，不只保留指南模板。

### 4.5 Acceptance Baselines 可操作性弱

**MyStocks 当前状态**: 部分采纳。

当前指南仍包含若干以“目标: 0”或“≤ 5”为代表的结果口径。对于可直接测量的项目可以保留为门禁；对依赖外部审批、工作树历史状态或尚未复核的统计，只能写为观察项。

**建议**:

- 可测量项：`git status --porcelain=v1`、`openspec validate --strict`、Markdown 结构检查。
- 观察项：过时 worktree 数、历史文档保留比例、无法归属的多分支脏线。
- OpenSpec tasks 已补充“无法精确测量的 acceptance baseline 降级为 observation”。

### 4.6 Recommended Document Set fallback 路径缺少目录前缀

**MyStocks 当前状态**: 待后续执行确认。

MyStocks 是 OpenSpec 项目，首选路径应继续使用：

- `openspec/changes/<change-id>/proposal.md`
- `openspec/changes/<change-id>/design.md`
- `openspec/changes/<change-id>/tasks.md`
- `openspec/changes/<change-id>/specs/<capability>/spec.md`

非 OpenSpec fallback 不应落在仓库根目录，应使用：

- `docs/reports/cleanup/DIRTY_WORKTREE_CLEANUP_PLAN_YYYY-MM-DD.md`
- `docs/reports/cleanup/DIRTY_WORKTREE_CLEANUP_TASKS_YYYY-MM-DD.md`
- `docs/reports/cleanup/DIRTY_WORKTREE_CLEANUP_POLICY.md`
- `docs/reports/cleanup/DIRTY_WORKTREE_CLEANUP_CLOSURE_SUMMARY_YYYY-MM-DD.md`
- `var/recovery/dirty-worktree-YYYY-MM-DD/restore-instructions.md`

### 4.7 缺少多分支脏线处理提示

**MyStocks 当前状态**: 已采纳。

当前指南已有“忽略多分支脏线”风险说明；OpenSpec tasks 已补充将 dirty paths 映射到 active worktrees、branches、PRs 或 OpenSpec changes 后再分配 owner。

### 4.8 命令附录技术栈耦合

**MyStocks 当前状态**: 已适配。

MyStocks 不应继承 quantix 的 Rust/Cargo 命令。项目执行命令应以 Python/Vue/FastAPI/Vite 为准，例如：

- `pytest`
- `ruff check`
- `cd web/frontend && npm run lint`
- `cd web/frontend && npm run test`
- `openspec validate <change-id> --strict`

### 4.9 缺少 `--porcelain=v1` 选择说明

**MyStocks 当前状态**: 已采纳。

当前指南已注明 `git status --porcelain=v1` 用于最大兼容性。机器解析路径时应使用 `-z`，避免空格、换行、中文路径或特殊字符造成解析错误。

### 4.10 Root clean 误判

**MyStocks 当前状态**: 已采纳。

当前指南已新增 `9.6 Root worktree clean 误判`。该条明确说明 root `git status` 为空只代表当前 root worktree 干净，不代表所有 registered worktree、WIP 分支、测试日志或未追踪文档都已清理。

**建议**:

- Final closeout 必须枚举 `git worktree list --porcelain`。
- 对每个 worktree 运行 `git -C <worktree-path> status --porcelain=v1`。
- 最终报告必须区分“root clean”和“whole repository cleanup complete”。

### 4.11 版本化 ignore 滥用

**MyStocks 当前状态**: 已采纳。

当前指南已新增 `9.7 版本化 ignore 滥用`。本机日志、临时报告和个人工具噪声不得直接进入版本化 `.gitignore`，否则会把单机习惯升级为团队规则。

**建议**:

- 单机噪声使用 `.git/info/exclude`。
- 只有团队共享、稳定复现、跨环境一致的 local-only 路径才允许进入版本化 `.gitignore`。
- `.gitignore` 变更必须说明路径来源、复现条件和团队共性。

### 4.12 Squash merge 分支判断误判

**MyStocks 当前状态**: 已采纳。

当前指南已新增 `9.8 Squash merge 分支判断误判`。Squash merge 后 topic branch 的原始 commit 不会逐个进入主干，`git branch --merged` 不能单独作为删除 branch/worktree 的依据。

**建议**:

- 同时检查 PR state、`mergedAt`、ahead/behind、`merge-base` 和文件级 diff。
- 删除分支或 worktree 前必须有 owner 确认。
- `git branch --merged` 只能作为辅助信号。

### 4.13 误删有实质 WIP 的 worktree

**MyStocks 当前状态**: 已采纳。

当前指南已新增 `9.9 误删有实质 WIP 的 worktree`。worktree 可能包含代码 diff、测试更新、未追踪计划文档或恢复材料，不能当作普通临时目录删除。

**建议**:

- 删除前记录 worktree status、branch、recent log 和 untracked files。
- 有实质 WIP 时，先提交到当前本地分支、生成 handoff，或归入单独 cleanup slice。
- 禁止用 `.gitignore` 掩盖实质 WIP。

### 4.14 误删 rescue 分支

**MyStocks 当前状态**: 已采纳。

当前指南已新增 `9.10 误删 rescue 分支`。`rescue/*` 分支若领先主干，通常是恢复包的 Git 指针；提前删除会削弱 root realignment 或误清理后的回滚能力。

**建议**:

- `rescue/*` 至少保留到恢复包外部归档、路径级 disposition、owner 批准和最终 closeout 完成。
- 删除时必须记录分支名、HEAD、删除原因和替代恢复路径。
- OpenSpec spec delta 已新增 `Rescue branches are retained until recovery is closed` 场景。

---

## 五、项目级补充意见

### 5.1 OpenSpec 与执行指南必须保持同步

当前 dirty-worktree 清理已建立 OpenSpec change：

- `openspec/changes/implement-dirty-worktree-cleanup-governance/`

后续修改指南时，应同步检查：

- `proposal.md`
- `design.md`
- `tasks.md`
- `specs/directory-governance/spec.md`

并运行：

```bash
openspec validate implement-dirty-worktree-cleanup-governance --strict
```

### 5.2 GitNexus staged-scope 是本项目额外硬约束

在 MyStocks 的 dirty worktree 场景中，不得用 `gitnexus_detect_changes(scope="unstaged")` 作为当前微批次风险结论。必须先 stage 本批次目标文件，再运行 staged-scope 检查。

### 5.3 前端收尾报告必须使用实际 E2E 结果

任何前端切片完成时，必须报告实际执行命令、浏览器项目、用例总数、通过/失败/跳过数量，不得沿用历史固定 `18/18` 文案。

### 5.4 删除判定必须回到 `architecture/STANDARDS.md`

对于 `*_new.py`、shim、archive、legacy、`.bak`、`.backup`、`part1/part2/part3`、历史报告和未引用文件，不能仅凭搜索结果删除。必须按 `architecture/STANDARDS.md` 的迁移收口与技术债治理规则判断：

- 是否仍承担兼容职责
- 是否有运行时字符串映射、动态导入、路由、菜单、注册表或构建脚本引用
- 是否属于有效、兼容保留、实验/灰度、重复冗余或待判定
- 是否存在可恢复路径和最终收口条件

---

## 六、推荐后续动作

1. 保持 `DIRTY_WORKTREE_CLEANUP_GUIDE.md` 为执行指南，保持本文为 review 记录。
2. 先审批并执行 OpenSpec change `implement-dirty-worktree-cleanup-governance`。
3. 在执行任务 `3. Classification` 时生成唯一 canonical classification manifest。
4. 在执行任务 `4. Clean Review Worktree And Slice Protocol` 时记录 review worktree 生命周期。
5. 每个切片完成后更新 `docs/reports/cleanup/` 下的执行证据，不回写成根目录散落文件。
6. 最终 closeout 时同时更新本文的“当前状态”或新增 closure review。

---

## 七、结论

MyStocks 当前指南已基本采纳 quantix updated review 的关键结构修正。剩余风险主要不在文档结构，而在执行阶段是否严格遵守：

- 快照先行
- 单一分类真相源
- 干净 worktree 提取
- 切片验证
- staged-scope GitNexus 检查
- root realignment 后置
- final cleanup 清理临时 worktree 和残余例外

在 OpenSpec change 被批准前，不建议继续推进任何高风险脏线清理动作。
