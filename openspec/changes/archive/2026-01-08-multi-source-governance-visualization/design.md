## Context

### Background
MyStocks 系统当前使用 7 个数据源适配器，但存在以下问题：
1. 数据源配置硬编码在适配器中，缺乏统一配置管理
2. 故障转移逻辑内嵌在业务代码中，难以维护和扩展
3. 无法实时了解各数据源的可用性和性能状态
4. 数据质量依赖人工检查，缺乏自动化监控
5. 数据流向不清晰，排查问题困难

### Constraints
- 复用现有 Grafana + Prometheus 监控体系
- 兼容现有 7 个数据源适配器（akshare, tushare 等）
- 不引入新的基础设施组件（除非必要）
- API 设计遵循现有规范（统一响应格式）

### Stakeholders
- 量化交易团队：需要可靠的数据源和实时数据质量反馈
- 运维团队：需要可视化监控数据源状态和快速定位问题
- 数据团队：需要了解数据血缘和质量指标

## Goals / Non-Goals

### Goals
1. 提供统一的数据源注册、配置、健康监控能力
2. 实现数据质量自动化检测和可视化
3. 追踪数据从采集到存储的完整血缘
4. 通过 Grafana 面板实现数据管理和治理的可视化

### Non-Goals
1. 不改造现有数据源适配器内部逻辑（兼容模式）
2. 不引入新的消息队列或流处理系统
3. 不实现完整的数据目录和发现功能（仅资产注册）
4. 不强制要求链路追踪（可选，血缘基于日志记录）

## Decisions

### Architecture Decision: Data Source Registry Pattern

**Decision**: 采用注册中心模式管理数据源，而非硬编码配置

```python
# src/core/datasource/registry.py
class DataSourceRegistry:
    """数据源注册中心 - 单一数据源"""
    def __init__(self, config: RedisConfig):
        self._config = config
        self._sources: Dict[str, DataSourceConfig] = {}
        self._health_status: Dict[str, HealthStatus] = {}

    def register(self, source_id: str, config: DataSourceConfig) -> None:
        """注册数据源"""
        self._sources[source_id] = config
        self._health_status[source_id] = HealthStatus.UNKNOWN

    def unregister(self, source_id: str) -> None:
        """注销数据源"""
        self._sources.pop(source_id, None)
        self._health_status.pop(source_id, None)

    def get_config(self, source_id: str) -> Optional[DataSourceConfig]:
        """获取数据源配置"""
        return self._sources.get(source_id)

    def list_sources(self) -> List[DataSourceInfo]:
        """列出所有数据源"""
        return [
            DataSourceInfo(id=id, config=config, health=self._health_status.get(id))
            for id, config in self._sources.items()
        ]
```

**Rationale**:
- 集中管理便于动态调整和监控
- 支持运行时注册/注销数据源
- 与现有适配器兼容（适配器从注册中心获取配置）

**Alternatives considered**:
- 配置中心（Apollo/Nacos）：引入新组件，增加运维复杂度
- 数据库存储：配置变更需要重启服务

### Architecture Decision: Health Check Model

**Decision**: 采用主动探测 + 被动监控双重健康检查机制

```python
# src/core/datasource/health.py
class DataSourceHealthMonitor:
    """数据源健康监控器"""

    async def check_health(self, source_id: str) -> HealthReport:
        """主动探测健康状态"""
        config = self.registry.get_config(source_id)
        if not config:
            return HealthReport(status=HealthStatus.UNKNOWN)

        start_time = time.time()
        try:
            # 调用数据源的 health_check 方法
            result = await self._probe_source(config)
            latency = time.time() - start_time

            return HealthReport(
                status=HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY,
                latency_ms=latency * 1000,
                last_check=datetime.utcnow(),
                details=result
            )
        except Exception as e:
            return HealthReport(
                status=HealthStatus.ERROR,
                latency_ms=(time.time() - start_time) * 1000,
                error=str(e),
                last_check=datetime.utcnow()
            )

    async def record_metrics(self, source_id: str, success: bool, latency: float):
        """被动记录调用指标"""
        # 更新 Prometheus 指标
        datasource_requests_total.labels(source_id=source_id, success=success).inc()
        datasource_latency_seconds.labels(source_id=source_id).observe(latency)
```

**Rationale**:
- 主动探测：定期检查数据源可用性
- 被动监控：基于实际调用记录成功率/延迟
- 暴露 Prometheus 指标，无缝集成现有监控

**Alternatives considered**:
- 仅被动监控：无法发现潜在故障
- 仅主动探测：无法反映真实业务调用情况

### Architecture Decision: Data Quality Metrics

**Decision**: 实现四维度数据质量指标

```python
# src/data_governance/quality.py
from enum import Enum
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

class QualityDimension(Enum):
    COMPLETENESS = "completeness"  # 完整性
    ACCURACY = "accuracy"          # 准确性
    TIMELINESS = "timeliness"      # 及时性
    CONSISTENCY = "consistency"    # 一致性

@dataclass
class QualityScore:
    dimension: QualityDimension
    score: float  # 0-100
    details: Dict[str, Any]
    measured_at: datetime

class DataQualityChecker:
    """数据质量检查器"""

    async def check_completeness(self, dataset_id: str) -> QualityScore:
        """检查完整性"""
        # 检查必要字段是否缺失
        # 检查记录数是否异常波动
        pass

    async def check_timeliness(self, dataset_id: str) -> QualityScore:
        """检查及时性"""
        # 检查数据更新时间
        # 检查更新频率是否符合预期
        pass

    async def get_overall_score(self, dataset_id: str) -> float:
        """计算综合质量分"""
        scores = await self.check_all_dimensions(dataset_id)
        weights = {"completeness": 0.3, "accuracy": 0.3, "timeliness": 0.2, "consistency": 0.2}
        return sum(s.score * weights[s.dimension.value] for s in scores)
```

**Rationale**:
- 四维度覆盖数据质量核心要素
- 权重可配置，适应不同数据源需求
- 分数可追溯，便于问题定位

**Alternatives considered**:
- 单一质量分：不够透明，难以定位问题
- 复杂质量模型：实施成本高，当前阶段不必要

### Architecture Decision: Data Lineage Tracking

**Decision**: 基于事件日志的轻量级血缘追踪

```python
# src/data_governance/lineage.py
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class LineageNode:
    node_id: str
    node_type: str  # "datasource", "dataset", "api", "storage"
    name: str
    metadata: Dict[str, Any]

@dataclass
class LineageEdge:
    from_node: str
    to_node: str
    operation: str  # "fetch", "transform", "store", "serve"
    timestamp: datetime = field(default_factory=datetime.utcnow)

class LineageTracker:
    """数据血缘追踪器"""

    def __init__(self, storage: LineageStorage):
        self._storage = storage
        self._current_chain: List[LineageNode] = []

    def start_trace(self, source_id: str):
        """开始追踪"""
        self._current_chain = [
            LineageNode(node_id=source_id, node_type="datasource", name=source_id)
        ]

    def record_operation(self, operation: str, target: str, target_type: str):
        """记录操作"""
        if not self._current_chain:
            return

        from_node = self._current_chain[-1].node_id
        new_node = LineageNode(node_id=target, node_type=target_type, name=target)
        edge = LineageEdge(from_node=from_node, to_node=target, operation=operation)

        self._current_chain.append(new_node)
        self._storage.save_edge(edge)
        self._storage.save_node(new_node)

    def end_trace(self):
        """结束追踪"""
        self._current_chain.clear()

    def get_lineage(self, node_id: str) -> Tuple[List[LineageNode], List[LineageEdge]]:
        """查询血缘"""
        return self._storage.get_lineage(node_id)
```

**Rationale**:
- 轻量级实现，无需引入专业链路追踪系统
- 基于现有存储（PostgreSQL）持久化
- 记录关键节点和操作，便于问题排查

**Alternatives considered**:
- OpenLineage：功能完整但引入新组件
- Jaeger：重量级，需要额外部署

### Visualization Decision: Grafana Dashboard Structure

**Decision**: 创建四个独立但关联的 Dashboard

1. **Data Source Overview** (`datasource-overview.json`)
   - 数据源状态总览（表格）
   - QPS 和延迟趋势图
   - 错误率告警面板

2. **Data Quality Monitor** (`data-quality.json`)
   - 数据集质量评分（仪表盘）
   - 各维度分数趋势图
   - 异常检测告警

3. **Data Lineage Explorer** (`data-lineage.json`)
   - 拓扑图（Graph 面板）
   - 节点详情（JSON 面板）
   - 时间范围筛选

4. **Data Asset Inventory** (`data-assets.json`)
   - 资产目录列表
   - 访问频次排名
   - 存储使用量

**Rationale**:
- 分离关注点，便于不同角色使用
- 独立 Dashboard 便于权限控制
- 复用现有 Prometheus 数据源

**Alternatives considered**:
- 单一 Dashboard：内容过多，难以维护
- 内嵌应用：开发成本高，不如直接用 Grafana

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|------------|
| 性能开销 | 健康检查增加系统负载 | 异步执行，频率可配置（默认 30s） |
| 存储增长 | 血缘记录随时间增长 | 保留 30 天，过期自动清理 |
| 兼容性 | 现有适配器需要改造 | 采用适配器模式，兼容旧接口 |
| 复杂度 | 新模块增加代码复杂度 | 保持模块独立，API 驱动设计 |

## Migration Plan

### Phase 1: Data Source Management (Week 1-2)
1. 创建 DataSourceRegistry 和配置文件
2. 迁移现有 7 个数据源配置到注册中心
3. 实现 HealthMonitor 和 Prometheus 指标暴露
4. 新增 Data Source Dashboard

### Phase 2: Data Governance Foundation (Week 3-4)
1. 实现 DataQualityChecker 基础框架
2. 实现 LineageTracker 事件记录
3. 创建治理 API 接口
4. 新增 Data Quality Dashboard

### Phase 3: Visualization Enhancement (Week 5-6)
1. 新增 Data Lineage Dashboard
2. 新增 Data Asset Dashboard
3. 配置告警规则
4. 文档和培训

### Rollback
- 通过配置开关禁用新功能
- 回退配置文件
- 保留旧代码路径（不删除）
