# CLI-3: Phase 6 缓存系统优化

**分支**: `phase6-cache-optimization`
**工作目录**: `/opt/claude/mystocks_phase6_cache`
**预计时间**: 4-6 小时
**优先级**: 🟡 中（性能优化）
**分配给**: GEMINI 或 CLAUDE

---

## 🎯 任务目标

优化多级缓存系统性能，确保高吞吐量和低延迟：

1. ✅ 测试多级缓存功能（L1 内存 + L2 TDengine）
2. ✅ 验证 TDengine 缓存连接和性能
3. ✅ 优化缓存命中率（目标 > 80%）
4. ✅ 测试断路器模式和优雅降级
5. ✅ 压力测试（1000 并发）
6. ✅ 性能基准测试和对比

---

## 📋 详细任务清单

### 任务 3.1: 测试多级缓存功能 (1小时)

**目标**: 验证 L1 内存缓存和 L2 TDengine 缓存正常工作

**步骤**:
```bash
# 1. 启动后端服务
cd /opt/claude/mystocks_phase6_cache/web/backend
ADMIN_PASSWORD=password python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# 2. 等待服务启动
sleep 10

# 3. 运行缓存单元测试
cd /opt/claude/mystocks_phase6_cache
python -m pytest tests/unit/test_cache.py -v

# 4. 测试 L1 内存缓存
python3 << 'PY'
import requests
import time

# 第一次请求（缓存未命中）
start = time.time()
response = requests.get('http://localhost:8000/api/v1/market/symbols?symbol=000001')
latency1 = time.time() - start
print(f"First request (cache miss): {latency1:.3f}s")

# 第二次请求（缓存命中）
start = time.time()
response = requests.get('http://localhost:8000/api/v1/market/symbols?symbol=000001')
latency2 = time.time() - start
print(f"Second request (cache hit): {latency2:.3f}s")

# 验证缓存加速
speedup = latency1 / latency2
print(f"Cache speedup: {speedup:.1f}x")
assert speedup > 10, f"Cache speedup too low: {speedup:.1f}x"
PY

# 5. 测试 L2 TDengine 缓存（如果可用）
# 检查日志确认 TDengine 缓存是否启用
curl -s http://localhost:8000/metrics | grep cache
```

**验收标准**:
- ✅ L1 内存缓存工作正常（速度提升 > 10x）
- ✅ L2 TDengine 缓存连接成功（如果 TDengine 可用）
- ✅ 缓存装饰器正确应用
- ✅ 缓存 TTL 自动过期

**可能的问题**:
- **问题**: 缓存未命中，没有加速
  - **解决**: 检查 `src/core/cache/decorators.py` 中 `@cache` 装饰器是否正确应用

- **问题**: TDengine 缓存失败
  - **解决**: 系统会自动降级到仅 L1 缓存，这是正常的

---

### 任务 3.2: 验证 TDengine 缓存连接 (30分钟)

**目标**: 确保 TDengine L2 缓存可用或正确降级

**步骤**:
```bash
# 1. 检查 TDengine 连接状态
cd /opt/claude/mystocks_phase6_cache
python3 << 'PY'
import os
from web.backend.app.core.tdengine_manager import get_tdengine_manager

tdengine = get_tdengine_manager()
if tdengine:
    print("✅ TDengine 可用")
    print(f"连接信息: {tdengine.conn}")
else:
    print("⚠️ TDengine 不可用，系统在 PostgreSQL-only 模式")
    print("缓存系统将使用 L1 内存缓存")
PY

# 2. 测试 TDengine 缓存写入（如果可用）
python3 << 'PY'
try:
    from src.core.cache.multi_level import MultiLevelCacheManager

    cache_mgr = MultiLevelCacheManager()

    # 写入测试数据
    test_key = "test:cache:key"
    test_value = {"data": "test", "timestamp": 1234567890}

    cache_mgr.set(test_key, test_value, ttl=60)

    # 读取测试数据
    result = cache_mgr.get(test_key)

    if result == test_value:
        print("✅ TDengine 缓存读写正常")
    else:
        print(f"❌ 缓存数据不匹配: {result} != {test_value}")

except Exception as e:
    print(f"⚠️ TDengine 缓存测试失败: {e}")
    print("系统将使用 L1 内存缓存")
PY

# 3. 检查缓存日志
tail -100 /opt/claude/mystocks_phase6_cache/logs/*.log 2>/dev/null | grep -i cache | tail -20
```

**验收标准**:
- ✅ TDengine 连接正常（如果可用）
- ✅ 缓存读写功能正常
- ✅ TDengine 不可用时正确降级到 L1 缓存
- ✅ 日志记录清晰

**可能的问题**:
- **问题**: TDengine 连接超时
  - **解决**: 系统会自动降级，这是预期的行为

- **问题**: 缓存读写失败
  - **解决**: 检查 TDengine 服务状态，或调整缓存配置

---

### 任务 3.3: 优化缓存命中率 (1.5小时)

**目标**: 提升缓存命中率到 80% 以上

**分析当前缓存性能**:
```bash
# 1. 查看当前缓存指标
curl -s http://localhost:8000/metrics | grep cache

# 应该看到:
# cache_hits_total - 缓存命中次数
# cache_misses_total - 缓存未命中次数
# cache_hit_rate - 缓存命中率

# 2. 计算当前命中率
python3 << 'PY'
import requests
import re

response = requests.get('http://localhost:8000/metrics')
metrics = response.text

# 提取缓存命中和未命中次数
hits = 0
misses = 0

for line in metrics.split('\n'):
    if 'cache_hits_total' in line and not line.startswith('#'):
        hits = int(line.split()[1])
    elif 'cache_misses_total' in line and not line.startswith('#'):
        misses = int(line.split()[1])

total = hits + misses
if total > 0:
    hit_rate = (hits / total) * 100
    print(f"缓存命中率: {hit_rate:.1f}%")
    print(f"命中次数: {hits}")
    print(f"未命中次数: {misses}")
    print(f"总请求: {total}")
else:
    print("⚠️ 暂无缓存数据")
PY

# 3. 运行缓存命中率测试脚本
cd /opt/claude/mystocks_phase6_cache
python3 << 'PY'
import requests
import time
import random

symbols = ['000001', '000002', '600000', '600519', '000858']
num_requests = 100

print(f"测试缓存命中率（{num_requests} 次请求）...")

for i in range(num_requests):
    symbol = random.choice(symbols)
    response = requests.get(f'http://localhost:8000/api/v1/market/symbols?symbol={symbol}')

    if i % 20 == 0:
        print(f"进度: {i}/{num_requests}")

print("\n测试完成，检查缓存指标...")
PY

# 4. 重新检查缓存命中率
curl -s http://localhost:8000/metrics | grep cache
```

**优化策略**:

如果命中率低于 80%，应用以下优化：

```bash
# 优化 1: 增加缓存 TTL
# 编辑 src/core/cache/decorators.py:
# 增加默认 TTL 从 300 秒到 600 秒

# 优化 2: 预热缓存
python3 << 'PY'
import requests

# 预加载常用数据到缓存
symbols = ['000001', '000002', '600000', '600519', '000858']

print("预热缓存...")
for symbol in symbols:
    response = requests.get(f'http://localhost:8000/api/v1/market/symbols?symbol={symbol}')
    print(f"加载 {symbol}: {response.status_code}")

print("缓存预热完成")
PY

# 优化 3: 调整缓存策略
# 编辑 src/core/cache/multi_level.py:
# - 增加 L1 缓存大小
# - 优化 LRU 淘汰策略
# - 增加缓存预加载逻辑
```

**验收标准**:
- ✅ 缓存命中率 > 80%
- ✅ 缓存未命中次数 < 20%
- ✅ 缓存响应时间 < 10ms（p95）

**可能的问题**:
- **问题**: 命中率持续低于 50%
  - **解决**: 检查缓存键是否正确，可能是每次请求使用不同的键

- **问题**: 缓存占用内存过大
  - **解决**: 减小缓存大小或缩短 TTL

---

### 任务 3.4: 测试断路器模式 (45分钟)

**目标**: 验证断路器正确工作，系统可以优雅降级

**步骤**:
```bash
# 1. 运行断路器测试
cd /opt/claude/mystocks_phase6_cache
python3 << 'PY'
from src.core.cache.multi_level import MultiLevelCacheManager
import time

cache_mgr = MultiLevelCacheManager()

print("测试断路器模式...")

# 模拟 TDengine 故障
# 1. 正常写入
try:
    cache_mgr.set("test:1", {"data": "value1"}, ttl=60)
    print("✅ 正常写入成功")
except Exception as e:
    print(f"❌ 写入失败: {e}")

# 2. 测试读取（应该在 L1 缓存中命中）
result = cache_mgr.get("test:1")
if result:
    print(f"✅ L1 缓存读取成功: {result}")
else:
    print("❌ L1 缓存读取失败")

# 3. 测试降级机制
# 即使 TDengine 不可用，L1 缓存仍应工作
print("\n✅ 断路器测试完成")
PY

# 2. 压力测试 TDengine 故障场景
# 停止 TDengine（如果正在运行）
# docker stop tdengine  # 如果使用 Docker

# 3. 验证系统仍能正常工作（仅 L1 缓存）
python3 << 'PY'
import requests

print("测试 TDengine 故障时的降级...")

for i in range(10):
    try:
        response = requests.get('http://localhost:8000/api/v1/market/symbols?symbol=000001')
        if response.status_code == 200:
            print(f"✅ 请求 {i+1} 成功（L1 缓存降级）")
        else:
            print(f"⚠️ 请求 {i+1} 返回 {response.status_code}")
    except Exception as e:
        print(f"❌ 请求 {i+1} 失败: {e}")

print("\n降级测试完成")
PY

# 4. 恢复 TDengine（如果停止了）
# docker start tdengine
```

**验收标准**:
- ✅ 断路器正确触发（TDengine 故障时）
- ✅ 系统自动降级到 L1 缓存
- ✅ 没有服务中断或错误
- ✅ 日志记录清晰的降级信息

**可能的问题**:
- **问题**: 断路器未触发
  - **解决**: 检查 `src/core/cache/multi_level.py` 中断路器配置

- **问题**: 降级后性能严重下降
  - **解决**: 这是正常的，L1 缓存仍然提供加速

---

### 任务 3.5: 压力测试 (1.5小时)

**目标**: 1000 并发用户下系统稳定运行

**步骤**:
```bash
# 1. 安装 Locust（负载测试工具）
pip install locust

# 2. 创建 Locust 测试脚本
cd /opt/claude/mystocks_phase6_cache
cat > cache_loadtest.py << 'PY'
from locust import HttpUser, task, between

class CacheUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # 登录（如果需要）
        pass

    @task(3)
    def get_market_data(self):
        """获取市场数据（高频操作）"""
        symbols = ['000001', '000002', '600000', '600519']
        symbol = random.choice(symbols)
        self.client.get(f"/api/v1/market/symbols?symbol={symbol}")

    @task(2)
    def get_kline_data(self):
        """获取 K 线数据"""
        self.client.get("/api/v1/market/kline?symbol=000001&interval=1d&limit=100")

    @task(1)
    def get_health(self):
        """健康检查"""
        self.client.get("/health")
PY

# 3. 运行负载测试（100 并发用户）
# 注意：先启动后端服务
cd /opt/claude/mystocks_phase6_cache/web/backend
ADMIN_PASSWORD=password python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

cd /opt/claude/mystocks_phase6_cache

echo "启动负载测试（100 用户，持续 2 分钟）..."
locust -f cache_loadtest.py --headless \
  -u 100 \
  -r 10 \
  -t 2m \
  -H http://localhost:8000 \
  --html cache_loadtest_report.html

# 4. 检查测试结果
echo "查看负载测试报告:"
ls -lh cache_loadtest_report.html

# 5. 测试更高负载（1000 用户）
echo "启动高负载测试（1000 用户，持续 1 分钟）..."
locust -f cache_loadtest.py --headless \
  -u 1000 \
  -r 50 \
  -t 1m \
  -H http://localhost:8000 \
  --html cache_loadtest_high_concurrency_report.html

# 6. 监控系统资源
# 在另一个终端运行:
# htop
# 或
# docker stats
```

**验收标准**:
- ✅ 100 并发用户测试通过
- ✅ 1000 并发用户测试完成（允许部分失败 < 5%）
- ✅ 响应时间 p95 < 500ms（100 用户）
- ✅ 响应时间 p95 < 2000ms（1000 用户）
- ✅ 没有内存泄漏或崩溃
- ✅ 缓存命中率保持 > 60%

**可能的问题**:
- **问题**: 响应时间过长
  - **解决**: 增加缓存大小，优化缓存键设计

- **问题**: 后端服务崩溃
  - **解决**: 减少并发数，检查内存使用

---

### 任务 3.6: 性能基准测试和对比 (1小时)

**目标**: 量化缓存性能提升

**步骤**:
```bash
# 1. 运行性能基准测试脚本
cd /opt/claude/mystocks_phase6_cache
python tests/performance/benchmark.py

# 2. 对比缓存启用 vs 禁用性能
# 创建对比测试脚本:
cat > cache_benchmark.py << 'PY'
import requests
import time
import statistics

def benchmark_api(url, num_requests=100):
    """API 性能基准测试"""
    latencies = []

    for i in range(num_requests):
        start = time.time()
        response = requests.get(url)
        latency = time.time() - start
        latencies.append(latency)

        if i % 20 == 0:
            print(f"进度: {i}/{num_requests}")

    return {
        'p50': statistics.median(latencies),
        'p95': sorted(latencies)[int(len(latencies) * 0.95)],
        'p99': sorted(latencies)[int(len(latencies) * 0.99)],
        'avg': sum(latencies) / len(latencies),
        'min': min(latencies),
        'max': max(latencies)
    }

print("性能基准测试（100 次请求）...")
print("="*50)

# 测试 1: 常缓存
print("\n测试 1: 启用缓存")
result_cached = benchmark_api('http://localhost:8000/api/v1/market/symbols?symbol=000001')
for key, value in result_cached.items():
    print(f"{key}: {value*1000:.2f}ms")

print("\n" + "="*50)
print("性能提升:")
p50_speedup = (result_cached['p50'] / result_cached['p50'])
p95_speedup = (result_cached['p95'] / result_cached['p95'])
print(f"p50 加速比: {p50_speedup:.1f}x")
print(f"p95 加速比: {p95_speedup:.1f}x")
PY

python3 cache_benchmark.py

# 3. 生成性能对比报告
cat > CACHE_PERFORMANCE_REPORT.md << 'EOF'
# 缓存性能优化报告

## 测试环境
- CPU: [CPU信息]
- Memory: [内存信息]
- Python 版本: [版本]
- 并发数: [数量]

## 性能指标
### 响应时间
| 指标 | 无缓存 | 有缓存 | 加速比 |
|------|--------|--------|--------|
| p50  | [ms]   | [ms]   | [x]    |
| p95  | [ms]   | [ms]   | [x]    |
| p99  | [ms]   | [ms]   | [x]    |
| 平均 | [ms]   | [ms]   | [x]    |

### 吞吐量
- 无缓存: [RPS]
- 有缓存: [RPS]
- 提升: [x]倍

### 缓存效率
- 命中率: [百分比]%
- 未命中率: [百分比]%
- 平均缓存大小: [MB]

### 负载测试结果
#### 100 并发用户
- 响应时间 p95: [ms]
- 错误率: [百分比]%
- RPS: [请求数/秒]

#### 1000 并发用户
- 响应时间 p95: [ms]
- 错误率: [百分比]%
- RPS: [请求数/秒]

## 优化措施
[记录应用的优化措施]

## 问题和解决方案
[记录遇到的问题和解决方案]

## 进一步优化建议
[基于测试结果的改进建议]
