# TypeScript Type Extension System - Design Decisions

## Context
MyStocks项目使用自动生成脚本从后端Pydantic schemas生成TypeScript类型，但前端专用的ViewModel类型无法通过自动生成获得。目前有36个TypeScript编译错误，影响开发效率和代码质量。

## Goals / Non-Goals

### Goals
- 解决36个TypeScript编译错误
- 建立可持续的类型管理系统
- 实现自动生成与手动扩展的分离
- 提升开发体验和类型安全性

### Non-Goals
- 重写现有的自动生成脚本
- 修改后端Pydantic模型结构
- 引入新的构建工具或框架
- 影响现有代码的运行时行为

## Decisions

### Decision 1: Directory Structure Design
**选择**: `src/api/types/extensions/` 独立扩展目录

**理由**:
- 清晰分离自动生成 vs 手动维护
- 避免与现有生成脚本冲突
- 支持按领域组织（strategy/、market/等）
- 易于版本控制和团队协作

**Alternatives Considered**:
- 直接修改自动生成的文件 → 会被覆盖，维护困难
- 创建平行目录结构 → 导入路径混乱
- 使用类型合并 → 复杂性过高

### Decision 2: Type Organization Strategy
**选择**: 按业务领域 + 技术层次双维度组织

**结构**:
```
extensions/
├── strategy/     # 业务领域
├── market/
├── common/
├── ui/          # 技术层次
├── api/
└── utils/
```

**理由**:
- 业务领域分组便于理解和维护
- 技术层次分组支持复用
- 支持渐进式扩展
- 符合单一职责原则

### Decision 3: Export Strategy
**选择**: 统一导出 + 向后兼容

```typescript
// src/api/types/index.ts
export * from './strategy';      // 自动生成
export * from './extensions';    // 手动扩展

// extensions/index.ts
export * from './strategy';
export * from './market';
// ... 其他领域
```

**理由**:
- 保持现有导入路径不变
- 统一访问入口
- 支持增量扩展

### Decision 4: Validation Approach
**选择**: 轻量级类型验证器 + 构建时检查

**实现**:
- `TypeValidator.ts` - 检测命名冲突和完整性
- Pre-commit hooks - 自动运行类型检查
- CI/CD集成 - 确保构建时类型安全

**理由**:
- 平衡验证深度与性能
- 尽早发现问题
- 自动化减少人工成本

### Decision 5: Type Definition Scope
**选择**: 42个类型（12个核心 + 30个扩展）

**核心类型 (12个)**: 解决当前36个错误
**扩展类型 (30个)**: 覆盖80%未来需求

**理由**:
- 核心类型确保立即解决问题
- 扩展类型避免频繁维护
- 平衡投入产出比

## Risks / Trade-offs

### Technical Risks

#### Risk 1: Type Conflicts
**Impact**: 编译失败，开发阻塞
**Probability**: 中等
**Mitigation**:
- 自动化冲突检测工具
- 明确的命名规范（VM后缀区分ViewModel）
- 团队培训和代码审查

#### Risk 2: Performance Impact
**Impact**: 编译时间增加
**Probability**: 低
**Mitigation**:
- 增量编译和缓存
- 按需加载类型定义
- 监控编译时间指标

#### Risk 3: Maintenance Burden
**Impact**: 类型定义过时
**Probability**: 中等
**Mitigation**:
- 文档化维护流程
- 自动化使用情况分析
- 定期审查和清理

### Business Risks

#### Risk 1: Adoption Resistance
**Impact**: 团队不使用新系统
**Probability**: 中等
**Mitigation**:
- 渐进式实施
- 详细培训文档
- 成功案例展示

#### Risk 2: Breaking Changes
**Impact**: 现有代码无法编译
**Probability**: 低
**Mitigation**:
- 100%向后兼容设计
- 充分的测试覆盖
- 快速回滚计划

## Migration Plan

### Phase 1: Pilot Implementation (Week 1)
1. 创建目录结构和基础类型（核心12个）
2. 实现类型验证工具
3. 在开发分支上测试

### Phase 2: Extended Types (Week 2)
1. 添加扩展类型（30个）
2. 完善文档和示例
3. 团队培训

### Phase 3: Production Rollout (Week 3)
1. 完整集成测试
2. Pre-commit hooks配置
3. 生产环境部署

### Rollback Plan
1. 删除 `extensions/` 目录
2. 恢复 `src/api/types/index.ts`
3. 重新运行自动生成脚本

## Open Questions

### Q1: Type Naming Conventions
**是否需要更严格的命名规范？**
- 当前: PascalCase for interfaces, VM suffix for ViewModels
- 考虑: 领域前缀 (StrategyVM, MarketVM)

### Q2: Version Management
**如何处理类型定义的版本演进？**
- 选项1: 语义化版本号
- 选项2: 变更日志记录
- 选项3: Git tags管理

### Q3: Tool Integration
**是否需要IDE插件支持？**
- VS Code扩展提供类型提示
- 自动导入建议
- 类型重构工具

## Implementation Considerations

### Code Organization
- 每个类型文件不超过200行
- 相关类型分组定义
- 清晰的导入导出结构

### Documentation Standards
- 每个接口都有JSDoc注释
- 使用示例和场景说明
- 更新日志记录变更

### Testing Strategy
- 类型定义的单元测试
- 集成测试验证导入
- 端到端测试确保功能完整

## Success Metrics

### Technical Metrics
- **Type Coverage**: 95%+ (from current 60%)
- **Compile Errors**: 0 (from current 36)
- **Build Time**: <30 seconds
- **Type Conflicts**: 0

### Team Metrics
- **Adoption Rate**: 90%+ 团队成员使用新系统
- **Issue Resolution**: 80% 类型相关问题通过新系统解决
- **Development Velocity**: 提升15% (更少的类型错误调试时间)

### Business Metrics
- **Code Quality**: TypeScript错误率降低90%
- **Development Efficiency**: 减少类型相关bug修复时间
- **Maintainability**: 代码可维护性评分提升20%</content>
<parameter name="filePath">openspec/changes/implement-typescript-type-extension-system/design.md