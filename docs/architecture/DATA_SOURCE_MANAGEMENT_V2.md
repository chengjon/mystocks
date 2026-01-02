# 数据源注册与治理中心 - 优化方案

> **版本**: v2.0
> **更新时间**: 2026-01-02
> **优化重点**: 融合现有方案与新增需求，保留Grafana仪表板

---

## 📊 方案总览

本方案旨在建立一个**集中式数据源治理中心**，统一管理所有外部数据源接口（akshare, tushare, baostock, tdx等），提供完整的监控、路由、调度和治理能力。

### 核心设计理念

1. **双存储策略**：PostgreSQL持久化 + YAML配置文件
2. **统一调用接口**：屏蔽底层数据源差异
3. **智能路由**：基于质量评分和性能自动选择最优数据源
4. **全生命周期管理**：注册 → 测试 → 上线 → 监控 → 下线
5. **可视化监控**：Grafana仪表板实时展示所有数据源状态

---

## 1️⃣ 数据源元数据注册表（PostgreSQL）

### 数据库表结构

```sql
-- 创建数据源注册表
CREATE TABLE data_source_registry (
    id SERIAL PRIMARY KEY,

    -- 基础信息
    source_name VARCHAR(50) NOT NULL,          -- 数据源名称：akshare、tushare、tdx等
    source_type VARCHAR(20) NOT NULL,          -- 类型：api_library/database/crawler/file
    endpoint_name VARCHAR(100) UNIQUE NOT NULL, -- 接口唯一标识：akshare.stock_zh_a_hist

    -- 调用信息
    call_method VARCHAR(20),                   -- http/get/post/function_call
    endpoint_url TEXT,                         -- 完整URL或函数路径
    parameters JSONB,                          -- 参数定义和示例（JSON格式）
    response_format VARCHAR(20),               -- json/csv/dataframe/protobuf

    -- 分类与路由
    data_category VARCHAR(50) NOT NULL,        -- 对应34个分类：DAILY_KLINE、TICK_DATA等
    data_classification VARCHAR(20),           -- 5大分类：market_data/reference_data等
    target_db VARCHAR(20) NOT NULL,            -- postgresql/tdengine
    table_name VARCHAR(100),                   -- 存储的目标表名

    -- 元数据
    description TEXT,
    update_frequency VARCHAR(20),              -- realtime/daily/weekly/monthly
    data_quality_score FLOAT DEFAULT 8.0,      -- 数据质量评分（0-10）
    priority INT DEFAULT 10,                   -- 优先级（数字越小优先级越高）
    status VARCHAR(20) DEFAULT 'active',       -- active/deprecated/maintenance/testing

    -- 监控指标
    last_success_time TIMESTAMP,
    last_failure_time TIMESTAMP,
    avg_response_time FLOAT DEFAULT 0,
    success_rate FLOAT DEFAULT 100.0,
    total_calls INT DEFAULT 0,
    failed_calls INT DEFAULT 0,
    consecutive_failures INT DEFAULT 0,
    quota_used INT DEFAULT 0,                  -- 调用额度使用情况
    quota_limit INT,                           -- 调用额度上限

    -- 数据质量
    data_freshness INTERVAL,                   -- 数据新鲜度
    last_check_time TIMESTAMP,
    health_status VARCHAR(20) DEFAULT 'unknown', -- healthy/degraded/failed/unknown

    -- 管理信息
    owner VARCHAR(50) DEFAULT 'system',
    tags TEXT[],                               -- 标签数组
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 约束
    CONSTRAINT chk_status CHECK (status IN ('active', 'deprecated', 'maintenance', 'testing')),
    CONSTRAINT chk_health CHECK (health_status IN ('healthy', 'degraded', 'failed', 'unknown')),
    CONSTRAINT chk_quality_score CHECK (data_quality_score >= 0 AND data_quality_score <= 10),
    CONSTRAINT chk_target_db CHECK (target_db IN ('postgresql', 'tdengine'))
);

-- 创建索引
CREATE INDEX idx_dsr_category ON data_source_registry(data_category);
CREATE INDEX idx_dsr_status ON data_source_registry(status, health_status);
CREATE INDEX idx_dsr_source_name ON data_source_registry(source_name);
CREATE INDEX idx_dsr_quality_score ON data_source_registry(data_quality_score DESC, priority ASC);
CREATE INDEX idx_dsr_last_success ON data_source_registry(last_success_time);

-- 创建更新触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_data_source_registry_updated_at
    BEFORE UPDATE ON data_source_registry
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 创建调用历史表（用于监控和统计）
CREATE TABLE data_source_call_history (
    id BIGSERIAL PRIMARY KEY,
    endpoint_name VARCHAR(100) NOT NULL,
    call_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- 调用参数
    parameters JSONB,

    -- 调用结果
    success BOOLEAN NOT NULL,
    response_time FLOAT,                       -- 响应时间（秒）
    record_count INT,                          -- 返回数据条数

    -- 错误信息
    error_message TEXT,
    error_type VARCHAR(100),

    -- 外键关联
    CONSTRAINT fk_endpoint FOREIGN KEY (endpoint_name)
        REFERENCES data_source_registry(endpoint_name) ON DELETE CASCADE
);

CREATE INDEX idx_dsch_call_time ON data_source_call_history(call_time DESC);
CREATE INDEX idx_dsch_endpoint ON data_source_call_history(endpoint_name, call_time DESC);
CREATE INDEX idx_dsch_success ON data_source_call_history(endpoint_name, success);
```

---

## 2️⃣ YAML配置文件（初始配置与版本控制）

### 配置文件结构

```yaml
# config/data_sources_registry.yaml
version: "2.0"
last_updated: "2026-01-02T12:00:00"

data_sources:
  # AKShare 数据源
  akshare_stock_daily:
    source_name: "akshare"
    source_type: "api_library"
    endpoint_name: "akshare.stock_zh_a_hist"
    call_method: "function_call"
    endpoint_url: "akshare.stock_zh_a_hist"

    data_category: "DAILY_KLINE"
    data_classification: "market_data"
    target_db: "postgresql"
    table_name: "daily_kline"

    parameters:
      symbol:
        type: "string"
        required: true
        description: "股票代码"
        example: "000001"
      period:
        type: "string"
        required: false
        default: "daily"
        options: ["daily", "weekly", "monthly"]
      start_date:
        type: "string"
        format: "YYYYMMDD"
        required: false
        description: "开始日期"
      end_date:
        type: "string"
        format: "YYYYMMDD"
        required: false
        description: "结束日期"
      adjust:
        type: "string"
        default: "qfq"
        options: ["qfq", "hfq", ""]
        description: "复权类型"

    description: "获取A股日线历史行情数据"
    update_frequency: "daily"
    update_schedule: "16:00"
    data_quality_score: 9.5
    priority: 2
    status: "active"
    tags: ["stock", "kline", "free"]

    # 测试参数（用于健康检查）
    test_parameters:
      symbol: "000001"
      period: "daily"
      start_date: "20240101"
      end_date: "20240110"
      adjust: "qfq"

    # 数据源特定配置
    source_config:
      module_name: "akshare"
      function_name: "stock_zh_a_hist"
      param_mapping:
        symbol: "symbol"
        period: "period"
        start_date: "start_date"
        end_date: "end_date"
        adjust: "adjust"
      quota_limit: null  # 无限制

    # 数据质量规则
    quality_rules:
      min_record_count: 1
      max_response_time: 10.0  # 秒
      required_columns: ["日期", "开盘", "最高", "最低", "收盘", "成交量"]

  # TuShare 数据源
  tushare_daily:
    source_name: "tushare"
    source_type: "api_library"
    endpoint_name: "tushare.daily"
    call_method: "function_call"
    endpoint_url: "ts.pro_api.daily"

    data_category: "DAILY_KLINE"
    data_classification: "market_data"
    target_db: "postgresql"
    table_name: "daily_kline"

    parameters:
      ts_code:
        type: "string"
        required: true
        description: "股票代码（TS格式）"
        example: "000001.SZ"
      trade_date:
        type: "string"
        format: "YYYYMMDD"
        required: false
      start_date:
        type: "string"
        format: "YYYYMMDD"
        required: false
      end_date:
        type: "string"
        format: "YYYYMMDD"
        required: false

    description: "获取A股日线行情数据（专业版）"
    update_frequency: "daily"
    update_schedule: "18:00"
    data_quality_score: 9.8
    priority: 1  # 优先级最高
    status: "active"
    tags: ["stock", "kline", "premium", "high-quality"]

    test_parameters:
      ts_code: "000001.SZ"
      start_date: "20240101"
      end_date: "20240110"

    source_config:
      token_env_var: "TUSHARE_TOKEN"
      module_name: "tushare"
      api_name: "daily"
      quota_limit: 5000  # 每日5000次
      quota_type: "daily"

    quality_rules:
      min_record_count: 1
      max_response_time: 5.0
      required_columns: ["ts_code", "trade_date", "open", "high", "low", "close", "vol", "amount"]

  # 通达信数据源
  tdx_realtime:
    source_name: "tdx"
    source_type: "database"
    endpoint_name: "tdx.get_security_quotes"
    call_method: "tcp"
    endpoint_url: "tcp://192.168.1.100:7709"

    data_category: "REALTIME_QUOTE"
    data_classification: "market_data"
    target_db: "tdengine"
    table_name: "tick_data"

    parameters:
      symbols:
        type: "array"
        required: true
        description: "股票代码列表"
        example: ["000001", "000002", "600000"]

    description: "通达信实时行情数据"
    update_frequency: "realtime"
    update_schedule: "*/5 * * * *"  # 每5分钟
    data_quality_score: 9.0
    priority: 3
    status: "active"
    tags: ["realtime", "tick", "low-latency"]

    test_parameters:
      symbols: ["000001"]

    source_config:
      connection_type: "tcp"
      host: "192.168.1.100"
      port: 7709
      timeout: 5

    quality_rules:
      max_response_time: 1.0  # 1秒内响应
      required_fields: ["symbol", "price", "volume", "timestamp"]

  # 爬虫数据源示例
  eastmoney_fund_flow:
    source_name: "web_crawler"
    source_type: "crawler"
    endpoint_name: "eastmoney.fund_flow"
    call_method: "http"
    endpoint_url: "http://data.push2.eastmoney.com/api/qt/clist/get"

    data_category: "FUND_FLOW"
    data_classification: "market_data"
    target_db: "postgresql"
    table_name: "fund_flow"

    parameters:
      market:
        type: "string"
        default: "sh"
        options: ["sh", "sz"]
      date:
        type: "string"
        format: "YYYY-MM-DD"
        required: false

    description: "东方财富资金流向数据"
    update_frequency: "daily"
    update_schedule: "17:00"
    data_quality_score: 8.5
    priority: 5
    status: "active"
    tags: ["fund_flow", "crawler", "free"]

    test_parameters:
      market: "sh"
      date: "2024-01-10"

    source_config:
      method: "GET"
      headers:
        User-Agent: "Mozilla/5.0"
      response_format: "json"
      json_path: "$.data.diff"  # JSON路径提取

    quality_rules:
      max_response_time: 15.0
      min_record_count: 10
      required_columns: ["代码", "名称", "最新价", "涨跌幅", "主力净流入"]
```

---

## 3️⃣ 统一数据源管理器（核心类）

### Python实现

```python
# src/core/data_source_manager.py
"""
统一数据源管理器 - 所有外部数据源的集中管理入口
"""
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import yaml
import pandas as pd

from src.storage.database import DatabaseConnectionManager
from src.monitoring import MonitoringDatabase


class DataSourceManager:
    """
    统一数据源管理器

    功能：
    1. 从数据库和YAML加载数据源配置
    2. 提供统一的数据获取接口
    3. 自动健康检查和质量评分
    4. 调用历史记录和性能统计
    5. 智能路由到最佳数据源
    """

    def __init__(self, config_path: str = "config/data_sources_registry.yaml"):
        self.config_path = config_path
        self.registry = {}  # 内存缓存: {endpoint_name: {handler, metadata, cache}}
        self.db_manager = DatabaseConnectionManager()
        self.monitoring = MonitoringDatabase()

        # 加载所有数据源配置
        self._load_registry()

    def _load_registry(self):
        """从数据库和YAML加载所有数据源配置"""
        print(f"[DataSourceManager] 开始加载数据源注册表...")

        # 1. 从数据库加载已注册的数据源
        db_sources = self._load_from_database()
        print(f"[DataSourceManager] 从数据库加载 {len(db_sources)} 个数据源")

        # 2. 从YAML加载配置（用于初始化和更新）
        yaml_sources = self._load_from_yaml()
        print(f"[DataSourceManager] 从YAML加载 {len(yaml_sources)} 个数据源配置")

        # 3. 合并配置（数据库优先，补充YAML中的新数据源）
        all_sources = self._merge_sources(db_sources, yaml_sources)

        # 4. 创建处理器和缓存
        for endpoint_name, source_config in all_sources.items():
            if source_config.get('status') != 'active':
                continue

            self.registry[endpoint_name] = {
                'handler': self._create_handler(source_config),
                'metadata': source_config,
                'cache': LRUCache(maxsize=100),
                'last_call': None,
                'call_count': 0
            }

        print(f"[DataSourceManager] 注册表加载完成，活跃数据源：{len(self.registry)} 个")

    def _load_from_database(self) -> Dict:
        """从PostgreSQL数据库加载数据源注册表"""
        query = """
            SELECT
                endpoint_name,
                source_name,
                source_type,
                data_category,
                target_db,
                table_name,
                parameters,
                data_quality_score,
                priority,
                status,
                health_status,
                avg_response_time,
                success_rate,
                consecutive_failures,
                last_success_time
            FROM data_source_registry
            WHERE status = 'active'
        """

        try:
            with self.db_manager.get_postgresql_connection() as conn:
                df = pd.read_sql(query, conn)

            sources = {}
            for _, row in df.iterrows():
                sources[row['endpoint_name']] = {
                    'endpoint_name': row['endpoint_name'],
                    'source_name': row['source_name'],
                    'source_type': row['source_type'],
                    'data_category': row['data_category'],
                    'target_db': row['target_db'],
                    'table_name': row['table_name'],
                    'parameters': json.loads(row['parameters']) if row['parameters'] else {},
                    'data_quality_score': row['data_quality_score'],
                    'priority': row['priority'],
                    'status': row['status'],
                    'health_status': row['health_status'],
                    'avg_response_time': row['avg_response_time'],
                    'success_rate': row['success_rate'],
                    'consecutive_failures': row['consecutive_failures'],
                    'last_success_time': row['last_success_time']
                }

            return sources
        except Exception as e:
            print(f"[DataSourceManager] 从数据库加载失败: {e}")
            return {}

    def _load_from_yaml(self) -> Dict:
        """从YAML配置文件加载数据源"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            sources = {}
            for endpoint_key, source_config in config.get('data_sources', {}).items():
                # 确保endpoint_name一致
                if 'endpoint_name' not in source_config:
                    source_config['endpoint_name'] = endpoint_key

                sources[endpoint_key] = source_config

            return sources
        except FileNotFoundError:
            print(f"[DataSourceManager] YAML配置文件不存在: {self.config_path}")
            return {}
        except Exception as e:
            print(f"[DataSourceManager] 从YAML加载失败: {e}")
            return {}

    def _merge_sources(self, db_sources: Dict, yaml_sources: Dict) -> Dict:
        """合并数据库和YAML配置"""
        # 数据库优先（包含运行时统计），YAML用于补充新数据源
        merged = db_sources.copy()

        for endpoint_name, yaml_config in yaml_sources.items():
            if endpoint_name not in merged:
                # 新数据源，从YAML添加
                merged[endpoint_name] = yaml_config
            else:
                # 已存在的数据源，仅更新配置字段（不覆盖运行时统计）
                db_source = merged[endpoint_name]
                for key in ['parameters', 'description', 'test_parameters', 'source_config']:
                    if key in yaml_config:
                        db_source[key] = yaml_config[key]

        return merged

    def _create_handler(self, source_config: Dict):
        """工厂方法创建具体数据源处理器"""
        from src.core.data_source_handlers import (
            AkshareHandler, TushareHandler, BaostockHandler,
            TdxHandler, WebCrawlerHandler, LocalFileHandler
        )

        source_type = source_config['source_type']
        source_name = source_config.get('source_name', '')

        handlers = {
            'akshare': AkshareHandler,
            'tushare': TushareHandler,
            'baostock': BaostockHandler,
            'tdx': TdxHandler,
            'web_crawler': WebCrawlerHandler,
            'database': TdxHandler,  # TDX也作为数据库处理
            'api_library': self._select_api_handler(source_name),
            'crawler': WebCrawlerHandler,
            'file': LocalFileHandler
        }

        handler_class = handlers.get(source_type)
        if not handler_class:
            raise ValueError(f"不支持的数据源类型: {source_type}")

        return handler_class(source_config)

    def _select_api_handler(self, source_name: str):
        """根据数据源名称选择处理器"""
        from src.core.data_source_handlers import AkshareHandler, TushareHandler

        handler_map = {
            'akshare': AkshareHandler,
            'tushare': TushareHandler,
            'baostock': BaostockHandler
        }

        return handler_map.get(source_name, AkshareHandler)

    def get_data(self, endpoint_name: str, **kwargs) -> pd.DataFrame:
        """
        统一数据获取接口

        Args:
            endpoint_name: 数据源端点名称（如 akshare.stock_zh_a_hist）
            **kwargs: 数据源特定参数

        Returns:
            pandas.DataFrame: 获取的数据

        Raises:
            ValueError: 数据源不存在或调用失败
        """
        # 1. 查找数据源
        source = self.registry.get(endpoint_name)
        if not source:
            raise ValueError(f"数据源 {endpoint_name} 不存在或未激活")

        # 2. 检查健康状态
        if source['metadata'].get('health_status') == 'failed':
            print(f"[WARNING] 数据源 {endpoint_name} 状态为失败，尝试调用可能会失败")

        # 3. 生成缓存键
        cache_key = self._generate_cache_key(endpoint_name, kwargs)

        # 4. 检查缓存
        if cached := source['cache'].get(cache_key):
            print(f"[DataSourceManager] 从缓存返回数据: {endpoint_name}")
            return cached

        # 5. 调用具体处理器
        start_time = time.time()
        try:
            data = source['handler'].fetch(**kwargs)
            response_time = time.time() - start_time

            # 6. 验证数据
            self._validate_data(endpoint_name, data)

            # 7. 记录成功指标
            self._record_success(endpoint_name, response_time, len(data) if hasattr(data, '__len__') else 0)

            # 8. 更新缓存
            source['cache'][cache_key] = data
            source['last_call'] = datetime.now()
            source['call_count'] += 1

            print(f"[DataSourceManager] 成功获取数据: {endpoint_name}, 耗时: {response_time:.2f}s, 记录数: {len(data) if hasattr(data, '__len__') else 'N/A'}")

            return data

        except Exception as e:
            # 9. 记录失败
            error_msg = str(e)
            self._record_failure(endpoint_name, error_msg)

            print(f"[ERROR] 数据源调用失败: {endpoint_name}, 错误: {error_msg}")
            raise

    def _generate_cache_key(self, endpoint_name: str, params: Dict) -> str:
        """生成缓存键"""
        # 将参数转换为稳定的字符串表示
        param_str = json.dumps(params, sort_keys=True)
        return f"{endpoint_name}:{hash(param_str)}"

    def _validate_data(self, endpoint_name: str, data: Any):
        """验证数据质量"""
        source = self.registry[endpoint_name]
        quality_rules = source['metadata'].get('quality_rules', {})

        if not isinstance(data, pd.DataFrame):
            return  # 非DataFrame数据跳过验证

        # 检查最小记录数
        min_count = quality_rules.get('min_record_count', 0)
        if len(data) < min_count:
            raise ValueError(f"数据记录数不足: {len(data)} < {min_count}")

        # 检查必需列
        required_columns = quality_rules.get('required_columns', [])
        if required_columns:
            missing_columns = set(required_columns) - set(data.columns)
            if missing_columns:
                raise ValueError(f"缺少必需列: {missing_columns}")

    def _record_success(self, endpoint_name: str, response_time: float, record_count: int):
        """记录成功调用"""
        # 更新内存统计
        source = self.registry[endpoint_name]
        metadata = source['metadata']

        # 更新平均响应时间
        old_avg = metadata.get('avg_response_time', 0)
        old_count = metadata.get('total_calls', 0)
        new_avg = (old_avg * old_count + response_time) / (old_count + 1)
        metadata['avg_response_time'] = new_avg
        metadata['total_calls'] = old_count + 1

        # 更新成功率
        failed_calls = metadata.get('failed_calls', 0)
        metadata['success_rate'] = (old_count + 1 - failed_calls) / (old_count + 1) * 100

        # 更新健康状态
        if response_time > 5.0:
            metadata['health_status'] = 'degraded'
        else:
            metadata['health_status'] = 'healthy'

        metadata['consecutive_failures'] = 0
        metadata['last_success_time'] = datetime.now()

        # 记录到监控数据库
        self.monitoring.log_data_source_call(
            endpoint_name=endpoint_name,
            success=True,
            response_time=response_time,
            record_count=record_count
        )

        # 记录到数据库历史表
        self._save_call_history(endpoint_name, {}, True, response_time, record_count)

    def _record_failure(self, endpoint_name: str, error_message: str):
        """记录失败调用"""
        source = self.registry.get(endpoint_name)
        if not source:
            return

        metadata = source['metadata']

        # 更新失败统计
        metadata['failed_calls'] = metadata.get('failed_calls', 0) + 1
        metadata['consecutive_failures'] = metadata.get('consecutive_failures', 0) + 1
        metadata['last_failure_time'] = datetime.now()

        # 连续失败3次标记为失败
        if metadata['consecutive_failures'] >= 3:
            metadata['health_status'] = 'failed'

        # 记录到监控数据库
        self.monitoring.log_data_source_call(
            endpoint_name=endpoint_name,
            success=False,
            error_message=error_message
        )

        # 记录到数据库历史表
        self._save_call_history(endpoint_name, {}, False, None, None, error_message)

    def _save_call_history(self, endpoint_name: str, parameters: Dict,
                          success: bool, response_time: Optional[float],
                          record_count: Optional[int], error_message: str = None):
        """保存调用历史到数据库"""
        query = """
            INSERT INTO data_source_call_history
            (endpoint_name, parameters, success, response_time, record_count, error_message)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        try:
            with self.db_manager.get_postgresql_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (
                    endpoint_name,
                    json.dumps(parameters),
                    success,
                    response_time,
                    record_count,
                    error_message
                ))
                conn.commit()
        except Exception as e:
            print(f"[ERROR] 保存调用历史失败: {e}")

    def find_endpoints(self, data_category: str,
                      status: str = 'active') -> List[Dict]:
        """
        查找支持特定数据类型的所有端点

        Args:
            data_category: 数据分类（如 DAILY_KLINE）
            status: 状态过滤（active, testing, deprecated）

        Returns:
            匹配的端点列表，按优先级和质量评分排序
        """
        matches = []

        for endpoint_name, source in self.registry.items():
            metadata = source['metadata']

            if metadata.get('status') != status:
                continue

            if metadata.get('data_category') != data_category:
                continue

            matches.append({
                'endpoint_name': endpoint_name,
                'source_name': metadata.get('source_name'),
                'data_category': metadata.get('data_category'),
                'target_db': metadata.get('target_db'),
                'quality_score': metadata.get('data_quality_score', 0),
                'priority': metadata.get('priority', 999),
                'health_status': metadata.get('health_status', 'unknown'),
                'success_rate': metadata.get('success_rate', 100),
                'avg_response_time': metadata.get('avg_response_time', 0)
            })

        # 按优先级（数字越小优先级越高）和质量评分排序
        matches.sort(key=lambda x: (x['priority'], -x['quality_score']))

        return matches

    def get_best_endpoint(self, data_category: str) -> Optional[Dict]:
        """
        获取最佳数据端点（智能路由）

        选择标准：
        1. 状态为active
        2. 健康状态为healthy或degraded（排除failed）
        3. 按优先级排序
        4. 同优先级按质量评分排序
        """
        endpoints = self.find_endpoints(data_category)

        # 过滤掉健康状态为failed的端点
        healthy_endpoints = [
            ep for ep in endpoints
            if ep.get('health_status') != 'failed'
        ]

        return healthy_endpoints[0] if healthy_endpoints else None

    def search_sources(self, keyword: str = None,
                      data_category: str = None,
                      source_name: str = None,
                      tags: List[str] = None) -> List[Dict]:
        """
        搜索可用数据源

        Args:
            keyword: 关键词搜索（匹配endpoint_name或description）
            data_category: 数据分类过滤
            source_name: 数据源名称过滤
            tags: 标签过滤

        Returns:
            匹配的数据源列表
        """
        results = []

        for endpoint_name, source in self.registry.items():
            metadata = source['metadata']

            # 关键词匹配
            if keyword:
                text = f"{endpoint_name} {metadata.get('description', '')}"
                if keyword.lower() not in text.lower():
                    continue

            # 数据分类过滤
            if data_category and metadata.get('data_category') != data_category:
                continue

            # 数据源名称过滤
            if source_name and metadata.get('source_name') != source_name:
                continue

            # 标签过滤
            if tags:
                source_tags = metadata.get('tags', [])
                if not any(tag in source_tags for tag in tags):
                    continue

            results.append({
                'endpoint_name': endpoint_name,
                'metadata': metadata
            })

        return results

    def list_all_endpoints(self) -> pd.DataFrame:
        """列出所有已注册的数据端点（便于查看和管理）"""
        data = []

        for endpoint_name, source in self.registry.items():
            metadata = source['metadata']

            data.append({
                '数据源': metadata.get('source_name'),
                '端点名称': endpoint_name,
                '数据分类': metadata.get('data_category'),
                '目标数据库': metadata.get('target_db'),
                '目标表': metadata.get('table_name'),
                '更新频率': metadata.get('update_frequency'),
                '质量评分': metadata.get('data_quality_score'),
                '优先级': metadata.get('priority'),
                '状态': metadata.get('status'),
                '健康状态': metadata.get('health_status'),
                '成功率': f"{metadata.get('success_rate', 100):.1f}%",
                '平均响应时间': f"{metadata.get('avg_response_time', 0):.2f}s",
                '调用次数': metadata.get('total_calls', 0),
                '最后成功': metadata.get('last_success_time')
            })

        return pd.DataFrame(data)

    def get_endpoint_details(self, endpoint_name: str) -> Optional[Dict]:
        """获取端点详细信息"""
        source = self.registry.get(endpoint_name)
        if not source:
            return None

        return {
            'endpoint_name': endpoint_name,
            'metadata': source['metadata'],
            'call_count': source['call_count'],
            'last_call': source['last_call']
        }

    def health_check(self, endpoint_name: str = None) -> Dict:
        """
        执行健康检查

        Args:
            endpoint_name: 指定端点名称，None表示检查所有

        Returns:
            健康检查结果
        """
        if endpoint_name:
            return self._check_single_endpoint(endpoint_name)
        else:
            return self._check_all_endpoints()

    def _check_single_endpoint(self, endpoint_name: str) -> Dict:
        """检查单个端点"""
        source = self.registry.get(endpoint_name)
        if not source:
            return {
                'endpoint_name': endpoint_name,
                'status': 'not_found'
            }

        metadata = source['metadata']
        test_params = metadata.get('test_parameters', {})

        try:
            # 使用测试参数调用
            data = source['handler'].fetch(**test_params)

            # 验证返回数据
            self._validate_data(endpoint_name, data)

            return {
                'endpoint_name': endpoint_name,
                'status': 'healthy',
                'response_time': metadata.get('avg_response_time', 0),
                'sample_record': data.head(1).to_dict() if hasattr(data, 'head') else str(data)[:100]
            }
        except Exception as e:
            return {
                'endpoint_name': endpoint_name,
                'status': 'unhealthy',
                'error': str(e)
            }

    def _check_all_endpoints(self) -> Dict:
        """检查所有端点"""
        results = {}

        for endpoint_name in self.registry.keys():
            results[endpoint_name] = self._check_single_endpoint(endpoint_name)

        return {
            'total': len(results),
            'healthy': sum(1 for r in results.values() if r['status'] == 'healthy'),
            'unhealthy': sum(1 for r in results.values() if r['status'] == 'unhealthy'),
            'details': results
        }


class LRUCache:
    """简单的LRU缓存实现"""
    def __init__(self, maxsize=100):
        from collections import OrderedDict
        self.cache = OrderedDict()
        self.maxsize = maxsize

    def get(self, key):
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        return None

    def __setitem__(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.maxsize:
            self.cache.popitem(last=False)
```

---

## 4️⃣ 数据源处理器实现

```python
# src/core/data_source_handlers.py
"""
具体数据源处理器实现
"""
import importlib
from typing import Dict, Any
import pandas as pd


class BaseDataSourceHandler:
    """数据源处理器基类"""

    def __init__(self, config: Dict):
        self.config = config
        self.endpoint_name = config['endpoint_name']
        self.source_name = config.get('source_name', '')

    def fetch(self, **kwargs) -> pd.DataFrame:
        """获取数据（子类必须实现）"""
        raise NotImplementedError

    def _map_arguments(self, args: Dict) -> Dict:
        """参数映射"""
        param_mapping = self.config.get('source_config', {}).get('param_mapping', {})
        return {param_mapping.get(k, k): v for k, v in args.items()}


class AkshareHandler(BaseDataSourceHandler):
    """AKShare数据源处理器"""

    def __init__(self, config: Dict):
        super().__init__(config)
        self.module = importlib.import_module('akshare')
        self.function_name = config['source_config']['function_name']

    def fetch(self, **kwargs) -> pd.DataFrame:
        # 参数映射
        mapped_args = self._map_arguments(kwargs)

        # 动态调用akshare函数
        func = getattr(self.module, self.function_name)
        return func(**mapped_args)


class TushareHandler(BaseDataSourceHandler):
    """TuShare数据源处理器（带token管理）"""

    def __init__(self, config: Dict):
        super().__init__(config)
        import tushare as ts

        token_env_var = config['source_config'].get('token_env_var')
        if token_env_var:
            import os
            token = os.getenv(token_env_var)
            if not token:
                raise ValueError(f"环境变量 {token_env_var} 未设置")
        else:
            token = config['source_config'].get('token')

        self.pro = ts.pro_api(token)
        self.api_name = config['source_config']['api_name']

    def fetch(self, **kwargs) -> pd.DataFrame:
        # 调用tushare API
        return self.pro.query(
            self.api_name,
            **kwargs,
            fields=self.config.get('source_config', {}).get('fields')
        )


class BaostockHandler(BaseDataSourceHandler):
    """BaoStock数据源处理器"""

    def __init__(self, config: Dict):
        super().__init__(config)
        import baostock as bs
        self.bs = bs
        self.login()

    def login(self):
        """登录baostock"""
        lg = self.bs.login()
        if lg.error_code != '0':
            raise ConnectionError(f"BaoStock登录失败: {lg.error_msg}")

    def fetch(self, **kwargs) -> pd.DataFrame:
        # 调用baostock query
        fields = self.config.get('source_config', {}).get('fields', '')
        return self.bs.query_stock_basic(**kwargs).get_data()

    def __del__(self):
        """退出登录"""
        try:
            self.bs.logout()
        except:
            pass


class TdxHandler(BaseDataSourceHandler):
    """通达信数据源处理器（直连）"""

    def __init__(self, config: Dict):
        super().__init__(config)
        from pytdx.hq import TdxHq_API
        self.api = TdxHq_API()

        conn_config = config.get('source_config', {})
        self.host = conn_config.get('host', '119.147.212.81')
        self.port = conn_config.get('port', 7709)

    def fetch(self, **kwargs) -> pd.DataFrame:
        # 连接通达信
        if not self.api.connected:
            self.api.connect(self.host, self.port)

        # 调用相应接口
        symbols = kwargs.get('symbols', [])
        if not symbols:
            raise ValueError("symbols参数不能为空")

        # 获取实时行情
        data = self.api.get_security_quotes(
            [(1, symbol) for symbol in symbols]  # 1表示深圳市场
        )

        return pd.DataFrame(data)


class WebCrawlerHandler(BaseDataSourceHandler):
    """爬虫数据源处理器"""

    def __init__(self, config: Dict):
        super().__init__(config)
        import requests
        self.requests = requests
        self.endpoint_url = config['endpoint_url']
        self.method = config['source_config'].get('method', 'GET')
        self.headers = config['source_config'].get('headers', {})
        self.response_format = config['source_config'].get('response_format', 'json')
        self.json_path = config['source_config'].get('json_path')

    def fetch(self, **kwargs) -> pd.DataFrame:
        # 构建请求
        url = self.endpoint_url
        params = {k: v for k, v in kwargs.items() if v is not None}

        # 发送请求
        if self.method.upper() == 'GET':
            response = self.requests.get(url, params=params, headers=self.headers)
        else:
            response = self.requests.post(url, json=params, headers=self.headers)

        response.raise_for_status()

        # 解析响应
        if self.response_format == 'json':
            data = response.json()

            # JSON路径提取
            if self.json_path:
                # 使用parse_json_path提取数据
                data = self._parse_json_path(data, self.json_path)

            return pd.DataFrame(data)
        else:
            raise ValueError(f"不支持的响应格式: {self.response_format}")

    def _parse_json_path(self, data: Any, path: str) -> Any:
        """简单的JSON路径解析"""
        # 支持类似 $.data.diff 的路径
        if path.startswith('$.'):
            parts = path[2:].split('.')
            for part in parts:
                if isinstance(data, dict):
                    data = data.get(part)
                elif isinstance(data, list) and part.isdigit():
                    data = data[int(part)]
                else:
                    raise ValueError(f"无法解析JSON路径: {path}")
            return data
        return data


class LocalFileHandler(BaseDataSourceHandler):
    """本地文件数据源处理器"""

    def __init__(self, config: Dict):
        super().__init__(config)
        self.file_path = config['endpoint_url']
        self.file_format = config.get('response_format', 'csv')

    def fetch(self, **kwargs) -> pd.DataFrame:
        if self.file_format == 'csv':
            return pd.read_csv(self.file_path, **kwargs)
        elif self.file_format == 'excel':
            return pd.read_excel(self.file_path, **kwargs)
        elif self.file_format == 'json':
            return pd.read_json(self.file_path, **kwargs)
        else:
            raise ValueError(f"不支持的文件格式: {self.file_format}")
```

---

## 5️⃣ FastAPI管理接口

```python
# web/backend/app/api/data_sources.py
"""
数据源管理API
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from pydantic import BaseModel
import pandas as pd

from src.core.data_source_manager import DataSourceManager

router = APIRouter(prefix="/api/v1/data-sources", tags=["数据源管理"])

# 全局单例
_manager = None


def get_manager():
    """获取数据源管理器单例"""
    global _manager
    if _manager is None:
        _manager = DataSourceManager()
    return _manager


class DataSourceSearchRequest(BaseModel):
    keyword: Optional[str] = None
    data_category: Optional[str] = None
    source_name: Optional[str] = None
    tags: Optional[List[str]] = None


@router.get("/list")
async def list_all_sources():
    """
    列出所有已注册的数据源

    返回完整的数据源清单，包括：
    - 数据源名称
    - 端点名称
    - 数据分类
    - 目标数据库和表
    - 质量评分和优先级
    - 健康状态和性能指标
    """
    manager = get_manager()
    df = manager.list_all_endpoints()

    return {
        "total": len(df),
        "sources": df.to_dict(orient='records')
    }


@router.get("/find")
async def find_data_sources(
    data_category: str = Query(..., description="数据分类，如 DAILY_KLINE"),
    status: str = Query("active", description="状态过滤")
):
    """
    查找支持特定数据类型的数据源

    示例:
    GET /api/v1/data-sources/find?data_category=DAILY_KLINE&status=active

    返回按优先级和质量排序的可用数据源列表
    """
    manager = get_manager()
    endpoints = manager.find_endpoints(data_category, status)

    return {
        "data_category": data_category,
        "found": len(endpoints),
        "sources": endpoints
    }


@router.get("/best")
async def get_best_source(
    data_category: str = Query(..., description="数据分类")
):
    """
    获取最佳数据源（智能路由）

    自动选择优先级最高、质量最好的健康数据源

    示例:
    GET /api/v1/data-sources/best?data_category=DAILY_KLINE
    """
    manager = get_manager()
    endpoint = manager.get_best_endpoint(data_category)

    if not endpoint:
        raise HTTPException(status_code=404, detail=f"未找到可用的 {data_category} 数据源")

    return endpoint


@router.post("/search")
async def search_sources(request: DataSourceSearchRequest):
    """
    高级搜索数据源

    支持关键词、分类、标签等多维度搜索
    """
    manager = get_manager()
    results = manager.search_sources(
        keyword=request.keyword,
        data_category=request.data_category,
        source_name=request.source_name,
        tags=request.tags
    )

    return {
        "total": len(results),
        "results": results
    }


@router.get("/details/{endpoint_name}")
async def get_endpoint_details(endpoint_name: str):
    """
    获取数据端点详细信息

    包括完整的配置、参数定义、质量规则等
    """
    manager = get_manager()
    details = manager.get_endpoint_details(endpoint_name)

    if not details:
        raise HTTPException(status_code=404, detail=f"数据源 {endpoint_name} 不存在")

    return details


@router.post("/health-check")
async def health_check(
    endpoint_name: Optional[str] = Query(None, description="指定端点名称，不指定则检查所有")
):
    """
    执行健康检查

    对数据源进行实际调用测试，验证可用性

    示例:
    POST /api/v1/data-sources/health-check?endpoint_name=akshare.stock_zh_a_hist
    """
    manager = get_manager()
    result = manager.health_check(endpoint_name)

    return result


@router.get("/call-history/{endpoint_name}")
async def get_call_history(
    endpoint_name: str,
    limit: int = Query(100, description="返回记录数"),
    success_only: bool = Query(False, description="仅显示成功记录")
):
    """
    获取数据源调用历史

    用于监控和分析数据源使用情况
    """
    manager = get_manager()

    # 查询数据库
    query = """
        SELECT * FROM data_source_call_history
        WHERE endpoint_name = %s
    """
    params = [endpoint_name]

    if success_only:
        query += " AND success = TRUE"

    query += " ORDER BY call_time DESC LIMIT %s"
    params.append(limit)

    with manager.db_manager.get_postgresql_connection() as conn:
        df = pd.read_sql(query, conn, params=params)

    return {
        "endpoint_name": endpoint_name,
        "total_calls": len(df),
        "history": df.to_dict(orient='records')
    }


@router.get("/statistics/summary")
async def get_statistics_summary():
    """
    获取数据源统计摘要

    包括：
    - 总数据源数量
    - 健康数据源数量
    - 平均成功率
    - 调用次数统计
    - 性能指标统计
    """
    manager = get_manager()

    query = """
        SELECT
            source_name,
            COUNT(*) as endpoint_count,
            AVG(success_rate) as avg_success_rate,
            AVG(avg_response_time) as avg_response_time,
            SUM(total_calls) as total_calls,
            SUM(CASE WHEN health_status = 'healthy' THEN 1 ELSE 0 END) as healthy_count,
            SUM(CASE WHEN health_status = 'failed' THEN 1 ELSE 0 END) as failed_count
        FROM data_source_registry
        WHERE status = 'active'
        GROUP BY source_name
    """

    with manager.db_manager.get_postgresql_connection() as conn:
        df = pd.read_sql(query, conn)

    return {
        "summary": {
            "total_endpoints": df['endpoint_count'].sum(),
            "total_calls": df['total_calls'].sum(),
            "overall_success_rate": df['avg_success_rate'].mean(),
            "healthy_endpoints": df['healthy_count'].sum(),
            "failed_endpoints": df['failed_count'].sum()
        },
        "by_source": df.to_dict(orient='records')
    }


@router.post("/sync-from-yaml")
async def sync_from_yaml():
    """
    从YAML配置同步数据源到数据库

    用于初始化或更新数据源注册表
    """
    manager = get_manager()

    try:
        # 重新加载注册表
        manager._load_registry()

        return {
            "status": "success",
            "message": "数据源配置同步成功",
            "active_sources": len(manager.registry)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"同步失败: {str(e)}")
```

---

## 6️⃣ Grafana数据源管理仪表板

### Prometheus监控指标

```python
# src/monitoring/data_source_metrics.py
"""
数据源监控指标导出器
"""
from prometheus_client import Gauge, Counter, Histogram

# 定义数据源监控指标
data_source_up = Gauge(
    'data_source_up',
    '数据源是否可用（1=可用，0=不可用）',
    ['endpoint_name', 'source_name', 'data_category']
)

data_source_response_time = Histogram(
    'data_source_response_time_seconds',
    '数据源响应时间',
    ['endpoint_name', 'source_name'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

data_source_calls_total = Counter(
    'data_source_calls_total',
    '数据源调用总次数',
    ['endpoint_name', 'source_name', 'status']  # status=success/failure
)

data_source_success_rate = Gauge(
    'data_source_success_rate',
    '数据源成功率（百分比）',
    ['endpoint_name', 'source_name']
)

data_source_record_count = Histogram(
    'data_source_record_count',
    '数据源返回记录数',
    ['endpoint_name', 'source_name'],
    buckets=[1, 10, 100, 1000, 10000]
)

data_source_quality_score = Gauge(
    'data_source_quality_score',
    '数据源质量评分',
    ['endpoint_name', 'source_name']
)

data_source_health_status = Gauge(
    'data_source_health_status',
    '数据源健康状态（3=healthy，2=degraded，1=failed）',
    ['endpoint_name', 'source_name']
)


class DataSourceMetricsExporter:
    """数据源指标导出器"""

    @staticmethod
    def update_call_metrics(endpoint_name: str, source_name: str,
                           success: bool, response_time: float,
                           record_count: int):
        """更新调用指标"""
        # 调用次数
        status = 'success' if success else 'failure'
        data_source_calls_total.labels(
            endpoint_name=endpoint_name,
            source_name=source_name,
            status=status
        ).inc()

        # 响应时间
        if response_time is not None:
            data_source_response_time.labels(
                endpoint_name=endpoint_name,
                source_name=source_name
            ).observe(response_time)

        # 记录数
        if record_count is not None:
            data_source_record_count.labels(
                endpoint_name=endpoint_name,
                source_name=source_name
            ).observe(record_count)

    @staticmethod
    def update_health_metrics(endpoint_name: str, source_name: str,
                             health_status: str, quality_score: float,
                             success_rate: float):
        """更新健康指标"""
        # 可用性
        is_up = 1 if health_status != 'failed' else 0
        data_source_up.labels(
            endpoint_name=endpoint_name,
            source_name=source_name,
            data_category=''  # 需要从配置获取
        ).set(is_up)

        # 健康状态
        status_map = {'healthy': 3, 'degraded': 2, 'failed': 1, 'unknown': 0}
        data_source_health_status.labels(
            endpoint_name=endpoint_name,
            source_name=source_name
        ).set(status_map.get(health_status, 0))

        # 质量评分
        data_source_quality_score.labels(
            endpoint_name=endpoint_name,
            source_name=source_name
        ).set(quality_score)

        # 成功率
        data_source_success_rate.labels(
            endpoint_name=endpoint_name,
            source_name=source_name
        ).set(success_rate)
```

### Grafana仪表板JSON

```json
{
  "dashboard": {
    "title": "数据源管理仪表板",
    "tags": ["数据源", "监控"],
    "timezone": "browser",
    "schemaVersion": 16,
    "version": 0,
    "refresh": "30s",
    "panels": [
      {
        "id": 1,
        "title": "数据源总览",
        "type": "stat",
        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 0},
        "targets": [
          {
            "expr": "count(data_source_up{endpoint_name=~\".*\"})",
            "legendFormat": "总数据源"
          },
          {
            "expr": "count(data_source_up == 1)",
            "legendFormat": "可用数据源"
          },
          {
            "expr": "count(data_source_up == 0)",
            "legendFormat": "不可用数据源"
          }
        ]
      },
      {
        "id": 2,
        "title": "数据源健康状态分布",
        "type": "piechart",
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8},
        "targets": [
          {
            "expr": "count by (health_status) (data_source_health_status)",
            "legendFormat": "{{health_status}}"
          }
        ]
      },
      {
        "id": 3,
        "title": "各数据源调用次数（24小时）",
        "type": "graph",
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8},
        "targets": [
          {
            "expr": "sum by (source_name) (increase(data_source_calls_total[24h]))",
            "legendFormat": "{{source_name}}"
          }
        ]
      },
      {
        "id": 4,
        "title": "数据源响应时间对比",
        "type": "graph",
        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 16},
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(data_source_response_time_seconds_bucket[5m]))",
            "legendFormat": "{{endpoint_name}} (p95)"
          },
          {
            "expr": "histogram_quantile(0.50, rate(data_source_response_time_seconds_bucket[5m]))",
            "legendFormat": "{{endpoint_name}} (p50)"
          }
        ]
      },
      {
        "id": 5,
        "title": "数据源成功率趋势",
        "type": "graph",
        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 24},
        "targets": [
          {
            "expr": "data_source_success_rate",
            "legendFormat": "{{endpoint_name}}"
          }
        ]
      },
      {
        "id": 6,
        "title": "数据源质量评分对比",
        "type": "bar gauge",
        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 32},
        "targets": [
          {
            "expr": "data_source_quality_score",
            "legendFormat": "{{endpoint_name}}"
          }
        ]
      },
      {
        "id": 7,
        "title": "数据源返回记录数分布",
        "type": "heatmap",
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 40},
        "targets": [
          {
            "expr": "sum by (endpoint_name) (rate(data_source_record_count_bucket[5m]))",
            "legendFormat": "{{endpoint_name}}"
          }
        ]
      },
      {
        "id": 8,
        "title": "数据源错误率监控",
        "type": "graph",
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 40},
        "targets": [
          {
            "expr": "rate(data_source_calls_total{status=\"failure\"}[5m]) / rate(data_source_calls_total[5m]) * 100",
            "legendFormat": "{{endpoint_name}} 错误率"
          }
        ]
      },
      {
        "id": 9,
        "title": "数据源调用排行榜（Top 10）",
        "type": "table",
        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 48},
        "targets": [
          {
            "expr": "topk(10, sum by (endpoint_name) (increase(data_source_calls_total[24h])))",
            "legendFormat": "{{endpoint_name}}"
          }
        ]
      }
    ]
  }
}
```

### 仪表板使用指南

**导入到Grafana**:
1. 登录Grafana（http://localhost:3000）
2. 进入 "+" → "Import"
3. 粘贴上面的JSON配置
4. 选择Prometheus数据源
5. 点击"Import"

**关键面板说明**:
- **数据源总览**: 实时显示可用/不可用数据源数量
- **健康状态分布**: 饼图展示healthy/degraded/failed比例
- **响应时间对比**: 折线图展示各数据源p50/p95响应时间
- **成功率趋势**: 监控数据源稳定性
- **质量评分**: 对比各数据源质量水平
- **错误率监控**: 及时发现异常数据源
- **调用排行榜**: 了解高频使用的数据源

---

## 7️⃣ 使用示例

### 场景1: 统一调用接口

```python
from src.core.data_source_manager import DataSourceManager

# 初始化管理器
manager = DataSourceManager()

# 获取日线数据（使用akshare）
kline_data = manager.get_data(
    endpoint_name="akshare.stock_zh_a_hist",
    symbol="000001",
    period="daily",
    start_date="20240101",
    end_date="20240131",
    adjust="qfq"
)

# 获取tushare数据
basic_data = manager.get_data(
    endpoint_name="tushare.stock_basic",
    list_status="L",
    fields="ts_code,symbol,name,area,industry"
)

# 获取实时行情
realtime_data = manager.get_data(
    endpoint_name="tdx.get_security_quotes",
    symbols=["000001", "600000", "000002"]
)
```

### 场景2: 智能路由

```python
# 自动选择最佳数据源
best_endpoint = manager.get_best_endpoint("DAILY_KLINE")

# 输出: {'endpoint_name': 'tushare.daily', 'source_name': 'tushare', ...}

# 直接使用最佳数据源
data = manager.get_data(
    endpoint_name=best_endpoint['endpoint_name'],
    ts_code="000001.SZ",
    start_date="20240101",
    end_date="20240131"
)
```

### 场景3: 查找和搜索

```python
# 查找所有支持日线K线的数据源
endpoints = manager.find_endpoints("DAILY_KLINE")
for ep in endpoints:
    print(f"{ep['endpoint_name']}: 质量={ep['quality_score']}, 优先级={ep['priority']}")

# 搜索免费数据源
free_sources = manager.search_source(tags=["free"])

# 关键词搜索
results = manager.search_source(keyword="实时行情")
```

### 场景4: 健康检查

```python
# 检查所有数据源
health_report = manager.health_check()
print(f"总计: {health_report['total']}")
print(f"健康: {health_report['healthy']}")
print(f"异常: {health_report['unhealthy']}")

# 检查单个数据源
status = manager.health_check("akshare.stock_zh_a_hist")
if status['status'] == 'healthy':
    print("数据源正常")
else:
    print(f"数据源异常: {status.get('error')}")
```

### 场景5: API调用

```bash
# 列出所有数据源
curl "http://localhost:8000/api/v1/data-sources/list"

# 查找日线数据源
curl "http://localhost:8000/api/v1/data-sources/find?data_category=DAILY_KLINE"

# 获取最佳数据源
curl "http://localhost:8000/api/v1/data-sources/best?data_category=DAILY_KLINE"

# 健康检查
curl -X POST "http://localhost:8000/api/v1/data-sources/health-check"

# 搜索数据源
curl -X POST "http://localhost:8000/api/v1/data-sources/search" \
  -H "Content-Type: application/json" \
  -d '{"tags": ["free", "realtime"]}'

# 获取统计摘要
curl "http://localhost:8000/api/v1/data-sources/statistics/summary"
```

---

## 8️⃣ 实施路线图

### 第一阶段：基础设施（1周）

- [x] 创建PostgreSQL注册表（data_source_registry + call_history）
- [ ] 创建YAML配置文件模板
- [ ] 实现BaseDataSourceHandler和基础处理器
- [ ] 实现DataSourceManager核心类
- [ ] 单元测试

### 第二阶段：核心功能（1周）

- [ ] 实现所有数据源处理器（Akshare/Tushare/Baostock/Tdx/Crawler）
- [ ] 实现参数映射和验证
- [ ] 实现健康检查机制
- [ ] 实现智能路由逻辑
- [ ] LRU缓存优化

### 第三阶段：API和监控（1周）

- [ ] 实现FastAPI管理接口
- [ ] 集成Prometheus监控指标
- [ ] 创建Grafana仪表板
- [ ] API文档和测试

### 第四阶段：优化和部署（1周）

- [ ] 性能优化（连接池、并发调用）
- [ ] 故障转移和降级机制
- [ ] 数据源自动发现和注册
- [ ] 生产环境部署和监控

---

## 9️⃣ 维护流程

```
新数据源 → 注册测试 → 质量评估 → 生产使用 → 定期巡检 → 下线归档
   ↓          ↓          ↓          ↓          ↓          ↓
 YAML配置   健康检查   评分打分    上线监控   性能统计   状态标记
```

**关键维护任务**:
1. **每日**: 查看Grafana仪表板，关注异常数据源
2. **每周**: 评估数据源质量评分，调整优先级
3. **每月**: 清理废弃数据源，更新配置
4. **每季度**: 全面审计，优化数据源组合

---

## 🎁 方案优势总结

| 特性 | 实现效果 | 对比优化前 |
|------|---------|----------|
| **集中管理** | PostgreSQL + YAML双存储 | ✅ 配置化+持久化 |
| **快速查找** | 按分类/标签/关键词搜索 | ✅ 多维度搜索 |
| **智能路由** | 自动选择最优数据源 | ✅ 基于质量+性能 |
| **健康监控** | 实时健康检查和告警 | ✅ 主动发现异常 |
| **性能追踪** | 调用历史和统计 | ✅ 完整数据链路 |
| **可视化** | Grafana仪表板 | ✅ 8大监控面板 |
| **统一调用** | 单一入口屏蔽差异 | ✅ 简化使用 |
| **故障转移** | 自动降级失败数据源 | ✅ 提高可用性 |
| **全生命周期** | 从注册到下线全管理 | ✅ 规范化流程 |

---

**文档版本**: v2.0
**最后更新**: 2026-01-02
**状态**: 优化完成，等待实施
