# Swagger API 文档完善指南

> **使用说明**:
> 本文件是 API 相关的参考文档或专题说明，不是当前 API 契约、当前实施基线或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`；若涉及 API 契约事实源，再以实际的 FastAPI 路由 + Pydantic Schema + `/openapi.json` 为准。
>
> 文内端点、命令、统计值和示例如未重新复核，应视为参考或历史材料，不得直接当作当前事实。


**Historical Guide Snapshot Date**: 2025-11-30
**Historical Priority Snapshot**: 🟡 P1 - 高优先级
**Historical Guide Status Snapshot**: 📋 计划阶段
**Historical Effort Snapshot**: 8-12 小时

---

## 📊 当前状态分析

### 发现结果

**API 端点统计**:
- ✅ **发现总端点数**: 269 个
- ✅ **已有文档**: 259 个 (96.3%)
- ⚠️ **缺失文档**: 10 个 (3.7%)
- 📁 **分析文件数**: 42 个 Python 文件

**HTTP 方法分布**:
- **GET**: 170 个 (63.2%)
- **POST**: 76 个 (28.3%)
- **DELETE**: 13 个 (4.8%)
- **PUT**: 9 个 (3.3%)
- **WEBSOCKET**: 1 个 (0.4%)

**模块分布** (前 10 个):
- `routes.py`: 29 个端点
- `monitoring.py`: 17 个端点
- `data.py`: 15 个端点
- `watchlist.py`: 15 个端点
- `announcement.py`: 13 个端点
- `backup_recovery.py`: 13 个端点
- `market_v2.py`: 13 个端点
- `tasks.py`: 13 个端点
- `cache.py`: 12 个端点
- `strategy_management.py`: 12 个端点

---

## 🔍 缺失文档的端点详情

### 需要添加文档的 10 个端点

| 端点 | HTTP 方法 | 文件 | 函数 | 优先级 |
|------|---------|------|------|--------|
| `/cleanup/old-backups` | POST | backup_recovery.py | cleanup_old_backups | 🟡 中 |
| `/health` | GET | dashboard.py | health_check | 🔴 高 |
| `/health` | GET | market.py | health_check | 🔴 高 |
| `/control/status` | GET | monitoring.py | get_monitoring_status | 🟡 中 |
| `/notifications/test` | POST | risk_management.py | test_notification | 🟢 低 |
| `/backtest/results/{backtest_id}/chart-data` | GET | strategy_management.py | get_backtest_chart_data | 🟡 中 |
| `/health` | GET | tasks.py | tasks_health | 🔴 高 |
| `/analyze` | POST | routes.py (technical) | analyze_data | 🟡 中 |
| `/analyze` | POST | routes.py (monitoring) | analyze_data | 🟡 中 |
| `/analyze` | POST | routes.py (multi_source) | analyze_data | 🟡 中 |

---

## 📝 文档添加步骤

### 第 1 步: 为端点函数添加文档字符串

**格式**: 使用 Google 风格的 docstring

```python
@router.get("/health")
async def health_check(current_user: User = Depends(get_current_active_user)):
    """
    获取系统健康状态检查结果

    返回系统各个组件的健康状态信息，包括数据库连接、API 可用性等。
    仅管理员用户可以访问。

    Args:
        current_user: 当前认证用户（自动注入）

    Returns:
        Dict: 包含以下信息的健康状态对象
            - status: 整体状态 (healthy/degraded/unhealthy)
            - timestamp: 检查时间戳
            - components: 各组件状态信息
            - message: 状态描述信息

    Raises:
        HTTPException: 401 - 未认证用户
                      403 - 权限不足（需要管理员角色）

    Examples:
        >>> response = await health_check(current_user)
        >>> response['status']
        'healthy'
    """
    # 实现代码
    ...
```

### 第 2 步: 定义请求/响应 Pydantic 模型

```python
# 在文件顶部添加模型定义

from pydantic import BaseModel, Field
from typing import Dict, Optional, List
from datetime import datetime

class ComponentHealthStatus(BaseModel):
    """单个组件的健康状态"""
    name: str = Field(..., description="组件名称")
    status: str = Field(..., description="状态: healthy/degraded/unhealthy")
    message: Optional[str] = Field(None, description="状态描述")
    last_check: datetime = Field(..., description="最后检查时间")


class SystemHealthResponse(BaseModel):
    """系统整体健康状态响应"""
    status: str = Field(..., description="整体状态: healthy/degraded/unhealthy")
    timestamp: datetime = Field(..., description="检查时间")
    components: List[ComponentHealthStatus] = Field(..., description="各组件状态")
    message: str = Field(..., description="整体状态描述")

    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2025-11-30T21:00:00Z",
                "components": [
                    {
                        "name": "database",
                        "status": "healthy",
                        "message": "PostgreSQL connected",
                        "last_check": "2025-11-30T21:00:00Z"
                    }
                ],
                "message": "All systems operational"
            }
        }
```

### 第 3 步: 更新装饰器使用响应模型

```python
@router.get("/health", response_model=SystemHealthResponse)
async def health_check(current_user: User = Depends(get_current_active_user)):
    """获取系统健康状态检查结果 - 详见文档字符串"""
    # 实现代码
    ...
```

### 第 4 步: 在 FastAPI 应用中注册 Swagger 标签

```python
# 在 main.py 中添加标签定义
from fastapi import FastAPI

tags_metadata = [
    {
        "name": "health",
        "description": "系统健康检查和监控端点",
        "externalDocs": {
            "description": "健康检查规范",
            "url": "https://docs.example.com/health-checks",
        },
    },
    # ... 其他标签
]

app = FastAPI(
    title="MyStocks API",
    description="量化交易数据管理系统 API",
    version="1.0.0",
    openapi_tags=tags_metadata,
)
```

---

## 🎯 改进优先级和时间表

### Phase 1: 高优先级端点 (1-2 小时)

**需要立即文档化的健康检查端点**:

1. **`GET /health` (dashboard.py)** - 仪表板健康检查
   - 估计时间: 20 分钟
   - 影响范围: 前端监控

2. **`GET /health` (market.py)** - 市场数据健康检查
   - 估计时间: 20 分钟
   - 影响范围: 数据服务

3. **`GET /health` (tasks.py)** - 后台任务健康检查
   - 估计时间: 20 分钟
   - 影响范围: 任务调度系统

### Phase 2: 中优先级端点 (3-4 小时)

4. **`GET /control/status` (monitoring.py)** - 监控控制状态
   - 估计时间: 30 分钟
   - 影响范围: 监控系统

5. **`GET /backtest/results/{backtest_id}/chart-data` (strategy_management.py)** - 回测图表数据
   - 估计时间: 45 分钟
   - 影响范围: 策略管理

6. **`POST /cleanup/old-backups` (backup_recovery.py)** - 清理旧备份
   - 估计时间: 30 分钟
   - 影响范围: 备份恢复系统

7. **`POST /analyze` (routes.py - 技术分析)** - 技术分析接口
   - 估计时间: 30 分钟
   - 影响范围: 技术指标系统

8. **`POST /analyze` (routes.py - 监控)** - 监控分析接口
   - 估计时间: 30 分钟
   - 影响范围: 监控分析

9. **`POST /analyze` (routes.py - 多源)** - 多源数据分析
   - 估计时间: 30 分钟
   - 影响范围: 多源数据整合

### Phase 3: 低优先级端点 (1 小时)

10. **`POST /notifications/test` (risk_management.py)** - 测试通知
    - 估计时间: 20 分钟
    - 影响范围: 风险管理通知

---

## 📋 完整的文档模板

### 完整示例: 健康检查端点

```python
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

# ============ 数据模型定义 ============

class HealthComponentStatus(BaseModel):
    """单个系统组件的健康状态"""
    name: str = Field(..., description="组件名称（如：database, redis, api）")
    status: str = Field(
        ...,
        description="组件状态",
        enum=["healthy", "degraded", "unhealthy"]
    )
    response_time_ms: Optional[float] = Field(None, description="响应时间（毫秒）")
    last_error: Optional[str] = Field(None, description="最后一次错误信息")
    last_check_time: datetime = Field(..., description="最后检查时间")


class SystemHealthCheckResponse(BaseModel):
    """系统整体健康状态响应"""
    overall_status: str = Field(
        ...,
        description="整体系统状态",
        enum=["healthy", "degraded", "unhealthy"]
    )
    timestamp: datetime = Field(..., description="检查时间戳")
    uptime_seconds: int = Field(..., description="系统运行时间（秒）")
    components: List[HealthComponentStatus] = Field(..., description="各组件状态列表")
    version: str = Field(..., description="API 版本")
    environment: str = Field(..., description="运行环境（dev/staging/prod）")

    class Config:
        schema_extra = {
            "example": {
                "overall_status": "healthy",
                "timestamp": "2025-11-30T21:05:30Z",
                "uptime_seconds": 86400,
                "components": [
                    {
                        "name": "database",
                        "status": "healthy",
                        "response_time_ms": 5.2,
                        "last_error": None,
                        "last_check_time": "2025-11-30T21:05:30Z"
                    },
                    {
                        "name": "cache",
                        "status": "healthy",
                        "response_time_ms": 1.1,
                        "last_error": None,
                        "last_check_time": "2025-11-30T21:05:30Z"
                    }
                ],
                "version": "1.0.0",
                "environment": "production"
            }
        }


# ============ API 端点定义 ============

@router.get(
    "/health",
    response_model=SystemHealthCheckResponse,
    summary="系统健康检查",
    tags=["health"],
    responses={
        200: {"description": "系统健康状态信息"},
        401: {"description": "未认证"},
        500: {"description": "服务器内部错误"},
    }
)
async def health_check(
    include_detailed_metrics: bool = Field(
        False,
        description="是否包含详细的性能指标（仅管理员可用）"
    ),
    current_user: User = Depends(get_current_active_user)
) -> SystemHealthCheckResponse:
    """
    获取 MyStocks API 系统的整体健康状态

    此端点用于监控系统健康状况，包括所有关键组件的状态检查。

    **功能说明**:
    - 检查数据库连接状态
    - 验证缓存系统可用性
    - 评估外部 API 响应时间
    - 监控系统资源使用情况

    **使用场景**:
    - 前端定期轮询以显示系统状态
    - 监控和告警系统集成
    - 负载均衡器的健康检查
    - DevOps 仪表板集成

    **权限要求**:
    - 任何认证用户都可以访问基本健康状态
    - `include_detailed_metrics=True` 需要管理员权限

    Args:
        include_detailed_metrics: 是否包含详细的性能指标
                                 （默认 False，需要管理员权限）
        current_user: 当前认证用户（自动注入）

    Returns:
        SystemHealthCheckResponse: 包含系统整体状态、各组件状态和性能指标

    Raises:
        HTTPException:
            - status_code=401: 用户未认证
            - status_code=403: 用户没有权限查看详细指标
            - status_code=500: 内部服务器错误

    Examples:
        获取基本健康状态:
        ```bash
        curl -H "Authorization: Bearer TOKEN" \\
             http://localhost:8020/health
        ```

        获取包含详细指标的健康状态（需要管理员权限）:
        ```bash
        curl -H "Authorization: Bearer ADMIN_TOKEN" \\
             http://localhost:8020/health?include_detailed_metrics=true
        ```

    Notes:
        - 响应时间通常在 100-500ms 之间
        - "degraded" 状态表示某个组件可能有轻微问题但系统可继续运行
        - "unhealthy" 状态表示至少一个关键组件不可用
        - 对于监控系统，建议每 30 秒调用一次
    """
    # 实现代码
    ...
```

---

## 🔧 自动化文档生成工具

### Swagger 文档更新脚本

为了简化文档维护，我们可以使用自动化工具生成部分文档：

```python
# scripts/generate_swagger_docs.py

import json
import re
from pathlib import Path

class SwaggerDocGenerator:
    """自动生成 Swagger 文档"""

    @staticmethod
    def extract_endpoints_from_file(file_path: str) -> list:
        """从 Python 文件提取端点"""
        with open(file_path, 'r') as f:
            content = f.read()

        # 使用正则表达式查找所有 @router 装饰器
        pattern = r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\'].*?\).*?async def (\w+)'
        matches = re.finditer(pattern, content, re.DOTALL)

        endpoints = []
        for match in matches:
            endpoints.append({
                'method': match.group(1).upper(),
                'path': match.group(2),
                'function': match.group(3),
            })

        return endpoints

    @staticmethod
    def generate_openapi_json(endpoints: list) -> dict:
        """生成 OpenAPI JSON"""
        openapi = {
            "openapi": "3.0.0",
            "info": {
                "title": "MyStocks API",
                "version": "1.0.0",
            },
            "paths": {}
        }

        for ep in endpoints:
            path = ep['path']
            method = ep['method'].lower()

            if path not in openapi['paths']:
                openapi['paths'][path] = {}

            openapi['paths'][path][method] = {
                "operationId": ep['function'],
                "summary": f"{method.upper()} {path}",
                "tags": [ep['function'].split('_')[0]],
            }

        return openapi
```

---

## 📊 预期改进效果

完成所有文档添加后，预期实现以下改进：

| 指标 | 当前状态 | 目标状态 | 改进幅度 |
|------|---------|---------|----------|
| **文档覆盖率** | 96.3% | 100% | +3.7% |
| **有效端点** | 269 | 269 | 无变化 |
| **Swagger 展示** | 缺失 10 个 | 所有 269 个 | +100% |
| **API 可用性文档** | 259/269 | 269/269 | 完整 |
| **开发者效率** | 低 | 高 | 显著提升 |

---

## ✅ 完成清单

### 前期准备
- [ ] 分析所有缺失文档的端点
- [ ] 确定每个端点的优先级
- [ ] 准备文档模板和示例

### 文档编写 (Phase 1 - 高优先级)
- [ ] 为 `dashboard.py` 的 `/health` 添加文档
- [ ] 为 `market.py` 的 `/health` 添加文档
- [ ] 为 `tasks.py` 的 `/health` 添加文档

### 文档编写 (Phase 2 - 中优先级)
- [ ] 为 `monitoring.py` 的 `/control/status` 添加文档
- [ ] 为 `strategy_management.py` 的 `/backtest/results/{id}/chart-data` 添加文档
- [ ] 为 `backup_recovery.py` 的 `/cleanup/old-backups` 添加文档
- [ ] 为三个 `analyze` 端点添加文档

### 文档编写 (Phase 3 - 低优先级)
- [ ] 为 `risk_management.py` 的 `/notifications/test` 添加文档

### 验证和部署
- [ ] 运行后端并验证 Swagger UI 显示所有 269 个端点
- [ ] 检查每个端点的 OpenAPI 规范是否正确
- [ ] 生成最新的 `swagger.json` 和 `openapi.json`
- [ ] 更新 API 文档站点

### 后续维护
- [ ] 建立文档维护流程
- [ ] 创建 CI/CD 自动化文档生成
- [ ] 定期审查和更新文档

---

## 📚 参考资源

- **Swagger/OpenAPI 官方文档**: https://swagger.io/docs/
- **FastAPI Swagger 集成**: https://fastapi.tiangolo.com/how-to/extending-openapi/
- **Pydantic 文档**: https://docs.pydantic.dev/
- **RESTful API 设计最佳实践**: https://restfulapi.net/

---

## 🎓 相关文档

- **当前状态**: `/docs/api/SWAGGER_DOCUMENTATION_STATUS_2025-11-30.md`
- **端点列表**: `/docs/api/SWAGGER_ENDPOINTS_2025-11-30.json`
- **之前的安全修复**: `/docs/api/API_SECURITY_FIXES_SUMMARY_2025-11-30.md`
- **API 架构总结**: `/docs/api/API_ARCHITECTURE_COMPREHENSIVE_SUMMARY_2025-11-30.md`

---

**Historical Last Updated Snapshot**: 2025-11-30
**Historical Maintainer Snapshot**: AI Assistant
**Historical Document Version Snapshot**: 1.0
