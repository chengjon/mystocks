# API 规范标准化综合方案

**版本**: v1.0
**日期**: 2026-01-01
**状态**: 📋 待执行

---

## 📊 项目现状分析

### ✅ 已有的 API 契约系统

你的项目已经实现了一个**企业级 API 契约管理系统**，包括：

#### 1. 契约版本管理 (`web/backend/app/api/contract/`)

**核心组件**:
```
contract/
├── models.py                 # 数据库模型
│   ├── ContractVersion      # 契约版本表
│   ├── ContractDiff         # 差异记录表
│   └── ContractValidation   # 验证记录表
├── routes.py                # API 路由 (8个端点)
├── schemas.py               # Pydantic 模型 (9个Schema)
└── services/
    ├── version_manager.py   # 版本管理
    ├── diff_engine.py       # 差异检测引擎
    ├── validator.py         # 契约验证器
    ├── contract_registry.py # 端点契约注册
    ├── openapi_generator.py # OpenAPI 生成器
    └── contract_testing.py  # 契约测试工具
```

**API 端点**:
- `POST /api/contracts/versions` - 创建契约版本
- `GET /api/contracts/versions/{version_id}` - 获取版本
- `GET /api/contracts/versions/{name}/active` - 获取激活版本
- `POST /api/contracts/versions/{version_id}/activate` - 激活版本
- `POST /api/contracts/diff` - 版本对比
- `POST /api/contracts/validate` - 验证契约
- `POST /api/contracts/sync` - 同步契约 (code_to_db/db_to_code)
- `GET /api/contracts/sync/report` - 同步报告

#### 2. OpenAPI 配置系统 (`web/backend/app/openapi_config.py`)

**核心功能**:
- ✅ API 元数据定义 (title, description, version)
- ✅ 27 个功能模块标签分组
- ✅ 安全方案定义 (JWT + CSRF)
- ✅ 统一响应示例 (200/400/401/403/404/422/500)
- ✅ Swagger UI 参数配置

#### 3. 统一响应格式 (Phase 3)

**响应结构** (`web/backend/app/middleware/response_format.py`):
```typescript
interface UnifiedResponse<T> {
  code: string;           // 业务状态码
  message: string;        // 用户消息
  data: T;               // 业务数据
  request_id?: string;   // 请求追踪 ID
  timestamp?: number;    // 响应时间戳
}
```

#### 4. 前端 API 管理 (`web/frontend/src/api/index.js`)

**现有 API 组织**:
```javascript
export const authApi = { ... }      // 认证
export const dataApi = { ... }      // 数据
export const monitoringApi = { ... } // 监控
export const technicalApi = { ... } // 技术分析
export const strategyApi = { ... }  // 策略
export const marketApi = { ... }    // 市场
```

**特性**:
- ✅ Axios 请求拦截器 (自动添加 JWT)
- ✅ 响应拦截器 (统一错误处理)
- ✅ 缓存管理集成
- ✅ 开发环境 Mock 认证

---

## 🎯 API 规范标准化方案

### 方案目标

基于现有契约系统，实现：
1. **统一 API 端点版本化规范**
2. **完善 OpenAPI 文档自动生成**
3. **前后端类型完全同步**
4. **建立契约测试闭环**

---

## 📋 实施计划

### Phase 1: API 端点版本化统一 ⭐ **优先级 P0**

#### 1.1 建立版本化规范

**当前问题**:
```python
# ❌ 混乱的版本管理
/api/v1/auth/login          # v1版本化
/market/kline               # 未版本化
/api/strategy/definitions   # 版本不明确
```

**统一规范**:
```python
# ✅ 统一版本化
/api/v1/auth/login
/api/v1/market/kline
/api/v1/strategy/definitions
/api/v1/monitoring/alerts
```

**实施步骤**:

1. **创建版本映射表**
```python
# web/backend/app/api/VERSION_MAPPING.py
"""
API版本映射表
定义所有端点的标准路径和版本
"""

VERSION_MAPPING = {
    # 认证模块 (已有v1)
    "auth": {
        "prefix": "/api/v1/auth",
        "version": "1.0.0",
        "endpoints": {
            "login": "/login",
            "logout": "/logout",
            "me": "/me",
            "refresh": "/refresh",
        }
    },

    # 市场数据 (需要升级到v1)
    "market": {
        "prefix": "/api/v1/market",
        "version": "1.0.0",
        "endpoints": {
            "kline": "/kline",
            "quotes": "/quotes",
            "fund_flow": "/fund-flow",
            "fund_flow_refresh": "/fund-flow/refresh",
        }
    },

    # 策略管理 (需要升级到v1)
    "strategy": {
        "prefix": "/api/v1/strategy",
        "version": "1.0.0",
        "endpoints": {
            "definitions": "/definitions",
            "run_single": "/run/single",
            "run_batch": "/run/batch",
            "results": "/results",
        }
    },

    # 监控模块 (需要升级到v1)
    "monitoring": {
        "prefix": "/api/v1/monitoring",
        "version": "1.0.0",
        "endpoints": {
            "alert_rules": "/alert-rules",
            "alerts": "/alerts",
            "realtime": "/realtime",
        }
    },
}
```

2. **批量更新路由注册**

**修改** `web/backend/app/main.py`:
```python
# 当前 (混合版本化)
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(market.router, tags=["market"])  # ❌ 未版本化
app.include_router(strategy.router, tags=["strategy"])  # ❌ 未版本化

# 统一版本化后
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(market.router, prefix="/api/v1/market", tags=["market-v1"])
app.include_router(strategy.router, prefix="/api/v1/strategy", tags=["strategy-v1"])
app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["monitoring-v1"])
```

3. **前端 API 调用同步更新**

**修改** `web/frontend/src/api/index.js`:
```javascript
// ❌ 当前 (混合路径)
export const marketApi = {
  async getKline(params) {
    return request.get('/market/kline', { params })  // 未版本化
  }
}

// ✅ 统一版本化
export const marketApi = {
  async getKline(params) {
    return request.get('/v1/market/kline', { params })  // v1版本化
  }
}
```

#### 1.2 版本兼容性策略

**过渡期兼容** (保留旧路径 3 个月):
```python
# 旧路径重定向到新路径
@app.get("/market/kline")
async def legacy_kline_redirect(request: Request):
    """临时重定向 (deprecated)"""
    return Redirect(url="/api/v1/market/kline", status_code=301)
```

---

### Phase 2: OpenAPI 文档完善 ⭐ **优先级 P1**

#### 2.1 增强 OpenAPI 元数据

**当前状态**: ✅ 已有基础配置

**改进方向**:
```python
# web/backend/app/openapi_config.py

API_METADATA = {
    "title": "MyStocks Web API",
    "description": "...",
    "version": "2.0.0",

    # 新增: 联系方式
    "contact": {
        "name": "MyStocks API Support",
        "email": "api@mystocks.com",
        "url": "https://mystocks.com/support"
    },

    # 新增: 许可证
    "license_info": {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },

    # 新增: 服务器列表
    "servers": [
        {"url": "http://localhost:8020", "description": "本地开发环境"},
        {"url": "http://127.0.0.1:8020", "description": "本地开发环境 (127.0.0.1)"},
        {"url": "https://api.mystocks.com", "description": "生产环境"},
    ]
}
```

#### 2.2 自动生成 API 目录

**目标**: 创建完整的 API 端点清单

**实施**:
```bash
# 使用已有的脚本
python scripts/generate_openapi.py

# 输出:
# - docs/api/openapi.json
# - docs/api/endpoints_catalog.md (端点清单)
```

**生成的端点清单格式**:
```markdown
# API 端点目录

## 认证模块 (/api/v1/auth)

| 端点 | 方法 | 描述 | 认证 |
|------|------|------|------|
| /login | POST | 用户登录 | ❌ |
| /logout | POST | 用户登出 | ✅ |
| /me | GET | 获取当前用户 | ✅ |

## 市场数据模块 (/api/v1/market)

| 端点 | 方法 | 描述 | 认证 |
|------|------|------|------|
| /kline | GET | K线数据 | ❌ |
| /quotes | GET | 实时行情 | ❌ |
```

---

### Phase 3: 前后端类型同步 ⭐ **优先级 P1**

#### 3.1 修复 TypeScript 生成脚本

**当前问题**: `scripts/generate_frontend_types.py:402` bug
```python
# 错误: AttributeError: 'TypeScriptGenerator' object has no attribute 'interfaces'
```

**修复方案**:
```python
# scripts/generate_frontend_types.py

class TypeScriptGenerator:
    def __init__(self):
        self.interfaces = []  # ✅ 添加此行
        self.types = []
        # ...
```

#### 3.2 完善类型生成逻辑

**增强功能**:
```python
# scripts/generate_frontend_types.py

def generate_from_pydantic(model_class: Type[BaseModel]) -> str:
    """从 Pydantic 模型生成 TypeScript 类型"""

    # 处理基础类型
    type_mapping = {
        str: "string",
        int: "number",
        float: "number",
        bool: "boolean",
        datetime: "string",  # ISO 8601
        list: "Array<T>",
        dict: "Record<string, any>",
    }

    # 生成 TypeScript 接口
    fields = []
    for field_name, field_info in model_class.model_fields.items():
        ts_type = map_pydantic_to_ts(field_info.annotation)
        fields.append(f"  {field_name}: {ts_type}")

    return f"export interface {model_class.__name__} {{\n" + "\n".join(fields) + "\n}"
```

**生成的类型文件**:
```typescript
// web/frontend/src/api/types/generated-types.ts

// 统一响应格式
export interface UnifiedResponse<T> {
  code: string;
  message: string;
  data: T;
  request_id?: string;
  timestamp?: number;
}

// 市场数据类型
export interface KlineRequest {
  symbol: string;
  period: 'daily' | 'weekly' | 'monthly';
  adjust: 'qfq' | 'hfq' | 'none';
  start_date?: string;
  end_date?: string;
}

export interface KlineData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  amount: number;
}

export type KlineResponse = UnifiedResponse<KlineData[]>;
```

#### 3.3 前端 API 使用类型

```typescript
// web/frontend/src/api/market.ts

import type { KlineRequest, KlineResponse } from '@/api/types/generated-types'

export const marketApi = {
  async getKline(params: KlineRequest): Promise<KlineResponse> {
    return request.get('/v1/market/kline', { params })
  }
}
```

---

### Phase 4: 契约测试闭环 ⭐ **优先级 P2**

#### 4.1 自动化契约测试

**使用现有的** `ContractTestMixin`:
```python
from app.api.contract.services.contract_testing import ContractTestMixin

class TestMarketAPI(ContractTestMixin):
    """市场数据 API 契约测试"""

    def test_kline_response_conforms_to_schema(self, api_client, contract_validator):
        """测试 K线接口响应符合契约"""
        response = api_client.get("/api/v1/market/kline?symbol=000001&period=daily")

        # 验证响应
        self.validate_response_against_contract(
            response=response,
            path="/api/v1/market/kline",
            method="GET",
            status_code=200,
            contract_validator=contract_validator
        )
```

#### 4.2 CI/CD 集成

**添加到** `.github/workflows/api-contract-test.yml`:
```yaml
name: API Contract Tests

on: [pull_request, push]

jobs:
  contract-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run contract tests
        run: |
          pytest tests/api/test_api_contracts.py -v

      - name: Generate contract report
        if: failure()
        run: |
          python scripts/generate_contract_report.py
```

---

## 🔧 实施步骤总结

### 立即行动 (本周)

1. ✅ **修复 TypeScript 生成脚本**
   - 文件: `scripts/generate_frontend_types.py`
   - 预计时间: 2小时
   - 影响: 解除前端启动阻塞

2. ✅ **创建版本映射表**
   - 文件: `web/backend/app/api/VERSION_MAPPING.py`
   - 预计时间: 1小时
   - 影响: 为版本化提供规范

3. ✅ **更新前端 API 路径**
   - 文件: `web/frontend/src/api/index.js`
   - 预计时间: 3小时
   - 影响: 统一API调用路径

### 短期行动 (本月)

4. 🔄 **批量更新路由注册**
   - 文件: `web/backend/app/main.py`
   - 预计时间: 4小时
   - 影响: 统一后端API版本

5. 🔄 **完善 OpenAPI 文档**
   - 文件: `web/backend/app/openapi_config.py`
   - 预计时间: 2小时
   - 影响: 改善API文档质量

6. 🔄 **生成完整API目录**
   - 命令: `python scripts/generate_openapi.py`
   - 预计时间: 1小时
   - 影响: 提供API完整清单

### 中期行动 (下月)

7. ⏳ **建立契约测试**
   - 文件: `tests/api/test_api_contracts.py`
   - 预计时间: 8小时
   - 影响: 确保前后端一致性

8. ⏳ **CI/CD 集成**
   - 文件: `.github/workflows/api-contract-test.yml`
   - 预计时间: 4小时
   - 影响: 自动化契约验证

---

## 📚 参考文档

### 项目现有文档

- ✅ `docs/api/guides/integration/API对齐核心流程.md` - API对接核心流程
- ✅ `web/backend/app/openapi_config.py` - OpenAPI配置
- ✅ `web/backend/app/api/contract/` - 契约管理系统

### 外部最佳实践

- [OpenAPI Specification 3.1.0](https://spec.openapis.org/oas/v3.1.0)
- [FastAPI API 文档最佳实践](https://fastapi.tiangolo.com/tutorial/tutorial-metadata/)
- [TypeScript 类型生成工具](https://github.com/vega/ts-json-schema-generator)

---

## ✅ 验收标准

### Phase 1 完成标准
- [ ] 所有 API 端点遵循 `/api/v1/{module}/{action}` 格式
- [ ] 前端 API 调用全部使用版本化路径
- [ ] 旧路径重定向正常工作
- [ ] API 目录文档完整准确

### Phase 2 完成标准
- [ ] OpenAPI 文档可通过 `/api/docs` 访问
- [ ] 每个端点都有完整的描述和示例
- [ ] 自动生成的端点清单与实际一致

### Phase 3 完成标准
- [ ] TypeScript 类型生成脚本无错误
- [ ] 生成的类型文件覆盖所有 API
- [ ] 前端 API 调用全部有类型注解
- [ ] TypeScript strict 模式无错误

### Phase 4 完成标准
- [ ] 契约测试覆盖所有关键 API
- [ ] CI/CD 自动运行契约测试
- [ ] 契约破坏性变更自动检测

---

## 🎯 预期成果

### 开发体验提升
- ✅ **类型安全**: 前端调用 API 时有完整类型提示
- ✅ **文档完善**: Swagger UI 提供准确的 API 文档
- ✅ **版本清晰**: 统一的版本管理，避免混淆

### 维护效率提升
- ✅ **自动生成**: OpenAPI 文档和 TypeScript 类型自动生成
- ✅ **契约测试**: 自动检测前后端不一致
- ✅ **版本管理**: 清晰的 API 版本演进路径

### 团队协作改善
- ✅ **规范统一**: 前后端遵循统一的 API 规范
- ✅ **文档同步**: API 变更自动同步到文档
- ✅ **质量保证**: 契约测试确保 API 质量

---

**文档完成时间**: 2026-01-01
**下一步**: 开始 Phase 1 - API 端点版本化统一
