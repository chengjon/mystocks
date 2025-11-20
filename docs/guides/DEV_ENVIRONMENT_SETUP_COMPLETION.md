# MyStocks 开发环境配置完成报告

## 任务概述

根据用户需求，已完成 MyStocks 项目开发环境的三个核心组件配置：

1. ✅ **tmux 会话布局脚本** (start-dev.sh)
2. ✅ **PM2 生态系统配置** (ecosystem.config.js)
3. ✅ **lnav 日志格式配置** (config/lnav_formats.json + setup_lnav.sh)

---

## 1. tmux 会话布局脚本 - start-dev.sh

### 功能特性

- **4窗格布局**: 后端、前端、数据库、日志监控
- **自动化启动**: 一键启动所有开发服务
- **依赖检查**: 自动检查 Python、Node.js、npm、tmux
- **错误处理**: 完善的错误处理和彩色输出
- **窗格标题**: 清晰标识每个窗格功能
- **快捷键支持**: 集成 tmux 快捷键提示

### 窗格布局

```
┌─────────────────────┬─────────────────────┐
│  窗格 0 (左上)       │  窗格 1 (右上)       │
│  后端服务           │  前端服务           │
│  FastAPI            │  Vue.js             │
│  端口: 8888         │  端口: 5173         │
├─────────────────────┼─────────────────────┤
│  窗格 2 (左下)       │  窗格 3 (右下)       │
│  数据库客户端       │  日志监控           │
│  PostgreSQL         │  lnav              │
│  交互式查询         │  格式化日志显示     │
└─────────────────────┴─────────────────────┘
```

### 使用方法

```bash
# 启动完整开发环境
./start-dev.sh

# 仅检查依赖
./start-dev.sh --check

# 启用调试模式
./start-dev.sh --debug

# 查看帮助
./start-dev.sh --help
```

### 集成功能

- 自动创建日志目录
- 后端服务自动重载 (--reload)
- 前端热更新 (npm run dev)
- 数据库连接信息显示
- **lnav 集成**: 自动使用自定义日志格式监控

---

## 2. PM2 生态系统配置 - ecosystem.config.js

### 配置特性

- **自动重启**: 服务崩溃时自动重启 (max_restarts: 10)
- **延迟重启**: 避免频繁重启 (restart_delay: 4000ms)
- **日志管理**: 统一日志输出到 logs/backend.log
- **健康检查**: 服务状态监控
- **环境配置**: 生产/开发环境分离

### 服务配置

```javascript
// 后端服务 (MyStocks FastAPI)
{
  name: 'mystocks-backend',
  script: 'uvicorn',
  args: 'app.main:app --host 0.0.0.0 --port 8888 --reload --log-level info',
  log_file: './logs/backend-combined.log',
  max_restarts: 10,
  restart_delay: 4000,
  env: {
    POSTGRESQL_HOST: 'localhost',
    POSTGRESQL_DATABASE: 'mystocks'
  }
}

// 数据收集服务 (可选)
{
  name: 'data-collector',
  script: 'python',
  args: 'src/monitoring/real_time_market_saver.py',
  cwd: '/opt/claude/mystocks_spec'
}

// GPU API 服务 (可选)
{
  name: 'gpu-api',
  script: 'src/gpu/api_system/main_server.py',
  cwd: '/opt/claude/mystocks_spec'
}
```

### 使用方法

```bash
# 启动服务
pm2 start ecosystem.config.js

# 重启服务
pm2 restart mystocks-backend

# 查看状态
pm2 status

# 查看日志
pm2 logs mystocks-backend

# 停止服务
pm2 stop mystocks-backend

# 删除服务
pm2 delete mystocks-backend
```

---

## 3. lnav 日志格式配置

### 配置文件

- **格式定义**: `config/lnav_formats.json`
- **安装脚本**: `scripts/setup_lnav.sh`
- **自动配置**: start-dev.sh 自动集成

### 日志格式识别

**支持格式**:
```
2025-11-16 10:00:00 [INFO] request_id=abc123 duration=200ms path=/api/strategy status=200
2025-11-16 10:00:01 [WARNING] request_id=def456 duration=500ms path=/api/data error_timeout
2025-11-16 10:00:02 [ERROR] request_id=ghi789 duration=1000ms path=/api/market error_db_connection
```

**自动解析字段**:
- `timestamp`: 时间戳 (`2025-11-16 10:00:00`)
- `level`: 日志级别 (`[INFO]`, `[WARNING]`, `[ERROR]`, `[DEBUG]`)
- `request_id`: 请求ID (`request_id=abc123`)
- `duration`: 响应时间 (`duration=200ms`)
- `path`: API路径 (`path=/api/strategy`)
- `status`: 响应状态 (`status=200`)
- `error`: 错误信息 (`error=timeout`)
- `action`: 操作类型 (`action=login_success`)

### 高级功能

- **时间轴视图**: 完整时间轴展示
- **搜索过滤**: 支持关键词搜索
- **错误高亮**: 自动高亮错误和警告
- **交互式过滤**: 支持字段过滤
- **格式化显示**: 清晰的字段对齐

### 使用方法

```bash
# 安装配置
./scripts/setup_lnav.sh

# 开发环境监控
./scripts/setup_lnav.sh dev

# 监控指定文件
./scripts/setup_lnav.sh start /path/to/log.log

# 测试配置
./scripts/setup_lnav.sh test
```

### lnav 快捷键

- `:q` - 退出 lnav
- `:c` - 清除高亮
- `/关键词` - 搜索
- `Tab` - 切换视图
- `Ctrl+r` - 刷新
- `:filter-out` - 排除过滤

---

## 集成验证

### 测试状态

1. **start-dev.sh**: ✅ 创建完成，权限设置正确
2. **ecosystem.config.js**: ✅ PM2 配置已就绪
3. **lnav 配置**: ✅ 格式配置已测试，示例日志已创建

### 文件清单

```
/opt/claude/mystocks_spec/
├── start-dev.sh                    # tmux 会话管理脚本
├── ecosystem.config.js             # PM2 生态系统配置
├── config/
│   └── lnav_formats.json           # lnav 日志格式定义
├── scripts/
│   └── setup_lnav.sh               # lnav 配置安装脚本
└── logs/
    ├── backend.log                 # 后端日志文件 (已创建)
    └── backend-combined.log        # PM2 日志文件 (已创建)
```

### 依赖要求

- **系统软件**: tmux, PM2, lnav
- **后端依赖**: Python 3.12+, FastAPI, uvicorn
- **前端依赖**: Node.js 16+, npm, Vue.js
- **数据库**: PostgreSQL, TDengine

### 安装依赖命令

```bash
# 系统依赖
sudo apt-get update
sudo apt-get install -y tmux lnav

# 安装 PM2
npm install -g pm2

# 后端依赖
cd web/backend
pip install -r requirements.txt

# 前端依赖
cd web/frontend
npm install
```

---

## 使用场景

### 场景 1: 完整开发环境启动

```bash
# 一键启动所有服务
./start-dev.sh
```

**结果**:
- 自动打开 tmux 4窗格会话
- 启动 FastAPI 后端 (端口 8888)
- 启动 Vue.js 前端 (端口 5173)
- 连接 PostgreSQL 数据库
- 使用 lnav 监控后端日志

### 场景 2: PM2 生产部署

```bash
# 使用 PM2 管理服务
pm2 start ecosystem.config.js

# 服务状态监控
pm2 status
pm2 logs mystocks-backend

# 服务故障自动重启
pm2 restart mystocks-backend
```

**结果**:
- 后端服务自动重启
- 日志统一输出到 logs/backend.log
- 服务健康状态监控
- 故障自动恢复

### 场景 3: 日志分析调试

```bash
# 配置 lnav 日志格式
./scripts/setup_lnav.sh dev

# 或直接使用
lnav logs/backend.log
```

**结果**:
- 自动识别 MyStocks 日志格式
- 格式化显示各字段
- 支持搜索和过滤
- 错误自动高亮

---

## 故障排查

### 常见问题

1. **tmux 未安装**
   ```bash
   sudo apt-get install tmux
   ```

2. **PM2 未安装**
   ```bash
   npm install -g pm2
   ```

3. **lnav 未安装**
   ```bash
   sudo apt-get install lnav
   ```

4. **端口被占用**
   ```bash
   # 查看端口占用
   lsof -i :8888
   lsof -i :5173
   
   # 杀死进程
   kill -9 <PID>
   ```

5. **数据库连接失败**
   ```bash
   # 检查 PostgreSQL 状态
   sudo systemctl status postgresql
   
   # 检查配置文件
   cat config/.env.example
   ```

### 日志文件位置

- **后端日志**: `logs/backend.log`
- **PM2 日志**: `logs/backend-combined.log`
- **系统日志**: `/var/log/syslog`
- **错误日志**: `logs/error.log`

---

## 性能优化建议

### tmux 优化

- 调整窗格大小适应屏幕
- 启用鼠标支持 (`tmux set-option mouse on`)
- 自定义配色方案
- 设置快捷键别名

### PM2 优化

- 调整 `max_restarts` 根据业务需求
- 配置集群模式 (`instances: 'max'`)
- 设置内存限制 (`max_memory_restart: '1G'`)
- 启用监控插件 (`pm2 install pm2-server-monit`)

### lnav 优化

- 调整格式配置提高解析准确性
- 设置日志滚动策略
- 配置自动刷新间隔
- 自定义高亮规则

---

## 扩展功能

### 后续可扩展功能

1. **自动化测试**: 集成测试工具
2. **代码质量**: 集成 linting 和格式化
3. **部署脚本**: 自动化部署工具
4. **监控告警**: 服务监控和通知
5. **日志分析**: 更高级的日志分析工具

### 集成 CI/CD

```yaml
# .github/workflows/dev-environment.yml
name: Dev Environment
on: [push, pull_request]
jobs:
  setup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup environment
        run: |
          ./start-dev.sh --check
          ./scripts/setup_lnav.sh
```

---

## 总结

✅ **任务完成状态**: 100%

1. **tmux 会话布局脚本** - 功能完整，支持4窗格开发环境
2. **PM2 生态系统配置** - 生产就绪，自动重启和日志管理
3. **lnav 日志格式配置** - 智能解析，支持后端日志结构化显示

所有配置文件已就绪，开发环境可立即使用。用户可以通过 `./start-dev.sh` 一键启动完整的开发环境，享受现代化的开发体验。

---

*报告生成时间: 2025-11-16*  
*配置版本: v1.0*  
*兼容性: MyStocks 项目*