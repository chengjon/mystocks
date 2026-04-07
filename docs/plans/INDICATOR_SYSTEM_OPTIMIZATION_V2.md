# 指标计算系统优化方案 V2.1

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、任务方案或执行矩阵，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值和时间线如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


> **版本**: v2.1
> **日期**: 2026-01-07
> **参考架构**: 数据源管理V2.0
> **状态**: 📋 优化方案 (已通过评审)
> **更新说明**: 新增流式计算(Streaming)、严格对齐标准、依赖管理及自动降级机制

---

## 📊 方案总览

本方案参考**数据源管理V2.0**的成功架构，为指标计算系统建立**中心化注册表 + 智能工厂 + 完整监控 + 向后兼容**的完整架构。

### 核心设计理念（参考数据源V2）

1.  **双存储策略**：PostgreSQL持久化 + YAML配置文件
2.  **统一工厂接口**：屏蔽底层指标实现差异
3.  **智能选择 & 自动降级**：优先使用高性能后端（GPU/Numba），失败时自动降级
4.  **双模式计算**：
    *   **Batch模式**：针对回测，全量向量化计算，$O(1)$ Python调用开销。
    *   **Streaming模式**：针对实盘，增量状态更新，Strict $O(1)$ 时间复杂度。
5.  **严格对齐**：强制输出索引与输入严格对齐，杜绝"未来函数"隐患。

### 与数据源V2的对应关系

| 数据源V2 | 指标系统V2 | 说明 |
|---------|-----------|------|
| `DataSourceManagerV2` | `IndicatorFactory` | 统一管理入口 |
| `data_source_registry` 表 | `indicator_registry` 表 | 元数据存储 |
| `data_sources_registry.yaml` | `indicators_registry.yaml` | 配置文件 |
| `manual_data_source_tester.py` | `manual_indicator_tester.py` | 测试工具 |
| `/api/data_source_registry` | `/api/indicator_registry` | FastAPI接口 |

---

## 1️⃣ 指标元数据注册表（PostgreSQL）

### 数据库表结构

```sql
-- 创建指标注册表
CREATE TABLE indicator_registry (
    id SERIAL PRIMARY KEY,

    -- 基础信息
    indicator_name VARCHAR(50) NOT NULL,        -- 指标名称：SMA、RSI、MACD等
    indicator_type VARCHAR(20) NOT NULL,        -- 类型：trend/momentum/volatility/volume
    indicator_id VARCHAR(100) UNIQUE NOT NULL,   -- 指标唯一标识：sma.20、rsi.14等

    -- 计算信息
    implementation_type VARCHAR(20),            -- python/talib/numba/gpu
    class_name VARCHAR(100),                    -- 实现类名
    module_path TEXT,                           -- 模块路径
    dependencies TEXT[],                        -- 依赖的其他指标ID (新增)

    -- 分类与用途
    indicator_category VARCHAR(50) NOT NULL,    -- 分类：trend_indicators/momentum_indicators等
    use_case VARCHAR(20) NOT NULL,             -- 用途：backtest/realtime/batch
    supported_backends TEXT[],                  -- 支持的后端：cpu/gpu/numba/talib
    supports_streaming BOOLEAN DEFAULT FALSE,   -- 是否支持流式计算 (新增)

    -- 安全与特性
    is_lagging BOOLEAN DEFAULT TRUE,            -- 是否滞后指标 (新增)
    lookahead_bias BOOLEAN DEFAULT FALSE,       -- 是否存在未来函数 (新增)

    -- 元数据
    description TEXT,
    formula TEXT,                               -- 指标公式（LaTeX格式）
    parameters JSONB,                           -- 参数定义和默认值
    required_columns TEXT[],                    -- 必需的列名
    output_columns TEXT[],                      -- 输出列名

    -- 性能指标
    performance_score FLOAT DEFAULT 8.0,        -- 性能评分（0-10）
    avg_calculation_time FLOAT DEFAULT 0,       -- 平均计算时间（毫秒）
    benchmark_rows INT DEFAULT 1000,            -- 基准测试行数

    -- 质量指标
    accuracy_score FLOAT DEFAULT 8.0,           -- 准确性评分（与TA-Lib对比）
    stability_score FLOAT DEFAULT 8.0,          -- 稳定性评分
    test_coverage FLOAT DEFAULT 0.0,            -- 测试覆盖率（0-100）

    -- 监控指标
    last_test_time TIMESTAMP,
    last_test_success BOOLEAN,
    total_calculations INT DEFAULT 0,
    failed_calculations INT DEFAULT 0,
    consecutive_failures INT DEFAULT 0,

    -- 状态管理
    status VARCHAR(20) DEFAULT 'active',       -- active/deprecated/experimental
    version VARCHAR(20) DEFAULT '1.0.0',
    tags TEXT[],                               -- 标签数组

    -- 管理信息
    owner VARCHAR(50) DEFAULT 'system',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 约束
    CONSTRAINT chk_status CHECK (status IN ('active', 'deprecated', 'experimental')),
    CONSTRAINT chk_performance_score CHECK (performance_score >= 0 AND performance_score <= 10),
    CONSTRAINT chk_accuracy_score CHECK (accuracy_score >= 0 AND accuracy_score <= 10),
    CONSTRAINT chk_test_coverage CHECK (test_coverage >= 0 AND test_coverage <= 100)
);

-- 索引略 (同V2.0)
```

---

## 2️⃣ YAML配置文件（增强版）

### 配置文件结构

新增 `dependencies`, `supports_streaming`, `lookahead_bias` 等字段。

```yaml
# config/indicators_registry.yaml
version: "2.1"
last_updated: "2026-01-07T14:00:00"

indicators:
  # 趋势指标
  sma_5:
    indicator_name: "SMA"
    indicator_type: "trend"
    indicator_id: "sma.5"
    implementation_type: "python"
    class_name: "SMAIndicator"
    module_path: "src.indicators.indicators"
    indicator_category: "trend_indicators"
    use_case: "backtest"
    supported_backends: ["cpu", "numba", "talib"]
    supports_streaming: true    # 支持流式计算
    is_lagging: true           # 滞后指标
    lookahead_bias: false      # 无未来函数

    description: "简单移动平均线（5日）"
    formula: "SMA = (P1 + P2 + ... + Pn) / n"
    parameters:
      period:
        type: "int"
        default: 5
        min: 1
        max: 1000
    required_columns: ["close"]
    output_columns: ["sma"]
    performance_score: 9.0
    status: "active"

  # 复杂指标（带依赖）
  kdj_9_3_3:
    indicator_name: "KDJ"
    indicator_type: "momentum"
    indicator_id: "kdj.9.3.3"
    implementation_type: "python"
    class_name: "KDJIndicator"
    module_path: "src.indicators.momentum"
    indicator_category: "momentum_indicators"
    supported_backends: ["cpu", "numba"]
    supports_streaming: true
    is_lagging: false
    lookahead_bias: false

    # 依赖声明
    dependencies:
      - "rsv.9"

    parameters:
      period: 9
      k_period: 3
      d_period: 3
    required_columns: ["high", "low", "close"]
    output_columns: ["k", "d", "j"]
    status: "active"
```

---

## 3️⃣ 指标工厂（核心管理器 V2.1）

### 核心类设计：支持流式与自动降级

```python
# src/indicators/indicator_factory.py

class IndicatorFactory:
    """
    指标工厂 V2.1
    新增特性：流式计算接口、自动降级、参数预校验
    """

    # ... (原有 __init__ 和 loader 方法保持不变) ...

    def get_calculator(
        self,
        indicator_id: str,
        backend: Optional[str] = None,
        streaming: bool = False
    ) -> Union['BatchIndicator', 'StreamingIndicator']:
        """
        获取计算器实例（核心入口）

        Args:
            indicator_id: 指标ID
            backend: 指定后端 (gpu/numba/cpu)，若不指定则自动选择
            streaming: 是否请求流式计算器

        Returns:
            计算器实例
        """
        config = self._get_config(indicator_id)

        # 1. 流式模式检查
        if streaming:
            if not config.get('supports_streaming'):
                raise ValueError(f"指标 {indicator_id} 不支持流式计算")
            # 流式通常默认用 CPU/Numba，GPU流式开销大通常不推荐
            return self._create_streaming_implementation(config)

        # 2. 批处理模式 - 自动降级逻辑
        preferred_backends = config.get('supported_backends', ['cpu'])

        # 如果用户指定了后端，则只尝试该后端
        if backend:
            if backend not in preferred_backends:
                raise ValueError(f"指标不支持后端: {backend}")
            target_backends = [backend]
        else:
            # 默认优先级: gpu > numba > talib > cpu
            priority_order = ['gpu', 'numba', 'talib', 'cpu']
            target_backends = [b for b in priority_order if b in preferred_backends]

        # 3. 尝试实例化 (Failover Loop)
        for be in target_backends:
            try:
                return self._create_batch_implementation(config, backend=be)
            except ImportError as e:
                logger.warning(f"后端 {be} 加载失败，尝试降级: {e}")
                continue
            except Exception as e:
                logger.error(f"后端 {be} 初始化错误: {e}")
                continue

        raise RuntimeError(f"无法为指标 {indicator_id} 创建任何可用的计算后端")

    def calculate(self, indicator_id: str, data: pd.DataFrame, **kwargs) -> pd.Series:
        """
        高层批处理接口
        保证：返回的 Series 索引与输入 data 严格对齐
        """
        # 1. 参数校验
        self._validate_parameters(indicator_id, kwargs)

        # 2. 获取计算器
        calculator = self.get_calculator(indicator_id)

        # 3. 计算
        result = calculator.calculate(data, **kwargs)

        # 4. 强制对齐检查 (Professional Practice)
        if len(result) != len(data) or not result.index.equals(data.index):
             # 尝试自动修复对齐（针对 TA-Lib 常见行为）
             result = result.reindex(data.index)

        return result

    def _validate_parameters(self, indicator_id: str, params: Dict):
        """基于YAML配置进行参数边界检查"""
        config = self.registry[indicator_id]['config']
        param_defs = config.get('parameters', {})

        for k, v in params.items():
            if k in param_defs:
                p_def = param_defs[k]
                if 'min' in p_def and v < p_def['min']:
                    raise ValueError(f"参数 {k}={v} 小于最小值 {p_def['min']}")
                if 'max' in p_def and v > p_def['max']:
                    raise ValueError(f"参数 {k}={v} 大于最大值 {p_def['max']}")
```

### 3.1 接口定义：批处理 vs 流式

```python
# src/indicators/base.py
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np

class BaseIndicator(ABC):
    """指标基类"""
    pass

class BatchIndicator(BaseIndicator):
    """批处理指标接口 (Vectorized)"""
    @abstractmethod
    def calculate(self, data: pd.DataFrame, **kwargs) -> pd.Series:
        pass

class StreamingIndicator(BaseIndicator):
    """
    流式指标接口 (Stateful)
    用于实盘，严格 O(1)
    """
    @abstractmethod
    def update(self, new_bar: Dict[str, float]) -> float:
        """
        输入最新的 Bar (Open/High/Low/Close/Volume)
        返回当前 Tick 的指标值
        """
        pass

    @abstractmethod
    def snapshot(self) -> Dict:
        """获取当前状态快照（用于系统重启恢复）"""
        pass

    @abstractmethod
    def load_snapshot(self, state: Dict):
        """从快照恢复状态"""
        pass
```

---

## 4️⃣ 实施路线图（修订版）

### Phase 1: 基础设施与核心接口（1-2周）

**目标**: 建立中心化注册表和**双模式**工厂接口

**任务**:
1.  ✅ 创建PostgreSQL表结构（增加 Streaming/Safety 字段）
2.  ✅ 创建YAML配置文件（增加依赖和参数限制配置）
3.  ✅ 定义 `BatchIndicator` 和 `StreamingIndicator` 抽象基类
4.  ✅ 实现 `IndicatorFactory` (含自动降级、参数校验逻辑)
5.  ✅ 迁移 SMA, RSI 指标（实现 Batch 和 Streaming 两个版本）

### Phase 2: 测试工具（1周）

**目标**: 实现手动测试工具和FastAPI接口

**任务**:
1.  ✅ 实现 `manual_indicator_tester.py`
2.  ✅ **新增**: 流式计算一致性测试（验证 `Streaming.update()` 结果序列是否等于 `Batch.calculate()`）
3.  ✅ 实现API接口

### Phase 3: 向后兼容（1周）

**目标**: "手术式"替换现有系统

**任务**:
1.  ✅ 修改 `TechnicalIndicatorCalculator`
2.  ✅ 确保所有旧接口调用底层走 Batch 模式并自动对齐数据

### Phase 4: 监控与性能（1-2周）

**目标**: 监控集成

---

## 5️⃣ 关键改进点总结

1.  **实盘就绪 (Production Ready)**: 通过 `StreamingIndicator` 彻底解决实盘重算历史数据的性能瓶颈。
2.  **数据安全 (Safety)**: 强制索引对齐，消灭"未来函数"；YAML 中显式标记 `lookahead_bias`。
3.  **鲁棒性 (Robustness)**: 工厂层级的参数校验和后端自动降级（GPU -> CPU），保证系统不崩。
4.  **一致性保障**: 在 Phase 2 测试中增加 "Batch vs Streaming" 结果一致性校验，确保回测和实盘逻辑完全一致。

---

**方案生成时间**: 2026-01-07
**方案版本**: v2.1
**参考架构**: 数据源管理V2.0
**修订人**: Gemini CLI
