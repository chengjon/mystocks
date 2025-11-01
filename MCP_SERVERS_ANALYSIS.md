# MyStocks项目 - MCP服务器配置分析报告

生成时间: 2025-10-31

## 概述

本项目当前集成了4个MCP (Model Context Protocol) 服务器，提供浏览器自动化、文档查询、任务管理等功能。

---

## 已安装的MCP服务器详情

### 1. Context7 - 库文档查询服务

**功能描述**:
- 为任意编程库提供最新文档和代码示例
- 自动解析库名称到Context7兼容的库ID
- 支持按主题过滤文档内容

**可用工具** (2个):
- `mcp__context7__resolve-library-id`: 解析库名称获取标准库ID
- `mcp__context7__get-library-docs`: 获取库文档（支持token限制和主题筛选）

**典型应用场景**:
- 快速查询Python/JavaScript/其他语言的库API文档
- 获取最新版本的代码示例
- 在开发过程中即时查阅库使用方法

**安装方式**: 用户级别（通过Claude Desktop配置）

---

### 2. Playwright - 浏览器自动化框架

**功能描述**:
- 跨浏览器自动化测试工具（支持Chromium/Firefox/WebKit）
- 页面交互、表单填充、截图、网络监控
- 支持多标签页管理和文件上传

**可用工具** (18个):
- **浏览器控制**: navigate, navigate_back, close, resize
- **页面交互**: click, type, fill_form, press_key, select_option
- **元素操作**: drag, hover, file_upload
- **调试工具**: snapshot, take_screenshot, evaluate
- **监控**: console_messages, network_requests, handle_dialog
- **高级**: wait_for, browser_install, tabs

**典型应用场景**:
- Web应用自动化测试
- 数据爬取和页面监控
- 端到端测试流程自动化
- 适用于本项目的Web前端测试

**安装方式**: 用户级别（通过Claude Desktop配置）

---

### 3. Chrome DevTools - Chrome开发者工具协议

**功能描述**:
- 基于Chrome DevTools Protocol的深度浏览器控制
- 性能分析、网络节流、CPU模拟
- Core Web Vitals监控和性能追踪

**可用工具** (28个):
- **页面操作**: click, fill, fill_form, drag, hover, upload_file
- **页面管理**: navigate_page, new_page, close_page, select_page, list_pages
- **调试**: take_snapshot, take_screenshot, evaluate_script
- **网络**: list_network_requests, get_network_request, emulate_network
- **性能**: performance_start_trace, performance_stop_trace, performance_analyze_insight
- **监控**: list_console_messages, get_console_message
- **高级**: emulate_cpu, resize_page, wait_for, handle_dialog

**典型应用场景**:
- 深度性能分析和优化
- 网络请求监控和调试
- 移动端模拟测试
- 性能回归测试
- 适用于本项目前端性能优化

**安装方式**: 用户级别（通过Claude Desktop配置）

---

### 4. TaskMaster AI - AI驱动的敏捷任务管理系统

**功能描述**:
- AI增强的项目任务管理和TDD工作流自动化
- PRD文档解析和任务生成
- 复杂度分析和智能任务分解
- 多模型支持（OpenAI、Anthropic、Google Vertex、AWS Bedrock等）

**可用工具** (40+个，分类如下):

#### 项目初始化 (2个)
- `initialize_project`: 创建Task Master项目结构
- `rules`: 添加/删除规则配置文件

#### 任务管理核心 (15个)
- `get_tasks`: 获取任务列表（支持状态筛选）
- `get_task`: 获取任务详情
- `next_task`: 智能推荐下一个任务
- `add_task`: AI生成新任务
- `add_subtask`: 添加子任务
- `update`: 批量更新任务
- `update_task`: 更新单个任务
- `update_subtask`: 更新子任务
- `remove_task`: 删除任务
- `remove_subtask`: 删除子任务
- `set_task_status`: 设置任务状态
- `move_task`: 移动任务位置
- `generate`: 生成任务文件
- `clear_subtasks`: 清除子任务
- `parse_prd`: 从PRD文档生成任务

#### 智能分析 (4个)
- `analyze_project_complexity`: 复杂度分析
- `complexity_report`: 查看分析报告
- `expand_task`: 扩展任务为子任务
- `expand_all`: 批量扩展所有任务
- `scope_up_task`: 增加任务复杂度
- `scope_down_task`: 降低任务复杂度

#### 依赖管理 (4个)
- `add_dependency`: 添加任务依赖
- `remove_dependency`: 删除依赖
- `validate_dependencies`: 验证依赖关系
- `fix_dependencies`: 自动修复无效依赖

#### 标签系统 (7个)
- `list_tags`: 列出所有标签
- `add_tag`: 创建新标签
- `delete_tag`: 删除标签
- `use_tag`: 切换标签上下文
- `rename_tag`: 重命名标签
- `copy_tag`: 复制标签

#### TDD自动化工作流 (7个)
- `autopilot_start`: 启动TDD工作流
- `autopilot_resume`: 恢复工作流
- `autopilot_next`: 获取下一步操作
- `autopilot_status`: 查看工作流状态
- `autopilot_complete_phase`: 完成TDD阶段（RED/GREEN/COMMIT）
- `autopilot_commit`: 创建Git提交
- `autopilot_finalize`: 完成工作流
- `autopilot_abort`: 中止工作流

#### 研究与配置 (3个)
- `research`: AI增强的项目研究
- `models`: 模型配置管理
- `response-language`: 设置响应语言

**典型应用场景**:
- 敏捷开发任务规划和跟踪
- TDD工作流自动化
- 需求文档自动解析
- 项目复杂度评估
- 多分支任务管理
- **非常适合本项目的开发任务管理**

**安装方式**: 用户级别（通过Claude Desktop配置）

---

## 安装范围分析

### 当前安装级别: **用户级别**

**配置文件位置** (WSL环境下):
- Windows侧: `%APPDATA%\Claude\claude_desktop_config.json`
- 通常路径: `C:\Users\{username}\AppData\Roaming\Claude\claude_desktop_config.json`

**安装范围影响**:
- ✅ 当前Windows用户的所有Claude Code会话可用
- ❌ 其他Windows用户无法使用
- ❌ 非本机环境需要重新配置

---

## 典型配置文件结构

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@context7/mcp-server"]
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-playwright"]
    },
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "@executeautomation/chrome-devtools-mcp-server"]
    },
    "taskmaster-ai": {
      "command": "npx",
      "args": ["-y", "@taskmaster/mcp-server"],
      "env": {
        "ANTHROPIC_API_KEY": "sk-...",
        "OPENAI_API_KEY": "sk-..."
      }
    }
  }
}
```

---

## 推荐使用策略

### 针对MyStocks项目的MCP使用建议:

1. **TaskMaster AI** - 主要任务管理工具
   - 用于管理数据库优化任务
   - TDD工作流自动化（API开发）
   - 跟踪前后端开发进度

2. **Context7** - 技术文档查询
   - 查询TDengine API文档
   - PostgreSQL/TimescaleDB最新特性
   - FastAPI、React等框架文档

3. **Chrome DevTools** - 前端性能优化
   - 监控Web应用性能
   - 分析网络请求
   - Core Web Vitals评估

4. **Playwright** - E2E测试
   - 自动化前端测试流程
   - 数据可视化验证
   - 用户交互测试

---

## 配置文件访问方法

由于当前环境是WSL，要查看配置文件需要：

### 方法1: 通过WSL访问Windows文件
```bash
# 查找Windows用户名
ls /mnt/c/Users/

# 访问配置文件（替换{username}）
cat /mnt/c/Users/{username}/AppData/Roaming/Claude/claude_desktop_config.json
```

### 方法2: 在Windows PowerShell中
```powershell
Get-Content $env:APPDATA\Claude\claude_desktop_config.json | ConvertFrom-Json
```

### 方法3: 在Windows文件资源管理器中
```
%APPDATA%\Claude\claude_desktop_config.json
```

---

## 项目级MCP配置建议

如需在项目级别配置MCP（便于团队共享），可以考虑：

1. 在项目根目录创建 `.claude/mcp_config.json`
2. 在项目README中说明MCP依赖
3. 提供安装脚本自动配置MCP

示例项目级配置：
```json
{
  "recommended_mcps": [
    {
      "name": "taskmaster-ai",
      "purpose": "任务管理和TDD工作流",
      "required": true
    },
    {
      "name": "context7",
      "purpose": "技术文档查询",
      "required": false
    }
  ]
}
```

---

## 总结

当前MCP配置为**用户级安装**，提供了完整的开发工具链：
- 📋 任务管理: TaskMaster AI
- 📚 文档查询: Context7
- 🌐 浏览器控制: Playwright + Chrome DevTools

这些工具覆盖了MyStocks项目的主要开发需求，建议充分利用以提升开发效率。
