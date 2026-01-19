# TODO状态显示问题调查报告

## 问题描述
OpenCode显示的TODO状态为 `[Status: 0/1 completed, 1 remaining]`，但实际项目状态应该是 `[Status: 16/142 completed, 126 remaining]`。

## 调查时间线
- **开始时间**: 2026-01-17 11:14
- **调查持续时间**: ~2小时
- **状态**: 未找到根本原因，决定暂停调查并记录经验

## 调查过的可能原因

### 1. Task Master系统状态
**检查结果**: ✅ 已验证
- **位置**: `.taskmaster/tasks/tasks.json`
- **实际状态**: 16/142 已完成 (126 remaining)
- **结论**: Task Master数据正确，不是问题所在

### 2. OpenSpec任务系统
**检查结果**: ✅ 已验证
- **位置**: `openspec/changes/consolidate-technical-debt-remediation/tasks.md`
- **实际状态**: 142个任务，大部分pending状态
- **结论**: OpenSpec数据与Task Master不一致，但都不是"0/1"的状态

### 3. Claude Code Hooks系统
**检查结果**: ✅ 已全面检查
- **SessionStart Hook**: `session-start-task-master-injector.sh`
  - 功能：注入Task Master上下文到Claude会话
  - 状态：正常工作，读取Task Master数据
- **其他Hooks**: File tracker, Database validator等
  - 结论：都不直接涉及状态显示
- **结论**: Claude Code hooks正常，不影响OpenCode的状态显示

### 4. OpenCode自身配置
**检查结果**: ✅ 已检查
- **配置文件**: `opencode.json`, `config/opencode.json`
  - 内容：仅基础配置，指向CLAUDE.md
- **插件版本**: `@opencode-ai/plugin@1.1.18`
  - 状态：之前有shell.js损坏问题，已修复
- **目录结构**: `.opencode/` 目录存在，包含修复脚本
- **结论**: OpenCode配置正常，无明显任务跟踪配置

### 5. 代码级状态显示逻辑
**检查结果**: ✅ 已搜索
- **搜索范围**: Python代码中的状态显示相关代码
- **搜索关键词**: "completed.*remaining", "Status.*completed"等
- **结果**: 找到多处进度显示代码，但都不是"0/1"格式
- **结论**: 没有找到直接生成"0/1 completed, 1 remaining"的代码

### 6. 环境变量和配置
**检查结果**: ✅ 已检查
- **Claude环境变量**: CLAUDE_ENV_FILE等
- **项目环境变量**: .env文件
- **OpenCode环境变量**: 无相关配置
- **结论**: 没有发现控制TODO显示的环境变量

## 排除的假设

### ❌ OpenCode读取Task Master数据
- **理由**: Task Master显示16/142，但OpenCode显示0/1
- **证据**: 数据不匹配

### ❌ OpenCode读取OpenSpec数据
- **理由**: OpenSpec有142个任务，大部分pending
- **证据**: 数据不匹配

### ❌ Claude Code控制显示
- **理由**: 用户明确说是"OpenCode itself"
- **证据**: 用户澄清

### ❌ 缓存或状态同步问题
- **理由**: 检查了相关文件和hooks，没有发现状态同步机制
- **证据**: 没有找到相关的同步代码

## 可能的其他原因（未验证）

### 🔍 OpenCode内部状态
- **假设**: OpenCode有自己的内部任务跟踪，与外部文件无关
- **验证方法**: 需要查看OpenCode源代码或文档
- **当前状态**: 未验证（需要访问OpenCode源码）

### 🔍 项目特定配置
- **假设**: 有未发现的配置文件控制OpenCode行为
- **验证方法**: 搜索所有可能的配置文件
- **当前状态**: 已搜索常见位置，未发现

### 🔍 插件或扩展冲突
- **假设**: 其他插件影响OpenCode的状态显示
- **验证方法**: 检查已安装插件和扩展
- **当前状态**: 未检查

## 下次继续工作的建议

### 1. 优先级最高的验证项
```bash
# 检查OpenCode是否使用特定的任务文件
find /opt/claude -name "*opencode*" -type f -exec grep -l "todo\|task\|status" {} \;

# 查看OpenCode进程状态
ps aux | grep opencode

# 检查OpenCode日志
find /opt/claude -name "*opencode*" -type f -name "*.log" -exec tail -50 {} \;
```

### 2. 向OpenCode社区求助
- 在GitHub Issues中询问状态显示机制
- 查看OpenCode文档中是否有任务跟踪说明
- 询问其他用户是否遇到类似问题

### 3. 本地调试OpenCode
```bash
# 如果可能的话，运行OpenCode的调试模式
opencode --debug --verbose

# 查看OpenCode的配置文件位置
opencode --config-path
```

### 4. 替代解决方案
如果找不到根本原因，可以考虑：
- 重置OpenCode配置
- 重新安装OpenCode插件
- 使用其他方式显示项目状态

## 技术债务记录

### 已修复的技术债务
1. ✅ OpenCode shell.js损坏问题
2. ✅ TypeScript类型导出问题
3. ✅ OpenSpec文件权限问题
4. ✅ Web前端功能验证

### 待解决的技术债务
1. 🔍 TODO状态显示问题 (0/1 vs 16/142)
2. 📋 需要整理的文档和经验总结

## 经验教训

1. **问题隔离**: 明确区分不同系统的职责（Task Master vs OpenSpec vs OpenCode）
2. **系统边界**: 理解各工具的职责范围，避免在错误的地方找问题
3. **文档记录**: 及时记录调查过程，避免重复工作
4. **用户澄清**: 及时向用户确认问题细节，避免误解

## 调查总结

经过2小时的深入调查，我们排除了最可能的原因：
- Task Master数据正确
- OpenSpec数据不匹配
- Claude Code hooks不相关
- OpenCode配置正常

问题很可能在于OpenCode的内部机制或未发现的配置。建议下次调查时优先查看OpenCode源代码或向社区求助。

---

**调查人员**: Claude Code Assistant
**报告日期**: 2026-01-17
**状态**: 暂停调查，等待进一步信息
**优先级**: 中等（不影响核心功能）</content>
<parameter name="filePath">docs/reports/TODO_STATUS_INVESTIGATION_REPORT.md