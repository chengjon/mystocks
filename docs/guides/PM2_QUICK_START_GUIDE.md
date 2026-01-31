# PM2、Tmux和Lnav快速启动指南

## 🚀 一键启动开发环境

### 快速命令

```bash
# 启动完整开发环境（推荐）
./scripts/dev/tmux-enhanced-session.sh start

# 后台启动监控（可选）
nohup ./scripts/automation/monitor_and_fix.py --daemon &

# 执行一次性监控检查
./scripts/automation/monitor_and_fix.py --check-once
```

## 📋 功能窗口说明

当执行 `./scripts/dev/tmux-enhanced-session.sh start` 后，你将获得以下6个功能窗口：

### 🪟 Window 0: PM2应用管理
- **功能**: 显示所有应用状态、启动/停止/重启服务
- **快捷键**: 默认选中窗口
- **使用**: `pm2 list`, `pm2 show`, `pm2 restart`, `pm2 logs`

### 🪟 Window 1: 数据库监控
- **子窗口1**: TDengine数据库状态
  - 监控连接数、查询性能、存储使用情况
- **子窗口2**: PostgreSQL数据库状态
  - 监控连接数、事务处理、锁等待情况
- **快捷键**: `Ctrl+B` 切换到子窗口1, `Ctrl+O` 切换到子窗口2

### 🪟 Window 2: 自动化监控
- **主面板**: 显示监控状态、告警信息、系统资源
- **实时信息**: 服务状态、错误计数、资源使用率
- **快捷键**: `Ctrl+C` 返回主面板

### 🪟 Window 3: 高级日志分析（需lnav）
- **功能**: lnav集成的结构化日志分析
- **特性**: 实时错误高亮、性能图表、查询过滤
- **快捷键**: `Ctrl+T` 激活日志分析功能

### 🪟 Window 4: 系统资源监控
- **CPU监控**: 实时CPU使用率图表
- **内存监控**: 内存使用情况历史和趋势
- **磁盘监控**: 磁盘空间和I/O统计
- **快捷键**: `Ctrl+Shift+R` 刷新资源数据

### 🪟 Window 5: 开发工具
- **Python环境**: 预配置的Python路径和包
- **Git操作**: 状态查看、提交、推送
- **包管理**: 安装、更新、删除Python包
- **快捷键**: `Ctrl+Shift+D` 进入开发模式

## 🔧 基础操作

### Tmux命令
```bash
# 列出会话
tmux list-sessions

# 新建会话
tmux new-session -s session_name

# 连接到会话
tmux attach-session -t session_name

# 分割窗口
tmux split-window -h -t session_name

# 选择窗口
tmux select-window -t session_name
```

### PM2命令
```bash
# 列出应用
pm2 list

# 显示应用详情
pm2 show app_name

# 启动应用
pm2 start app_name

# 重启应用
pm2 restart app_name

# 停止应用
pm2 stop app_name

# 查看日志
pm2 logs app_name

# 监控模式
pm2 monit
```

### Lnav命令
```bash
# 分析日志
lnav logs/error.log

# 过滤错误日志
lnav -c ":filter-in log_level IN (ERROR, CRITICAL)" error.log

# 导出报告
lnav -c ":export-to-json report.json" error.log
```

## 🎯 环境要求

### 必需工具
- **Node.js**: v14+ (用于前端服务）
- **Python**: 3.8+ (用于后端和监控）
- **PM2**: 进程管理器
- **Tmux**: 终端复用器
- **Lnav**: 日志分析工具（可选）

### 可选工具
- **Docker**: 用于数据库容器管理
- **Git**: 版本控制
- **VS Code**: 代码编辑器（替代vim/nano）

## 📖 使用场景

### 场景1: 日常开发
```bash
./scripts/dev/tmux-enhanced-session.sh start
# 在Window 0中查看前端状态
# 在Window 1中监控数据库状态
# 在Window 5中开发新功能
```

### 场景2: 生产部署
```bash
# 切换到生产环境配置
NODE_ENV=production ./scripts/dev/tmux-enhanced-session.sh start

# 一键部署到生产服务器
pm2 deploy production
```

### 场景3: 故障排查
```bash
# 在Window 2中查看自动化监控状态
# 检查告警信息和系统资源
# 在Window 3中分析错误日志
```

## 💡 最佳实践

### 1. 监控策略
- 设置检查间隔为60秒，平衡实时性和系统负载
- CPU告警阈值设为80%，内存85%，磁盘90%
- 使用指数退避策略，防止频繁重启

### 2. 日志管理
- 定期清理30天前的日志文件
- 错误日志保留7天，普通日志保留30天
- 使用结构化JSON格式，便于自动化分析

### 3. 开发流程
- 优先在tmux中进行开发，减少环境切换
- 使用Git分支管理功能开发
- 定期提交代码，避免大量冲突

### 4. 安全考虑
- 生产环境使用HTTPS连接
- 敏感配置使用环境变量
- 定期更新依赖包和系统补丁

---

**快速上手**: 记住 `./scripts/dev/tmux-enhanced-session.sh start` 这一个命令就够了！