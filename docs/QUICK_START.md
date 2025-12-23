# MyStocks 快速启动指南

## 系统要求
- Python 3.12+
- Node.js 16+
- PostgreSQL 17.x
- TDengine 3.3.x

## 启动步骤

### 1. 启动数据库服务
```bash
# 启动PostgreSQL
sudo systemctl start postgresql
# 或使用Docker
docker-compose -f /opt/claude/mystocks_spec/config/docker-compose.postgresql.yml up -d

# 启动TDengine (如果需要)
docker-compose -f /opt/claude/mystocks_spec/config/docker-compose.tdengine.yml up -d
```

### 2. 启动后端服务
```bash
# 进入项目目录
cd /opt/claude/mystocks_spec

# 启动后端服务
pm2 start ecosystem.config.js --env dev

# 验证后端服务
curl http://localhost:8888/health
# 应返回: {"status":"healthy","timestamp":...,"service":"mystocks-web-api"}
```

### 3. 启动前端服务
```bash
# 进入前端目录
cd /opt/claude/mystocks_spec/web/frontend

# 安装依赖 (首次启动时)
npm install

# 启动前端服务
npm run dev

# 前端服务将运行在 http://localhost:3001
```

### 4. 启动数据同步服务（可选）
```bash
# 启动数据同步服务（股票基础信息和K线数据）
pm2 start ecosystem.config.js --only data-sync-basic,data-sync-kline --env dev

# 或启动所有服务
pm2 start ecosystem.config.js --env dev

# 查看服务状态
pm2 list

# 手动触发数据同步（测试）
pm2 trigger data-sync-basic
pm2 trigger data-sync-kline
pm2 trigger data-sync-minute-kline
pm2 trigger data-sync-industry-classify
pm2 trigger data-sync-concept-classify
pm2 trigger data-sync-stock-industry-concept

# 查看同步日志
tail -f logs/data_sync/stock_basic_sync.log
tail -f logs/data_sync/stock_kline_sync.log
tail -f logs/data_sync/minute_kline_sync.log
tail -f logs/data_sync/industry_classify_sync.log
tail -f logs/data_sync/concept_classify_sync.log
tail -f logs/data_sync/stock_industry_concept_sync.log
```

### 5. 验证效果
```bash
# 访问前端页面
open http://localhost:3001  # 或在浏览器中手动访问

# 验证API连接
curl -X POST "http://localhost:8888/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# 验证数据获取
TOKEN=$(curl -s -X POST "http://localhost:8888/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | \
  python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))")

curl -X GET "http://localhost:8888/api/data/stocks/basic?limit=5" \
  -H "Authorization: Bearer $TOKEN"
```

## 页面功能验证
启动完成后，访问以下页面确认功能正常：

1. **首页 (`http://localhost:3001/`)**: 显示系统概览
2. **仪表板 (`http://localhost:3001/dashboard`)**: 显示股票统计数据
3. **股票列表 (`http://localhost:3001/stocks`)**: 显示真实股票数据（如平安银行、万科A等）
4. **技术分析 (`http://localhost:3001/technical-analysis`)**: 技术指标分析界面

## 常见问题
1. 如果前端页面显示空白，请检查Vite配置中的代理设置
2. 如果API调用失败，请确认后端服务端口和认证令牌
3. 如果数据不显示，请检查数据库连接和数据表是否存在
4. 如果数据同步失败，请检查网络连接和数据源配置

## 停止服务
```bash
# 停止后端服务
pm2 stop mystocks-backend

# 停止数据同步服务
pm2 stop data-sync-basic data-sync-kline

# 停止前端服务（在前端目录中按Ctrl+C）
cd /opt/claude/mystocks_spec/web/frontend
# (在运行npm run dev的终端中按Ctrl+C)

# 停止所有服务
pm2 stop all
```
