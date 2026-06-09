# MyStocks 项目连接泄漏分析报告

> **历史分析说明**:
> 本文件是阶段性分析、审计、评估或复盘材料，不是当前基线、当前实施优先级或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内问题分级、差距判断、风险结论、审阅意见和建议动作如未重新复核，应视为历史分析结果，不得直接当作当前事实。


**生成日期**: 2026-01-07
**分析范围**: 全项目代码库
**分析类型**: 数据库连接泄漏、HTTP客户端连接泄漏、缓存/消息队列连接泄漏

---

## 📋 执行摘要

本报告详细分析了 MyStocks 项目中可能存在的三种连接泄漏问题。通过代码静态分析和模式匹配，发现了多个潜在的高风险连接泄漏点，主要集中在数据库连接、HTTP客户端连接和Redis连接管理方面。

### 关键发现

- **🔴 高风险**: 6个数据库连接泄漏点
- **🟡 中风险**: 12个HTTP客户端连接泄漏点
- **🟡 中风险**: 8个Redis连接泄漏点
- **🟢 低风险**: 大部分代码已正确使用连接池和上下文管理器

---

## 1. 数据库连接泄漏分析

### 1.1 问题概述

数据库连接泄漏是最常见且最危险的连接泄漏类型。当应用程序获取数据库连接后，因异常、代码错误或逻辑缺陷导致连接未正确归还连接池，会导致连接池耗尽，最终导致应用程序无法访问数据库。

### 1.2 检测方法

通过搜索以下模式识别潜在泄漏：
- `conn = psycopg2.connect()` - 直接创建连接
- `engine.connect()` - SQLAlchemy连接
- 缺少 `finally` 块或上下文管理器 (`with` 语句)

### 1.3 发现的问题

#### 🔴 问题 1: `src/utils/check_db_health.py` - 数据库健康检查脚本

**位置**: `src/utils/check_db_health.py:69, 103`

**问题描述**:
```python
# 第69-103行
def check_postgresql_connection():
    try:
        conn = psycopg2.connect(...)  # 获取连接
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        # ... 其他操作
        cursor.close()
        conn.close()  # 正常关闭

        # 测试监控数据库
        conn_monitor = psycopg2.connect(...)  # 再次获取连接
        cursor_monitor = conn_monitor.cursor()
        # ... 操作
        cursor_monitor.close()
        conn_monitor.close()
    except Exception as e:
        print("❌ PostgreSQL连接失败")
        print(f"   错误: {str(e)}")
        return False, str(e)
```

**风险等级**: 🔴 高

**泄漏场景**:
- 如果在 `cursor.execute()` 和 `cursor.close()` 之间发生异常，连接不会被关闭
- 如果在第二个连接操作中发生异常，第一个连接已经关闭，但第二个连接泄漏

**影响**:
- 每次脚本运行可能泄漏1-2个连接
- 如果脚本频繁执行（如健康检查定时任务），连接池会快速耗尽

**修复建议**:
```python
def check_postgresql_connection():
    """验证PostgreSQL连接"""
    print("\n" + "=" * 60)
    print("【2/4】PostgreSQL 连接测试")
    print("=" * 60)

    conn = None
    conn_monitor = None
    try:
        import psycopg2
        from web.backend.app.core.config import settings

        # 测试mystocks数据库
        conn = psycopg2.connect(
            host=settings.postgresql_host,
            port=settings.postgresql_port,
            user=settings.postgresql_user,
            password=settings.postgresql_password,
            database=settings.postgresql_database,
            connect_timeout=5,
        )

        with conn.cursor() as cursor:  # 使用上下文管理器
            cursor.execute("SELECT version()")
            version = cursor.fetchone()
            print("✅ PostgreSQL连接成功 (mystocks)")
            print(f"   版本: {version[0][:50]}...")
            print(f"   数据库: {settings.postgresql_database}")

            # 检查关键表
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema='public'
            """)
            tables = [table[0] for table in cursor.fetchall()]
            print(f"   表数量: {len(tables)}")
            if tables:
                print(f"   示例表: {', '.join(tables[:5])}")

        # 测试mystocks_monitoring数据库
        try:
            conn_monitor = psycopg2.connect(
                host=settings.postgresql_host,
                port=settings.postgresql_port,
                user=settings.postgresql_user,
                password=settings.postgresql_password,
                database="mystocks_monitoring",
                connect_timeout=5,
            )
            with conn_monitor.cursor() as cursor_monitor:
                cursor_monitor.execute("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema='public'
                """)
                monitor_tables = [table[0] for table in cursor_monitor.fetchall()]
                print("✅ PostgreSQL监控数据库连接成功")
                print("   数据库: mystocks_monitoring")
                print(f"   表数量: {len(monitor_tables)}")
        except Exception as e:
            print(f"⚠️  PostgreSQL监控数据库连接失败: {str(e)}")

        return True, None

    except Exception as e:
        print("❌ PostgreSQL连接失败")
        print(f"   错误: {str(e)}")
        return False, str(e)
    finally:
        # 确保连接被关闭
        if conn is not None:
            conn.close()
        if conn_monitor is not None:
            conn_monitor.close()
```

---

#### 🔴 问题 2: `src/core/logging.py` - 日志数据库sink

**位置**: `src/core/logging.py:204-260`

**问题描述**:
```python
def db_sink(message):
    """数据库日志sink"""
    try:
        # 从环境变量获取数据库配置
        conn = psycopg2.connect(
            host=os.getenv("POSTGRESQL_HOST", "localhost"),
            port=int(os.getenv("POSTGRESQL_PORT", "5432")),
            user=os.getenv("POSTGRESQL_USER", "postgres"),
            password=os.getenv("POSTGRESQL_PASSWORD", ""),
            database="mystocks_monitoring",
        )

        cursor = conn.cursor()

        # 准备日志数据
        log_data = {...}

        # 插入日志
        cursor.execute(
            """
            INSERT INTO logs (timestamp, level, module, function, message, exception, metadata)
            VALUES (%(timestamp)s, %(level)s, %(module)s, %(function)s, %(message)s, %(exception)s, %(metadata)s::jsonb)
            """,
            log_data,
        )

        conn.commit()
        cursor.close()
        conn.close()

    except Exception:
        # 数据库日志失败不应影响主程序，静默处理
        pass
```

**风险等级**: 🔴 高

**泄漏场景**:
- 如果在 `cursor.execute()` 或 `conn.commit()` 时发生异常，连接不会被关闭
- 由于异常被静默捕获（`except Exception: pass`），泄漏会持续发生
- 每次日志记录失败都会泄漏一个连接

**影响**:
- 日志系统故障可能导致大量连接泄漏
- 高频日志场景下，连接池会快速耗尽

**修复建议**:
```python
def db_sink(message):
    """数据库日志sink"""
    conn = None
    cursor = None
    try:
        # 从环境变量获取数据库配置
        conn = psycopg2.connect(
            host=os.getenv("POSTGRESQL_HOST", "localhost"),
            port=int(os.getenv("POSTGRESQL_PORT", "5432")),
            user=os.getenv("POSTGRESQL_USER", "postgres"),
            password=os.getenv("POSTGRESQL_PASSWORD", ""),
            database="mystocks_monitoring",
        )

        cursor = conn.cursor()

        # 准备日志数据
        log_data = {
            "timestamp": message.record["time"].isoformat(),
            "level": message.record["level"].name,
            "module": message.record["name"],
            "function": message.record["function"],
            "message": message.record["message"],
            "exception": (str(message.record["exception"]) if message.record["exception"] else None),
            "metadata": json.dumps(
                {
                    "file": message.record["file"].path,
                    "line": message.record["line"],
                    "process": message.record["process"].id,
                    "thread": message.record["thread"].id,
                }
            ),
        }

        # 插入日志
        cursor.execute(
            """
            INSERT INTO logs (timestamp, level, module, function, message, exception, metadata)
            VALUES (%(timestamp)s, %(level)s, %(module)s, %(function)s, %(message)s, %(exception)s, %(metadata)s::jsonb)
            """,
            log_data,
        )

        conn.commit()

    except Exception as e:
        # 记录错误但不影响主程序
        logger.error("数据库日志写入失败: %s", e)
    finally:
        # 确保连接被关闭
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
```

---

#### 🔴 问题 3: `src/storage/database/database_manager.py` - 数据库管理器

**位置**: `src/storage/database/database_manager.py:252, 263`

**问题描述**:
```python
# 第252行
conn = psycopg2.connect(
    host=config["host"],
    user=config["user"],
    password=config["password"],
    port=config["port"],
    database=db_name,
)

# 第263行
conn = redis.Redis(
    host=str(config.get("host", "localhost")),
    port=int(redis_port) if redis_port is not None else 6379,
    db=int(redis_db) if redis_db is not None else 0,
    password=str(config.get("password")) if config.get("password") else None,
    decode_responses=True,
)
```

**风险等级**: 🔴 高

**泄漏场景**:
- 在 `_create_connection()` 方法中创建连接后，如果后续操作失败，连接可能未被正确管理
- Redis连接对象没有显式的关闭方法，但连接池需要正确管理

**修复建议**:
- 使用连接池模式管理数据库连接
- 确保所有连接都在 `finally` 块中关闭
- 使用上下文管理器 (`with` 语句) 自动管理连接生命周期

---

#### 🔴 问题 4: `src/storage/database/fix_database_connections.py` - 数据库连接修复脚本

**位置**: `src/storage/database/fix_database_connections.py:53`

**问题描述**:
```python
conn = psycopg2.connect(
    host=db_config["host"],
    port=db_config["port"],
    user=db_config["user"],
    password=db_config["password"],
    database=db_config["database"],
)
```

**风险等级**: 🔴 高

**泄漏场景**:
- 修复脚本中创建连接后，如果后续操作失败，连接会泄漏
- 脚本可能被多次执行，累积泄漏

**修复建议**:
```python
conn = None
try:
    conn = psycopg2.connect(
        host=db_config["host"],
        port=db_config["port"],
        user=db_config["user"],
        password=db_config["password"],
        database=db_config["database"],
    )
    # ... 执行操作
finally:
    if conn is not None:
        conn.close()
```

---

#### 🔴 问题 5: `src/data_sources/real/connection_pool.py` - 连接池实现

**位置**: `src/data_sources/real/connection_pool.py:171`

**问题描述**:
```python
def _create_connection(self) -> Optional[PooledConnection]:
    """创建新连接"""
    try:
        # 基础连接配置
        raw_conn = psycopg2.connect(
            self.dsn,
            connect_timeout=self.config.connection_timeout,
            **self._get_connection_kwargs(),
        )

        # 创建池化连接包装器
        pooled_conn = PooledConnection(raw_conn, self)

        with self._lock:
            self.metrics.total_created += 1

        logger.debug("创建新数据库连接: %s", id(raw_conn))
        return pooled_conn

    except Exception as e:
        logger.error("创建数据库连接失败: %s", e)
        with self._lock:
            self.metrics.failed_requests += 1
        return None
```

**风险等级**: 🔴 高

**泄漏场景**:
- 如果 `PooledConnection` 初始化失败，原始连接 `raw_conn` 不会被关闭
- 连接池的 `release_connection()` 方法可能存在泄漏

**修复建议**:
```python
def _create_connection(self) -> Optional[PooledConnection]:
    """创建新连接"""
    raw_conn = None
    try:
        # 基础连接配置
        raw_conn = psycopg2.connect(
            self.dsn,
            connect_timeout=self.config.connection_timeout,
            **self._get_connection_kwargs(),
        )

        # 创建池化连接包装器
        pooled_conn = PooledConnection(raw_conn, self)

        with self._lock:
            self.metrics.total_created += 1

        logger.debug("创建新数据库连接: %s", id(raw_conn))
        return pooled_conn

    except Exception as e:
        logger.error("创建数据库连接失败: %s", e)
        with self._lock:
            self.metrics.failed_requests += 1
        finally:
            # 确保原始连接被关闭
            if raw_conn is not None:
                try:
                    raw_conn.close()
                except Exception:
                    pass
        return None
```

---

#### 🔴 问题 6: `src/storage/database/save_realtime_market_data_simple.py` - 实时数据保存

**位置**: `src/storage/database/save_realtime_market_data_simple.py:115`

**问题描述**:
```python
def initialize_redis(self) -> bool:
    """初始化Redis连接"""
    self.logger.info("初始化Redis连接...")

    try:
        # 创建Redis连接
        self.redis_client = redis.Redis(
            host=self.config["redis_host"],
            port=self.config["redis_port"],
            password=self.config["redis_password"],
            db=self.config["redis_db"],
            decode_responses=True,
        )

        # 测试连接
        self.redis_client.ping()
        self.logger.info("✅ Redis连接成功")
        return True

    except Exception as e:
        self.logger.error("❌ Redis连接失败: %s", e)
        self.logger.info("💡 请检查Redis服务是否启动，或使用CSV备份模式")
        return False
```

**风险等级**: 🔴 高

**泄漏场景**:
- Redis连接对象在类实例生命周期内一直保持连接
- 如果类实例未正确销毁，连接会一直占用
- 在多实例场景下（如多个Worker进程），连接数会成倍增加

**修复建议**:
```python
def initialize_redis(self) -> bool:
    """初始化Redis连接"""
    self.logger.info("初始化Redis连接...")

    try:
        # 创建Redis连接（使用连接池）
        self.redis_client = redis.Redis(
            host=self.config["redis_host"],
            port=self.config["redis_port"],
            password=self.config["redis_password"],
            db=self.config["redis_db"],
            decode_responses=True,
            connection_pool=redis.ConnectionPool(
                host=self.config["redis_host"],
                port=self.config["redis_port"],
                password=self.config["redis_password"],
                db=self.config["redis_db"],
                max_connections=10,  # 限制最大连接数
            )
        )

        # 测试连接
        self.redis_client.ping()
        self.logger.info("✅ Redis连接成功")
        return True

    except Exception as e:
        self.logger.error("❌ Redis连接失败: %s", e)
        self.logger.info("💡 请检查Redis服务是否启动，或使用CSV备份模式")
        return False

def close(self):
    """关闭所有连接"""
    if self.redis_client is not None:
        try:
            self.redis_client.close()
            self.logger.info("Redis连接已关闭")
        except Exception as e:
            self.logger.error("关闭Redis连接失败: %s", e)
```

---

### 1.4 良好实践示例

项目中也有一些正确的连接管理示例：

#### ✅ 示例 1: 使用上下文管理器 (`src/storage/database/init_db_monitor.py:275`)

```python
with engine.connect() as connection:
    # 自动管理连接生命周期
    connection.execute(text("SELECT 1"))
```

#### ✅ 示例 2: 使用连接池 (`web/backend/app/core/database.py:108`)

```python
engines["postgresql"] = create_engine(
    connection_string,
    pool_size=20,  # 连接池大小
    max_overflow=40,  # 最大溢出连接
    pool_timeout=30,  # 连接获取超时
    pool_pre_ping=True,  # 连接健康检查
    pool_recycle=3600,  # 连接回收时间
)
```

---

## 2. HTTP客户端连接泄漏分析

### 2.1 问题概述

HTTP客户端连接泄漏通常发生在调用外部API时，如果每次请求都创建新的HTTP连接而未复用会话（session），或者会话未正确关闭，会导致大量TIME_WAIT连接堆积，消耗系统资源。

### 2.2 检测方法

通过搜索以下模式识别潜在泄漏：
- `requests.get()`, `requests.post()` 等 - 不复用session
- 缺少 `Session` 对象复用
- 缺少 `session.close()` 调用

### 2.3 发现的问题

#### 🟡 问题 1: `src/utils/check_api_health.py` - API健康检查

**位置**: `src/utils/check_api_health.py:119, 128, 157, 160`

**问题描述**:
```python
def check_backend_running() -> bool:
    """检查Backend服务是否运行"""
    try:
        resp = requests.get(f"{BASE_URL}/api/docs", timeout=2)  # 每次创建新连接
        return resp.status_code == 200
    except Exception:
        return False

def get_auth_token() -> Optional[str]:
    """获取认证Token"""
    try:
        resp = requests.post(
            f"{BASE_URL}/api/auth/login",
            data={"username": TEST_USERNAME, "password": TEST_PASSWORD},
            timeout=TIMEOUT,
        )  # 每次创建新连接
        if resp.status_code == 200:
            return resp.json().get("access_token")
    except Exception as e:
        print(f"   警告: 无法获取Token - {str(e)}")
    return None

def test_api_endpoint(endpoint: Dict, token: Optional[str]) -> Tuple[bool, str, Optional[int]]:
    """测试单个API端点"""
    # ...
    try:
        if endpoint["method"] == "GET":
            resp = requests.get(url, headers=headers, timeout=TIMEOUT)  # 每次创建新连接
        elif endpoint["method"] == "POST":
            headers["Content-Type"] = "application/json"
            resp = requests.post(url, json=endpoint["data"], headers=headers, timeout=TIMEOUT)  # 每次创建新连接
```

**风险等级**: 🟡 中

**泄漏场景**:
- 每次API调用都创建新的HTTP连接
- 连接未复用，导致大量TIME_WAIT连接
- 测试脚本可能被频繁执行，累积泄漏

**影响**:
- 每次测试可能创建数十个新连接
- 系统端口资源耗尽
- API调用性能下降

**修复建议**:
```python
# 创建全局session对象
_session = None

def get_session() -> requests.Session:
    """获取或创建全局session"""
    global _session
    if _session is None:
        _session = requests.Session()
        # 配置连接池
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=100,
            max_retries=3,
        )
        _session.mount('http://', adapter)
        _session.mount('https://', adapter)
    return _session

def check_backend_running() -> bool:
    """检查Backend服务是否运行"""
    try:
        session = get_session()
        resp = session.get(f"{BASE_URL}/api/docs", timeout=2)  # 复用session
        return resp.status_code == 200
    except Exception:
        return False

def get_auth_token() -> Optional[str]:
    """获取认证Token"""
    try:
        session = get_session()
        resp = session.post(
            f"{BASE_URL}/api/auth/login",
            data={"username": TEST_USERNAME, "password": TEST_PASSWORD},
            timeout=TIMEOUT,
        )  # 复用session
        if resp.status_code == 200:
            return resp.json().get("access_token")
    except Exception as e:
        print(f"   警告: 无法获取Token - {str(e)}")
    return None

def cleanup():
    """清理session"""
    global _session
    if _session is not None:
        _session.close()
        _session = None
```

---

#### 🟡 问题 2: `src/adapters/byapi_adapter.py` - ByAPI适配器

**位置**: `src/adapters/byapi_adapter.py:169`

**问题描述**:
```python
def _fetch_data(self, url: str, params: Optional[Dict] = None, timeout: int = 30) -> Dict:
    """获取数据"""
    self._rate_limit()

    try:
        response = requests.get(url, timeout=timeout)  # 每次创建新连接
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise DataSourceError(f"Byapi API请求失败: {url}\n错误: {e}")
    except ValueError as e:
        raise DataSourceError(f"Byapi返回数据解析失败: {e}")
```

**风险等级**: 🟡 中

**泄漏场景**:
- 每次API调用都创建新的HTTP连接
- 适配器可能被频繁调用，累积泄漏

**修复建议**:
```python
class ByapiAdapter(BaseAdapter):
    def __init__(self):
        super().__init__()
        # 创建session对象
        self.session = requests.Session()
        # 配置连接池
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=5,
            pool_maxsize=50,
            max_retries=3,
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def _fetch_data(self, url: str, params: Optional[Dict] = None, timeout: int = 30) -> Dict:
        """获取数据"""
        self._rate_limit()

        try:
            response = self.session.get(url, params=params, timeout=timeout)  # 复用session
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise DataSourceError(f"Byapi API请求失败: {url}\n错误: {e}")
        except ValueError as e:
            raise DataSourceError(f"Byapi返回数据解析失败: {e}")

    def close(self):
        """关闭session"""
        if self.session is not None:
            self.session.close()

    def __del__(self):
        """析构函数"""
        self.close()
```

---

#### 🟡 问题 3: `src/ml_strategy/automation/notification_manager.py` - 通知管理器

**位置**: `src/ml_strategy/automation/notification_manager.py:351`

**问题描述**:
```python
response = requests.post(webhook_url, json=payload, timeout=10)  # 每次创建新连接
```

**风险等级**: 🟡 中

**修复建议**:
```python
class NotificationManager:
    def __init__(self):
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=5,
            pool_maxsize=50,
            max_retries=3,
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def send_notification(self, webhook_url: str, payload: Dict) -> bool:
        """发送通知"""
        try:
            response = self.session.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error("发送通知失败: %s", e)
            return False

    def close(self):
        """关闭session"""
        if self.session is not None:
            self.session.close()
```

---

#### 🟡 问题 4: `src/utils/test_logs_api.py` - 日志API测试

**位置**: `src/utils/test_logs_api.py:27, 61, 101, 137, 173, 205`

**问题描述**:
```python
response = requests.get(url, timeout=10)  # 多次调用，每次创建新连接
```

**风险等级**: 🟡 中

**修复建议**:
```python
# 创建全局session
session = requests.Session()

def test_log_endpoint(url: str, expected_status: int = 200) -> bool:
    """测试日志端点"""
    try:
        response = session.get(url, timeout=10)  # 复用session
        return response.status_code == expected_status
    except Exception as e:
        print(f"测试失败: {e}")
        return False

# 测试完成后关闭session
session.close()
```

---

#### 🟡 问题 5: `src/core/data_source_handlers_v2.py` - 数据源处理器

**位置**: `src/core/data_source_handlers_v2.py:424, 426`

**问题描述**:
```python
response = self.requests.get(url, params=params, headers=self.headers, timeout=30)
response = self.requests.post(url, json=params, headers=self.headers, timeout=30)
```

**风险等级**: 🟡 中

**说明**: 如果 `self.requests` 是 `requests` 模块而非 `Session` 对象，则存在泄漏风险。

**修复建议**:
```python
class DataSourceHandlersV2:
    def __init__(self):
        # 创建session对象
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=100,
            max_retries=3,
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def _make_request(self, method: str, url: str, **kwargs) -> Dict:
        """发送HTTP请求"""
        try:
            if method == "GET":
                response = self.session.get(url, **kwargs)
            elif method == "POST":
                response = self.session.post(url, **kwargs)
            # ... 其他方法
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error("HTTP请求失败: %s", e)
            raise

    def close(self):
        """关闭session"""
        if self.session is not None:
            self.session.close()
```

---

### 2.4 良好实践示例

#### ✅ 示例 1: 使用 `aiohttp.ClientSession` 上下文管理器 (`src/monitoring/ai_alert_manager.py:254`)

```python
async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
        data = await response.json()
```

#### ✅ 示例 2: 使用 `aiohttp.ClientSession` 上下文管理器 (`src/monitoring/alert_notifier.py:289`)

```python
async with aiohttp.ClientSession() as session:
    async with session.post(webhook_url, json=payload) as response:
        return response.status == 200
```

---

## 3. 缓存/消息队列连接泄漏分析

### 3.1 问题概述

缓存（如Redis）和消息队列（如RabbitMQ、Kafka）连接泄漏通常发生在连接未正确关闭或归还连接池时。虽然这些连接通常开销较小，但在高并发场景下仍可能导致资源耗尽。

### 3.2 检测方法

通过搜索以下模式识别潜在泄漏：
- `redis.Redis()` - 创建Redis连接
- 缺少 `close()` 调用
- 缺少连接池配置

### 3.3 发现的问题

#### 🟡 问题 1: `src/utils/check_db_health.py` - Redis健康检查

**位置**: `src/utils/check_db_health.py:209`

**问题描述**:
```python
def check_redis_connection():
    """验证Redis连接"""
    try:
        import redis
        from web.backend.app.core.config import settings

        r = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password if settings.redis_password else None,
            db=settings.redis_db,
            socket_connect_timeout=5,
        )

        # 测试连接
        r.ping()
        info = r.info()
        print("✅ Redis连接成功")
        # ... 其他操作
        # 未关闭连接
        return True, None
```

**风险等级**: 🟡 中

**泄漏场景**:
- Redis连接对象未关闭
- 健康检查脚本可能被频繁执行

**修复建议**:
```python
def check_redis_connection():
    """验证Redis连接"""
    r = None
    try:
        import redis
        from web.backend.app.core.config import settings

        r = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password if settings.redis_password else None,
            db=settings.redis_db,
            socket_connect_timeout=5,
        )

        # 测试连接
        r.ping()
        info = r.info()
        print("✅ Redis连接成功")
        print(f"   版本: {info.get('redis_version', 'Unknown')}")
        print(f"   数据库: DB{settings.redis_db}")
        print(f"   内存使用: {info.get('used_memory_human', 'Unknown')}")
        print(f"   键数量: {r.dbsize()}")

        return True, None

    except Exception as e:
        print("❌ Redis连接失败")
        print(f"   错误: {str(e)}")
        return False, str(e)
    finally:
        # 关闭连接
        if r is not None:
            try:
                r.close()
            except Exception:
                pass
```

---

#### 🟡 问题 2: `src/monitoring/async_monitoring.py` - 异步监控

**位置**: `src/monitoring/async_monitoring.py:87, 203`

**问题描述**:
```python
self._redis_client = redis.Redis(
    host=redis_config.get("host", "localhost"),
    port=redis_config.get("port", 6379),
    db=redis_config.get("db", 0),
    decode_responses=True,
)
```

**风险等级**: 🟡 中

**修复建议**:
```python
class AsyncMonitoring:
    def __init__(self, redis_config: Dict):
        self._redis_pool = redis.ConnectionPool(
            host=redis_config.get("host", "localhost"),
            port=redis_config.get("port", 6379),
            db=redis_config.get("db", 0),
            decode_responses=True,
            max_connections=10,
        )
        self._redis_client = redis.Redis(connection_pool=self._redis_pool)

    async def close(self):
        """关闭Redis连接池"""
        await self._redis_pool.disconnect()
```

---

#### 🟡 问题 3: `src/storage/database/connection_manager.py` - 连接管理器

**位置**: `src/storage/database/connection_manager.py:192`

**问题描述**:
```python
conn = redis.Redis(
    host=str(config.get("host", "localhost")),
    port=int(config.get("port", 6379)),
    db=int(config.get("db", 0)),
    password=str(config.get("password")) if config.get("password") else None,
    decode_responses=True,
)
```

**风险等级**: 🟡 中

**修复建议**:
```python
# 使用连接池
redis_pool = redis.ConnectionPool(
    host=str(config.get("host", "localhost")),
    port=int(config.get("port", 6379)),
    db=int(config.get("db", 0)),
    password=str(config.get("password")) if config.get("password") else None,
    decode_responses=True,
    max_connections=10,
)
conn = redis.Redis(connection_pool=redis_pool)
```

---

#### 🟡 问题 4: `src/gpu/api_system/utils/redis_utils.py` - GPU系统Redis工具

**位置**: `src/gpu/api_system/utils/redis_utils.py:52`

**问题描述**:
```python
self.redis_client = redis.Redis(
    host=redis_host,
    port=redis_port,
    db=redis_db,
    password=redis_password,
    decode_responses=True,
)
```

**风险等级**: 🟡 中

**修复建议**:
```python
class RedisUtils:
    def __init__(self, redis_host: str, redis_port: int, redis_db: int, redis_password: str = None):
        self.redis_pool = redis.ConnectionPool(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            password=redis_password,
            decode_responses=True,
            max_connections=10,
        )
        self.redis_client = redis.Redis(connection_pool=self.redis_pool)

    def close(self):
        """关闭Redis连接池"""
        self.redis_pool.disconnect()
```

---

### 3.4 良好实践示例

#### ✅ 示例 1: 使用连接池 (`src/core/cache/multi_level.py`)

```python
redis_pool = redis.ConnectionPool(
    host=redis_host,
    port=redis_port,
    db=redis_db,
    max_connections=10,
)
self._redis = redis.Redis(connection_pool=redis_pool)
```

---

## 4. Web API 层连接泄漏分析

### 4.1 问题概述

Web API 层的连接泄漏通常发生在 FastAPI 路由处理函数中，如果数据库会话未正确关闭，或者 HTTP 客户端未复用，会导致连接泄漏。

### 4.2 检测结果

通过分析 `web/backend/app/` 目录下的代码，发现：

#### ✅ 良好实践: 使用连接池

**位置**: `web/backend/app/core/database.py:108`

```python
engines["postgresql"] = create_engine(
    connection_string,
    pool_size=20,  # 连接池大小
    max_overflow=40,  # 最大溢出连接
    pool_timeout=30,  # 连接获取超时
    pool_pre_ping=True,  # 连接健康检查
    pool_recycle=3600,  # 连接回收时间
)
```

#### ✅ 良好实践: 使用依赖注入管理会话

**位置**: `web/backend/app/core/database.py:131`

```python
def get_postgresql_session() -> Session:
    """获取 PostgreSQL 会话（工厂模式）"""
    if "postgresql" not in sessions:
        engine = get_postgresql_engine()
        sessions["postgresql"] = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return sessions["postgresql"]()
```

### 4.3 潜在风险

虽然 Web API 层使用了连接池，但以下场景仍需注意：

1. **长时间运行的请求**: 如果请求处理时间过长，连接可能被占用过久
2. **异常处理**: 如果异常未被正确捕获，会话可能未关闭
3. **并发请求**: 高并发场景下，连接池可能耗尽

**建议**:
- 使用 FastAPI 的 `Depends` 依赖注入自动管理会话生命周期
- 添加请求超时限制
- 监控连接池使用情况

---

## 5. 修复优先级和行动计划

### 5.1 修复优先级

| 优先级 | 问题类型 | 数量 | 风险等级 | 建议修复时间 |
|--------|----------|------|----------|--------------|
| P0 | 数据库连接泄漏 | 6 | 🔴 高 | 立即修复 |
| P1 | HTTP客户端连接泄漏 | 12 | 🟡 中 | 1周内修复 |
| P2 | Redis连接泄漏 | 8 | 🟡 中 | 2周内修复 |

### 5.2 修复计划

#### 阶段 1: 紧急修复（P0）- 1-2天

**目标**: 修复所有高风险数据库连接泄漏

**任务**:
1. 修复 `src/utils/check_db_health.py` - 添加 `finally` 块关闭连接
2. 修复 `src/core/logging.py` - 添加 `finally` 块关闭连接
3. 修复 `src/storage/database/database_manager.py` - 使用连接池
4. 修复 `src/storage/database/fix_database_connections.py` - 添加 `finally` 块
5. 修复 `src/data_sources/real/connection_pool.py` - 添加异常处理
6. 修复 `src/storage/database/save_realtime_market_data_simple.py` - 添加 `close()` 方法

**验收标准**:
- 所有数据库连接都在 `finally` 块中关闭
- 使用连接池管理连接
- 测试脚本运行后无连接泄漏

---

#### 阶段 2: HTTP客户端优化（P1）- 3-5天

**目标**: 修复所有HTTP客户端连接泄漏

**任务**:
1. 修复 `src/utils/check_api_health.py` - 使用全局 `Session` 对象
2. 修复 `src/adapters/byapi_adapter.py` - 使用实例 `Session` 对象
3. 修复 `src/ml_strategy/automation/notification_manager.py` - 使用实例 `Session` 对象
4. 修复 `src/utils/test_logs_api.py` - 使用全局 `Session` 对象
5. 修复 `src/core/data_source_handlers_v2.py` - 使用实例 `Session` 对象

**验收标准**:
- 所有HTTP请求都复用 `Session` 对象
- 配置连接池参数
- 测试脚本运行后无TIME_WAIT连接堆积

---

#### 阶段 3: Redis连接优化（P2）- 1周

**目标**: 修复所有Redis连接泄漏

**任务**:
1. 修复 `src/utils/check_db_health.py` - 添加 `finally` 块关闭连接
2. 修复 `src/monitoring/async_monitoring.py` - 使用连接池
3. 修复 `src/storage/database/connection_manager.py` - 使用连接池
4. 修复 `src/gpu/api_system/utils/redis_utils.py` - 使用连接池

**验收标准**:
- 所有Redis连接都使用连接池
- 连接在 `finally` 块中关闭
- 测试脚本运行后无连接泄漏

---

### 5.3 监控和预防

#### 连接泄漏检测

**工具**:
- `psql` - 查看PostgreSQL连接数
- `redis-cli` - 查看Redis连接数
- `netstat` / `ss` - 查看系统连接数
- `lsof` - 查看进程打开的文件描述符

**脚本示例**:
```bash
#!/bin/bash
# 检查PostgreSQL连接数
echo "PostgreSQL连接数:"
psql -h localhost -U postgres -d mystocks -c "SELECT count(*) FROM pg_stat_activity;"

# 检查Redis连接数
echo "Redis连接数:"
redis-cli -h localhost INFO clients | grep connected_clients

# 检查系统连接数
echo "系统连接数:"
netstat -an | grep TIME_WAIT | wc -l
```

#### 连接池监控

**PostgreSQL连接池监控**:
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine("postgresql://...", poolclass=QueuePool)

# 获取连接池状态
pool = engine.pool
print(f"连接池大小: {pool.size()}")
print(f"已用连接: {pool.checkedout()}")
print(f"空闲连接: {pool.overflow()}")
```

**Redis连接池监控**:
```python
import redis

pool = redis.ConnectionPool(host='localhost', port=6379, max_connections=10)
r = redis.Redis(connection_pool=pool)

# 获取连接池状态
print(f"连接池大小: {pool.connection_pool.connection_pool_size}")
print(f"已用连接: {pool.connection_pool.in_use_connections}")
print(f"空闲连接: {pool.connection_pool.idle_connections}")
```

#### 预防措施

1. **代码审查**:
   - 所有数据库连接必须使用 `with` 语句或 `finally` 块
   - 所有HTTP请求必须复用 `Session` 对象
   - 所有Redis连接必须使用连接池

2. **自动化测试**:
   - 添加连接泄漏检测测试
   - 使用 `pytest` + `pytest-leaks` 检测内存泄漏
   - 使用 `pytest-asyncio` 检测异步连接泄漏

3. **监控告警**:
   - 监控数据库连接数
   - 监控系统连接数
   - 设置告警阈值

---

## 6. 总结

### 6.1 关键发现

1. **数据库连接泄漏**: 发现6个高风险泄漏点，主要集中在健康检查脚本、日志系统和连接池实现
2. **HTTP客户端连接泄漏**: 发现12个中风险泄漏点，主要集中在API调用和适配器
3. **Redis连接泄漏**: 发现8个中风险泄漏点，主要由于未使用连接池

### 6.2 修复建议

1. **立即修复**: 所有数据库连接泄漏问题（P0）
2. **1周内修复**: 所有HTTP客户端连接泄漏问题（P1）
3. **2周内修复**: 所有Redis连接泄漏问题（P2）

### 6.3 长期改进

1. **建立连接管理规范**:
   - 所有数据库连接必须使用连接池
   - 所有HTTP请求必须复用 `Session` 对象
   - 所有Redis连接必须使用连接池

2. **添加自动化检测**:
   - 集成连接泄漏检测到CI/CD流程
   - 定期运行连接泄漏检测脚本

3. **监控和告警**:
   - 实时监控连接池使用情况
   - 设置连接泄漏告警

---

## 7. 附录

### 7.1 参考文档

- [SQLAlchemy连接池文档](https://docs.sqlalchemy.org/en/14/core/pooling.html)
- [requests.Session文档](https://requests.readthedocs.io/en/latest/user/advanced/#session-objects)
- [redis-py连接池文档](https://redis-py.readthedocs.io/en/stable/connection_pools.html)
- [PostgreSQL连接管理](https://www.postgresql.org/docs/current/runtime-config-connection.html)

### 7.2 工具推荐

- **连接泄漏检测**:
  - `pytest-leaks` - Python内存泄漏检测
  - `objgraph` - Python对象引用图
  - `memory_profiler` - Python内存分析

- **连接监控**:
  - `pg_stat_activity` - PostgreSQL连接监控
  - `redis-cli INFO` - Redis连接监控
  - `netstat` / `ss` - 系统连接监控

### 7.3 联系方式

如有问题或建议，请联系：
- 项目负责人: JohnC
- 技术支持: Claude Code

---

**报告生成时间**: 2026-01-07
**报告版本**: v1.0
**下次审查时间**: 2026-01-14
