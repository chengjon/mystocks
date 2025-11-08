# ValueCell 功能迁移计划

## 📋 项目概述

本文档规划了将 ValueCell 多智能体交易系统的关键功能迁移到 MyStocks 量化交易数据管理系统的详细方案。

**迁移日期**: 2025-10-23
**状态**: 规划中 (Planning)

---

## 🎯 迁移目标

### 核心目标
1. **增强实时监控能力**: 引入实时市场监控和智能告警系统
2. **提升技术分析水平**: 集成更丰富的技术指标和分析工具
3. **扩展数据源**: 添加多个数据源以提高数据可靠性和覆盖面
4. **智能化分析**: 引入 AI 驱动的多维度分析能力
5. **优化用户体验**: 改进前端可视化和交互体验

### 适配原则
- **本地化优先**: 所有功能必须适配中国A股市场特点
- **渐进式迁移**: 分阶段实施，每个阶段都有可交付成果
- **保持兼容**: 不破坏现有功能，增量式添加新特性
- **性能优化**: 确保新功能不影响系统整体性能

---

## 📊 ValueCell 核心功能分析

### 1. SEC Agent (证券监管文件分析)
**原功能**:
- 监控美国 SEC EDGAR 文件 (10-K, 8-K, 10-Q, 13F-HR)
- 实时文件变更检测和通知
- AI 驱动的财务文件分析

**迁移适配**:
- ✅ **适配中国市场**: 监控上交所/深交所公告
- ✅ **文件类型**: 年报、季报、临时公告、股东大会决议
- ✅ **数据源**: 巨潮资讯网 API
- ⚠️ **优先级**: 高 (P0)

### 2. Auto Trading Agent (自动交易智能体)
**原功能**:
- 实时市场数据获取 (yfinance)
- 技术指标计算 (EMA, MACD, RSI, Bollinger Bands)
- 持仓管理和交易执行
- 风险管理和投资组合优化

**迁移适配**:
- ✅ **市场数据**: 使用现有 akshare 适配器
- ✅ **技术指标**: 集成 TA-Lib (已安装)
- ⚠️ **交易执行**: 仅实现模拟交易 (纸面交易)
- ✅ **风险管理**: 添加中国特色风控规则 (涨跌停、T+1)
- ⚠️ **优先级**: 中 (P1)

### 3. Research Agent (研究智能体)
**原功能**:
- 向量数据库 (VDB) 存储知识
- 多源数据聚合和分析
- AI 驱动的研究报告生成

**迁移适配**:
- ⚠️ **向量数据库**: 暂不实施 (需要额外基础设施)
- ✅ **研究数据**: 整合到现有 PostgreSQL
- ✅ **报告生成**: 使用现有策略分析框架
- ⚠️ **优先级**: 低 (P2)

### 4. 实时监控和告警系统
**原功能**:
- 价格变动监控
- 成交量激增检测
- 技术突破信号
- 多渠道通知 (webhook, email, log)

**迁移适配**:
- ✅ **完全适用**: 中国市场同样需要
- ✅ **本地化**: 适配 A股交易时间 (9:30-15:00)
- ✅ **扩展**: 添加龙虎榜、大单监控
- ✅ **优先级**: 高 (P0)

### 5. 多智能体协作框架
**原功能**:
- 基于 Agno 框架的多智能体系统
- 基本面分析师、情绪分析师、新闻分析师、技术分析师协作
- 动态讨论机制

**迁移适配**:
- ⚠️ **框架依赖**: 需要引入 Agno 或 LangChain
- ⚠️ **LLM 集成**: 需要配置 OpenAI/Anthropic API
- ✅ **简化版本**: 先实现单一分析智能体
- ⚠️ **优先级**: 低 (P2)

---

## 🗓️ 分阶段实施计划

### Phase 1: 实时监控和告警系统 (优先级: P0)

**目标**: 构建完整的实时市场监控体系

**实施内容**:

#### 1.1 后端监控服务
- [ ] 创建 `monitoring_service.py` 监控服务模块
- [ ] 实现实时价格监控 (基于 akshare 实时行情)
- [ ] 实现成交量激增检测
- [ ] 实现技术突破信号检测 (突破重要阻力位/支撑位)
- [ ] 实现涨停/跌停监控
- [ ] 实现龙虎榜数据抓取和分析

**数据库设计**:
```sql
-- 告警规则表
CREATE TABLE alert_rule (
    id SERIAL PRIMARY KEY,
    rule_name VARCHAR(100) NOT NULL,
    rule_type VARCHAR(50) NOT NULL, -- price_change, volume_surge, technical_break
    symbol VARCHAR(20),              -- NULL表示全市场
    parameters JSONB,                -- 规则参数
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 告警记录表
CREATE TABLE alert_record (
    id SERIAL PRIMARY KEY,
    rule_id INTEGER REFERENCES alert_rule(id),
    symbol VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100),
    alert_time TIMESTAMP DEFAULT NOW(),
    alert_type VARCHAR(50) NOT NULL,
    alert_level VARCHAR(20) DEFAULT 'info', -- info, warning, critical
    alert_message TEXT,
    alert_details JSONB,
    is_read BOOLEAN DEFAULT FALSE
);

-- 实时监控数据表
CREATE TABLE realtime_monitoring (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    price DECIMAL(10, 2),
    volume BIGINT,
    amount DECIMAL(20, 2),
    change_percent DECIMAL(10, 2),
    indicators JSONB,                -- 技术指标
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_alert_record_symbol ON alert_record(symbol);
CREATE INDEX idx_alert_record_time ON alert_record(alert_time);
CREATE INDEX idx_realtime_symbol_time ON realtime_monitoring(symbol, timestamp);
```

#### 1.2 API 端点
```python
# app/api/monitoring.py

@router.get("/alerts")
async def get_alerts(
    symbol: Optional[str] = None,
    alert_type: Optional[str] = None,
    is_read: Optional[bool] = None,
    limit: int = 100
):
    """获取告警记录"""

@router.post("/alerts/rules")
async def create_alert_rule(rule: AlertRuleCreate):
    """创建告警规则"""

@router.get("/alerts/rules")
async def get_alert_rules():
    """获取所有告警规则"""

@router.put("/alerts/rules/{rule_id}")
async def update_alert_rule(rule_id: int, rule: AlertRuleUpdate):
    """更新告警规则"""

@router.delete("/alerts/rules/{rule_id}")
async def delete_alert_rule(rule_id: int):
    """删除告警规则"""

@router.post("/alerts/{alert_id}/mark-read")
async def mark_alert_read(alert_id: int):
    """标记告警为已读"""

@router.get("/monitoring/realtime/{symbol}")
async def get_realtime_monitoring(symbol: str):
    """获取单只股票的实时监控数据"""

@router.get("/monitoring/summary")
async def get_monitoring_summary():
    """获取市场监控摘要"""
```

#### 1.3 前端实现
```
src/views/
├── MarketMonitoring.vue          # 市场监控主页面
└── monitoring/
    ├── AlertList.vue              # 告警列表
    ├── AlertRules.vue             # 告警规则配置
    ├── RealtimeMonitor.vue        # 实时监控面板
    └── MonitoringSummary.vue      # 监控摘要
```

**功能特性**:
- 实时告警弹窗通知
- 告警声音提示
- 告警规则可视化配置
- 实时监控数据图表 (使用 ECharts)
- WebSocket 推送实时数据

**时间估算**: 5-7 天

---

### Phase 2: 增强技术分析能力 (优先级: P1)

**目标**: 提供更丰富的技术指标和图表分析工具

**实施内容**:

#### 2.1 技术指标扩展
基于 ValueCell 的 `MarketDataProvider` 和 `TechnicalIndicators`，扩展现有技术分析功能：

```python
# app/services/technical_analysis_service.py

class TechnicalAnalysisService:
    """技术分析服务"""

    def calculate_all_indicators(self, symbol: str, period: str = "daily") -> Dict:
        """计算所有技术指标"""
        return {
            "trend": self.calculate_trend_indicators(symbol),
            "momentum": self.calculate_momentum_indicators(symbol),
            "volatility": self.calculate_volatility_indicators(symbol),
            "volume": self.calculate_volume_indicators(symbol),
        }

    def calculate_trend_indicators(self, symbol: str) -> Dict:
        """趋势指标"""
        # MA, EMA, MACD, DMI, SAR

    def calculate_momentum_indicators(self, symbol: str) -> Dict:
        """动量指标"""
        # RSI, KDJ, CCI, WR

    def calculate_volatility_indicators(self, symbol: str) -> Dict:
        """波动性指标"""
        # Bollinger Bands, ATR, Keltner Channel

    def calculate_volume_indicators(self, symbol: str) -> Dict:
        """成交量指标"""
        # OBV, VWAP, Volume Profile
```

#### 2.2 增强 K 线图表
参考 ValueCell 的图表组件，使用 ECharts 实现：

- 主图指标: MA, EMA, Bollinger Bands
- 副图指标: MACD, RSI, KDJ, Volume
- 画线工具: 趋势线、水平线、黄金分割
- 形态识别: 自动标注头肩顶、双底等形态

#### 2.3 API 端点
```python
@router.get("/technical/{symbol}/indicators")
async def get_technical_indicators(symbol: str, period: str = "daily"):
    """获取技术指标"""

@router.get("/technical/{symbol}/patterns")
async def detect_patterns(symbol: str):
    """检测技术形态"""

@router.get("/technical/{symbol}/signals")
async def get_trading_signals(symbol: str):
    """获取交易信号"""
```

**时间估算**: 3-4 天

---

### Phase 3: 多数据源集成 (优先级: P1)

**目标**: 扩展数据源以提高数据可靠性和覆盖面

**实施内容**:

#### 3.1 新增数据源适配器
```python
# adapters/tushare_pro_adapter.py
class TushareProDataSource(IDataSource):
    """Tushare Pro 数据源 (付费版，数据更全)"""

# adapters/eastmoney_adapter.py
class EastMoneyDataSource(IDataSource):
    """东方财富数据源 (免费，实时性好)"""

# adapters/cninfo_adapter.py
class CninfoDataSource(IDataSource):
    """巨潮资讯数据源 (官方公告)"""
```

#### 3.2 数据源管理
```python
# manager/multi_source_manager.py

class MultiSourceManager:
    """多数据源管理器"""

    def get_data_with_fallback(self,
                                source_priority: List[str],
                                data_type: str,
                                **kwargs) -> pd.DataFrame:
        """使用优先级顺序获取数据，自动降级"""

    def aggregate_from_multiple_sources(self,
                                       sources: List[str],
                                       data_type: str,
                                       **kwargs) -> pd.DataFrame:
        """从多个数据源聚合数据"""

    def validate_data_consistency(self,
                                  source1: str,
                                  source2: str,
                                  **kwargs) -> Dict:
        """验证不同数据源的一致性"""
```

#### 3.3 公告监控 (类似 SEC Agent)
```python
# services/announcement_monitor.py

class AnnouncementMonitor:
    """公告监控服务 (适配中国市场的 SEC Agent)"""

    async def monitor_announcements(self, symbols: List[str] = None):
        """监控公司公告"""

    async def analyze_announcement(self, announcement_id: str) -> Dict:
        """分析公告内容"""

    async def detect_important_events(self) -> List[Dict]:
        """检测重要事件"""
        # 大股东增减持、重大合同、业绩预告等
```

**数据库表**:
```sql
CREATE TABLE announcement (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100),
    title TEXT NOT NULL,
    announcement_type VARCHAR(50), -- 年报、季报、临时公告等
    publish_date DATE NOT NULL,
    content TEXT,
    url TEXT,
    importance_level INTEGER,      -- 1-5重要性评级
    keywords TEXT[],               -- 关键词数组
    sentiment_score DECIMAL(3, 2), -- 情绪评分 -1到1
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_announcement_symbol ON announcement(symbol);
CREATE INDEX idx_announcement_date ON announcement(publish_date);
CREATE INDEX idx_announcement_type ON announcement(announcement_type);
```

**时间估算**: 4-5 天

---

### Phase 4: 智能分析增强 (优先级: P2)

**目标**: 引入 AI 驱动的智能分析能力

**实施内容**:

#### 4.1 简化版智能分析
不完全实现 ValueCell 的多智能体框架，而是实现单一的综合分析服务：

```python
# services/intelligent_analysis_service.py

class IntelligentAnalysisService:
    """智能分析服务 (简化版)"""

    def __init__(self):
        self.llm_client = None  # 可选集成 OpenAI/Claude

    async def analyze_stock(self, symbol: str) -> Dict:
        """综合分析股票"""
        return {
            "technical": await self._technical_analysis(symbol),
            "fundamental": await self._fundamental_analysis(symbol),
            "sentiment": await self._sentiment_analysis(symbol),
            "risk": await self._risk_analysis(symbol),
            "recommendation": await self._generate_recommendation(symbol)
        }

    async def _technical_analysis(self, symbol: str) -> Dict:
        """技术面分析"""
        # 使用现有策略系统 + 技术指标

    async def _fundamental_analysis(self, symbol: str) -> Dict:
        """基本面分析"""
        # 财务指标、估值水平

    async def _sentiment_analysis(self, symbol: str) -> Dict:
        """情绪面分析"""
        # 基于公告、新闻、社交媒体

    async def _risk_analysis(self, symbol: str) -> Dict:
        """风险分析"""
        # 波动率、回撤、行业风险

    async def _generate_recommendation(self, symbol: str) -> Dict:
        """生成投资建议"""
        # 综合以上分析给出建议
```

#### 4.2 AI 集成 (可选)
如果用户有 LLM API 密钥，可以启用 AI 增强：

```python
# 配置文件 .env
ENABLE_AI_ANALYSIS=true
OPENAI_API_KEY=sk-xxx
# 或
ANTHROPIC_API_KEY=sk-ant-xxx
```

使用 LLM 进行：
- 公告内容摘要和解读
- 财报数据分析和洞察
- 技术形态描述和建议
- 综合投资建议生成

**时间估算**: 5-7 天 (包含 LLM 集成)

---

### Phase 5: 前端可视化增强 (优先级: P1)

**目标**: 参考 ValueCell 前端实现更丰富的可视化

**实施内容**:

#### 5.1 新增页面和组件
参考 ValueCell 的 React 组件结构，用 Vue 3 实现：

```
src/views/
├── Dashboard.vue                  # 仪表盘 (新)
│   ├── MarketOverview.vue        # 市场概览
│   ├── WatchlistQuick.vue        # 自选股快览
│   └── AlertSummary.vue          # 告警摘要
│
├── Analysis.vue                   # 智能分析 (新)
│   ├── StockAnalysis.vue         # 个股分析
│   ├── ComparisonAnalysis.vue    # 对比分析
│   └── IndustryAnalysis.vue      # 行业分析
│
└── Charts/                        # 图表组件
    ├── CandlestickChart.vue      # K线图 (增强)
    ├── SparklineChart.vue        # 迷你走势图 (新)
    ├── VolumeChart.vue           # 成交量图 (新)
    └── IndicatorChart.vue        # 指标图 (新)
```

#### 5.2 实时数据推送
使用 WebSocket 实现实时数据推送：

```javascript
// src/composables/useRealtimeData.js
export function useRealtimeData(symbol) {
  const ws = ref(null)
  const data = ref(null)

  const connect = () => {
    ws.value = new WebSocket(`ws://localhost:8000/ws/realtime/${symbol}`)
    ws.value.onmessage = (event) => {
      data.value = JSON.parse(event.data)
    }
  }

  return { data, connect }
}
```

#### 5.3 数据可视化增强
使用 ECharts 实现：
- 迷你走势图 (Sparkline) - 参考 ValueCell
- 热力图 (Heatmap) - 显示板块强弱
- 关系图 (Graph) - 显示关联股票
- 仪表盘 (Gauge) - 显示评分指标

**时间估算**: 4-5 天

---

## 📦 技术依赖

### 新增 Python 包
```bash
pip install \
    yfinance \           # 获取市场数据 (备用)
    websockets \         # WebSocket 支持
    schedule \           # 定时任务
    python-dateutil \    # 日期处理
    tenacity \           # 重试机制
    aiohttp \            # 异步 HTTP 客户端
    beautifulsoup4 \     # HTML 解析 (公告抓取)
    lxml                 # XML 解析
```

### 前端新增依赖
```bash
npm install \
    echarts \            # 数据可视化
    echarts-for-vue \    # Vue 集成
    reconnecting-websocket \  # WebSocket 重连
    dayjs                # 日期处理
```

### 可选依赖 (AI 功能)
```bash
pip install \
    openai \             # OpenAI API
    anthropic \          # Claude API
    langchain \          # LLM 框架
    chromadb             # 向量数据库 (如需要)
```

---

## 🔄 迁移策略

### 不直接迁移的内容
1. **Agno 框架**: 太重，暂不引入完整多智能体框架
2. **向量数据库**: 当前规模不需要，未来再考虑
3. **加密货币交易**: 仅专注 A 股市场
4. **纸面交易执行**: 仅做分析，不做实盘/模拟盘交易

### 适配性改造的内容
1. **SEC Agent → 公告监控**: 适配中国监管体系
2. **美股数据 → A股数据**: 使用 akshare 替代 yfinance
3. **多币种 → 人民币**: 简化货币处理
4. **多时区 → 东八区**: 统一时区处理

### 增量添加的内容
1. **龙虎榜监控**: A股特色功能
2. **涨跌停监控**: A股特色功能
3. **行业板块分析**: 增强行业维度
4. **资金流向分析**: A股常用指标

---

## 📈 实施优先级

### 🔴 P0 - 立即开始 (Phase 1)
- **实时监控和告警系统**
- 预计完成时间: 1 周
- 交付成果: 完整的告警系统，支持规则配置和实时推送

### 🟡 P1 - 近期实施 (Phase 2 & 3)
- **增强技术分析能力**
- **多数据源集成**
- 预计完成时间: 2 周
- 交付成果: 丰富的技术指标和多数据源支持

### 🟢 P2 - 中期规划 (Phase 4 & 5)
- **智能分析增强**
- **前端可视化增强**
- 预计完成时间: 2 周
- 交付成果: AI 驱动的分析和更好的用户体验

---

## ✅ 验收标准

### Phase 1 验收
- [ ] 能够创建和管理告警规则
- [ ] 实时监控至少 100 只股票无性能问题
- [ ] 触发告警时前端能实时收到通知
- [ ] 告警记录可查询和统计
- [ ] 支持龙虎榜数据抓取和展示

### Phase 2 验收
- [ ] 提供至少 20 个技术指标
- [ ] K 线图支持至少 5 个主图指标和 5 个副图指标
- [ ] 能够检测至少 5 种常见技术形态
- [ ] 技术分析响应时间 < 2 秒

### Phase 3 验收
- [ ] 至少集成 3 个数据源
- [ ] 数据源故障能自动降级
- [ ] 公告监控能覆盖沪深两市
- [ ] 公告能自动分类和评级

### Phase 4 验收
- [ ] 能生成个股综合分析报告
- [ ] 分析报告包含技术、基本面、情绪、风险 4 个维度
- [ ] 如启用 AI，能生成自然语言建议
- [ ] 分析完成时间 < 5 秒

### Phase 5 验收
- [ ] 新增仪表盘页面展示市场概况
- [ ] 支持实时数据推送 (WebSocket)
- [ ] 图表渲染流畅 (60 FPS)
- [ ] 响应式布局适配不同屏幕尺寸

---

## 🚀 后续规划

### 长期目标 (3-6 个月)
1. **完整多智能体系统**: 引入 LangChain/Agno 实现真正的多智能体协作
2. **向量数据库**: 添加 ChromaDB 支持知识检索
3. **回测系统**: 基于历史数据验证策略效果
4. **模拟交易**: 纸面交易系统验证策略
5. **移动端**: 开发 App 或响应式 H5 版本

### 持续优化
1. **性能优化**: 实时数据处理性能优化
2. **UI/UX**: 根据用户反馈持续改进交互
3. **数据质量**: 持续监控和改进数据准确性
4. **安全加固**: 加强 API 安全和数据保护

---

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- **项目仓库**: /opt/claude/mystocks_spec
- **文档位置**: VALUECELL_MIGRATION_PLAN.md
- **更新日期**: 2025-10-23

---

**注**: 本计划为初步规划，实施过程中会根据实际情况调整。每个 Phase 完成后会生成详细的实施报告。
