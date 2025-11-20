# MyStocks 5窗格TMUX开发工具链整合方案

## 📋 概述

MyStocks 5窗格TMUX开发工具链是一个完整的开发环境解决方案，集成了TMUX多窗格布局、PM2进程管理、lnav日志分析和环境差异化配置，为量化交易系统开发提供高效的一体化开发体验。

## 🏗️ 核心架构

### 1. 系统组件

| 组件 | 功能 | 配置位置 |
|------|------|----------|
| **TMUX 5窗格布局** | 多终端会话管理 | `scripts/dev/start-dev.sh` |
| **PM2 进程管理** | 服务自动重启和监控 | `ecosystem.config.js` |
| **lnav 日志分析** | 高级日志解析和SQL查询 | `config/lnav/` |
| **环境差异化** | 开发/生产配置分离 | `scripts/dev/start-dev.sh` |

### 2. 5窗格布局设计

```
┌─────────────┬─────────────┐
│   窗格 0    │   窗格 1    │  ← 后端服务 + 前端服务
│  后端服务   │  前端服务   │     (PM2管理 + Vue.js)
│ (PM2管理)   │(Vue.js dev) │
├─────────────┼─────────────┤
│   窗格 3    │   窗格 4    │  ← 数据库客户端 + 日志中心
│  数据库客户端│  日志中心   │     (psql/taos + lnav)
│ (psql/taos) │  (lnav)    │
└─────────────┴─────────────┘
```

## 🚀 快速开始

### 1. 一键启动开发环境

```bash
# 启动完整开发环境 (包含5窗格TMUX + PM2 + lnav)
./scripts/dev/start-dev.sh

# 指定环境启动
./scripts/dev/start-dev.sh development  # 开发环境
./scripts/dev/start-dev.sh production   # 生产环境

# 清理现有会话后启动
./scripts/dev/start-dev.sh --clean
```

### 2. lnav配置管理

```bash
# 安装开发环境lnav配置 (包含调试字段)
./scripts/dev/setup_lnav.sh development

# 安装生产环境lnav配置 (精简字段)
./scripts/dev/setup_lnav.sh production

# 仅验证配置
./scripts/dev/setup_lnav.sh --validate

# 显示使用指南
./scripts/dev/setup_lnav.sh --guide
```

## 📊 组件详解

### 1. TMUX 5窗格会话 (`scripts/dev/start-dev.sh`)

**功能特性：**
- ✅ 5窗格自动化布局 (2x3网格)
- ✅ 依赖检查和自动安装提示
- ✅ PM2集成管理和自动重启
- ✅ lnav日志格式自动配置
- ✅ 环境差异化配置 (开发/生产)
- ✅ 彩色交互界面和进度指示
- ✅ 一键跳转到指定窗格

**使用方法：**
```bash
# 基本启动
./scripts/dev/start-dev.sh

# 高级选项
./scripts/dev/start-dev.sh --check        # 仅检查依赖
./scripts/dev/start-dev.sh --debug        # 启用调试模式
./scripts/dev/start-dev.sh --clean        # 清理后启动
```

**窗格布局：**
- **窗格 0**: 后端服务 (PM2管理，自动重启)
- **窗格 1**: 前端服务 (Vue.js dev server)
- **窗格 2**: 监控面板 (系统状态和资源监控)
- **窗格 3**: 数据库客户端 (PostgreSQL + TDengine)
- **窗格 4**: 日志中心 (lnav + 自定义格式)

### 2. PM2进程管理 (`ecosystem.config.js`)

**服务列表：**
```javascript
{
  // MyStocks 后端API服务
  "mystocks-backend": {
    "script": "uvicorn",
    "args": "app.main:app --host 0.0.0.0 --port 8888 --reload --log-level info",
    "instances": 1,
    "max_restarts": 10,
    "max_memory_restart": "1G"
  },
  
  // 数据采集服务
  "mystocks-data-collector": {
    "script": "python",
    "args": "-m src.scripts.data_collector",
    "max_memory_restart": "512M"
  },
  
  // GPU API服务 (可选)
  "mystocks-gpu-api": {
    "script": "python",
    "args": "-m src.gpu.api_system.main_server",
    "max_memory_restart": "2G",
    "env": {
      "CUDA_VISIBLE_DEVICES": "0"
    }
  }
}
```

**环境配置：**
```bash
# 启动开发环境
pm2 start ecosystem.config.js --env development

# 启动生产环境
pm2 start ecosystem.config.js --env production

# 常用命令
pm2 status                    # 查看服务状态
pm2 logs mystocks-backend     # 查看后端日志
pm2 restart mystocks-backend  # 重启后端服务
pm2 monit                     # 启动监控面板
```

### 3. lnav日志分析 (`config/lnav/`)

**配置差异：**

| 功能 | 开发环境 | 生产环境 |
|------|----------|----------|
| **日志字段** | 完整调试信息 | 精简性能字段 |
| **查询模板** | SQL查询 + 调试分析 | 性能监控 + 错误统计 |
| **字段着色** | 完整状态映射 | 核心状态映射 |
| **查询深度** | 历史数据分析 | 实时性能监控 |

**支持日志格式：**
```json
{
  "mystocks_backend_logs": {
    "fields": ["timestamp", "level", "request_id", "duration", "path", "status", "error"],
    "coloring": {
      "level": {"ERROR": "red", "WARNING": "yellow", "INFO": "blue"},
      "status": {"2xx": "green", "4xx": "orange", "5xx": "red"},
      "duration": {"0-100": "green", "500+": "red"}
    }
  }
}
```

**常用命令：**
```bash
# 启动lnav
lnav logs/backend.log

# 过滤错误日志
:filter-in ERROR

# SQL查询分析
:sql-query SELECT path, AVG(duration) FROM log GROUP BY path

# 响应时间分布
:histogram -f duration

# 搜索特定request_id
:search /request_id=abc123
```

## 🔄 协同工作流

### 1. 开发流程闭环

```
1. 前端开发 → 窗格1 (Vue.js)
   ↓ 编译错误 → 窗格4 (lnav)
2. 后端开发 → 窗格0 (PM2)
   ↓ API调试 → 窗格4 (lnav)
3. 数据库调试 → 窗格3 (psql/taos)
   ↓ 性能分析 → 窗格4 (lnav)
```

### 2. 问题排查流程

```bash
# 场景: 前端报错查找对应后端日志
# 步骤:
1. 在窗格1看到前端错误
2. 记录request_id (如: abc123)
3. 在窗格4执行: :filter-in abc123
4. 分析完整请求链路

# 场景: 服务崩溃自动重启
# 步骤:
1. PM2检测到服务崩溃
2. 自动重启服务 (窗格0)
3. 记录重启日志 (窗格4)
4. 发送告警到终端 (窗格2)
```

### 3. 性能分析流程

```bash
# 场景: 接口响应慢分析
# 步骤:
1. 在窗格4使用: :sql-query SELECT path, AVG(duration) FROM log WHERE duration > 1000
2. 识别慢接口
3. 在窗格0重启特定服务
4. 窗格4监控性能改善
```

## ⚙️ 配置定制

### 1. 环境变量配置

```bash
# 开发环境
export PM2_ENV=development
export NODE_ENV=development
export LOG_LEVEL=debug

# 生产环境
export PM2_ENV=production
export NODE_ENV=production
export LOG_LEVEL=info
```

### 2. TMUX快捷键

```bash
# 窗格操作
Ctrl+b d           # 分离会话
Ctrl+b ↑↓←→        # 切换窗格
Ctrl+b z           # 切换全屏
Ctrl+b [           # 进入复制模式
Ctrl+b q           # 显示窗格编号

# 窗口操作
Ctrl+b c           # 创建新窗口
Ctrl+b n           # 下一个窗口
Ctrl+b p           # 上一个窗口
Ctrl+b &           # 关闭窗口
```

### 3. PM2环境配置

```javascript
// development环境
{
  "watch": true,           // 文件变更自动重启
  "restart_delay": 4000,   // 重启延迟
  "log_level": "debug"     // 调试日志
}

// production环境
{
  "watch": false,          // 禁用文件监控
  "max_restarts": 10,      // 最大重启次数
  "log_level": "info",     // 信息日志
  "max_memory_restart": "1G" // 内存限制
}
```

## 📈 性能优化

### 1. 系统资源优化

```bash
# TMUX优化
export TMUX_TMPDIR="/dev/shm"  # 使用内存缓存
tmux set-option history-limit 50000

# PM2优化
pm2 start ecosystem.config.js --max-memory-restart 1G

# lnav优化
lnav --config-file ~/.config/lnav/formats.json logs/*.log
```

### 2. 日志轮转配置

```javascript
// ecosystem.config.js
{
  "log_file": "./logs/backend-combined.log",
  "out_file": "./logs/backend-out.log",
  "error_file": "./logs/backend-error.log",
  "log_date_format": "YYYY-MM-DD HH:mm:ss Z",
  "merge_logs": true,
  "log_type": "json"
}
```

### 3. 数据库连接优化

```bash
# PostgreSQL连接池
psql -h localhost -U postgres -d mystocks -c "SHOW max_connections;"

# TDengine连接配置
taos -h localhost -P 6030 -d market_data
```

## 🛠️ 故障排除

### 1. 常见问题

**TMUX会话无法创建：**
```bash
# 检查TMUX安装
tmux -V

# 清理损坏的会话
tmux kill-server
tmux new-session -s test
```

**PM2服务启动失败：**
```bash
# 检查PM2配置
pm2 start ecosystem.config.js --env development --dry-run

# 查看详细错误
pm2 logs mystocks-backend --lines 100
```

**lnav配置不生效：**
```bash
# 检查配置文件
ls -la ~/.config/lnav/

# 验证JSON格式
jq empty ~/.config/lnav/formats.json

# 重新安装配置
./scripts/dev/setup_lnav.sh development
```

### 2. 调试模式

```bash
# 启用完整调试
./scripts/dev/start-dev.sh --debug

# 手动启动各组件
tmux new-session -s debug
pm2 start ecosystem.config.js --env development --no-daemon
lnav -d logs/backend.log
```

## 📚 扩展开发

### 1. 添加新服务

```javascript
// 在ecosystem.config.js中添加
{
  "name": "mystocks-new-service",
  "script": "python",
  "args": "-m src.modules.new_service",
  "max_memory_restart": "512M",
  "env_development": {
    "NODE_ENV": "development",
    "PYTHONPATH": "/opt/claude/mystocks_spec"
  }
}
```

### 2. 自定义lnav格式

```json
// 在 ~/.config/lnav/formats.json 中添加
{
  "custom_service_logs": {
    "title": "Custom Service Logs",
    "regex": {
      "std": {
        "pattern": "^(?<timestamp>\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}) \\[(?<level>\\w+)\\] (?<message>.*)$"
      }
    }
  }
}
```

### 3. TMUX自定义布局

```bash
# 修改 scripts/dev/start-dev.sh 中的布局函数
create_5pane_session() {
  # 自定义窗格大小和位置
  tmux resize-pane -t "$SESSION_NAME":0.0 -x 150 -y 40
  
  # 添加更多窗格
  tmux split-window -t "$SESSION_NAME" -v
}
```

## 📊 监控指标

### 1. 系统健康指标

```bash
# 服务状态监控
pm2 list | grep -E "online|errored"

# 内存使用监控
pm2 monit

# 日志错误统计
grep -c "ERROR" logs/*.log

# 数据库连接状态
psql -h localhost -c "SELECT 1;" 2>/dev/null && echo "OK" || echo "FAIL"
```

### 2. 性能指标

```sql
-- lnav中的SQL查询示例
SELECT 
  path,
  AVG(duration) as avg_duration,
  COUNT(*) as request_count,
  MAX(duration) as max_duration
FROM log 
WHERE timestamp > datetime('now', '-1 hour')
GROUP BY path
ORDER BY avg_duration DESC
LIMIT 10;
```

## 🎯 最佳实践

### 1. 开发工作流

```bash
# 1. 启动完整环境
./scripts/dev/start-dev.sh development

# 2. 开发过程中
# - 窗格0: 监控后端服务状态
# - 窗格1: 前端开发
# - 窗格2: 监控系统资源
# - 窗格3: 数据库操作
# - 窗格4: 日志分析

# 3. 问题排查时
# - 使用窗格4的lnav进行日志分析
# - PM2服务重启 (窗格0)
# - 数据库查询调试 (窗格3)
```

### 2. 生产部署

```bash
# 1. 安装生产环境配置
./scripts/dev/start-dev.sh production

# 2. 启动生产服务
pm2 start ecosystem.config.js --env production

# 3. 配置监控
pm2 monit

# 4. 日志轮转
pm2 install pm2-logrotate
pm2 set pm2-logrotate:max_size 10M
pm2 set pm2-logrotate:retain 30
```

## 📞 支持与贡献

### 1. 问题反馈

```bash
# 查看系统状态
./scripts/dev/start-dev.sh --check

# 生成诊断报告
echo "=== TMUX状态 ==="
tmux list-sessions
echo "=== PM2状态 ==="
pm2 list
echo "=== 服务端口 ==="
netstat -tlnp | grep -E "8888|5173"
```

### 2. 功能建议

- 通过GitHub Issues提交功能请求
- 通过Pull Request贡献代码
- 通过Issue报告bug和问题

### 3. 文档更新

```bash
# 更新文档
git add docs/DEV_TOOLCHAIN_GUIDE.md
git commit -m "docs: update development toolchain guide"
git push origin main
```

---

**版本**: v2.0  
**最后更新**: 2025-11-16  
**维护者**: MyStocks开发团队  
**文档地址**: `/opt/claude/mystocks_spec/docs/guides/DEV_TOOLCHAIN_GUIDE.md`