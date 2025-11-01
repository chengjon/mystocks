# MyStocks Web系统访问指南

**更新日期**: 2025-10-25
**系统架构**: TDengine + PostgreSQL 双数据库

---

## 服务器信息

### 前端服务 (Vite)
- **URL**: http://localhost:3000
- **端口**: 3000
- **框架**: Vue 3 + Element Plus + Vite
- **状态**: ✅ 运行中

### 后端服务 (FastAPI)
- **URL**: http://localhost:8000
- **端口**: 8000
- **框架**: FastAPI + Uvicorn
- **API文档**: http://localhost:8000/docs
- **状态**: ✅ 运行中

---

## 数据库监控页面 (US2新增)

### 访问地址
```
http://localhost:3000/system/database-monitor
```

### 功能特性
1. **健康状态监控**
   - TDengine连接状态
   - PostgreSQL连接状态
   - 数据库版本信息
   - 实时健康检查

2. **数据路由分布**
   - TDengine: 5项高频时序数据
   - PostgreSQL: 29项其他数据
   - 分类详细列表

3. **架构历史**
   - 简化历程：4数据库 → 2数据库
   - MySQL迁移记录（299行）
   - Redis移除记录

---

## API端点测试

### 数据库健康检查
```bash
curl http://localhost:8000/api/system/database/health | jq .
```

**预期输出**:
```json
{
  "success": true,
  "message": "数据库健康检查完成",
  "data": {
    "tdengine": {
      "status": "healthy",
      "message": "连接成功",
      "version": "3.3.6.13",
      "host": "192.168.123.104",
      "port": 6030,
      "database": "market_data"
    },
    "postgresql": {
      "status": "healthy",
      "message": "连接成功",
      "version": "PostgreSQL 17.6",
      "host": "192.168.123.104",
      "port": 5438,
      "database": "mystocks"
    },
    "summary": {
      "total_databases": 2,
      "healthy": 2,
      "unhealthy": 0,
      "checked_at": "2025-10-25T14:38:26.391462"
    }
  }
}
```

### 数据库统计信息
```bash
curl http://localhost:8000/api/system/database/stats | jq .
```

**返回**: 34项数据分类，5项TDengine，29项PostgreSQL的详细统计

---

## 其他系统页面

### 1. 系统架构页面 (US1)
```
http://localhost:3000/system/architecture
```
- 架构简化展示
- 双数据库配置详情
- 数据分类路由策略

### 2. 仪表盘
```
http://localhost:3000/dashboard
```
- 系统总览
- 实时数据统计

### 3. 市场行情
```
http://localhost:3000/market
```
- 实时行情数据
- 市场数据展示

---

## 启动服务

### 前端 (手动)
```bash
cd /opt/claude/mystocks_spec/web/frontend
npm run dev
# 服务启动在 http://localhost:3000
```

### 后端 (手动)
```bash
cd /opt/claude/mystocks_spec/web/backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# API启动在 http://localhost:8000
```

### 检查运行状态
```bash
# 检查前端
ps aux | grep vite | grep -v grep
curl -I http://localhost:3000

# 检查后端
ps aux | grep uvicorn | grep -v grep
curl http://localhost:8000/api/system/database/health
```

---

## 常见问题

### Q: 端口5173无法访问？
**A**: 系统配置使用端口3000，不是默认的5173。请访问 http://localhost:3000

### Q: 数据库监控页面空白？
**A**: 检查：
1. 后端API是否运行 (curl http://localhost:8000/api/system/database/health)
2. TDengine和PostgreSQL是否可访问
3. 浏览器控制台是否有错误

### Q: API返回连接失败？
**A**: 检查数据库连接：
```bash
# TDengine
taos -h 192.168.123.104 -P 6030 -u root -p taosdata

# PostgreSQL
psql -h 192.168.123.104 -p 5438 -U postgres -d mystocks
```

### Q: 如何查看日志？
**A**:
```bash
# 前端日志
tail -f /opt/claude/mystocks_spec/web/frontend/frontend.log

# 后端日志
tail -f /opt/claude/mystocks_spec/web/backend/backend.log
```

---

## 网络访问 (外部访问)

如果需要从外部网络访问（非localhost）：

### 前端
修改 `vite.config.js`:
```javascript
export default defineConfig({
  server: {
    host: '0.0.0.0',  // 监听所有网络接口
    port: 3000
  }
})
```

### 后端
后端已配置为监听 `0.0.0.0:8000`，可从外部访问。

**外部访问地址**:
- 前端: http://[服务器IP]:3000
- 后端: http://[服务器IP]:8000

**当前服务器IP**:
- 10.255.255.254
- 172.26.26.12

**外部访问URL示例**:
- http://172.26.26.12:3000/system/database-monitor
- http://172.26.26.12:8000/api/system/database/health

---

## 安全注意事项

⚠️ **生产环境部署**:
1. 修改默认密码
2. 启用HTTPS
3. 配置防火墙规则
4. 启用API认证
5. 限制CORS源

---

**文档维护**: 如有问题请查看 docs/US2_SIMPLIFIED_DATABASE_ARCHITECTURE_COMPLETION.md
