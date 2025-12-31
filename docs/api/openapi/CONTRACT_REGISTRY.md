# API契约注册记录

本文档记录所有已注册的API契约，作为临时的契约管理平台。

---

## 契约列表

### market-data v1.0.0

**基本信息**:
- **名称**: market-data
- **版本**: 1.0.0
- **状态**: ✅ Active (stable, production)
- **注册日期**: 2025-12-29
- **描述**: 市场数据API - 包含6个核心端点

**API端点**:
1. `GET /api/market/overview` - 市场概览
2. `GET /api/market/fund-flow` - 资金流向
3. `GET /api/market/kline` - K线数据
4. `GET /api/market/etf/list` - ETF列表
5. `GET /api/market/lhb` - 龙虎榜
6. `GET /api/market/chip-race` - 竞价抢筹

**规范文件**:
- OpenAPI 3.0.3: `docs/api/openapi/market-data-api.yaml`
- 完整JSON: `docs/api/openapi/market-data-api-full.json`

**响应格式**:
- 标准: `UnifiedResponse v2.0.0`
- 字段: success, code, message, data, timestamp, request_id, errors

**TypeScript类型**:
- 生成文件: `web/frontend/src/types/market-data-generated.ts`
- 生成工具: openapi-typescript
- 生成命令: `npx openapi-typescript docs/api/openapi/market-data-api.yaml -o web/frontend/src/types/market-data-generated.ts`

**前端服务**:
- API服务: `web/frontend/src/services/marketService.ts`
- 降级服务: `web/frontend/src/services/marketWithFallback.ts`
- 数据适配器: `web/frontend/src/services/adapters/marketAdapter.ts`

**测试状态**:
- 契约验证: ⏳ 待执行
- 类型生成: ⏳ 待执行
- 前端集成: ⏳ 待执行

---

## 版本历史

| 日期 | 契约 | 版本 | 变更说明 |
|------|------|------|----------|
| 2025-12-29 | market-data | 1.0.0 | 初始版本，6个核心端点 |

---

## 变更日志

### market-data 1.0.0 (2025-12-29)

**新增**:
- 市场概览API - 包含指数、涨跌统计、换手率、ETF涨幅榜
- 资金流向API - 主力/散户/大单资金流向
- K线数据API - 支持1m/5m/15m/30m/1h/1d多周期
- ETF列表API - 支持代码/市场/类型筛选
- 龙虎榜API - 涨幅/跌幅/异常波动榜单
- 竞价抢筹API - 开盘抢筹比例和主力vs散户对比

**统一响应格式**:
```typescript
interface UnifiedResponse<T> {
  success: boolean;
  code: number;
  message: string;
  data: T;
  timestamp: string;  // ISO 8601
  request_id: string;
  errors?: ErrorDetail[];
}
```

---

## 下一步计划

1. ✅ 创建market-data-api.yaml契约
2. ⏳ 生成TypeScript类型定义
3. ⏳ 创建前端API服务层
4. ⏳ 实现数据适配器
5. ⏳ 集成到Dashboard组件
6. ⏳ 编写E2E测试

---

**注意**: 当api-contract-sync CLI工具实现后，此文档将迁移到契约管理平台的数据库中。
