# MyStocks 量化交易算法 API 详细规格文档

> **设计方案说明**:
> 本文件是 API 相关的设计稿、映射文档或方案说明，不是当前 API 契约、当前实现基线或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`；若涉及 API 契约事实源，再以实际的 FastAPI 路由 + Pydantic Schema + `/openapi.json` 为准。
>
> 文内结构设计、端点规划、映射关系和实施建议应结合当前代码与主线文档复核；若未落地，不得直接当作当前标准。


## 📋 概述

基于MyStocks系统中已实现的11种量化交易算法，为每个算法提供专门的REST API接口。本文档遵循以下规范：

- **合同管理API规范** (`docs/api/CONTRACT_MANAGEMENT_API.md`)
- **新API源集成指南** (`docs/guides/data-source/NEW_API_SOURCE_INTEGRATION_GUIDE.md`)
- **统一API响应格式** (code/message/data/request_id)

## 🎯 算法API架构

```bash
# API根路径
/api/v1/algorithms/

# 算法分类
├── classification/          # 分类算法 (SVM/决策树/朴素贝叶斯)
├── pattern-matching/        # 模式匹配算法 (BF/KMP/BMH/AC)
└── advanced/               # 高级算法 (HMM/贝叶斯网络/N-gram/神经网络)
```

## 🔍 详细API规格

### I. 分类算法 (Classification Algorithms)

#### 1. **支持向量机 (SVM)** - 买卖点判断

**API**: `POST /api/v1/algorithms/classification/svm/train`
- **应用场景**: 基于历史技术指标训练SVM模型，预测股票买卖时机
- **实现功能**: 使用GPU加速的SVM算法训练分类器，支持多核并行计算
- **依赖数据**:
  - **数据名称**: `historical_data`, `features`, `labels`, `config`
  - **数据格式**:
    ```json
    {
      "historical_data": [
        {"date": "2024-01-01", "close": 10.5, "rsi": 65.2, "macd": 0.3}
      ],
      "features": ["rsi", "macd", "volume_ratio"],
      "labels": ["BUY", "SELL", "HOLD"],
      "config": {"kernel": "rbf", "C": 1.0, "gamma": "scale"}
    }
    ```
  - **数据来源**: `GET /api/v1/market/kline` (历史K线数据)
  - **数据接口**: 市场数据API返回OHLCV格式数据

**API**: `POST /api/v1/algorithms/classification/svm/predict`
- **应用场景**: 实时预测当前市场买卖信号
- **实现功能**: 使用训练好的SVM模型对新数据进行分类预测
- **依赖数据**:
  - **数据名称**: `model_id`, `features_data`
  - **数据格式**:
    ```json
    {
      "model_id": "svm_model_20240101_001",
      "features_data": [65.2, 0.3, 1.2]
    }
    ```
  - **数据来源**: 客户端实时计算技术指标
  - **数据接口**: 训练API返回的model_id

#### 2. **决策树** - 交易决策规则

**API**: `POST /api/v1/algorithms/classification/decision-tree/train`
- **应用场景**: 生成可解释的交易决策树规则
- **实现功能**: 训练决策树分类器，支持特征重要性分析
- **依赖数据**:
  - **数据名称**: `training_data`, `max_depth`, `criterion`
  - **数据格式**:
    ```json
    {
      "training_data": {"features": [[...]], "labels": [...]},
      "max_depth": 10,
      "criterion": "gini"
    }
    ```
  - **数据来源**: `GET /api/v1/data/stocks/daily` (日线数据)
  - **数据接口**: 数据API返回的标准化特征矩阵

#### 3. **朴素贝叶斯** - 概率交易信号

**API**: `POST /api/v1/algorithms/classification/naive-bayes/train`
- **应用场景**: 基于概率分布的快速交易信号生成
- **实现功能**: 训练朴素贝叶斯分类器，输出类别概率
- **依赖数据**:
  - **数据名称**: `feature_matrix`, `target_vector`, `distribution_type`
  - **数据格式**:
    ```json
    {
      "feature_matrix": [[0.7, 1.2, 0.8], [...]],
      "target_vector": [0, 1, 2],
      "distribution_type": "gaussian"
    }
    ```
  - **数据来源**: `GET /api/v1/indicators/calculate` (批量指标计算)
  - **数据接口**: 指标API返回的特征向量

### II. 模式匹配算法 (Pattern Matching Algorithms)

#### 4. **Aho-Corasick** - 多模式走势匹配

**API**: `POST /api/v1/algorithms/pattern-matching/ac/train`
- **应用场景**: 构建股票走势模式库，支持多模式同时匹配
- **实现功能**: 构造AC自动机，支持数千个模式的高效匹配
- **依赖数据**:
  - **数据名称**: `patterns`, `pattern_type`, `market`
  - **数据格式**:
    ```json
    {
      "patterns": [
        {"name": "bull_flag", "sequence": [1.02, 1.05, 1.03, 1.08]},
        {"name": "bear_flag", "sequence": [0.98, 0.95, 0.97, 0.92]}
      ],
      "pattern_type": "price_relative",
      "market": "cn"
    }
    ```
  - **数据来源**: 用户定义或`GET /api/v1/market/patterns` (历史模式库)
  - **数据接口**: 市场API返回的标准化价格序列

**API**: `POST /api/v1/algorithms/pattern-matching/ac/match`
- **应用场景**: 实时检测股票走势中的预定义模式
- **实现功能**: 在实时价格序列中搜索所有匹配的模式
- **依赖数据**:
  - **数据名称**: `automaton_id`, `price_sequence`, `threshold`
  - **数据格式**:
    ```json
    {
      "automaton_id": "ac_patterns_001",
      "price_sequence": [10.1, 10.3, 10.2, 10.6, 10.4],
      "threshold": 0.95
    }
    ```
  - **数据来源**: WebSocket `/api/market/realtime/{symbol}` (实时价格流)
  - **数据接口**: 实时市场数据WebSocket推送

#### 5. **KMP算法** - 单模式精确匹配

**API**: `POST /api/v1/algorithms/pattern-matching/kmp/search`
- **应用场景**: 在历史数据中精确查找特定价格模式
- **实现功能**: 使用KMP算法进行高效的单模式字符串匹配
- **依赖数据**:
  - **数据名称**: `symbol`, `pattern`, `data_type`
  - **数据格式**:
    ```json
    {
      "symbol": "000001",
      "pattern": [1.02, 1.05, 1.03],
      "data_type": "price_changes"
    }
    ```
  - **数据来源**: `GET /api/v1/market/kline?symbol={symbol}&period=1d`
  - **数据接口**: K线API返回的价格变动百分比序列

#### 6. **BMH算法** - 启发式模式匹配

**API**: `POST /api/v1/algorithms/pattern-matching/bmh/search`
- **应用场景**: 大规模历史数据中的快速模式搜索
- **实现功能**: 使用坏字符启发式的BMH算法进行快速匹配
- **依赖数据**:
  - **数据名称**: `symbol`, `pattern`, `max_errors`
  - **数据格式**:
    ```json
    {
      "symbol": "000001",
      "pattern": [1.02, 1.05, 1.03],
      "max_errors": 1
    }
    ```
  - **数据来源**: `GET /api/v1/data/stocks/intraday` (日内数据)
  - **数据接口**: 股票数据API返回的高频价格序列

#### 7. **BF算法** - 暴力模式匹配

**API**: `POST /api/v1/algorithms/pattern-matching/bf/search`
- **应用场景**: 小规模数据的基础模式匹配基准测试
- **实现功能**: 标准的暴力字符串匹配算法
- **依赖数据**:
  - **数据名称**: `symbol`, `pattern`
  - **数据格式**:
    ```json
    {
      "symbol": "000001",
      "pattern": [1.02, 1.05, 1.03]
    }
    ```
  - **数据来源**: `GET /api/v1/market/heatmap` (市场热力图数据)
  - **数据接口**: 热力图API返回的区域价格数据

### III. 高级算法 (Advanced Algorithms)

#### 8. **隐马尔可夫模型 (HMM)** - 市场状态识别

**API**: `POST /api/v1/algorithms/advanced/hmm/train`
- **应用场景**: 识别市场结构性变化（牛市/熊市/震荡市）
- **实现功能**: 训练HMM模型识别隐藏市场状态
- **依赖数据**:
  - **数据名称**: `symbol`, `observations`, `n_states`
  - **数据格式**:
    ```json
    {
      "symbol": "000001",
      "observations": ["high_volatility", "price_up", "volume_spike"],
      "n_states": 3
    }
    ```
  - **数据来源**: `GET /api/v1/market/realtime` (实时市场数据)
  - **数据接口**: 实时API返回的离散化观测序列

**API**: `POST /api/v1/algorithms/advanced/hmm/predict`
- **应用场景**: 实时判断当前市场所处的结构状态
- **实现功能**: 使用训练的HMM预测当前最可能的市场状态
- **依赖数据**:
  - **数据名称**: `model_id`, `current_observations`
  - **数据格式**:
    ```json
    {
      "model_id": "hmm_market_001",
      "current_observations": ["high_volatility", "price_up"]
    }
    ```
  - **数据来源**: WebSocket实时数据流
  - **数据接口**: WebSocket推送的实时观测数据

#### 9. **贝叶斯网络** - 股票联动分析

**API**: `POST /api/v1/algorithms/advanced/bayesian-network/build`
- **应用场景**: 分析股票间的因果关系和联动效应
- **实现功能**: 构建贝叶斯网络模型量化股票间依赖关系
- **依赖数据**:
  - **数据名称**: `symbols`, `relationships`, `time_window`
  - **数据格式**:
    ```json
    {
      "symbols": ["000001", "000002", "600000"],
      "relationships": [
        {"from": "000001", "to": "000002", "delay": 1}
      ],
      "time_window": 30
    }
    ```
  - **数据来源**: `GET /api/v1/data/stocks/daily` (多股票日线数据)
  - **数据接口**: 数据API返回的多股票历史数据

**API**: `POST /api/v1/algorithms/advanced/bayesian-network/infer`
- **应用场景**: 预测特定股票异动对其他股票的影响
- **实现功能**: 基于贝叶斯网络进行概率推理
- **依赖数据**:
  - **数据名称**: `network_id`, `trigger_event`, `max_delay`
  - **数据格式**:
    ```json
    {
      "network_id": "bayes_network_001",
      "trigger_event": {"symbol": "000001", "type": "price_spike"},
      "max_delay": 5
    }
    ```
  - **数据来源**: 实时告警系统
  - **数据接口**: 告警API推送的事件数据

#### 10. **N-gram模型** - 序列模式分析

**API**: `POST /api/v1/algorithms/advanced/n-gram/train`
- **应用场景**: 学习股价或交易量的序列统计模式
- **实现功能**: 训练N-gram语言模型捕捉市场序列规律
- **依赖数据**:
  - **数据名称**: `symbol`, `n`, `sequence_type`, `window_size`
  - **数据格式**:
    ```json
    {
      "symbol": "000001",
      "n": 3,
      "sequence_type": "price_changes",
      "window_size": 1000
    }
    ```
  - **数据来源**: `GET /api/v1/market/kline` (历史K线数据)
  - **数据接口**: K线API返回的价格变动序列

**API**: `POST /api/v1/algorithms/advanced/n-gram/predict`
- **应用场景**: 预测市场序列的下一个最可能状态
- **实现功能**: 基于N-gram模型进行序列预测
- **依赖数据**:
  - **数据名称**: `model_id`, `current_sequence`
  - **数据格式**:
    ```json
    {
      "model_id": "ngram_price_001",
      "current_sequence": [0.02, -0.01, 0.015]
    }
    ```
  - **数据来源**: 实时计算的最新价格变动
  - **数据接口**: 客户端实时计算的N-1个价格变动

#### 11. **神经网络** - 时间序列预测

**API**: `POST /api/v1/algorithms/advanced/neural-network/train`
- **应用场景**: 使用深度学习进行复杂的股价趋势预测
- **实现功能**: 训练LSTM/GRU等神经网络进行时间序列预测
- **依赖数据**:
  - **数据名称**: `symbol`, `architecture`, `input_features`, `prediction_horizon`
  - **数据格式**:
    ```json
    {
      "symbol": "000001",
      "architecture": "lstm",
      "input_features": ["price", "volume", "rsi", "macd"],
      "prediction_horizon": 5,
      "lookback_window": 60
    }
    ```
  - **数据来源**: `GET /api/v1/indicators/calculate/batch` (批量指标计算)
  - **数据接口**: 指标API返回的多特征时间序列

**API**: `POST /api/v1/algorithms/advanced/neural-network/predict`
- **应用场景**: 实时生成深度学习驱动的预测结果
- **实现功能**: 使用训练的神经网络进行滚动预测
- **依赖数据**:
  - **数据名称**: `model_id`, `current_data`
  - **数据格式**:
    ```json
    {
      "model_id": "lstm_predictor_001",
      "current_data": {
        "price": [10.5, 10.8, 10.2],
        "volume": [1000000, 1200000, 800000],
        "rsi": [65, 72, 58],
        "macd": [0.2, 0.3, 0.1]
      }
    }
    ```
  - **数据来源**: 实时市场数据流
  - **数据接口**: WebSocket或REST API的实时特征数据

## 📊 API统计与覆盖

| 算法分类 | 算法数量 | API端点数 | 主要应用场景 |
|----------|----------|-----------|--------------|
| 分类算法 | 3 | 6 | 买卖点判断、交易信号生成 |
| 模式匹配 | 4 | 4 | 走势模式识别、相似股票发现 |
| 高级算法 | 4 | 7 | 市场状态识别、联动分析、序列预测 |

**总计**: 11种算法，17个API端点

## 🔗 数据依赖关系

```
量化算法API
├── 市场数据API (GET /api/v1/market/*)
│   ├── K线数据 → 训练历史模型
│   ├── 实时数据 → 实时预测
│   └── 板块数据 → 模式匹配
├── 指标计算API (GET /api/v1/indicators/*)
│   ├── 技术指标 → 特征工程
│   └── 批量计算 → 神经网络输入
├── 数据查询API (GET /api/v1/data/*)
│   ├── 股票基础数据 → 多股票分析
│   └── 财务数据 → 贝叶斯网络构建
└── 实时数据流 (WebSocket)
    ├── 价格更新 → 滚动预测
    └── 成交数据 → 状态识别
```

## 🛠️ 技术实现要求

### 遵循规范
- ✅ **合同管理API规范**: 使用统一的响应格式和版本管理
- ✅ **新API源集成指南**: 通过5步验证流程
- ✅ **适配器模式**: 支持多种数据源和算法后端
- ✅ **GPU加速**: 优先使用cuML/cuDF进行加速

### 安全与性能
- **认证**: JWT Bearer Token + API Key
- **限流**: 每分钟1000次请求限制
- **异步处理**: 长时间训练任务使用后台队列
- **缓存**: Redis缓存频繁查询的模型结果

### 监控与告警
- **性能指标**: 响应时间、GPU利用率、内存使用
- **健康检查**: 算法服务可用性监控
- **告警规则**: 模型训练失败、预测准确率下降

---

**文档版本**: v1.0.0
**API端点**: 17个
**覆盖算法**: 11种
**设计遵循**: 合同管理API规范 + 新API集成指南
