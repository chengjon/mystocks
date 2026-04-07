# Change: Implement TypeScript Type Extension System

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。


## Why
MyStocks项目当前存在36个TypeScript编译错误，主要原因是缺少前端ViewModel类型定义。现有的自动生成脚本只处理后端Pydantic schemas，无法生成前端专用的类型。需要建立一个完整的类型扩展系统，实现自动生成类型与手动扩展类型的分离管理。

## What Changes
- 创建独立的类型扩展目录结构 `src/api/types/extensions/`
- 定义42个TypeScript类型（12个核心 + 30个扩展）
- 实现类型冲突检测和验证工具
- 更新构建脚本集成类型扩展系统
- 解决当前36个TypeScript编译错误

## Impact
- **Affected specs**: frontend-type-system (新增)
- **Affected code**: `web/frontend/src/api/types/`, `package.json`, `tsconfig.json`
- **Breaking changes**: 无 - 向后兼容，现有代码无需修改
- **Performance**: 轻微增加编译时间 (<5秒)，运行时无影响
- **Testing**: 需要添加类型验证测试用例</content>
<parameter name="filePath">openspec/changes/implement-typescript-type-extension-system/proposal.md