# Marketplace & Agent 完整清单

**生成时间**: 2025-12-30
**项目**: MyStocks Spec
**来源**: Claude Code 配置

---

## 1. Compound Engineering Marketplace

**提供者**: compound-engineering@every-marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `general-purpose` | 通用代理，用于复杂的搜索和多步骤任务 |
| `Explore` | 快速代理，专门用于探索代码库、搜索文件、理解代码库 |
| `Plan` | 软件架构师代理，用于设计实现计划和识别关键文件 |
| `spec-flow-analyzer` | 分析规格文档中的用户流程和缺失元素 |
| `claude-code-guide` | 提供 Claude Code 和 Claude Agent SDK 文档指导 |
| `changelog` | 为 main 分支的合并创建引人入胜的变更日志 |
| `create-agent-skill` | 创建或编辑 Claude Code 技能，提供结构和最佳实践指导 |
| `deploy-docs` | 验证并准备文档以供 GitHub Pages 部署 |
| `generate_command` | 创建新的自定义斜杠命令，遵循约定和最佳实践 |
| `heal-skill` | 修复错误的 SKILL.md 文件（错误指令或过时的 API 引用） |
| `plan_review` | 使用多个专门代理并行审查计划 |
| `release-docs` | 使用当前插件组件构建和更新文档站点 |
| `report-bug` | 报告 compound-engineering 插件中的 bug |
| `reproduce-bug` | 使用日志和控制台检查重现和调查 bug |
| `resolve_parallel` | 使用并行处理解决所有 TODO 注释 |
| `resolve_pr_parallel` | 使用并行处理解决所有 PR 评论 |
| `resolve_todo_parallel` | 使用并行处理解决所有待处理的 CLI todos |
| `triage` | 为 CLI todo 系统分类和整理发现 |
| `workflows:compound` | 记录已解决问题的知识 |
| `workflows:plan` | 将功能描述转换为结构化的项目计划 |
| `workflows:review` | 使用多代理分析、ultra-thinking 和 worktrees 进行详尽的代码审查 |
| `workflows:work` | 高效执行工作计划，同时保持质量并完成功能 |

---

## 2. Superpowers Marketplace

**提供者**: superpowers@superpowers-marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `brainstorm` | 使用苏格拉底方法进行交互式设计优化 |
| `execute-plan` | 以审查检查点分批执行计划 |
| `write-plan` | 创建包含小任务的详细实现计划 |

---

## 3. Feature Dev Marketplace

**提供者**: feature-dev@claude-code-plugins

| Agent 名称 | 功能描述 |
|-----------|----------|
| `feature-dev` | 有指导的功能开发，包含代码库理解和架构重点 |
| `code-explorer` | 深度分析现有代码库功能，追踪执行路径、映射架构层 |
| `code-reviewer` | 审查代码中的 bug、逻辑错误、安全漏洞、代码质量问题 |

---

## 4. Commit Commands Marketplace

**提供者**: commit-commands@claude-code-plugins

| Agent 名称 | 功能描述 |
|-----------|----------|
| `clean_gone` | 清理所有标记为 [gone] 的 git 分支（已在远程删除但仍存在本地） |
| `commit-push-pr` | 提交、推送并打开 PR |
| `commit` | 创建 git commit |

---

## 5. Ralph Wiggum Marketplace

**提供者**: ralph-wiggum@claude-code-plugins

| Agent 名称 | 功能描述 |
|-----------|----------|
| `cancel-ralph` | 取消活动的 Ralph Wiggum 循环 |
| `help` | 解释 Ralph Wiggum 技术和可用命令 |
| `ralph-loop` | 在当前 session 开始 Ralph Wiggum 循环 |

---

## 6. Double Check Marketplace

**提供者**: double-check@claude-code-marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `double-check` | 强制 agent 再次思考，如果它说"工作完成且生产就绪"通常实际上还没完成 |

---

## 7. Python Development Marketplace

**提供者**: python-development@claude-code-workflows

| Agent 名称 | 功能描述 |
|-----------|----------|
| `async-python-patterns` | 掌握 Python asyncio、并发编程和 async/await 模式，用于构建高性能应用。用于构建异步 API、并发系统或需要非阻塞操作的 I/O 密集型应用 |
| `python-packaging` | 创建具有适当项目结构的可分发 Python 包（setup.py/pyproject.toml），发布到 PyPI。用于打包 Python 库、创建 CLI 工具或分发 Python 代码 |
| `python-performance-optimization` | 使用 cProfile、内存分析器和性能最佳实践分析和优化 Python 代码。用于调试慢速 Python 代码、优化瓶颈或改进应用性能 |
| `python-testing-patterns` | 使用 pytest、fixture、mocking 和 TDD 实现全面的测试策略。用于编写 Python 测试、设置测试套件或实施 TDD/BDD 工作流 |
| `uv-package-manager` | 掌握 uv 包管理器以实现快速 Python 依赖管理、虚拟环境和现代 Python 项目工作流。用于设置 Python 项目、管理依赖或优化 Python 开发工作流 |

---

## 8. JavaScript/TypeScript Marketplace

**提供者**: javascript-typescript@claude-code-workflows

| Agent 名称 | 功能描述 |
|-----------|----------|
| `javascript-testing-patterns` | 使用 Jest、Vitest 和 Testing Library 实现全面的测试策略，包括单元测试、集成测试和端到端测试，以及 mocking、fixture 和 TDD。用于编写 JavaScript/TypeScript 测试、设置测试基础设施或实施 TDD/BDD 工作流 |
| `modern-javascript-patterns` | 掌握 ES6+ 特性，包括 async/await、解构、展开运算符、箭头函数、promise、模块、迭代器和生成器，以及用于编写干净、高效 JavaScript 代码的函数式编程模式。用于重构遗留代码、实施现代模式或优化 JavaScript 应用 |

---

## 9. Backend Development Marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `backend-architect` | 专家级后端架构师，专注于可扩展的 API 设计、微服务架构和分布式系统。掌握 REST/GraphQL/gRPC API、事件驱动架构、服务边界定义、进程间通信、弹性模式、服务网格模式和可观测性。用于创建新的后端服务或 API、设计进程间通信或评估 API 架构 |

---

## 10. Backend Development (GraphQL) Marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `graphql-architect` | 掌握现代 GraphQL 及其联邦、性能优化和企业级安全。构建可扩展的模式、实现高级缓存、设计实时系统。用于 GraphQL 架构或性能优化 |

---

## 11. Backend Development (TDD) Marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `tdd-orchestrator` | 掌握 TDD 编排纪律、红-绿-重构纪律和多代理工作流协调。实施全面的测试驱动开发实践。用于 TDD 实施和治理 |

---

## 12. Backend Development (Temporal) Marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `temporal-python-pro` | 掌握 Temporal 工作流编排，使用 Python SDK。实现持久工作流、saga 模式和分布式事务。覆盖异步/等待、测试策略、生产部署。用于工作流设计、微服务编排或长期运行的进程 |

---

## 13. Code Review Marketplace

**提供者**: compound-engineering@every-marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `architect-review` | 软件架构师，专注于现代架构模式、整洁架构、微服务、事件驱动系统和 DDD。从架构角度审查代码更改 |

---

## 14. Code Review (Agent Native) Marketplace

**提供者**: compound-engineering@every-marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `agent-native-reviewer` | 审查代码以确保功能是 agent-native 的 - 任何用户可以采取的行动，agent 也可以采取，任何用户可以看到的，agent 也可以看到 |

---

## 15. Code Review (Simplicity) Marketplace

**提供者**: compound-engineering@every-marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `code-simplicity-reviewer` | 代码的最终审查通过，确保代码更改尽可能简单和最小。仅在实现完成后但在最终化之前使用 |

---

## 16. Code Review (Data Integrity) Marketplace

**提供者**: compound-engineering@every-marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `data-integrity-guardian` | 审查数据库迁移、数据模型或任何操作持久化数据的代码。检查迁移安全、数据约束、事务边界和引用完整性 |

---

## 17. Code Review (Data Migration) Marketplace

**提供者**: compound-engineering@every-marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `data-migration-expert` | 审查涉及 ID 映射、列重命名或数据转换的迁移的 PR。验证 ID 映射与生产环境匹配，检查交换值，验证回滚安全 |

---

## 18. Code Review (Deployment) Marketplace

**提供者**: compound-engineering@every-marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `deployment-verification-agent` | 当 PR 触及生产数据、迁移或任何可能静默丢弃或复制记录的行为时使用。生成具体的部署前/后检查清单 |

---

## 19. Code Review (DHH Rails) Marketplace

**提供者**: compound-engineering@every-marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `dhh-rails-reviewer` | 从 David Heinemeier Hansson 的角度进行残酷诚实的 Rails 代码审查。识别反模式、JavaScript 框架污染和 Rails 约定违规 |

---

## 20. Code Review (Julik Python) Marketplace

**提供者**: compound-engineering@every-marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `kieran-python-reviewer` | 使用极其高的质量标准审查 Python 代码更改。应用 Kieran 严格的 Python 约定和品味偏好 |

---

## 21. Code Review (Julik Rails) Marketplace

**提供者**: compound-engineering@every-marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `kieran-rails-reviewer` | 使用极其高的质量标准审查 Rails 代码更改。应用 Kieran 严格的 Rails 约定和品味偏好 |

---

## 22. Code Review (Julik TypeScript) Marketplace

**提供者**: compound-engineering@every-marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `kieran-typescript-reviewer` | 使用极其高的质量标准审查 TypeScript 代码更改。应用 Kieran 严格的 TypeScript 约定和品味偏好 |

---

## 23. Code Review (Pattern Recognition) Marketplace

**提供者**: compound-engineering@every-marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `pattern-recognition-specialist` | 分析代码的设计模式、反模式、命名约定和代码重复。识别架构模式、检测代码气味并确保代码库的一致性 |

---

## 24. Code Review (Performance Oracle) Marketplace

**提供者**: compound-engineering@every-marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `performance-oracle` | 分析代码的性能问题、优化算法、识别瓶颈并确保可扩展性。包括数据库查询、内存使用、缓存策略和整体系统性能 |

---

## 25. Code Review (Security Sentinel) Marketplace

**提供者**: compound-engineering@every-marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `security-sentinel` | 执行安全审计、漏洞评估和安全代码审查。检查常见安全漏洞、验证输入处理、审查认证/授权实现、扫描硬编码机密并确保 OWASP 合规性 |

---

## 26. Workflow (Bug Reproduction) Marketplace

**提供者**: compound-engineering@every-marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `bug-reproduction-validator` | 收到 bug 报告或问题描述时使用，通过系统尝试重现问题，验证重现步骤并确认行为是否偏离预期功能 |

---

## 27. Workflow (Every Style Editor) Marketplace

**提供者**: compound-engineering@every-marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `every-style-editor` | 审查和编辑文本内容以符合 Every 的特定风格指南。系统检查标题大小写、句子大小写、公司单复数使用、过度使用词、被动语态、数字格式、标点符号等 |

---

## 28. Workflow (Lint) Marketplace

**提供者**: compound-engineering@every-marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `lint` | 运行 linting 和代码质量检查 Ruby 和 ERB 文件。在推送到 origin 之前运行 |

---

## 29. Workflow (PR Comment Resolver) Marketplace

**提供者**: compound-engineering@every-marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `pr-comment-resolver` | 通过实施修复并报告回来处理代码审查中的评论。处理完整的请求：理解评论、实施修复、提供完成的简明摘要 |

---

## 30. Full Stack Orchestration (Deployment) Marketplace

**提供者**: compound-engineering@every-marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `deployment-engineer` | 专家级部署工程师，专注于现代 CI/CD 管道、GitOps 工作流和高级部署自动化。掌握 GitHub Actions、ArgoCD/Flux、渐进式交付、容器安全、平台工程和开发者体验优化 |

---

## 31. Full Stack Orchestration (Performance) Marketplace

**提供者**: compound-engineering@every-marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `performance-engineer` | 专家级性能工程师，专注于现代可观测性、应用优化和可扩展系统性能。掌握 OpenTelemetry、分布式追踪、负载测试、多层缓存、Core Web Vitals 和性能监控 |

---

## 32. Full Stack Orchestration (Security) Marketplace

**提供者**: compound-engineering@every-marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `security-auditor` | 专家级安全审计员，专注于 DevSecOps、全面的网络安全和合规框架。掌握漏洞评估、威胁建模、安全认证（OAuth2/OIDC）、OWASP 标准、云安全和安全自动化 |

---

## 33. Full Stack Orchestration (Test Automation) Marketplace

**提供者**: compound-engineering@every-marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `test-automator` | AI 驱动的测试自动化专家，掌握现代框架、自愈测试和全面的质量工程。构建可扩展的测试策略，集成到 CI/CD 管道 |

---

## 34. Design (Implementation Review) Marketplace

**提供者**: compound-engineering@every-marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `design-implementation-reviewer` | 验证 UI 实现是否匹配其 Figma 设计规范。应该在基于设计编写代码（HTML/CSS/React 组件）后使用此代理 |

---

## 35. Design (Iterator) Marketplace

**提供者**: compound-engineering@every-marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `design-iterator` | 当设计工作在第一次尝试时没有奏效时使用。如果进行了 1-2 次设计更改结果仍然感觉不对，建议使用 5x 或 10x 迭代进行深度改进 |

---

## 36. Design (Figma Sync) Marketplace

**提供者**: compound-engineering@every-marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `figma-design-sync` | 通过自动检测和修复视觉差异，将 web 实现与其 Figma 设计同步。应该迭代使用，直到实现与设计匹配 |

---

## 37. Documentation (Ankane README Writer) Marketplace

**提供者**: compound-engineering@every-marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `ankane-readme-writer` | 遵循 Ankane 风格模板创建或更新 README 文件。使用简洁的文档，包含祈使语气、15 字以下句子、按标准顺序组织的章节 |

---

## 38. Research (Best Practices) Marketplace

**提供者**: compound-engineering@every-marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `best-practices-researcher` | 研究和收集任何技术、框架或开发实践的外部最佳实践、文档和示例。包括官方文档、社区标准、开源项目的良好示例和领域特定约定 |

---

## 39. Research (Framework Docs) Marketplace

**提供者**: compound-engineering@every-marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `framework-docs-researcher` | 为项目中使用的框架、库或依赖项收集全面的文档和最佳实践。获取官方文档、探索源代码、识别版本特定约束、理解实现模式 |

---

## 40. Research (Git History Analyzer) Marketplace

**提供者**: compound-engineering@every-marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `git-history-analyzer` | 理解代码更改的历史背景和演变、追踪特定代码模式的起源、识别关键贡献者及其专业领域、分析提交历史中的模式 |

---

## 41. Research (Repo Analyst) Marketplace

**提供者**: compound-engineering@every-marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `repo-research-analyst` | 对仓库的结构、文档和模式进行彻底研究。分析架构文件、检查 GitHub issue 以查找模式、审查贡献指南、检查模板、搜索代码库中的实现模式 |

---

## 42. Cook Zh CN Roles Marketplace

**提供者**: cook-zh-cn@roles

| Agent 名称 | 功能描述 |
|-----------|----------|
| `analyzer` | 根本原因分析专家。5 Whys、系统思维、证据优先方法解决复杂问题 |
| `architect` | 系统架构师。证据优先设计、MECE 分析、演进式架构 |
| `backend` | 后端开发专家。API 设计、微服务、云原生、无服务器架构 |
| `frontend` | 前端和 UI/UX 专家。WCAG 2.1 合规、设计系统、用户中心设计。React/Vue/Angular 优化 |
| `mobile` | 移动开发专家。iOS HIG、Android Material Design、跨平台策略、Touch-First 设计 |
| `performance` | 性能优化专家。Core Web Vitals、RAIL 模型、渐进式优化、ROI 分析 |
| `qa` | 测试工程师。测试覆盖率分析、E2E/集成/单元测试策略、自动化建议、质量指标设计 |
| `reviewer` | 代码审查专家。Evidence-First、Clean Code 原则、官方风格指南遵循的代码质量评估 |
| `security` | 安全漏洞检测专家。OWASP Top 10、CVE 对照、LLM/AI 安全对应 |

---

## 43. UI Designer Marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `ui-designer` | 创建用户界面、设计组件、构建设计系统或改善视觉美学。专门构建可在 6 天 sprint 内快速实现的漂亮、功能接口 |

---

## 44. API Tester Marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `api-tester` | 全面的 API 测试，包括性能测试、负载测试和契约测试。确保 API 在部署前强大、高性能且符合规范 |

---

## 45. Superpowers (Code Reviewer) Marketplace

**提供者**: superpowers@superpowers-marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `code-reviewer` | | (所有工具) |

---

## 46. Contract Driven Dev Expert Marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `contract-driven-dev-expert` | 为小团队（2-3 名开发者）实施契约驱动开发（API 优先开发）的专家指导。包括设置 API 文档和 mock 服务、使用 Swagger、Mock.js 和 JSON Server、使用 Puppeteer、Playwright 和 Chrome DevTools 进行自动化测试、配置 GitHub Actions CI/CD 管道、设计轻量级架构、故障排除 API 契约工作流和工具集成、优化前端-后端协作 |

---

## 47. Code Reviewer Marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `code-reviewer` | 当代码被编写或修改且需要在合并或部署前进行专家审查时使用。在完成重要代码块后主动调用 |

---

## 48. Root Cause Debugger Marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `root-cause-debugger` | 当遇到错误、测试失败、意外行为或需要诊断代码为何不按预期工作时使用。在需要调试时主动使用 |

---

## 49. Web Full Stack Architect Marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `web-fullstack-architect` | 需要全面的 Web 开发解决方案时使用，涉及前端架构、后端服务、数据库优化或部署策略 |

---

## 50. Database Architect CN Marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `database-architect-cn` | 数据库架构设计、性能优化或技术选择的专家指导，特别适用于分布式系统。适用于：设计高并发场景的数据库架构（例如电商、IoT 数据收集）、在 MySQL、PostgreSQL、TimescaleDB、TDengine、Redis 等不同数据库技术之间进行选择、优化查询性能、设计索引、分析执行计划以优化现有系统、设计高可用架构，包括复制、分片或多活设置、实现分布式事务并确保系统间的数据一致性、设计备份/恢复策略、实施监控解决方案 |

---

## 51. First Principles Full Stack Architect Marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `first-principles-fullstack-architect` | 通过应用第一性原理思维为中到小型企业设计或优化全栈系统。将复杂需求解构为最小的可行组件、设计成本效益高的架构、基于可量化的约束（而非行业惯例）做出技术决策。适用于：添加有意义的新功能、任务可以通过多种方式解决、影响现有行为或结构的代码修改、需要做出架构决策（WebSockets vs SSE vs polling）、影响多个文件的任务、需要探索才能理解完整范围的模糊需求 |

---

## 52. Auth Route Tester Marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `auth-route-tester` | 简要描述此 Subagent 的作用 |

---

## 53. Database Verifier Marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `database-verifier` | 简要描述此 Subagent 的作用 |

---

## 54. Frontend Error Fixer Marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `frontend-error-fixer` | 简要描述此 Subagent 的作用 |

---

## 55. Documentation Architect Marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `documentation-architect` | 简要描述此 Subagent 的作用 |

---

## 56. Code Architecture Reviewer Marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `code-architecture-reviewer` | 简要描述此 Subagent 的作用 |

---

## 57. Build Error Resolver Marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `build-error-resolver` | 简要描述此 Subagent 的作用 |

---

## 58. Strategic Plan Architect Marketplace

| Agent 名称 | 功能描述 |
|-----------|----------|
| `strategic-plan-architect` | 简要描述此 Subagent 的作用 |

---

## 统计汇总

- **总 Marketplace 数量**: 58+
- **Compound Engineering**: 27+ agents
- **Python Development**: 5 agents
- **JavaScript/TypeScript**: 2 agents
- **Backend Development**: 3 agents
- **Full Stack Orchestration**: 3 agents
- **Code Review**: 12+ agents
- **Workflow**: 4 agents
- **Design**: 3 agents
- **Research**: 4 agents
- **Cook Zh CN**: 9 roles

---

**使用方法**:

```python
# 使用 Task tool 调用 agent
Task(
    subagent_type="general-purpose",  # agent 类型
    prompt="具体任务描述",  # 任务提示
    description="简短描述"  # 3-5个词的描述
)
```

**注意事项**:
- 某些 agent 需要 `run_in_background=True` 参数在后台运行
- 某些 agent 可以使用 `resume` 参数恢复之前的执行
- 选择 agent 时应根据具体任务类型和需求
