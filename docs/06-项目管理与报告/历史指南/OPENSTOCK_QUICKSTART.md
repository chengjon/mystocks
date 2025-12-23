# OpenStock 功能快速开始

本文档提供快速开始使用从 OpenStock 迁移的功能。

## 🚀 5分钟快速开始

### 1. 启动后端服务

```bash
cd /opt/claude/mystocks_spec/web/backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. 获取访问令牌

```bash
# 使用默认管理员账号登录
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -d "username=admin&password=admin123" \
  | jq -r .access_token)

echo "Your token: $TOKEN"
```

### 3. 尝试第一个 API 调用

```bash
# 搜索浦发银行
curl -X GET "http://localhost:8000/api/stock-search/search?q=浦发&market=cn" \
  -H "Authorization: Bearer $TOKEN" | jq
```

## 📚 常用功能示例

### 股票搜索

#### 搜索 A 股
```bash
# 按名称搜索
curl -X GET "http://localhost:8000/api/stock-search/search?q=茅台&market=cn" \
  -H "Authorization: Bearer $TOKEN" | jq

# 按代码搜索
curl -X GET "http://localhost:8000/api/stock-search/search?q=600000&market=cn" \
  -H "Authorization: Bearer $TOKEN" | jq
```

#### 获取实时行情
```bash
curl -X GET "http://localhost:8000/api/stock-search/quote/600000?market=cn" \
  -H "Authorization: Bearer $TOKEN" | jq
```

#### 获取股票新闻
```bash
curl -X GET "http://localhost:8000/api/stock-search/news/600000?market=cn&days=3" \
  -H "Authorization: Bearer $TOKEN" | jq
```

### 自选股管理

#### 添加自选股
```bash
curl -X POST http://localhost:8000/api/watchlist/add \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "600000",
    "display_name": "浦发银行",
    "exchange": "上海证券交易所",
    "notes": "银行股龙头"
  }' | jq
```

#### 查看自选股列表
```bash
curl -X GET http://localhost:8000/api/watchlist/ \
  -H "Authorization: Bearer $TOKEN" | jq
```

#### 删除自选股
```bash
curl -X DELETE http://localhost:8000/api/watchlist/remove/600000 \
  -H "Authorization: Bearer $TOKEN" | jq
```

### TradingView Widget 配置

#### 获取图表配置
```bash
curl -X POST http://localhost:8000/api/tradingview/chart/config \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "600000",
    "market": "CN",
    "interval": "D",
    "theme": "dark"
  }' | jq
```

#### 获取市场概览配置
```bash
curl -X GET "http://localhost:8000/api/tradingview/market-overview/config?market=china&theme=dark" \
  -H "Authorization: Bearer $TOKEN" | jq
```

## 📖 API 文档

访问交互式 API 文档:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## 🔧 配置

### 最小配置（仅 A 股）

在 `.env` 文件中只需配置 PostgreSQL:

```bash
POSTGRESQL_HOST=localhost
POSTGRESQL_PORT=5432
POSTGRESQL_DATABASE=mystocks
POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=your_password
```

### 完整配置（A股+美股）

```bash
# PostgreSQL
POSTGRESQL_HOST=localhost
POSTGRESQL_PORT=5432
POSTGRESQL_DATABASE=mystocks
POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=your_password

# Finnhub API（美股数据）
FINNHUB_API_KEY=your_finnhub_api_key

# 邮件服务（可选）
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

## 🎯 实用脚本

### 批量添加自选股

创建文件 `add_watchlist.sh`:

```bash
#!/bin/bash

TOKEN="your_token_here"

# 自选股列表
stocks=(
  "600000:浦发银行"
  "600519:贵州茅台"
  "000858:五粮液"
  "000333:美的集团"
)

for stock in "${stocks[@]}"; do
  IFS=':' read -r symbol name <<< "$stock"

  curl -X POST http://localhost:8000/api/watchlist/add \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"symbol\": \"$symbol\",
      \"display_name\": \"$name\",
      \"exchange\": \"上海证券交易所\"
    }"

  echo "Added $name ($symbol)"
  sleep 0.5
done
```

### 获取自选股实时行情

创建文件 `get_watchlist_quotes.sh`:

```bash
#!/bin/bash

TOKEN="your_token_here"

# 获取自选股列表
symbols=$(curl -s -X GET http://localhost:8000/api/watchlist/symbols \
  -H "Authorization: Bearer $TOKEN" | jq -r '.[]')

echo "=== 自选股实时行情 ==="

for symbol in $symbols; do
  quote=$(curl -s -X GET "http://localhost:8000/api/stock-search/quote/$symbol?market=cn" \
    -H "Authorization: Bearer $TOKEN")

  name=$(echo $quote | jq -r '.name')
  current=$(echo $quote | jq -r '.current')
  change=$(echo $quote | jq -r '.percent_change')

  echo "$name ($symbol): ¥$current (${change}%)"
done
```

## 🐛 故障排查

### 问题：搜索返回空结果

**原因**: AKShare 未安装或网络问题

**解决**:
```bash
pip install akshare --upgrade
```

### 问题：自选股添加失败

**原因**: PostgreSQL 连接失败

**解决**:
1. 检查 PostgreSQL 是否运行
2. 验证 `.env` 中的数据库配置
3. 检查数据库权限

### 问题：美股搜索不工作

**原因**: Finnhub API Key 未配置

**解决**:
1. 注册 Finnhub 账号获取 API Key
2. 在 `.env` 中配置 `FINNHUB_API_KEY`
3. 重启后端服务

## 📝 下一步

1. 查看完整文档: `OPENSTOCK_MIGRATION_GUIDE.md`
2. 查看迁移总结: `OPENSTOCK_MIGRATION_SUMMARY.md`
3. 开发前端页面集成
4. 编写单元测试

## 💡 提示

- 使用 `jq` 格式化 JSON 输出: `| jq`
- 保存 token 到环境变量避免重复登录
- 使用 API 文档页面测试接口: http://localhost:8000/api/docs
- 自选股数据存储在 PostgreSQL，重启后不会丢失

## 🤝 获取帮助

如有问题，请参考:
- API 文档: http://localhost:8000/api/docs
- 迁移指南: OPENSTOCK_MIGRATION_GUIDE.md
- 项目 README: README.md

---

**快速开始版本**: v1.0
**最后更新**: 2025-10-20
