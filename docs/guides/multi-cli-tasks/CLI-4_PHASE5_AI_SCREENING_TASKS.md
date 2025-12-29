# CLI-4 任务分配：Phase 5 AI智能选股系统

**分配时间**: 2025-12-29
**预计工作量**: 10-12 工作日
**优先级**: Round 2 - 第一优先
**依赖**: CLI-3 完成 (需要161个指标数据)
**Worktree路径**: `/opt/claude/mystocks_phase5_ai_screening`
**分支**: `phase5-ai-screening`

---

## 📋 任务概览

### 核心目标
实现**问财式自然语言查询引擎** + **AI驱动的智能选股推荐系统**，支持用户通过自然语言查询股票，并获得AI分析后的推荐列表和实时告警。

### 关键交付物
1. **NLP查询引擎**: 自然语言 → 结构化查询条件
2. **9个预定义查询模板**: 常见选股场景快速查询
3. **AI推荐引擎**: 基于161指标的智能推荐算法
4. **实时告警系统**: 满足条件时推送通知
5. **前端UI组件**: 查询界面 + 推荐列表 + 告警中心

### 技术栈
- **NLP**: transformers (BERT中文模型), jieba分词
- **推荐算法**: scikit-learn, LightGBM, pandas
- **实时推送**: Server-Sent Events (SSE)
- **缓存**: Redis (查询结果缓存)
- **前端**: Vue 3 + TypeScript

---

## 🎯 分阶段任务列表

### **阶段1: NLP查询引擎 (Day 1-3)**

#### T4.1 设计查询语法和意图识别模型
**目标**: 定义自然语言查询语法和意图分类体系

**关键工作**:
1. **查询语法设计**:
   ```python
   # 查询语法示例
   "市盈率小于20且ROE大于15的股票"
   → {
       "filters": [
           {"field": "pe_ratio", "operator": "lt", "value": 20},
           {"field": "roe", "operator": "gt", "value": 15}
       ],
       "sort": None,
       "limit": 100
   }

   "涨停打开后成交量放大3倍"
   → {
       "filters": [
           {"field": "is_limit_up_broken", "operator": "eq", "value": True},
           {"field": "volume_ratio", "operator": "gte", "value": 3.0}
       ]
   }
   ```

2. **意图分类体系** (9大类):
   ```python
   from enum import Enum

   class QueryIntent(Enum):
       VALUE_SCREENING = "价值筛选"        # 基本面指标
       TECHNICAL_SCREENING = "技术筛选"   # 技术指标
       MOMENTUM_SCREENING = "动量筛选"    # 涨跌幅、成交量
       PATTERN_SCREENING = "形态筛选"     # K线形态
       SECTOR_SCREENING = "行业筛选"      # 行业板块
       MIXED_SCREENING = "综合筛选"       # 多条件组合
       RANKING_QUERY = "排行查询"         # 涨跌幅排行
       STOCK_DETAIL = "个股详情"          # 单只股票信息
       CUSTOM_FORMULA = "自定义公式"      # 复杂公式计算
   ```

3. **NER实体识别规则**:
   ```python
   # 识别查询中的实体
   entities = {
       "指标名": ["市盈率", "ROE", "MACD", "KDJ"],
       "比较运算符": ["大于", "小于", "等于", "介于"],
       "数值": [20, 15, 3.0],
       "时间范围": ["今天", "近3天", "本周", "本月"],
       "行业": ["医药", "科技", "金融"]
   }
   ```

**验收标准**:
- [ ] 查询语法文档完整 (覆盖9大查询场景)
- [ ] 意图分类准确率 > 90% (100个测试样本)
- [ ] NER实体识别召回率 > 85%

**预估时间**: 1天

---

#### T4.2 实现查询解析器 (NLP → 结构化查询)
**目标**: 将自然语言查询转换为结构化的数据库查询条件

**关键实现**:
```python
from typing import List, Dict, Optional
from pydantic import BaseModel
from transformers import BertTokenizer, BertForSequenceClassification
import jieba
import re

class StructuredQuery(BaseModel):
    """结构化查询对象"""
    intent: str                          # 查询意图
    filters: List[Dict[str, any]]        # 过滤条件
    sort_by: Optional[str] = None        # 排序字段
    sort_order: str = "desc"             # 排序方向
    limit: int = 100                     # 返回数量

class QueryParser:
    """自然语言查询解析器"""

    def __init__(self):
        # 加载BERT中文模型 (意图分类)
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')
        self.intent_classifier = BertForSequenceClassification.from_pretrained(
            'bert-base-chinese',
            num_labels=9  # 9种查询意图
        )

        # 加载自定义词典 (jieba分词)
        jieba.load_userdict('stock_indicators_dict.txt')

        # 指标映射表 (中文名 → 数据库字段)
        self.indicator_mapping = {
            "市盈率": "pe_ratio",
            "市净率": "pb_ratio",
            "ROE": "roe",
            "MACD": "macd",
            "KDJ": "kdj",
            "涨停": "is_limit_up",
            "成交量": "volume"
        }

        # 比较运算符映射
        self.operator_mapping = {
            "大于": "gt",
            "小于": "lt",
            "等于": "eq",
            "不等于": "ne",
            "大于等于": "gte",
            "小于等于": "lte",
            "介于": "between"
        }

    def parse(self, query_text: str) -> StructuredQuery:
        """解析自然语言查询"""
        # 1. 意图分类
        intent = self._classify_intent(query_text)

        # 2. 分词和实体识别
        tokens = list(jieba.cut(query_text))
        entities = self._extract_entities(tokens)

        # 3. 构建过滤条件
        filters = self._build_filters(entities)

        # 4. 提取排序和限制
        sort_by, sort_order = self._extract_sort(query_text)
        limit = self._extract_limit(query_text)

        return StructuredQuery(
            intent=intent,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit
        )

    def _classify_intent(self, text: str) -> str:
        """使用BERT模型分类查询意图"""
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        outputs = self.intent_classifier(**inputs)
        intent_id = outputs.logits.argmax().item()
        return QueryIntent(intent_id).name

    def _extract_entities(self, tokens: List[str]) -> Dict[str, List]:
        """提取查询实体 (指标、运算符、数值)"""
        entities = {"indicators": [], "operators": [], "values": []}

        for i, token in enumerate(tokens):
            # 识别指标
            if token in self.indicator_mapping:
                entities["indicators"].append({
                    "name": token,
                    "field": self.indicator_mapping[token],
                    "position": i
                })

            # 识别运算符
            if token in self.operator_mapping:
                entities["operators"].append({
                    "op": token,
                    "op_code": self.operator_mapping[token],
                    "position": i
                })

            # 识别数值
            if re.match(r'^-?\d+(\.\d+)?$', token):
                entities["values"].append({
                    "value": float(token),
                    "position": i
                })

        return entities

    def _build_filters(self, entities: Dict) -> List[Dict]:
        """根据实体构建过滤条件"""
        filters = []

        # 简单规则匹配: 指标 + 运算符 + 数值
        for i in range(len(entities["indicators"])):
            indicator = entities["indicators"][i]

            # 查找最近的运算符和数值
            op = self._find_nearest(entities["operators"], indicator["position"])
            val = self._find_nearest(entities["values"], indicator["position"])

            if op and val:
                filters.append({
                    "field": indicator["field"],
                    "operator": op["op_code"],
                    "value": val["value"]
                })

        return filters

    def _find_nearest(self, entity_list: List[Dict], position: int) -> Optional[Dict]:
        """查找最近的实体"""
        nearest = None
        min_distance = float('inf')

        for entity in entity_list:
            distance = abs(entity["position"] - position)
            if distance < min_distance:
                min_distance = distance
                nearest = entity

        return nearest

    def _extract_sort(self, text: str) -> tuple[Optional[str], str]:
        """提取排序条件"""
        if "涨幅最大" in text or "涨幅排名" in text:
            return "change_percent", "desc"
        if "跌幅最大" in text:
            return "change_percent", "asc"
        if "成交量最大" in text:
            return "volume", "desc"
        return None, "desc"

    def _extract_limit(self, text: str) -> int:
        """提取返回数量限制"""
        match = re.search(r'前(\d+)名|前(\d+)只|(\d+)只股票', text)
        if match:
            return int(match.group(1) or match.group(2) or match.group(3))
        return 100  # 默认100只
```

**验收标准**:
- [ ] 解析准确率 > 85% (200个测试查询)
- [ ] 处理速度 < 200ms (单次查询)
- [ ] 支持复杂组合条件 (AND/OR逻辑)

**预估时间**: 2天

---

#### T4.3 实现9个预定义查询模板
**目标**: 提供常见选股场景的快速查询模板

**预定义模板**:
```python
class QueryTemplates:
    """9个预定义查询模板"""

    @staticmethod
    def low_pe_high_roe() -> StructuredQuery:
        """模板1: 低市盈率高ROE (价值投资)"""
        return StructuredQuery(
            intent="VALUE_SCREENING",
            filters=[
                {"field": "pe_ratio", "operator": "lt", "value": 20},
                {"field": "roe", "operator": "gt", "value": 15},
                {"field": "pb_ratio", "operator": "lt", "value": 3}
            ],
            sort_by="roe",
            limit=50
        )

    @staticmethod
    def macd_golden_cross() -> StructuredQuery:
        """模板2: MACD金叉 (技术突破)"""
        return StructuredQuery(
            intent="TECHNICAL_SCREENING",
            filters=[
                {"field": "macd_signal", "operator": "eq", "value": "golden_cross"},
                {"field": "macd_histogram", "operator": "gt", "value": 0},
                {"field": "volume_ratio", "operator": "gt", "value": 1.5}
            ],
            sort_by="macd_histogram",
            limit=100
        )

    @staticmethod
    def limit_up_broken() -> StructuredQuery:
        """模板3: 涨停打开 (短线机会)"""
        return StructuredQuery(
            intent="MOMENTUM_SCREENING",
            filters=[
                {"field": "is_limit_up_broken", "operator": "eq", "value": True},
                {"field": "volume_ratio", "operator": "gte", "value": 3.0},
                {"field": "turnover_rate", "operator": "gt", "value": 5.0}
            ],
            sort_by="volume_ratio",
            limit=50
        )

    @staticmethod
    def three_crows_pattern() -> StructuredQuery:
        """模板4: 三只乌鸦形态 (顶部警示)"""
        return StructuredQuery(
            intent="PATTERN_SCREENING",
            filters=[
                {"field": "pattern_three_crows", "operator": "eq", "value": True},
                {"field": "rsi", "operator": "gt", "value": 70},  # 超买
                {"field": "volume_trend", "operator": "eq", "value": "increasing"}
            ],
            sort_by="rsi",
            limit=30
        )

    @staticmethod
    def high_volume_breakout() -> StructuredQuery:
        """模板5: 放量突破 (动量强劲)"""
        return StructuredQuery(
            intent="MOMENTUM_SCREENING",
            filters=[
                {"field": "is_breakout_high", "operator": "eq", "value": True},
                {"field": "volume_ratio", "operator": "gte", "value": 2.0},
                {"field": "change_percent", "operator": "gt", "value": 3.0}
            ],
            sort_by="volume_ratio",
            limit=50
        )

    @staticmethod
    def kdj_oversold_rebound() -> StructuredQuery:
        """模板6: KDJ超卖反弹 (抄底机会)"""
        return StructuredQuery(
            intent="TECHNICAL_SCREENING",
            filters=[
                {"field": "kdj_k", "operator": "lt", "value": 20},
                {"field": "kdj_d", "operator": "lt", "value": 20},
                {"field": "kdj_j", "operator": "gt", "value": "kdj_k"},  # J值上穿K值
                {"field": "rsi", "operator": "lt", "value": 30}
            ],
            sort_by="kdj_j",
            limit=50
        )

    @staticmethod
    def high_profit_growth() -> StructuredQuery:
        """模板7: 高盈利增长 (成长股)"""
        return StructuredQuery(
            intent="VALUE_SCREENING",
            filters=[
                {"field": "profit_growth_yoy", "operator": "gt", "value": 30},
                {"field": "revenue_growth_yoy", "operator": "gt", "value": 20},
                {"field": "pe_ratio", "operator": "lt", "value": 50}
            ],
            sort_by="profit_growth_yoy",
            limit=50
        )

    @staticmethod
    def sector_leader_ranking() -> StructuredQuery:
        """模板8: 行业龙头排名 (板块轮动)"""
        return StructuredQuery(
            intent="SECTOR_SCREENING",
            filters=[
                {"field": "market_cap_rank_in_sector", "operator": "lte", "value": 5},
                {"field": "turnover_rate", "operator": "gt", "value": 3.0}
            ],
            sort_by="change_percent",
            limit=100
        )

    @staticmethod
    def custom_momentum_value() -> StructuredQuery:
        """模板9: 动量+价值组合 (综合选股)"""
        return StructuredQuery(
            intent="MIXED_SCREENING",
            filters=[
                {"field": "ma5_gt_ma20", "operator": "eq", "value": True},
                {"field": "rsi", "operator": "between", "value": [40, 60]},
                {"field": "pe_ratio", "operator": "lt", "value": 30},
                {"field": "roe", "operator": "gt", "value": 10}
            ],
            sort_by="综合评分",  # 自定义评分公式
            limit=50
        )
```

**前端快速选择UI**:
```typescript
// web/frontend/src/components/AIScreening/TemplateSelector.vue
interface QueryTemplate {
  id: string;
  name: string;
  description: string;
  icon: string;
  execute: () => StructuredQuery;
}

const templates: QueryTemplate[] = [
  {
    id: 'low_pe_high_roe',
    name: '价值投资',
    description: '低市盈率 + 高ROE + 低市净率',
    icon: 'money-bag',
    execute: QueryTemplates.low_pe_high_roe
  },
  {
    id: 'macd_golden_cross',
    name: 'MACD金叉',
    description: 'MACD金叉 + 放量',
    icon: 'chart-line',
    execute: QueryTemplates.macd_golden_cross
  },
  // ... 其他7个模板
];
```

**验收标准**:
- [ ] 9个模板全部实现并测试通过
- [ ] 每个模板查询速度 < 3秒
- [ ] 前端UI支持一键选择模板

**预估时间**: 1天 (Day 3)

---

### **阶段2: AI推荐引擎 (Day 4-6)**

#### T4.4 设计推荐算法和评分模型
**目标**: 基于161个指标设计智能推荐算法

**推荐算法架构**:
```python
from typing import List, Dict
import pandas as pd
from sklearn.preprocessing import StandardScaler
from lightgbm import LGBMClassifier
import numpy as np

class StockRecommendationEngine:
    """股票推荐引擎"""

    def __init__(self):
        self.scaler = StandardScaler()
        self.model = LGBMClassifier(
            n_estimators=100,
            learning_rate=0.05,
            max_depth=5
        )
        self.feature_importance = {}

    def calculate_composite_score(
        self,
        stock_data: pd.DataFrame,
        weights: Dict[str, float]
    ) -> pd.Series:
        """计算综合评分 (加权多指标)"""

        # 5大维度评分
        scores = {
            "value_score": self._calculate_value_score(stock_data),      # 价值评分
            "growth_score": self._calculate_growth_score(stock_data),    # 成长评分
            "momentum_score": self._calculate_momentum_score(stock_data),# 动量评分
            "quality_score": self._calculate_quality_score(stock_data),  # 质量评分
            "technical_score": self._calculate_technical_score(stock_data)# 技术评分
        }

        # 加权求和
        composite_score = sum(
            scores[dim] * weights.get(dim, 0.2)
            for dim in scores
        )

        return composite_score

    def _calculate_value_score(self, df: pd.DataFrame) -> pd.Series:
        """价值评分 (PE/PB/PS/股息率)"""
        # 归一化处理 (越低越好)
        pe_norm = 1 / (1 + df['pe_ratio'] / 20)
        pb_norm = 1 / (1 + df['pb_ratio'] / 3)
        ps_norm = 1 / (1 + df['ps_ratio'] / 5)
        dividend_norm = df['dividend_yield'] / 10

        # 加权平均
        value_score = (
            pe_norm * 0.3 +
            pb_norm * 0.3 +
            ps_norm * 0.2 +
            dividend_norm * 0.2
        ) * 100

        return value_score

    def _calculate_growth_score(self, df: pd.DataFrame) -> pd.Series:
        """成长评分 (营收增长/利润增长/ROE)"""
        revenue_norm = df['revenue_growth_yoy'] / 50
        profit_norm = df['profit_growth_yoy'] / 50
        roe_norm = df['roe'] / 20

        growth_score = (
            revenue_norm * 0.3 +
            profit_norm * 0.4 +
            roe_norm * 0.3
        ) * 100

        return growth_score.clip(0, 100)

    def _calculate_momentum_score(self, df: pd.DataFrame) -> pd.Series:
        """动量评分 (涨跌幅/成交量/换手率)"""
        change_norm = (df['change_percent'] + 10) / 20  # [-10, 10] → [0, 1]
        volume_norm = df['volume_ratio'] / 5
        turnover_norm = df['turnover_rate'] / 10

        momentum_score = (
            change_norm * 0.4 +
            volume_norm * 0.3 +
            turnover_norm * 0.3
        ) * 100

        return momentum_score.clip(0, 100)

    def _calculate_quality_score(self, df: pd.DataFrame) -> pd.Series:
        """质量评分 (ROE/ROA/负债率/现金流)"""
        roe_norm = df['roe'] / 20
        roa_norm = df['roa'] / 10
        debt_norm = 1 - df['debt_ratio'] / 100
        cashflow_norm = df['operating_cashflow'] / df['revenue']

        quality_score = (
            roe_norm * 0.3 +
            roa_norm * 0.2 +
            debt_norm * 0.3 +
            cashflow_norm * 0.2
        ) * 100

        return quality_score.clip(0, 100)

    def _calculate_technical_score(self, df: pd.DataFrame) -> pd.Series:
        """技术评分 (MACD/KDJ/RSI/布林带)"""
        # MACD信号
        macd_score = np.where(df['macd_histogram'] > 0, 30, 0)

        # KDJ超卖反弹
        kdj_score = np.where(
            (df['kdj_k'] < 30) & (df['kdj_j'] > df['kdj_k']),
            30, 0
        )

        # RSI中性区间
        rsi_score = np.where(
            (df['rsi'] > 40) & (df['rsi'] < 60),
            20, 0
        )

        # 布林带位置
        boll_score = np.where(df['close'] > df['boll_mid'], 20, 0)

        technical_score = macd_score + kdj_score + rsi_score + boll_score

        return pd.Series(technical_score, index=df.index)
```

**机器学习模型训练** (可选增强):
```python
def train_recommendation_model(self, historical_data: pd.DataFrame):
    """训练LightGBM推荐模型"""

    # 特征工程: 161个指标 + 衍生特征
    features = self._engineer_features(historical_data)

    # 标签: 未来N天涨幅 > 10% 为正样本
    labels = (historical_data['future_return_5d'] > 10).astype(int)

    # 训练模型
    self.model.fit(features, labels)

    # 特征重要性
    self.feature_importance = dict(zip(
        features.columns,
        self.model.feature_importances_
    ))

    return self.model

def predict_recommendation_probability(self, stock_data: pd.DataFrame) -> pd.Series:
    """预测推荐概率 (0-1)"""
    features = self._engineer_features(stock_data)
    probabilities = self.model.predict_proba(features)[:, 1]
    return pd.Series(probabilities, index=stock_data.index)
```

**验收标准**:
- [ ] 综合评分模型实现并测试
- [ ] 评分与实际收益相关性 > 0.3 (回测验证)
- [ ] 机器学习模型AUC > 0.65 (可选)

**预估时间**: 2天

---

#### T4.5 实现推荐API端点
**目标**: 提供推荐接口供前端调用

**API端点实现**:
```python
from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/api/ai-screening", tags=["AI筛选"])

class RecommendationRequest(BaseModel):
    """推荐请求"""
    strategy: str = "balanced"  # balanced/value/growth/momentum
    top_n: int = 50
    sector_filter: Optional[List[str]] = None
    min_score: float = 60.0

class StockRecommendation(BaseModel):
    """推荐结果"""
    symbol: str
    name: str
    composite_score: float
    value_score: float
    growth_score: float
    momentum_score: float
    quality_score: float
    technical_score: float
    recommendation_reason: str
    risk_level: str  # low/medium/high

@router.post("/recommendations", response_model=List[StockRecommendation])
async def get_recommendations(request: RecommendationRequest):
    """获取AI推荐股票列表"""

    # 1. 获取所有股票数据 (包含161个指标)
    all_stocks = await fetch_all_stocks_with_indicators()

    # 2. 应用行业过滤
    if request.sector_filter:
        all_stocks = all_stocks[all_stocks['sector'].isin(request.sector_filter)]

    # 3. 计算综合评分
    engine = StockRecommendationEngine()
    weights = STRATEGY_WEIGHTS[request.strategy]  # 不同策略的权重配置

    all_stocks['composite_score'] = engine.calculate_composite_score(
        all_stocks,
        weights
    )

    # 4. 过滤和排序
    recommendations = all_stocks[
        all_stocks['composite_score'] >= request.min_score
    ].nlargest(request.top_n, 'composite_score')

    # 5. 生成推荐理由
    recommendations['recommendation_reason'] = recommendations.apply(
        lambda row: generate_recommendation_reason(row),
        axis=1
    )

    # 6. 风险评级
    recommendations['risk_level'] = recommendations.apply(
        lambda row: calculate_risk_level(row),
        axis=1
    )

    return recommendations.to_dict('records')

# 策略权重配置
STRATEGY_WEIGHTS = {
    "balanced": {
        "value_score": 0.2,
        "growth_score": 0.2,
        "momentum_score": 0.2,
        "quality_score": 0.2,
        "technical_score": 0.2
    },
    "value": {
        "value_score": 0.4,
        "growth_score": 0.1,
        "momentum_score": 0.1,
        "quality_score": 0.3,
        "technical_score": 0.1
    },
    "growth": {
        "value_score": 0.1,
        "growth_score": 0.5,
        "momentum_score": 0.2,
        "quality_score": 0.1,
        "technical_score": 0.1
    },
    "momentum": {
        "value_score": 0.1,
        "growth_score": 0.1,
        "momentum_score": 0.5,
        "quality_score": 0.1,
        "technical_score": 0.3
    }
}

def generate_recommendation_reason(row: pd.Series) -> str:
    """生成推荐理由"""
    reasons = []

    if row['value_score'] > 80:
        reasons.append(f"估值合理 (PE: {row['pe_ratio']:.1f})")
    if row['growth_score'] > 80:
        reasons.append(f"高成长 (利润增长: {row['profit_growth_yoy']:.1f}%)")
    if row['momentum_score'] > 80:
        reasons.append(f"动量强劲 (涨幅: {row['change_percent']:.2f}%)")
    if row['macd_signal'] == 'golden_cross':
        reasons.append("MACD金叉")
    if row['kdj_k'] < 30 and row['kdj_j'] > row['kdj_k']:
        reasons.append("KDJ超卖反弹")

    return " | ".join(reasons) if reasons else "综合评分优秀"

def calculate_risk_level(row: pd.Series) -> str:
    """计算风险等级"""
    risk_score = (
        row['volatility'] * 0.4 +
        row['debt_ratio'] * 0.3 +
        row['beta'] * 0.3
    )

    if risk_score < 30:
        return "low"
    elif risk_score < 60:
        return "medium"
    else:
        return "high"
```

**查询缓存优化**:
```python
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

@router.post("/recommendations")
async def get_recommendations_cached(request: RecommendationRequest):
    """带缓存的推荐接口"""

    # 生成缓存键
    cache_key = f"recommendations:{request.strategy}:{request.top_n}:{request.min_score}"

    # 尝试从缓存读取
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # 计算推荐
    recommendations = await get_recommendations(request)

    # 写入缓存 (5分钟过期)
    redis_client.setex(cache_key, 300, json.dumps(recommendations))

    return recommendations
```

**验收标准**:
- [ ] API端点正常运行
- [ ] 响应时间 < 3秒 (带缓存 < 500ms)
- [ ] 支持4种推荐策略
- [ ] 返回数据包含评分和推荐理由

**预估时间**: 1天

---

#### T4.6 实现前端推荐列表UI
**目标**: 展示AI推荐结果的前端界面

**核心组件**:
```typescript
// web/frontend/src/components/AIScreening/RecommendationList.vue
<template>
  <div class="recommendation-container">
    <!-- 策略选择器 -->
    <div class="strategy-selector">
      <el-radio-group v-model="selectedStrategy" @change="fetchRecommendations">
        <el-radio-button label="balanced">均衡策略</el-radio-button>
        <el-radio-button label="value">价值策略</el-radio-button>
        <el-radio-button label="growth">成长策略</el-radio-button>
        <el-radio-button label="momentum">动量策略</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 推荐列表 -->
    <el-table :data="recommendations" v-loading="loading">
      <el-table-column prop="symbol" label="代码" width="100" />
      <el-table-column prop="name" label="名称" width="120" />

      <!-- 综合评分 (带颜色渐变) -->
      <el-table-column label="综合评分" width="120">
        <template #default="{ row }">
          <el-progress
            :percentage="row.composite_score"
            :color="getScoreColor(row.composite_score)"
          />
        </template>
      </el-table-column>

      <!-- 五维雷达图预览 -->
      <el-table-column label="五维分析" width="200">
        <template #default="{ row }">
          <mini-radar-chart :scores="{
            value: row.value_score,
            growth: row.growth_score,
            momentum: row.momentum_score,
            quality: row.quality_score,
            technical: row.technical_score
          }" />
        </template>
      </el-table-column>

      <!-- 推荐理由 -->
      <el-table-column prop="recommendation_reason" label="推荐理由" min-width="300" />

      <!-- 风险等级 -->
      <el-table-column label="风险" width="100">
        <template #default="{ row }">
          <el-tag :type="getRiskTagType(row.risk_level)">
            {{ getRiskLabel(row.risk_level) }}
          </el-tag>
        </template>
      </el-table-column>

      <!-- 操作 -->
      <el-table-column label="操作" width="150">
        <template #default="{ row }">
          <el-button size="small" @click="viewDetail(row)">详情</el-button>
          <el-button size="small" type="primary" @click="addToWatchlist(row)">
            加自选
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';

const selectedStrategy = ref('balanced');
const recommendations = ref([]);
const loading = ref(false);

const fetchRecommendations = async () => {
  loading.value = true;
  try {
    const response = await axios.post('/api/ai-screening/recommendations', {
      strategy: selectedStrategy.value,
      top_n: 50,
      min_score: 60.0
    });
    recommendations.value = response.data;
  } finally {
    loading.value = false;
  }
};

const getScoreColor = (score: number) => {
  if (score >= 80) return '#67C23A';  // 绿色
  if (score >= 60) return '#E6A23C';  // 橙色
  return '#F56C6C';  // 红色
};

const getRiskTagType = (level: string) => {
  const map = { low: 'success', medium: 'warning', high: 'danger' };
  return map[level] || 'info';
};

const getRiskLabel = (level: string) => {
  const map = { low: '低风险', medium: '中风险', high: '高风险' };
  return map[level] || '未知';
};

onMounted(fetchRecommendations);
</script>
```

**Mini雷达图组件** (五维分析):
```typescript
// web/frontend/src/components/AIScreening/MiniRadarChart.vue
<template>
  <div ref="chartRef" style="width: 180px; height: 120px;"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import * as echarts from 'echarts';

const props = defineProps<{
  scores: {
    value: number;
    growth: number;
    momentum: number;
    quality: number;
    technical: number;
  };
}>();

const chartRef = ref<HTMLElement>();
let chartInstance: echarts.ECharts;

const initChart = () => {
  chartInstance = echarts.init(chartRef.value!);

  const option = {
    radar: {
      indicator: [
        { name: '价值', max: 100 },
        { name: '成长', max: 100 },
        { name: '动量', max: 100 },
        { name: '质量', max: 100 },
        { name: '技术', max: 100 }
      ],
      radius: '60%'
    },
    series: [{
      type: 'radar',
      data: [{
        value: [
          props.scores.value,
          props.scores.growth,
          props.scores.momentum,
          props.scores.quality,
          props.scores.technical
        ],
        areaStyle: {
          color: 'rgba(103, 194, 58, 0.2)'
        }
      }]
    }]
  };

  chartInstance.setOption(option);
};

onMounted(initChart);
watch(() => props.scores, initChart, { deep: true });
</script>
```

**验收标准**:
- [ ] 推荐列表正常显示
- [ ] 支持4种策略切换
- [ ] 五维雷达图正常渲染
- [ ] 点击加自选功能正常

**预估时间**: 1天

---

### **阶段3: 实时告警系统 (Day 7-9)**

#### T4.7 设计告警规则引擎
**目标**: 支持用户自定义告警条件和多渠道推送

**告警规则数据模型**:
```python
from pydantic import BaseModel
from typing import List, Dict, Optional
from enum import Enum

class AlertTriggerType(Enum):
    """告警触发类型"""
    PRICE_THRESHOLD = "价格阈值"
    INDICATOR_SIGNAL = "指标信号"
    RECOMMENDATION_UPDATE = "推荐更新"
    PATTERN_DETECTED = "形态识别"

class AlertChannel(Enum):
    """告警渠道"""
    WEB_NOTIFICATION = "网页通知"
    EMAIL = "邮件"
    WEBHOOK = "Webhook"
    SMS = "短信"  # 可选

class AlertRule(BaseModel):
    """告警规则"""
    id: str
    user_id: str
    name: str
    trigger_type: AlertTriggerType
    conditions: List[Dict[str, any]]  # 触发条件
    channels: List[AlertChannel]
    is_active: bool = True
    created_at: datetime

    # 示例条件格式
    # [
    #   {"field": "close", "operator": "gt", "value": 50.0},
    #   {"field": "macd_signal", "operator": "eq", "value": "golden_cross"}
    # ]

class AlertEvent(BaseModel):
    """告警事件"""
    id: str
    rule_id: str
    symbol: str
    trigger_data: Dict[str, any]
    message: str
    severity: str  # info/warning/critical
    timestamp: datetime
    is_read: bool = False
```

**告警规则引擎**:
```python
class AlertRuleEngine:
    """告警规则引擎"""

    def __init__(self):
        self.active_rules = []
        self.alert_history = []

    def add_rule(self, rule: AlertRule):
        """添加告警规则"""
        self.active_rules.append(rule)
        # 持久化到数据库
        save_alert_rule_to_db(rule)

    def check_rules(self, stock_data: pd.DataFrame):
        """检查所有告警规则"""
        triggered_events = []

        for rule in self.active_rules:
            if not rule.is_active:
                continue

            # 评估每只股票是否满足条件
            for _, stock in stock_data.iterrows():
                if self._evaluate_conditions(stock, rule.conditions):
                    event = self._create_alert_event(rule, stock)
                    triggered_events.append(event)
                    self._send_alert(event, rule.channels)

        return triggered_events

    def _evaluate_conditions(self, stock: pd.Series, conditions: List[Dict]) -> bool:
        """评估告警条件 (AND逻辑)"""
        for condition in conditions:
            field = condition['field']
            operator = condition['operator']
            value = condition['value']

            stock_value = stock.get(field)

            if operator == 'gt' and not (stock_value > value):
                return False
            elif operator == 'lt' and not (stock_value < value):
                return False
            elif operator == 'eq' and not (stock_value == value):
                return False
            elif operator == 'between':
                if not (value[0] <= stock_value <= value[1]):
                    return False

        return True

    def _create_alert_event(self, rule: AlertRule, stock: pd.Series) -> AlertEvent:
        """创建告警事件"""
        return AlertEvent(
            id=generate_uuid(),
            rule_id=rule.id,
            symbol=stock['symbol'],
            trigger_data=stock.to_dict(),
            message=self._generate_alert_message(rule, stock),
            severity=self._calculate_severity(rule, stock),
            timestamp=datetime.now()
        )

    def _generate_alert_message(self, rule: AlertRule, stock: pd.Series) -> str:
        """生成告警消息"""
        if rule.trigger_type == AlertTriggerType.PRICE_THRESHOLD:
            return f"【价格告警】{stock['name']}({stock['symbol']}) 当前价格 {stock['close']:.2f} 元"

        elif rule.trigger_type == AlertTriggerType.INDICATOR_SIGNAL:
            return f"【指标信号】{stock['name']}({stock['symbol']}) {rule.conditions[0]['field']} 触发条件"

        elif rule.trigger_type == AlertTriggerType.RECOMMENDATION_UPDATE:
            return f"【AI推荐】{stock['name']}({stock['symbol']}) 新增AI推荐 (评分: {stock['composite_score']:.1f})"

        return f"【告警】{rule.name} 触发"

    def _calculate_severity(self, rule: AlertRule, stock: pd.Series) -> str:
        """计算告警严重程度"""
        if rule.trigger_type == AlertTriggerType.PRICE_THRESHOLD:
            change = abs(stock['change_percent'])
            if change > 9:
                return "critical"
            elif change > 5:
                return "warning"

        return "info"

    def _send_alert(self, event: AlertEvent, channels: List[AlertChannel]):
        """发送告警通知"""
        for channel in channels:
            if channel == AlertChannel.WEB_NOTIFICATION:
                self._send_web_notification(event)
            elif channel == AlertChannel.EMAIL:
                self._send_email(event)
            elif channel == AlertChannel.WEBHOOK:
                self._send_webhook(event)

    def _send_web_notification(self, event: AlertEvent):
        """发送网页通知 (通过SSE推送)"""
        sse_manager.broadcast({
            "type": "alert",
            "data": event.dict()
        })

    def _send_email(self, event: AlertEvent):
        """发送邮件告警"""
        # 使用SMTP发送邮件
        pass

    def _send_webhook(self, event: AlertEvent):
        """发送Webhook回调"""
        # POST请求到用户配置的webhook URL
        pass
```

**验收标准**:
- [ ] 支持4种触发类型
- [ ] 支持3种推送渠道 (网页/邮件/Webhook)
- [ ] 告警延迟 < 10秒

**预估时间**: 2天

---

#### T4.8 实现SSE实时推送
**目标**: 使用Server-Sent Events推送实时告警到前端

**后端SSE实现**:
```python
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
import asyncio
import json

router = APIRouter(prefix="/api/alerts", tags=["告警"])

class SSEManager:
    """SSE连接管理器"""

    def __init__(self):
        self.connections = {}  # user_id -> queue

    def add_connection(self, user_id: str, queue: asyncio.Queue):
        """添加SSE连接"""
        self.connections[user_id] = queue

    def remove_connection(self, user_id: str):
        """移除SSE连接"""
        if user_id in self.connections:
            del self.connections[user_id]

    async def send_to_user(self, user_id: str, message: dict):
        """发送消息给特定用户"""
        if user_id in self.connections:
            await self.connections[user_id].put(message)

    def broadcast(self, message: dict):
        """广播消息给所有连接"""
        for user_id in self.connections:
            asyncio.create_task(self.send_to_user(user_id, message))

sse_manager = SSEManager()

@router.get("/stream")
async def alert_stream(user_id: str):
    """SSE告警推送端点"""

    async def event_generator() -> AsyncGenerator[str, None]:
        queue = asyncio.Queue()
        sse_manager.add_connection(user_id, queue)

        try:
            # 发送初始连接消息
            yield f"data: {json.dumps({'type': 'connected', 'message': 'SSE连接成功'})}\n\n"

            # 持续推送告警事件
            while True:
                message = await queue.get()
                yield f"data: {json.dumps(message)}\n\n"

        except asyncio.CancelledError:
            sse_manager.remove_connection(user_id)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

# 后台任务: 定期检查告警规则
@router.on_event("startup")
async def start_alert_checker():
    """启动告警检查后台任务"""
    asyncio.create_task(alert_checker_loop())

async def alert_checker_loop():
    """告警检查循环 (每30秒检查一次)"""
    engine = AlertRuleEngine()

    while True:
        try:
            # 获取最新股票数据
            stock_data = await fetch_latest_stock_data()

            # 检查告警规则
            triggered_events = engine.check_rules(stock_data)

            # 推送到前端 (已在engine._send_alert中处理)

        except Exception as e:
            logger.error(f"告警检查失败: {e}")

        await asyncio.sleep(30)  # 每30秒检查一次
```

**前端SSE接收**:
```typescript
// web/frontend/src/composables/useAlertStream.ts
import { ref, onMounted, onUnmounted } from 'vue';
import { ElNotification } from 'element-plus';

export function useAlertStream(userId: string) {
  const alerts = ref<any[]>([]);
  let eventSource: EventSource | null = null;

  const connect = () => {
    eventSource = new EventSource(`/api/alerts/stream?user_id=${userId}`);

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'alert') {
        alerts.value.unshift(data.data);

        // 弹出通知
        ElNotification({
          title: data.data.severity === 'critical' ? '🚨 重要告警' : '📢 提醒',
          message: data.data.message,
          type: data.data.severity === 'critical' ? 'error' : 'info',
          duration: 0,  // 不自动关闭
          position: 'top-right'
        });

        // 播放提示音
        if (data.data.severity === 'critical') {
          playAlertSound();
        }
      }
    };

    eventSource.onerror = () => {
      console.error('SSE连接断开,5秒后重连...');
      setTimeout(connect, 5000);
    };
  };

  onMounted(connect);
  onUnmounted(() => {
    eventSource?.close();
  });

  return { alerts };
}

function playAlertSound() {
  const audio = new Audio('/sounds/alert.mp3');
  audio.play();
}
```

**验收标准**:
- [ ] SSE连接稳定 (断线自动重连)
- [ ] 告警推送延迟 < 5秒
- [ ] 前端弹窗通知正常显示
- [ ] 支持浏览器通知API (可选)

**预估时间**: 1天

---

#### T4.9 实现告警中心UI
**目标**: 用户管理告警规则和查看告警历史

**告警中心页面**:
```typescript
// web/frontend/src/views/AIScreening/AlertCenter.vue
<template>
  <div class="alert-center">
    <el-tabs v-model="activeTab">
      <!-- Tab 1: 告警规则管理 -->
      <el-tab-pane label="我的规则" name="rules">
        <el-button type="primary" @click="showCreateRuleDialog = true">
          + 创建告警规则
        </el-button>

        <el-table :data="alertRules" class="mt-4">
          <el-table-column prop="name" label="规则名称" />
          <el-table-column prop="trigger_type" label="触发类型" />
          <el-table-column label="条件" min-width="300">
            <template #default="{ row }">
              <el-tag v-for="cond in row.conditions" :key="cond.field" class="mr-2">
                {{ cond.field }} {{ getOperatorLabel(cond.operator) }} {{ cond.value }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-switch v-model="row.is_active" @change="toggleRule(row)" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150">
            <template #default="{ row }">
              <el-button size="small" @click="editRule(row)">编辑</el-button>
              <el-button size="small" type="danger" @click="deleteRule(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- Tab 2: 告警历史 -->
      <el-tab-pane label="告警历史" name="history">
        <el-timeline>
          <el-timeline-item
            v-for="alert in alertHistory"
            :key="alert.id"
            :timestamp="formatTime(alert.timestamp)"
            :type="getSeverityType(alert.severity)"
          >
            <el-card>
              <h4>{{ alert.message }}</h4>
              <p>触发规则: {{ alert.rule_name }}</p>
              <p>股票: {{ alert.symbol }} | 评分: {{ alert.trigger_data.composite_score }}</p>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </el-tab-pane>
    </el-tabs>

    <!-- 创建规则对话框 -->
    <el-dialog v-model="showCreateRuleDialog" title="创建告警规则" width="600px">
      <el-form :model="newRule" label-width="100px">
        <el-form-item label="规则名称">
          <el-input v-model="newRule.name" placeholder="如: MACD金叉告警" />
        </el-form-item>

        <el-form-item label="触发类型">
          <el-select v-model="newRule.trigger_type">
            <el-option label="价格阈值" value="PRICE_THRESHOLD" />
            <el-option label="指标信号" value="INDICATOR_SIGNAL" />
            <el-option label="推荐更新" value="RECOMMENDATION_UPDATE" />
            <el-option label="形态识别" value="PATTERN_DETECTED" />
          </el-select>
        </el-form-item>

        <el-form-item label="触发条件">
          <div v-for="(cond, idx) in newRule.conditions" :key="idx" class="condition-row">
            <el-select v-model="cond.field" placeholder="选择指标">
              <el-option label="价格" value="close" />
              <el-option label="涨跌幅" value="change_percent" />
              <el-option label="MACD信号" value="macd_signal" />
              <el-option label="KDJ K值" value="kdj_k" />
              <el-option label="综合评分" value="composite_score" />
            </el-select>

            <el-select v-model="cond.operator">
              <el-option label="大于" value="gt" />
              <el-option label="小于" value="lt" />
              <el-option label="等于" value="eq" />
              <el-option label="介于" value="between" />
            </el-select>

            <el-input-number v-model="cond.value" :precision="2" />

            <el-button
              type="danger"
              icon="Delete"
              @click="newRule.conditions.splice(idx, 1)"
            />
          </div>
          <el-button @click="addCondition">+ 添加条件</el-button>
        </el-form-item>

        <el-form-item label="推送渠道">
          <el-checkbox-group v-model="newRule.channels">
            <el-checkbox label="WEB_NOTIFICATION">网页通知</el-checkbox>
            <el-checkbox label="EMAIL">邮件</el-checkbox>
            <el-checkbox label="WEBHOOK">Webhook</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateRuleDialog = false">取消</el-button>
        <el-button type="primary" @click="createRule">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';

const activeTab = ref('rules');
const alertRules = ref([]);
const alertHistory = ref([]);
const showCreateRuleDialog = ref(false);

const newRule = ref({
  name: '',
  trigger_type: 'INDICATOR_SIGNAL',
  conditions: [{ field: '', operator: 'gt', value: 0 }],
  channels: ['WEB_NOTIFICATION']
});

const fetchAlertRules = async () => {
  const response = await axios.get('/api/alerts/rules');
  alertRules.value = response.data;
};

const fetchAlertHistory = async () => {
  const response = await axios.get('/api/alerts/history');
  alertHistory.value = response.data;
};

const createRule = async () => {
  await axios.post('/api/alerts/rules', newRule.value);
  showCreateRuleDialog.value = false;
  await fetchAlertRules();
};

const addCondition = () => {
  newRule.value.conditions.push({ field: '', operator: 'gt', value: 0 });
};

onMounted(() => {
  fetchAlertRules();
  fetchAlertHistory();
});
</script>
```

**验收标准**:
- [ ] 支持创建、编辑、删除告警规则
- [ ] 告警历史正常显示
- [ ] 规则开关立即生效

**预估时间**: 1天

---

### **阶段4: 集成测试与优化 (Day 10-12)**

#### T4.10 端到端集成测试
**目标**: 验证完整流程: 查询 → 推荐 → 告警

**测试用例**:
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_query_parser_accuracy():
    """测试查询解析准确率"""
    test_cases = [
        {
            "query": "市盈率小于20且ROE大于15的股票",
            "expected": {
                "filters": [
                    {"field": "pe_ratio", "operator": "lt", "value": 20},
                    {"field": "roe", "operator": "gt", "value": 15}
                ]
            }
        },
        {
            "query": "MACD金叉且成交量放大3倍",
            "expected": {
                "filters": [
                    {"field": "macd_signal", "operator": "eq", "value": "golden_cross"},
                    {"field": "volume_ratio", "operator": "gte", "value": 3.0}
                ]
            }
        }
    ]

    for case in test_cases:
        response = client.post("/api/ai-screening/parse-query", json={"query": case["query"]})
        assert response.status_code == 200
        result = response.json()
        assert result["filters"] == case["expected"]["filters"]

def test_recommendation_api_performance():
    """测试推荐API性能"""
    import time

    start = time.time()
    response = client.post("/api/ai-screening/recommendations", json={
        "strategy": "balanced",
        "top_n": 50
    })
    elapsed = time.time() - start

    assert response.status_code == 200
    assert elapsed < 3.0  # 3秒内返回
    assert len(response.json()) <= 50

def test_alert_trigger_and_push():
    """测试告警触发和推送"""
    # 创建告警规则
    rule = {
        "name": "测试MACD金叉告警",
        "trigger_type": "INDICATOR_SIGNAL",
        "conditions": [
            {"field": "macd_signal", "operator": "eq", "value": "golden_cross"}
        ],
        "channels": ["WEB_NOTIFICATION"]
    }

    response = client.post("/api/alerts/rules", json=rule)
    assert response.status_code == 200
    rule_id = response.json()["id"]

    # 模拟触发条件
    # ... (后续实现)

    # 验证告警事件生成
    events = client.get(f"/api/alerts/history?rule_id={rule_id}").json()
    assert len(events) > 0

def test_end_to_end_workflow():
    """端到端测试: 自然语言查询 → AI推荐 → 告警"""
    # 1. 用户输入自然语言查询
    query_response = client.post("/api/ai-screening/parse-query", json={
        "query": "MACD金叉且KDJ超卖的股票"
    })
    assert query_response.status_code == 200

    # 2. 获取AI推荐
    structured_query = query_response.json()
    rec_response = client.post("/api/ai-screening/recommendations", json={
        "strategy": "momentum",
        "filters": structured_query["filters"]
    })
    assert rec_response.status_code == 200
    recommendations = rec_response.json()
    assert len(recommendations) > 0

    # 3. 设置告警规则 (当推荐更新时通知)
    alert_response = client.post("/api/alerts/rules", json={
        "name": "AI推荐更新告警",
        "trigger_type": "RECOMMENDATION_UPDATE",
        "conditions": [
            {"field": "composite_score", "operator": "gt", "value": 80}
        ],
        "channels": ["WEB_NOTIFICATION"]
    })
    assert alert_response.status_code == 200
```

**性能基准测试**:
```bash
# 使用Locust进行压力测试
locust -f tests/load_test.py --host=http://localhost:8000
```

**验收标准**:
- [ ] 所有测试用例通过 (覆盖率 > 80%)
- [ ] API响应时间达标 (查询<200ms, 推荐<3s, 告警<10s)
- [ ] 压力测试通过 (100并发用户)

**预估时间**: 2天

---

#### T4.11 前端性能优化
**目标**: 优化页面加载和渲染性能

**优化措施**:
1. **虚拟滚动** (大列表优化):
```typescript
// 使用 vue-virtual-scroller 优化推荐列表
<template>
  <RecycleScroller
    :items="recommendations"
    :item-size="80"
    key-field="symbol"
  >
    <template #default="{ item }">
      <recommendation-card :stock="item" />
    </template>
  </RecycleScroller>
</template>
```

2. **懒加载雷达图**:
```typescript
// 只在可见区域渲染雷达图
import { useIntersectionObserver } from '@vueuse/core';

const chartRef = ref<HTMLElement>();
const isVisible = ref(false);

useIntersectionObserver(chartRef, ([{ isIntersecting }]) => {
  if (isIntersecting && !isVisible.value) {
    isVisible.value = true;
    initChart();
  }
});
```

3. **缓存推荐结果**:
```typescript
// 使用IndexedDB缓存推荐数据 (5分钟)
import { useIndexedDB } from '@vueuse/integrations/useIndexedDB';

const { data, update } = useIndexedDB('recommendations_cache', 'balanced_50');

const fetchWithCache = async () => {
  if (data.value && Date.now() - data.value.timestamp < 300000) {
    return data.value.recommendations;
  }

  const fresh = await axios.post('/api/ai-screening/recommendations', {...});
  await update({ recommendations: fresh.data, timestamp: Date.now() });
  return fresh.data;
};
```

**验收标准**:
- [ ] 推荐列表渲染 < 1秒 (1000条数据)
- [ ] Lighthouse性能评分 > 90
- [ ] 缓存命中率 > 60%

**预估时间**: 1天

---

## 📊 进度跟踪与验收

### 里程碑检查点

| 里程碑 | 时间节点 | 验收标准 |
|--------|---------|---------|
| M1: NLP查询引擎完成 | Day 3 | 解析准确率>85%, 9个模板全部可用 |
| M2: AI推荐引擎上线 | Day 6 | 推荐API正常, 前端UI完整, 评分准确 |
| M3: 实时告警系统可用 | Day 9 | SSE推送稳定, 告警延迟<10s |
| M4: 集成测试通过 | Day 12 | 测试覆盖率>80%, 性能达标 |

### 每日验收检查清单

**Day 1-3 (NLP引擎)**:
- [ ] 查询语法文档完成
- [ ] 意图分类准确率>90%
- [ ] QueryParser实现并测试
- [ ] 9个模板全部可用

**Day 4-6 (推荐引擎)**:
- [ ] 综合评分模型实现
- [ ] 推荐API端点正常
- [ ] 前端推荐列表UI完成
- [ ] 五维雷达图正常渲染

**Day 7-9 (告警系统)**:
- [ ] 告警规则引擎实现
- [ ] SSE推送功能正常
- [ ] 告警中心UI完成
- [ ] 多渠道推送测试通过

**Day 10-12 (集成优化)**:
- [ ] 端到端测试通过
- [ ] 性能优化完成
- [ ] 文档更新完整

---

## 🔗 依赖关系

### 上游依赖
- **CLI-3 (Phase 4)**: 提供161个技术指标数据 (T3.5-T3.8)
- **CLI-2 (API契约)**: 提供统一API响应格式和错误码 (T2.1-T2.7)

### 下游影响
- **CLI-6 (质量保证)**: 需要AI推荐API的测试用例 (Week 2)
- **前端Phase 5页面**: 需要AI筛选组件集成 (Week 3)

### 数据流依赖
```
TDengine (高频数据) + PostgreSQL (日线/指标缓存)
    ↓
CLI-3 (161指标计算)
    ↓
CLI-4 (AI推荐引擎) → 评分 + 排序 + 告警
    ↓
前端UI (推荐列表 + 告警中心)
```

---

## 📝 交付清单

### 代码交付
- [ ] `src/ai_screening/` - 后端AI筛选模块
  - `query_parser.py` - 查询解析器
  - `recommendation_engine.py` - 推荐引擎
  - `alert_engine.py` - 告警引擎
  - `sse_manager.py` - SSE推送管理器
- [ ] `web/frontend/src/views/AIScreening/` - 前端页面
  - `NaturalQueryInput.vue` - 自然语言查询输入
  - `TemplateSelector.vue` - 查询模板选择器
  - `RecommendationList.vue` - 推荐列表
  - `AlertCenter.vue` - 告警中心
- [ ] `tests/ai_screening/` - 测试用例
  - `test_query_parser.py` - 查询解析测试
  - `test_recommendation_engine.py` - 推荐引擎测试
  - `test_alert_engine.py` - 告警引擎测试

### 文档交付
- [ ] `docs/ai_screening/AI_SCREENING_ARCHITECTURE.md` - 架构设计文档
- [ ] `docs/ai_screening/QUERY_SYNTAX_GUIDE.md` - 查询语法指南
- [ ] `docs/ai_screening/RECOMMENDATION_ALGORITHM.md` - 推荐算法说明
- [ ] `docs/ai_screening/ALERT_RULE_EXAMPLES.md` - 告警规则示例
- [ ] `README_CLI4.md` - CLI-4完成报告

---

## 🎯 成功标准

### 功能完整性
- [x] 自然语言查询准确率 > 85%
- [x] 9个预定义模板全部可用
- [x] AI推荐API响应时间 < 3秒
- [x] 告警推送延迟 < 10秒
- [x] SSE连接稳定 (断线自动重连)

### 性能指标
- [x] 查询解析速度 < 200ms
- [x] 推荐计算速度 < 3秒 (100只股票)
- [x] 告警检查周期 = 30秒
- [x] 前端列表渲染 < 1秒 (1000条)

### 质量标准
- [x] 测试覆盖率 > 80%
- [x] 代码Review通过
- [x] 文档完整无遗漏
- [x] 性能基准测试通过

---

## ⚠️ 风险提示

### 技术风险
1. **NLP模型准确率不足** → 备选方案: 基于规则的模板匹配
2. **推荐算法效果差** → 增加用户反馈机制,持续优化权重
3. **SSE推送稳定性问题** → 备选WebSocket或轮询方案

### 依赖风险
1. **CLI-3未按时交付** → 使用Mock数据先行开发UI
2. **161指标计算性能不达标** → 优先实现核心30个指标

---

**最后更新**: 2025-12-29
**责任人**: CLI-4 Worker (Phase 5 AI Screening)
**预计完成**: 2025-01-09 (10-12工作日)
