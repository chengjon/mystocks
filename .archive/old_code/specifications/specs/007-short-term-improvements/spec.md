# Feature 007: 短期优化改进

**创建人**: JohnC & Claude
**版本**: 1.0.0
**批准日期**: 2025-10-16
**最后修订**: 2025-10-16
**本次修订内容**: 创建短期优化规划

---

## 1. Feature概述

### 背景
MyStocks v2.1系统规范化改进已完成，但仍有改进空间：
- **API覆盖率**: 当前仅20% (2/10)，TDX核心功能已100%可用
- **监控仪表板**: Grafana配置文档存在但未实施
- **测试覆盖率**: 缺乏单元测试

### 目标
在1-2周内完成以下改进：
1. 提升API覆盖率至80% (8/10端点可用)
2. 配置Grafana监控仪表板
3. 添加单元测试达到80%覆盖率

### 范围

#### In Scope
- 实现8个缺失的API端点
- 配置Grafana + Prometheus监控
- 为核心模块添加pytest单元测试
- 更新API文档

#### Out of Scope
- 前端页面开发 (Phase 2)
- 性能优化 (中期规划)
- 新数据源添加 (长期规划)

---

## 2. 成功标准

### SC-001: API端点实现 (P1)
- ✅ 至少实现6个缺失端点 (75%)
- ✅ 所有端点返回正确的数据格式
- ✅ 错误处理完善
- ✅ API文档自动生成 (Swagger)

**验证**: `python utils/check_api_health.py` 显示 ≥ 80% 通过率

###SC-002: Grafana监控配置 (P1)
- ✅ Grafana仪表板可访问
- ✅ 至少3个核心面板配置完成：
  - 数据库连接状态
  - API请求统计
  - 系统资源监控
- ✅ 告警规则配置

**验证**: 访问 http://localhost:3001 可查看仪表板

### SC-003: 单元测试覆盖率 (P2)
- ✅ pytest配置完成
- ✅ 核心模块测试覆盖率≥70%：
  - adapters/ (数据源适配器)
  - db_manager/ (数据库管理)
  - utils/ (工具函数)
- ✅ CI/CD集成准备

**验证**: `pytest --cov=. --cov-report=html` 显示 ≥ 70%

---

## 3. 技术方案

### 3.1 API端点实现

#### 缺失端点分析

| 端点 | 文件 | 状态 | 实现难度 |
|------|------|------|---------|
| GET /api/market/quotes | market.py | ❌ 未实现 | 中 |
| GET /api/market/stocks | data.py | ✅ 已实现但未注册 | 低 |
| GET /api/data/kline | data.py | ✅ 已实现 (/stocks/daily) | 低 |
| GET /api/data/financial | data.py | ❌ 未实现 | 中 |
| POST /api/indicators/calculate | indicators.py | ❌ 部分实现 | 中 |
| GET /api/system/datasources | system.py | ❌ 未实现 | 低 |
| GET /api/system/health | system.py | ❌ 未实现 | 低 |

#### 实现计划

**Phase 1: 低难度端点** (2小时)
1. GET /api/system/health - 系统健康检查
2. GET /api/system/datasources - 数据源列表
3. GET /api/market/stocks - 股票列表 (重命名已有endpoint)
4. GET /api/data/kline - K线数据 (别名映射)

**Phase 2: 中难度端点** (4小时)
5. GET /api/market/quotes - 实时行情 (调用TDX adapter)
6. GET /api/data/financial - 财务数据 (调用akshare adapter)
7. POST /api/indicators/calculate - 技术指标计算
8. 修复 POST /api/auth/login 422错误

###3.2 Grafana监控配置

#### 架构
```
Prometheus (数据采集)
    ↓
Grafana (可视化)
    ↓
Alert Manager (告警)
```

#### 配置步骤

**Step 1: Prometheus Exporter** (2小时)
- 安装prometheus-client
- 创建/api/metrics端点
- 暴露核心指标：
  - HTTP请求计数/延迟
  - 数据库连接池状态
  - 缓存命中率

**Step 2: Grafana仪表板** (3小时)
- 使用现有配置: monitoring/grafana_setup.md
- 导入仪表板模板
- 配置3个核心面板：
  - 数据库健康监控
  - API性能监控
  - 系统资源监控

**Step 3: 告警规则** (1小时)
- 数据库连接失败告警
- API响应时间超标告警
- 系统资源告警

### 3.3 单元测试

#### 测试框架
- **pytest**: 测试执行
- **pytest-cov**: 覆盖率统计
- **pytest-mock**: Mock支持
- **pytest-asyncio**: 异步测试支持

#### 测试范围

**Priority 1: 核心适配器** (70%目标)
- adapters/akshare_adapter.py
- adapters/financial_adapter.py
- adapters/tdx_adapter.py

**Priority 2: 数据库管理** (70%目标)
- db_manager/database_manager.py

**Priority 3: 工具函数** (80%目标)
- utils/check_db_health.py
- utils/check_api_health.py
- utils/tdx_server_config.py

#### 测试用例设计

**示例: test_akshare_adapter.py**
```python
import pytest
from adapters.akshare_adapter import AkshareDataSource

class TestAkshareAdapter:
    def setup_method(self):
        self.adapter = AkshareDataSource()

    def test_get_stock_daily_success(self):
        """测试获取日线数据成功场景"""
        result = self.adapter.get_stock_daily("000001", "2024-01-01", "2024-01-31")
        assert result is not None
        assert len(result) > 0
        assert 'date' in result.columns

    def test_get_stock_daily_invalid_symbol(self):
        """测试无效股票代码"""
        with pytest.raises(ValueError):
            self.adapter.get_stock_daily("INVALID", "2024-01-01", "2024-01-31")

    @pytest.mark.asyncio
    async def test_get_realtime_data(self):
        """测试获取实时行情"""
        result = await self.adapter.get_real_time_data("000001")
        assert result is not None
```

---

## 4. 实施计划

### Timeline (2周)

**Week 1: API实现 + Grafana配置**

| 日期 | 任务 | 预计工时 |
|------|------|---------|
| Day 1-2 | 实现低难度API端点 (4个) | 4h |
| Day 3-4 | 实现中难度API端点 (4个) | 8h |
| Day 5 | Prometheus Exporter配置 | 3h |
| Day 6-7 | Grafana仪表板配置 | 6h |

**Week 2: 单元测试**

| 日期 | 任务 | 预计工时 |
|------|------|---------|
| Day 8-9 | 适配器单元测试 | 8h |
| Day 10 | 数据库管理单元测试 | 4h |
| Day 11 | 工具函数单元测试 | 3h |
| Day 12-13 | 测试完善 + CI配置 | 6h |
| Day 14 | 文档更新 + 验收测试 | 3h |

**总计**: ~45小时 (约2周)

---

## 5. 风险与依赖

### 风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| 数据源API限流 | 中 | 中 | 实现缓存机制 |
| 测试数据不足 | 低 | 中 | 使用Mock数据 |
| Grafana配置复杂 | 中 | 低 | 使用已有文档 |

### 依赖

**外部依赖**:
- akshare (数据源)
- pytdx (通达信)
- prometheus-client (监控)
- grafana (可视化)

**内部依赖**:
- 数据库已正常运行 (MySQL, PostgreSQL, TDengine, Redis)
- Backend服务已启动 (http://localhost:8000)

---

## 6. 验收标准

### 整体验收

| 标准 | 要求 | 验证方法 |
|------|------|---------|
| **API覆盖率** | ≥ 80% (8/10) | check_api_health.py |
| **API响应时间** | < 500ms (P95) | 性能测试 |
| **Grafana可用** | 3个面板正常 | 手动验证 |
| **测试覆盖率** | ≥ 70% | pytest --cov |
| **CI/CD准备** | pytest配置完成 | GitHub Actions |

### 交付物

1. **代码**:
   - 8个新增API端点实现
   - prometheus metrics endpoint
   - 30+ 单元测试用例

2. **配置**:
   - grafana/dashboards/*.json (仪表板配置)
   - prometheus.yml (Prometheus配置)
   - pytest.ini (测试配置)

3. **文档**:
   - API_IMPROVEMENTS.md (API改进报告)
   - MONITORING_SETUP.md (监控配置指南)
   - TESTING_GUIDE.md (测试指南)

---

## 7. 后续规划

### 中期 (1-2月)
- 前端页面开发
- 性能优化 (数据库查询优化)
- 安全加固 (依赖漏洞扫描)

### 长期 (3-6月)
- 新数据源添加 (Wind, Choice)
- 回测引擎实现
- 微服务改造

---

**文档版本**: 1.0
**最后更新**: 2025-10-16
**负责人**: JohnC & Claude
