# Subtask 2.2: 实现缓存读写逻辑 - 实现计划

**任务编号**: 2.2
**任务名称**: 实现缓存读写逻辑
**优先级**: CRITICAL (P0-架构)
**预计时长**: 2-3 天
**状态**: 待开始

---

## 📋 任务概述

在 Task 2.1 (TDengine 服务搭建) 完成的基础上，实现缓存的读写逻辑，包括：

1. **缓存读取接口**: `fetch_from_cache()` - 从 TDengine 读取缓存数据
2. **缓存写入接口**: `write_to_cache()` - 将数据写入 TDengine 缓存
3. **缓存失效机制**: 自动清理过期数据、手动失效接口
4. **批量操作支持**: 批量读/写，性能优化
5. **数据管理器集成**: 与现有 DataManager 无缝集成

---

## 🎯 验收标准

### 必须完成
- [ ] `CacheManager` 类实现 (包含 fetch/write 方法)
- [ ] 与 TDengineManager 的完整集成
- [ ] 批量读/写支持 (性能 > 100 ops/sec)
- [ ] 缓存失效机制 (自动 + 手动)
- [ ] 单元测试 (≥20 个测试用例)
- [ ] 集成测试与现有数据访问层
- [ ] 完整的 API 文档和使用示例
- [ ] 性能基准测试

### 可选优化
- [ ] 缓存预热机制
- [ ] 异步写入支持
- [ ] 缓存命中率统计
- [ ] Redis 作为二级缓存

---

## 🏗️ 架构设计

### 缓存层次结构

```
API 请求
    ↓
CacheManager (new)
    ├─ fetch_from_cache()     ← 一级缓存 (TDengine)
    ├─ write_to_cache()
    ├─ invalidate_cache()
    └─ batch_operations()
    ↓
TDengineManager (existing)
    ├─ read_cache()
    ├─ write_cache()
    └─ clear_expired_cache()
    ↓
TDengine (time-series database)
```

### 缓存密钥结构

```python
# 设计缓存键
cache_key_format = "{data_type}:{symbol}:{timeframe}"

# 例子:
fund_flow:000001:1d
etf:000858:1w
chip_race:000001:3d

# 带时间范围的查询
cache_query = {
    "symbol": "000001",
    "data_type": "fund_flow",
    "timeframe": "1d",
    "start_date": "2025-11-01",  # 可选
    "end_date": "2025-11-06"      # 可选
}
```

### 缓存流程 (Cache-Aside Pattern)

```
读操作:
1. 检查 TDengine 缓存 (Cache.fetch())
2. 如果命中 (hit) → 返回数据
3. 如果未命中 (miss):
   a. 从源数据获取 (DataManager.load())
   b. 写入缓存 (Cache.write())
   c. 返回数据

写操作:
1. 保存到数据库 (DataManager.save())
2. 写入缓存 (Cache.write())
3. 返回成功状态
```

---

## 📝 实现步骤

### Phase 1: 缓存管理器设计 (Day 1 上午)

#### 1.1 创建 `CacheManager` 类

**文件**: `web/backend/app/core/cache_manager.py`

```python
class CacheManager:
    """缓存管理器 - 统一缓存接口"""

    def __init__(self, tdengine_manager=None):
        """初始化缓存管理器"""
        self.tdengine = tdengine_manager or get_tdengine_manager()
        self.logger = structlog.get_logger()

    # 核心方法
    def fetch_from_cache(self, symbol: str, data_type: str,
                        timeframe: str = None, days: int = 1) -> Optional[Dict]:
        """从缓存读取数据"""
        # 实现缓存读取逻辑
        pass

    def write_to_cache(self, symbol: str, data_type: str,
                      timeframe: str, data: Dict, ttl_days: int = 7) -> bool:
        """写入数据到缓存"""
        # 实现缓存写入逻辑
        pass

    def invalidate_cache(self, symbol: str = None, data_type: str = None) -> int:
        """清除特定的缓存"""
        # 清除缓存逻辑
        pass

    def batch_read(self, queries: List[Dict]) -> Dict:
        """批量读取缓存"""
        # 批量读取逻辑
        pass

    def batch_write(self, records: List[Dict]) -> int:
        """批量写入缓存"""
        # 批量写入逻辑
        pass

    # 辅助方法
    def get_cache_key(self, symbol: str, data_type: str, timeframe: str) -> str:
        """生成缓存键"""
        pass

    def is_cache_valid(self, symbol: str, data_type: str) -> bool:
        """检查缓存有效性"""
        pass
```

#### 1.2 设计单例工厂

```python
# 全局实例
_cache_manager: Optional[CacheManager] = None

def get_cache_manager() -> CacheManager:
    """获取缓存管理器单例"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager
```

---

### Phase 2: 缓存读写实现 (Day 1 下午 - Day 2 上午)

#### 2.1 实现 `fetch_from_cache()`

```python
def fetch_from_cache(self, symbol: str, data_type: str,
                    timeframe: str = None, days: int = 1) -> Optional[Dict]:
    """从缓存读取数据

    实现 Cache-Aside 模式的读操作
    """
    try:
        # 1. 尝试从 TDengine 读取
        cache_data = self.tdengine.read_cache(
            symbol=symbol,
            data_type=data_type,
            timeframe=timeframe,
            days=days
        )

        if cache_data:
            self.logger.info(
                "✅ 缓存命中",
                symbol=symbol,
                data_type=data_type
            )
            # 增加命中计数
            return {
                "data": cache_data,
                "source": "cache",
                "timestamp": datetime.utcnow().isoformat()
            }

        self.logger.debug(
            "⚠️ 缓存未命中",
            symbol=symbol,
            data_type=data_type
        )
        return None

    except Exception as e:
        self.logger.error(
            "❌ 缓存读取失败",
            symbol=symbol,
            error=str(e)
        )
        return None
```

#### 2.2 实现 `write_to_cache()`

```python
def write_to_cache(self, symbol: str, data_type: str,
                  timeframe: str, data: Dict, ttl_days: int = 7) -> bool:
    """写入数据到缓存"""
    try:
        # 1. 验证数据
        if not data or not isinstance(data, dict):
            self.logger.warning("Invalid cache data", data=data)
            return False

        # 2. 增加元数据
        enriched_data = {
            **data,
            "_cached_at": datetime.utcnow().isoformat(),
            "_ttl_days": ttl_days,
            "_source": "market_data"
        }

        # 3. 写入 TDengine
        result = self.tdengine.write_cache(
            symbol=symbol,
            data_type=data_type,
            timeframe=timeframe,
            data=enriched_data
        )

        if result:
            self.logger.info(
                "✅ 数据已缓存",
                symbol=symbol,
                data_type=data_type
            )
            return True
        else:
            self.logger.error("❌ 缓存写入失败")
            return False

    except Exception as e:
        self.logger.error(
            "❌ 缓存写入异常",
            symbol=symbol,
            error=str(e)
        )
        return False
```

#### 2.3 实现 `batch_read()` 和 `batch_write()`

```python
def batch_read(self, queries: List[Dict]) -> Dict:
    """批量读取缓存 - 提高性能"""
    results = {}
    for query in queries:
        symbol = query.get("symbol")
        data_type = query.get("data_type")

        data = self.fetch_from_cache(
            symbol=symbol,
            data_type=data_type,
            timeframe=query.get("timeframe"),
            days=query.get("days", 1)
        )

        results[f"{symbol}:{data_type}"] = data

    return results

def batch_write(self, records: List[Dict]) -> int:
    """批量写入缓存"""
    count = 0
    for record in records:
        if self.write_to_cache(
            symbol=record["symbol"],
            data_type=record["data_type"],
            timeframe=record.get("timeframe", "1d"),
            data=record.get("data", {})
        ):
            count += 1

    self.logger.info(f"✅ 批量写入完成: {count}/{len(records)} 记录")
    return count
```

---

### Phase 3: 集成与失效 (Day 2 下午)

#### 3.1 实现缓存失效机制

```python
def invalidate_cache(self, symbol: str = None, data_type: str = None) -> int:
    """清除特定的缓存

    如果不指定 symbol/data_type，则清除所有缓存
    """
    try:
        if symbol and data_type:
            # 清除特定符号+数据类型的缓存
            sql = f"""
                DELETE FROM market_data_cache
                WHERE symbol = '{symbol}' AND data_type = '{data_type}'
            """
        elif symbol:
            # 清除特定符号的所有缓存
            sql = f"DELETE FROM market_data_cache WHERE symbol = '{symbol}'"
        else:
            # 清除所有缓存
            sql = "DELETE FROM market_data_cache"

        self.tdengine._execute(sql)
        self.logger.info(
            "✅ 缓存已清除",
            symbol=symbol,
            data_type=data_type
        )
        return 1

    except Exception as e:
        self.logger.error("❌ 缓存清除失败", error=str(e))
        return 0
```

#### 3.2 与 DataManager 集成

```python
# 在 DataManager 中添加缓存支持

class DataManager:
    def __init__(self):
        self.cache = get_cache_manager()

    def fetch_with_cache(self, symbol: str, data_type: str,
                        use_cache: bool = True) -> Dict:
        """读取数据 - 优先使用缓存"""

        # 1. 尝试从缓存读取
        if use_cache:
            cache_data = self.cache.fetch_from_cache(symbol, data_type)
            if cache_data:
                return cache_data

        # 2. 从源数据读取
        source_data = self.load_from_source(symbol, data_type)

        # 3. 写入缓存
        if source_data:
            self.cache.write_to_cache(symbol, data_type, "1d", source_data)

        return source_data

    def save_with_cache(self, symbol: str, data_type: str, data: Dict) -> bool:
        """保存数据 - 同时更新缓存"""

        # 1. 保存到数据库
        if not self.save_to_database(symbol, data_type, data):
            return False

        # 2. 更新缓存
        self.cache.write_to_cache(symbol, data_type, "1d", data)

        return True
```

---

### Phase 4: 测试 (Day 2 下午 - Day 3 上午)

#### 4.1 单元测试

**文件**: `web/backend/tests/test_cache_manager.py`

```python
class TestCacheManager:
    """缓存管理器单元测试"""

    def test_fetch_from_cache_hit(self):
        """测试缓存命中"""
        # 1. 写入缓存
        # 2. 读取缓存
        # 3. 验证数据匹配
        pass

    def test_fetch_from_cache_miss(self):
        """测试缓存未命中"""
        # 验证返回 None
        pass

    def test_write_to_cache(self):
        """测试缓存写入"""
        # 1. 写入数据
        # 2. 读取验证
        # 3. 检查元数据
        pass

    def test_batch_operations(self):
        """测试批量操作"""
        # 1. 批量写入 10 个记录
        # 2. 批量读取
        # 3. 验证数据完整性
        pass

    def test_cache_invalidation(self):
        """测试缓存失效"""
        # 1. 写入缓存
        # 2. 清除缓存
        # 3. 验证数据已删除
        pass

    def test_performance_benchmark(self):
        """性能基准测试"""
        # 测试 100 次读写操作
        # 验证 QPS > 100 ops/sec
        pass
```

#### 4.2 集成测试

```python
class TestCacheIntegration:
    """缓存集成测试"""

    def test_cache_aside_pattern(self):
        """测试 Cache-Aside 模式"""
        # 1. 清除缓存
        # 2. 首次读取 (从源读取+写入缓存)
        # 3. 第二次读取 (从缓存读取)
        # 4. 验证数据一致性
        pass

    def test_datamanager_integration(self):
        """测试与 DataManager 的集成"""
        # 1. 通过 DataManager 写入
        # 2. 验证缓存已更新
        # 3. 通过 DataManager 读取
        # 4. 验证缓存命中
        pass

    def test_cache_ttl(self):
        """测试 TTL 机制"""
        # 1. 写入 TTL=1 天的数据
        # 2. 验证可以读取
        # 3. 模拟时间推进
        # 4. 验证过期清理
        pass
```

---

## 📊 文件列表

### 新增文件

| 文件 | 行数 | 说明 |
|------|------|------|
| `web/backend/app/core/cache_manager.py` | 400+ | 缓存管理器主类 |
| `web/backend/app/core/cache_utils.py` | 150+ | 缓存工具函数 |
| `web/backend/tests/test_cache_manager.py` | 500+ | 缓存管理器测试 |
| `web/backend/tests/test_cache_integration.py` | 300+ | 集成测试 |

### 修改文件

| 文件 | 变更 | 说明 |
|------|------|------|
| `web/backend/app/data_manager.py` | +50 L | 添加缓存集成方法 |
| `web/backend/app/core/__init__.py` | +5 L | 导出 CacheManager |

---

## 🧪 测试计划

### 单元测试 (15 个)
- ✅ 缓存读取命中/未命中 (2)
- ✅ 缓存写入成功/失败 (2)
- ✅ 缓存键生成 (1)
- ✅ 批量读/写 (2)
- ✅ 缓存失效 (2)
- ✅ 错误处理 (2)
- ✅ 特殊字符处理 (1)
- ✅ 大数据处理 (1)

### 集成测试 (8 个)
- ✅ Cache-Aside 模式 (1)
- ✅ DataManager 集成 (1)
- ✅ TTL 机制 (1)
- ✅ 并发读写 (1)
- ✅ 缓存一致性 (1)
- ✅ 性能基准 (2)
- ✅ 端到端流程 (1)

**总计**: 23 个测试用例

---

## 📈 性能目标

| 指标 | 目标 | 说明 |
|------|------|------|
| 缓存读延迟 | <5ms | 单次读取 |
| 缓存写延迟 | <10ms | 单次写入 |
| 批量吞吐 | >1000 ops/sec | 100 条记录批量操作 |
| 缓存命中率 | ≥80% | 生产环境目标 |
| 内存占用 | <500MB | TDengine 进程 |

---

## ⚡ 实现时间表

| Phase | 任务 | 预计时长 | 完成日期 |
|-------|------|---------|---------|
| 1 | 设计与规划 | 4 小时 | Day 1 AM |
| 2 | 核心实现 | 8 小时 | Day 1-2 |
| 3 | 集成与失效 | 4 小时 | Day 2 PM |
| 4 | 测试与验证 | 4 小时 | Day 3 AM |
| 总计 | | 20 小时 | 2-3 天 |

---

## 📋 代码清单检查

### 必须实现
- [ ] CacheManager 类定义
- [ ] fetch_from_cache() 方法
- [ ] write_to_cache() 方法
- [ ] invalidate_cache() 方法
- [ ] batch_read() 方法
- [ ] batch_write() 方法
- [ ] 缓存键生成函数
- [ ] 错误处理和日志记录

### 必须测试
- [ ] 15 个单元测试通过
- [ ] 8 个集成测试通过
- [ ] 性能基准验证 (>100 ops/sec)
- [ ] 缓存命中率验证 (≥80%)

### 必须文档化
- [ ] CacheManager API 文档
- [ ] 使用示例代码
- [ ] 与 DataManager 集成指南
- [ ] 性能调优建议

---

## 🔄 后续任务依赖

### 此任务完成后解锁
- Task 2.3: 时间窗口淘汰策略
- Task 2.4: 缓存预热和监控
- Task 5: 双库数据一致性方案
- Task 8: 实时数据更新机制

---

## 📚 参考资源

### 相关代码
- `web/backend/app/core/tdengine_manager.py` - TDengine 驱动
- `web/backend/app/data_manager.py` - 数据管理层
- `TDENGINE_QUICK_REFERENCE.md` - TDengine API 参考

### 设计模式
- Cache-Aside Pattern
- Singleton Pattern
- Factory Pattern
- Decorator Pattern (错误处理)

---

## ✅ 完成标准

- ✅ 所有代码通过 PEP8 检查
- ✅ 所有方法有完整的类型提示
- ✅ 所有公共方法有详细的文档字符串
- ✅ 23 个测试全部通过 (100%)
- ✅ 性能指标达成
- ✅ 与 TDengineManager 的完整集成
- ✅ 与 DataManager 的无缝集成
- ✅ 完整的用户文档

---

*计划生成: 2025-11-06*
*Subtask 2.2: 实现缓存读写逻辑*
*预计完成: 2025-11-09*
