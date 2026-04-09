# TypeScript Guide Family

> **导航说明**:
> 本文件是 `docs/guides/typescript/` 的 transition index，不是当前仓库共享规则、当前实现边界或唯一 TypeScript 真相源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 [`architecture/STANDARDS.md`](/opt/claude/mystocks_spec/architecture/STANDARDS.md)；若涉及当前代码实现与前端质量治理，请结合根目录 `AGENTS.md`、相关代码与实际验证结果。

## Current Entry Order

这一 family 当前角色是 `supporting`，用于 TypeScript 使用说明、培训材料和历史治理方案，不承担仓库级 trunk。推荐阅读顺序：

1. [`Typescript_QUICKSTART.md`](./Typescript_QUICKSTART.md)
2. [`Typescript_USER_GUIDE.md`](./Typescript_USER_GUIDE.md)
3. [`Typescript_BEST_PRACTICES.md`](./Typescript_BEST_PRACTICES.md)
4. [`Typescript_CONFIG_REFERENCE.md`](./Typescript_CONFIG_REFERENCE.md)
5. 再按需进入 API 参考、培训、排障和历史实施方案

## Active Supporting Guides

- [`Typescript_QUICKSTART.md`](./Typescript_QUICKSTART.md)
  - TypeScript 快速开始入口
- [`Typescript_USER_GUIDE.md`](./Typescript_USER_GUIDE.md)
  - TypeScript 完整使用手册
- [`Typescript_BEST_PRACTICES.md`](./Typescript_BEST_PRACTICES.md)
  - TypeScript 最佳实践与质量建议
- [`Typescript_CONFIG_REFERENCE.md`](./Typescript_CONFIG_REFERENCE.md)
  - TypeScript 配置参考

## Retained Specialized References

- [`Typescript_API_REFERENCE.md`](./Typescript_API_REFERENCE.md)
  - API 参考手册
- [`Typescript_TRAINING_BEGINNER.md`](./Typescript_TRAINING_BEGINNER.md)
  - 新手培训指南
- [`Typescript_TRAINING_ADVANCED.md`](./Typescript_TRAINING_ADVANCED.md)
  - 高级培训材料
- [`Typescript_TROUBLESHOOTING.md`](./Typescript_TROUBLESHOOTING.md)
  - 故障排除指南
- [`TYPESCRIPT_ERROR_FIXING_GUIDE.md`](./TYPESCRIPT_ERROR_FIXING_GUIDE.md)
  - 错误快速修复指南
- [`TYPESCRIPT_SOURCE_FIX_GUIDE.md`](./TYPESCRIPT_SOURCE_FIX_GUIDE.md)
  - 从源头修复类型问题的方法
- [`TYPE_CHECKING_INTEGRATION.md`](./TYPE_CHECKING_INTEGRATION.md)
  - CI/CD Type Checking 集成说明
- [`TypeScript_优化修复方案.md`](./TypeScript_优化修复方案.md)
  - 前端代码质量修复与重构方案
- [`TypeScript_快速修复指南.md`](./TypeScript_快速修复指南.md)
  - 中文快速修复实战指南
- [`TYPEScript_EXTENSION_SYSTEM_PROPOSAL.md`](./TYPEScript_EXTENSION_SYSTEM_PROPOSAL.md)
  - 类型扩展系统设计方案
- [`TYPESCRIPT_EXTENSION_SYSTEM_BALANCED_PLAN.md`](./TYPESCRIPT_EXTENSION_SYSTEM_BALANCED_PLAN.md)
  - 类型扩展系统平衡实施方案
- [`TYPESCRIPT_EXTENSION_SYSTEM_IMPLEMENTATION_PLAN.md`](./TYPESCRIPT_EXTENSION_SYSTEM_IMPLEMENTATION_PLAN.md)
  - 类型扩展系统详细实施计划
- [`TYPESCRIPT_EXTENSION_SYSTEM_IMPLEMENTATION_PLAN_V3.md`](./TYPESCRIPT_EXTENSION_SYSTEM_IMPLEMENTATION_PLAN_V3.md)
  - 类型扩展系统精简实施计划

## Retention Rule

- 该 family 当前保留为 `supporting`，不升级为新的 canonical docs trunk
- 根导航只暴露核心上手/配置/最佳实践入口，其余培训、排障、修复和历史方案统一通过本 index 进入
- 若后续历史方案或专项修复材料入链继续下降，再按 bounded batch 单独评估 archive/delete
