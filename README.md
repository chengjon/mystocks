# CLI-4: Phase 6 文档和标准化

**分支**: `phase6-documentation`  
**工作目录**: `/opt/claude/mystocks_phase6_docs`  
**预计时间**: 6-8 小时  
**优先级**: 🟢 低（知识沉淀，可并行进行）  
**分配给**: GEMINI 或 OPENCODE  

**特殊说明**: 此任务可以与其他任务并行进行，因为文档工作不阻塞系统运行。

---

## 🎯 任务目标

完善项目文档体系，为发布做准备：

1. ✅ 完善 API 文档（OpenAPI/Swagger）
2. ✅ 编写部署指南（Docker/K8s）
3. ✅ 创建故障排查手册
4. ✅ 更新架构文档
5. ✅ 编写用户使用指南
6. ✅ 准备发布说明（CHANGELOG）

---

## 📋 详细任务清单

### 任务 4.1: 完善 API 文档 (2小时)

**目标**: 确保 API 文档完整且准确

**步骤**:
```bash
# 1. 检查现有 API 文档
cd /opt/claude/mystocks_phase6_docs
ls -la docs/api/

# 2. 生成 OpenAPI/Swagger 文档
# FastAPI 自动生成 OpenAPI schema
cd web/backend
python3 << 'PY'
from fastapi.openapi.utils import get_openapi
from app.main import app

openapi_schema = get_openapi(
    title=app.title,
    version=app.version,
    routes=app.routes,
)

import json
with open('openapi.json', 'w') as f:
    json.dump(openapi_schema, f, indent=2)

print("✅ OpenAPI schema 生成完成")
print(f"端点数量: {len(openapi_schema['paths'])}")
PY

# 3. 验证 Swagger UI 可访问
# 启动后端:
ADMIN_PASSWORD=password python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# 访问: http://localhost:8000/docs
# 应该看到 Swagger UI with 所有 API 端点

# 4. 检查 API 文档完整性
# 以下端点应该有完整文档:
# - Authentication (/auth/login)
# - Market Data (/api/v1/market/*)
# - Strategies (/api/v1/strategies/*)
# - Backtests (/api/v1/backtests/*)
# - Health (/health)
# - Metrics (/metrics)

# 5. 创建 API 文档索引
cat > docs/api/API_INDEX.md << 'EOF'
# MyStocks API 文档索引

## 在线文档
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI Schema: /openapi.json

## 核心端点
### 认证
- POST /api/v1/auth/login - 用户登录
- POST /api/v1/auth/logout - 用户登出
- GET /api/v1/auth/me - 获取当前用户信息

### 市场数据
- GET /api/v1/market/symbols - 获取股票列表
- GET /api/v1/market/kline - 获取K线数据
- GET /api/v1/market/realtime - 获取实时行情

### 策略管理
- GET /api/v1/strategies - 获取策略列表
- POST /api/v1/strategies - 创建策略
- GET /api/v1/strategies/{id} - 获取策略详情
- PUT /api/v1/strategies/{id} - 更新策略
- DELETE /api/v1/strategies/{id} - 删除策略

### 回测
- POST /api/v1/backtests - 创建回测
- GET /api/v1/backtests/{id} - 获取回测结果
- GET /api/v1/backtests/{id}/trades - 获取交易记录

### 系统监控
- GET /health - 健康检查
- GET /metrics - Prometheus 指标
- GET /api/v1/system/status - 系统状态

## 数据模型
详见: docs/api/DATA_MODELS.md

## 错误码
详见: docs/api/ERROR_CODES.md
