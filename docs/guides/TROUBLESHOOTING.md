# MyStocks 故障排查手册

## 目录

- [快速诊断](#快速诊断)
- [常见问题](#常见问题)
- [数据库问题](#数据库问题)
- [API 问题](#api-问题)
- [前端问题](#前端问题)
- [日志查看](#日志查看)
- [性能问题](#性能问题)

---

## 快速诊断

### 系统健康检查

```bash
# 检查后端服务
curl http://localhost:8000/health

# 检查前端服务
curl http://localhost:3000

# 检查数据库连接
python3 -c "from app.db import engine; engine.connect(); print('DB OK')"
```

### 预期响应

```json
{
  "status": "healthy",
  "timestamp": "2025-12-28T12:00:00Z",
  "services": {
    "database": "up",
    "cache": "up",
    "api": "up"
  }
}
```

---

## 常见问题

### Q1: 登录失败，用户名或密码错误

**症状**: 返回 `1001` 错误码

**排查步骤**:
1. 确认用户名是否正确
2. 确认密码是否正确（注意大小写）
3. 检查是否启用了大小写敏感设置
4. 确认账户是否被禁用

**解决方案**:
```bash
# 重置密码
python3 scripts/reset_password.py --username admin

# 检查账户状态
python3 scripts/check_user_status.py --username admin
```

---

### Q2: Token 过期

**症状**: 返回 `1002` 错误码

**排查步骤**:
1. 检查 Token 过期时间设置
2. 确认客户端是否实现了 Token 刷新逻辑

**解决方案**:
```bash
# 延长 Token 过期时间（.env 文件）
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=7200
```

---

### Q3: API 返回 503 Service Unavailable

**症状**: 返回 `9003` 错误码，服务维护中

**排查步骤**:
1. 检查是否有维护窗口计划
2. 查看系统状态页面
3. 检查最近是否进行了部署

**解决方案**:
- 等待维护完成
- 联系管理员确认维护计划

---

### Q4: 数据不更新

**症状**: K 线数据长时间不变

**排查步骤**:
1. 检查数据源配置
2. 确认定时任务是否运行
3. 检查网络连接

**解决方案**:
```bash
# 手动触发数据更新
python3 scripts/update_market_data.py --force

# 检查定时任务状态
python3 scripts/check_schedules.py
```

---

## 数据库问题

### PostgreSQL 连接失败

**错误信息**: `could not connect to server: Connection refused`

**排查步骤**:
```bash
# 检查 PostgreSQL 服务状态
sudo systemctl status postgresql

# 检查端口是否监听
netstat -tlnp | grep 5432

# 测试连接
psql -h localhost -U mystocks -d mystocks
```

**解决方案**:
```bash
# 启动 PostgreSQL
sudo systemctl start postgresql

# 重启 PostgreSQL
sudo systemctl restart postgresql

# 检查防火墙
sudo ufw allow 5432/tcp
```

### TDengine 连接失败

**错误信息**: `Unable to establish connection to TDengine`

**排查步骤**:
```bash
# 检查 TDengine 服务状态
systemctl status taosd

# 检查端口
netstat -tlnp | grep 6030

# 测试连接
taos -h localhost -P 6030 -u root -p taosdata
```

**解决方案**:
```bash
# 启动 TDengine
systemctl start taosd

# 检查日志
tail -f /var/log/taos/taosd.log
```

---

## API 问题

### Swagger UI 无法访问

**排查步骤**:
1. 检查后端服务是否运行
2. 检查端口是否正确
3. 检查 CORS 配置

```bash
# 检查进程
ps aux | grep uvicorn

# 检查端口占用
lsof -i :8000

# 测试 API 健康
curl http://localhost:8000/health
```

### 请求超时

**排查步骤**:
1. 检查网络延迟
2. 检查数据库查询性能
3. 检查是否有慢查询

```bash
# 检查慢查询日志
tail -f /var/log/postgresql/postgresql.log | grep "duration:"

# 检查 API 响应时间
curl -w "\nTime: %{time_total}s\n" http://localhost:8000/api/v1/market/kline
```

---

## 前端问题

### 页面加载缓慢

**排查步骤**:
1. 检查网络连接
2. 检查浏览器控制台错误
3. 检查是否加载了过多资源

**解决方案**:
```bash
# 清除浏览器缓存
# 打开开发者工具 -> Network -> 勾选 "Disable cache"

# 检查前端构建
npm run build
npm run preview
```

### WebSocket 连接失败

**排查步骤**:
```javascript
// 浏览器控制台检查
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onerror = (e) => console.error('WebSocket error:', e);
```

**解决方案**:
```bash
# 检查 WebSocket 服务
curl http://localhost:8000/ws/health
```

---

## 日志查看

### API 日志

```bash
# 实时查看 API 日志
tail -f /var/log/mystocks/api.log

# 查看最近 100 行
tail -n 100 /var/log/mystocks/api.log

# 搜索错误
grep -i error /var/log/mystocks/api.log

# 搜索特定 request_id
grep "550e8400-e29b-41d4-a716-446655440000" /var/log/mystocks/api.log
```

### 数据库日志

```bash
# PostgreSQL 日志
tail -f /var/log/postgresql/postgresql.log

# TDengine 日志
tail -f /var/log/taos/taosd.log
```

### Nginx 日志

```bash
# 访问日志
tail -f /var/log/nginx/access.log

# 错误日志
tail -f /var/log/nginx/error.log
```

---

## 性能问题

### CPU 使用率过高

**排查步骤**:
```bash
# 查看进程占用
top -c

# 查看 Python 进程
ps aux | grep python

# 检查线程
pstack <pid>
```

**解决方案**:
```bash
# 重启服务
systemctl restart mystocks-api

# 增加 worker 数量
# .env 文件
UVICORN_WORKERS=4
```

### 内存不足

**排查步骤**:
```bash
# 查看内存使用
free -h

# 查看进程内存
ps aux --sort=-%mem | head
```

**解决方案**:
```bash
# 增加内存限制
# .env 文件
PYTHONMEMORYLIMIT=4G

# 重启服务
systemctl restart mystocks-api
```

### 数据库连接池耗尽

**错误信息**: `could not obtain connection from the pool`

**排查步骤**:
```bash
# 检查活跃连接
SELECT count(*) FROM pg_stat_activity;

# 检查最大连接数
SHOW max_connections;
```

**解决方案**:
```bash
# 增加连接池大小
# .env 文件
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10

# 减少连接泄漏
# 检查代码中的连接释放逻辑
```

---

## 联系方式

### 紧急支持

- **技术支持邮箱**: support@mystocks.example.com
- **值班电话**: 400-xxx-xxxx

### 提交问题反馈

请提供以下信息：
1. 错误截图
2. Request ID
3. 操作步骤
4. 期望结果
5. 实际结果
6. 环境信息（操作系统、Python 版本等）

```bash
# 获取环境信息
python3 -c "import sys; print('Python:', sys.version)"
python3 -c "import fastapi; print('FastAPI:', fastapi.__version__)"
```
