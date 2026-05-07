## Context

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

`enhance-api-contract-management-integration` 的 `3.2 Move contract tests from tests/contract/ to main test structure` 已经完成了第一段真实迁移：唯一仍位于 `tests/contract/` 的 pytest case `test_api_contract_schemathesis.py` 已迁入 `tests/integration/contract/`。

当前剩余问题不再是“还有哪些测试文件没挪走”，而是 `tests/contract/` 目录里混杂了一批 misnamed framework / support module：

- `contract_engine.py`
- `contract_validator.py`
- `models.py`
- `report_generator.py`
- `test_executor.py`
- `test_contract_executor.py`
- `test_contract_generator.py`
- `test_contract_validator/`
- `test_reverse_contract_generator.py`

这些文件名保留了历史“test_*”命名，但很多并不是 pytest case，而是运行时 helper、executor、model 或 compatibility alias。

进一步的 GitNexus 核对显示，这条线已经不是低风险目录整理：

- `tests/contract/contract_engine.py` upstream risk: `LOW`，direct callers `3`
- `tests/contract/models.py` upstream risk: `HIGH`，direct callers `20`
- `tests/contract/__init__.py` upstream risk: `LOW`，direct callers `1`

`models.py` 的直接依赖已扩散到 `tests/test_runner.py`、`tests/ai/*`、`scripts/dev/analysis/*` 以及部分 `src/algorithms/*`。因此下一步不能把 support-module 收敛继续当成“无审批微批 rename/move”，需要明确 canonical support package、compatibility shim 和 phased migration 顺序。

## Goals / Non-Goals

### Goals

- 为 `tests/contract/` 剩余 support-module 定义一个 canonical home，避免继续把 legacy tree 当作主实现面。
- 在不破坏现有 importer 的前提下，逐步把 support-module 从 `tests/contract/` 收敛出去。
- 让 `tests/contract/` 最终只保留薄 compatibility wrapper / re-export，而不再承载主实现。
- 为后续关闭 OpenSpec `3.2` 提供明确的阶段性停手条件和完成条件。

### Non-Goals

- 本设计不尝试在同一批里删除 `tests.contract` compatibility import surface。
- 本设计不把 `ContractTestExecutor`、`ContractTestConfig` 等 public names 改名成新的外部 API。
- 本设计不重写 contract testing framework 行为，也不引入新的 runtime validation 语义。
- 本设计不在本批中修复与 `models.py` 高扇出相关的所有下游 importer；这里只定义迁移顺序与边界。

## Decisions

### Decision 1: Introduce a canonical Python support package outside `tests/contract/`

剩余 support-module 的 canonical home 统一定义为：

- `tests/contract_support/`

原因：

- 它比 `tests/contract/` 更明确地表达“这是 Python support / framework code，不是 pytest case tree”。
- 它避免把现有 `tests/helpers/` 这个更偏通用脚本 / page helper 的目录语义混淆为 contract runtime package。
- 它允许 `tests/contract/` 继续作为短期 compatibility barrel，而 `tests/contract_support/` 成为唯一主实现位置。

拟收敛后的 canonical mapping：

- `tests/contract/contract_engine.py` -> `tests/contract_support/engine.py`
- `tests/contract/contract_validator.py` -> `tests/contract_support/validator.py`
- `tests/contract/models.py` -> `tests/contract_support/models.py`
- `tests/contract/report_generator.py` -> `tests/contract_support/report_generator.py`
- `tests/contract/test_executor.py` -> `tests/contract_support/executor.py`

对名称明显误导但实际是 implementation 的文件：

- `tests/contract/test_contract_executor.py`
- `tests/contract/test_contract_generator.py`
- `tests/contract/test_reverse_contract_generator.py`
- `tests/contract/test_contract_validator/`

不要求在第一批就全部重命名；它们可以先保留在原位，待主 support package 建成后分批迁出或显式标记为 compatibility surface。

### Decision 2: Keep `tests.contract` as a thin compatibility layer during migration

迁移期间保留：

- `tests/contract/__init__.py`
- `tests/contract/contract_engine.py`
- `tests/contract/contract_validator.py`
- `tests/contract/models.py`
- `tests/contract/report_generator.py`
- `tests/contract/test_executor.py`

但这些文件在收敛完成后只允许承载：

- re-export
- import forwarding
- 必要的 deprecation docstring / comments

禁止继续在 wrapper 中沉淀新业务逻辑或新测试逻辑。

这样做的原因是：

- `tests/test_runner.py`、`tests/ai/*` 和部分脚本仍显式依赖 `tests.contract.*`
- `models.py` 目前 upstream `HIGH`，直接断开旧导入面会带来大范围回归
- 先建 canonical package，再逐步回写 importer，比一次性全局 rename 更可控

### Decision 3: Migrate by fan-out risk, not by filename

迁移顺序按 blast radius 分层，而不是按目录一次性搬空。

#### Phase A: Establish canonical package with lowest-risk module moves

优先处理 blast radius 较低、依赖面更清晰的模块，例如：

- `contract_engine.py`
- `contract_validator.py`
- `report_generator.py`
- `test_executor.py`

策略：

1. 在 `tests/contract_support/` 建立 canonical module
2. 旧位置改成薄 wrapper
3. 先把 `tests/contract/` 内部相互导入改为 canonical package
4. 跑 unit / integration / runner smoke

#### Phase B: Update direct importers outside the legacy tree

逐批回写以下 importer：

- `tests/unit/contract/test_contract_engine_runtime_source.py`
- `tests/test_runner.py`
- `tests/ai/test_integration_system.py`
- `tests/ai/__init__.py`
- `scripts/dev/analysis/*`

这一步的目标不是删除 wrapper，而是把“主动依赖旧路径”的 importer 数量持续压缩。

#### Phase C: Handle `models.py` last

`models.py` 单独留到最后处理，因为它的上游扇出最高。

在进入 `models.py` 迁移前，必须先满足：

- `tests/contract_support/` 已稳定承载 engine / validator / executor / reporting
- 低风险 importer 已尽量切换到 canonical package
- 已有 import-compat tests 覆盖 legacy alias correctness

#### Phase D: Reclassify `tests/contract/` as compatibility-only

当 `tests/contract/` 中所有主实现都已有 canonical home，且 wrapper 已验证可用后：

- `tests/contract/` 可正式被文档标记为 compatibility-only tree
- OpenSpec `3.2` 才有资格闭合

### Decision 4: Add explicit repo-truth guards before deleting any legacy wrapper

后续实现批次必须继续沿用 repo-truth guard，而不是凭静态搜索直接删文件。

最低要求：

- 保留或扩展 `tests/unit/contract/test_legacy_contract_tree_inventory.py`
  - 证明 `tests/contract/` 不再承载真实 pytest case
- 增加 legacy alias correctness tests
  - 证明 `tests.contract.*` 仍指向 canonical `tests.contract_support.*`
- 对高扇出 importer，增加 targeted runtime/source tests
  - 避免 wrapper 替换后静默漂移

## Risks / Trade-offs

### Risk 1: Wrapper drift

如果旧文件长期保留为 wrapper，但没有 alias correctness tests，wrapper 很容易与 canonical package 漂移。

Mitigation:

- 每次引入 wrapper 都配套 alias / import identity tests
- wrapper 只允许单行 re-export，不允许继续积累逻辑

### Risk 2: `models.py` wide fan-out regression

`models.py` 是当前最大风险点。一次性迁移可能打断测试运行器、AI 测试、分析脚本，甚至部分 `src/algorithms/*` 导入链。

Mitigation:

- 将 `models.py` 迁移明确推迟到最后一批
- 先削减外围 importer 对 legacy path 的依赖
- 在进入该批前重新跑 GitNexus impact

### Risk 3: “tests/contract is empty enough” 的误判

如果只看 pytest case 数量，可能误以为 `3.2` 已完成；但 support-module 仍留在 legacy tree，会继续误导后续开发者。

Mitigation:

- 把 `3.2` 的完成定义明确写为“主测试文件迁移 + support-module canonicalization”
- 在 docs / tasks 中持续声明 `tests/contract/` 当前只是过渡层

## Migration Plan

### Batch 1

- 已完成：迁移 `test_api_contract_schemathesis.py` 到 `tests/integration/contract/`
- 已完成：增加 legacy pytest-case inventory guard

### Batch 2

- 新建 `tests/contract_support/`
- 迁移低风险主实现模块中的第一批
- 旧位置改为 thin wrapper
- 更新少量 direct importer 和 targeted tests

### Batch 3

- 持续迁移剩余低风险 support module
- 扩展 alias correctness coverage
- 更新 `tests/README.md` 和治理指南

### Batch 4

- 单独处理 `models.py` 高扇出迁移
- 再次运行 GitNexus impact / detect scope / targeted regression

### Batch 5

- 把 `tests/contract/` 正式降级为 compatibility-only tree
- 若此时无真实 pytest case、无主实现残留，可关闭 `3.2`

## Completion Criteria

`3.2` 只有在以下条件全部满足时才可关闭：

1. 真实 pytest contract cases 全部位于 `tests/integration/contract/` 或 `tests/unit/contract/`
2. `tests/contract_support/` 成为 contract framework/support code 的唯一主实现位置
3. `tests/contract/` 仅保留薄 compatibility wrapper / re-export
4. 存在 repo-truth guard，证明 `tests/contract/` 不再承载真实 pytest case
5. 存在 alias correctness tests，证明 legacy import surface 仍可工作
6. `openspec validate enhance-api-contract-management-integration --strict` 通过

## Open Questions

- `test_contract_executor.py` / `test_contract_generator.py` / `test_reverse_contract_generator.py` 是否应全部迁入 `tests/contract_support/`，还是先只做 wrapper classification？
- `tests/contract/test_contract_validator/` 这个包应保留历史命名，还是在 canonical package 下拆成 `validator_aliases/` 或 `validator_types/`？
- `src/algorithms/*` 对 `tests/contract/models.py` 的依赖是否本身构成单独的治理问题，需不需要在 support-package 迁移之外再开一条清理线？
