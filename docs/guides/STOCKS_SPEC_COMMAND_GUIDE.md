# stocks_spec 命令使用指南

## 概述

`stocks_spec` 是 MyStocks_spec 项目的服务管理工具，用于方便地启动、停止和管理前端和后端服务。

## 安装

脚本已自动配置为系统命令：
- 脚本位置: `/opt/claude/mystocks_spec/scripts/stocks_spec.sh`
- 系统链接: `/usr/local/bin/stocks_spec`

## 基本用法

```bash
stocks_spec [选项] [服务] [端口]
```

## 全栈服务管理

### 启动所有服务
```bash
stocks_spec -start
```
输出示例：
```
ℹ️  启动MyStocks_spec完整服务...

✅ 后端服务已启动
ℹ️    PID: 1234
ℹ️    端口: 8000
ℹ️    Swagger文档: http://localhost:8000/docs
ℹ️    ReDoc文档: http://localhost:8000/api/redoc
ℹ️    日志文件: /opt/claude/mystocks_spec/web/backend/backend.log

✅ 前端服务已启动
ℹ️    PID: 5678
ℹ️    端口: 3000
ℹ️    访问地址: http://localhost:3000
ℹ️    日志文件: /opt/claude/mystocks_spec/web/frontend/frontend.log

✅ MyStocks_spec服务已全部启动

📊 服务状态:
  后端: http://localhost:8000
  前端: http://localhost:3000
  Swagger文档: http://localhost:8000/docs
  ReDoc文档: http://localhost:8000/api/redoc
```

### 停止所有服务
```bash
stocks_spec -stop
```

### 重启所有服务
```bash
stocks_spec -restart
```

### 查看服务状态
```bash
stocks_spec -status
```

## 前端服务管理

### 启动前端（默认端口 3000）
```bash
stocks_spec -start front
```

### 启动前端（指定端口）
```bash
stocks_spec -start front 3005
```

### 停止前端
```bash
stocks_spec -stop front
```

### 重启前端
```bash
stocks_spec -restart front
```

## 后端服务管理

### 启动后端（默认端口 8000）
```bash
stocks_spec -start back
```

### 启动后端（指定端口）
```bash
stocks_spec -start back 8010
```

### 停止后端
```bash
stocks_spec -stop back
```

### 重启后端
```bash
stocks_spec -restart back
```

## API 文档访问

启动后端服务后，可以通过以下地址访问 API 文档：

### Swagger UI
- **主路径**: http://localhost:8000/docs
- **备用路径**: http://localhost:8000/api/docs
- 提供交互式 API 测试界面
- 支持直接在浏览器中测试 API 端点

### ReDoc
- **路径**: http://localhost:8000/api/redoc
- 提供更美观的 API 文档阅读界面
- 适合查看完整的 API 规范

### OpenAPI JSON
- **路径**: http://localhost:8000/openapi.json
- 提供原始的 OpenAPI 规范文件

## 端口配置

### 允许的端口范围
- **前端**: 3000-3009
- **后端**: 8000-8009

### 端口占用处理
脚本会自动检测端口占用：
- 如果默认端口被占用，会提示警告
- 可以通过指定端口参数使用其他端口
- 脚本包含自动查找可用端口的功能（在指定范围内）

## 日志文件

### 后端日志
```bash
/opt/claude/mystocks_spec/web/backend/backend.log
```

### 前端日志
```bash
/opt/claude/mystocks_spec/web/frontend/frontend.log
```

### 查看实时日志
```bash
# 后端日志
tail -f /opt/claude/mystocks_spec/web/backend/backend.log

# 前端日志
tail -f /opt/claude/mystocks_spec/web/frontend/frontend.log
```

## 常见使用场景

### 开发环境启动
```bash
# 启动完整开发环境
stocks_spec -start

# 访问前端应用
# http://localhost:3000

# 访问 API 文档
# http://localhost:8000/docs
```

### 仅启动后端进行 API 测试
```bash
stocks_spec -start back
# 访问 http://localhost:8000/docs 进行 API 测试
```

### 前端开发（连接到已运行的后端）
```bash
stocks_spec -start front
```

### 端口冲突解决
```bash
# 使用其他端口启动
stocks_spec -start front 3005
stocks_spec -start back 8010
```

### 快速重启服务
```bash
# 重启所有服务
stocks_spec -restart

# 仅重启后端
stocks_spec -restart back

# 仅重启前端
stocks_spec -restart front
```

## 故障排除

### 服务无法启动
1. 检查端口是否被占用：
   ```bash
   lsof -i :3000  # 检查前端端口
   lsof -i :8000  # 检查后端端口
   ```

2. 查看日志文件：
   ```bash
   tail -50 /opt/claude/mystocks_spec/web/backend/backend.log
   tail -50 /opt/claude/mystocks_spec/web/frontend/frontend.log
   ```

3. 手动清理进程：
   ```bash
   # 停止所有服务
   stocks_spec -stop

   # 如果仍有残留进程，手动终止
   pkill -f "uvicorn app.main:app"
   pkill -f "npm run dev"
   ```

### 无法访问 API 文档
1. 确认后端服务正在运行：
   ```bash
   stocks_spec -status
   ```

2. 尝试访问备用路径：
   - http://localhost:8000/docs （会重定向到 /api/docs）
   - http://localhost:8000/api/docs （Swagger UI）
   - http://localhost:8000/api/redoc （ReDoc）

3. 检查健康检查端点：
   ```bash
   curl http://localhost:8000/health
   ```

### 权限问题
确保脚本有执行权限：
```bash
chmod +x /opt/claude/mystocks_spec/scripts/stocks_spec.sh
```

## 技术细节

### 进程管理
- 使用 `nohup` 在后台运行服务
- 自动记录 PID 用于进程管理
- 支持优雅停止和强制终止

### 端口检测
- 使用 `lsof` 检测端口占用
- 支持端口范围内的自动查找
- 提供详细的端口使用信息

### 服务启动等待
- 自动等待服务启动（最多 30 秒）
- 实时检测端口监听状态
- 启动超时时提供明确的错误提示

## 更新日志

### v1.0 (2025-12-10)
- ✅ 初始版本发布
- ✅ 支持前端/后端独立和联合管理
- ✅ 支持自定义端口配置
- ✅ 添加双 API 文档路径支持（Swagger + ReDoc）
- ✅ 更新所有提示文本为 MyStocks_spec
- ✅ 修复 Windows 行尾符问题
- ✅ 配置为系统全局命令

## 相关文档

- [API 文档](http://localhost:8000/docs) - 启动后端后访问
- [WEB_PAGES_DOCUMENTATION.md](/opt/claude/mystocks_spec/docs/WEB_PAGES_DOCUMENTATION.md) - 前端页面文档
- [WEB_PAGES_API_MAPPING.md](/opt/claude/mystocks_spec/docs/api/WEB_PAGES_API_MAPPING.md) - API 映射文档
- [PORT_CONFIGURATION.md](/opt/claude/mystocks_spec/PORT_CONFIGURATION.md) - 端口配置说明

## 支持

如遇问题，请检查：
1. 日志文件输出
2. 端口占用情况
3. 服务运行状态
4. 相关文档说明
