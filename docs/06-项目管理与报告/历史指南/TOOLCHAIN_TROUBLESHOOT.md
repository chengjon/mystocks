# MyStocks 工具链排障手册

## 目录
1. [常见问题及解决方案](#常见问题及解决方案)
2. [数据显示异常排障流程](#数据显示异常排障流程)
3. [服务状态检查](#服务状态检查)
4. [日志查看与分析](#日志查看与分析)
5. [本次踩坑记录](#本次踩坑记录)

## 常见问题及解决方案

### 前端页面无法访问
1. 检查前端服务是否启动：
   ```bash
   # 查看前端服务状态
   lsof -i :3001
   
   # 如果未启动，重新启动前端服务
   cd /opt/claude/mystocks_spec/web/frontend
   npm run dev
   ```

2. 检查网络连接：
   ```bash
   # 测试本地访问
   curl -I http://localhost:3001/
   ```

### 后端API无法访问
1. 检查后端服务状态：
   ```bash
   # 查看PM2服务状态
   pm2 status
   
   # 查看后端日志
   pm2 logs mystocks-backend
   
   # 重启后端服务
   pm2 restart mystocks-backend
   ```

2. 检查端口占用：
   ```bash
   # 检查8888端口
   lsof -i :8888
   ```

## 数据显示异常排障流程

### 1. 先查前端端口/API地址
检查前端环境变量配置：
```bash
# 查看前端环境变量文件
cat /opt/claude/mystocks_spec/web/frontend/.env
cat /opt/claude/mystocks_spec/web/frontend/.env.development

# 应确保VITE_API_BASE_URL=http://localhost:8888
```

检查Vite代理配置：
```bash
# 查看vite.config.js
cat /opt/claude/mystocks_spec/web/frontend/vite.config.js

# 应确保代理目标为http://localhost:8888
```

### 2. 再查服务状态
检查PM2服务状态：
```bash
pm2 status
```

查看后端日志：
```bash
pm2 logs mystocks-backend
```

### 3. 再查跨域问题
检查后端CORS配置：
```bash
# 查看后端main.py文件中的CORS配置
grep -A 20 "add_middleware" /opt/claude/mystocks_spec/web/backend/app/main.py
```

确保允许前端地址：
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001",  # Vite dev server
        # 其他允许的地址
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4. 最后查数据格式
使用curl调用API验证：
```bash
# 获取认证令牌
TOKEN=$(curl -s -X POST "http://localhost:8888/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | \
  python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))")

# 调用API验证返回格式
curl -X GET "http://localhost:8888/api/data/stocks/basic?limit=5" \
  -H "Authorization: Bearer $TOKEN"
```

期望返回格式：
```json
{
  "success": true,
  "data": [...],
  "total": 4,
  "timestamp": "2025-11-17T00:00:00.000000"
}
```

## 服务状态检查

### PM2服务状态
```bash
# 查看所有服务
pm2 status

# 查看详细信息
pm2 list

# 查看日志
pm2 logs

# 重启服务
pm2 restart mystocks-backend
```

### 端口检查
```bash
# 检查前端端口
lsof -i :3001

# 检查后端端口
lsof -i :8888

# 检查数据库端口
lsof -i :5432  # PostgreSQL
lsof -i :6030  # TDengine
```

## 日志查看与分析

### 前端日志
```bash
# 查看前端服务日志
cd /opt/claude/mystocks_spec/web/frontend
tail -f frontend.log
```

### 后端日志
```bash
# 查看PM2日志
pm2 logs mystocks-backend

# 查看详细日志文件
tail -f /opt/claude/mystocks_spec/web/backend/logs/backend.log
```

### 数据库日志
```bash
# PostgreSQL日志位置（根据实际配置）
tail -f /var/log/postgresql/postgresql-17-main.log

# TDengine日志位置（根据实际配置）
tail -f /var/log/taos/taosd.log
```

## 本次踩坑记录

### 1. 前端端口不一致问题
**问题描述**：前端服务实际运行在3001端口，而非预期的5173端口。
**解决方案**：
1. 查看前端服务启动日志确认实际端口：
   ```bash
   cd /opt/claude/mystocks_spec/web/frontend
   cat frontend.log
   ```
2. 更新前端代理配置中的端口引用。

### 2. 代理地址错误问题
**问题描述**：Vite配置中的API代理目标地址错误。
**解决方案**：
1. 检查并修正`/opt/claude/mystocks_spec/web/frontend/vite.config.js`中的代理配置：
   ```javascript
   proxy: {
     '/api': {
       target: 'http://localhost:8888', // 确保指向正确的后端端口
       changeOrigin: true
     }
   }
   ```

### 3. 环境变量配置错误
**问题描述**：前端环境变量文件中API基础URL配置错误。
**解决方案**：
1. 检查并修正`.env`和`.env.development`文件中的配置：
   ```bash
   VITE_API_BASE_URL=http://localhost:8888
   ```

### 4. 跨域问题
**问题描述**：前端请求后端API时出现跨域错误。
**解决方案**：
1. 确认后端CORS中间件配置允许前端地址：
   ```python
   allow_origins=[
       "http://localhost:3001",  # Vite dev server
   ]
   ```

### 5. 数据格式问题
**问题描述**：前端无法正确解析API返回的数据。
**解决方案**：
1. 确保后端API返回统一的响应格式：
   ```json
   {
     "success": true,
     "data": [...],
     "total": 4,
     "timestamp": "..."
   }
   ```
2. 在前端添加相应的数据校验和错误处理逻辑。