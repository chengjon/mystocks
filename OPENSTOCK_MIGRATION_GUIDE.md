# OpenStock 功能迁移指南

本文档记录了从 OpenStock 项目迁移到 MyStocks 项目的功能模块及其使用方法。

## 迁移概览

迁移日期: 2025-10-20

### 迁移的功能模块

1. **股票搜索服务** (Stock Search Service)
   - 支持多市场搜索：A 股（AKShare）和美股（Finnhub API）
   - 实时报价获取
   - 公司信息查询
   - 新闻获取

2. **自选股管理** (Watchlist Management)
   - 基于 PostgreSQL 的自选股存储
   - 用户级别的自选股列表
   - 备注功能

3. **TradingView 集成** (TradingView Widgets)
   - 图表配置生成
   - 多种 Widget 支持
   - 市场概览和筛选器

4. **邮件通知服务** (Email Notification)
   - SMTP 邮件发送
   - 欢迎邮件和每日简报
   - 告警邮件

5. **用户认证** (Authentication)
   - JWT 认证（已存在，无需迁移）
   - 会话管理

## 文件结构

### 新增服务文件

```
web/backend/app/services/
├── stock_search_service.py          # 股票搜索服务（支持A股+美股）
├── watchlist_service.py             # 自选股管理服务
├── email_notification_service.py   # 邮件通知服务
└── tradingview_widget_service.py   # TradingView Widget 服务
```

### 新增 API 路由

```
web/backend/app/api/
├── stock_search.py      # 股票搜索 API
├── watchlist.py         # 自选股管理 API
└── tradingview.py       # TradingView Widget API
```

## 功能详细说明

### 1. 股票搜索服务

#### 服务特性
- **多市场支持**: 自动检测并支持 A 股和美股搜索
- **智能路由**: 根据查询关键词自动选择数据源
- **缓存机制**: LRU 缓存提升搜索性能
- **统一接口**: 统一的搜索和报价接口

#### API 端点

**搜索股票**
```http
GET /api/stock-search/search?q={keyword}&market={auto|cn|us}
Authorization: Bearer {token}

响应示例:
[
  {
    "symbol": "600000",
    "description": "浦发银行",
    "displaySymbol": "600000",
    "type": "A股",
    "exchange": "上海证券交易所",
    "market": "CN"
  }
]
```

**获取实时报价**
```http
GET /api/stock-search/quote/{symbol}?market={cn|us}
Authorization: Bearer {token}

响应示例:
{
  "symbol": "600000",
  "name": "浦发银行",
  "current": 8.52,
  "change": 0.12,
  "percent_change": 1.43,
  "open": 8.40,
  "high": 8.55,
  "low": 8.38,
  "previous_close": 8.40,
  "volume": 12345678,
  "timestamp": 1697788800
}
```

**获取股票新闻**
```http
GET /api/stock-search/news/{symbol}?market={cn|us}&days=7
Authorization: Bearer {token}

响应示例:
[
  {
    "headline": "新闻标题",
    "summary": "新闻摘要",
    "source": "东方财富",
    "datetime": 1697788800,
    "url": "https://...",
    "category": "A股新闻"
  }
]
```

#### 配置要求

在 `.env` 文件中添加（可选）:
```bash
# 美股数据（可选，如果只用 A 股可以不配置）
FINNHUB_API_KEY=your_finnhub_api_key
```

### 2. 自选股管理

#### 服务特性
- **PostgreSQL 存储**: 基于关系数据库的可靠存储
- **用户隔离**: 每个用户独立的自选股列表
- **备注支持**: 为每只股票添加个人备注
- **自动去重**: 防止重复添加同一股票

#### API 端点

**获取自选股列表**
```http
GET /api/watchlist/
Authorization: Bearer {token}

响应示例:
[
  {
    "id": 1,
    "symbol": "600000",
    "display_name": "浦发银行",
    "exchange": "上海证券交易所",
    "added_at": "2025-10-20T10:30:00",
    "notes": "重点关注"
  }
]
```

**添加自选股**
```http
POST /api/watchlist/add
Authorization: Bearer {token}
Content-Type: application/json

{
  "symbol": "600000",
  "display_name": "浦发银行",
  "exchange": "上海证券交易所",
  "notes": "重点关注"
}

响应:
{
  "success": true,
  "message": "已添加到自选股",
  "symbol": "600000"
}
```

**删除自选股**
```http
DELETE /api/watchlist/remove/{symbol}
Authorization: Bearer {token}

响应:
{
  "success": true,
  "message": "已从自选股移除",
  "symbol": "600000"
}
```

**检查是否在自选股中**
```http
GET /api/watchlist/check/{symbol}
Authorization: Bearer {token}

响应:
{
  "symbol": "600000",
  "is_in_watchlist": true
}
```

**更新备注**
```http
PUT /api/watchlist/notes/{symbol}
Authorization: Bearer {token}
Content-Type: application/json

{
  "notes": "新的备注内容"
}
```

#### 数据库表结构

自选股表 `user_watchlist`:
```sql
CREATE TABLE user_watchlist (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    display_name VARCHAR(100),
    exchange VARCHAR(50),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    UNIQUE(user_id, symbol)
);
```

### 3. TradingView 集成

#### 服务特性
- **多种 Widget**: 支持图表、迷你图、Ticker Tape、市场概览等
- **配置生成**: 自动生成符合 TradingView 标准的配置
- **代码转换**: 自动将国内股票代码转换为 TradingView 格式

#### API 端点

**生成图表配置**
```http
POST /api/tradingview/chart/config
Authorization: Bearer {token}
Content-Type: application/json

{
  "symbol": "600000",
  "market": "CN",
  "interval": "D",
  "theme": "dark",
  "locale": "zh_CN",
  "container_id": "tradingview_chart"
}

响应:
{
  "success": true,
  "config": {
    "autosize": true,
    "symbol": "SSE:600000",
    "interval": "D",
    "theme": "dark",
    ...
  }
}
```

**生成迷你图表配置**
```http
POST /api/tradingview/mini-chart/config?symbol=600000&market=CN&theme=dark
Authorization: Bearer {token}

响应:
{
  "success": true,
  "config": {
    "symbol": "SSE:600000",
    "width": "100%",
    "height": 220,
    ...
  }
}
```

**生成市场概览配置**
```http
GET /api/tradingview/market-overview/config?market=china&theme=dark
Authorization: Bearer {token}

响应:
{
  "success": true,
  "config": {
    "tabs": [
      {
        "title": "指数",
        "symbols": [...]
      }
    ],
    ...
  }
}
```

#### 前端集成示例

```html
<!-- 引入 TradingView 库 -->
<script src="https://s3.tradingview.com/tv.js"></script>

<!-- 图表容器 -->
<div id="tradingview_chart"></div>

<script>
// 从 API 获取配置
fetch('/api/tradingview/chart/config', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    symbol: '600000',
    market: 'CN'
  })
})
.then(res => res.json())
.then(data => {
  // 创建 TradingView Widget
  new TradingView.widget(data.config);
});
</script>
```

### 4. 邮件通知服务

#### 服务特性
- **SMTP 支持**: 标准 SMTP 协议发送邮件
- **HTML 模板**: 美观的 HTML 邮件模板
- **多种邮件类型**: 欢迎邮件、每日简报、告警邮件

#### 配置要求

在 `.env` 文件中添加:
```bash
# SMTP 邮件配置
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_USE_TLS=true
SMTP_FROM_NAME=MyStocks
```

#### 使用示例

```python
from app.services.email_notification_service import get_email_service

# 获取邮件服务
email_service = get_email_service()

# 发送欢迎邮件
email_service.send_welcome_email(
    user_email="user@example.com",
    user_name="张三"
)

# 发送每日新闻简报
email_service.send_daily_newsletter(
    user_email="user@example.com",
    user_name="张三",
    watchlist_symbols=["600000", "000001"],
    news_data=[...]
)

# 发送告警邮件
email_service.send_alert_email(
    user_email="user@example.com",
    alert_type="price_alert",
    alert_message="浦发银行股价突破 10 元"
)
```

## 测试指南

### 1. 测试股票搜索

```bash
# 搜索 A 股
curl -X GET "http://localhost:8000/api/stock-search/search?q=浦发银行&market=cn" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取实时报价
curl -X GET "http://localhost:8000/api/stock-search/quote/600000?market=cn" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取股票新闻
curl -X GET "http://localhost:8000/api/stock-search/news/600000?market=cn&days=7" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. 测试自选股管理

```bash
# 添加自选股
curl -X POST "http://localhost:8000/api/watchlist/add" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "600000",
    "display_name": "浦发银行",
    "exchange": "上海证券交易所"
  }'

# 获取自选股列表
curl -X GET "http://localhost:8000/api/watchlist/" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 删除自选股
curl -X DELETE "http://localhost:8000/api/watchlist/remove/600000" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. 测试 TradingView 配置

```bash
# 获取图表配置
curl -X POST "http://localhost:8000/api/tradingview/chart/config" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "600000",
    "market": "CN",
    "interval": "D",
    "theme": "dark"
  }'

# 获取市场概览配置
curl -X GET "http://localhost:8000/api/tradingview/market-overview/config?market=china" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 环境配置示例

完整的 `.env` 配置示例:

```bash
# PostgreSQL 数据库（必需）
POSTGRESQL_HOST=localhost
POSTGRESQL_PORT=5432
POSTGRESQL_DATABASE=mystocks
POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=your_password

# Finnhub API（可选，仅美股）
FINNHUB_API_KEY=your_finnhub_api_key

# SMTP 邮件配置（可选）
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_USE_TLS=true
SMTP_FROM_NAME=MyStocks

# JWT 密钥（已存在）
SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

## 注意事项

1. **AKShare 依赖**: 确保已安装 akshare (`pip install akshare`)
2. **数据库表**: 自选股表会自动创建，但建议提前运行迁移
3. **API Key**: Finnhub API 仅在需要美股数据时配置
4. **邮件服务**: Gmail 需要使用应用专用密码
5. **前端集成**: TradingView 需要在前端引入官方 JS 库

## 迁移清单

- [x] 股票搜索服务迁移（支持 A 股 + 美股）
- [x] 自选股管理服务迁移（PostgreSQL）
- [x] TradingView Widget 集成
- [x] 邮件通知服务迁移
- [x] API 路由注册
- [x] 依赖项更新
- [x] 文档编写
- [ ] 单元测试编写
- [ ] 前端集成

## 下一步计划

1. 编写单元测试
2. 前端页面集成
3. 性能优化和缓存策略
4. 添加更多数据源支持

## 常见问题

### Q: 如何只使用 A 股功能？
A: 不配置 `FINNHUB_API_KEY`，系统会自动只使用 AKShare 数据源。

### Q: 自选股数据存储在哪里？
A: 存储在 PostgreSQL 数据库的 `user_watchlist` 表中。

### Q: TradingView Widget 需要付费吗？
A: TradingView 免费版 Widget 足够使用，高级功能可能需要付费。

### Q: 邮件发送失败怎么办？
A: 检查 SMTP 配置，Gmail 需要启用"不够安全的应用访问权限"或使用应用专用密码。

## 支持与反馈

如有问题或建议，请联系项目维护人员或提交 Issue。
