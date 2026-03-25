# 目录整理文档重写审核报告

**审核对象**:

- `docs/standards/DIRECTORY_AND_FILE_ORGANIZATION_RULES.md`
- `docs/reports/cleanup/directory-organization/DIRECTORY_ORGANIZATION_PLAN.md`

**交叉核对依据**:

- `architecture/STANDARDS.md`
- `AGENTS.md`
- `governance/mainline/policies/directory-structure.yaml`
- `scripts/hooks/check_directory_structure.py`
- `scripts/tree-lint.sh`
- 当前仓库目录现状与现有脚本入口

**审核日期**: 2026-03-23  
**审核结论**: 可作为后续审批基线，仍需用户批准后才能执行实际迁移

---

## 一、总体结论

重写后的两份文档已经从“理想化目录模板”切换为“治理优先、兼容优先、分阶段收敛”的口径，和当前仓库的真实约束基本一致。

本次重写解决了旧版文档中的三个核心问题：

1. 不再把“九大顶层目录模型”误写成 MyStocks 的强制落地目标
2. 不再建议移动会破坏当前工作流的根目录契约文件
3. 不再引用仓库中不存在的脚本或未经验证的回滚路径

---

## 二、已解决的一致性问题

### 1. 根目录口径已统一

新版规则与方案都明确区分了两件事：

- “根目录应精简”是治理目标
- “自动发现入口与工作流契约可保留在根目录”是现实约束

这修正了旧版“既要求清空根目录、又保留大量根目录入口”的内在矛盾。

### 2. `.FILE_OWNERSHIP`、`TASK.md`、`TASK-REPORT.md` 已被正确保护

新版方案不再建议移动或删除这些文件，而是把它们纳入受保护对象与审批清单。

### 3. 配置文件治理改为“主配置收敛 + 根目录兼容入口”

新版方案不再直接要求把根目录 Playwright/PM2/Vitest 入口搬走，而是要求先迁移调用方，再决定是否保留兼容包装。

对于 Docker 资产，当前口径进一步明确为：

- `docker/` 是 canonical 目录
- 根目录 `docker-compose.prod.yml`、`docker-compose.test.yml`、`monitoring-stack.yml` 只保留兼容 symlink 入口
- `config/docker/` 与 `config/docker-infra/` 只保留兼容 symlink

因此，根目录这几个 yml 从“物理归属”上已经完成下沉，不再是下一步优先迁移对象。

### 4. `scripts/tests/` 改为文件级分类治理

新版方案不再把 `scripts/tests/` 机械视为“应该整体迁移到 `tests/` 的目录”，而是区分：

- pytest 测试
- runner 脚本
- 报告
- fixtures / 示例工程

### 5. 审核口径已回到“仓库事实”

新版文档只保留了仓库中能找到的对象、脚本和命令：

- `scripts/dev/tools/docs_indexer.py`
- `scripts/hooks/check_directory_structure.py`
- `scripts/tree-lint.sh`
- `governance/mainline/policies/directory-structure.yaml`

不再引用不存在的 `scripts/tools/docs_indexer.py` 或 `scripts/dev/rollback_migration.py`。

### 6. 根目录运行日志已完成收口

执行阶段已将根目录 `logs/` 的活跃落点迁移到 `var/log/`，并同步更新了 logging、PM2、安全扫描和测试脚本中的主要运行时路径。

### 7. 剩余 root tolerated files 已完成收敛

执行阶段已进一步完成以下收敛：

- `FUNCTION_MAP.md` → `docs/overview/FUNCTION_MAP.md`
- `rewrite_public_history.sh` 与其过滤规则文件 → `scripts/maintenance/public-history/`
- 根目录 `run-api-tests.sh` 兼容包装已移除，CI 与测试统一改为 `scripts/tests/run-api-tests.sh`

---

## 三、当前仍保留的审批门槛

以下事项在文档上已被正确标记，但仍需要用户审批后才能进入执行：

| 事项 | 当前状态 | 备注 |
|------|----------|------|
| 根目录生成物清理 | 可执行候选 | 需结合 `.gitignore` 一并处理 |
| `archived/` / `.archive/` 收敛 | 可执行候选 | 需先区分历史归档与运行备份 |
| `docs/` 家族收敛 | 可执行候选 | 需逐类更新链接与索引 |
| `scripts/tests/` 分类治理 | 待详细清单 | 不能整目录搬迁 |
| 根目录配置入口迁移 | 高风险待批 | 必须先迁移调用方 |
| `architecture/` 与 `docs/architecture/` 是否合并 | 单独议题 | 不应混入本轮整理 |
| hook / policy 根目录白名单同步 | 持续维护项 | 已补齐主漂移，后续新增根入口仍需同步更新测试与 hook |
| `docs/function-classification-manual/` 迁移 | 已收敛 | 生成脚本已切换到 `docs/references/function-classification-manual/` |

---

## 四、残余风险

### 1. 仓库治理入口之间仍需持续同步，但根目录白名单主漂移已收口

此前存在的一个真实问题是：目录治理策略已经允许部分根目录入口，但 `check_directory_structure.py` 的根目录白名单没有完全同步，容易在继续整理时误判。

当前更准确的结论是：

- `directory-structure.yaml` 已把 `.FILE_OWNERSHIP`、`TASK.md`、`TASK-REPORT.md` 作为 workflow exception 管理
- 已跟踪的根目录 dotfile（如 `.gitignore`、`.gitattributes`、`.mcp.json`、`.pre-commit-config.yaml`、`.pylintrc`）已进入显式治理口径，而不是继续依赖“扫描器默认跳过隐藏文件”
- 根目录 Docker 兼容入口已通过测试固定为指向 `docker/` 的 symlink
- `check_directory_structure.py` 与 `tree-lint.sh` 都应与这些治理口径保持同步；其中 `tree-lint.sh` 还需跳过已被 `.gitignore` 忽略的本地态 root dotfile，避免把本地工具文件误报为仓库结构违规
- `opencode.json`、`tui.json` 当前都已从显式 root allowlist 降级为 gitignored local-only 配置；仓库治理只需保证它们不会被误纳入 allowlist，也不会因为本地存在而触发误报
- 已退役的 `.aider.*` root dotfile 已从仓库工作区移除，但对应 `.gitignore` 规则仍应保留，避免本地重建时重新污染根目录治理视图

这类问题属于**治理同步维护项**，但不再应被表述为“根目录 Docker 文件尚未下沉”或“.FILE_OWNERSHIP 尚未进入治理”。

### 2. 顶层 `architecture/` 与 `docs/architecture/` 的双归属仍未彻底消解

新版方案选择了更稳妥的处理方式：

- 先定义边界
- 不在本轮目录整理里强行合并

这降低了执行风险，但保留了一个后续需要单独决策的议题。

### 3. 文档收敛工作量依然不小

`docs/` 顶层子目录当前接近 40 个，真正执行时仍需要：

- 分类盘点
- 更新索引
- 更新链接
- 逐批提交与回滚控制

因此本方案适合作为审批与执行基线，但不应理解为“几条命令即可完成”的轻量工作。

### 4. 归档收敛宜采用保守命名空间

对 `archived/` 和 `.archive/` 的收敛，不建议直接平铺并入已有 `archive/docs/`、`archive/legacy-docs/`、`archive/legacy-root-archived/` 子树。更稳妥的方式是先以独立命名空间收口，例如：

- `archive/legacy-root-archived/archived-root/`
- `archive/legacy-dot-archive/`

这样可以先完成根目录生命周期收口，再决定后续是否做二次细分整理。

### 5. `docs/web-dev/` 应作为特殊工作目录保留

当前 `docs/web-dev/` 不只是普通指南目录，它还承载：

- `docs/web-dev/GUIDE.md` 等 Web 工作流入口说明
- 与 Web 文档整理 hook 直接相关的工作约定

同时，运行态追踪日志已经更适合收敛到：

- `var/log/web-dev/tracing/web-edit-tracker.jsonl`

因此更合理的做法是：

- 将其明确标注为“特殊保留目录”
- 在收尾文档中说明其定位为“说明/入口目录”，而非运行态产物目录
- 暂不并入 `docs/guides/`

### 6. `docs/design/` 与 `docs/plans/` 现阶段不适合机械迁移

当前更稳妥的结论是：

- `docs/design/` 作为设计资料混合目录保留，先修入口与死链，再做子类分流
- `docs/plans/` 作为规划与实施计划目录保留，因其已被 README、OpenSpec、脚本和任务文档广泛引用

### 7. Docker 目录已完成“主目录提升 + 兼容层保留”

当前更合理的口径是：

- 根级 `docker/` 作为 Docker 资产的 canonical 路径
- `config/docker/` 与 `config/docker-infra/` 作为兼容 symlink 保留
- 根级 `docker-compose*.yml` 与 `monitoring-stack.yml` 保持符号链接入口，避免破坏自动发现与现有脚本

因此，若继续做根目录收敛，优先级应放在运行产物、缓存、备份和散装报告，而不是再次尝试移除这些根级 Compose 兼容入口。

---

## 五、推荐结论

建议将当前两份文档作为新的目录整理基线，并按以下顺序推进：

1. 先审批文档
2. 再补齐治理策略与工作流例外同步
3. 最后进入 Phase 1 根目录卫生清理

如果后续要真正执行目录迁移，应以 [DIRECTORY_ORGANIZATION_PLAN.md](../cleanup/directory-organization/DIRECTORY_ORGANIZATION_PLAN.md) 为唯一项目级实施方案，不再参考旧版审核结论。

---

**结语**: 这份审核报告只确认“文档是否已经说对”。它不等同于“目录整理已经可以无条件执行”；真正执行仍以审批状态和当时的仓库调用方盘点结果为准。
