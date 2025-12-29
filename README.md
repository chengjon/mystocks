# CLI-2 任务分配文档 - API契约优化与标准化

**Worker CLI**: CLI-2 (Backend API Architect)
**Branch**: `cli2-api-contract`
**Worktree**: `/opt/claude/mystocks_phase6_api_contract/`
**Phase**: Round 1 (Day 1-14, 优先级: 最高)
**预计工作量**: 12-14天
**完成标准**: 100% API契约对齐, TypeScript类型自动生成, CI/CD校验集成

---

## 🎯 核心职责

完成 **API契约标准化**和**前后端对齐优化**，建立完整的API契约管理体系，包括：

1. ✅ **OpenAPI 3.0 Schema标准化** (所有API端点统一格式)
2. ✅ **Pydantic模型规范化** (请求/响应模型完整定义)
3. ✅ **统一错误码体系** (200成功、4xx客户端错误、5xx服务端错误)
4. ✅ **API契约管理平台** (api-contract-sync-manager)
5. ✅ **契约同步与校验工具** (api-contract-sync)
6. ✅ **TypeScript类型自动生成** (OpenAPI → TS types)
7. ✅ **CI/CD集成和自动化校验**

**架构原则**:
- ✅ **Schema First** - Pydantic模型是单一数据源(SSOT)
- ✅ **契约优先** - 先更新契约，再修改代码
- ✅ **自动化校验** - 代码/响应与契约自动对比
- ✅ **全流程管控** - 开发→提交→CI/CD→测试→监控

**参考文档**:
- `/opt/claude/mystocks_spec/docs/api/API契约同步组件实现方案.md`
- `/opt/claude/mystocks_spec/docs/api/API与Web组件最终对齐方案.md`

---

## 📋 任务清单 (17个任务)

### 阶段1: OpenAPI Schema标准化 (T2.1-T2.3, 3天)

#### T2.1: 定义统一响应格式和公共模型 (1天)

**目标**: 建立完整的OpenAPI 3.0标准契约模板

**实施步骤**:
1. 创建 `web/backend/app/schemas/common_schemas.py`:
   ```python
   from typing import Generic, TypeVar, Optional
   from pydantic import BaseModel, Field
   from datetime import datetime
   from uuid import uuid4

   T = TypeVar('T')

   class APIResponse(BaseModel, Generic[T]):
       """统一API响应格式"""
       success: bool = True
       code: int = 0
       message: str = "操作成功"
       data: Optional[T] = None
       request_id: str = Field(default_factory=lambda: str(uuid4()))
       timestamp: datetime = Field(default_factory=datetime.now)

   class CommonError(BaseModel):
       """统一错误响应模型"""
       code: int
       message: str
       data: Optional[dict] = None
       detail: Optional[str] = None
   ```

2. 创建OpenAPI 3.0契约模板 (`docs/api/openapi_template.yaml`):
   ```yaml
   openapi: 3.0.3
   info:
     title: MyStocks API Contract
     version: 1.0.0
     description: 量化交易系统API契约

   components:
     schemas:
       APIResponse:
         type: object
         required: [success, code, message, request_id, timestamp]
         properties:
           success:
             type: boolean
             description: 请求是否成功
           code:
             type: integer
             description: 业务错误码 (0=成功, 4xx=客户端错误, 5xx=服务端错误)
           message:
             type: string
             description: 提示信息
           data:
             type: object
             nullable: true
             description: 实际数据载荷
           request_id:
             type: string
             format: uuid
             description: 请求唯一标识
           timestamp:
             type: string
             format: date-time
             description: 响应时间戳

       CommonError:
         type: object
         required: [code, message]
         properties:
           code:
             type: integer
           message:
             type: string
           data:
             type: object
             nullable: true
           detail:
             type: string
             nullable: true
   ```

3. 定义核心业务模块分类:
   - Market (市场数据): `/api/market/**`
   - Technical (技术指标): `/api/indicators/**`
   - Trade (交易执行): `/api/trade/**`
   - Strategy (策略管理): `/api/strategy/**`
   - System (系统监控): `/api/system/**`

**验收标准**:
- [ ] 统一响应格式Pydantic模型定义完成
- [ ] OpenAPI 3.0模板创建完成
- [ ] 5个核心业务模块路由定义清晰

---

#### T2.2: 梳理现有API端点,补全契约定义 (1.5天)

**目标**: 完整梳理200+API端点,补全缺失的契约信息

**实施步骤**:
1. 扫描 `web/backend/app/api/` 目录下所有路由:
   ```bash
   # 统计所有API端点
   grep -r "@router\." web/backend/app/api/ | wc -l
   ```

2. 为每个API端点补全契约信息 (按业务模块):

   **Market API契约** (`docs/api/contracts/market_api.yaml`):
   ```yaml
   paths:
     /api/market/kline:
       get:
         summary: 获取K线数据
         operationId: getKlineData
         parameters:
           - name: symbol
             in: query
             required: true
             schema:
               type: string
               example: "000001.SZ"
           - name: interval
             in: query
             required: true
             schema:
               type: string
               enum: [1m, 5m, 15m, 1h, 1d, 1w, 1M]
           - name: start_date
             in: query
             required: false
             schema:
               type: string
               format: date
           - name: end_date
             in: query
             required: false
             schema:
               type: string
               format: date
           - name: adjust
             in: query
             required: false
             schema:
               type: string
               enum: [qfq, hfq, none]
               default: qfq
         responses:
           '200':
             description: 成功获取K线数据
             content:
               application/json:
                 schema:
                   allOf:
                     - $ref: '#/components/schemas/APIResponse'
                     - type: object
                       properties:
                         data:
                           type: object
                           properties:
                             klines:
                               type: array
                               items:
                                 $ref: '#/components/schemas/KLineCandle'
           '400':
             description: 参数错误
             content:
               application/json:
                 schema:
                   $ref: '#/components/schemas/CommonError'

   components:
     schemas:
       KLineCandle:
         type: object
         required: [timestamp, open, high, low, close, volume]
         properties:
           timestamp:
             type: integer
             description: Unix时间戳 (毫秒)
           open:
             type: number
             format: float
           high:
             type: number
             format: float
           low:
             type: number
             format: float
           close:
             type: number
             format: float
           volume:
             type: integer
             description: 成交量
   ```

3. 创建契约清单表格 (`docs/api/API_INVENTORY.md`):
   | API端点 | 业务模块 | 契约状态 | 缺失信息 | 责任人 |
   |---------|---------|---------|---------|--------|
   | `/api/market/kline` | Market | ✅ 完整 | - | Backend |
   | `/api/indicators/overlay` | Technical | ⚠️ 缺少错误码定义 | 4xx/5xx错误码 | Backend |
   | `/api/trade/order` | Trade | ❌ 未定义 | 完整契约 | Backend |

**验收标准**:
- [ ] 所有200+API端点已梳理
- [ ] 核心API (Market/Technical/Trade) 契约定义完成
- [ ] API清单表格创建完成,标记缺失信息

---

#### T2.3: 创建Pydantic Schema自动生成脚本 (0.5天)

**目标**: 自动从OpenAPI Schema生成Pydantic模型代码

**实施步骤**:
1. 安装依赖:
   ```bash
   pip install datamodel-code-generator
   ```

2. 创建自动生成脚本 (`scripts/dev/generate_pydantic_schemas.py`):
   ```python
   import subprocess
   from pathlib import Path

   def generate_schemas_from_openapi(
       openapi_file: str,
       output_file: str
   ):
       """从OpenAPI YAML生成Pydantic模型"""
       cmd = [
           "datamodel-codegen",
           "--input", openapi_file,
           "--output", output_file,
           "--input-file-type", "openapi",
           "--output-model-type", "pydantic_v2.BaseModel",
           "--use-schema-description",
           "--use-field-description",
           "--field-constraints"
       ]
       subprocess.run(cmd, check=True)

   if __name__ == "__main__":
       # 生成Market API模型
       generate_schemas_from_openapi(
           "docs/api/contracts/market_api.yaml",
           "web/backend/app/schemas/market_schemas.py"
       )
   ```

3. 验证生成的模型正确性:
   ```python
   from web.backend.app.schemas.market_schemas import KLineCandle

   # 测试模型验证
   candle = KLineCandle(
       timestamp=1640995200000,
       open=10.5,
       high=11.0,
       low=10.3,
       close=10.8,
       volume=1000000
   )
   assert candle.open == 10.5
   ```

**验收标准**:
- [ ] `datamodel-code-generator` 安装成功
- [ ] 自动生成脚本创建完成
- [ ] 从OpenAPI生成Pydantic模型测试通过

---

### 阶段2: Pydantic模型规范化 (T2.4-T2.6, 3天)

#### T2.4: 定义所有API的请求/响应Pydantic模型 (2天)

**目标**: 确保所有API端点都有明确的Pydantic请求/响应模型

**实施步骤**:
1. **Market模块模型** (`web/backend/app/schemas/market_schemas.py`):
   ```python
   from pydantic import BaseModel, Field
   from typing import Optional, List
   from datetime import datetime

   # 请求模型
   class KLineRequest(BaseModel):
       symbol: str = Field(..., description="股票代码", example="000001.SZ")
       interval: str = Field(..., description="K线周期", pattern="^(1m|5m|15m|1h|1d|1w|1M)$")
       start_date: Optional[datetime] = Field(None, description="开始日期")
       end_date: Optional[datetime] = Field(None, description="结束日期")
       adjust: str = Field("qfq", description="复权方式", pattern="^(qfq|hfq|none)$")

   # 响应模型
   class KLineCandle(BaseModel):
       timestamp: int = Field(..., description="Unix时间戳(毫秒)")
       open: float = Field(..., ge=0, description="开盘价")
       high: float = Field(..., ge=0, description="最高价")
       low: float = Field(..., ge=0, description="最低价")
       close: float = Field(..., ge=0, description="收盘价")
       volume: int = Field(..., ge=0, description="成交量")

   class KLineResponse(BaseModel):
       klines: List[KLineCandle]
       total_count: int
       symbol: str
       interval: str
   ```

2. **Technical模块模型** (`web/backend/app/schemas/technical_schemas.py`):
   ```python
   # 技术指标请求
   class IndicatorRequest(BaseModel):
       symbol: str
       interval: str
       indicators: List[str] = Field(..., description="指标列表", example=["MA", "EMA", "BOLL"])
       params: Optional[dict] = Field(None, description="指标参数", example={"MA_period": 20})

   # 技术指标响应
   class IndicatorValue(BaseModel):
       timestamp: int
       indicator_name: str
       value: float
       params: Optional[dict] = None

   class IndicatorResponse(BaseModel):
       symbol: str
       interval: str
       indicators: List[IndicatorValue]
   ```

3. **Trade模块模型** (`web/backend/app/schemas/trade_schemas.py`):
   ```python
   # 下单请求
   class OrderRequest(BaseModel):
       symbol: str
       direction: str = Field(..., pattern="^(buy|sell)$")
       price: float = Field(..., gt=0)
       quantity: int = Field(..., gt=0)
       order_type: str = Field("limit", pattern="^(limit|market)$")

   # 委托响应
   class OrderResponse(BaseModel):
       order_id: str
       status: str
       filled_quantity: int
       average_price: Optional[float] = None
       commission: float
       created_at: datetime
   ```

**验收标准**:
- [ ] Market/Technical/Trade模块所有模型定义完成
- [ ] 所有字段包含类型、描述、验证规则
- [ ] 请求/响应模型分离清晰

---

#### T2.5: 更新所有API路由,使用Pydantic模型 (1天)

**目标**: 重构API路由,强制使用Pydantic模型

**实施步骤**:
1. 重构Market API (`web/backend/app/api/market.py`):
   ```python
   from fastapi import APIRouter, HTTPException
   from app.schemas.market_schemas import KLineRequest, KLineResponse
   from app.schemas.common_schemas import APIResponse

   router = APIRouter(prefix="/api/market", tags=["market"])

   @router.get("/kline", response_model=APIResponse[KLineResponse])
   async def get_kline(request: KLineRequest):
       """获取K线数据 (使用Pydantic模型验证)"""
       try:
           # 调用数据服务
           klines = await fetch_kline_data(request)

           return APIResponse(
               success=True,
               code=0,
               message="成功获取K线数据",
               data=klines
           )
       except ValueError as e:
           raise HTTPException(status_code=400, detail=str(e))
   ```

2. 确保所有API都返回 `APIResponse[T]` 格式:
   ```python
   # ✅ 正确: 使用统一响应格式
   @router.get("/indicators/overlay", response_model=APIResponse[IndicatorResponse])
   async def get_overlay_indicators(request: IndicatorRequest):
       ...

   # ❌ 错误: 直接返回数据
   @router.get("/indicators/overlay")
   async def get_overlay_indicators(request: IndicatorRequest):
       return {"data": indicators}  # 不符合统一格式
   ```

**验收标准**:
- [ ] 所有API路由使用Pydantic请求模型
- [ ] 所有API返回 `APIResponse[T]` 格式
- [ ] FastAPI自动生成的OpenAPI文档正确

---

#### T2.6: 添加字段验证规则和错误提示 (0.5天)

**目标**: 增强Pydantic模型的数据验证能力

**实施步骤**:
1. 添加自定义验证器:
   ```python
   from pydantic import validator

   class KLineRequest(BaseModel):
       symbol: str
       interval: str

       @validator('symbol')
       def validate_symbol(cls, v):
           """验证股票代码格式"""
           if not v or len(v) < 6:
               raise ValueError("股票代码格式错误,至少6位")
           return v.upper()

       @validator('interval')
       def validate_interval(cls, v):
           """验证K线周期"""
           valid_intervals = ['1m', '5m', '15m', '1h', '1d', '1w', '1M']
           if v not in valid_intervals:
               raise ValueError(f"无效的K线周期,支持: {valid_intervals}")
           return v
   ```

2. 创建中文错误提示 (`web/backend/app/core/error_messages.py`):
   ```python
   ERROR_MESSAGES = {
       "INVALID_SYMBOL": "股票代码格式错误",
       "INVALID_INTERVAL": "K线周期格式错误",
       "INVALID_DATE_RANGE": "日期范围无效",
       "MISSING_REQUIRED_FIELD": "缺少必填字段: {field}",
   }
   ```

**验收标准**:
- [ ] 核心字段添加验证器
- [ ] 错误提示本地化 (中文)
- [ ] 验证失败返回清晰的错误信息

---

### 阶段3: 错误码标准化 (T2.7-T2.8, 1.5天)

#### T2.7: 定义统一错误码体系 (1天)

**目标**: 建立完整的业务错误码规范

**实施步骤**:
1. 创建错误码枚举 (`web/backend/app/core/error_codes.py`):
   ```python
   from enum import Enum

   class ErrorCode(Enum):
       """统一错误码"""
       # 成功 (0)
       SUCCESS = (0, "操作成功")

       # 客户端错误 (4xx)
       INVALID_PARAMETER = (400, "参数错误")
       UNAUTHORIZED = (401, "未授权,请先登录")
       FORBIDDEN = (403, "无权限访问")
       NOT_FOUND = (404, "资源不存在")
       METHOD_NOT_ALLOWED = (405, "请求方法不支持")
       REQUEST_TIMEOUT = (408, "请求超时")
       CONFLICT = (409, "数据冲突")
       UNPROCESSABLE_ENTITY = (422, "数据验证失败")
       TOO_MANY_REQUESTS = (429, "请求过于频繁")

       # 服务端错误 (5xx)
       INTERNAL_SERVER_ERROR = (500, "服务器内部错误")
       SERVICE_UNAVAILABLE = (503, "服务暂不可用")
       GATEWAY_TIMEOUT = (504, "网关超时")

       # 业务错误 (1xxx - 9xxx)
       SYMBOL_NOT_FOUND = (1001, "股票代码不存在")
       KLINE_DATA_NOT_AVAILABLE = (1002, "K线数据暂不可用")
       INDICATOR_CALCULATION_FAILED = (1003, "技术指标计算失败")
       ORDER_REJECTED = (2001, "订单被拒绝")
       INSUFFICIENT_BALANCE = (2002, "账户余额不足")
       POSITION_NOT_FOUND = (2003, "持仓不存在")
       STRATEGY_BACKTEST_FAILED = (3001, "策略回测失败")

       def __init__(self, code: int, message: str):
           self.code = code
           self.message = message
   ```

2. 创建异常类层次结构:
   ```python
   class APIException(Exception):
       """API业务异常基类"""
       def __init__(self, error_code: ErrorCode, detail: str = None):
           self.error_code = error_code
           self.detail = detail

       def to_response(self) -> dict:
           return {
               "success": False,
               "code": self.error_code.code,
               "message": self.error_code.message,
               "data": None,
               "detail": self.detail
           }

   class SymbolNotFoundException(APIException):
       def __init__(self, symbol: str):
           super().__init__(
               ErrorCode.SYMBOL_NOT_FOUND,
               detail=f"股票代码 '{symbol}' 不存在"
           )
   ```

**验收标准**:
- [ ] 错误码枚举定义完成 (0, 4xx, 5xx, 业务错误)
- [ ] 异常类层次结构创建完成
- [ ] 所有错误包含code和message

---

#### T2.8: 实现全局异常处理器 (0.5天)

**目标**: 统一处理所有异常,返回标准化错误响应

**实施步骤**:
1. 创建全局异常处理器 (`web/backend/app/middleware/exception_handler.py`):
   ```python
   from fastapi import Request, status
   from fastapi.responses import JSONResponse
   from app.core.error_codes import ErrorCode, APIException
   from pydantic import ValidationError

   async def api_exception_handler(request: Request, exc: APIException):
       """处理业务异常"""
       return JSONResponse(
           status_code=status.HTTP_200_OK,  # 业务异常HTTP状态码仍为200
           content=exc.to_response()
       )

   async def validation_exception_handler(request: Request, exc: ValidationError):
       """处理Pydantic验证异常"""
       errors = exc.errors()
       error_messages = [f"{err['loc'][-1]}: {err['msg']}" for err in errors]

       return JSONResponse(
           status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
           content={
               "success": False,
               "code": ErrorCode.UNPROCESSABLE_ENTITY.code,
               "message": "数据验证失败",
               "data": None,
               "detail": "; ".join(error_messages)
           }
       )

   async def generic_exception_handler(request: Request, exc: Exception):
       """处理未捕获的异常"""
       return JSONResponse(
           status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
           content={
               "success": False,
               "code": ErrorCode.INTERNAL_SERVER_ERROR.code,
               "message": "服务器内部错误",
               "data": None,
               "detail": str(exc) if settings.DEBUG else None
           }
       )
   ```

2. 在主应用注册异常处理器 (`web/backend/app/main.py`):
   ```python
   from app.middleware.exception_handler import (
       api_exception_handler,
       validation_exception_handler,
       generic_exception_handler
   )

   app.add_exception_handler(APIException, api_exception_handler)
   app.add_exception_handler(ValidationError, validation_exception_handler)
   app.add_exception_handler(Exception, generic_exception_handler)
   ```

**验收标准**:
- [ ] 全局异常处理器创建完成
- [ ] 所有异常返回统一格式
- [ ] 生产环境不暴露详细错误堆栈

---

### 阶段4: API契约组件开发 (T2.9-T2.12, 4天)

#### T2.9: 搭建api-contract-sync-manager平台 (最小可用版本, 2天)

**目标**: 创建契约管理平台,实现契约仓库和可视化编辑

**实施步骤**:
1. 创建契约管理目录结构:
   ```
   tools/api-contract-manager/
   ├── backend/
   │   ├── main.py                    # FastAPI应用
   │   ├── models/                    # 数据库模型
   │   │   ├── contract.py           # 契约模型
   │   │   └── version.py            # 版本模型
   │   ├── api/
   │   │   ├── contracts.py          # 契约CRUD
   │   │   └── validation.py         # 校验规则
   │   └── storage/
   │       └── contract_storage.py   # 契约文件存储
   ├── frontend/
   │   ├── src/
   │   │   ├── views/
   │   │   │   ├── ContractList.vue  # 契约列表
   │   │   │   ├── ContractEditor.vue # 可视化编辑器
   │   │   │   └── ValidationRules.vue # 校验规则配置
   │   │   └── components/
   │   │       └── SwaggerPreview.vue # Swagger预览
   │   └── package.json
   └── README.md
   ```

2. 实现契约仓库后端 (`tools/api-contract-manager/backend/main.py`):
   ```python
   from fastapi import FastAPI, HTTPException
   from pydantic import BaseModel
   from typing import List, Optional
   import yaml

   app = FastAPI(title="API Contract Manager")

   class Contract(BaseModel):
       id: str
       name: str
       module: str                    # 业务模块 (market/technical/trade)
       version: str                   # 语义化版本 (1.0.0)
       status: str                    # 待审核/已发布/已废弃
       openapi_spec: dict             # OpenAPI 3.0规范
       created_by: str
       created_at: str
       updated_at: str

   # 契约存储 (简化版,使用文件系统)
   CONTRACTS_DIR = "contracts/"

   @app.get("/api/contracts", response_model=List[Contract])
   async def list_contracts(module: Optional[str] = None, status: Optional[str] = None):
       """获取契约列表"""
       # 从文件系统加载契约
       ...

   @app.post("/api/contracts", response_model=Contract)
   async def create_contract(contract: Contract):
       """创建新契约"""
       # 保存契约到文件
       contract_file = f"{CONTRACTS_DIR}/{contract.module}/{contract.id}.yaml"
       with open(contract_file, 'w') as f:
           yaml.dump(contract.openapi_spec, f)
       return contract

   @app.get("/api/contracts/{contract_id}", response_model=Contract)
   async def get_contract(contract_id: str):
       """获取单个契约"""
       ...

   @app.put("/api/contracts/{contract_id}", response_model=Contract)
   async def update_contract(contract_id: str, contract: Contract):
       """更新契约 (创建新版本)"""
       ...

   @app.post("/api/contracts/{contract_id}/publish")
   async def publish_contract(contract_id: str):
       """发布契约 (状态: 待审核 → 已发布)"""
       ...
   ```

3. 实现可视化契约编辑器前端 (`tools/api-contract-manager/frontend/src/views/ContractEditor.vue`):
   ```vue
   <template>
     <div class="contract-editor">
       <el-form :model="contract" label-width="120px">
         <el-form-item label="契约名称">
           <el-input v-model="contract.name" />
         </el-form-item>

         <el-form-item label="业务模块">
           <el-select v-model="contract.module">
             <el-option label="Market" value="market" />
             <el-option label="Technical" value="technical" />
             <el-option label="Trade" value="trade" />
           </el-select>
         </el-form-item>

         <el-form-item label="API路径">
           <el-input v-model="contract.path" placeholder="/api/market/kline" />
         </el-form-item>

         <el-form-item label="请求方法">
           <el-radio-group v-model="contract.method">
             <el-radio label="GET" />
             <el-radio label="POST" />
             <el-radio label="PUT" />
             <el-radio label="DELETE" />
           </el-radio-group>
         </el-form-item>

         <!-- 参数配置 -->
         <el-form-item label="请求参数">
           <el-button @click="addParameter">添加参数</el-button>
           <el-table :data="contract.parameters">
             <el-table-column prop="name" label="参数名" />
             <el-table-column prop="type" label="类型" />
             <el-table-column prop="required" label="必填" />
             <el-table-column label="操作">
               <template #default="{ $index }">
                 <el-button @click="removeParameter($index)">删除</el-button>
               </template>
             </el-table-column>
           </el-table>
         </el-form-item>

         <!-- Swagger预览 -->
         <el-form-item label="预览">
           <swagger-preview :spec="generatedOpenAPISpec" />
         </el-form-item>

         <el-form-item>
           <el-button type="primary" @click="saveContract">保存契约</el-button>
           <el-button @click="publishContract">发布契约</el-button>
         </el-form-item>
       </el-form>
     </div>
   </template>

   <script setup>
   import { ref, computed } from 'vue'
   import SwaggerPreview from '@/components/SwaggerPreview.vue'

   const contract = ref({
     name: '',
     module: '',
     path: '',
     method: 'GET',
     parameters: []
   })

   const generatedOpenAPISpec = computed(() => {
     // 根据表单数据生成OpenAPI 3.0规范
     return {
       openapi: '3.0.3',
       paths: {
         [contract.value.path]: {
           [contract.value.method.toLowerCase()]: {
             summary: contract.value.name,
             parameters: contract.value.parameters
           }
         }
       }
     }
   })

   function addParameter() {
     contract.value.parameters.push({
       name: '',
       type: 'string',
       required: false
     })
   }

   function saveContract() {
     // 保存契约到后端
   }
   </script>
   ```

**验收标准**:
- [ ] 契约管理后端API创建完成 (CRUD)
- [ ] 可视化编辑器前端实现
- [ ] 契约按业务模块分类存储
- [ ] 支持契约版本管理

---

#### T2.10: 开发api-contract-sync CLI工具 (1.5天)

**目标**: 创建命令行工具,实现契约拉取和本地同步

**实施步骤**:
1. 创建CLI工具目录结构:
   ```
   tools/api-contract-sync/
   ├── cli/
   │   ├── main.py                   # 主入口
   │   ├── commands/
   │   │   ├── pull.py               # 拉取契约
   │   │   ├── validate.py           # 校验契约
   │   │   └── generate.py           # 生成测试用例
   │   └── utils/
   │       ├── contract_client.py    # Manager API客户端
   │       └── validator.py          # 契约校验器
   ├── setup.py
   └── README.md
   ```

2. 实现契约拉取命令 (`tools/api-contract-sync/cli/commands/pull.py`):
   ```python
   import click
   import requests
   import yaml
   from pathlib import Path

   @click.command()
   @click.option('--module', help='业务模块名称 (如 market)')
   @click.option('--all', is_flag=True, help='拉取所有契约')
   @click.option('--manager-url', required=True, help='Manager平台地址')
   @click.option('--token', required=True, help='认证Token')
   @click.option('--output-dir', default='./contracts', help='契约保存目录')
   def pull(module, all, manager_url, token, output_dir):
       """从Manager拉取最新契约"""
       headers = {'Authorization': f'Bearer {token}'}

       if all:
           # 拉取所有模块
           url = f'{manager_url}/api/contracts?status=已发布'
       else:
           # 拉取指定模块
           url = f'{manager_url}/api/contracts?module={module}&status=已发布'

       response = requests.get(url, headers=headers)
       contracts = response.json()

       # 保存到本地
       output_path = Path(output_dir)
       output_path.mkdir(parents=True, exist_ok=True)

       for contract in contracts:
           module_dir = output_path / contract['module']
           module_dir.mkdir(exist_ok=True)

           contract_file = module_dir / f"{contract['id']}.yaml"
           with open(contract_file, 'w') as f:
               yaml.dump(contract['openapi_spec'], f)

           click.echo(f"✅ 已拉取契约: {contract['name']} (v{contract['version']})")
   ```

3. 实现契约验证命令 (`tools/api-contract-sync/cli/commands/validate.py`):
   ```python
   @click.command()
   @click.option('--contract-path', required=True, help='本地契约目录')
   @click.option('--src-path', required=True, help='后端代码目录')
   def validate_code(contract_path, src_path):
       """校验后端代码与契约的一致性"""
       # 1. 加载所有本地契约
       contracts = load_contracts_from_path(contract_path)

       # 2. 扫描后端代码,提取API定义
       api_definitions = scan_fastapi_routes(src_path)

       # 3. 对比契约与代码
       mismatches = []
       for contract in contracts:
           api_path = contract['paths'].keys()[0]

           if api_path not in api_definitions:
               mismatches.append({
                   'type': 'MISSING_ENDPOINT',
                   'path': api_path,
                   'message': f"契约中存在,但代码中未实现"
               })
           else:
               # 对比参数、返回模型
               code_api = api_definitions[api_path]

               # 检查参数一致性
               if not check_parameters_match(contract, code_api):
                   mismatches.append({
                       'type': 'PARAMETER_MISMATCH',
                       'path': api_path
                   })

       # 4. 生成校验报告
       if mismatches:
           click.echo("❌ 契约校验失败:")
           for mismatch in mismatches:
               click.echo(f"  - {mismatch['type']}: {mismatch['path']}")
           exit(1)
       else:
           click.echo("✅ 契约校验通过")
   ```

4. 实现测试用例生成命令 (`tools/api-contract-sync/cli/commands/generate.py`):
   ```python
   @click.command()
   @click.option('--contract-path', required=True, help='契约文件路径')
   @click.option('--output-path', required=True, help='测试用例输出路径')
   @click.option('--type', default='pytest', help='测试类型 (pytest/postman)')
   def generate_test(contract_path, output_path, type):
       """根据契约生成测试用例"""
       contract = load_contract(contract_path)

       if type == 'pytest':
           # 生成pytest脚本
           test_code = generate_pytest_code(contract)

           with open(output_path, 'w') as f:
               f.write(test_code)

           click.echo(f"✅ 已生成pytest测试用例: {output_path}")
       elif type == 'postman':
           # 生成Postman集合
           postman_collection = generate_postman_collection(contract)

           with open(output_path, 'w') as f:
               json.dump(postman_collection, f, indent=2)

           click.echo(f"✅ 已生成Postman集合: {output_path}")
   ```

5. 创建CLI入口 (`tools/api-contract-sync/cli/main.py`):
   ```python
   import click
   from commands.pull import pull
   from commands.validate import validate_code
   from commands.generate import generate_test

   @click.group()
   def cli():
       """API Contract Sync CLI"""
       pass

   cli.add_command(pull)
   cli.add_command(validate_code)
   cli.add_command(generate_test)

   if __name__ == '__main__':
       cli()
   ```

**验收标准**:
- [ ] CLI工具创建完成 (pull/validate/generate命令)
- [ ] 契约拉取和本地同步功能测试通过
- [ ] 代码与契约校验功能测试通过
- [ ] 测试用例生成功能测试通过

---

#### T2.11: 实现契约校验规则引擎 (0.5天)

**目标**: 实现基础和自定义校验规则

**实施步骤**:
1. 创建校验规则引擎 (`tools/api-contract-sync/cli/utils/validator.py`):
   ```python
   from typing import List, Dict, Any

   class ValidationRule:
       """校验规则基类"""
       def validate(self, contract: dict, actual_response: dict) -> List[str]:
           """返回错误列表,空列表表示通过"""
           raise NotImplementedError

   class FieldNameConsistencyRule(ValidationRule):
       """字段名一致性校验"""
       def validate(self, contract: dict, actual_response: dict) -> List[str]:
           errors = []
           expected_fields = set(contract['properties'].keys())
           actual_fields = set(actual_response.keys())

           # 检查缺失字段
           missing_fields = expected_fields - actual_fields
           if missing_fields:
               errors.append(f"缺失字段: {missing_fields}")

           # 检查多余字段
           extra_fields = actual_fields - expected_fields
           if extra_fields:
               errors.append(f"多余字段: {extra_fields}")

           return errors

   class FieldTypeConsistencyRule(ValidationRule):
       """字段类型一致性校验"""
       def validate(self, contract: dict, actual_response: dict) -> List[str]:
           errors = []
           for field, schema in contract['properties'].items():
               if field in actual_response:
                   expected_type = schema['type']
                   actual_value = actual_response[field]

                   if expected_type == 'integer' and not isinstance(actual_value, int):
                       errors.append(f"字段 '{field}' 类型错误: 期望 integer, 实际 {type(actual_value).__name__}")
                   elif expected_type == 'string' and not isinstance(actual_value, str):
                       errors.append(f"字段 '{field}' 类型错误: 期望 string, 实际 {type(actual_value).__name__}")

           return errors

   class RequiredFieldNonNullRule(ValidationRule):
       """必填字段非空校验"""
       def validate(self, contract: dict, actual_response: dict) -> List[str]:
           errors = []
           required_fields = contract.get('required', [])

           for field in required_fields:
               if field not in actual_response or actual_response[field] is None:
                   errors.append(f"必填字段 '{field}' 缺失或为空")

           return errors

   class ContractValidator:
       """契约校验器"""
       def __init__(self):
           self.rules = [
               FieldNameConsistencyRule(),
               FieldTypeConsistencyRule(),
               RequiredFieldNonNullRule()
           ]

       def validate(self, contract: dict, actual_response: dict) -> Dict[str, Any]:
           """执行所有校验规则"""
           all_errors = []

           for rule in self.rules:
               errors = rule.validate(contract, actual_response)
               all_errors.extend(errors)

           return {
               'passed': len(all_errors) == 0,
               'errors': all_errors
           }
   ```

2. 集成到validate命令:
   ```python
   from utils.validator import ContractValidator

   def validate_response(contract_file: str, actual_response: dict):
       """校验实际响应与契约的一致性"""
       contract = load_contract(contract_file)
       validator = ContractValidator()

       result = validator.validate(contract, actual_response)

       if result['passed']:
           click.echo("✅ 响应校验通过")
       else:
           click.echo("❌ 响应校验失败:")
           for error in result['errors']:
               click.echo(f"  - {error}")
   ```

**验收标准**:
- [ ] 基础校验规则实现完成 (字段名/类型/必填)
- [ ] 校验器集成到CLI工具
- [ ] 校验失败返回详细错误信息

---

#### T2.12: 集成CI/CD和告警通知 (0.5天)

**目标**: 在GitLab CI中集成契约校验,阻断不合格API上线

**实施步骤**:
1. 创建GitLab CI配置 (`.gitlab-ci.yml`):
   ```yaml
   stages:
     - contract_validate
     - build
     - test
     - deploy

   # 契约校验阶段 (前置步骤)
   contract_validate:
     stage: contract_validate
     image: python:3.12
     script:
       # 1. 安装api-contract-sync工具
       - cd tools/api-contract-sync
       - pip install -e .

       # 2. 拉取Manager最新契约
       - api-contract-sync pull --all --manager-url $CONTRACT_MANAGER_URL --token $CONTRACT_MANAGER_TOKEN

       # 3. 校验后端代码与契约的一致性
       - api-contract-sync validate code --contract-path ./contracts --src-path ./web/backend/app

       # 4. 启动测试环境并校验实际响应
       - cd ../../web/backend
       - uvicorn app.main:app --host 0.0.0.0 --port 8000 &
       - sleep 5
       - pytest tests/contract_validation/ --contract-dir ../../contracts

     # 阻断规则: 校验失败则阻断后续流程
     only:
       - master
       - develop

     # 失败时发送告警
     after_script:
       - |
         if [ $CI_JOB_STATUS == 'failed' ]; then
           curl -X POST $DINGTALK_WEBHOOK \
             -H 'Content-Type: application/json' \
             -d "{
               \"msgtype\": \"text\",
               \"text\": {
                 \"content\": \"❌ API契约校验失败\n项目: $CI_PROJECT_NAME\n分支: $CI_COMMIT_REF_NAME\n提交: $CI_COMMIT_SHORT_SHA\n详情: $CI_JOB_URL\"
               }
             }"
         fi

   build:
     stage: build
     script:
       - echo "构建应用..."
     needs:
       - contract_validate  # 依赖契约校验通过
   ```

2. 创建契约校验测试用例 (`tests/contract_validation/test_market_api_contract.py`):
   ```python
   import pytest
   import requests
   from api_contract_sync.utils.validator import ContractValidator
   import yaml

   @pytest.fixture
   def market_kline_contract():
       """加载Market K线API契约"""
       with open('contracts/market/kline.yaml', 'r') as f:
           return yaml.safe_load(f)

   def test_kline_api_contract_compliance(market_kline_contract):
       """测试K线API是否符合契约"""
       # 发送实际请求
       response = requests.get(
           'http://localhost:8000/api/market/kline',
           params={
               'symbol': '000001.SZ',
               'interval': '1d',
               'start_date': '2024-01-01',
               'end_date': '2024-12-29'
           }
       )

       assert response.status_code == 200
       actual_response = response.json()

       # 校验响应与契约的一致性
       validator = ContractValidator()
       result = validator.validate(market_kline_contract, actual_response['data'])

       assert result['passed'], f"契约校验失败: {result['errors']}"
   ```

**验收标准**:
- [ ] GitLab CI配置完成
- [ ] 契约校验集成到CI流程
- [ ] 校验失败阻断后续部署
- [ ] 告警通知发送成功 (钉钉/企业微信)

---

### 阶段5: TypeScript类型生成 (T2.13-T2.14, 2天)

#### T2.13: 从OpenAPI自动生成TypeScript类型定义 (1.5天)

**目标**: 实现前端TypeScript类型与后端契约完全同步

**实施步骤**:
1. 安装TypeScript类型生成工具:
   ```bash
   npm install --save-dev openapi-typescript
   ```

2. 创建类型生成脚本 (`scripts/dev/generate_typescript_types.sh`):
   ```bash
   #!/bin/bash

   # 生成TypeScript类型定义

   # 1. 从FastAPI自动生成OpenAPI Schema
   cd web/backend
   python -c "
   from app.main import app
   import json

   openapi_schema = app.openapi()

   with open('../../web/frontend/src/api/types/openapi.json', 'w') as f:
       json.dump(openapi_schema, f, indent=2)
   "

   # 2. 从OpenAPI Schema生成TypeScript类型
   cd ../../web/frontend
   npx openapi-typescript src/api/types/openapi.json --output src/api/types/api-types.ts

   echo "✅ TypeScript类型定义已生成: src/api/types/api-types.ts"
   ```

3. 生成的TypeScript类型示例 (`web/frontend/src/api/types/api-types.ts`):
   ```typescript
   // 自动生成的类型定义

   export interface paths {
     "/api/market/kline": {
       get: operations["getKlineData"];
     };
     "/api/indicators/overlay": {
       get: operations["getOverlayIndicators"];
     };
   }

   export interface components {
     schemas: {
       APIResponse_KLineResponse_: {
         success: boolean;
         code: number;
         message: string;
         data?: components["schemas"]["KLineResponse"];
         request_id: string;
         timestamp: string;
       };
       KLineResponse: {
         klines: components["schemas"]["KLineCandle"][];
         total_count: number;
         symbol: string;
         interval: string;
       };
       KLineCandle: {
         timestamp: number;
         open: number;
         high: number;
         low: number;
         close: number;
         volume: number;
       };
     };
   }

   export interface operations {
     getKlineData: {
       parameters: {
         query: {
           symbol: string;
           interval: string;
           start_date?: string;
           end_date?: string;
           adjust?: string;
         };
       };
       responses: {
         200: {
           content: {
             "application/json": components["schemas"]["APIResponse_KLineResponse_"];
           };
         };
       };
     };
   }
   ```

4. 配置自动生成流程 (添加到 `package.json`):
   ```json
   {
     "scripts": {
       "generate-types": "bash ../../scripts/dev/generate_typescript_types.sh",
       "predev": "npm run generate-types"
     }
   }
   ```

**验收标准**:
- [ ] TypeScript类型生成脚本创建完成
- [ ] 前端可以正确导入和使用生成的类型
- [ ] 类型定义与后端Pydantic模型完全一致

---

#### T2.14: 创建前端Service适配器层 (0.5天)

**目标**: 封装API调用,使用TypeScript类型约束

**实施步骤**:
1. 创建类型安全的API Service (`web/frontend/src/api/market.ts`):
   ```typescript
   import request from '@/utils/request'
   import type { components, operations } from './types/api-types'

   type KLineResponse = components['schemas']['APIResponse_KLineResponse_']
   type KLineParams = operations['getKlineData']['parameters']['query']

   /**
    * 获取K线数据 (类型安全)
    */
   export async function getKlineData(params: KLineParams): Promise<KLineResponse> {
     return request.get<KLineResponse>('/api/market/kline', { params })
   }

   /**
    * 获取主图叠加指标
    */
   export async function getOverlayIndicators(
     params: operations['getOverlayIndicators']['parameters']['query']
   ): Promise<components['schemas']['APIResponse_IndicatorResponse_']> {
     return request.get('/api/indicators/overlay', { params })
   }
   ```

2. 创建数据适配器 (`web/frontend/src/utils/adapters.ts`):
   ```typescript
   import type { components } from '@/api/types/api-types'

   type KLineCandle = components['schemas']['KLineCandle']

   /**
    * 将API返回的K线数据转换为ECharts格式
    */
   export function adaptKLineToECharts(klines: KLineCandle[]) {
     return klines.map(candle => ({
       time: candle.timestamp / 1000,  // 转换为秒
       open: candle.open,
       high: candle.high,
       low: candle.low,
       close: candle.close,
       volume: candle.volume
     }))
   }
   ```

3. 在组件中使用 (`web/frontend/src/views/StockDetail.vue`):
   ```typescript
   <script setup lang="ts">
   import { ref } from 'vue'
   import { getKlineData } from '@/api/market'
   import { adaptKLineToECharts } from '@/utils/adapters'
   import type { components } from '@/api/types/api-types'

   type KLineCandle = components['schemas']['KLineCandle']

   const klineData = ref<KLineCandle[]>([])

   async function fetchKlineData() {
     try {
       const response = await getKlineData({
         symbol: '000001.SZ',
         interval: '1d'
       })

       if (response.success) {
         klineData.value = response.data?.klines || []

         // 转换为ECharts格式
         const chartData = adaptKLineToECharts(klineData.value)
         renderChart(chartData)
       }
     } catch (error) {
       console.error('获取K线数据失败:', error)
     }
   }
   </script>
   ```

**验收标准**:
- [ ] API Service层创建完成,所有调用类型安全
- [ ] 数据适配器层实现完成
- [ ] 组件中正确使用生成的TypeScript类型

---

### 阶段6: 文档与测试 (T2.15-T2.17, 1.5天)

#### T2.15: 集成Swagger UI和API文档 (0.5天)

**目标**: 提供交互式API文档和在线调试

**实施步骤**:
1. 配置FastAPI Swagger UI (`web/backend/app/main.py`):
   ```python
   from fastapi import FastAPI
   from fastapi.openapi.docs import get_swagger_ui_html
   from fastapi.openapi.utils import get_openapi

   app = FastAPI(
       title="MyStocks API",
       version="1.0.0",
       docs_url="/api/docs",       # Swagger UI地址
       redoc_url="/api/redoc",      # ReDoc文档地址
       openapi_url="/api/openapi.json"
   )

   # 自定义Swagger UI主题
   @app.get("/api/docs", include_in_schema=False)
   async def custom_swagger_ui_html():
       return get_swagger_ui_html(
           openapi_url=app.openapi_url,
           title=f"{app.title} - Swagger UI",
           swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png"
       )

   # 自定义OpenAPI Schema
   def custom_openapi():
       if app.openapi_schema:
           return app.openapi_schema

       openapi_schema = get_openapi(
           title=app.title,
           version=app.version,
           description="""
           **MyStocks量化交易系统API文档**

           - **Market**: 市场数据API
           - **Technical**: 技术指标API
           - **Trade**: 交易执行API
           - **Strategy**: 策略管理API
           - **System**: 系统监控API
           """,
           routes=app.routes
       )

       # 添加全局安全定义
       openapi_schema["components"]["securitySchemes"] = {
           "BearerAuth": {
               "type": "http",
               "scheme": "bearer",
               "bearerFormat": "JWT"
           }
       }

       app.openapi_schema = openapi_schema
       return app.openapi_schema

   app.openapi = custom_openapi
   ```

2. 添加API使用示例 (在Pydantic模型中):
   ```python
   class KLineRequest(BaseModel):
       symbol: str = Field(..., description="股票代码", example="000001.SZ")
       interval: str = Field(..., description="K线周期", example="1d")

       class Config:
           schema_extra = {
               "example": {
                   "symbol": "000001.SZ",
                   "interval": "1d",
                   "start_date": "2024-01-01",
                   "end_date": "2024-12-29",
                   "adjust": "qfq"
               }
           }
   ```

**验收标准**:
- [ ] Swagger UI可访问 (http://localhost:8000/api/docs)
- [ ] 所有API端点在文档中展示
- [ ] 支持在线调试和参数测试

---

#### T2.16: 创建API测试套件 (0.5天)

**目标**: 批量生成API测试用例,验证契约合规性

**实施步骤**:
1. 使用api-contract-sync生成pytest测试用例:
   ```bash
   api-contract-sync generate test \
     --contract-path contracts/ \
     --output-path tests/api_contract/ \
     --type pytest
   ```

2. 生成的测试用例示例 (`tests/api_contract/test_market_api.py`):
   ```python
   import pytest
   import requests
   from api_contract_sync.utils.validator import ContractValidator

   BASE_URL = "http://localhost:8000"

   class TestMarketAPIContract:
       """Market API契约测试"""

       def test_kline_api(self):
           """测试K线API契约合规性"""
           # 发送请求
           response = requests.get(
               f"{BASE_URL}/api/market/kline",
               params={
                   "symbol": "000001.SZ",
                   "interval": "1d",
                   "start_date": "2024-01-01",
                   "end_date": "2024-12-29"
               }
           )

           # 基本断言
           assert response.status_code == 200
           data = response.json()
           assert data['success'] is True

           # 契约校验
           validator = ContractValidator()
           result = validator.validate(
               contract_file="contracts/market/kline.yaml",
               actual_response=data
           )

           assert result['passed'], f"契约校验失败: {result['errors']}"

       @pytest.mark.parametrize("symbol,interval", [
           ("000001.SZ", "1d"),
           ("600519.SH", "1h"),
           ("300750.SZ", "15m")
       ])
       def test_kline_api_multiple_symbols(self, symbol, interval):
           """测试多种股票代码和周期"""
           response = requests.get(
               f"{BASE_URL}/api/market/kline",
               params={"symbol": symbol, "interval": interval}
           )

           assert response.status_code == 200
           assert response.json()['success'] is True
   ```

3. 运行测试套件:
   ```bash
   pytest tests/api_contract/ -v --html=reports/api_contract_report.html
   ```

**验收标准**:
- [ ] 所有核心API有对应的契约测试
- [ ] 测试套件可正常运行
- [ ] 生成HTML测试报告

---

#### T2.17: 编写完成报告和交付文档 (0.5天)

**目标**: 记录API契约优化的完整成果

**实施步骤**:
1. 创建完成报告 (`docs/guides/multi-cli-tasks/CLI-2_COMPLETION_REPORT.md`):
   ```markdown
   # CLI-2 完成报告 - API契约优化与标准化

   **完成时间**: 2025-XX-XX
   **分支**: cli2-api-contract
   **验收状态**: ✅ 所有任务完成

   ---

   ## 1. 核心成果

   ### 1.1 OpenAPI Schema标准化
   - ✅ 统一响应格式 (APIResponse, CommonError)
   - ✅ 完整的OpenAPI 3.0契约模板
   - ✅ 200+API端点契约梳理完成
   - ✅ Pydantic模型自动生成脚本

   ### 1.2 Pydantic模型规范化
   - ✅ 所有API使用Pydantic请求/响应模型
   - ✅ 字段验证规则和错误提示本地化
   - ✅ Market/Technical/Trade模块模型完整

   ### 1.3 错误码标准化
   - ✅ 统一错误码枚举 (0, 4xx, 5xx, 业务错误)
   - ✅ 异常类层次结构
   - ✅ 全局异常处理器

   ### 1.4 API契约组件
   - ✅ api-contract-sync-manager平台 (契约仓库/可视化编辑)
   - ✅ api-contract-sync CLI工具 (拉取/校验/生成)
   - ✅ 契约校验规则引擎 (基础+自定义规则)
   - ✅ CI/CD集成 (GitLab CI)

   ### 1.5 TypeScript类型生成
   - ✅ OpenAPI → TypeScript自动生成
   - ✅ 类型安全的API Service层
   - ✅ 数据适配器层

   ### 1.6 文档与测试
   - ✅ Swagger UI集成
   - ✅ API测试套件 (pytest)
   - ✅ 契约合规性测试

   ---

   ## 2. 关键指标

   | 指标 | 目标 | 实际 | 状态 |
   |------|------|------|------|
   | API契约覆盖率 | 100% | 100% | ✅ |
   | Pydantic模型覆盖率 | 100% | 100% | ✅ |
   | TypeScript类型同步 | 自动化 | 自动化 | ✅ |
   | CI/CD集成 | 完成 | 完成 | ✅ |
   | 契约校验通过率 | >95% | 98% | ✅ |

   ---

   ## 3. 关键文件清单

   ### 后端 (FastAPI)
   - `web/backend/app/schemas/common_schemas.py` - 统一响应格式
   - `web/backend/app/schemas/market_schemas.py` - Market API模型
   - `web/backend/app/schemas/technical_schemas.py` - Technical API模型
   - `web/backend/app/schemas/trade_schemas.py` - Trade API模型
   - `web/backend/app/core/error_codes.py` - 错误码枚举
   - `web/backend/app/middleware/exception_handler.py` - 全局异常处理

   ### 前端 (Vue 3 + TypeScript)
   - `web/frontend/src/api/types/api-types.ts` - 自动生成的TypeScript类型
   - `web/frontend/src/api/market.ts` - Market API Service
   - `web/frontend/src/utils/adapters.ts` - 数据适配器

   ### 工具 (API契约组件)
   - `tools/api-contract-manager/` - 契约管理平台
   - `tools/api-contract-sync/` - 契约同步工具

   ### 文档
   - `docs/api/openapi_template.yaml` - OpenAPI 3.0模板
   - `docs/api/contracts/` - 所有API契约文件
   - `docs/api/API_INVENTORY.md` - API清单

   ### 测试
   - `tests/api_contract/` - API契约测试套件
   - `.gitlab-ci.yml` - CI/CD配置

   ---

   ## 4. 后续建议

   1. **CLI-1依赖**: CLI-1前端K线组件可直接使用生成的TypeScript类型
   2. **CLI-3依赖**: CLI-3后端指标计算API应遵循契约标准
   3. **持续维护**: 所有新API必须先在Manager中定义契约
   4. **团队培训**: 确保所有开发人员掌握契约工作流程

   ---

   **交付状态**: ✅ 已完成,可合并到main分支
   ```

**验收标准**:
- [ ] 完成报告创建
- [ ] 关键文件清单完整
- [ ] 后续建议清晰

---

## 📊 任务依赖关系

```
T2.1 (统一响应格式)
  ↓
T2.2 (梳理API端点)
  ↓
T2.3 (Pydantic自动生成)
  ↓
T2.4 (定义Pydantic模型) ─→ T2.13 (TypeScript类型生成)
  ↓                         ↓
T2.5 (更新API路由)         T2.14 (Service适配器层)
  ↓
T2.6 (字段验证规则)
  ↓
T2.7 (错误码体系)
  ↓
T2.8 (全局异常处理)
  ↓
T2.9 (Manager平台)
  ↓
T2.10 (Sync CLI工具)
  ↓
T2.11 (校验规则引擎)
  ↓
T2.12 (CI/CD集成)
  ↓
T2.15 (Swagger UI)
  ↓
T2.16 (测试套件)
  ↓
T2.17 (完成报告)
```

---

## ⏱️ 时间分配

| 阶段 | 任务编号 | 预计时间 | 说明 |
|------|---------|---------|------|
| 阶段1 | T2.1-T2.3 | 3天 | OpenAPI Schema标准化 |
| 阶段2 | T2.4-T2.6 | 3天 | Pydantic模型规范化 |
| 阶段3 | T2.7-T2.8 | 1.5天 | 错误码标准化 |
| 阶段4 | T2.9-T2.12 | 4天 | API契约组件开发 |
| 阶段5 | T2.13-T2.14 | 2天 | TypeScript类型生成 |
| 阶段6 | T2.15-T2.17 | 1.5天 | 文档与测试 |
| **总计** | **17任务** | **12-14天** | |

---

## ✅ 最终验收标准

### 功能验收
- [ ] 所有200+API端点有完整的OpenAPI 3.0契约定义
- [ ] 所有API使用Pydantic请求/响应模型,类型验证完整
- [ ] 统一错误码体系覆盖所有错误场景
- [ ] api-contract-sync-manager平台功能正常 (契约CRUD/版本管理)
- [ ] api-contract-sync CLI工具所有命令测试通过
- [ ] TypeScript类型定义与后端Pydantic模型100%同步
- [ ] CI/CD中契约校验集成,阻断不合格API上线
- [ ] Swagger UI可访问,支持在线调试

### 质量验收
- [ ] 契约校验通过率 > 95%
- [ ] API测试套件覆盖率 > 80%
- [ ] 前端TypeScript类型检查无错误
- [ ] 所有API返回统一响应格式 (APIResponse)
- [ ] 错误信息本地化 (中文提示)

### 文档验收
- [ ] API清单 (API_INVENTORY.md) 完整
- [ ] Swagger UI文档准确
- [ ] 完成报告包含所有关键文件和成果
- [ ] 操作手册 (如何使用Manager和Sync工具)

---

## 📝 工作日志模板

```markdown
# CLI-2 工作日志

## Day 1 (YYYY-MM-DD)
**进度**: T2.1 统一响应格式定义

### 完成工作
- 创建 `common_schemas.py`,定义 `APIResponse` 和 `CommonError`
- 创建OpenAPI 3.0契约模板 (`docs/api/openapi_template.yaml`)
- 定义5个核心业务模块路由

### 遇到问题
- 无

### 明日计划
- 开始T2.2梳理现有API端点

---

## Day 2 (YYYY-MM-DD)
...
```

---

## 🎯 成功标准总结

**CLI-2完成的标志**:
1. ✅ 所有API有明确的OpenAPI 3.0契约
2. ✅ 前后端通过契约完全对齐 (TypeScript类型自动生成)
3. ✅ CI/CD流程中集成契约校验,阻断不合格API
4. ✅ CLI-1和CLI-3可以直接使用标准化的API契约

**对项目的价值**:
- **零开发摩擦**: 前端组件与后端API无缝对接
- **类型安全**: 端到端类型安全,减少90%类型错误
- **自动化校验**: 契约与代码自动对比,避免"文档写的是A,代码实现的是B"
- **CI/CD保障**: 不合格API无法上线,确保契约合规性

---

**参考文档**:
- `/opt/claude/mystocks_spec/docs/api/API契约同步组件实现方案.md`
- `/opt/claude/mystocks_spec/docs/api/API与Web组件最终对齐方案.md`
- `/opt/claude/mystocks_spec/openspec/changes/frontend-optimization-six-phase/proposal.md`

---

## 冲突预防与文件所有权

### 🔐 核心原则

**明确所有权 + 职责分离 = 零冲突协作**

- **文件所有权明确**: 每个文件有唯一的拥有者CLI
- **职责范围清晰**: 通过目录结构物理隔离
- **配置集中管理**: Pre-commit配置只由主CLI维护
- **协调机制完善**: 跨CLI修改需要主CLI协调

### 📋 CLI-2文件所有权

**CLI-2拥有以下文件**:
- `docs/api/contracts/` - API契约文档
- `web/backend/app/schemas/` - Pydantic数据模型
- `web/backend/openapi/` - OpenAPI规范文件
- `tools/api-contract-manager/` - API契约管理平台
- `tools/api-contract-sync/` - API契约同步工具

**共享文件** (需协调修改):
- `README.md` - 主CLI维护，CLI-2可建议
- `web/backend/app/main.py` - 拥有者: main (CLI-2需要修改时需申请)
- `CHANGELOG.md` - 主CLI维护

### 🚫 文件修改限制

**CLI-2不允许修改**:
1. ✅ `.pre-commit-config.yaml` - Pre-commit配置（由主CLI管理）
2. ✅ `pyproject.toml` - Python项目配置（由主CLI管理）
3. ✅ `src/` - 核心业务逻辑（由主CLI管理）
4. ✅ `config/` - 配置文件（由主CLI管理）
5. ✅ 其他CLI拥有的文件

**如需修改其他CLI拥有的文件**:
1. 向主CLI提交申请（包含修改原因和内容）
2. 主CLI评估影响范围
3. 主CLI协调相关CLI
4. 主CLI执行修改或授权CLI-2修改
5. 主CLI通知所有相关CLI

**⚠️ 特别注意**: CLI-2需要修改`web/backend/app/main.py`来注册全局异常处理器。根据冲突检测结果，这是1个历史遗留冲突，需要通过主CLI协调。

### 🔍 如何查看文件所有权

```bash
# 方法1: 查看所有权映射文件
cat /opt/claude/mystocks_spec/.FILE_OWNERSHIP | grep <文件路径>

# 方法2: 运行冲突检测脚本
cd /opt/claude/mystocks_spec
bash scripts/maintenance/check_file_conflicts.sh

# 方法3: 查看完整所有权映射
cat /opt/claude/mystocks_spec/.FILE_OWNERSHIP
```

### ⚙️ Pre-commit配置说明

**重要**: CLI-2 **继承**主CLI的pre-commit配置，**不应修改** `.pre-commit-config.yaml`。

**如果pre-commit检查失败**（例如目录结构检查）:
```bash
# 使用环境变量绕过不适用的检查
DISABLE_DIR_STRUCTURE_CHECK=1 git commit -m "commit message"
```

**何时使用环境变量**:
- ✅ Worktree环境与主仓库不同，导致目录结构检查失败
- ✅ 文件组织形式不同，但仍符合项目规范
- ❌ 不能用于绕过代码质量检查（Ruff, Black, Pylint等）

### 📖 相关文档

- **[冲突预防规范](../../mystocks_spec/docs/guides/multi-cli-tasks/GIT_WORKTREE_COLLABORATION_CONFLICT_PREVENTION.md)** - 完整指南
- **[文件所有权映射](../../mystocks_spec/.FILE_OWNERSHIP)** - 所有权定义
- **[主CLI工作规范](../../mystocks_spec/docs/guides/multi-cli-tasks/MAIN_CLI_WORKFLOW_STANDARDS.md)** - 工作流程标准

---

## 工作流程与Git提交规范

### 📚 完整工作流程指南

详细的Worker CLI工作流程请参考:
📖 **[CLI工作流程指南](../../mystocks_spec/docs/guides/multi-cli-tasks/CLI_WORKFLOW_GUIDE.md)**

### ⚡ 快速参考

#### 每日工作流程

```bash
# 1. 拉取最新代码
cd /opt/claude/mystocks_phase6_api_contract
git pull

# 2. 查看今日任务
vim README.md  # 查看"进度跟踪"章节

# 3. 开发实现
vim docs/api/contracts/market_api.yaml

# 4. 代码质量检查
ruff check . --fix
black .
pylint src/

# 5. Git提交
git add .
git commit -m "feat(api): add market data OpenAPI schema

- Define GET /api/market/kline endpoint
- Add request/response schemas with Pydantic
- Include error codes and validation rules

Task: T2.1
Acceptance: [x] OpenAPI schema [x] Pydantic models [ ] TypeScript types"

# 6. 更新README进度
vim README.md
git add README.md
git commit -m "docs(readme): update progress to T+24h"

# 7. 推送到远程
git push
```

#### Git提交消息规范

```bash
# 格式: <type>(<scope>): <subject>

# Type类型:
feat:     新功能
fix:      修复bug
docs:     文档更新
test:     测试相关
refactor: 重构代码
chore:    构建/工具链相关

# 示例:
git commit -m "feat(schemas): implement UnifiedResponse v2.0

- Add UnifiedResponse base class
- Implement ErrorCode enum with 20+ error codes
- Add success() and error() factory methods
- Include request_id tracking

Task: T2.3
Acceptance: [x] Base class [x] ErrorCode [x] Factory methods [x] Tests"
```

#### 完成标准检查清单

每个任务完成前必须确认:

- [ ] 所有验收标准通过
- [ ] 代码已提交到Git（频繁提交，小步快跑）
- [ ] 测试覆盖率达标（后端>80%）
- [ ] 代码质量检查通过（Pylint>8.0）
- [ ] README已更新（进度+任务状态）
- [ ] API契约文档完整（OpenAPI + Pydantic + TypeScript）

#### 提交频率建议

✅ **好的实践**:
- 每完成一个API端点定义就提交
- 至少每天一次提交
- 每次提交只包含一个API模块

❌ **不好的实践**:
- 积累多个API定义后才提交
- 一次提交包含不相关的改动
- 几天不提交代码

#### 进度更新格式

```markdown
## 进度更新

### T+0h (2025-12-29 15:00)
- ✅ 任务启动
- 📝 当前任务: T2.1 创建API契约目录结构
- ⏳ 预计完成: 2025-12-29 18:00
- 🚧 阻塞问题: 无

### T+24h (2025-12-30 15:00)
- ✅ T2.2 Market API契约定义完成
  - Git提交: abc1234, def5678
  - 验收标准: [x] OpenAPI schema [x] TypeScript types
  - 测试覆盖: 90%
- 📝 当前任务: T2.3 实现UnifiedResponse
- 🚧 阻塞问题: 无
```

### 🎯 关键注意事项

1. **API契约优先**: 先定义OpenAPI schema，再实现Pydantic模型
2. **频繁提交**: 每完成一个API端点就提交
3. **原子提交**: 每次提交只包含一个API模块
4. **优先级最高**: CLI-3和CLI-4依赖你，请加快进度
5. **及时更新README**: 每天至少更新一次进度

### 📞 需要帮助？

- 📖 [完整工作流程](../../mystocks_spec/docs/guides/multi-cli-tasks/CLI_WORKFLOW_GUIDE.md)
- 📚 [API契约参考](../../mystocks_spec/docs/api/API契约同步组件实现方案.md)
- 🚧 遇到阻塞: 在README中记录，主CLI会优先处理
