# OpenSpec 命令扩展指南

本文档说明如何为 OpenSpec 系统创建和集成新的命令。

## 📁 目录结构

```
docs/guides/openspec-cmd/        # OpenSpec 命令扩展包
├── README.md                    # 本指南文档
├── check.md                     # openspec-check 命令定义
├── check-report-example.md      # 检查报告示例
└── [command-template.md](./command-template.md)  # OpenSpec 命令模板
```

## 🎯 OpenSpec 命令系统概述

OpenSpec 提供了三个核心命令用于管理变更生命周期：
- `/openspec-proposal` - 创建变更提案
- `/openspec-apply` - 实施已批准的变更
- `/openspec-archive` - 归档已完成的变更

## 🔧 创建新命令的步骤

### 步骤 1: 理解命令文件格式

OpenSpec 命令使用标准的 Markdown 格式，包含 YAML front matter：

```markdown
---
name: OpenSpec: CommandName
description: Brief description of what the command does
category: OpenSpec
tags: [openspec, command-tag]
---

<!-- OPENSPEC:START -->
**Guardrails**
- 简洁实现优先，避免不必要复杂性
- 严格遵循请求的目标范围
- 参考 `openspec/AGENTS.md` 获取 OpenSpec 约定

**Steps**
1. 步骤1的详细说明
2. 步骤2的详细说明
...

**Reference**
- 相关参考资料和链接
<!-- OPENSPEC:END -->
```

### 步骤 2: 创建命令文件

在 `.claude/commands/openspec/` 目录下创建新的命令文件：

```bash
# 使用模板创建命令文件
cp docs/guides/openspec-cmd/command-template.md .claude/commands/openspec/your-command.md
# 然后根据需要编辑文件内容
```

### 步骤 3: 实现命令逻辑

根据命令的用途，实现相应的功能：

#### 对于 openspec-check 这样的验证命令：
1. 读取指定变更的任务文件
2. 解析任务完成状态（`- [ ]` vs `- [x]`）
3. 检查代码实现是否存在
4. 生成状态报告
5. 更新任务文件状态

#### 对于其他类型的命令：
- 遵循 OpenSpec 的工作流程
- 保持与现有命令的一致性
- 提供清晰的错误处理

### 步骤 4: 测试命令

1. **语法验证**：
   ```bash
   # 检查 Markdown 格式是否正确
   cat .claude/commands/openspec/your-command.md
   ```

2. **功能测试**：
   - 手动执行命令逻辑
   - 验证输出格式正确性
   - 确认与现有系统的兼容性

3. **集成测试**：
   - 测试与其他 OpenSpec 命令的交互
   - 验证错误处理机制
   - 确认文档更新正确

### 步骤 5: 系统集成

#### 方法 1: 等待系统重载
- 保存命令文件后，系统可能会自动识别
- 某些环境中需要重启或重新加载

#### 方法 2: 手动集成
如果系统不自动识别，可以：
1. 检查命令注册机制
2. 验证文件权限
3. 确认文件路径正确

## 📋 openspec-check 命令示例

### 命令目的
检查指定 OpenSpec 变更中任务的完成状态，生成报告并更新任务状态。

### 实现逻辑

1. **读取任务文件**：
   ```bash
   # 解析 tasks.md 中的任务状态
   grep "^- \[" openspec/changes/CHANGE-ID/tasks.md
   ```

2. **验证代码实现**：
   ```bash
   # 检查文件/组件是否存在
   find web/frontend/src -name "Component.vue"
   ```

3. **生成报告**：
   ```markdown
   # 创建 check-report.md
   - 总体完成统计
   - 各阶段进度
   - 实施建议
   ```

4. **更新状态**：
   ```bash
   # 将验证完成的任务标记为 - [x]
   sed -i 's/- \[ \] Task description/- [x] Task description/' tasks.md
   ```

### 使用示例

```bash
# 检查特定变更
/openspec-check frontend-unified-optimization

# 手动执行检查逻辑
grep "^- \[x\]" openspec/changes/frontend-unified-optimization/tasks.md | wc -l
```

## 🔄 OpenSpec 更新时的命令迁移

当 OpenSpec 系统更新时，按照以下步骤迁移自定义命令：

### 1. 备份现有命令
```bash
# 备份自定义命令
cp -r .claude/commands/openspec/custom-commands/ /tmp/
```

### 2. 更新 OpenSpec
```bash
# 执行 OpenSpec 更新
openspec update
```

### 3. 恢复和调整命令
```bash
# 恢复自定义命令
cp /tmp/custom-commands/* .claude/commands/openspec/

# 检查命令格式兼容性
# 根据新的 OpenSpec 版本调整格式
```

### 4. 测试兼容性
```bash
# 测试所有命令是否正常工作
/openspec-list
/openspec-check your-change-id
```

## 📚 最佳实践

### 命令设计原则
1. **单一职责**：每个命令只做一件事情
2. **一致性**：遵循现有命令的格式和风格
3. **错误处理**：提供清晰的错误信息和恢复机制
4. **文档完整**：包含详细的使用说明和示例

### 命名规范
- 使用动词-名词格式：`check`, `validate`, `archive`
- 避免与现有命令冲突
- 使用描述性名称

### 版本控制
- 将命令文件纳入版本控制
- 为重大变更创建标签
- 维护变更日志

## 🐛 故障排除

### 常见问题

#### 命令未被识别
```bash
# 检查文件是否存在
ls -la .claude/commands/openspec/your-command.md

# 检查文件权限
ls -l .claude/commands/openspec/your-command.md

# 检查文件格式
head -20 .claude/commands/openspec/your-command.md
```

#### 命令执行失败
```bash
# 查看错误日志
tail -f var/log/openspec.log

# 检查依赖项
openspec validate your-change-id
```

#### 格式错误
```bash
# 验证 YAML front matter
head -10 .claude/commands/openspec/your-command.md

# 检查 Markdown 语法
markdown-lint .claude/commands/openspec/your-command.md
```

## 📞 支持和贡献

### 获取帮助
1. 参考 `openspec/AGENTS.md` 获取详细规范
2. 查看现有命令的实现方式
3. 在社区论坛寻求帮助

### 贡献新命令
1. 遵循本文档的创建步骤
2. 提供完整的测试用例
3. 更新相关文档
4. 提交 Pull Request

---

## 📝 变更日志

### v1.0.0 (2026-01-13)
- ✅ 创建 openspec-check 命令
- ✅ 建立命令创建指南
- ✅ 提供完整的使用示例

---

**文档维护者**: Claude Code
**最后更新**: 2026-01-13</content>
<parameter name="filePath">docs/guides/openspec-cmd/README.md
