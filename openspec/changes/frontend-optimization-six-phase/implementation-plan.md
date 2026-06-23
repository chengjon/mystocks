# Frontend Six-Phase Optimization - Multi-CLI Implementation Plan

> **设计方案说明**:
> 本文件用于记录测试方案中的结构设计、数据模型、技术取舍或实现路径，属于方案设计层材料。
> 它不是共享规则正文，也不直接代表当前已落地状态；落地判断应结合 `architecture/STANDARDS.md`、当前测试实现与实际验证结果。


**Change ID**: `frontend-optimization-six-phase`
**Implementation Strategy**: Multi-CLI Parallel Development
**Created**: 2025-12-29
**Status**: Pending Approval
**Estimated Duration**: 28 工作日 (4 weeks)

---

## 📋 Executive Summary

本实施方案采用**多CLI并行开发模式**,将六阶段前端优化工作拆分为**6个独立CLI**,通过Git Worktree实现真正的并行执行。

**核心优势**:
- ✅ **并行开发**: 6个CLI同时工作,缩短总周期40%
- ✅ **隔离风险**: 每个CLI独立分支,互不干扰
- ✅ **渐进交付**: Round 1和Round 2分批验收
- ✅ **质量保证**: 专职QA CLI贯穿全程
- ✅ **可回滚**: 每个CLI独立Git历史,随时回滚

---

## 🎯 Implementation Architecture

### 总体架构

```
主仓库 (main)
    ↓
┌───────────────────────────────────────────────────────┐
│              Git Worktree 隔离环境                   │
├───────────────────────────────────────────────────────┤
│                                                       │
│  Round 1 (Day 1-14) - 4个CLI并行                     │
│  ┌─────────────┐  ┌─────────────┐                   │
│  │   CLI-1     │  │   CLI-2     │                   │
│  │  Phase 3    │  │ API契约     │                   │
│  │  K线图      │  │             │                   │
│  └─────────────┘  └─────────────┘                   │
│  ┌─────────────┐  ┌─────────────┐                   │
│  │   CLI-5     │  │   CLI-6     │                   │
│  │ GPU监控     │  │  质量保证   │                   │
│  └─────────────┘  └─────────────┘                   │
│                                                       │
│  Round 2 (Day 15-28) - 2个CLI并行                    │
│  ┌─────────────┐  ┌─────────────┐                   │
│  │   CLI-3     │  │   CLI-4     │                   │
│  │  Phase 4    │  │ AI筛选      │                   │
│  │  完整实现   │  │             │                   │
│  └─────────────┘  └─────────────┘                   │
│                                                       │
└───────────────────────────────────────────────────────┘
    ↓
主CLI集成验证 (Day 29-30)
    ↓
生产部署
```

### 依赖关系

```
CLI-2 (API契约) → CLI-3 (Phase 4) → CLI-4 (AI筛选)
      ↓
    所有CLI
      ↓
CLI-6 (质量保证) → 主CLI (集成)
```

---

## 📊 Resource Allocation

### 时间分配 (28工作日)

| Round | CLI | 开始日期 | 结束日期 | 工作量 | 并行 |
|-------|-----|---------|---------|-------|------|
| **Round 1** | CLI-1 (Phase 3) | Day 1 | Day 14 | 12-14天 | ✅ |
| **Round 1** | CLI-2 (API契约) | Day 1 | Day 14 | 12-14天 | ✅ |
| **Round 1** | CLI-5 (GPU监控) | Day 1 | Day 12 | 8-10天 | ✅ |
| **Round 1** | CLI-6 (质量) | Day 1 | Day 14 | 8-10天 | ✅ |
| **Round 2** | CLI-3 (Phase 4) | Day 15 | Day 26 | 10-12天 | ✅ |
| **Round 2** | CLI-4 (AI筛选) | Day 15 | Day 26 | 10-12天 | ✅ |
| **集成** | 主CLI | Day 27 | Day 28 | 2天 | - |
| **部署** | 主CLI | Day 29 | Day 30 | 2天 | - |

### 任务总量统计

| CLI | 任务数 | 预估人天 | 优先级 |
|-----|--------|---------|--------|
| CLI-1: Phase 3 K线图 | 20 | 12-14 | Round 1 |
| CLI-2: API契约 | 17 | 12-14 | Round 1 (最高) |
| CLI-3: Phase 4完整 | 18 | 10-12 | Round 2 |
| CLI-4: AI筛选 | 18 | 10-12 | Round 2 |
| CLI-5: GPU监控 | 18 | 8-10 | Round 1 |
| CLI-6: 质量保证 | 20 | 8-10 | Round 1 (贯穿) |
| **总计** | **111** | **60-72** | - |

**并行优化**:
- 传统串行: 60-72天
- 多CLI并行: 28天 (节省53%时间)

### 技术栈分布

**后端 (Python)**:
- FastAPI 0.114+
- Pydantic 2.0+ (API契约)
- TA-Lib (161指标计算)
- pynvml (GPU监控)
- transformers (NLP查询)

**前端 (TypeScript + Vue 3)**:
- klinecharts 9.6.0 (K线图)
- ECharts (性能图表)
- Element Plus (UI组件)
- Playwright (E2E测试)

**数据库**:
- PostgreSQL 17+ (缓存+历史数据)
- TDengine (高频时序数据)
- Redis (实时缓存)

**测试与质量**:
- pytest + pytest-cov (单元测试)
- Vitest + Vue Test Utils (前端测试)
- Ruff + Pylint + Bandit (代码质量)
- Locust + Lighthouse (性能测试)

---

## 📁 Deliverables by CLI

### CLI-1: Phase 3 Enhanced K-line Charts

**交付物**:
- [x] `ProKLineChart.vue` - 专业K线图组件
- [x] 70+ technical indicators integration
- [x] Multi-period data switching (1m/5m/15m/1h/1d/1w)
- [x] A股特性 (涨跌停/前复权/T+1)
- [x] 60fps smooth rendering
- [x] E2E tests (Playwright)

**文档**:
- `docs/guides/web/WEB_FRAMEWORK_INCREMENTAL_OPTIMIZATION_PLAN.md`
- `README_CLI1.md`

### CLI-2: API Contract Standardization

**交付物**:
- [x] `UnifiedResponse<T>` generic response format
- [x] `ErrorCode` enum (200+ codes)
- [x] OpenAPI 3.0 Schema (200+ endpoints)
- [x] Pydantic models (DTO validation)
- [x] `api-contract-sync-manager` (management platform)
- [x] `api-contract-sync` (CLI tool)
- [x] CI/CD pre-commit hooks

**文档**:
- `docs/api/API_CONTRACT_SPECIFICATION.md`
- `docs/api/CONTRACT_SYNC_GUIDE.md`
- `README_CLI2.md`

### CLI-3: Phase 4 Complete Implementation

**交付物**:
- [x] `AStockRulesEngine` (T+1/涨跌停/100股)
- [x] `IndicatorRegistry` (161 indicators metadata)
- [x] `BatchIndicatorCalculator` (GPU accelerated)
- [x] TA-Lib wrapper (all 161 indicators)
- [x] PostgreSQL caching layer (>80% hit rate)
- [x] API endpoints (calculation + batch)
- [x] Unit tests (>80% coverage)

**文档**:
- `docs/indicators/INDICATOR_LIBRARY_GUIDE.md`
- `docs/indicators/ASTOCK_RULES_ENGINE.md`
- `README_CLI3.md`

### CLI-4: Phase 5 AI Smart Screening

**交付物**:
- [x] `QueryParser` (NLP → structured query)
- [x] 9 predefined query templates
- [x] `StockRecommendationEngine` (scoring algorithm)
- [x] `AlertRuleEngine` (4 alert types)
- [x] SSE real-time push (alerts + recommendations)
- [x] Frontend UI (RecommendationList + AlertCenter)
- [x] E2E tests (query → recommendation → alert)

**文档**:
- `docs/ai_screening/AI_SCREENING_ARCHITECTURE.md`
- `docs/ai_screening/QUERY_SYNTAX_GUIDE.md`
- `README_CLI4.md`

### CLI-5: Phase 6 GPU Monitoring Dashboard

**交付物**:
- [x] `GPUMonitoringService` (pynvml wrapper)
- [x] `PerformanceCollector` (GFLOPS/speedup metrics)
- [x] `HistoryDataService` (PostgreSQL persistence)
- [x] `OptimizationAdvisor` (5 optimization rules)
- [x] Frontend dashboard (GPUStatusCard + PerformanceChart)
- [x] SSE real-time push (2s refresh)
- [x] Alert system (4 alert types)

**文档**:
- `docs/gpu_monitoring/GPU_MONITORING_ARCHITECTURE.md`
- `docs/gpu_monitoring/OPTIMIZATION_GUIDE.md`
- `README_CLI5.md`

### CLI-6: Quality Assurance

**交付物**:
- [x] Unit tests (>80% coverage)
- [x] Frontend component tests (>70% coverage)
- [x] Integration tests (API endpoints)
- [x] E2E tests (Playwright)
- [x] Code quality reports (Ruff/Pylint/Bandit)
- [x] Performance test reports (Locust/Lighthouse)
- [x] Final quality report

**文档**:
- `docs/quality/TESTING_GUIDE.md`
- `docs/quality/CODE_QUALITY_STANDARDS.md`
- `docs/quality/FINAL_QUALITY_REPORT.md`
- `README_CLI6.md`

---

## 🎯 Milestones & Acceptance Criteria

### Round 1 Milestones (Day 1-14)

| Milestone | Date | Acceptance Criteria |
|-----------|------|---------------------|
| M1: Round 1 Kickoff | Day 1 | 4 worktrees created, README initialized |
| M2: Round 1 Mid-point | Day 7 | CLI-1,2,5,6 50% tasks completed |
| M3: Round 1 Complete | Day 14 | CLI-1,2,5,6 100% tasks completed, merged to main |

### Round 2 Milestones (Day 15-28)

| Milestone | Date | Acceptance Criteria |
|-----------|------|---------------------|
| M4: Round 2 Kickoff | Day 15 | CLI-3,4 worktrees created, dependencies verified |
| M5: Round 2 Mid-point | Day 21 | CLI-3,4 50% tasks completed |
| M6: Round 2 Complete | Day 26 | CLI-3,4 100% tasks completed, merged to main |

### Integration & Deployment (Day 27-30)

| Milestone | Date | Acceptance Criteria |
|-----------|------|---------------------|
| M7: Integration Validation | Day 27-28 | All CLIs integrated, E2E tests pass |
| M8: Production Deployment | Day 29-30 | Deployed to production, quality report published |

---

## ⚠️ Risk Assessment & Mitigation

### High-Priority Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **CLI-2未按时交付** | Medium | High | 标记为最高优先级,每日监控进度 |
| **CLI-3/4依赖阻塞** | Medium | High | 提前Mock数据,允许并行开发UI |
| **集成测试失败** | Low | High | CLI-6贯穿全程,及早发现问题 |
| **性能不达标** | Low | Medium | 每个CLI独立性能测试,不达标不合并 |
| **Git冲突** | Medium | Medium | Worktree隔离,主CLI统一合并 |

### Contingency Plans

**Plan A: CLI-2延期** (影响CLI-3/4)
- **应对**: CLI-3/4使用Mock统一响应格式先行开发UI
- **时间缓冲**: 允许CLI-2延期2天,Round 2顺延

**Plan B: GPU监控性能问题** (CLI-5)
- **应对**: 降级方案,仅显示基础指标
- **核心保留**: GPU利用率+温度+显存,其他可选

**Plan C: AI推荐准确率不达标** (CLI-4)
- **应对**: 使用预定义模板作为主要功能
- **NLP查询**: 降级为可选功能

---

## 📈 Success Metrics

### Technical Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Test Coverage** | > 80% | pytest-cov, Vitest |
| **Code Quality** | Pylint > 8.0 | Ruff + Pylint reports |
| **API Performance** | RPS > 500 | Locust load test |
| **Frontend Performance** | Lighthouse > 90 | Lighthouse CI |
| **Security** | 0 high-severity issues | Bandit + Safety |

### Business Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Development Time** | 28 days | Project timeline tracking |
| **Defect Density** | < 5 defects/KLOC | Bug tracking system |
| **Deployment Success Rate** | 100% (first time) | Deployment logs |
| **User Satisfaction** | > 4.0/5 | Post-deployment survey |

---

## 📚 Supporting Documentation

### Implementation Guides

1. **[Multi-CLI Worktree Management](../../../docs/guides/MULTI_CLI_WORKTREE_MANAGEMENT.md)** - 完整的多CLI协作手册
2. **[Git Worktree Main CLI Manual](../../../docs/guides/GIT_WORKTREE_MAIN_CLI_MANUAL.md)** - Git Worktree命令参考
3. **[Progress Monitoring & Milestones](../../../docs/guides/.multi-cli-tasks/PROGRESS_MONITORING_AND_MILESTONES.md)** - 进度监控与里程碑管理

### Task Allocation Files

1. **[CLI-1 Phase 3 Tasks](../../../docs/guides/.multi-cli-tasks/CLI-1_PHASE3_TASKS.md)** - K线图任务分配
2. **[CLI-2 API Contract Tasks](../../../docs/guides/.multi-cli-tasks/CLI-2_API_CONTRACT_TASKS.md)** - API契约任务分配
3. **[CLI-3 Phase 4 Complete Tasks](../../../docs/guides/.multi-cli-tasks/CLI-3_PHASE4_COMPLETE_TASKS.md)** - Phase 4完整任务分配
4. **[CLI-4 Phase 5 AI Screening Tasks](../../../docs/guides/.multi-cli-tasks/CLI-4_PHASE5_AI_SCREENING_TASKS.md)** - AI筛选任务分配
5. **[CLI-5 Phase 6 GPU Monitoring Tasks](../../../docs/guides/.multi-cli-tasks/CLI-5_PHASE6_GPU_MONITORING_TASKS.md)** - GPU监控任务分配
6. **[CLI-6 Quality Assurance Tasks](../../../docs/guides/.multi-cli-tasks/CLI-6_QUALITY_ASSURANCE_TASKS.md)** - 质量保证任务分配

### Original Proposal

- **[Frontend Six-Phase Optimization Proposal](./proposal.md)** - 原始六阶段优化提案

---

## ✅ Approval Checklist

请在批准此实施方案前确认以下事项:

### Technical Readiness

- [ ] **Git Worktree Environment**: 主仓库支持Git Worktree (Git 2.5+)
- [ ] **Development Environment**: 所有依赖已安装 (Python 3.12+, Node 18+, PostgreSQL 17+)
- [ ] **GPU Environment**: GPU加速引擎已验证 (Phase 6.4完成, 68.58x speedup)
- [ ] **Database Schema**: 所有数据库表结构已定义

### Resource Availability

- [ ] **CLI Workers**: 6个CLI Worker可同时工作 (或顺序工作)
- [ ] **Main CLI**: 主CLI可用于监控和集成
- [ ] **Infrastructure**: 开发/测试环境资源充足

### Risk Acceptance

- [ ] **并行开发风险**: 理解并接受多CLI并行带来的协调复杂度
- [ ] **依赖风险**: 理解CLI-2延期会影响CLI-3/4,已制定应对方案
- [ ] **集成风险**: 理解最终集成可能出现冲突,已分配2天集成时间

### Quality Standards

- [ ] **测试覆盖率**: 同意>80%的覆盖率要求
- [ ] **代码质量**: 同意Pylint>8.0的质量标准
- [ ] **性能基准**: 同意API RPS>500, 前端Lighthouse>90的性能要求

---

## 🚀 Next Steps (Post-Approval)

**立即执行 (Day 1)**:
1. ✅ Create 6 task allocation files (已完成)
2. ✅ Define progress monitoring mechanism (已完成)
3. ✅ Create implementation plan (本文档)
4. ⏳ **等待用户审批**

**审批通过后**:
1. **Day 1 Morning**: 创建Round 1的4个worktrees (CLI-1,2,5,6)
2. **Day 1 Afternoon**: 初始化每个worktree的README和任务清单
3. **Day 1 Evening**: 启动自动化监控脚本
4. **Day 2+**: Worker CLIs开始独立工作

**主CLI角色** (贯穿全程):
- 每2小时运行进度监控脚本
- 每日9:00生成进度报告
- 发现阻塞问题时提供解决方案文档
- Day 27-28执行集成验证
- Day 29-30执行生产部署

---

## 📞 Contact & Support

**Main CLI (Manager)**:
- **Location**: `/opt/claude/mystocks_spec`
- **Branch**: `main`
- **Role**: Coordination, Monitoring, Integration

**Worker CLIs**:
- **CLI-1**: `/opt/claude/mystocks_phase3_frontend` (phase3-kline-charts)
- **CLI-2**: `/opt/claude/mystocks_phase6_api_contract` (phase6-api-contract)
- **CLI-3**: `/opt/claude/mystocks_phase4_complete` (phase4-complete-implementation)
- **CLI-4**: `/opt/claude/mystocks_phase5_ai_screening` (phase5-ai-screening)
- **CLI-5**: `/opt/claude/mystocks_phase6_monitoring` (phase6-gpu-monitoring)
- **CLI-6**: `/opt/claude/mystocks_phase6_quality` (phase6-quality-assurance)

**问题上报**:
- 在各自worktree的README中更新"## ⚠️ 阻塞问题"章节
- 主CLI通过监控脚本自动发现

---

**Approval Required**: 请确认是否批准此多CLI并行实施方案。

**签署**:
- [ ] **技术负责人**: ___________________  日期: ___________
- [ ] **项目经理**: ___________________  日期: ___________
- [ ] **质量负责人**: ___________________  日期: ___________

---

**文档版本**: v1.0
**最后更新**: 2025-12-29
**作者**: Main CLI (Manager)
**状态**: ⏳ Pending Approval
