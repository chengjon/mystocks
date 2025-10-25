# MyStocks 快速行动计划

> 基于第一性原理架构审查，本文档提供可立即执行的具体步骤

**目标**: 在8周内将系统复杂度降低70%，同时保持核心功能100%可用

---

## 第1周：代码清理（立即可做）

### Day 1: 临时文件清理

```bash
# 1. 备份当前代码
cd /opt/claude/mystocks_spec
git add -A
git commit -m "Backup before cleanup"
git tag backup-before-cleanup

# 2. 删除临时文件
rm -rf temp/
rm -rf htmlcov/
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +

# 3. 清理备份文件
find . -name "*_backup.py" -delete
find . -name "*_old.py" -delete
find . -name "*_v2.py" -delete

# 4. 验证Git状态
git status
git add -A
git commit -m "Clean up temporary files and backups"
```

**预期成果**: 删除~50个文件，减少~10MB代码

### Day 2-3: 识别未使用的适配器

```bash
# 1. 列出所有适配器
ls -la adapters/*.py

# 2. 搜索每个适配器的使用情况
for adapter in adapters/*_adapter.py; do
    name=$(basename $adapter .py)
    echo "=== Checking $name ==="
    grep -r "import.*$name" . --include="*.py" | grep -v adapters/
done

# 3. 创建使用情况报告
# 手动记录哪些适配器实际被使用
```

**决策标准**:
- ✅ 保留: akshare_adapter.py (主数据源)
- ⚠️ 保留: baostock_adapter.py (备用数据源)
- ❌ 移除: 其他未使用的适配器

### Day 4-5: 代码去重

```bash
# 1. 使用工具检测重复代码
pip install pylint
pylint --disable=all --enable=duplicate-code . > duplicates.txt

# 2. 手动审查重复代码
cat duplicates.txt

# 3. 提取公共函数
# 创建 utils/common.py 存放公共代码
# 重构重复代码调用公共函数
```

**预期成果**: 减少5000-10000行重复代码

---

## 第2周：数据库评估和迁移规划

### Step 1: 评估当前数据库使用情况

创建评估脚本 `scripts/database_assessment.py`:

```python
#!/usr/bin/env python3
"""评估各数据库实际使用情况"""

import os
from dotenv import load_dotenv

load_dotenv()

# 检查环境变量
databases = {
    'TDengine': ['TDENGINE_HOST', 'TDENGINE_USER'],
    'PostgreSQL': ['POSTGRESQL_HOST', 'POSTGRESQL_USER'],
    'MySQL': ['MYSQL_HOST', 'MYSQL_USER'],
    'Redis': ['REDIS_HOST', 'REDIS_PORT']
}

print("=== Database Configuration Check ===")
for db, vars in databases.items():
    configured = all(os.getenv(v) for v in vars)
    print(f"{db}: {'✅ Configured' if configured else '❌ Not configured'}")

# TODO: 连接各数据库，检查表数量和数据量
# TODO: 生成使用报告
```

运行评估：

```bash
python scripts/database_assessment.py > database_usage_report.txt
```

### Step 2: 制定迁移决策

基于评估结果填写决策表：

| 数据库 | 表数量 | 数据量 | 实际使用率 | 决策 |
|-------|--------|--------|-----------|------|
| TDengine | ? | ? | ? | 保留/迁移/移除 |
| PostgreSQL | ? | ? | ? | 保留 |
| MySQL | ? | ? | ? | 迁移到PostgreSQL |
| Redis | ? | ? | ? | 评估后决定 |

### Step 3: 数据备份

```bash
# PostgreSQL备份
pg_dump -h $POSTGRESQL_HOST -U $POSTGRESQL_USER -d $POSTGRESQL_DATABASE \
    -F c -f backup_postgresql_$(date +%Y%m%d).dump

# MySQL备份
mysqldump -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PASSWORD \
    $MYSQL_DATABASE > backup_mysql_$(date +%Y%m%d).sql

# TDengine备份（如果有数据）
# 参考TDengine官方文档
```

**关键检查点**: ✅ 所有备份文件完整且可恢复

---

## 第3-4周：核心架构重构

### 新架构目录结构

```
mystocks_simple/
├── config/
│   ├── __init__.py
│   ├── settings.py          # 配置管理（200行）
│   └── database.py          # 数据库连接（150行）
│
├── models/
│   ├── __init__.py
│   └── schemas.py           # Pydantic模型（300行）
│
├── data/
│   ├── __init__.py
│   ├── akshare_client.py    # AKShare客户端（250行）
│   ├── baostock_client.py   # Baostock客户端（250行）
│   └── loader.py            # 数据加载器（200行）
│
├── indicators/
│   ├── __init__.py
│   ├── calculator.py        # 指标计算（400行）
│   └── library.py           # 指标库（300行）
│
├── backtest/
│   ├── __init__.py
│   ├── engine.py            # 回测引擎（500行）
│   ├── strategy.py          # 策略基类（200行）
│   └── metrics.py           # 性能指标（200行）
│
├── api/
│   ├── __init__.py
│   ├── server.py            # FastAPI服务（300行）
│   └── routes.py            # API路由（200行）
│
├── scripts/
│   ├── init_database.py     # 初始化数据库（100行）
│   ├── fetch_data.py        # 数据获取脚本（150行）
│   └── run_backtest.py      # 回测脚本（150行）
│
└── tests/
    ├── test_data.py
    ├── test_indicators.py
    └── test_backtest.py

总计: ~4,000行核心代码 + 测试
```

### Step 1: 创建新项目结构

```bash
# 在当前项目目录创建新架构
mkdir -p mystocks_simple/{config,models,data,indicators,backtest,api,scripts,tests}

# 创建__init__.py
find mystocks_simple -type d -exec touch {}/__init__.py \;
```

### Step 2: 实现核心配置管理

创建 `mystocks_simple/config/settings.py`:

```python
#!/usr/bin/env python3
"""简化配置管理"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 加载.env文件
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

class DatabaseConfig(BaseSettings):
    """数据库配置"""
    host: str = os.getenv('POSTGRESQL_HOST', 'localhost')
    port: int = int(os.getenv('POSTGRESQL_PORT', 5432))
    user: str = os.getenv('POSTGRESQL_USER', 'postgres')
    password: str = os.getenv('POSTGRESQL_PASSWORD', '')
    database: str = os.getenv('POSTGRESQL_DATABASE', 'mystocks')

    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

class RedisConfig(BaseSettings):
    """Redis配置（可选）"""
    host: str = os.getenv('REDIS_HOST', 'localhost')
    port: int = int(os.getenv('REDIS_PORT', 6379))
    password: Optional[str] = os.getenv('REDIS_PASSWORD')
    db: int = int(os.getenv('REDIS_DB', 0))
    enabled: bool = os.getenv('REDIS_ENABLED', 'false').lower() == 'true'

class Settings(BaseSettings):
    """全局配置"""
    database: DatabaseConfig = DatabaseConfig()
    redis: RedisConfig = RedisConfig()

    # 数据源配置
    default_data_source: str = 'akshare'

    # 日志配置
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')
    log_file: str = 'mystocks.log'

# 全局配置实例
settings = Settings()
```

### Step 3: 实现简化的数据库连接

创建 `mystocks_simple/config/database.py`:

```python
#!/usr/bin/env python3
"""简化数据库连接管理"""

import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Generator
import logging

from .settings import settings

logger = logging.getLogger(__name__)

class Database:
    """PostgreSQL数据库连接管理"""

    def __init__(self):
        self.config = settings.database
        self._conn = None

    @contextmanager
    def get_connection(self) -> Generator:
        """获取数据库连接（上下文管理器）"""
        conn = None
        try:
            conn = psycopg2.connect(
                host=self.config.host,
                port=self.config.port,
                user=self.config.user,
                password=self.config.password,
                database=self.config.database,
                cursor_factory=RealDictCursor
            )
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def execute(self, query: str, params: tuple = None):
        """执行SQL查询"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                if cur.description:
                    return cur.fetchall()
                return None

# 全局数据库实例
db = Database()
```

### Step 4: 创建核心数据模型

创建 `mystocks_simple/models/schemas.py`:

```python
#!/usr/bin/env python3
"""数据模型定义"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field

class Symbol(BaseModel):
    """股票基础信息"""
    symbol: str = Field(..., description="股票代码")
    name: str = Field(..., description="股票名称")
    exchange: str = Field(..., description="交易所")
    sector: Optional[str] = Field(None, description="行业分类")
    is_active: bool = Field(True, description="是否有效")

class DailyBar(BaseModel):
    """日线行情"""
    symbol: str
    trade_date: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    amount: Decimal

class Indicator(BaseModel):
    """技术指标"""
    symbol: str
    trade_date: date
    indicator_name: str
    value: Decimal

class BacktestResult(BaseModel):
    """回测结果"""
    strategy_name: str
    symbol: str
    start_date: date
    end_date: date
    initial_capital: Decimal
    final_capital: Decimal
    total_return: Decimal
    sharpe_ratio: Optional[Decimal]
    max_drawdown: Optional[Decimal]
```

---

## 第5周：数据库Schema简化

### 简化的PostgreSQL Schema

创建 `scripts/init_database.sql`:

```sql
-- 1. 股票基础信息表
CREATE TABLE IF NOT EXISTS symbols (
    symbol VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    exchange VARCHAR(10) NOT NULL,
    sector VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_symbols_exchange ON symbols(exchange);
CREATE INDEX idx_symbols_sector ON symbols(sector);

-- 2. 日线行情表（TimescaleDB超表）
CREATE TABLE IF NOT EXISTS daily_bars (
    symbol VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,
    open DECIMAL(10,3) NOT NULL,
    high DECIMAL(10,3) NOT NULL,
    low DECIMAL(10,3) NOT NULL,
    close DECIMAL(10,3) NOT NULL,
    volume BIGINT NOT NULL,
    amount DECIMAL(20,2),
    PRIMARY KEY (symbol, trade_date)
);

-- 转换为TimescaleDB超表
SELECT create_hypertable('daily_bars', 'trade_date', if_not_exists => TRUE);

-- 创建索引
CREATE INDEX idx_daily_bars_symbol ON daily_bars(symbol, trade_date DESC);

-- 3. 技术指标表（TimescaleDB超表）
CREATE TABLE IF NOT EXISTS indicators (
    symbol VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,
    indicator_name VARCHAR(50) NOT NULL,
    value DECIMAL(20,6),
    metadata JSONB,
    PRIMARY KEY (symbol, trade_date, indicator_name)
);

SELECT create_hypertable('indicators', 'trade_date', if_not_exists => TRUE);

CREATE INDEX idx_indicators_symbol ON indicators(symbol, trade_date DESC);
CREATE INDEX idx_indicators_name ON indicators(indicator_name, trade_date DESC);

-- 4. 回测结果表
CREATE TABLE IF NOT EXISTS backtest_results (
    id SERIAL PRIMARY KEY,
    strategy_name VARCHAR(100) NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_capital DECIMAL(20,2) NOT NULL,
    final_capital DECIMAL(20,2) NOT NULL,
    total_return DECIMAL(10,4),
    sharpe_ratio DECIMAL(10,4),
    max_drawdown DECIMAL(10,4),
    win_rate DECIMAL(5,4),
    total_trades INT,
    parameters JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_backtest_strategy ON backtest_results(strategy_name, created_at DESC);
CREATE INDEX idx_backtest_symbol ON backtest_results(symbol, created_at DESC);

-- 5. 系统配置表（可选）
CREATE TABLE IF NOT EXISTS system_config (
    config_key VARCHAR(100) PRIMARY KEY,
    config_value TEXT NOT NULL,
    config_type VARCHAR(20) DEFAULT 'string',
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

运行初始化：

```bash
# 安装TimescaleDB扩展
psql -U postgres -d mystocks -c "CREATE EXTENSION IF NOT EXISTS timescaledb;"

# 执行Schema创建
psql -U postgres -d mystocks -f scripts/init_database.sql
```

---

## 第6-8周：渐进式迁移

### Week 6: 数据迁移

#### Task 1: 从MySQL迁移元数据

```python
#!/usr/bin/env python3
"""migrate_mysql_to_postgresql.py"""

import pymysql
import psycopg2
from config.settings import settings

def migrate_symbols():
    """迁移股票基础信息"""
    # 从MySQL读取
    mysql_conn = pymysql.connect(
        host=os.getenv('MYSQL_HOST'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE')
    )

    pg_conn = psycopg2.connect(settings.database.url)

    with mysql_conn.cursor() as cur:
        cur.execute("SELECT symbol, name, exchange, sector, is_active FROM symbols")
        rows = cur.fetchall()

    with pg_conn.cursor() as cur:
        for row in rows:
            cur.execute("""
                INSERT INTO symbols (symbol, name, exchange, sector, is_active)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (symbol) DO UPDATE SET
                    name = EXCLUDED.name,
                    exchange = EXCLUDED.exchange,
                    sector = EXCLUDED.sector,
                    is_active = EXCLUDED.is_active
            """, row)

    pg_conn.commit()
    mysql_conn.close()
    pg_conn.close()

    print("✅ Symbols migrated successfully")

if __name__ == '__main__':
    migrate_symbols()
```

#### Task 2: 从TDengine迁移时序数据（如需要）

```python
# 根据实际TDengine使用情况决定是否需要迁移
# 如果数据量小，可以重新从数据源获取
```

### Week 7: 功能验证

创建测试脚本验证核心功能：

```python
#!/usr/bin/env python3
"""test_core_functionality.py"""

import pytest
from mystocks_simple.data.akshare_client import AKShareClient
from mystocks_simple.indicators.calculator import IndicatorCalculator
from mystocks_simple.backtest.engine import BacktestEngine

def test_data_fetching():
    """测试数据获取"""
    client = AKShareClient()
    data = client.get_daily_bars('000001.SZ', start_date='2024-01-01', end_date='2024-10-01')
    assert len(data) > 0
    assert 'close' in data.columns

def test_indicator_calculation():
    """测试指标计算"""
    calc = IndicatorCalculator()
    # TODO: 实现测试

def test_backtest():
    """测试回测"""
    engine = BacktestEngine()
    # TODO: 实现测试

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

### Week 8: 全面切换

1. **用户验收测试**: 让实际用户测试新系统
2. **性能对比**: 对比新旧系统性能
3. **文档更新**: 更新所有文档和示例
4. **旧系统归档**: 将旧系统移至 `legacy/` 目录

---

## 关键检查点

### ✅ Week 1 完成标志
- [ ] temp/目录已删除
- [ ] 备份文件已清理
- [ ] 未使用的适配器已识别
- [ ] 代码重复案例已记录

### ✅ Week 2 完成标志
- [ ] 数据库使用报告已生成
- [ ] 迁移决策已制定
- [ ] 所有数据库已备份
- [ ] 备份可恢复性已验证

### ✅ Week 3-4 完成标志
- [ ] 新架构目录已创建
- [ ] 核心模块已实现（config, models, database）
- [ ] 单元测试通过
- [ ] 文档已编写

### ✅ Week 5 完成标志
- [ ] PostgreSQL Schema已创建
- [ ] TimescaleDB扩展已安装
- [ ] 索引已优化
- [ ] 性能测试通过

### ✅ Week 6-8 完成标志
- [ ] 数据迁移完成且验证
- [ ] 核心功能测试通过
- [ ] 用户验收测试通过
- [ ] 文档完整更新
- [ ] 旧系统已归档

---

## 风险应对

### 如果遇到数据迁移问题
1. **立即停止迁移**
2. 从备份恢复
3. 分析失败原因
4. 修复脚本后重试

### 如果遇到性能问题
1. 检查PostgreSQL配置
2. 添加必要索引
3. 优化查询语句
4. 如确实需要，考虑添加Redis缓存

### 如果团队抵触
1. 展示成本收益分析
2. 强调长期可维护性
3. 渐进式改进，不强制一步到位

---

## 每周进度报告模板

```markdown
# Week X Progress Report

## 完成的任务
- [ ] Task 1
- [ ] Task 2

## 遇到的问题
1. Problem 1 - 解决方案：...
2. Problem 2 - 待解决

## 下周计划
- [ ] Next task 1
- [ ] Next task 2

## 度量指标
- 代码行数: 当前XX行（目标XX行）
- 数据库数: 当前X个（目标X个）
- 测试覆盖率: XX%（目标70%）
```

---

## 快速参考命令

### 代码统计
```bash
# 统计Python文件数
find . -name "*.py" | wc -l

# 统计代码行数（需要cloc）
cloc . --include-lang=Python

# 查找大文件
find . -name "*.py" -exec wc -l {} + | sort -rn | head -20
```

### 数据库操作
```bash
# PostgreSQL连接
psql -U $POSTGRESQL_USER -d $POSTGRESQL_DATABASE

# 查看表大小
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

# 查看表数据量
SELECT
    schemaname,
    tablename,
    n_live_tup AS row_count
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC;
```

### Git操作
```bash
# 创建检查点
git tag -a checkpoint-week-1 -m "Week 1 cleanup complete"

# 查看变更统计
git diff --stat

# 回滚到上一个检查点
git reset --hard checkpoint-week-1
```

---

## 获取帮助

### 问题反馈
- 在项目中创建Issue记录问题
- 详细描述问题、预期行为、实际行为
- 附上错误日志和环境信息

### 参考文档
- PostgreSQL官方文档: https://www.postgresql.org/docs/
- TimescaleDB文档: https://docs.timescale.com/
- AKShare文档: https://akshare.akfamily.xyz/

---

**开始日期**: ________
**预期完成日期**: 8周后
**项目负责人**: ________

**祝重构顺利！Keep it simple!**
