# 目录重构计划 - 根目录整理

> **历史计划说明**:
> 本文件是 API 相关的阶段性计划、路线图或方案材料，不是当前 API 契约、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`；若涉及 API 契约事实源，再以实际的 FastAPI 路由 + Pydantic Schema + `/openapi.json` 为准。
>
> 文内优先级、时间线、实施状态和建议动作如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


## 📊 当前状况分析

**根目录目录数量**: 92个 (严重超标)
**标准目录**: 9个 (src/, config/, scripts/, docs/, tests/, reports/, web/, temp/, logs/)
**需要清理**: 83个目录

## 🎯 重构目标

将92个目录精简为9个标准目录，合并相关功能到统一位置。

## 📋 目录合并策略

### 1. 编号目录合并 (3个目录)
```
02-架构与设计文档/ → docs/architecture/
03-API与功能文档/     → docs/api/
06-项目管理与报告/     → docs/reports/
```

### 2. 功能目录合并
```
CLIS/                   → scripts/cli/
conductor/              → scripts/dev/
buger/                  → scripts/dev/
calcu/                  → src/algorithms/ (如果存在) 或 scripts/dev/

ai_tools/               → scripts/dev/
ai_generated_tests/      → tests/ai/
ai_test_optimizer_toolkit/ → scripts/dev/
```

### 3. 文档目录合并
```
api/                    → docs/api/
architecture/           → docs/architecture/
archive/                → docs/archived/
archived/               → docs/archived/
code_quality/           → docs/standards/
```

### 4. 报告目录合并
```
cli_reports/            → reports/cli/
completion_reports/     → reports/completion/
```

### 5. 备份和临时目录
```
backups/                → 保留 (重要备份)
gpu_migration_backups_*/ → temp/ 或删除
*_backups/              → temp/
```

### 6. 数据目录
```
data/                   → 保留 (重要数据)
grafana/                → config/grafana/
monitoring_data/        → data/monitoring/ 或 reports/
```

### 7. 测试相关
```
smart_ai_tests/         → tests/ai/
test-directory-org/     → temp/
```

### 8. Web相关
```
web-dev/                → web/frontend/ 或 scripts/web/
playwright-tests/       → tests/e2e/
```

## 🔄 实施步骤

### Phase 1: 目录内容分析 (当前阶段)
1. 统计每个目录的文件数量和类型
2. 确定合并策略和目标位置
3. 创建备份和回滚计划

### Phase 2: 安全合并
1. 从最简单目录开始 (空目录、单文件目录)
2. 使用 `git mv` 保留历史记录
3. 逐个验证合并结果

### Phase 3: 复杂目录处理
1. 处理有冲突的目录 (重名文件)
2. 更新所有引用路径
3. 验证功能完整性

### Phase 4: 清理和验证
1. 删除空目录
2. 更新文档引用
3. 运行完整测试套件

## ⚠️ 高风险目录

### 需要特别注意的目录:
- `gpu_migration_backups_*/`: 包含重要迁移数据
- `backups/`: 可能包含生产数据备份
- `data/`: 可能包含实时数据
- `monitoring_data/`: 可能包含监控历史

### 合并冲突预测:
- `api/` vs `03-API与功能文档/`: 需要检查重复内容
- `architecture/` vs `02-架构与设计文档/`: 可能有重复文档
- `reports/` vs `06-项目管理与报告/`: 报告分类冲突

## ✅ 成功标准

- **根目录目录数**: 92个 → 9个 (**90%减少**)
- **功能完整性**: 所有文件可正常访问
- **路径引用**: 所有内部链接正确更新
- **Git历史**: 保留完整的文件移动历史

## 🛡️ 安全措施

1. **备份标签**: `git tag directory-restructure-backup`
2. **逐步执行**: 每次只处理少量目录
3. **回滚计划**: 可通过Git回滚到备份点
4. **测试验证**: 每个合并后运行关键测试

## 📊 预期收益

- **导航效率**: 90%提升 (从92个目录到9个)
- **维护成本**: 80%降低 (统一管理标准目录)
- **新手友好**: 显著提升 (清晰的目录结构)
- **CI/CD效率**: 提升 (标准化的目录布局)</content>
<parameter name="filePath">docs/reports/directory_restructure_plan.md