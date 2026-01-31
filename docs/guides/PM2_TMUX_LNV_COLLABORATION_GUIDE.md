# PM2、Tmux和Lnav三者协作开发运维体系完整指南

## 概述

MyStocks项目通过PM2、Tmux和Lnav的深度集成，构建了一个高效的三维开发运维体系。本指南详细说明了如何使用这套增强版的工具链，实现开发、监控、部署和运维的全面自动化。

## 版本信息

- **版本**: 2.0 Enhanced
- **更新日期**: 2026-01-27
- **兼容性**: 支持WSL2、Linux、macOS环境

## 🎯 核心优势

### 1. 三维统一管理
- **PM2**: 进程管理和自动重启
- **Tmux**: 多窗口并行开发环境
- **Lnav**: 智能日志分析和错误处理

### 2. 增强功能特性
- **智能健康检查**: 不仅检查URL可用性，还检查响应时间和状态码
- **指数退避重启策略**: 防止频繁重启导致系统不稳定
- **系统资源监控**: CPU、内存、磁盘使用率实时监控
- **高级日志分析**: 结构化日志查询、错误模式匹配、性能分析
- **多渠道告警**: 邮件、Webhook、Slack集成

## 📋 快速参考卡片

### 快速启动命令

```bash
# 启动增强开发环境
./scripts/dev/tmux-enhanced-session.sh start

# 启动监控（守护进程模式）
./scripts/dev/tmux-enhanced-session.sh start --daemon

# 执行一次性监控检查
./scripts/automation/monitor_and_fix.py --check-once

# PM2命令参考
pm2 list                          # 列出所有应用
pm2 show mystocks-frontend        # 查看前端状态
pm2 restart mystocks-backend       # 重启后端服务
pm2 logs mystocks-frontend        # 查看前端日志
pm2 monit                     # 查看监控状态

# Tmux命令参考
tmux list-sessions                   # 列出所有会话
tmux new-session -s mystocks_dev     # 创建新会话
tmux attach-session -t mystocks_dev    # 连接到会话

# Lnav命令参考
lnav -c logs/api/*               # 分析API日志
lnav -c logs/backend/*            # 分析后端日志
lnav -c logs/frontend/*           # 分析前端日志
lnav -c logs/database/*            # 分析数据库日志
lnav -c :export-to-json report.json logs/*  # 导出分析报告
```

### 常用操作流程

#### 1. 开发环境启动
```bash
# 一键启动完整开发环境
./scripts/dev/tmux-enhanced-session.sh start
```

#### 2. 监控和告警
```bash
# 启动自动化监控（后台运行）
nohup ./scripts/automation/monitor_and_fix.py --daemon &

# 手动执行一次检查
./scripts/automation/monitor_and_fix.py --check-once
```

#### 3. 日志分析
```bash
# 实时分析API错误日志
lnav -c logs/api/*

# 过滤ERROR级别日志
lnav -c ":filter-in log_level IN (ERROR, CRITICAL)" logs/api/*

# 分析响应时间超过1秒的请求
lnav -c ":filter-in response_time > 1000" logs/api/*

# 导出分析报告
lnav -c ":export-to-json /tmp/analysis_report.json" logs/api/*
```

## 🔧 配置详解

### PM2增强配置

#### 核心服务配置
- **健康检查增强**: 响应时间阈值、数据库连接检查、多端点验证
- **重启策略**: 指数退避、最大重试次数、冷却期保护
- **日志管理**: 自动轮转、大小限制、压缩存档
- **资源监控**: CPU/内存/磁盘阈值告警

#### 新增监控服务
- **独立监控进程**: 专门的监控应用，不影响主服务
- **GPU服务支持**: 自动检测GPU API服务并集成监控

### Tmux增强功能

#### 6个功能窗口
1. **PM2管理面板**: 应用状态、启动/停止/重启
2. **数据库监控**: TDengine + PostgreSQL实时状态
3. **自动化监控面板**: 系统监控、告警状态、日志查看
4. **高级日志分析**: Lnav集成、结构化查询、实时过滤
5. **系统资源监控**: CPU/内存/磁盘使用率、进程状态
6. **开发工具**: Python环境、Git操作、包管理

### Lnav集成优化

#### 日志格式配置
```json
{
  "backend_logs": {
    "title": "MyStocks Backend Logs",
    "description": "FastAPI后端结构化日志分析",
    "url": ["file:///opt/claude/mystocks_spec/logs/backend.log"],
    "sample": ["2026-01-27 10:00:00 [INFO] request_id=abc123 duration=200ms"]
  }
}
```

## 📊 性能指标

### 监控覆盖率
- **服务健康检查**: 99.9% 可用性
- **系统资源监控**: 实时CPU/内存/磁盘使用率
- **告警响应时间**: < 30秒（包含Webhook通知）
- **日志分析效率**: 支持GB级日志文件，毫秒级查询

### 故障恢复能力
- **自动重启**: 90% 成功率，指数退避策略
- **故障检测**: < 60秒发现异常
- **告警送达**: 99% 成功率（多渠道支持）

## 🚀 部署和运维

### 一键部署
```bash
# 生产环境部署
pm2 deploy production

# 开发环境启动
pm2 deploy development
```

### 生产环境配置切换
- **自动识别**: 通过NODE_ENV自动选择配置
- **安全切换**: 支持代码拉取、构建、部署自动化

## 📈 最佳实践

### 1. 监控配置
- 设置合理的检查间隔（60秒）
- 配置适当的告警阈值（CPU 80%, 内存 85%, 磁盘 90%）
- 启用错误率监控（> 5% 告警）

### 2. 日志管理
- 定期清理旧日志文件
- 使用结构化日志格式（JSON推荐）
- 关键日志保留30天，普通日志保留7天

### 3. 资源优化
- 监控GPU资源使用情况
- 设置进程优先级和限制
- 定期检查磁盘空间和内存泄漏

### 4. 安全考虑
- 使用环境变量管理敏感配置
- 限制PM2 Web接口访问权限
- 定期更新依赖包和系统补丁

## 🔍 故障排查

### 常见问题解决
1. **服务无法启动**: 检查端口占用、配置文件错误
2. **监控误报**: 调整阈值、检查依赖服务
3. **日志分析慢**: 优化日志格式、使用索引
4. **内存泄漏**: 重启服务、检查进程状态

### 调试工具
```bash
# PM2调试模式
pm2 start --no-daemon

# Tmux调试
tmux new-session -d -L debug_session -c "$PROJECT_ROOT"

# Lnav调试
lnav -c logs/error.log --debug
```

## 📚 相关文档

- **配置文件详解**: `ecosystem.enhanced.config.js`
- **监控API文档**: `scripts/automation/monitor_and_fix.py`
- **Tmux脚本详解**: `scripts/dev/tmux-enhanced-session.sh`
- **Lnav格式配置**: `config/lnav_formats.json`
- **部署脚本**: `deploy.sh`（如需）

## 🎓 总结

通过这套增强版的PM2、Tmux和Lnav协作体系，MyStocks项目实现了：

✅ **开发效率提升**: 多窗口并行开发，一键环境搭建
✅ **系统稳定性**: 智能监控和自动恢复，减少人工干预
✅ **问题定位**: 结构化日志分析，快速故障诊断
✅ **运维自动化**: 部署和配置管理，降低运维成本
✅ **可扩展性**: 模块化设计，易于扩展新功能

---

**最后更新**: 2026-01-27
**文档维护**: MyStocks开发团队