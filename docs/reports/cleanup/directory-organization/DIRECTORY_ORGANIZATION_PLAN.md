# MyStocks 项目目录整理方案

**版本**: v3.0  
**创建日期**: 2026-03-23  
**基于规范**: [目录与文件整理通用规则](../standards/DIRECTORY_AND_FILE_ORGANIZATION_RULES.md)  
**状态**: 待审批

---

## 一、目标与范围

本方案的目标不是把仓库强行压缩成某个“理想模板”，而是在**不破坏现有工作流、治理门禁、自动发现入口和运行脚本**的前提下，分阶段收敛目录结构。

本次整理聚焦四类问题：

1. 根目录存在真实的生成物、缓存、备份和杂项文件
2. `docs/` 顶层子目录过多，职责边界不清
3. `archive/`、`archived/`、`.archive/` 生命周期位置分裂
4. `scripts/tests/`、报告目录、配置目录存在混放与重复收敛问题

本方案**不**做以下事情：

- 不把所有根目录配置一刀切移入 `config/`
- 不移动 `.FILE_OWNERSHIP`、`TASK.md`、`TASK-REPORT.md`
- 不在本方案中强制合并 `architecture/` 与 `docs/architecture/`
- 不在未验证调用方前移除根目录兼容入口：`docker-compose.prod.yml`、`docker-compose.test.yml`、`monitoring-stack.yml`
- 不在未验证调用方前移动 `playwright.config.ts`、`vitest.config.mts`、`ecosystem.test.config.js`
- 不把 `scripts/tests/` 整体机械搬到 `tests/`

---

## 二、当前执行时必须遵守的约束

### 2.1 方案审批门禁

目录整理属于结构性变更。执行任何实际移动前，必须遵守 [STANDARDS.md](../../architecture/STANDARDS.md) 的审批要求。

### 2.2 当前仓库的事实性治理入口

当前仓库已经存在下列事实性门禁，它们比“理想目录模型”更高优先级：

- [AGENTS.md](../../AGENTS.md) 中的主分支/worker 协作规则
- [directory-structure.yaml](../../governance/mainline/policies/directory-structure.yaml) 中的根目录 allowlist、workflow exception、tolerated 规则
- [check_directory_structure.py](../../scripts/hooks/check_directory_structure.py) 中的新增文件位置检查
- [tree-lint.sh](../../scripts/tree-lint.sh) 中的根目录巡检逻辑
- 现有脚本和 package script 对根目录入口文件的直接依赖

### 2.3 当前必须视为“受保护”的对象

以下对象在本次整理中默认视为**受保护对象**，除非另有单独审批：

| 路径 | 保护原因 |
|------|----------|
| `.FILE_OWNERSHIP` | `main` 分支协作 owner 分配依赖 |
| `TASK.md` | Multi-CLI 根目录工作流契约 |
| `TASK-REPORT.md` | Multi-CLI 根目录工作流契约 |
| `playwright.config.ts` | 根目录 Playwright 入口，现有脚本直接引用 |
| `vitest.config.mts` | 根目录 Vitest 入口，受治理策略显式允许 |
| `ecosystem.test.config.js` | PM2/E2E 脚本直接引用 |
| `docker-compose.prod.yml` | 根目录 Compose 兼容入口，canonical 文件已下沉到 `docker/` |
| `docker-compose.test.yml` | 根目录 Compose 兼容入口，canonical 文件已下沉到 `docker/` |
| `monitoring-stack.yml` | 根目录监控栈兼容入口，canonical 文件已下沉到 `docker/` |
| `web/` | 独立 Web 子模块 |
| `openspec/` | 规范系统 |
| `monitoring-stack/` | 独立监控栈目录 |
| `architecture/STANDARDS.md` | 全仓统一工程红线 |
| `.env*` | 本地环境配置，需先验证发现机制 |

---

## 三、经核实的当前基线

### 3.1 根目录问题不止“文件多”，而是“类型混杂”

根目录当前同时存在三类对象：

1. **合法且必须保留的入口**
   - `docker-compose.prod.yml`（根目录 symlink 入口 → `docker/docker-compose.prod.yml`）
   - `docker-compose.test.yml`（根目录 symlink 入口 → `docker/docker-compose.test.yml`）
   - `monitoring-stack.yml`（根目录 symlink 入口 → `docker/monitoring-stack.yml`）
   - `playwright.config.ts`
   - `vitest.config.mts`
   - `ecosystem.test.config.js`
   - `TASK.md`
   - `TASK-REPORT.md`
   - `.FILE_OWNERSHIP`

2. **待评估的工具/环境配置**
   - `.env*`

### 3.1.3 根目录 dotfile 的当前治理结论

当前应区分两类根目录 dotfile：

- **已跟踪且属于仓库治理入口的 dotfile**：
  - `.gitignore`
  - `.gitattributes`
  - `.mcp.json`
  - `.pre-commit-config.yaml`
  - `.pre-commit-hooks.yaml`
  - `.pylintrc`
  - `.pylint.test.rc`
  - `.env.example`
  - `.FILE_OWNERSHIP`

这类文件当前已经纳入显式治理：

- 在 `directory-structure.yaml` 中登记为 `allowed_files` 或 `workflow_exception_files`
- 在 `check_directory_structure.py` / `tree-lint.sh` 中有对应 allowlist
- `tree-lint.sh` 对已被 `.gitignore` 忽略的本地态 root dotfile 采取跳过策略，不将其视为仓库结构违规

- **未入库的本地环境 dotfile**：
  - `.env.async_monitoring`
  - `.env.data-sources.local`

这类文件当前更适合视为“本地态配置”，不应在未统一发现机制前强行纳入仓库主 policy，更不建议在本轮整理中机械迁移。

- **已退役的本地工具 dotfile**：
  - `.aider.conf.yml`
  - `.aider.model.*`
  - `.aiderignore`

这类文件在对应 CLI/tool 退役后可以直接删除；但 `.gitignore` 仍应保留相应忽略规则，防止本地再次生成时误入仓库治理口径。

- **未入库的本地工具根配置**：
  - `opencode.json`
  - `tui.json`

这类文件虽然位于根目录，但当前已明确按“gitignored 本地态配置”处理：

- 不再纳入 `directory-structure.yaml` 的显式 `allowed_files`
- 不再进入 `check_directory_structure.py` / `tree-lint.sh` 的根目录 allowlist
- 仅当本地工具需要时保留于工作区；对仓库治理视角而言，应被视为“本地存在但不入库”的对象

3. **明显应清理或收敛的杂项/生成物**
   - `.coverage`
   - `coverage.xml`
   - `htmlcov/`
   - `opencode.json.bak.*`
   - `opencode.json.tui-migration.bak`
   - 孤立文件 `1`

4. **运行态目录已收敛的对象**
   - 运行日志已统一收敛到 `var/log/`
   - 根目录 `logs/` 不再作为允许保留对象

### 3.1.1 关于根目录 `docker-compose.*.yml` 的当前结论

当前仓库对 Docker 资产的处理方式已经不是“文件还堆在根目录”，而是：

- `docker/` 是 Docker / Compose 资产的 canonical 目录
- 根目录 `docker-compose.prod.yml`、`docker-compose.test.yml`、`monitoring-stack.yml` 只是兼容 symlink 入口
- `config/docker/` 与 `config/docker-infra/` 也仅作为历史兼容 symlink 保留

这意味着：

- 从“物理归属”看，它们已经放进了 `docker/`
- 从“使用体验与自动发现”看，根目录仍保留短路径入口，避免破坏现有脚本、README、测试和人工操作习惯

因此，本轮整理的重点不再是“把这几个 yml 再搬一次”，而是维持 `docker/` 为主、根目录入口为兼容层的治理口径。

### 3.1.2 根目录剩余文件的建议边界

下一步更值得继续收纳的是：

- 运行产物与缓存：`.coverage`、`coverage.xml`、`htmlcov/`、`.pytest_cache/`、`.mypy_cache/`
- 备份与临时文件：`*.bak`、`*.tmp`、孤立文件、散装导出
- 需先验证发现机制的工具配置：`.env*`（只有在调用方迁移完成后才考虑进一步收纳）
- 本地态工具配置：`opencode.json`、`tui.json`（当前按 gitignored local-only 处理，不纳入显式根目录治理）

当前不建议继续移动的根目录文件包括：

- 工具自动发现入口：`pyproject.toml`、`pytest.ini`、`mypy.ini`、`package.json`、`package-lock.json`、`playwright.config.ts`、`vitest.config.mts`、`ecosystem.test.config.js`
- 工作流契约：`.FILE_OWNERSHIP`、`TASK.md`、`TASK-REPORT.md`
- 兼容导出入口：`core.py`、`data_access.py`、`monitoring.py`、`unified_manager.py`
- 项目/治理入口：`README.md`、`LICENSE`、`AGENTS.md`、`CLAUDE.md`、`IFLOW.md`、`CHANGELOG.md`

### 3.2 `docs/` 顶层子目录当前为 39 个

这是事实性的文档碎片化问题，但不能靠一次“批量重命名”粗暴解决。原因是：

- 有些目录是说明文档
- 有些目录是审计/报告
- 有些目录混合了现行内容与历史内容
- 有些目录已被索引、README、执行指南引用

### 3.3 归档目录已经出现三处生命周期位置

当前同时存在：

- `archive/`
- `archived/`
- `.archive/`

此外，治理策略还把 `archived/` 视为 tolerated historical materials，说明它已进入“需要收敛但尚未完成”的状态。

### 3.4 `scripts/tests/` 不是纯粹的 pytest 测试目录

经核实，`scripts/tests/` 内混有：

- Python 测试脚本
- Shell/Node runner
- 压测与演示脚本
- 测试报告
- 小型样例工程

因此不能简单下结论“全部迁移到 `tests/`”。

---

## 四、目标状态

本方案的目标状态如下：

### 4.1 根目录

- 保留真实入口与审批过的工作流例外
- 清理明显的生成物、缓存、备份和孤立文件
- 把“为什么某些文件仍留在根目录”写入治理而不是靠默认认知

### 4.2 文档体系

`docs/` 顶层目录最终收敛到一组**稳定家族**，推荐如下：

- `docs/overview/`
- `docs/guides/`
- `docs/api/`
- `docs/architecture/`
- `docs/standards/`
- `docs/operations/`
- `docs/testing/`
- `docs/reports/`
- `docs/references/`
- `docs/examples/`
- `docs/archive/`

说明：

- 顶层 `architecture/` 本次继续承担“仓库级架构规范/ADR/工程红线”职责
- `docs/architecture/` 继续承载“领域设计、方案、实现说明、历史设计文档”
- 二者是否合并，单列为后续高风险议题

### 4.2.1 `docs/` 根层最终边界

完成本轮收敛后，`docs/` 根层按以下边界冻结：

- `docs/INDEX.md`
- `docs/FUNCTION_TREE.md`

说明：

- `docs/INDEX.md` 是文档总入口与自动生成索引。
- `docs/FUNCTION_TREE.md` 是当前治理总线文档，承担功能域、入口映射和维护规则，不纳入低风险机械迁移范围。
- 新增普通说明文档默认不得直接落在 `docs/` 根层，应优先归入 `overview/`、`guides/`、`reports/`、`standards/` 等稳定家族。

### 4.3 生命周期位置

- 历史保留物统一收敛到 `archive/`
- 运行态输出优先收敛到 `var/`
- 生成型报告优先收敛到 `reports/` 或 `var/reports/`

### 4.4 配置体系

- `config/` 继续作为主收敛目录
- 对外仍需根目录自动发现的配置，采用“`config/` 为主、根目录兼容入口为辅”的方式逐步收敛
- Docker 资产当前已提升到根级 `docker/`，`config/docker/` 与 `config/docker-infra/` 仅作为兼容 symlink 保留

---

## 五、硬门槛与禁止项

### 5.1 未满足以下条件前，禁止执行对应移动

| 对象 | 禁止条件 | 允许进入执行的前提 |
|------|----------|--------------------|
| `.FILE_OWNERSHIP` | 未同步 AGENTS 与治理策略 | 单独审批并完成工作流替代 |
| `TASK.md` / `TASK-REPORT.md` | 仍为根目录协作契约 | 工作流替代方案落地并获批 |
| `playwright.config.ts` | 仍被脚本/package script直接引用 | 所有调用方迁移完成，保留兼容包装或批准删除 |
| `vitest.config.mts` | 仍被根目录工具链使用 | 调用方迁移与验证完成 |
| `ecosystem.test.config.js` | `scripts/run_e2e_pm2.sh` 仍直接调用 | PM2/E2E 脚本迁移完成 |
| `docker-compose.prod.yml` / `docker-compose.test.yml` / `monitoring-stack.yml` | 当前已是根目录兼容 symlink，仍被脚本/文档/人工命令作为短路径入口使用 | 只有在调用方全面迁移且短路径不再需要时，才评估是否移除根入口 |
| `.env*` | 工具发现机制未核实 | 工具侧明确支持新位置 |
| `scripts/tests/` | 未完成目录内资产分类 | 形成文件级清单后再分流 |

### 5.2 当前明确不做的动作

- 不把根目录强制压缩成“只剩九大目录”
- 不删除任何仅凭静态搜索判断“未使用”的对象
- 不在本次方案里统一重写所有文档链接
- 不引用不存在的迁移脚本或回滚脚本

---

## 六、分阶段执行方案

### Phase 0: 文档与治理对齐

**优先级**: P0  
**目标**: 在动任何文件前，先把“规则、方案、审核口径”统一

**工作项**:

1. 重写目录整理通用规则，明确“通用基线 != 仓库最终 allowlist”
2. 重写本方案，改为与当前治理脚本、AGENTS 和实际入口一致
3. 重写审核报告，清理错误结论
4. 准备后续治理同步清单：
   - 是否将 `.FILE_OWNERSHIP` 显式纳入根目录例外
   - 哪些根目录入口是长期保留，哪些是兼容包装

**验收**:

- 规则、方案、审核报告三份文档结论一致
- 所有命令路径、脚本路径、保护对象都能在仓库中找到

---

### Phase 1: 根目录卫生清理

**优先级**: P0  
**目标**: 先处理明显的生成物与无归属对象，不碰自动发现入口

**建议处理对象**:

- `.coverage`
- `coverage.xml`
- `htmlcov/`
- `opencode.json.bak.*`
- `opencode.json.tui-migration.bak`
- 孤立文件 `1`
- 根目录缓存目录：`.mypy_cache/`、`.pytest_cache/`

**处理原则**:

- 生成物优先移出版本控制或纳入 `.gitignore`
- 需要保留的备份移动到 `archive/` 或 `var/backups/`
- 不在本阶段移动根目录工具链入口

**验收**:

- 根目录不再保留无归属生成物
- 治理策略中的 forbidden patterns 显著减少命中

---

### Phase 2: 归档位置收敛

**优先级**: P1  
**目标**: 收敛 `archive/`、`archived/`、`.archive/`

**执行方向**:

- `archived/` 内容收敛到 `archive/legacy-root-archived/archived-root/`
- `.archive/` 内容收敛到 `archive/legacy-dot-archive/`
- 运营备份类内容视情况收敛到 `var/backups/`

**执行要求**:

- 逐目录确认“历史归档”还是“运行备份”
- 对有受 Git 跟踪文件的目录使用 `git mv`
- 对仅包含空目录、无受 Git 跟踪文件的历史树，允许使用文件系统移动
- 保留原语义，不做顺手重构

**验收**:

- `archived/` 不再作为常规存量目录
- `.archive/` 清空或删除
- `archive/` 下按历史代码/历史文档/迁移记录/工具归档分类

---

### Phase 3: `docs/` 家族收敛

**优先级**: P1  
**目标**: 从 39 个顶层子目录收敛到稳定家族

**推荐家族路由表**:

| 当前目录族群 | 目标家族 | 说明 |
|--------------|----------|------|
| `docs/ai_tools/`, `docs/features/`, `docs/frontend/`, `docs/openspec_cmd/`, `docs/superpowers/`, `docs/tdx_integration/`, `docs/web/`, `docs/ui-ux-pro-max/` | `docs/guides/` | 使用说明、开发指南、工具使用；已执行的低风险子批次包括 `docs/guides/ai-tools/`、`docs/guides/openspec-cmd/`、`docs/guides/tdx-integration/`、`docs/guides/features/`、`docs/guides/superpowers/`、`docs/guides/ui-ux-pro-max/` 与 `docs/guides/web/` |
| `docs/web-dev/` | 特殊保留 | Web 工作流说明与入口目录，当前由 hook 说明和工作约定直接依赖；运行态追踪日志已迁至 `var/log/web-dev/tracing/`，不按普通 guides 家族迁移 |
| `docs/ci-cd/`, `docs/deployment/`, `docs/monitoring/` | `docs/operations/` | 运维、部署、CI/CD |
| `docs/04-测试/`, `docs/e2e/` | `docs/testing/` | 测试方法、测试说明；低风险执行时可分别收敛到 `docs/testing/legacy-cn/04-测试/` 与 `docs/testing/e2e/` |
| `docs/function-classification-manual/`, `docs/examples/` | `docs/references/` | 参考资料、辅助材料；`function-classification-manual` 已完成脚本解耦后迁入 `docs/references/function-classification-manual/`，示例脚本已迁入 `docs/references/examples/` |
| `docs/legacy/` | `docs/archive/` 或 `archive/docs/` | 历史文档 |
| `docs/cli_reports/`, `docs/reviews/`, `docs/tasks/`, `docs/technical_debt/`, `docs/worklogs/`, `docs/performance/` | `docs/reports/` 或 `reports/` | 先按“叙述型/生成型”二分，再决定落点；已执行的低风险子批次包括 `docs/reports/tasks/legacy/` |
| `docs/code_quality/`, `docs/quality/`, `docs/security/` | `docs/standards/` / `docs/reports/` | 规范文档进 `standards`，审计结果进 `reports`；已执行的低风险子批次包括 `docs/standards/security/SECURITY_BEST_PRACTICES.md`、`docs/reports/code_quality/` 与 `docs/reports/quality/` |
| `docs/design/` | 特殊保留 | 混合承载设计规范、设计工具说明、HTML 样例与阶段性更新方案，需专题分流 |
| `docs/plans/` | 特殊保留 | 规划与实施计划目录，被 README、OpenSpec 与脚本直接引用，当前不迁移 |
| `docs/docs/` | 验证后删除或并入目标家族 | 先确认是否为空聚合目录 |

**特别说明**:

- `docs/api/`、`docs/guides/`、`docs/operations/`、`docs/overview/`、`docs/testing/`、`docs/reports/`、`docs/standards/` 可直接作为保留家族
- `docs/architecture/` 本次保留，不与顶层 `architecture/` 混并

**验收**:

- 每个顶层 docs 目录要么属于 canonical family，要么被标记为兼容/历史目录
- `docs/INDEX.md` 与受影响子目录索引更新

---

### Phase 4: 报告与生成物收敛

**优先级**: P1  
**目标**: 区分“叙述型报告”与“机器生成产物”

**收敛规则**:

- Markdown 叙述型审核、复盘、方案评审保留在 `docs/reports/`
- JSON/HTML/截图/批量测试结果优先进入 `reports/` 或 `var/reports/`
- 不再把大量生成物长期放在 `docs/reports/`

**验收**:

- `reports/` 承接机器生成报告
- `docs/reports/` 主要保留人类阅读型结论文档

---

### Phase 5: `scripts/tests/` 分类治理

**优先级**: P2  
**目标**: 不再把 `scripts/tests/` 视为一个单一目录类型

**分类规则**:

| 类型 | 目标位置 |
|------|----------|
| 被 pytest 收集的 Python 测试 | `tests/` |
| 测试 runner、环境启动脚本、外部工具桥接脚本 | `scripts/testing/` |
| 测试报告与结果快照 | `reports/testing/` 或 `var/reports/testing/` |
| 测试示例项目、fixture 工程 | `tests/fixtures/` 或 `docs/examples/` |

**要求**:

- 先生成文件级清单，再迁移
- 禁止整目录整体搬运

**验收**:

- `scripts/tests/` 中每一类对象都有明确归属
- 迁移后 pytest、脚本入口、测试说明仍可工作

---

### Phase 6: 配置收敛与兼容入口治理

**优先级**: P2  
**目标**: 把重复配置收敛到 `config/`，但不破坏发现机制

**执行策略**:

1. 在 `config/playwright/`、`config/pm2/` 维护主配置
2. 根目录入口保留为兼容包装，直到所有调用方迁移完成
3. `tui.json`、`.env*`、其他工具本地配置单独评估，不与 PM2/Playwright 同批迁移

**验收**:

- 配置主归属清晰
- 根目录自动发现入口仍可用
- 不出现“文档说在 `config/`，脚本仍写死根目录”的断裂状态

---

### Phase 7: 持续治理

**优先级**: P3  
**目标**: 让目录治理成为持续门禁，而不是一次性清理

**建议动作**:

1. 保持 [directory-structure.yaml](../../governance/mainline/policies/directory-structure.yaml) 与实际工作流同步
2. 使用 [check_directory_structure.py](../../scripts/hooks/check_directory_structure.py) 与 [tree-lint.sh](../../scripts/tree-lint.sh) 做日常检查
3. 文档新增或迁移后更新索引
4. 对根目录例外建立“批准原因 + 后续处理计划”

---

## 七、执行顺序与依赖

建议严格按以下顺序执行：

1. `Phase 0`
2. `Phase 1`
3. `Phase 2`
4. `Phase 3`
5. `Phase 4`
6. `Phase 5`
7. `Phase 6`
8. `Phase 7`

依赖关系说明：

- `Phase 0` 不完成，不进入任何文件移动
- `Phase 1` 与 `Phase 2` 先做，可快速降低根目录噪音
- `Phase 3` 与 `Phase 4` 应一起看待，避免“文档目录刚合并、报告又散回去”
- `Phase 5` 必须晚于前述文档/归档整理，因为它需要更细颗粒度的清单
- `Phase 6` 只能在调用方盘点完成后执行

---

## 八、验证方式

### 8.1 每个 Phase 完成后的通用检查

```bash
git status --short
bash scripts/tree-lint.sh
python scripts/dev/tools/docs_indexer.py --path docs/ --output docs/INDEX.md --categories
rg -n "old/path/or/name" docs scripts tests web src
```

### 8.2 与目录治理直接相关的现有检查

```bash
python scripts/hooks/check_directory_structure.py
pytest tests/unit/scripts/test_pm2_first_class_gate.py -q
pytest tests/unit/scripts/test_route_layout_pm2_gate.py -q
pytest tests/unit/scripts/test_pm2_first_class_gate_integration.py -q
pytest tests/unit/scripts/test_route_layout_pm2_gate_integration.py -q
```

说明：

- `check_directory_structure.py` 主要检查新增/暂存文件位置
- `tree-lint.sh` 适合巡检根目录和脚本目录
- `docs_indexer.py` 的真实路径是 `scripts/dev/tools/docs_indexer.py`

---

## 九、回滚策略

本方案只采用**已验证存在**的回滚方式：

1. 每个 Phase 独立提交
2. 回滚优先使用：

```bash
git revert <phase-commit>
```

3. 对于尚未提交的迁移，直接用 Git 工作区恢复

本方案**不**依赖不存在的 `rollback_migration.py` 等脚本。

---

## 十、审批清单

执行任何实际目录迁移前，至少需要确认以下事项：

- [ ] 本方案整体获批
- [ ] `.FILE_OWNERSHIP` 是否显式纳入根目录例外治理
- [ ] `TASK.md` / `TASK-REPORT.md` 保留策略确认
- [ ] 根目录自动发现入口是否允许采用“兼容包装”方案
- [ ] `architecture/` 与 `docs/architecture/` 的边界确认
- [ ] `scripts/tests/` 将采用“文件级分类迁移”而不是整目录迁移
- [ ] `archived/` 与 `.archive/` 的目标归属确认
- [ ] 生成物清理是否同步补齐 `.gitignore`

---

**备注**: 本文档是“项目级实施方案”，不是最终执行脚本。任何目录移动仍需结合当时的调用方盘点结果、治理策略和审批状态执行。
