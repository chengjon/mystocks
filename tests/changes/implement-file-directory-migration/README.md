## Context

MyStocks项目经过2年的快速发展，积累了大量文件，但缺乏有效的目录管理机制。当前根目录包含95个文件，远超规定的5个文件上限。项目规模已达2.9GB，包含1948个Python文件、5137个Markdown文件和26657个JSON文件。

问题根源：
- 缺乏自动化检查和强制执行机制
- 规则文档存在但未实际执行
- 历史遗留问题积累，无有效清理机制
- 团队对目录规范的执行不一致

## Goals / Non-Goals

### Goals
- 将根目录文件数从95个减少到≤5个
- 建立自动化的目录结构检查和维护机制
- 确保所有文件按功能正确分类
- 建立长期有效的目录管理流程
- 提升项目的可维护性和开发效率

### Non-Goals
- 不进行大规模的代码重构
- 不改变现有的功能架构
- 不影响当前的CI/CD流程
- 不要求一次性完成所有迁移

## Decisions

### 迁移策略：渐进式 vs 一次性
**Decision**: 采用渐进式迁移策略
**Rationale**:
- 一次性迁移风险过高，可能影响现有功能
- 渐进式允许逐步验证和调整
- 降低对团队开发的影响
- 更容易回滚和问题排查

### 自动化机制：强制 vs 建议
**Decision**: 实施强制性的自动化检查
**Rationale**:
- 建议性机制依赖自觉性，执行效果差
- 强制机制通过Git hooks确保合规
- 平衡开发效率和规范执行
- 提供禁用选项应对特殊情况

### 文件移动：手动 vs 自动
**Decision**: 优先使用自动化脚本，辅以手动验证
**Rationale**:
- 自动化脚本减少人为错误
- 手动验证确保移动的准确性
- dry-run模式允许预览和确认
- 脚本生成的报告便于审计

## Risks / Trade-offs

### 风险：路径引用错误
- **影响**: 代码无法找到移动后的文件
- **缓解**: 实施全面的路径搜索和更新；分批验证功能

### 风险：Git历史复杂化
- **影响**: 文件移动可能影响Git历史追踪
- **缓解**: 使用 `git mv` 保留历史；创建备份标签

### 风险：团队适应成本
- **影响**: 开发者需要适应新目录结构
- **缓解**: 提供详细的迁移指南；渐进式培训

### 风险：自动化脚本错误
- **影响**: 脚本可能误移动重要文件
- **缓解**: 强制dry-run模式；人工审核；备份机制

## Migration Plan

### Phase 1: 准备和分析 (1天)
1. 创建备份标签
2. 分析所有根目录文件
3. 制定详细的移动计划
4. 测试自动化脚本

### Phase 2: 核心迁移 (2-3天)
1. 批量移动文档文件
2. 批量移动脚本文件
3. 批量移动配置文件
4. 更新路径引用

### Phase 3: 自动化部署 (1天)
1. 启用结构检查脚本
2. 配置Git hooks
3. 测试自动化机制
4. 培训团队使用

### Phase 4: 验证和优化 (1-2周)
1. 全面功能测试
2. 性能影响评估
3. 文档更新
4. 监控机制建立

### Rollback Plan
1. 使用备份标签回滚: `git reset --hard backup-before-directory-migration`
2. 恢复移动的文件（如果有备份）
3. 禁用Git hooks防止重复问题
4. 重新评估迁移策略

## Open Questions

1. **脚本执行权限**: 是否需要在所有开发者环境中配置脚本执行权限？

2. **CI/CD影响**: 当前CI/CD流程是否需要调整以适应新的目录结构？

3. **子模块处理**: 对于web/等子模块的文档，是否需要特殊处理？

4. **监控粒度**: 需要监控哪些具体的目录结构指标？

5. **培训方式**: 如何最有效地让团队理解和适应新规范？

## Technical Implementation

### 自动化脚本架构
```
scripts/maintenance/
├── check-structure.sh      # 结构检查和报告
├── organize-files.sh       # 文件自动整理
└── utils/                  # 辅助工具函数
```

### Git Hook集成
```bash
.git/hooks/pre-commit:
#!/bin/bash
# 运行目录结构检查
if ! scripts/maintenance/check-structure.sh --quiet; then
    echo "Directory structure violations found. Please fix before committing."
    exit 1
fi
```

### 路径解析机制
```python
# 动态项目根目录解析
def get_project_root():
    """获取项目根目录，支持从任何位置执行"""
    current_path = Path(__file__).resolve()
    # 根据特征文件定位根目录
    for parent in current_path.parents:
        if (parent / "requirements.txt").exists():
            return parent
    raise RuntimeError("Could not find project root")
```

## Success Metrics

- **根目录文件数**: 95个 → ≤5个 (目标达成率)
- **自动化执行率**: 100% (Git hooks阻止违规提交)
- **路径引用错误**: 0个 (所有引用正确更新)
- **团队适应时间**: <1周 (培训和适应周期)
- **CI/CD通过率**: 100% (不因目录结构失败)</content>
<parameter name="filePath">openspec/changes/implement-file-directory-migration/design.md