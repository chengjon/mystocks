"""
Redis Services Usage Examples
=============================

三数据库架构中Redis服务的使用示例。

Version: 1.0.0
"""

# ===================================
# 1. L2 缓存服务示例
# ===================================

from app.services.redis import redis_cache

# 1.1 基础缓存操作
def basic_cache_example():
    # 设置缓存
    redis_cache.set("key", {"data": "value"}, ttl=3600)

    # 获取缓存
    data = redis_cache.get("key")
    if data:
        print(f"Cache hit: {data}")

    # 删除缓存
    redis_cache.delete("key")

    # 检查缓存是否存在
    exists = redis_cache.exists("key")

# 1.2 指标计算结果缓存
def indicator_cache_example():
    stock_code = "000001"
    indicator_code = "SMA"
    params = {"timeperiod": 20}

    # 尝试从缓存获取
    cached_result = redis_cache.get_cached_indicator_result(
        stock_code, indicator_code, params
    )

    if cached_result:
        print(f"Cache hit! Using cached result: {cached_result}")
    else:
        # 缓存未命中，执行计算
        result = calculate_indicator(stock_code, indicator_code, params)

        # 缓存结果 (1小时过期)
        redis_cache.cache_indicator_result(
            stock_code, indicator_code, params, result, ttl=3600
        )

# 1.3 API响应缓存
def api_cache_example():
    endpoint = "/api/stocks/000001"
    params = {"start_date": "2024-01-01"}

    # 尝试从缓存获取
    cached_response = redis_cache.get_cached_api_response(endpoint, params)

    if cached_response:
        return cached_response

    # 缓存未命中，调用API
    response = call_api(endpoint, params)

    # 缓存响应 (5分钟过期)
    redis_cache.cache_api_response(endpoint, params, response, ttl=300)

    return response

# 1.4 批量操作
def batch_cache_example():
    # 批量设置
    data = {
        "key1": {"value": 1},
        "key2": {"value": 2},
        "key3": {"value": 3}
    }
    redis_cache.mset(data, ttl=3600)

    # 批量获取
    keys = ["key1", "key2", "key3"]
    results = redis_cache.mget(keys)
    print(results)

    # 删除匹配模式的所有缓存
    deleted_count = redis_cache.delete_pattern("indicator:*")

# ===================================
# 2. 消息总线服务示例
# ===================================

from app.services.redis import redis_pubsub

# 2.1 发布消息
def publish_example():
    # 发布指标计算完成事件
    redis_pubsub.publish_indicator_calculated(
        stock_code="000001",
        indicator_code="MACD",
        params={"fastperiod": 12, "slowperiod": 26},
        success=True
    )

    # 发布价格更新事件
    redis_pubsub.publish_price_update(
        stock_code="000001",
        price=10.50,
        change=0.50,
        change_pct=5.0
    )

    # 发布任务状态更新
    redis_pubsub.publish_task_updated(
        task_id="daily_calc_20240110",
        status="running",
        progress=45.5
    )

# 2.2 订阅消息
def subscribe_example():
    def indicator_handler(message):
        print(f"Indicator calculated: {message}")

    def price_handler(message):
        print(f"Price updated: {message}")
        # 触发WebSocket推送
        notify_clients(message)

    # 订阅频道
    redis_pubsub.subscribe("indicator:calculated", indicator_handler)
    redis_pubsub.subscribe("price:update", price_handler)

    # 启动监听 (在单独线程中运行)
    redis_pubsub.start_listening()

# 2.3 异步发布
import asyncio

async def async_publish_example():
    await redis_pubsub.async_publish(
        "custom:channel",
        {"message": "Hello World"}
    )

# ===================================
# 3. 分布式锁服务示例
# ===================================

from app.services.redis import redis_lock

# 3.1 基础锁操作
def basic_lock_example():
    resource = "my_resource"

    # 获取锁
    token = redis_lock.acquire(resource, timeout=30, blocking=True)

    if token:
        try:
            # 执行临界区代码
            do_something_critical()
        finally:
            # 释放锁
            redis_lock.release(resource, token)

# 3.2 上下文管理器 (推荐)
def context_manager_example():
    resource = "my_resource"

    with redis_lock.lock(resource, timeout=30):
        # 临界区代码
        do_something_critical()
        # 自动释放锁

# 3.3 指标计算锁 (防止重复计算)
def indicator_calculation_example():
    stock_code = "000001"
    indicator_code = "MACD"
    params = {"fastperiod": 12, "slowperiod": 26}

    with redis_lock.indicator_calculation_lock(stock_code, indicator_code, params):
        # 如果已有实例在计算此指标，会阻塞等待
        # 计算完成后直接使用结果
        result = calculate_indicator(stock_code, indicator_code, params)

        # 自动保存到缓存
        redis_cache.cache_indicator_result(
            stock_code, indicator_code, params, result
        )

        return result

# 3.4 批量任务锁
def batch_task_example():
    task_id = "daily_calc_20240110"

    with redis_lock.batch_task_lock(task_id):
        # 防止任务重复执行
        run_daily_calculation()

# 3.5 资源更新锁
def resource_update_example():
    resource_type = "data_source"
    resource_id = "akshare"

    with redis_lock.resource_update_lock(resource_type, resource_id):
        # 防止并发修改
        update_data_source_config(resource_id)

# ===================================
# 4. 综合应用示例
# ===================================

def indicator_calculation_with_redis(stock_code, indicator_code, params):
    """
    完整的指标计算流程 (使用Redis三件套)

    流程:
    1. 检查缓存 (L2 Cache)
    2. 获取计算锁 (Distributed Lock)
    3. 执行计算
    4. 缓存结果 (L2 Cache)
    5. 发布完成事件 (Pub/Sub)
    """

    # 1. 检查缓存
    cached = redis_cache.get_cached_indicator_result(stock_code, indicator_code, params)
    if cached:
        print("✅ Cache hit - returning cached result")
        return cached

    # 2. 获取计算锁 (防止重复计算)
    with redis_lock.indicator_calculation_lock(stock_code, indicator_code, params):
        # 双重检查缓存 (可能在等待锁时已被其他实例计算)
        cached = redis_cache.get_cached_indicator_result(stock_code, indicator_code, params)
        if cached:
            print("✅ Cache hit after lock - returning cached result")
            return cached

        # 3. 执行计算
        print(f"⚙️ Calculating {indicator_code} for {stock_code}...")
        result = calculate_indicator(stock_code, indicator_code, params)

        # 4. 缓存结果
        redis_cache.cache_indicator_result(
            stock_code, indicator_code, params, result, ttl=3600
        )
        print("✅ Result cached")

        # 5. 发布完成事件
        redis_pubsub.publish_indicator_calculated(
            stock_code=stock_code,
            indicator_code=indicator_code,
            params=params,
            success=True
        )
        print("📢 Event published")

        return result


# 辅助函数
def calculate_indicator(stock_code, indicator_code, params):
    """模拟指标计算"""
    return {"value": 123.45, "timestamp": "2024-01-10"}


def call_api(endpoint, params):
    """模拟API调用"""
    return {"data": "response"}


def do_something_critical():
    """模拟临界区代码"""
    pass


def run_daily_calculation():
    """模拟批量任务"""
    pass


def update_data_source_config(resource_id):
    """模拟配置更新"""
    pass
