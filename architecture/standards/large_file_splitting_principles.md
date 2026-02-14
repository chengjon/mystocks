# 大文件拆分原则 (Large File Splitting Principles)

## 治理元数据 (Governance Metadata)
*   **当前状态 (Current Status)**: 已批准 (Approved)
*   **批准日期 (Approval Date)**: 2026-02-13
*   **生效日期 (Effective Date)**: 2026-02-13
*   **所有者 (Owner)**: 架构组 / Tech Lead
*   **取代 (Supersedes)**: `openspec/changes/refactor-large-code-files/proposal.md` 中关于文件大小限制的通用建议，以及任何早于此日期且与本文档内容冲突的内部大文件拆分指导。
*   **冲突解决 (Conflict Resolution)**: 本文档为当前项目进行大文件拆分的**操作指导与最低标准**。如果本文档与现有 `openspec` 中的具体 `spec.md` 文件（如 `code-quality/spec.md`, `test-suite/spec.md`）存在差异，应以更严格的标准为准。任何新的或修订的 `spec.md` 应与此原则文档保持一致。若发现无法调和的冲突，需提交团队讨论并更新相关文档。

本项目为提升代码可维护性、可测试性、协作效率及系统性能，特制定以下大文件拆分原则。所有代码重构及新功能开发应严格遵循本原则。

## 一、拆分依据 (Basis for Splitting)

大文件拆分的根本依据在于其对项目维护和发展的负面影响。以下是判断文件是否需要拆分的核心指标：

1.  **代码行数 (Lines of Code - LoC)**：
    *   **考虑拆分阈值 (Consider for Splitting)**：当文件达到此阈值时，应在代码评审中引起关注，并评估是否有拆分必要。
    *   **强制拆分阈值 (Mandatory Splitting)**：当文件超过此阈值时，必须制定并执行拆分计划。

| 文件类型                     | 考虑拆分阈值 (Should Evaluate) | 强制拆分阈值 (Must Split) | 现有 `spec.md` 参照                                                                                                    |
| :--------------------------- | :----------------------------- | :------------------------ | :--------------------------------------------------------------------------------------------------------------------- |
| Python 文件                  | > 500 行                       | > 800 行                  | `openspec/changes/refactor-large-files/specs/code-quality/spec.md`: Python 文件超过 500 行应考虑重构。                       |
| Vue/JS 文件                  | > 400 行                       | > 500 行                  | `openspec/changes/refactor-large-files/specs/frontend-component/spec.md`: Vue 组件超过 500 行必须拆分。                       |
| TypeScript 类型文件 (`.ts`)  | > 300 行                       | > 500 行                  | `openspec/changes/refactor-large-files/specs/code-quality/spec.md`: TypeScript 类型文件超过 500 行必须拆分。                 |
| Vue 模板 (`template`)        | > 150 行                       | > 200 行                  | `openspec/changes/refactor-large-files/specs/code-quality/spec.md`: Vue 模板超过 200 行应考虑抽取组件。                       |
| Vue 脚本 (`script`)          | > 150 行                       | > 200 行                  | `openspec/changes/refactor-large-files/specs/code-quality/spec.md`: Vue script setup 超过 200 行应抽取逻辑到 composables。 |
| Vue 样式 (`style`)           | > 80 行                        | > 100 行                  | `openspec/changes/refactor-large-files/specs/code-quality/spec.md`: Vue 样式超过 100 行应抽取共享样式。                       |
| 测试文件                     | > 500 行                       | > 1000 行                 | `openspec/changes/refactor-large-files/specs/test-suite/spec.md`: 测试文件超过 1000 行必须拆分，建议新文件 300-500 行。   |

2.  **软件工程原则**：
    *   **单一职责原则 (Single Responsibility Principle - SRP)**：一个文件、类、函数或组件应只有一个引起它变化的原因。如果文件内包含多个不相关的职责，则应拆分。
    *   **高内聚，低耦合 (High Cohesion, Low Coupling)**：文件内部的功能应紧密相关，文件之间或模块之间的依赖关系应尽可能减少且清晰。
    *   **可读性与可理解性 (Readability & Understandability)**：文件过长或逻辑过于复杂会降低代码可读性，使得新成员难以快速理解。
    *   **可测试性 (Testability)**：难以编写单元测试、集成测试或测试覆盖率低的文件是拆分的信号。
    *   **可复用性 (Reusability)**：文件内存在可独立复用的逻辑或组件，但因文件过大而难以抽离。

3.  **团队协作效率 (Team Collaboration Efficiency)**：
    *   频繁的代码冲突：多个团队成员经常需要修改同一个大文件。
    *   代码审查困难：大型 Pull Request 难以有效审查。

4.  **例外条款 (Exceptions)**：
    *   **例外申请流程**: 任何需要例外处理的情况，均需遵循以下流程：
        *   **原因**: 详细说明为何该文件不能遵循拆分原则（例如，自动生成文件的特殊性、第三方库限制、短期紧急任务等）。
        *   **影响**: 评估不拆分对项目维护性、性能、团队协作的潜在负面影响。
        *   **审批**: 提交给**架构组/Tech Lead**进行审批，审批记录需存档。
        *   **时限**: 设定明确的例外期限（例如，3个月、下一个版本周期），到期需重新评估。
        *   **缓解措施**: 提出在例外期间将如何管理该文件（例如，加强代码审查、定期清理、限制修改范围）。
        *   **记录**: 所有例外情况及其审批记录需在相关文档或代码注释中明确体现，例如：`docs/exceptions/large_files.md`。
    *   **自动生成的文件 (Auto-generated Files)**：例如 `generated-types.ts`。这类文件可能因其生成机制而天然庞大。**不强制进行手动拆分**，但应优先**优化生成脚本或工具**，使其能按领域或功能生成多个更小的文件。若无法优化生成脚本，则需按上述例外申请流程进行审批。

## 二、拆分策略 (Splitting Strategies)

拆分应有策略地进行，避免盲目拆分造成碎片化。

1.  **按职责拆分 (By Responsibility)**：
    *   **后端 (Python)**：
        *   **API层**：将路由定义、请求解析、参数验证与业务逻辑分离。例如：`api.py` 拆分为 `routers/` (仅路由)、`schemas/` (请求响应模型)、`dependencies/` (依赖注入)。
        *   **服务层**：将复杂的业务逻辑分解为更小的、协作的服务。例如：`service.py` 拆分为 `core_logic_service.py`, `helper_service.py` 等。
        *   **数据访问层 (DAL)**：将数据库操作、外部 API 调用、数据转换等逻辑封装到独立的模块或适配器中。
        *   **工具类/辅助函数**：将通用的工具函数、常量、枚举等提取到 `utils/` 或 `common/` 模块。
        *   **配置**：将不同的配置项（如数据库配置、外部服务配置）拆分到独立的配置文件或模块中。
    *   **前端 (Vue/JS/TS)**：
        *   **组件拆分**：将大型 Vue 页面组件拆分为布局组件、功能组件、原子组件等。每个组件应专注于渲染特定 UI 或处理特定交互。
        *   **逻辑抽离**：将组件内的复杂业务逻辑、状态管理逻辑（如 `Pinia` actions/getters）、API 调用逻辑、工具函数抽离到 `composables/` (Vue 3 Composition API)、`stores/`、`api/` 或 `utils/` 目录。
        *   **样式分离**：将组件样式（特别是 TailwindCSS 或 SCSS 变量）分离到独立的 `*.css`/`*.scss` 文件，并通过 `scoped` 保持组件封装性。
        *   **路由配置**：将大型路由配置文件按模块或业务领域拆分。
        *   **类型定义**：将 TypeScript 类型定义按领域或功能拆分到多个文件，并由 `index.ts` 统一导出。

2.  **按领域拆分 (By Domain/Feature)**：
    *   一个大文件如果处理多个业务领域或功能，应将其拆分为对应领域的子模块。
    *   **后端 API 组织**: 严格遵循按业务领域组织 API 的原则，而不是按开发阶段。例如，API 目录结构应为 `api/v1/{system,strategy,trading,admin,analysis}/`，禁止使用 `phase1`, `phase2` 等阶段性命名。此约束是强制性的，任何新的 API 必须符合此约定。
    *   **前端 ArtDeco 组件约束**: 对于 ArtDeco 风格的 Vue 组件，如果一个组件内部包含多个通过 `v-if`/`v-show` 或 `<keep-alive>` 等机制切换的“Tab”或“视图”，且这些 Tab 共同服务于一个高内聚的业务功能，**禁止将其拆分成独立的路由页面**。应优先拆分为该组件的子组件，并通过 Props/Emit 或 Provide/Inject/Pinia 进行状态管理，以保持其作为单一应用入口的完整性和性能。只有当 Tab 间的业务关联性极低，或需要独立加载、权限控制时，才考虑拆分为独立路由。此约束是强制性的，旨在维护 ArtDeco 组件的统一体验和性能。

3.  **按层级拆分 (By Layer)**：
    *   严格遵循分层架构原则，确保各层职责清晰，依赖关系单向。
    *   例如：API -> Service -> Repository -> Model。

4.  **逐步重构 (Incremental Refactoring)**：
    *   不一次性进行大规模拆分，而是从小处着手，逐步迭代。
    *   优先拆分最影响开发效率和质量的文件。

## 三、拆分工具 (Splitting Tools)

合理的工具可以辅助拆分过程并确保代码质量。

1.  **代码分析工具**：
    *   **行数统计**：`wc -l` (Shell), `cloc` (跨语言代码统计)。
    *   **依赖分析**：
        *   Python: `deptry`, `Pylint` (模块/循环依赖报告)。
        *   JavaScript/TypeScript: `Madge` (模块依赖图), `ESLint` (配置规则检测)。
    *   **圈复杂度**：`Radon` (Python), `ESLint` (JS/TS) - 识别复杂函数，辅助函数拆分。

2.  **IDE 支持**：
    *   PyCharm, VS Code 等现代 IDE 提供了代码重构功能，如“提取方法”、“移动文件”、“提取组件”等，可辅助拆分。

3.  **自动化测试框架**：
    *   `pytest` (Python), `Vitest`/`Jest` (JavaScript/TypeScript) - 确保拆分过程中功能不被破坏。

4.  **版本控制系统**：
    *   `Git`：利用分支管理、小步提交，便于回溯和协作。

## 四、验证标准 (Validation Standards)

拆分完成后，必须通过以下标准验证其有效性和质量：

1.  **代码行数达标**：
    *   所有拆分后的文件行数均应满足上述“拆分依据”中的目标阈值。
    *   自动生成的文件需遵循例外申请流程。

2.  **通过所有测试 (All Tests Pass)**：
    *   **执行命令**:
        *   Python: `pytest`
        *   前端 (Vue/JS/TS): `cd web/frontend && npm run test` (运行所有单元和组件测试)
        *   端到端 (E2E): `cd web/frontend && npm run test:e2e` (使用 Playwright 运行所有 E2E 测试)
    *   确保所有单元测试、集成测试、端到端测试（如果适用）在拆分后全部通过，**无任何失败或错误**。

3.  **测试覆盖率 (Test Coverage)**：
    *   **执行命令**:
        *   Python: `pytest --cov=./src --cov-report term-missing`
        *   前端 (Vue/JS/TS): `cd web/frontend && npm run test:coverage`
    *   **门槛**:
        *   **整体代码覆盖率**: 至少达到 **80%**。
        *   **关键路径/核心业务逻辑覆盖率**: 必须达到 **100%**。
    *   拆分后的新模块或修改的模块，其测试覆盖率应达到或高于上述门槛。

4.  **遵循单一职责原则**：
    *   每个文件、类、函数或组件的职责应清晰明确，避免“上帝对象”或“大泥球”现象。
    *   代码审查过程中，若发现职责不清，需重新拆分或合并。

5.  **清晰的模块化与命名规范**：
    *   文件和目录结构应符合项目规范，易于导航和理解。
    *   命名应语义化，准确反映其内容和职责。

6.  **无循环依赖 (No Circular Dependencies)**：
    *   **执行命令**:
        *   Python: `pylint --disable=all --enable=R0401 your_module` (需针对特定模块配置) 或使用 `deptry`。
        *   JavaScript/TypeScript: `madge --circular --extensions js,ts,vue src`
    *   使用依赖分析工具检查，确保模块间不存在循环引用。
    *   严格遵循单向依赖原则。

7.  **代码质量工具检查通过 (Code Quality Tools Pass)**：
    *   **执行命令**:
        *   Python: `ruff check .` 和 `mypy .`
        *   前端 (Vue/JS/TS): `cd web/frontend && npm run lint` (检查 ESLint 错误，已配置为只读检查 `eslint . --max-warnings=0`) 和 `cd web/frontend && npm run type-check` (运行 `vue-tsc --noEmit` 进行 TypeScript 类型检查)。
    *   所有代码质量工具 (如 `ruff`, `mypy`, `eslint`, `tsc`) 检查必须无报错或警告。

8.  **性能无明显下降 (No Significant Performance Degradation)**：
    *   **强制验收**: 仅以 Playwright/Locust 指标为强制门禁。
    *   **基线与阈值**: 在拆分前，需对受影响的关键功能或页面（例如，复杂图表渲染、高频数据更新接口）记录性能基线（如加载时间、响应时间、FPS、内存占用）。
    *   **验收命令**:
        *   **前端性能 (强制)**:
            *   **Playwright 性能验证**: 使用 `cd web/frontend && npm run test:e2e` 运行 E2E 测试时，可以集成 Playwright 的性能指标捕捉（例如，`page.metrics()` 或 `page.performance.getMetrics()`）。验收标准为：关键页面加载时间、首次内容绘制 (FCP)、最大内容绘制 (LCP) 等核心 Web 指标**无恶化（例如，P95 加载时间增加不超过 10%）**。
        *   **后端性能 (强制)**: `locust -f your_locustfile.py --headless -u 10 -r 1 --run-time 1m --csv=test_results` (或类似的压力测试工具)。验收标准为：RPS (Requests Per Second), P95 响应时间等关键指标**无恶化（例如，P95 响应时间增加不超过 10%）**。
        *   **Lighthouse 审计 (建议)**: 如果项目中配置了 `cd web/frontend && npm run lighthouse` 脚本，则建议执行该脚本并分析结果。验收标准为：PWA, Performance, Accessibility, Best Practices, SEO 分数**性能得分下降不超过 5 分**。
    *   拆分后，重新运行性能测试，确保性能指标在可接受范围内。

9.  **部署与运维影响评估 (Deployment & Operations Impact Assessment)**：
    *   评估拆分对 CI/CD 流程、构建时间、部署包大小的影响，确保其顺畅且无负面优化。
    *   如果引入了新的微服务或独立部署单元，需更新相关部署文档、监控配置和运维手册。

遵循这些原则，可以确保代码库的健康发展，提高开发效率和系统稳定性。
