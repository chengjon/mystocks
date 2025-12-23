# MyStocks 生产环境信息手册

## 部署信息

### 服务器配置
- **服务器IP**: [待填写]
- **部署目录**: /opt/claude/mystocks_spec
- **部署时间**: 2025-11-17 18:10:00
- **版本**: v1.0.0-production

### 服务地址
- **前端访问地址**: http://localhost:3001
- **后端API地址**: http://localhost:8888
- **API文档地址**: http://localhost:8888/docs
- **API健康检查**: http://localhost:8888/api/health

### 端口使用情况
- **3000**: 可用（未占用）
- **3001**: 前端服务（已占用）
- **8888**: 后端API服务（已占用）
- **5432**: PostgreSQL（容器内）
- **6030**: TDengine（容器内，未启动）

## 数据库配置

### PostgreSQL
- **容器名称**: mystocks_postgres
- **端口**: 5432（容器内）
- **状态**: 运行正常（20小时运行时间）
- **管理命令**:
  ```bash
  # 查看数据库状态
  docker ps --filter "name=postgres"
  
  # 连接数据库
  docker exec -it mystocks_postgres psql -U postgres
  
  # 查看数据库日志
  docker logs mystocks_postgres
  ```

### TDengine
- **状态**: 未启动（网络超时）
- **建议**: 使用Mock数据模式作为临时方案

## 服务管理

### 启动命令
```bash
# 启动后端服务
cd /opt/claude/mystocks_spec/web/backend
export PYTHONPATH=/opt/claude/mystocks_spec/web/backend:$PYTHONPATH
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8888 &

# 启动前端服务
cd /opt/claude/mystocks_spec/web/frontend
npm run preview -- --port 3001 --host 0.0.0.0 &
```

### 停止命令
```bash
# 停止后端服务
pkill -f "uvicorn.*8888"

# 停止前端服务
pkill -f "npm.*preview"

# 停止所有相关进程
pkill -f "mystocks"
```

### 重启命令
```bash
# 完全重启
./scripts/automation/deploy.sh --rollback
./scripts/automation/deploy.sh
```

### 查看日志
```bash
# 后端日志
tail -f /opt/claude/mystocks_spec/logs/backend.log

# 前端日志
tail -f /opt/claude/mystocks_spec/logs/frontend.log

# PM2日志（如果使用）
pm2 logs
```

## 数据源配置

### Mock数据模式（当前使用）
- **环境变量**: USE_MOCK_DATA=true
- **优势**: 快速启动，无外部依赖
- **适用场景**: 开发测试、生产演示

### 真实数据模式
- **环境变量**: USE_MOCK_DATA=false
- **要求**: 需要TDengine数据库正常运行
- **适用场景**: 生产环境实际使用

## 性能监控

### 系统资源
```bash
# 查看内存使用
free -m

# 查看磁盘使用
df -h

# 查看CPU使用
top
```

### 服务状态
```bash
# 检查端口占用
lsof -Pi :8888 -sTCP:LISTEN
lsof -Pi :3001 -sTCP:LISTEN

# 检查进程状态
ps aux | grep uvicorn
ps aux | grep npm
```

### 健康检查
```bash
# API健康检查
curl http://localhost:8888/api/health

# 前端页面检查
curl -I http://localhost:3001/

# 数据库连接检查
docker exec mystocks_postgres pg_isready -U postgres
```

## 备份策略

### 配置文件备份
- **环境配置**: /opt/claude/mystocks_spec/.env.production
- **PM2配置**: /opt/claude/mystocks_spec/ecosystem.production.config.js
- **数据库配置**: /opt/claude/mystocks_spec/config/docker-compose*.yml

### 数据备份
```bash
# PostgreSQL备份
docker exec mystocks_postgres pg_dumpall > backup_$(date +%Y%m%d_%H%M%S).sql

# 配置文件备份
cp -r /opt/claude/mystocks_spec/config /opt/mystocks/config_backup_$(date +%Y%m%d)
```

## 故障排查

### 常见问题

1. **端口被占用**
   ```bash
   # 查找占用进程
   lsof -Pi :8888 -sTCP:LISTEN
   lsof -Pi :3001 -sTCP:LISTEN
   
   # 清理冲突进程
   pkill -f "uvicorn.*8888"
   pkill -f "serve.*300"
   ```

2. **数据库连接失败**
   ```bash
   # 检查数据库状态
   docker ps --filter "name=postgres"
   docker logs mystocks_postgres
   
   # 重启数据库
   docker restart mystocks_postgres
   ```

3. **前端页面无法访问**
   ```bash
   # 检查前端服务
   curl -I http://localhost:3001/
   
   # 检查前端日志
   tail -f /opt/claude/mystocks_spec/logs/frontend.log
   
   # 重启前端服务
   pkill -f "npm.*preview"
   cd /opt/claude/mystocks_spec/web/frontend && npm run preview -- --port 3001 --host 0.0.0.0 &
   ```

4. **API响应异常**
   ```bash
   # 检查后端日志
   tail -f /opt/claude/mystocks_spec/logs/backend.log
   
   # 检查进程状态
   ps aux | grep uvicorn
   
   # 重启后端服务
   pkill -f "uvicorn.*8888"
   cd /opt/claude/mystocks_spec/web/backend && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8888 &
   ```

## 维护日程

### 日常检查（每日）
- [ ] 检查服务状态
- [ ] 查看错误日志
- [ ] 监控资源使用

### 定期维护（每周）
- [ ] 清理过期日志
- [ ] 更新依赖包
- [ ] 备份配置文件

### 升级维护（每月）
- [ ] 性能优化
- [ ] 安全更新
- [ ] 功能升级

## 联系信息

- **技术支持**: [待填写]
- **运维负责**: [待填写]
- **紧急联系**: [待填写]

---

*最后更新: 2025-11-17 18:10*