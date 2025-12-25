# MyStocks 项目 - Claude Code 插件完整列表

> 生成时间: 2025-12-25
> 总计插件数: 160+
> Marketplace数量: 9

---

## 📊 目录

- [Anthropic Agent Skills](#anthropic-agent-skills) - 17个技能
- [Claude Code Plugins](#claude-code-plugins) - 官方插件
- [Claude Code Workflows](#claude-code-workflows) - 工作流插件
- [Every Marketplace](#every-marketplace) - 综合插件
- [Superpowers Marketplace](#superpowers-marketplace) - 超级能力插件
- [ClaudeForge Marketplace](#claudeforge-marketplace) - 社区插件
- [CC Marketplace](#cc-marketplace) - 专业插件

---

## 🔵 Anthropic Agent Skills

**Marketplace**: `anthropic-agent-skills`
**说明**: Anthropic官方维护的通用技能集合

### 1. **frontend-design** - 前端设计
- **功能**: 创建独特、生产级的前端界面，避免通用AI美学
- **使用场景**: 构建Web组件、页面、工件、海报、仪表板、React组件
- **输出**: HTML/CSS/JS/React代码
- **关键特性**:
  - 独特的字体选择（避免Inter、Roboto）
  - 鲜明的配色方案和主题
  - 页面加载动画和微交互
  - 非对称布局和创意设计
  - 背景纹理和视觉效果

### 2. **web-artifacts-builder** - Web工件构建器
- **功能**: 创建复杂的多组件 claude.ai HTML 工件
- **使用场景**: 需要状态管理、路由或 shadcn/ui 组件的复杂React应用
- **输出**: bundle.html 单文件
- **技术栈**: React 18 + TypeScript + Vite + Tailwind CSS + shadcn/ui
- **关键特性**:
  - 40+ shadcn/ui 组件预装
  - Parcel 打包工具
  - 路径别名配置
  - 单HTML文件输出

### 3. **webapp-testing** - Web应用测试
- **功能**: 使用 Playwright 测试本地 Web 应用
- **使用场景**: 验证前端功能、调试UI行为、捕获截图、查看日志
- **输出**: Python测试脚本
- **关键特性**:
  - `with_server.py` 服务器生命周期管理
  - 支持**多服务器**（前端+后端）
  - **Reconnaissance-Then-Action** 模式
  - networkidle 等待策略

### 4. **docx** - Word文档处理
- **功能**: 创建、编辑和分析 .docx 文档
- **使用场景**: 专业文档创建、修订追踪、评论添加、格式保持
- **输出**: .docx 文件
- **关键特性**:
  - 支持修订追踪（tracked changes）
  - 评论管理
  - 格式保留
  - 文本提取

### 5. **pptx** - PowerPoint演示文稿
- **功能**: 创建、编辑和分析演示文稿
- **使用场景**: 演示文稿创建、内容修改、布局设计、备注添加
- **输出**: .pptx 文件
- **关键特性**:
  - 布局模板
  - 幻灯片组织
  - 评论和演讲者备注

### 6. **xlsx** - Excel电子表格
- **功能**: 创建、编辑和分析电子表格
- **使用场景**: 数据分析、公式计算、可视化、格式化
- **输出**: .xlsx/.xlsm/.csv/.tsv 文件
- **关键特性**:
  - 公式保留
  - 数据分析
  - 图表生成
  - 格式化样式

### 7. **pdf** - PDF文档处理
- **功能**: PDF 文本的提取、创建、合并、分割
- **使用场景**: 表单填写、批量处理、文档分析
- **输出**: PDF 文件
- **关键特性**:
  - 文本和表格提取
  - PDF合并/分割
  - 表单处理

### 8. **canvas-design** - 画布设计
- **功能**: 使用设计哲学创建精美的视觉艺术
- **使用场景**: 海报、艺术作品、设计、静态图像
- **输出**: .png 和 .pdf 文件
- **关键特性**:
  - 原创视觉设计
  - 避免版权侵权
  - 设计哲学应用

### 9. **algorithmic-art** - 算法艺术
- **功能**: 使用 p5.js 创建算法艺术
- **使用场景**: 代码艺术、生成艺术、流场、粒子系统
- **输出**: p5.js 代码
- **关键特性**:
  - 种子随机性
  - 交互式参数探索
  - 原创算法艺术

### 10. **theme-factory** - 主题工厂
- **功能**: 为工件应用主题样式
- **使用场景**: 幻灯片、文档、报告、HTML着陆页
- **输出**: 主题化的工件
- **关键特性**:
  - 10个预设主题
  - 自定义主题生成
  - 颜色和字体应用

### 11. **skill-creator** - 技能创建器
- **功能**: 创建有效技能的指南
- **使用场景**: 创建新技能、更新现有技能、扩展Claude能力
- **输出**: SKILL.md 文件
- **关键特性**:
  - 专业知识整合
  - 工作流集成
  - 技能结构指导

### 12. **mcp-builder** - MCP构建器
- **功能**: 创建高质量的MCP（Model Context Protocol）服务器
- **使用场景**: 集成外部API或服务到LLM
- **输出**: MCP服务器代码（Python/Node.js）
- **关键特性**:
  - FastMCP (Python)
  - MCP SDK (Node/TypeScript)
  - 外部服务集成
  - 工具设计指南

### 13. **doc-coauthoring** - 文档协作
- **功能**: 引导结构化文档协作工作流
- **使用场景**: 文档编写、提案、技术规范、决策文档
- **输出**: 结构化文档
- **关键特性**:
  - 上下文转移
  - 迭代优化
  - 读者验证

### 14. **brand-guidelines** - 品牌指南
- **功能**: 应用Anthropic官方品牌颜色和字体
- **使用场景**: 需要Anthropic视觉风格的工件
- **输出**: 品牌化工件
- **关键特性**:
  - 官方颜色方案
  - 字体排印
  - 视觉格式

### 15. **slack-gif-creator** - Slack GIF创建器
- **功能**: 为Slack创建优化的动画GIF
- **使用场景**: "为Slack创建X做Y的GIF"
- **输出**: GIF 文件
- **关键特性**:
  - 尺寸约束验证
  - 动画概念
  - Slack优化

### 16. **internal-comms** - 内部沟通
- **功能**: 撰写各类内部沟通文档
- **使用场景**: 状态报告、领导层更新、公司通讯、FAQ、事故报告、项目更新
- **输出**: 公司标准格式的文档
- **关键特性**:
  - 多种格式支持
  - 公司标准模板

### 17. **template** - 模板
- **功能**: 技能模板（占位符）

---

## 🔵 Claude Code Plugins

**Marketplace**: `claude-code-plugins`
**说明**: Claude Code 官方插件集合

### 1. **frontend-design** - 前端设计
- 同 anthropic-agent-skills 版本

### 2. **plugin-dev** - 插件开发套件
包含多个子技能：

#### 2.1 **MCP Integration** - MCP集成
- **功能**: 集成MCP服务器到插件
- **使用场景**: 添加MCP服务器、配置.mcp.json、连接外部服务
- **输出**: MCP集成代码
- **关键特性**:
  - SSE、stdio、HTTP、WebSocket支持
  - 外部工具集成
  - 服务配置指南

#### 2.2 **Agent Development** - Agent开发
- **功能**: 创建子agent
- **使用场景**: 创建agent、添加agent、编写subagent
- **输出**: Agent定义
- **关键特性**:
  - Agent结构
  - 系统提示词
  - 触发条件
  - 最佳实践

#### 2.3 **Hook Development** - Hook开发
- **功能**: 创建事件驱动的自动化
- **使用场景**: 创建hook、验证工具使用、阻止危险命令
- **输出**: Hook代码
- **关键特性**:
  - PreToolUse/PostToolUse/Stop hooks
  - 基于提示的hooks API
  - 事件驱动自动化

#### 2.4 **Plugin Structure** - 插件结构
- **功能**: 理解和组织插件组件
- **使用场景**: 创建插件、脚手架插件、配置plugin.json
- **输出**: 插件目录结构
- **关键特性**:
  - 目录布局
  - 清单配置
  - 组件组织
  - 文件命名约定

#### 2.5 **Plugin Settings** - 插件设置
- **功能**: 存储插件配置
- **使用场景**: 用户可配置的插件、.local.md文件
- **输出**: 配置文件
- **关键特性**:
  - YAML frontmatter
  - 每项目设置
  - 状态管理

#### 2.6 **Skill Development** - 技能开发
- **功能**: 创建技能
- **使用场景**: 添加技能、编写新技能、改进技能描述
- **输出**: SKILL.md 文件
- **关键特性**:
  - 技能结构
  - 渐进式披露
  - 最佳实践

#### 2.7 **Command Development** - 命令开发
- **功能**: 创建斜杠命令
- **使用场景**: 创建自定义命令、定义参数、交互式命令
- **输出**: 命令定义
- **关键特性**:
  - YAML frontmatter
  - 动态参数
  - 用户交互
  - Bash执行

### 3. **hookify** - Hook规则
#### 3.1 **writing-rules** - 编写Hookify规则
- **功能**: 创建hookify规则
- **使用场景**: 配置hookify、添加规则
- **输出**: Hookify规则

### 4. **claude-opus-4-5-migration** - Opus 4.5迁移
- **功能**: 从Sonnet 4.0/4.5或Opus 4.1迁移到Opus 4.5
- **使用场景**: 更新代码库、提示词、API调用
- **输出**: 迁移后的代码和提示词
- **关键特性**:
  - 模型字符串更新
  - 提示词调整
  - 行为差异处理

### 5. **commit-commands** - 提交命令
- **功能**: Git提交相关的命令
- **使用场景**: Git提交工作流

### 6. **ralph-wiggum** - Ralph Wiggum
- **功能**: 测试循环工具
- **使用场景**: 测试和验证

### 7. **pr-review-toolkit** - PR审查工具包
- **功能**: Pull request审查工具
- **使用场景**: 代码审查

### 8. **learning-output-style** - 学习输出风格
- **功能**: 调整输出风格用于学习

### 9. **feature-dev** - 功能开发
- **功能**: 功能开发引导
- **使用场景**: 新功能开发

### 10. **code-review** - 代码审查
- **功能**: 代码审查工具
- **使用场景**: 代码质量检查

### 11. **agent-sdk-dev** - Agent SDK开发
- **功能**: Agent SDK开发工具
- **使用场景**: 开发Claude Agent SDK

### 12. **explanatory-output-style** - 解释性输出风格
- **功能**: 解释性输出风格调整

---

## 🔵 Claude Code Workflows

**Marketplace**: `claude-code-workflows`
**说明**: Claude Code 工作流集合

### 1. **Kubernetes Operations** - K8s操作
#### 1.1 **gitops-workflow** - GitOps工作流
- **功能**: GitOps工作流指南
- **使用场景**: Kubernetes GitOps部署

#### 1.2 **helm-chart-scaffolding** - Helm图表脚手架
- **功能**: 创建Helm图表
- **使用场景**: Helm Chart开发

#### 1.3 **k8s-security-policies** - K8s安全策略
- **功能**: Kubernetes安全策略配置
- **使用场景**: 安全策略设置

#### 1.4 **k8s-manifest-generator** - K8s清单生成器
- **功能**: 生成Kubernetes清单
- **使用场景**: K8s资源配置

### 2. **Security Scanning** - 安全扫描
#### 2.1 **sast-configuration** - SAST配置
- **功能**: 静态应用安全测试配置
- **使用场景**: 安全扫描设置

### 3. **Cloud Infrastructure** - 云基础设施
#### 3.1 **cost-optimization** - 成本优化
- **功能**: 云成本优化策略
- **使用场景**: 降低云服务成本

#### 3.2 **terraform-module-library** - Terraform模块库
- **功能**: Terraform模块开发
- **使用场景**: 基础设施即代码

#### 3.3 **hybrid-cloud-networking** - 混合云网络
- **功能**: 混合云网络架构
- **使用场景**: 多云网络配置

#### 3.4 **multi-cloud-architecture** - 多云架构
- **功能**: 多云架构设计
- **使用场景**: 跨云部署策略

### 4. **LLM Application Dev** - LLM应用开发
#### 4.1 **rag-implementation** - RAG实现
- **功能**: 检索增强生成实现
- **使用场景**: 构建RAG应用

#### 4.2 **langchain-architecture** - LangChain架构
- **功能**: LangChain架构设计
- **使用场景**: LangChain应用开发

#### 4.3 **prompt-engineering-patterns** - 提示工程模式
- **功能**: 提示工程最佳实践
- **使用场景**: 优化提示词

#### 4.4 **llm-evaluation** - LLM评估
- **功能**: LLM性能评估
- **使用场景**: 模型评估和测试

### 5. **Shell Scripting** - Shell脚本
#### 5.1 **bats-testing-patterns** - BATS测试模式
- **功能**: Bash自动化测试
- **使用场景**: Shell脚本测试

#### 5.2 **bash-defensive-patterns** - Bash防御模式
- **功能**: 防御性Bash编程
- **使用场景**: 编写健壮的Shell脚本

#### 5.3 **shellcheck-configuration** - Shellcheck配置
- **功能**: Shell脚本静态分析
- **使用场景**: Shell代码质量检查

### 6. **Developer Essentials** - 开发者必备
#### 6.1 **e2e-testing-patterns** - E2E测试模式
- **功能**: 端到端测试策略
- **使用场景**: E2E测试设计

#### 6.2 **sql-optimization-patterns** - SQL优化模式
- **功能**: SQL查询优化
- **使用场景**: 数据库性能调优

#### 6.3 **debugging-strategies** - 调试策略
- **功能**: 系统化调试方法
- **使用场景**: 问题诊断和调试

#### 6.4 **git-advanced-workflows** - Git高级工作流
- **功能**: 复杂Git工作流
- **使用场景**: 高级Git操作

---

## 🔵 Every Marketplace

**Marketplace**: `every-marketplace`
**说明**: 综合插件集合

### **compound-engineering** - 复合工程
包含多个工程实践插件：
- **changelog**: 创建引人入胜的变更日志
- **create-agent-skill**: 创建Claude Code技能
- **deploy-docs**: 准备GitHub Pages部署文档
- **generate_command**: 创建自定义斜杠命令
- **heal-skill**: 修复错误的SKILL.md文件
- **plan_review**: 多个专业代理并行审查计划
- **release-docs**: 使用当前插件组件构建文档站点
- **report-bug**: 报告compound-engineering插件错误
- **reproduce-bug**: 使用日志和控制台检查重现bug
- **resolve_parallel**: 并行处理解析TODO注释
- **resolve_pr_parallel**: 并行处理解析PR评论
- **resolve_todo_parallel**: 并行处理解析TODO
- **triage**: 为CLI todo系统分类发现
- **workflows:compound**: 记录已解决问题的知识
- **workflows:plan**: 将功能描述转化为结构化项目计划
- **workflows:review**: 使用多代理分析进行详尽代码审查
- **workflows:work**: 高效执行工作计划

---

## 🔵 Superpowers Marketplace

**Marketplace**: `superpowers-marketplace`
**说明**: 超级能力插件集合

### 1. **brainstorm** - 头脑风暴
- **功能**: 使用苏格拉底方法进行交互式设计优化
- **使用场景**: 需要创意和设计优化的任务

### 2. **execute-plan** - 执行计划
- **功能**: 分批执行计划，带审查检查点
- **使用场景**: 执行复杂的实施计划

### 3. **write-plan** - 编写计划
- **功能**: 创建详细的实施计划和分解任务
- **使用场景**: 项目规划和任务分解

---

## 🔵 ClaudeForge Marketplace

**Marketplace**: `claudeforge-marketplace`
**说明**: 社区维护的插件集合

包含与claude-code-plugins和claude-plugins-official类似的插件集合。

---

## 🔵 CC Marketplace

**Marketplace**: `cc-marketplace`
**说明**: 专业插件集合

### 1. **math** - 数学
- **功能**: 数学计算和分析工具
- **使用场景**: 复杂数学运算

### 2. **experienced-engineer** - 经验工程师
- **功能**: 工程最佳实践指导
- **使用场景**: 代码架构和设计决策

### 3. **api-contract-sync-manager** - API契约同步管理器
- **功能**: API契约同步和管理
- **使用场景**: API版本控制和同步

#### 3.1 **api-contract-sync** - API契约同步
- **功能**: 同步API契约
- **使用场景**: 保持API文档和实现一致

### 4. **sugar** - Sugar
- **功能**: 语法糖和代码简化
- **使用场景**: 简化代码编写

---

## 📈 使用建议

### 按任务类型选择插件

| 任务类型 | 推荐插件 |
|---------|---------|
| **前端开发** | frontend-design, web-artifacts-builder |
| **文档处理** | docx, pptx, xlsx, pdf |
| **测试** | webapp-testing |
| **插件开发** | plugin-dev (全部子技能) |
| **基础设施** | Kubernetes Operations, Cloud Infrastructure |
| **LLM开发** | RAG实现, LangChain架构 |
| **代码审查** | code-review, plan_review |
| **项目管理** | write-plan, execute-plan |

### 按经验水平选择

**初学者**:
- frontend-design (设计指导)
- plugin-dev (结构指南)
- doc-coauthoring (文档写作)

**中级开发者**:
- webapp-testing (应用测试)
- web-artifacts-builder (复杂工件)
- mcp-builder (MCP集成)

**高级开发者**:
- k8s-manifest-generator (Kubernetes)
- rag-implementation (LLM应用)
- cost-optimization (云成本优化)

---

## 🔧 插件管理

### 启用/禁用插件
```bash
# 启用插件
/plugin

# 禁用插件
/plugin
```

### 查看已安装插件
```bash
ls /root/.claude/plugins/marketplaces/
```

### 更新插件
插件会自动从其GitHub仓库更新。

---

## 📚 相关文档

- [Claude Code 官方文档](https://docs.claude.com/en/docs/claude-code)
- [插件开发指南](https://github.com/anthropics/claude-code-plugins)
- [Agent SDK 文档](https://docs.anthropic.com/)

---

**文档生成**: 2025-12-25
**版本**: 1.0
**项目**: MyStocks Quantitative Trading System
