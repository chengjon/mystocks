# MyStocks Quant System - Next Phase Development Plan (Optimized V2.3)

## 🎯 Overview

Building upon the robust **V2 Indicator System** (`TalibGenericIndicator` & `IndicatorFactory`) and the established **Data Source Registry**, this plan outlines the path to a high-performance, real-time trading signal engine.

**Core Objectives:**
1.  **Real-Time Architecture**: Upgrade from polling to event-driven streaming.
2.  **GPU Acceleration**: Introduce `GpuIndicatorAdapter` for high-frequency/batch calculation.
3.  **Signal Engine**: Create a multi-factor signal generation system.

---

## 📅 Execution Roadmap

| Phase | Duration | Focus | Key Deliverables |
| :--- | :--- | :--- | :--- |
| **Phase 1** | 2 Weeks | **Streaming Infrastructure** | `WebSocketAdapter`, `StreamService`, Event Bus |
| **Phase 2** | 2 Weeks | **GPU Acceleration** | `GpuIndicatorAdapter` (cuDF/cuPy), Performance Benchmarks |
| **Phase 3** | 3 Weeks | **Signal Intelligence** | `SignalEngine`, Strategy Registry, Live Alerting |

---

## 🚀 Phase 1: Real-Time Streaming Infrastructure

**Goal**: Transition from "Store-then-Calculate" to "Stream-Calculate-Signal".

### 1.1 Unified Stream Manager
**File**: `web/backend/app/services/streaming/stream_manager.py`

*   **Role**: Central hub for managing live subscriptions.
*   **Design**:
    *   Integrates with `UnifiedDataManager` to resolve symbols to adapters.
    *   Manages WebSocket connections to providers (Sina, Tencent, etc.).
    *   Broadcasts updates via internal `EventBus` (asyncio queues for MVP, Redis/Kafka later).

```python
class StreamManager:
    async def subscribe(self, symbols: List[str]):
        """
        1. Resolve adapter for symbol via DataSourcesRegistry
        2. Initiate WebSocket connection (if not active)
        3. Register internal callback to EventBus
        """
```

### 1.2 WebSocket Adapter Interface
**File**: `web/backend/app/data_sources/base_websocket.py`

*   **Role**: Standardize real-time data ingress.
*   **Extension**: Add `WebSocketCapability` to existing `BaseDataSourceAdapter`.

```python
class WebSocketCapability(Protocol):
    async def connect(self): ...
    async def subscribe(self, symbols: List[str]): ...
    async def on_message(self, handler: Callable): ...
```

### 1.3 Event Bus System
**File**: `web/backend/app/core/event_bus.py`

*   **Topics**:
    *   `market.tick.{symbol}`: Raw price updates.
    *   `market.bar.{symbol}.{frame}`: Aggregated OHLCV bars.
    *   `signal.alert`: Generated trading signals.

---

## 🚀 Phase 2: GPU Acceleration (Indicator System V2.5)

**Goal**: Achieve <10ms calculation time for 5000+ stocks to enable real-time full-market scanning.

### 2.1 GPU Indicator Adapter
**File**: `web/backend/app/services/indicators/gpu_adapter.py`

*   **Strategy**: Create a drop-in replacement for `TalibGenericIndicator` that uses NVIDIA RAPIDS (cuDF) or CuPy.
*   **Integration**:
    *   Extend `IndicatorInterface`.
    *   Use `IndicatorPluginFactory` to register GPU versions with a `_gpu` suffix (e.g., `MACD_GPU`) or a runtime flag.

```python
class GpuGenericIndicator(IndicatorInterface):
    """
    Uses cuDF to perform vectorized calculations on GPU memory.
    Fallback to CPU if GPU is unavailable.
    """
    def calculate(self, data: OHLCVData, parameters: Dict) -> IndicatorResult:
        import cudf
        # Convert numpy/pandas to cuDF Series
        gpu_close = cudf.Series(data.close)
        # Calculate using rolling windows on GPU
        ...
```

### 2.2 Benchmarking & Optimization
*   **Target**: 50x speedup over TA-Lib for batch processing (all stocks, one indicator).
*   **Deliverable**: `docs/reports/GPU_ACCELERATION_BENCHMARK.md`

---

## 🚀 Phase 3: Signal Generation Engine

**Goal**: Convert data and indicators into actionable trading signals.

### 3.1 Signal Engine
**File**: `web/backend/app/services/signals/engine.py`

*   **Logic**:
    1.  Listen to `market.bar.*` events.
    2.  Invoke `IndicatorFactory` (using `SmartScheduler` for dependency resolution).
    3.  Evaluate `SignalStrategy` rules.
    4.  Publish `signal.alert`.

### 3.2 Strategy Registry
**File**: `web/backend/app/services/signals/strategies/registry.py`

*   **Concept**: Configurable rules defined in YAML or Python classes.

```python
class MacdCrossStrategy(BaseStrategy):
    def evaluate(self, context: MarketContext) -> Signal:
        macd = context.indicators.get("MACD")
        if cross_over(macd.diff, macd.dea):
             return Signal(action="BUY", confidence=0.8)
```

### 3.3 Dashboard Integration
*   **Frontend**: Update React frontend to listen to WebSocket `/ws/signals`.
*   **Grafana**: Push signals to InfluxDB/Prometheus for historical visualization overlay.

---

## 📝 Success Metrics

1.  **Latency**: End-to-end (Price Update -> Signal) < 200ms.
2.  **Throughput**: Process 5000 stocks * 20 indicators in < 1 second (Batch/GPU).
3.  **Coverage**: 100% of existing 23+ V2 indicators verified.

## ⚠️ Risk Management

*   **GPU Availability**: Ensure graceful fallback to CPU (TA-Lib) if CUDA is missing.
*   **Memory Leaks**: Strict monitoring of WebSocket connections and GPU memory (VRAM).
