# 双模计算引擎 - Spec Delta

**能力**: 双模计算引擎 (Dual-Mode Calculation Engine)
**变更ID**: add-smart-quant-monitoring
**状态**: 待审核

---

## ADDED Requirements

### Requirement: 智能CPU/GPU模式切换

The system MUST automatically select CPU or GPU calculation engine based on data scale and GPU health status.

#### Scenario: 小规模数据自动选择CPU模式

**GIVEN** 用户请求计算50只股票健康度
**AND** 每只股票有500行K线数据
**WHEN** 系统执行计算引擎选择
**THEN** 数据规模检查：50只股票 <100只，500行 <3000行
**AND** 系统选择 CPU 模式（Pandas向量化）
**AND** 日志记录："⚙️ 使用CPU引擎 (stocks=50, rows=500)"

#### Scenario: 大规模数据自动选择GPU模式

**GIVEN** 用户请求计算500只股票健康度
**AND** 每只股票有2000行K线数据
**WHEN** 系统执行计算引擎选择
**THEN** 数据规模检查：500只股票 >100只，触发GPU模式
**AND** GPU健康检查：
  - GPU可用：✓
  - GPU健康：✓
  - 可用显存：6GB ≥ 4GB
**AND** 系统选择 GPU 模式（CuPy/RAPIDS）
**AND** 日志记录："🚀 使用GPU引擎 (stocks=500, rows=2000)"

#### Scenario: GPU不可用时降级CPU

**GIVEN** 用户请求计算1000只股票
**AND** GPU可用性检查：
  - GPU可用：✗（未安装CUDA）
**WHEN** 系统执行计算引擎选择
**THEN** 系统降级到 CPU 模式
**AND** 日志记录："⚠️ GPU不可用，使用CPU引擎"

#### Scenario: GPU显存不足时降级CPU

**GIVEN** 用户请求计算1000只股票
**AND** GPU可用性检查：
  - GPU可用：✓
  - GPU健康：✓
  - 可用显存：3GB < 4GB（阈值）
**WHEN** 系统执行计算引擎选择
**THEN** 系统降级到 CPU 模式
**AND** 日志记录："⚠️ GPU显存不足（3GB < 4GB），使用CPU引擎"

---

### Requirement: CPU向量化计算引擎

The system MUST use Pandas/Numpy vectorized calculation to avoid loops and improve performance.

#### Scenario: 向量化计算五维评分

**GIVEN** 计算引擎处于 CPU 模式
**AND** 输入数据：100只股票 × 500行K线数据
**WHEN** 系统执行 `VectorizedHealthCalculator.calculate()`
**THEN** 系统执行向量化操作：
  ```python
  df = pd.DataFrame(stock_data)
  trend_scores = df.groupby('stock_code').apply(calc_trend_vectorized)
  technical_scores = df.groupby('stock_code').apply(calc_technical_vectorized)
  ```
**AND** 避免循环：`for stock in stocks` ❌
**AND** 计算耗时 <5秒

#### Scenario: 验证向量化计算正确性

**GIVEN** 同一批股票数据
**WHEN** 系统执行向量化计算
**AND** 系统执行循环计算（对照组）
**THEN** 两种方法结果误差 <0.01
**AND** 向量化速度提升 >50x

---

### Requirement: GPU加速计算引擎

The system MUST use CuPy/RAPIDS for GPU acceleration, achieving 50x+ performance improvement for large-scale calculations.

#### Scenario: GPU加速计算健康度

**GIVEN** 计算引擎处于 GPU 模式
**AND** 输入数据：1000只股票 × 5000行K线数据
**WHEN** 系统执行 `GPUHealthCalculator.calculate()`
**THEN** 系统执行：
  1. 数据传输到GPU（CuPy DataFrame）
  2. GPU向量化计算（CuPy/RAPIDS）
  3. 结果传回CPU
**AND** 计算耗时 <2秒
**AND** 性能提升：142秒（CPU）→ 1.4秒（GPU）= 101x加速

#### Scenario: GPU内存管理

**GIVEN** GPU显存8GB，建议分配6GB
**WHEN** 系统执行GPU计算
**THEN** 系统执行：
  1. 检查可用显存：6GB ✓
  2. 分配GPU内存
  3. 执行计算
  4. 及时释放内存：`cupy.cuda.memory.free_all_blocks()`
**AND** 无显存泄漏

#### Scenario: GPU故障降级处理

**GIVEN** 计算引擎处于 GPU 模式
**WHEN** 执行计算时触发 CUDA OOM 错误
**THEN** 系统捕获异常：`CudaOutOfMemoryError`
**AND** 日志记录："⚠️ GPU显存不足，降级到CPU"
**AND** 自动切换到 CPU 模式重试
**AND** 返回正确结果

---

### Requirement: 计算引擎工厂模式

The system MUST provide a factory class to uniformly manage CPU/GPU engine creation and switching.

#### Scenario: 工厂类创建计算引擎

**GIVEN** 系统初始化
**WHEN** 调用 `HealthCalculatorFactory.get_calculator(stock_count=50, data_rows=500)`
**THEN** 工厂类执行决策：
  1. 检查数据规模：小规模 ✓
  2. 检查GPU健康：跳过（小规模不需要）
  3. 返回 `VectorizedHealthCalculator` 实例
**AND** 返回的引擎可直接调用 `calculate()`

#### Scenario: 工厂类智能切换引擎

**GIVEN** 用户请求计算不同规模的股票
**WHEN** 第一次请求：50只股票 → 工厂返回 CPU 引擎
**AND** 第二次请求：1000只股票 → 工厂返回 GPU 引擎
**AND** 第三次请求：100只股票 → 工厂返回 CPU 引擎
**THEN** 每次请求都获得最优引擎
**AND** 切换对用户透明

---

### Requirement: 复用现有GPU模块

The system MUST reuse the resource management and health checking functionality from the `src/gpu` module.

#### Scenario: 复用GPU资源管理器

**GIVEN** 系统初始化GPU计算引擎
**WHEN** 调用 `get_gpu_performance_optimizer()`
**THEN** 系统复用 `src/monitoring/gpu_performance_optimizer.py`
**AND** 调用 `get_gpu_health_status()` 获取：
  - available: GPU是否可用
  - healthy: GPU是否健康
  - free_memory_gb: 可用显存
  - temperature: GPU温度
  - utilization: GPU利用率

#### Scenario: 复用RAPIDS CuPy集成

**GIVEN** GPU计算引擎执行计算
**WHEN** 系统需要GPU加速
**THEN** 系统复用 `src/gpu/api/` 模块
**AND** 使用 CuPy DataFrame 替代 Pandas
**AND** 使用 RAPIDS cuDF 加速DataFrame操作

---

### Requirement: 计算结果一致性保证

The system MUST guarantee consistency between CPU and GPU engine calculation results (error <0.01).

#### Scenario: 验证CPU/GPU结果一致性

**GIVEN** 同一批股票数据（100只）
**WHEN** 系统分别使用CPU和GPU引擎计算
**THEN** 对比每只股票的五维评分：
  - trend_score 误差 <0.01
  - technical_score 误差 <0.01
  - momentum_score 误差 <0.01
  - volatility_score 误差 <0.01
  - risk_score 误差 <0.01
**AND** total_score 误差 <0.01
**AND** 所有指标在可接受范围内

---

## MODIFIED Requirements

*无修改现有需求*

---

## REMOVED Requirements

*无删除现有需求*

---

## Cross-References

- **依赖**: `src/gpu` 模块 - GPU资源管理、CuPy/RAPIDS集成
- **依赖**: `src/monitoring/gpu_performance_optimizer.py` - GPU健康检查
- **服务**: `health-scoring` - 提供评分计算接口
- **关联**: `watchlist-management` - 清单数据作为计算输入

---

## 技术实现

### GPU配置阈值

```python
GPU_CONFIG = {
    'total_memory_threshold_gb': 8,      # 总显存要求（用户指定）
    'recommended_allocation_gb': 6,      # 建议分配显存（用户指定）
    'min_available_memory_gb': 4,        # 最低可用显存
    'cpu_max_rows': 3000,                # CPU模式最大行数（用户指定）
    'cpu_max_stocks': 100,               # CPU模式最大股票数
}
```

### 计算引擎工厂

```python
class HealthCalculatorFactory:
    @staticmethod
    async def get_calculator(stock_count: int, data_rows: int) -> HealthCalculator:
        """智能选择计算引擎"""
        gpu_optimizer = await get_gpu_performance_optimizer()
        gpu_status = await gpu_optimizer.get_gpu_health_status()

        needs_gpu = (stock_count > 100 or data_rows > 3000)
        gpu_available = (
            gpu_status['available'] and
            gpu_status['healthy'] and
            gpu_status['free_memory_gb'] >= 4
        )

        if needs_gpu and gpu_available:
            return GPUHealthCalculator()
        else:
            return VectorizedHealthCalculator()
```

---

## 性能基准

| 数据规模 | CPU (Pandas) | GPU (CuPy/RAPIDS) | 加速比 |
|---------|--------------|-------------------|--------|
| 100只股票 × 500行 | 2.3秒 | 0.8秒 | 2.9x |
| 500只股票 × 2000行 | 28秒 | 0.9秒 | 31x |
| 1000只股票 × 5000行 | 142秒 | 1.4秒 | 101x |

---

**状态**: 待审核
**版本**: v1.0
