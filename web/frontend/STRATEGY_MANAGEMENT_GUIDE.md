# 策略管理功能使用指南

## 📋 功能概览

策略管理模块提供了完整的股票策略筛选系统，基于InStock项目的10个经典策略实现。系统分为5个功能标签页：

1. **策略列表** - 查看所有可用策略及其详细信息
2. **单只运行** - 对单只股票运行指定策略
3. **批量扫描** - 批量扫描全市场或指定股票列表
4. **结果查询** - 查询和分析历史策略结果
5. **统计分析** - 查看策略统计数据和排行榜

## 🗂️ 文件结构

```
web/frontend/src/
├── views/
│   ├── StrategyManagement.vue          # 策略管理主页面
│   └── strategy/                        # 策略子组件目录
│       ├── StrategyList.vue            # 策略列表
│       ├── SingleRun.vue               # 单只运行
│       ├── BatchScan.vue               # 批量扫描
│       ├── ResultsQuery.vue            # 结果查询
│       └── StatsAnalysis.vue           # 统计分析
└── config/
    └── api.js                           # API配置（已添加策略端点）

web/backend/
├── app/
│   ├── strategies/
│   │   └── stock_strategies.py         # 10个策略实现
│   ├── models/
│   │   └── strategy.py                 # 策略数据模型
│   ├── services/
│   │   └── strategy_service.py         # 策略服务层
│   └── api/
│       └── strategy.py                  # 策略API端点
└── scripts/
    ├── create_strategy_tables.sql      # 数据库表创建脚本
    └── test_strategy_api.py            # API测试脚本
```

## 🔧 配置说明

### 1. 数据库配置

策略系统使用PostgreSQL数据库存储策略结果。数据库配置在后端的`.env`文件中：

```bash
POSTGRESQL_HOST=192.168.123.104
POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=c790414J
POSTGRESQL_PORT=5438
POSTGRESQL_DATABASE=mystocks
```

### 2. API端点配置

前端API配置已自动添加到 `src/config/api.js`:

```javascript
strategy: {
  definitions: `${API_BASE_URL}/api/strategy/definitions`,
  runSingle: `${API_BASE_URL}/api/strategy/run/single`,
  runBatch: `${API_BASE_URL}/api/strategy/run/batch`,
  results: `${API_BASE_URL}/api/strategy/results`,
  matchedStocks: `${API_BASE_URL}/api/strategy/matched-stocks`,
  stats: `${API_BASE_URL}/api/strategy/stats/summary`
}
```

## 📊 10个经典策略

| 策略代码 | 中文名 | 英文名 | 描述 |
|---------|--------|--------|------|
| volume_surge | 放量上涨 | Volume Surge | 成交量放大2倍以上且价格上涨 |
| ma_bullish | 均线多头 | MA Bullish | 短期均线在长期均线上方，多条均线向上发散 |
| turtle_trading | 海龟交易法则 | Turtle Trading | 创出60日新高的股票 |
| consolidation_platform | 停机坪 | Consolidation Platform | 股价横盘整理，成交量缩小，蓄势待发 |
| ma250_pullback | 回踩年线 | MA250 Pullback | 股价回踩250日均线获得支撑 |
| breakthrough_platform | 突破平台 | Breakthrough Platform | 股价突破前期平台高点 |
| low_drawdown | 无大幅回撤 | Low Drawdown | 上涨过程中回撤幅度较小的强势股 |
| high_tight_flag | 高而窄的旗形 | High Tight Flag | 快速上涨后窄幅整理的旗形形态 |
| volume_limit_down | 放量跌停 | Volume Limit Down | 放量且跌停，识别恐慌性抛售 |
| low_atr_growth | 低ATR成长 | Low ATR Growth | ATR（平均真实波幅）较低但稳定增长 |

## 🚀 使用步骤

### 1. 启动后端服务

```bash
cd /opt/claude/mystocks_spec/web/backend
python -m app.main
```

后端服务将在 `http://localhost:8000` 启动。

### 2. 启动前端服务

```bash
cd /opt/claude/mystocks_spec/web/frontend
npm run dev
```

前端服务将在 `http://localhost:3000` 启动。

### 3. 访问策略管理页面

在浏览器中访问前端地址，导航到 **策略管理** 菜单。

## 💡 功能使用说明

### 策略列表

- 显示所有10个可用策略
- 每个策略卡片显示：
  - 中英文名称
  - 策略描述
  - 策略参数
  - 启用状态
- 可快速跳转到"运行策略"或"查看结果"

### 单只运行

1. 选择要运行的策略
2. 输入股票代码（如：600519）
3. 可选输入股票名称（如：贵州茅台）
4. 可选择检查日期（默认今天）
5. 点击"运行策略"
6. 查看匹配结果

### 批量扫描

支持三种扫描模式：

1. **全市场扫描** - 扫描所有A股
2. **指定股票列表** - 输入逗号分隔的股票代码
3. **限制数量扫描** - 用于测试，扫描前N只股票

扫描完成后显示统计信息：
- 总计扫描数量
- 匹配数量
- 失败数量
- 匹配率

### 结果查询

支持多维度查询：
- 按策略筛选
- 按股票代码筛选
- 按检查日期筛选
- 按匹配结果筛选

查询结果表格显示：
- 检查日期
- 策略名称
- 股票代码和名称
- 匹配结果
- 最新价和涨跌幅
- 匹配度评分

### 统计分析

提供策略统计和排行榜：
- 选择统计日期
- 显示每个策略的匹配数量
- 汇总统计（总数、平均、最大）
- TOP 5策略排行榜
- 点击查看具体匹配股票列表

## 🧪 测试

### 后端API测试

```bash
cd /opt/claude/mystocks_spec/web/backend
python scripts/test_strategy_api.py
```

测试包括：
- 获取策略定义
- 单只股票策略运行
- 批量策略运行
- 结果查询
- 统计分析

### 手动测试建议

1. **测试单只运行**：
   - 策略：turtle_trading（海龟交易法则）
   - 股票：600519（贵州茅台）

2. **测试批量扫描**：
   - 策略：volume_surge（放量上涨）
   - 模式：限制数量
   - 数量：10只（快速测试）

3. **测试结果查询**：
   - 筛选匹配结果：true
   - 查看最近10条记录

## 📝 数据库表

策略系统使用3个PostgreSQL表：

### 1. strategy_definition（策略定义表）
- 存储10个策略的元数据
- 包含策略代码、名称、描述、参数等

### 2. strategy_result（策略结果表）
- 存储策略运行结果
- 包含股票代码、匹配结果、匹配度评分等

### 3. strategy_backtest（策略回测表）
- 预留用于回测功能
- 存储回测结果和收益率数据

## 🔍 API端点说明

### 1. GET /api/strategy/definitions
获取所有策略定义

**响应示例**：
```json
{
  "success": true,
  "data": [
    {
      "strategy_code": "volume_surge",
      "strategy_name_cn": "放量上涨",
      "strategy_name_en": "Volume Surge",
      "description": "成交量放大2倍以上且价格上涨的股票",
      "is_active": true
    }
  ]
}
```

### 2. POST /api/strategy/run/single
对单只股票运行策略

**参数**：
- `strategy_code`: 策略代码（必填）
- `symbol`: 股票代码（必填）
- `stock_name`: 股票名称（可选）
- `check_date`: 检查日期 YYYY-MM-DD（可选）

### 3. POST /api/strategy/run/batch
批量运行策略

**参数**：
- `strategy_code`: 策略代码（必填）
- `symbols`: 股票代码列表，逗号分隔（可选）
- `limit`: 限制数量（可选）
- `market`: 市场类型 A/SH/SZ/CYB/KCB（可选）

### 4. GET /api/strategy/results
查询策略结果

**参数**：
- `strategy_code`: 策略代码（可选）
- `symbol`: 股票代码（可选）
- `check_date`: 检查日期（可选）
- `match_result`: 是否匹配 true/false（可选）
- `limit`: 返回数量（默认100）
- `offset`: 偏移量（默认0）

### 5. GET /api/strategy/matched-stocks
获取匹配指定策略的股票列表

**参数**：
- `strategy_code`: 策略代码（必填）
- `check_date`: 检查日期（可选）
- `limit`: 返回数量（默认100）

### 6. GET /api/strategy/stats/summary
获取策略统计摘要

**参数**：
- `check_date`: 统计日期（可选）

## 🎯 最佳实践

1. **先测试再批量**
   - 先用"单只运行"测试策略效果
   - 再用"批量扫描"的限制模式（10-100只）测试
   - 最后再进行全市场扫描

2. **合理使用日期**
   - 默认使用今天的数据
   - 可选择历史日期进行回测

3. **关注匹配率**
   - 不同策略的匹配率差异很大
   - 海龟交易法则通常匹配率较低（强势股少）
   - 放量上涨策略匹配率相对较高

4. **结合多个策略**
   - 可以运行多个策略交叉验证
   - 同时满足多个策略的股票质量更高

## ⚠️ 注意事项

1. **数据依赖**
   - 策略依赖akshare获取股票历史数据
   - 需要稳定的网络连接
   - 非交易时间数据可能不完整

2. **性能考虑**
   - 全市场扫描（5000+只股票）需要较长时间
   - 建议使用限制模式进行测试
   - 批量扫描时注意API限流

3. **数据准确性**
   - 策略结果仅供参考
   - 需结合基本面分析
   - 建议人工复核重要决策

## 📞 技术支持

如有问题，请查看：
- API文档：http://localhost:8000/api/docs
- 测试脚本：`scripts/test_strategy_api.py`
- 迁移报告：`INSTOCK_MIGRATION_REPORT.md`

---

**版本**: 1.0.0
**更新日期**: 2025-10-23
**作者**: MyStocks Team
