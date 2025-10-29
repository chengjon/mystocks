# 故障排查指南

本文档提供常见问题的快速诊断和解决方案，基于 5 层验证模型。

**适用场景**: 功能不工作时的系统化排查流程

---

## 快速诊断流程

```
发现问题
    ↓
运行多层验证
    ↓
识别失败层级
    ↓
应用对应解决方案
    ↓
验证修复成功
```

---

## 常见故障场景

### 场景 1: API 返回 500 错误

**症状**: 前端显示"服务器错误"或空白页面

**诊断步骤**:
```bash
# 1. 检查后端服务是否运行
curl http://localhost:8000/health

# 2. 直接测试 API
http GET http://localhost:8000/api/market/dragon-tiger

# 3. 查看后端日志
tail -f /tmp/uvicorn.log
```

**常见原因**:
- **Layer 5 (数据库)**: 数据库连接失败或表不存在
- **Layer 2 (API)**: 后端代码逻辑错误、SQL 语法错误

**解决方案**:

**如果是数据库问题**:
```bash
# 检查数据库连接
PGPASSWORD=mystocks2025 psql -h localhost -U mystocks_user -d mystocks -c "SELECT 1"

# 检查表是否存在
PGPASSWORD=mystocks2025 psql -h localhost -U mystocks_user -d mystocks -c "\dt"

# 检查数据是否存在
PGPASSWORD=mystocks2025 psql -h localhost -U mystocks_user -d mystocks -c "SELECT COUNT(*) FROM cn_stock_top"
```

**如果是后端代码问题**:
```bash
# 重启后端服务
pkill -f uvicorn
cd web/backend && python -m uvicorn app.main:app --reload

# 查看详细错误
tail -100 /tmp/uvicorn.log
```

---

### 场景 2: 前端页面显示"无数据"

**症状**: 页面加载正常，但表格为空或显示"无数据"

**诊断步骤**:
```bash
# 1. Layer 5: 检查数据库是否有数据
PGPASSWORD=mystocks2025 psql -h localhost -U mystocks_user -d mystocks -c "SELECT COUNT(*) FROM cn_stock_top"

# 2. Layer 2: 检查 API 是否返回数据
http GET http://localhost:8000/api/market/v3/dragon-tiger?limit=5

# 3. Layer 4: 检查浏览器控制台
# 打开浏览器 F12 → Console 查看错误
```

**常见原因**:
1. **数据库无数据** → 运行数据采集
2. **API 返回空数组** → 检查查询条件
3. **前端未正确渲染** → 检查字段映射

**解决方案**:

**情况 A: 数据库无数据**
```bash
# 运行数据采集（根据实际脚本调整）
python collect_dragon_tiger.py
python collect_etf_data.py
```

**情况 B: API 查询条件过严**
```python
# 检查 API 代码中的日期过滤
# ❌ 错误：只查今天
WHERE trade_date = CURRENT_DATE

# ✅ 正确：查最新交易日
WHERE trade_date = (SELECT MAX(trade_date) FROM cn_stock_top)
```

**情况 C: 前端字段映射错误**
```javascript
// 检查 API 返回字段和前端使用字段是否一致
// API 返回: { stock_code, stock_name }
// 前端使用: {{ item.code }} ❌
// 应该使用: {{ item.stock_code }} ✅
```

---

### 场景 3: 数据库连接失败

**症状**: 应用启动报错"could not connect to server"

**诊断步骤**:
```bash
# 1. 检查 PostgreSQL 服务状态
sudo systemctl status postgresql
# 或
pg_isready -h localhost -p 5432

# 2. 检查连接配置
cat .env | grep POSTGRESQL

# 3. 测试连接
PGPASSWORD=mystocks2025 psql -h localhost -U mystocks_user -d mystocks
```

**常见原因**:
- PostgreSQL 服务未启动
- 连接配置错误（主机、端口、密码）
- 防火墙阻止连接
- 数据库不存在

**解决方案**:

**启动 PostgreSQL**:
```bash
# Ubuntu/Debian
sudo systemctl start postgresql

# macOS
brew services start postgresql

# 验证
pg_isready
```

**检查配置**:
```bash
# 确认 .env 文件配置正确
POSTGRESQL_HOST=localhost
POSTGRESQL_PORT=5432
POSTGRESQL_USER=mystocks_user
POSTGRESQL_PASSWORD=mystocks2025
POSTGRESQL_DATABASE=mystocks
```

**创建数据库**（如果不存在）:
```bash
# 使用 postgres 超级用户创建
sudo -u postgres createdb mystocks
sudo -u postgres createuser mystocks_user
sudo -u postgres psql -c "ALTER USER mystocks_user WITH PASSWORD 'mystocks2025'"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE mystocks TO mystocks_user"
```

---

### 场景 4: 前端控制台报 JavaScript 错误

**症状**: 浏览器 Console 显示红色错误信息

**诊断步骤**:
1. 打开浏览器开发者工具 (F12)
2. 切换到 Console 标签
3. 查看错误信息

**常见错误类型**:

**4.1 TypeError: Cannot read property of undefined**
```javascript
// 错误示例
{{ item.fund_name }}  // ❌ API 返回的字段是 stock_name

// 解决方法
{{ item.stock_name }}  // ✅ 使用正确的字段名
```

**4.2 Network Error / CORS Error**
```
Access to fetch at 'http://localhost:8000/api/...' from origin 'http://localhost:5173' has been blocked by CORS policy
```

**解决方案**:
检查后端 CORS 配置:
```python
# web/backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**4.3 401 Unauthorized**
```
Failed to load resource: the server responded with a status of 401
```

**原因**: Token 过期或未提供

**解决方案**:
```javascript
// 检查请求是否包含 Authorization header
headers: {
  'Authorization': `Bearer ${token}`
}

// 重新登录获取新 token
```

---

### 场景 5: 页面加载缓慢

**症状**: 页面需要 5-10 秒才能显示数据

**诊断步骤**:
```bash
# 1. 检查 API 响应时间
time http GET http://localhost:8000/api/market/dragon-tiger

# 2. 检查数据库查询时间
PGPASSWORD=mystocks2025 psql -h localhost -U mystocks_user -d mystocks
\timing on
SELECT * FROM cn_stock_top LIMIT 100;
```

**常见原因**:
- 缺少数据库索引
- 查询返回数据量过大
- N+1 查询问题

**解决方案**:

**添加索引**:
```sql
-- 检查是否有索引
SELECT * FROM pg_indexes WHERE tablename = 'cn_stock_top';

-- 添加索引（如果缺少）
CREATE INDEX idx_cn_stock_top_trade_date ON cn_stock_top(trade_date);
CREATE INDEX idx_cn_stock_top_stock_code ON cn_stock_top(stock_code);
```

**限制返回数据量**:
```python
# API 添加默认限制
@app.get("/api/market/dragon-tiger")
async def get_dragon_tiger(limit: int = 50):  # 默认最多 50 条
    query = "SELECT * FROM cn_stock_top LIMIT %s"
    return db.execute(query, (min(limit, 100),))  # 最多 100 条
```

---

## 系统化排查模板

当遇到任何问题时，按以下顺序检查：

### 1. Layer 5 (数据库)
```bash
# 检查数据存在性
SELECT COUNT(*) FROM [table_name];

# 检查数据时效性
SELECT MAX(trade_date), CURRENT_DATE - MAX(trade_date) as days_old FROM [table_name];

# 检查数据完整性
SELECT COUNT(*) FROM [table_name] WHERE [key_field] IS NULL;
```

### 2. Layer 2 (API)
```bash
# 测试 API 端点
http GET http://localhost:8000/api/[endpoint]

# 检查响应状态
curl -I http://localhost:8000/api/[endpoint]

# 查看后端日志
tail -f /tmp/uvicorn.log
```

### 3. Layer 4 (UI)
- 打开浏览器开发者工具 (F12)
- 查看 Console 错误
- 查看 Network 请求状态
- 检查元素是否存在 (Elements 标签)

### 4. Layer 3 (集成)
```bash
# 运行集成测试
pytest tests/integration/test_[feature].py -v -s

# 使用多层验证
pytest specs/006-web-90-1/contracts/playwright-test-examples/ -v -s
```

---

## 快速修复检查清单

遇到问题时，快速过一遍这个清单：

### 后端服务
- [ ] 后端服务是否运行？ `curl http://localhost:8000/health`
- [ ] 是否有错误日志？ `tail -f /tmp/uvicorn.log`
- [ ] 端口是否被占用？ `lsof -i :8000`

### 数据库
- [ ] PostgreSQL 是否运行？ `pg_isready`
- [ ] 数据库是否有数据？ `SELECT COUNT(*) FROM cn_stock_top`
- [ ] 连接配置是否正确？ `cat .env | grep POSTGRESQL`

### 前端
- [ ] 前端服务是否运行？ `curl http://localhost:5173`
- [ ] 是否有控制台错误？ (F12 → Console)
- [ ] 网络请求是否成功？ (F12 → Network)

### 环境
- [ ] 依赖是否安装？ `pip list | grep playwright`
- [ ] 环境变量是否设置？ `echo $MYSTOCKS_URL`
- [ ] Node modules 是否安装？ `ls node_modules/`

---

## 获取帮助

### 日志位置
- **后端日志**: `/tmp/uvicorn.log`
- **前端日志**: 浏览器 Console (F12)
- **数据库日志**: `/var/log/postgresql/`
- **测试日志**: `pytest -v -s` 输出

### 调试工具
- **后端**: `http` (httpie) 测试 API
- **数据库**: `pgcli` 交互式查询
- **前端**: 浏览器 DevTools (F12)
- **集成**: Playwright 测试 + 截图

### 有用的命令
```bash
# 完整健康检查
./scripts/health_check.sh

# 重启所有服务
./scripts/restart_all.sh

# 运行完整验证
pytest tests/integration/ -v
```

---

## 预防性维护

定期执行以下操作避免问题：

### 每日
- 检查数据更新: `SELECT MAX(trade_date) FROM cn_stock_top`
- 检查服务状态: `curl http://localhost:8000/health`

### 每周
- 运行集成测试: `pytest tests/integration/ -v`
- 检查磁盘空间: `df -h`
- 清理旧日志: `find /tmp -name "*.log" -mtime +7 -delete`

### 每月
- 数据库维护: `VACUUM ANALYZE`
- 更新依赖: `pip install --upgrade -r requirements.txt`
- 代码审查: 运行 linter 和格式化工具

---

**记住**: 90% 的问题都能通过 5 层验证快速定位。使用 `validate_all_layers()` 是最快的诊断方法。
