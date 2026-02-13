"""
用户体验监控指标 - User Experience Monitoring Metrics
提供用户体验相关的核心监控指标：响应时间、成功率、系统资源、页面加载时间
"""

import time

import psutil
from prometheus_client import Counter, Gauge, Histogram, generate_latest

# ==================== 用户体验核心指标 ====================

# 1. 接口响应时间指标（用户体验关键）
API_RESPONSE_TIME = Histogram(
    "api_response_time_seconds",
    "API接口响应时间(秒) - 用户体验关键指标",
    ["endpoint", "method", "status_code"],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.0, 5.0, 10.0],  # 重点关注2秒以内
)

# 2. 接口成功率指标
API_SUCCESS_RATE = Gauge("api_success_rate", "API接口成功率(%) - 目标100%", ["endpoint", "time_window"])

# 3. 系统资源使用率（影响用户体验）
SYSTEM_CPU_USAGE = Gauge("system_cpu_usage_percent", "系统CPU使用率(%) - 阈值80%")

SYSTEM_MEMORY_USAGE = Gauge("system_memory_usage_percent", "系统内存使用率(%) - 阈值85%")

SYSTEM_DISK_USAGE = Gauge("system_disk_usage_percent", "系统磁盘使用率(%) - 数据目录")

# 4. 前端页面加载时间（用户直接感知）
PAGE_LOAD_TIME = Histogram(
    "page_load_time_seconds",
    "前端页面加载时间(秒) - 用户体验关键",
    ["page", "device_type"],
    buckets=[0.5, 1.0, 2.0, 3.0, 5.0, 10.0],  # 重点关注3秒以内
)

# 5. 数据库查询性能（间接影响用户体验）
DB_QUERY_TIME = Histogram(
    "db_query_time_seconds",
    "数据库查询时间(秒)",
    ["query_type", "table"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0],
)

# ==================== 告警相关指标 ====================

# 阈值超标计数器
THRESHOLD_VIOLATIONS = Counter(
    "threshold_violations_total",
    "阈值违规计数",
    ["metric_type", "severity", "threshold_value"],
)

# 用户体验健康状态
USER_EXPERIENCE_HEALTH = Gauge("user_experience_health_score", "用户体验健康评分(0-100) - 综合评估", ["component"])

# ==================== 监控工具类 ====================


class UserExperienceMonitor:
    """用户体验监控器"""

    def __init__(self):
        self.last_update = 0
        self.update_interval = 30  # 30秒更新一次系统指标

    def update_system_metrics(self):
        """更新系统资源指标"""
        current_time = time.time()
        if current_time - self.last_update < self.update_interval:
            return  # 避免过于频繁的更新

        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            SYSTEM_CPU_USAGE.set(cpu_percent)

            # 内存使用率
            memory = psutil.virtual_memory()
            SYSTEM_MEMORY_USAGE.set(memory.percent)

            # 磁盘使用率（监控数据目录）
            disk = psutil.disk_usage("/")
            SYSTEM_DISK_USAGE.set(disk.percent)

            self.last_update = current_time

        except Exception as e:
            print(f"Failed to update system metrics: {e}")

    def record_api_response(self, endpoint: str, method: str, status_code: int, response_time: float):
        """记录API响应"""
        API_RESPONSE_TIME.labels(endpoint=endpoint, method=method, status_code=str(status_code)).observe(response_time)

        # 检查是否超过2秒阈值
        if response_time > 2.0:
            THRESHOLD_VIOLATIONS.labels(
                metric_type="api_response_time",
                severity="warning" if response_time < 5.0 else "critical",
                threshold_value="2.0",
            ).inc()

    def record_page_load(self, page: str, load_time: float, device_type: str = "desktop"):
        """记录页面加载时间"""
        PAGE_LOAD_TIME.labels(page=page, device_type=device_type).observe(load_time)

        # 检查是否超过3秒阈值
        if load_time > 3.0:
            THRESHOLD_VIOLATIONS.labels(
                metric_type="page_load_time",
                severity="warning" if load_time < 5.0 else "critical",
                threshold_value="3.0",
            ).inc()

    def record_db_query(self, query_type: str, table: str, query_time: float):
        """记录数据库查询时间"""
        DB_QUERY_TIME.labels(query_type=query_type, table=table).observe(query_time)

    def calculate_success_rate(
        self,
        endpoint: str,
        success_count: int,
        total_count: int,
        time_window: str = "5m",
    ):
        """计算并记录成功率"""
        if total_count > 0:
            success_rate = (success_count / total_count) * 100
            API_SUCCESS_RATE.labels(endpoint=endpoint, time_window=time_window).set(success_rate)

            # 检查是否低于100%成功率
            if success_rate < 100.0:
                THRESHOLD_VIOLATIONS.labels(
                    metric_type="api_success_rate",
                    severity="warning" if success_rate > 95.0 else "critical",
                    threshold_value="100.0",
                ).inc()

    def update_health_score(self):
        """更新用户体验健康评分"""
        try:
            # 获取各项指标的健康状态
            scores = []

            # CPU健康评分（80%为满分）
            cpu_usage = SYSTEM_CPU_USAGE._value or 0
            cpu_score = max(0, 100 - (cpu_usage / 0.8) * 100)
            scores.append(cpu_score)

            # 内存健康评分（85%为满分）
            memory_usage = SYSTEM_MEMORY_USAGE._value or 0
            memory_score = max(0, 100 - (memory_usage / 0.85) * 100)
            scores.append(memory_score)

            # 计算综合健康评分
            if scores:
                overall_score = sum(scores) / len(scores)
                USER_EXPERIENCE_HEALTH.labels(component="system_resources").set(overall_score)
                USER_EXPERIENCE_HEALTH.labels(component="overall").set(overall_score)

        except Exception as e:
            print(f"Failed to calculate health score: {e}")


# ==================== 全局监控实例 ====================

# 创建全局用户体验监控器实例
ux_monitor = UserExperienceMonitor()

# ==================== FastAPI中间件 ====================


class UserExperienceMiddleware:
    """用户体验监控中间件"""

    def __init__(self, app):
        self.app = app
        self.ux_monitor = ux_monitor

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # 更新系统指标（定期）
        self.ux_monitor.update_system_metrics()

        # 更新健康评分
        self.ux_monitor.update_health_score()

        # 处理请求
        await self.app(scope, receive, send)


# ==================== 工具函数 ====================


def record_api_performance(endpoint: str, method: str, status_code: int, response_time: float):
    """便捷函数：记录API性能"""
    ux_monitor.record_api_response(endpoint, method, status_code, response_time)


def record_page_load_performance(page: str, load_time: float, device_type: str = "desktop"):
    """便捷函数：记录页面加载性能"""
    ux_monitor.record_page_load(page, load_time, device_type)


def record_db_query_performance(query_type: str, table: str, query_time: float):
    """便捷函数：记录数据库查询性能"""
    ux_monitor.record_db_query(query_type, table, query_time)


def update_api_success_rate(endpoint: str, success_count: int, total_count: int, time_window: str = "5m"):
    """便捷函数：更新API成功率"""
    ux_monitor.calculate_success_rate(endpoint, success_count, total_count, time_window)


def get_user_experience_metrics():
    """获取用户体验指标数据"""
    return generate_latest()


# ==================== 监控装饰器 ====================


def monitor_api_performance(endpoint_name: str):
    """API性能监控装饰器"""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                response_time = time.time() - start_time
                # 这里需要从请求上下文中获取method和status_code
                # 暂时使用默认值，后续完善
                record_api_performance(endpoint_name, "GET", 200, response_time)
                return result
            except Exception:
                response_time = time.time() - start_time
                record_api_performance(endpoint_name, "GET", 500, response_time)
                raise

        return wrapper

    return decorator


def monitor_db_query(query_type: str, table: str):
    """数据库查询监控装饰器"""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                query_time = time.time() - start_time
                record_db_query_performance(query_type, table, query_time)
                return result
            except Exception:
                query_time = time.time() - start_time
                record_db_query_performance(query_type, table, query_time)
                raise

        return wrapper

    return decorator
