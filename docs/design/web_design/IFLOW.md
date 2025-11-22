# A股量化交易分析与管理系统 - Web设计项目IFLOW文档

## 项目概览

本目录包含了一个完整的A股量化交易分析与管理系统的Web设计文档。项目采用Python + NiceGUI技术栈，为量化交易提供全方位的Web界面解决方案，包括实时行情监控、技术分析、策略回测、风险管理等核心功能。

**核心特点**:
- 🎯 **专业量化交易平台**: 针对A股市场特性设计（T+1、涨跌停、100股整数倍等）
- 🔄 **实时数据处理**: 支持WebSocket实时行情推送和3秒高频数据刷新
- 📊 **多维数据可视化**: 基于Plotly/ECharts的K线图、技术指标、资金流向等
- 🛡️ **全面风控管理**: 集成止损、止盈、风险监控和预警系统
- ⚡ **高性能架构**: PostgreSQL + TDengine双数据库架构，支持高频交易数据
- 🎛️ **NiceGUI原生界面**: Python原生Web框架，开发效率高，易于维护

## 项目结构

### 核心页面设计文档

| 文档 | 功能定位 | 技术重点 | Owner建议 |
|------|----------|----------|-----------|
| `1.仪表盘页面.md` | 全局市场概览与投资组合监控 | 实时数据聚合、卡片布局、行情汇总 | 前端(NiceGUI) |
| `2.市场行情页面.md` | 实时行情与技术指标分析 | WebSocket行情、K线图、TA-Lib指标 | 前端 + 后端 |
| `3.市场数据页面.md` | 市场基础数据与统计分析 | 批量数据处理、统计分析 | 数据工程 |
| `4.股票管理页面.md` | 自选股池与股票信息管理 | 股票池操作、CRUD、导入导出 | 前端 + 后端 |
| `5.数据分析页面.md` | 技术指标与条件筛选 | TA-Lib集成、自定义指标、批量计算 | 量化工程 |
| `6.风险管理页面.md` | 风险指标监控与预警 | 风险计算、预警系统、监控面板 | 风控工程 + 后端 |
| `7.策略回测管理页面.md` | 策略开发与回测分析 | 回测引擎、策略存储、GPU加速 | 量化工程 + 后端 |
| `8.交易管理页面.md` | 订单管理与交易执行 | 订单处理、交易记录、模拟交易 | 后端 + 运维 |
| `9.其他页面.md` | 系统设置与数据源配置 | 配置管理、数据源切换 | 数据工程 + 运维 |

### 管理与规范文档

| 文档 | 内容 | 用途 |
|------|------|------|
| `web_design_index.md` | 项目总览与技术架构 | 项目导入和总体了解 |
| `开发分工与里程碑.md` | 角色职责与项目里程碑 | 团队协作和任务分配 |
| `开发规范与接口契约.md` | API契约与开发规范 | 接口设计和代码标准 |

## 技术栈详解

### 前端技术栈
- **框架**: NiceGUI (Python原生Web框架)
- **可视化**: Plotly (K线图) + ECharts (图表组件)
- **UI组件**: ui.card、ui.table、ui.grid、ui.aggrid
- **实时通信**: WebSocket + Server Sent Events
- **响应式设计**: 支持桌面和平板设备

### 后端技术栈
- **开发语言**: Python 3.8+
- **异步框架**: asyncio + aiohttp
- **数据处理**: Pandas + NumPy + TA-Lib
- **任务队列**: Celery (可选)
- **缓存**: Redis (可选)

### 数据存储架构
- **主数据库**: PostgreSQL 17.x
  - 股票基础信息
  - 财务数据
  - 自选股分组
  - 策略配置
  - 回测结果
- **时序数据库**: TDengine 3.3.x
  - 分钟/秒级行情
  - 高频技术指标
  - 实时资金流向
- **扩展功能**: TimescaleDB (PostgreSQL扩展)

### 数据源优先级策略
1. **Wind** (机构付费数据，优先级最高)
2. **Tushare Pro** (专业金融数据)
3. **AKShare** (免费开源数据源)
4. **Baostock** (基础行情数据)
5. **爬虫** (数据兜底方案)

## 核心功能模块

### 1. 仪表盘 (Dashboard)
- **市场概况**: 三大指数实时行情、涨跌家数统计
- **投资组合**: 账户总览、持仓分布、盈亏分析
- **实时监控**: 自选股行情表、资金流向排名
- **预警系统**: 价格突破、技术信号、异动提醒

### 2. 市场行情 (Market Quote)
- **实时行情**: WebSocket推送，1秒高频刷新
- **技术分析**: K线图 + 20+ TA-Lib指标
- **复权功能**: 支持前复权/后复权/不复权
- **TDX集成**: 通达信客户端数据直连

### 3. 数据分析 (Data Analysis)
- **标准指标**: 70+ TA-Lib技术指标
- **自定义指标**: Python代码沙箱运行
- **批量计算**: 异步任务队列，支持全市场扫描
- **因子分析**: IC分析、分层回测、因子报告

### 4. 策略回测 (Strategy Backtest)
- **回测引擎**: 支持单策略/多策略回测
- **性能分析**: 净值曲线、收益统计、风险指标
- **策略管理**: 策略版本控制、参数优化
- **GPU加速**: 支持RAPIDS加速回测计算

### 5. 风险管理 (Risk Management)
- **实时监控**: VaR计算、最大回撤监控
- **预警系统**: 多级风险预警，邮件/微信通知
- **止损管理**: 动态止损、止盈策略
- **风控报告**: 定期风控分析报告

### 6. 交易管理 (Trade Management)
- **订单管理**: 模拟交易、订单执行记录
- **持仓监控**: 实时持仓、盈亏分析
- **A股特性**: T+1限制、涨跌停检测、整数倍验证
- **手续费计算**: 实时手续费和税费计算

## 开发流程指南

### 阶段一: 基础框架 (1周)
```bash
# 环境搭建
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# 项目初始化
mkdir -p src/{adapters,api,core,db}
touch requirements.txt
touch .env.example
```

### 阶段二: 数据接入 (2周)
```python
# 数据适配器开发
class AKShareAdapter(BaseAdapter):
    def get_daily(self, code: str, start: date, end: date) -> pd.DataFrame:
        # 实现akshare数据获取逻辑
        pass
    
    def get_realtime(self, codes: List[str]) -> pd.DataFrame:
        # 实现实时行情获取
        pass
```

### 阶段三: 核心功能 (4-6周)
按照优先级实现各页面功能：
1. 仪表盘基础功能
2. 市场行情与K线展示
3. 股票管理基础功能
4. 技术指标分析

### 阶段四: 高级功能 (3-4周)
1. 自定义指标系统
2. 策略回测引擎
3. 风险管理系统
4. 交易管理功能

## 接口契约规范

### REST API设计
```python
# 基础响应格式
{
    "code": 200,
    "message": "success",
    "data": {
        # 具体数据内容
    }
}

# 行情数据接口
GET /api/v1/market/quote?code=600519&period=d&start=2025-01-01&end=2025-11-12

# 实时行情WebSocket
ws://localhost:8000/ws/realtime
# 消息格式: {"type": "quote_update", "data": {...}}
```

### 数据库设计
```sql
-- PostgreSQL表结构示例
CREATE TABLE stock_basic (
    stock_code VARCHAR(10) PRIMARY KEY,
    stock_name VARCHAR(50),
    industry VARCHAR(30),
    market VARCHAR(10),
    list_date DATE
);

-- TDengine超级表示例
CREATE STABLE realtime_quote (
    ts TIMESTAMP,
    open_price DOUBLE,
    high_price DOUBLE,
    low_price DOUBLE,
    close_price DOUBLE,
    volume BIGINT
) TAGS (
    stock_code NCHAR(10)
);
```

## 部署与运维

### Docker部署
```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/mystocks
      - TDENGINE_URL=taos://tdengine:6041/mystocks
    depends_on:
      - postgres
      - tdengine
  
  postgres:
    image: postgres:17
    environment:
      POSTGRES_DB: mystocks
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  tdengine:
    image: tdengine/tdengine:3.3.0
    environment:
      TAOS_DATA_DIR: /var/lib/taos
    volumes:
      - tdengine_data:/var/lib/taos
```

### 监控配置
```python
# 健康检查
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": await check_database(),
        "tdengine": await check_tdengine(),
        "data_sources": await check_data_sources()
    }
```

## 质量保证

### 代码质量
- **代码规范**: flake8/ruff + black格式化
- **类型检查**: mypy类型注解
- **测试覆盖**: pytest + 覆盖率>80%
- **文档**: 所有API必须提供文档

### 测试策略
- **单元测试**: 核心算法、指标计算
- **集成测试**: 数据库操作、API接口
- **性能测试**: 高频数据处理、实时更新
- **端到端测试**: 完整业务流程

### CI/CD流程
```yaml
# .github/workflows/ci.yml
name: CI/CD
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest
      - name: Run linting
        run: flake8 src/
```

## 扩展开发指南

### 添加新数据源
1. 继承BaseAdapter基类
2. 实现必需的数据获取方法
3. 在数据源优先级中注册
4. 添加对应的配置和测试

### 自定义技术指标
1. 使用TA-Lib扩展
2. 或编写自定义Python函数
3. 注册到指标工厂
4. 添加到前端指标选择器

### 新页面开发
1. 在NiceGUI中添加路由
2. 创建对应的Markdown设计文档
3. 实现前后端接口
4. 添加集成测试

## 故障排查

### 常见问题
1. **数据源连接失败**: 检查API密钥和网络连接
2. **实时数据延迟**: 检查WebSocket连接状态
3. **内存使用过高**: 检查数据查询范围和缓存策略
4. **指标计算缓慢**: 启用GPU加速或优化算法

### 调试工具
```python
# 启用调试模式
import logging
logging.basicConfig(level=logging.DEBUG)

# 数据库连接测试
from src.db.connection import test_connections
test_connections()

# 实时数据模拟
python scripts/simulate_realtime_data.py
```

## 项目状态

- ✅ **基础架构**: 完成设计和规范制定
- ✅ **核心页面**: 完成9个主要页面的详细设计
- ✅ **开发规范**: 制定完整的API契约和代码标准
- 🔄 **MVP开发**: 准备进入第一阶段开发
- 📅 **预计完成**: 2025年12月前完成MVP版本

---

**项目维护者**: MyStocks开发团队  
**最后更新**: 2025-11-12  
**版本**: v1.0.0  
**许可证**: MIT License

*本文档为A股量化交易分析与管理系统的Web设计项目IFLOW指导文档，为开发团队提供全面的项目背景、技术规范和开发指南。*