# Code Refactoring: Large Files Split

**Change ID**: `refactor-large-code-files`
**Type**: Refactoring
**Status**: Draft
**Created**: 2026-01-28
**Author**: Claude Code
**Approver**: Pending

---

## 📋 Summary

拆分项目中65+个超过1000行的代码文件，提升代码可维护性、可测试性和团队开发效率。

### 问题陈述

当前项目存在大量超大文件（1000-3238行），导致：
- 🔴 **维护困难**：单文件包含过多职责
- 🔴 **测试困难**：无法细粒度测试
- 🔴 **协作冲突**：多人同时修改同一文件
- 🔴 **代码重复**：5对重复文件（89-95%重复度）

### 建议方案

基于 `docs/reports/CODE_FILES_OVER_1000_LINES_2026-01-28.md` 和 `docs/code_refactoring_plan.md`：

1. **Week 1**: 合并重复代码（5对文件）
2. **Week 2-3**: 拆分2000+行文件（10个文件）
3. **Week 4-8**: 拆分1000-1999行文件（55个文件）
4. **Week 8**: 建立质量保障机制

### 预期收益

- 📈 **代码质量**：平均文件行数从1500降至500
- 🧪 **测试覆盖率**：从6%提升至80%+
- ⚡ **开发效率**：减少50%的merge冲突
- 🔄 **维护成本**：降低70%的bug修复时间

---

## 🎯 Scope

### In Scope（包含范围）

#### 1. 重复代码合并
- `src/adapters/akshare/market_data.py` vs `src/interfaces/adapters/akshare/market_data.py`
- `src/domain/monitoring/*` vs `src/monitoring/*`（4对文件）
- `src/gpu/acceleration/gpu_acceleration_engine.py` vs `src/gpu/api_system/utils/gpu_acceleration_engine.py`

#### 2. Python超大文件拆分（2000+行）
- `src/interfaces/adapters/akshare/market_data.py` (2,521行)
- `src/adapters/akshare/market_data.py` (2,249行)
- `src/advanced_analysis/decision_models_analyzer.py` (1,659行)
- 其他21个1000+行Python文件

#### 3. 后端API文件拆分
- `web/backend/app/api/risk_management.py` (2,112行)
- `web/backend/app/services/data_adapter.py` (2,016行)
- `web/backend/app/api/data.py` (1,786行)
- 其他7个1000+行后端文件

#### 4. 前端Vue组件拆分（2000+行）
- `web/frontend/src/views/artdeco-pages/ArtDecoMarketData.vue` (3,238行)
- `web/frontend/src/views/artdeco-pages/ArtDecoDataAnalysis.vue` (2,425行)
- `web/frontend/src/components/artdeco/advanced/ArtDecoDecisionModels.vue` (2,398行)

#### 5. TypeScript类型文件拆分
- `web/frontend/src/api/types/common.ts` (2,235行)

### Out of Scope（不包含范围）

- 文档文件（.md）
- 自动生成文件（generated-types.ts）
- node_modules、dist、build等构建产物
- History Mode 迁移任务（已在 `docs/guides/history-mode-deployment-guide.md` 中标记为"完成"）

### 特殊说明：测试文件处理（Phase 5）

虽然测试文件当前列为优先级P1，但本提案明确包含测试文件重构作为**Phase 5**独立阶段：
- 优先级：**P1.5**（核心应用代码重构完成后立即处理）
- 时间：**Week 9-10**
- 范围：11个大型测试文件（1000-2120行）
- 详见 `REQ-6: 拆分大型测试文件`

---

## 🔧 Requirements

### ADDED Requirements

#### REQ-1: 合并重复代码

**Priority**: P0 (Critical)

**Description**: 消除5对重复代码，统一到单一位置

**Acceptance Criteria**:
- [ ] 5对重复文件已分析完成
- [ ] 主副本和副本已识别
- [ ] 所有导入路径已更新
- [ ] 副本文件已删除
- [ ] 测试套件全部通过
- [ ] 无编译错误

**Scenarios**:

##### Scenario 1: 分析重复代码差异

**Given**: 5对可能重复的文件

**When**: 开发者运行差异分析工具

**Then**:
- 生成详细的差异报告
- 计算重复度百分比
- 识别每个文件对的最新修改时间
- 推荐保留哪个版本

##### Scenario 2: 选择主副本

**Given**: 差异报告显示两个文件89-95%重复

**When**: 开发者审查差异报告

**Then**:
- 保留更新、更完整的版本作为主副本
- 删除旧的或功能较弱的副本
- 更新所有导入到主副本

##### Scenario 3: 更新导入路径

**Given**: 副本文件被删除

**When**: 其他代码尝试导入已删除的文件

**Then**:
- 自动重定向到主副本
- 无编译错误
- 功能行为保持一致

---

#### REQ-2: 拆分Python超大文件（2000+行）

**Priority**: P0 (Critical)

**Description**: 拆分10个超过2000行的Python文件

**Acceptance Criteria**:
- [ ] 所有文件拆分为<500行的模块
- [ ] 每个模块职责单一
- [ ] 模块间依赖清晰
- [ ] 所有测试通过
- [ ] 性能无明显下降（±5%）

**Scenarios**:

##### Scenario 1: 按功能模块拆分

**Given**: `src/interfaces/adapters/akshare/market_data.py` (2,521行)

**When**:
- 按市场数据类型拆分为独立模块
- 创建统一的抽象基类
- 实现标准的数据源接口

**Then**:
- 生成6个独立模块（每个< 500行）
- 通过基类实现代码复用
- 所有功能保持不变

##### Scenario 2: 按领域拆分

**Given**: `web/backend/app/api/risk_management.py` (2,112行)

**When**:
- 按风险类型拆分为独立服务
- API层仅保留端点定义
- 业务逻辑移至服务层

**Then**:
- API文件 < 500行
- 服务模块职责单一
- 易于测试和维护

---

#### REQ-3: 拆分Vue超大组件（2000+行）- 遵循ArtDeco"一组件多Tab"架构

**Priority**: P0 (Critical)

**Description**: 拆分3个超过2000行的Vue组件，**严格遵循ArtDeco设计系统"一组件多Tab"核心原则**

**核心架构原则**:
- ✅ **子组件拆分**：将Tab内容抽取为**子组件 (Child Components)**
- ✅ **父组件编排**：父组件负责Tab切换和动态加载子组件
- ❌ **独立路由错误**：**不要**将Tab内容拆分为独立路由页面
- ✅ **配置驱动**：通过PAGE_CONFIG动态获取API/WS资源

**Acceptance Criteria**:
- [ ] 组件拆分为<500行的**子组件**（非独立路由）
- [ ] 父组件继续管理Tab切换状态
- [ ] 使用组合式API提取逻辑到Composables
- [ ] Props传递清晰明确（层级>2使用Provide/Inject或Pinia）
- [ ] 集成PAGE_CONFIG系统动态管理API/WS资源
- [ ] 所有UI功能保持不变
- [ ] 页面性能无明显下降（±5%）

**Scenarios**:

##### Scenario 1: 组件拆分为子组件（遵循"一组件多Tab"原则）

**Given**: `ArtDecoMarketData.vue` (3,238行) 包含多个Tab

**When**:
- 将每个Tab内容抽取为独立的子组件文件（如 `MarketDataOverview.vue`）
- 父组件 `ArtDecoMarketData.vue` 导入并动态渲染子组件
- 父组件继续管理Tab切换状态和逻辑
- 子组件通过Props接收数据，通过Emit向父组件通信

**Then**:
- 7个子组件职责明确（每个 < 500行）
- 父组件仅负责Tab编排和状态管理
- **不创建新路由**（用户体验保持一致）
- 易于单独测试和维护

##### Scenario 2: 提取Composables

**Given**: 大型Vue组件包含复杂业务逻辑

**When**:
- 提取共享逻辑到composables（如 `useMarketData.ts`）
- 使用useXxx命名约定
- 保持响应式特性

**Then**:
- 逻辑可复用
- 组件代码更清晰
- 测试更容易

##### Scenario 3: 集成PAGE_CONFIG统一配置系统

**Given**: Vue组件需要动态获取API端点和WebSocket频道

**When**:
- 父组件导入 `PAGE_CONFIG` 从 `@/config/pageConfig`
- 根据当前激活的Tab动态获取对应的 `apiEndpoint` 和 `wsChannel`
- 子组件通过Props或Inject获取配置

**Then**:
- 无硬编码API/WS路径
- 配置集中在统一位置管理
- 支持运行时配置切换

---

#### REQ-4: 拆分TypeScript类型文件

**Priority**: P0 (Critical)

**Description**: 拆分2个超过2000行的TypeScript文件

**Acceptance Criteria**:
- [ ] 类型定义按功能分类
- [ ] 每个文件< 1000行
- [ ] 使用命名空间组织
- [ ] 类型导出清晰
- [ ] 无TypeScript编译错误

---

#### REQ-5: 前端组件与统一配置系统集成（PAGE_CONFIG）

**Priority**: P0 (Critical)

**Description**: 确保重构后的Vue组件集成统一配置系统，避免硬编码API/WS路径

**Acceptance Criteria**:
- [ ] 所有父组件导入 `PAGE_CONFIG` 从 `@/config/pageConfig`
- [ ] 父组件通过 `PAGE_CONFIG` 动态获取当前激活Tab的 `apiEndpoint`
- [ ] 父组件通过 `PAGE_CONFIG` 动态获取当前激活Tab的 `wsChannel`
- [ ] 子组件通过Props或Inject接收配置信息
- [ ] 配置覆盖率从23%提升至100%（重构的组件）
- [ ] 无硬编码API端点或WebSocket频道

**Scenarios**:

##### Scenario 1: 父组件集成PAGE_CONFIG

**Given**: `ArtDecoMarketData.vue` 父组件完成子组件拆分

**When**:
- 父组件导入 `PAGE_CONFIG`
- 根据当前激活Tab的key（如 `market-realtime`）获取配置
- 将配置传递给子组件

**Then**:
- API端点动态获取（无硬编码）
- WebSocket频道动态配置
- 支持运行时配置切换

##### Scenario 2: 子组件接收配置

**Given**: 子组件需要访问API和WebSocket配置

**When**:
- 父组件通过Props传递配置
- 或使用Provide/Inject注入配置

**Then**:
- 子组件不直接访问 `PAGE_CONFIG`
- 配置来源清晰（来自父组件）
- 易于测试和Mock

---

#### REQ-6: 拆分大型测试文件（Phase 5 - P1.5优先级）

**Priority**: P1.5 (High - 紧随核心代码重构)

**Description**: 拆分11个超过1000行的测试文件，提升测试代码的可读性、可维护性和执行效率

**Acceptance Criteria**:
- [ ] 每个测试文件 < 1000行（推荐 < 800行）
- [ ] 按测试功能模块拆分（如按数据源、按验证类型）
- [ ] 每个测试模块可独立运行
- [ ] 使用pytest fixtures共享测试数据
- [ ] Mock数据统一管理
- [ ] 测试覆盖率不下降

**Scenarios**:

##### Scenario 1: 按功能模块拆分测试文件

**Given**: `tests/ai/test_ai_assisted_testing.py` (2,120行)

**When**:
- 按AI功能类型拆分为多个测试文件
- 提取共享fixtures到 `conftest.py`
- 统一Mock数据管理

**Then**:
- 生成3-4个独立测试文件（每个 < 700行）
- 测试功能模块清晰
- 易于定位和维护测试用例

##### Scenario 2: 测试文件优先级排序

**Given**: 11个大型测试文件待拆分

**When**:
- 优先拆分 > 1500行的测试文件
- 保留功能完整的测试套件
- 确保测试基线不破坏

**Then**:
- 最关键的测试文件优先处理
- 测试执行效率提升
- 测试失败定位更快速

**测试文件清单**（按优先级排序）:
| 文件 | 行数 | 优先级 | 建议拆分方案 |
|------|------|--------|-------------|
| `tests/ai/test_ai_assisted_testing.py` | 2,120 | P1.5 | 按AI功能拆分（3-4个文件） |
| `tests/adapters/test_akshare_adapter.py` | 1,905 | P1.5 | 按数据源方法拆分 |
| `tests/security/test_security_compliance.py` | 1,824 | P1.5 | 按安全模块拆分 |
| `tests/monitoring/test_monitoring_alerts.py` | 1,489 | P2 | 按告警类型拆分 |
| `tests/ai/test_data_analyzer.py` | 1,461 | P2 | 按分析方法拆分 |
| `tests/security/test_security_vulnerabilities.py` | 1,226 | P2 | 按漏洞类型拆分 |
| `tests/contract/test_contract_validator.py` | 1,204 | P2 | 按验证规则拆分 |
| `tests/dashboard/test_dashboard.py` | 1,183 | P2 | 按功能模块拆分 |
| `tests/unit/core/test_monitoring.py` | 1,093 | P2 | 按监控功能拆分 |
| `tests/metrics/test_quality_metrics.py` | 1,073 | P2 | 按指标类型拆分 |
| `tests/reporting/test_report_generator.py` | 1,005 | P2 | 按报告类型拆分 |

---

#### REQ-7: 建立质量保障机制

**Priority**: P1 (High)

**Description**: 防止未来产生大文件，并与 `code_refactoring_plan.md` 的KPI体系对齐

**Acceptance Criteria**:
- [ ] Pre-commit hook检查文件大小
- [ ] 代码审查checklist包含文件大小检查
- [ ] CI/CD流水线拒绝超大文件的PR
- [ ] 开发规范文档更新完成
- [ ] KPI监控系统配置完成（SonarQube/CodeClimate）
- [ ] 定期生成代码复杂度报告

**Scenarios**:

##### Scenario 1: Pre-commit检查

**Given**: 开发者提交代码

**When**: 新增或修改文件超过1000行

**Then**:
- Pre-commit hook发出警告
- 要求开发者说明原因
- 提供拆分建议链接

##### Scenario 2: PR审查检查

**Given**: Pull Request包含大文件

**When**: Reviewer审查PR

**Then**:
- 检查文件大小是否合理
- 如果超过阈值，要求拆分
- 记录到代码审查系统

##### Scenario 3: KPI持续监控

**Given**: 重构完成后的代码库

**When**:
- 配置SonarQube或CodeClimate集成
- 定期生成代码复杂度和质量报告
- 监控测试覆盖率变化

**Then**:
- 代码质量指标可视化
- 及时发现新的大文件
- 质量趋势可追踪

---

## 🎯 Success Metrics

**KPI来源**: 直接引用 `docs/code_refactoring_plan.md` 中定义的量化指标、性能指标、质量指标和项目管理指标

### 量化指标（Quantitative Metrics）

| 指标 | 当前值 | 目标值 | 测量方法 |
|------|--------|--------|---------|
| **超大文件(>2000行)** | 10个 | **0个** | 统计代码行数 |
| **大文件(1000-1999行)** | 65个 | **< 20个** | 统计代码行数 |
| **重复代码对** | 5对 | **0对** | 重复度分析 |
| **平均文件行数** | ~1500行 | **< 500行** | 统计所有文件 |
| **测试覆盖率** | 6% | **80%+** | 测试套件运行 |
| **合并冲突频率** | 高 | **降低50%** | Git冲突统计 |
| **单个文件修改影响范围** | 3-5个文件 | **≤ 2个文件** | 依赖分析 |

### 质量指标（Quality Metrics）

| 指标 | 当前值 | 目标值 | 测量方法 |
|------|--------|--------|---------|
| **代码可维护性指数** | 低 | **中-高** | 代码审查评分 |
| **模块耦合度** | 高 | **低** | 静态分析工具 |
| **单元测试通过率** | 60% | **95%** | CI/CD测试结果 |
| **代码复杂度（圈复杂度）** | > 15 | **< 10** | SonarQube分析 |
| **代码重复率** | 89-95% | **< 5%** | 重复代码检测 |

### 性能指标（Performance Metrics）

| 指标 | 测量方法 | 目标 |
|------|----------|------|
| **前端加载时间** | Lighthouse/DevTools | 无明显下降（±5%） |
| **API响应时间** | 性能监控 | 无明显下降（±5%） |
| **测试执行时间** | pytest运行时间 | 降低或持平 |

### 项目管理指标（Project Management Metrics）

| 指标 | 测量方法 | 目标 |
|------|----------|------|
| **开发效率提升** | 功能开发时间 | 减少30% |
| **Bug修复时间** | Issue追踪系统 | 降低70% |
| **新功能开发时间** | Sprint统计 | 减少30% |
| **代码审查时间** | PR统计 | 减少40% |

### KPI监控系统（实施要求）

根据 `REQ-7: 建立质量保障机制`，需配置以下KPI监控：

1. **SonarQube/CodeCloud集成**
   - 代码复杂度趋势图
   - 代码重复率监控
   - 测试覆盖率追踪
   - 技术债务指数

2. **定期报告生成**
   - 每周代码质量报告
   - 每月KPI趋势分析
   - 每阶段重构效果评估

3. **告警机制**
   - 新增超大文件自动告警
   - 测试覆盖率下降告警
   - 代码重复率超标告警

---

## 🗓️ Design Decisions

### DEC-1: 采用领域驱动拆分策略

**Rationale**: 按业务领域拆分比按技术层面拆分更符合业务逻辑

**Decision**:
- Python后端文件按**领域**拆分（market, trading, risk, monitoring等）
- Vue组件按**功能模块**拆分（子组件模式，非独立路由）
- TypeScript类型按**数据类型**拆分

### DEC-2: 保留功能向后兼容（引用关系维系策略）

**Rationale**: 确保拆分过程不影响现有功能，引用关系不断裂

**Decision**:
- 所有API端点保持不变
- 组件Props保持兼容
- 导出路径使用别名向后兼容
- **采用渐进式重构策略**（小步快跑，频繁验证）

**Python后端兼容层实现**:
```python
# 原文件保留兼容层（使用DeprecationWarning）
import warnings

def deprecated(old_name: str, new_path: str):
    """生成废弃警告的装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"{old_name} 已被废弃，请迁移至 {new_path}。",
                DeprecationWarning,
                stacklevel=2
            )
            return func(*args, **kwargs)
        return wrapper
    return decorator

# 示例：data_access.py 保留兼容层
from .storage.access.tdengine import get_market_data as _new_get_market_data

@deprecated("data_access.get_market_data", "storage.access.tdengine.get_market_data")
def get_market_data(*args, **kwargs):
    """保留原接口名，重定向到新模块实现"""
    return _new_get_market_data(*args, **kwargs)
```

**`__init__.py` 聚合导出策略**:
```python
# module/__init__.py (拆分后的聚合导出)
from .sub_module_a import function_a as old_function_a
from .sub_module_b import function_b as old_function_b

# 确保外部模块仍可通过 from module import old_function_a 访问
```

**Vue组件向后兼容**:
- 父组件导入子组件并动态渲染
- 原有对外引用关系保持不变（外部仍引用父组件）
- Props/Emit接口保持兼容

**兼容期时间表**:
- **兼容期**: 1-2个迭代周期（4-8周）
- **DeprecationWarning**: 立即生效，提供清晰的迁移路径
- **版本规划**: 在CHANGELOG中标记废弃接口和移除时间表

### DEC-3: 渐进式拆分策略（增量重构）

**Rationale**: 降低风险，避免一次性大规模重构

**Decision**:
- **小步快跑**: 每次只拆分一个功能模块，立即验证
- **独立分支**: 所有重构工作在独立Git功能分支进行
- **频繁提交**: 每完成一个可验证的拆分步骤即提交，附清晰提交信息
- Week 1: 仅处理重复代码（风险最低）
- Week 2-3: 拆分最大文件（影响最大）
- Week 4-8: 分批拆分中等文件
- Week 9-10: 拆分测试文件（P1.5优先级）
- 每周完成后进行测试验证

### DEC-4: 自动生成工具豁免

**Rationale**: 自动生成的文件不应计入代码行数限制

**Decision**:
- `generated-types.ts` 不拆分（3137行，自动生成）
- 其他自动生成文件类似处理

### DEC-5: History Mode迁移状态确认

**Rationale**: 确保不重复已完成的工作

**Decision**:
- 根据 `docs/guides/history-mode-deployment-guide.md`，HTML5 History模式迁移已标记为"完成"
- 本提案**不包含**History Mode迁移任务
- 如需验证完成状态，在启动阶段检查实际路由配置
- 如发现未完成，将其作为独立优先级P0任务处理（不混入本重构提案）

### DEC-6: Vue组件"一组件多Tab"架构原则

**Rationale**: 遵循ArtDeco设计系统核心原则，确保用户体验一致性

**Decision**:
- ✅ **正确做法**：将Tab内容拆分为子组件，父组件负责Tab编排
- ❌ **错误做法**：将Tab内容拆分为独立路由页面
- ✅ **配置驱动**：通过PAGE_CONFIG动态获取API/WS资源
- ✅ **状态管理**：父组件管理Tab状态，子组件通过Props/Inject通信

### DEC-7: 工具辅助重构和引用验证

**Rationale**: 利用自动化工具确保引用关系不断裂

**Decision**:

**IDE自动重构工具使用**:
- **重命名 (Rename)**: VS Code F2功能，自动更新所有引用
- **移动 (Move)**: 移动文件时自动更新导入路径
- **提取 (Extract)**: 提取代码到新函数/组件时自动处理引用
- **重要**: 重构前先提交当前工作，便于出错时回滚

**全局搜索替换流程**:
- 对于IDE无法自动处理的复杂引用（动态导入、字符串拼接路径）
- 通过项目范围搜索（grep, VS Code全局搜索）进行人工确认修改
- 谨慎使用全局替换，限定范围和模式，避免误伤

**依赖分析工具**:
- **Python**:
  - `pyreverse`: 生成模块依赖图，识别依赖关系和循环依赖
  - `pylint`: 报告循环导入等问题
  - 依赖注入: 使用`injector`库解耦模块间硬编码依赖
- **前端**:
  - Vite/Webpack打包工具依赖分析: 分析模块依赖图
  - TypeScript Path Mapping: 规范导入路径，减少相对路径混乱

### DEC-8: 严格验证流程（引用关系完整性检查）

**Rationale**: 通过多层验证确保引用关系完好无损

**Decision**:

**1. 静态代码分析**:
- **Python**: `mypy`, `ruff` - 确保类型检查通过，无未定义变量或未解析导入
- **TypeScript**: `vue-tsc`, `eslint` - 确保编译无错误，无未解析模块
- **Pre-commit Hooks**: 提交前强制执行检查，尽早发现问题

**2. 多层次测试验证**:
- **单元测试**: 为拆分出的每个新函数、类、组件编写单元测试
- **集成测试**: 验证拆分后的模块组合是否按预期工作
- **端到端测试**: Playwright/Cypress测试，模拟用户操作
- **视觉回归测试**: 使用Playwright的`toMatchSnapshot`比对UI差异

**3. 代码审查检查清单**:
- [ ] 所有导入路径已更新（Python: `__init__.py`聚合导出）
- [ ] 兼容层已实现（DeprecationWarning + 重定向）
- [ ] 静态代码分析通过（mypy/ruff/vite-tsc无错误）
- [ ] 单元测试覆盖率不下降
- [ ] 集成测试通过
- [ ] E2E测试通过
- [ ] 性能无明显下降（±5%）
- [ ] 依赖图无循环依赖

**4. 兼容期管理**:
- **兼容期**: 1-2个迭代周期（4-8周）
- **DeprecationWarning**: 立即生效，提供清晰迁移路径
- **版本规划**: CHANGELOG中标记废弃接口和移除时间表

---

## 📋 Risks & Mitigations

### Risk 1: 引入新的Bug

**Probability**: Medium
**Impact**: High

**Mitigation**:
- 每个拆分步骤运行完整测试套件
- 保留原文件备份至archive目录
- 使用Git分支隔离拆分工作
- 每周进行代码审查

### Risk 2: 拆分粒度过细

**Probability**: Medium
**Impact**: Medium

**Mitigation**:
- 制定明确的拆分原则（500行目标）
- 代码审查检查拆分粒度
- 定期评估模块数量合理性

### Risk 3: 导入路径混乱

**Probability**: High
**Impact**: High

**Mitigation**:
- 使用统一导入规范
- IDE自动导入配置
- Pre-commit hook检查导入路径
- 提供迁移工具脚本

### Risk 4: 性能下降

**Probability**: Low
**Impact**: Medium

**Mitigation**:
- 拆分前后性能基准测试
- 监控关键指标（加载时间、响应时间）
- 必要时进行性能优化

---

## 📅 Timeline

| Week | 任务 | 交付物 | 验收标准 |
|------|------|--------|---------|
| **Week 1** | 合并重复代码 | - 5对文件合并<br>- 导入路径更新<br>- 测试通过 | 无重复代码<br>所有测试通过 |
| **Week 2-3** | 拆分2000+行文件 | - Python后端文件拆分<br>- 前端Vue组件拆分（子组件模式）<br>- Composables提取<br>- 测试通过 | 每个文件<500行<br>所有测试通过 |
| **Week 4-8** | 拆分1000-1999行文件 | - 55个文件拆分完成<br>- PAGE_CONFIG集成<br>- 代码质量提升<br>- 测试覆盖率提升80% | 平均行数<500<br>测试覆盖率80% |
| **Week 8** | 建立质量保障 | - Pre-commit hook配置<br>- CI/CD集成<br>- 开发规范文档更新 | 新文件自动检查<br>PR自动审查 |
| **Week 9-10** | 拆分大型测试文件（Phase 5） | - 11个测试文件拆分<br>- Fixtures统一管理<br>- Mock数据优化 | 测试文件<1000行<br>测试覆盖率不降 |

**时间表说明**:
- **Week 1**: Phase 1 - 重复代码合并（风险最低）
- **Week 2-3**: Phase 2-3 - Python和Vue超大文件拆分（影响最大）
- **Week 4-8**: Phase 4 - 中型文件拆分 + 质量保障
- **Week 9-10**: Phase 5 - 测试文件拆分（P1.5优先级）

---

## 👥 Stakeholders

| 角色 | 姓名 | 职责 |
|------|------|------|
| **Approver** | 项目负责人 | 批准提案和优先级 |
| **Architect** | 架构师 | 技术方案审查 |
| **Developers** | 开发团队 | 执行重构任务 |
| **QA** | 测试团队 | 验证功能和测试 |

---

## 📚 References

- `docs/reports/CODE_FILES_OVER_1000_LINES_2026-01-28.md` - 代码文件统计报告
- `docs/code_refactoring_plan.md` - 代码重构方案
- `docs/standards/CODE_SIZE_OPTIMIZATION_SAVED_20251125.md` - 代码长度优化规范
- `docs/standards/FILE_ORGANIZATION_RULES.md` - 文件组织规范
