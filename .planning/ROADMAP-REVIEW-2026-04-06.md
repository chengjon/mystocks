# `.planning/ROADMAP.md` 审核意见 — **Status: Historical review snapshot**


> **历史分析说明**:
> 本文件是阶段性分析、审计、评估或复盘材料，不是当前基线、当前实施优先级或仓库共享规则的唯一事实来源。
> 当前共享规则与治理口径请优先遵循 `architecture/STANDARDS.md`；执行流程、命令与协作约束再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内问题分级、差距判断、风险结论、审阅意见和建议动作如未重新复核，应视为历史分析结果，不得直接当作当前事实。

**Resolved by ROADMAP revision dated 2026-04-06:** findings 1 (Phase 2 deletion gates), 2 (Data access truth source), 3 (Frontend entry truth source), 4 (Success criteria)

 5 (Root shim disposition)
**Remaining open findings:** Finding 4 (case-conflict merge still in Phase 1 — moved to Phase 3, ROADMAP revision)

**Date reviewed:** 2026-04-06

**审核日期**: 2026-04-06  
**审核对象**: `.planning/ROADMAP.md`

## 总体结论

这份 roadmap 的方向基本正确，问题识别也大体贴近仓库现实，但当前版本还不适合直接作为执行蓝图。主要缺口不在“要不要做”，而在“真相源是否定义清楚、删除门禁是否闭环、阶段边界是否自洽、验证口径是否符合项目治理要求”。

按 `architecture/STANDARDS.md:88-111` 与 `architecture/STANDARDS.md:96`，这里涉及的数据访问层合并、路由收敛、大小写目录统一、兼容层下线，本质上都属于需要先明确收口条件并经过审批的架构治理动作。建议把当前文件定位为“评审草案”，修订后再作为执行版 roadmap。

## Findings

### 1. [高] Phase 2 的删除门禁过弱，而且与仓库现状不符

涉及位置：`.planning/ROADMAP.md:30-41`

问题：
Phase 2 目前把删除条件写成 “`grep evidence` + `zero imports` + user approval”。这低于项目治理要求。`architecture/STANDARDS.md:103-111` 明确要求删除前同时完成“代码路径判定”和“功能树判定”，不能只靠静态搜索。

证据：
`src/routes/` 和 `src/api/` 并非可以直接按“零引用”假设处理，仓库里已有真实调用面：

- `src/database/services/database_service.py:155` 仍直接导入 `src.routes.wencai_routes`
- `scripts/cicd_pipeline.sh:184` 仍执行 `from src.routes import *`
- `tests/api_contract_tests.py:21-23` 仍导入 `src.api.types.*`
- `.planning/research/PITFALLS.md:10-21` 也明确提醒了动态导入、注册表、配置侧引用风险

影响：
如果按现稿推进，Phase 2 很容易把“历史层”误判成“死代码”，在 CI、脚本、契约测试或运行时路径上制造断裂。

建议：
把 Phase 2 拆成三个明确子阶段：

1. 先做调用方盘点与功能树标注，不做删除。
2. 再做调用方重定向和兼容层下线条件确认。
3. 最后生成删除清单并走用户审批，审批通过后才真正删除。

`DELETION-CANDIDATES.md` 也不应只有 grep 证据，还应包含“功能节点归属、当前状态、保留/删除理由、兼容面、验证命令”。

### 2. [高] Data access 的最终真相源定义前后矛盾

涉及位置：`.planning/ROADMAP.md:39-40`，`.planning/ROADMAP.md:62-63`

问题：
Phase 2 写的是把 `src/data_access_pkg/` 合并进 `src/data_access/`，同时把 `src/database_optimization/` 合并进 `src/database/`。但 Phase 3 又要求 `src/data_access/` 成为唯一 data access layer。

这意味着 Phase 2 在把一部分数据库能力继续收敛到 `src/database/`，Phase 3 又要把 data access 的唯一真相源设为 `src/data_access/`。这两个目标不一致。

证据：

- `architecture/STANDARDS.md:83-96` 要求同一职责只保留一个主实现，并且迁移前必须先写清目标真相源和旧层下线条件
- `.planning/research/ARCHITECTURE.md:51-55` 已经给出更一致的方向：保留 `src/data_access/` 为 canonical，把 `data_access_pkg/` 和 `database/` 的唯一内容迁移进去

影响：
如果按现稿执行，Phase 2 会先强化 `src/database/` 的地位，Phase 3 再试图反向收敛，等于主动制造一次额外迁移。

建议：
在 roadmap 顶部先写清一句不可歧义的话：

`src/data_access/` 是否就是数据访问层的唯一保留对象？

如果答案是“是”，那么所有相关迁移都应该朝这个目标收口，`src/database_optimization/` 的归宿也不应再写成 `src/database/`。

### 3. [中高] Frontend 主入口的真相源没有先确认，Phase 3 可能删错文件

涉及位置：`.planning/ROADMAP.md:63`

问题：
Phase 3 直接把 `main.js` 写成唯一保留入口，但仓库当前证据并不支持这个结论。

证据：

- `.planning/codebase/ARCHITECTURE.md:38-40` 说实际入口是 `web/frontend/src/main.js`
- 但 `web/frontend/index.html:67` 实际加载的是 `/src/main-standard.ts`
- 这说明“当前运行入口是谁”在研究文档和仓库现实之间已经出现分歧

影响：
如果不先澄清入口真相源，就直接执行“只保留 `main.js`”，有可能把当前实际入口删成“历史产物”，或者把历史入口误升为 canonical。

建议：
把 Phase 3 的第一步改成：

“先确认当前生产/开发构建实际使用的 frontend entry（以 `index.html`、Vite 配置、PM2 启动方式为准），再定义唯一保留入口并清退其他变体。”

在这个结论明确之前，不建议把 `main.js` 写死为成功标准。

### 4. [中] Phase 1 把 case-conflict 合并和 Python lint baseline 绑在一起，和研究文档的顺序不一致

涉及位置：`.planning/ROADMAP.md:11-19`

问题：
Phase 1 同时做两类性质不同的工作：

- Python 侧 duplicate adapter + ruff baseline
- Frontend 侧大小写目录合并

这会把两个不同风险面的改动打成一个批次，增加回滚和定位成本。

证据：

- `.planning/research/ARCHITECTURE.md:57-64` 把 case-conflict merge 放在 Phase 3b
- `.planning/research/ARCHITECTURE.md:99-107` 还明确写了它可以与 Python phases 并行
- `.planning/research/PITFALLS.md:44-57` 也把 P-03 归到 Phase 3，而不是 Phase 1

影响：
当前 roadmap 与它引用的研究结论不一致，执行者很难判断到底该信 roadmap 还是 research。

建议：
二选一即可：

1. 把 case-conflict merge 移回 Phase 3，保持与研究文档一致。
2. 保留在 Phase 1，但必须补一段“为什么提前”的理由，以及单独的验证和回滚策略。

### 5. [中] 成功标准里的验证口径不符合项目门禁，也有命令不可执行的问题

涉及位置：`.planning/ROADMAP.md:16-20`，`.planning/ROADMAP.md:66-67`，`.planning/ROADMAP.md:93-94`

问题：
roadmap 里多处使用“`stylelint` 通过”“`npm run build` 成功”“All existing functionality works”这类表述，但这不够可执行，也不符合项目既有门禁。

证据：

- `architecture/STANDARDS.md:58-60` 规定，凡涉及路由或 Layout 变更，必须跑 `scripts/run_e2e_pm2.sh`
- `AGENTS.md:324-345` 规定，凡涉及前端构建、类型检查、E2E 或服务启动，必须报告 PM2 状态、实际 E2E 套件/浏览器/通过情况、服务访问地址
- `.planning/codebase/CONVENTIONS.md:58-68` 规定的 stylelint 命令是 `npx stylelint "src/**/*.{vue,scss,css}"`
- `web/frontend/package.json:5-67` 中并没有 `stylelint` 这个 npm script

影响：
当前成功标准无法直接拿来当 phase gate，执行者即使“完成”了，也无法按项目规则给出合格的验收报告。

建议：
把成功标准改成明确命令和报告口径，例如：

- `cd web/frontend && npm run build`
- `cd web/frontend && npx stylelint "src/**/*.{vue,scss,css}"`
- `python -c "from web.backend.app.main import app"`
- 路由 / layout / entry 相关阶段补 `scripts/run_e2e_pm2.sh`
- 报告中附 PM2 状态、访问地址、E2E 实际执行结果

“All existing functionality works” 这种表述建议改成一组明确的 smoke gate，而不是笼统判断。

### 6. [中] Phase 4 对 root shim 的收口条件仍不闭环

涉及位置：`.planning/ROADMAP.md:83-94`，`.planning/ROADMAP.md:114`

问题：
当前文件一方面把目标写成“resolve root-level shims”，总结表又写成“zero shims”；另一方面成功标准又允许“removed, deprecated, or documented as intentional”。这三种表述对应的是三个不同的终局。

证据：

- `.planning/research/ARCHITECTURE.md:76-80` 已明确指出 `unified_manager.py` 若仍是 documented entry point，应保留
- 仓库中仍存在真实运行态依赖：
  - `web/backend/app/api/strategy_management/get_monitoring_db.py:37`
  - `src/storage/database/save_realtime_market_data.py:42`
  - `scripts/runtime/system_demo.py:26`
- `.planning/research/PITFALLS.md:61-71` 也要求先检查脚本、Dockerfile、compose 等外部入口

影响：
如果不先写清“哪些 shim 允许保留、哪些必须下线、哪些只做 deprecate”，Phase 4 会变成高度依赖现场判断的清理行动，不满足收口条件要求。

建议：
给 root shim 单独加一张收口表，至少写清：

- shim 名称
- 当前消费者
- 是否允许继续保留
- 若保留，保留到什么里程碑
- 若下线，需要先迁移哪些调用方
- 下线后的验证命令

## 建议的修订方向

建议在 roadmap 修订版中补充以下内容：

1. 增加一段“全局执行前提”，明确本文件只是审批前草案还是已批准执行版。
2. 在文档开头声明每类治理对象的唯一目标真相源，尤其是 data access、frontend entry、root shim。
3. 把 Phase 2 改成“盘点/重定向/审批/删除”四段式，不再把删除动作和识别动作混写。
4. 把 Phase 3 的 frontend entry 收口改成“先确认当前入口，再收敛到唯一入口”。
5. 把所有 success criteria 改成可直接执行的命令和可审计的报告口径。
6. 让 Phase Summary 的风险等级与 `.planning/research/PITFALLS.md` 保持一致，或者明确说明为什么降级。

## 最终判断

这份 roadmap 作为“问题清单 + 初始阶段划分”是可用的，但还不是一个可以直接开工的架构治理执行文件。先把上面的 6 个缺口补齐，再进入实施阶段，会更符合本项目对迁移收口、删除治理和环境一致性的要求。
