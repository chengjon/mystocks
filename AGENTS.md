# AGENTS.md - Coding Agent Configuration

## Build/Lint/Test Commands

```bash
# Run all tests
pytest

# Run a single test file
pytest tests/unit/test_specific_module.py

# Run tests with coverage
pytest --cov=src --cov-report=html

# Run specific test function
pytest tests/unit/test_specific_module.py::test_specific_function

# Run integration tests
pytest tests/integration/ -v

# Run performance tests
pytest tests/performance/ -v

# Run e2e tests (Playwright)
npm run test:e2e

# Linting (Python)
black .
mypy src/
ruff check src/

# Check formatting
black --check .
mypy src/ --no-error-summary

# Frontend linting (TypeScript/Vue)
cd web/frontend && npm run lint

# Security scanning
bandit -r src/
safety check

# GPU API tests
cd gpu_api_system && python -m pytest tests/ -v

# Contract testing
pytest tests/contract/ -v

# AI-optimized testing
python ai_test_optimizer_toolkit/bin/ai_test_optimizer.py --run-all
```

## Code Style Guidelines

### Imports
- Use absolute imports with `src.` prefix: `from src.core import ConfigDrivenTableManager`
- Group imports: standard library, third-party, local imports
- Avoid wildcard imports
- Use explicit imports for clarity

### Formatting
- Use Black formatter with default settings
- Line length: 120 characters (Black default)
- Use double quotes for strings
- Use 4 spaces for indentation

### Types
- Use type hints for all function parameters and return values
- Prefer `from __future__ import annotations` for forward references
- Use Pydantic models for data validation where appropriate

### Naming Conventions
- Classes: PascalCase (`DataManager`)
- Functions/Variables: snake_case (`save_data_by_classification`)
- Constants: UPPER_SNAKE_CASE (`DATABASE_CONFIG`)
- Private members: prefixed with underscore (`_private_method`)

### Error Handling
- Use specific exception types
- Log errors with context before raising
- Implement retry logic for external API calls
- Use context managers for resource management

### Project Structure
- Source code: `src/` directory with standardized imports
- Tests: `tests/` directory mirroring source structure
- Scripts: `scripts/` directory organized by purpose
- Config: `config/` directory for YAML/JSON configs
- Docs: `docs/` directory for documentation
- Web application: `web/` directory (FastAPI backend + Vue 3 frontend)
- GPU API system: `gpu_api_system/` directory for accelerated computations
- Monitoring stack: `monitoring-stack/` directory for observability
- OpenSpec: `openspec/` directory for change management

### Database Architecture (Week 3+)
- Dual database: TDengine for high-frequency time-series, PostgreSQL for everything else
- Use `MyStocksUnifiedManager` for automatic routing
- Classification-based methods: `save_data_by_classification()`, `load_data_by_classification()`
- **TDengine**: High-frequency market data (Tick, minute K-lines) with 20:1 compression
- **PostgreSQL + TimescaleDB**: Historical data, reference data, derived data, transactions
- **Monitoring**: Independent PostgreSQL schema for system observability

### Key Import Patterns
```python
# Core components
from src.core import ConfigDrivenTableManager, DataClassification
from src.core.unified_manager import MyStocksUnifiedManager

# Data access
from src.data_access import TDengineDataAccess, PostgreSQLDataAccess

# Adapters
from src.adapters.akshare_adapter import AkshareDataSource
from src.interfaces import IDataSource

# Database management
from src.db_manager import DatabaseTableManager  # Compatibility layer
# OR
from src.storage.database import DatabaseTableManager  # Direct import

# GPU API system
from gpu_api_system.services import GPUBacktestService, GPURealtimeService

# Monitoring
from src.monitoring import MonitoringDatabase, AlertManager

# Web API
from web.backend.app.api import trading_signals_api, monitoring_api
```

### OpenSpec Workflow
- Always open `@/openspec/AGENTS.md` when the request mentions planning or proposals
- Use OpenSpec for introducing new capabilities, breaking changes, architecture shifts
- Follow the change proposal format in `openspec/changes/`
- Keep managed blocks for 'openspec update' to refresh instructions

### ValueCell Migration Features
- **Phase 1**: Real-time monitoring and alerting system (龙虎榜、资金流向、自定义规则)
- **Phase 2**: Enhanced technical analysis system (26个技术指标、交易信号生成)
- **Phase 3**: Multi-data source integration (优先级路由、自动故障转移、公告监控)

### GPU API System
- **GPU加速回测引擎**: cuDF/cuML实现15-44倍性能提升
- **实时数据处理**: 10,000条/秒实时处理能力
- **智能三级缓存**: L1应用层 + L2 GPU内存 + L3 Redis，命中率>90%
- **WSL2 GPU支持**: 完全解决WSL2环境下RAPIDS GPU访问问题

### Testing Infrastructure
- **AI优化测试**: `ai_test_optimizer_toolkit` 自动生成和优化测试用例
- **合同测试**: `tests/contract/` 验证API合约
- **E2E测试**: Playwright实现全栈端到端测试
- **性能测试**: `tests/performance/` 负载和性能验证

### Monitoring & Observability
- **独立监控数据库**: PostgreSQL独立schema记录所有操作
- **Prometheus + Grafana**: 实时监控和可视化
- **告警管理**: 多渠道告警（邮件、Webhook、日志）
- **数据质量监控**: 实时验证数据完整性和准确性

### CI/CD Workflows
- **code-quality.yml**: 代码质量检查 (Black, MyPy, Ruff, Bandit, Safety)
- **test-coverage.yml**: 测试覆盖率报告
- **security-testing.yml**: 安全漏洞扫描
- **comprehensive-testing.yml**: 全栈集成测试
- **e2e-testing.yml**: 端到端测试 (Playwright)
- **api-compliance-testing.yml**: API合规性验证
- **contract-testing.yml**: 合同测试
- **ai-test-optimization.yml**: AI优化测试生成

### Advanced Architecture Features

#### 智能数据路由 (Intelligent Data Routing)
- **自适应路由算法**: 根据数据类型、访问频率和系统负载自动选择最优存储引擎
- **实时性能监控**: 持续监控各数据库性能指标，动态调整路由策略
- **负载均衡**: 在多个数据源间智能分配查询压力，确保系统稳定性
- **故障自动转移**: 当主数据源故障时，自动切换到备用数据源，无缝保障服务连续性

#### API契约管理 (API Contract Management)
- **契约驱动开发**: 通过OpenAPI/Swagger规范定义和验证API接口
- **自动化契约测试**: 使用Pact/Spring Cloud Contract进行消费者驱动的契约测试
- **版本管理**: API版本控制和向后兼容性保证
- **契约验证**: 运行时API响应与契约规范的自动验证

#### TDD方法应用 (Test-Driven Development)
- **红绿重构循环**: 严格遵循测试先行、快速反馈、重构优化的TDD开发流程
- **测试覆盖率驱动**: 确保核心业务逻辑测试覆盖率达到95%以上
- **行为驱动测试**: 使用BDD框架(Gherkin/Cucumber)编写业务可读的测试用例
- **持续集成测试**: 每次代码提交自动运行完整测试套件，确保代码质量

#### DDD架构实施 (Domain-Driven Design)
- **领域建模**: 通过事件风暴和工作坊识别和定义核心业务领域
- **聚合设计**: 明确聚合根、实体、值对象和服务对象的职责边界
- **领域服务**: 封装复杂业务逻辑，确保领域层的纯净性
- **上下文映射**: 定义限界上下文间的集成关系和防腐层

#### 数据源集中管理 (Centralized Data Source Management)
- **统一配置管理**: 通过YAML配置文件集中管理所有34个数据源的连接参数
- **健康状态监控**: 实时监控数据源可用性、响应时间和错误率
- **动态配置更新**: 支持运行时动态调整数据源优先级和权重
- **故障恢复机制**: 自动检测并恢复故障数据源，确保数据获取的连续性

#### 智能量化监控与投资组合管理系统 (Smart Quantitative Monitoring & Portfolio Management)
- **实时风险监控**: 基于VaR、CVaR等指标的实时风险评估和预警
- **投资组合优化**: 使用现代投资组合理论(Markowitz模型)进行资产配置优化
- **绩效归因分析**: 深入分析投资组合收益来源和风险贡献
- **智能再平衡**: 根据市场条件和风险偏好自动调整投资组合权重

#### 信号监控管理系统 (Signal Monitoring Management System)
- **多维度信号聚合**: 整合技术指标、基本面和量化信号的统一监控平台
- **信号质量评估**: 通过回测和实盘表现评估信号的有效性和稳定性
- **实时信号分发**: WebSocket推送和消息队列确保信号的低延迟传递
- **信号回溯分析**: 完整的信号生成、执行和结果的审计追踪