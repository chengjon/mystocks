# API 响应格式标准化规范

**规范版本**: 1.0
**生效日期**: 2025-11-28
**适用范围**: 所有 FastAPI 后端 API 端点
**维护责任**: 后端开发团队
**目标**: 确保 25+ API 端点响应格式 100% 标准化

---

## 1. 标准化目标

### 当前状态
- **非标准化端点**: 25+ 个 (100%)
- **修复进展**: 2 个端点已修复 (8%)
- **通过率影响**: API 格式不匹配导致 28.6% 的 E2E 测试失败

### 目标状态 (Week 1)
- **标准化端点**: 25+ 个 (100%)
- **测试通过率**: 95%+ (从 82.7% 提升)
- **零格式不匹配**: 0 个测试因格式失败

---

## 2. 标准响应格式模板

### 通用格式 (适用于所有成功响应)

```json
{
  "success": true,
  "code": 0,
  "message": "请求成功",
  "data": {
    "/* 实际数据内容 */"
  },
  "timestamp": "2025-11-28T11:30:00.123456Z",
  "pagination": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  }
}
```

### 字段定义

| 字段 | 类型 | 必需 | 说明 | 示例 |
|------|------|------|------|------|
| `success` | boolean | ✅ 必需 | 请求是否成功 | `true` / `false` |
| `code` | integer | ✅ 必需 | 业务状态码 | 0 (成功), 400 (客户端错误), 500 (服务器错误) |
| `message` | string | 可选 | 消息描述 | "请求成功" / "用户不存在" |
| `data` | object / array | 取决于端点 | 实际数据内容 | 见各端点示例 |
| `timestamp` | string (ISO 8601) | ✅ 必需 | 响应时间戳 | "2025-11-28T11:30:00.123456Z" |
| `pagination` | object | 条件必需 | 分页信息 (仅列表端点) | 见下表 |

### 分页对象格式

```json
{
  "pagination": {
    "total": 100,           // 总记录数
    "page": 1,              // 当前页码 (从 1 开始)
    "page_size": 20,        // 每页记录数
    "total_pages": 5        // 总页数
  }
}
```

**何时包含 pagination 字段**:
- ✅ 包含：任何返回列表/分页数据的端点
- ❌ 不包含：返回单个对象或统计数据的端点

### 错误响应格式

```json
{
  "success": false,
  "code": 400,
  "message": "参数验证失败",
  "data": {
    "errors": [
      {
        "field": "symbol",
        "message": "股票代码不能为空"
      }
    ]
  },
  "timestamp": "2025-11-28T11:30:00.123456Z"
}
```

---

## 3. 端点分类标准化

### 3.1 公告监控 API (`/api/announcement/*`)

#### ✅ 已修复端点

**GET /api/announcement/stats**
```json
{
  "success": true,
  "code": 0,
  "message": "获取统计信息成功",
  "data": {
    "total_count": 1000,
    "today_count": 25,
    "important_count": 5,
    "triggered_count": 2,
    "by_source": {
      "source_a": 500,
      "source_b": 500
    },
    "by_type": {
      "type_1": 600,
      "type_2": 400
    },
    "by_sentiment": {
      "positive": 400,
      "neutral": 400,
      "negative": 200
    }
  },
  "timestamp": "2025-11-28T11:30:00.123456Z"
}
```

#### ⏳ 待修复端点

**GET /api/announcement/list**
```json
{
  "success": true,
  "code": 0,
  "message": "获取公告列表成功",
  "data": [
    {
      "id": 1,
      "announcement_title": "公告标题",
      "stock_code": "000001",
      "announcement_type": "重要事项",
      "importance_level": 3,
      "publish_date": "2025-11-28",
      "content_summary": "公告内容摘要"
    }
  ],
  "pagination": {
    "total": 1000,
    "page": 1,
    "page_size": 20,
    "total_pages": 50
  },
  "timestamp": "2025-11-28T11:30:00.123456Z"
}
```

**GET /api/announcement/today**
```json
{
  "success": true,
  "code": 0,
  "message": "获取今日公告成功",
  "data": [
    {
      "id": 1,
      "announcement_title": "今日公告",
      "stock_code": "000001",
      "importance_level": 3
    }
  ],
  "pagination": {
    "total": 25,
    "page": 1,
    "page_size": 100,
    "total_pages": 1
  },
  "timestamp": "2025-11-28T11:30:00.123456Z"
}
```

**GET /api/announcement/important**
```json
{
  "success": true,
  "code": 0,
  "message": "获取重要公告成功",
  "data": [
    {
      "id": 1,
      "announcement_title": "重要公告",
      "importance_level": 4
    }
  ],
  "pagination": {
    "total": 50,
    "page": 1,
    "page_size": 100,
    "total_pages": 1
  },
  "timestamp": "2025-11-28T11:30:00.123456Z"
}
```

**GET /api/announcement/monitor-rules**
```json
{
  "success": true,
  "code": 0,
  "message": "获取监控规则成功",
  "data": [
    {
      "id": 1,
      "rule_name": "规则名称",
      "stock_codes": ["000001", "000002"],
      "keywords": ["关键词1", "关键词2"],
      "min_importance_level": 3,
      "notify_enabled": true,
      "is_active": true
    }
  ],
  "pagination": null,
  "timestamp": "2025-11-28T11:30:00.123456Z"
}
```

**GET /api/announcement/triggered-records**
```json
{
  "success": true,
  "code": 0,
  "message": "获取触发记录成功",
  "data": [
    {
      "id": 1,
      "rule_id": 1,
      "announcement_id": 1,
      "matched_keywords": ["关键词1"],
      "triggered_at": "2025-11-28T11:30:00Z",
      "notified": true,
      "notified_at": "2025-11-28T11:30:01Z"
    }
  ],
  "pagination": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  },
  "timestamp": "2025-11-28T11:30:00.123456Z"
}
```

---

### 3.2 数据库监控 API (`/api/system/database/*`)

#### ✅ 已修复端点

**GET /api/system/database/stats**
```json
{
  "success": true,
  "code": 0,
  "message": "获取数据库统计成功",
  "data": {
    "connections": {
      "tdengine": {
        "status": "connected",
        "pool_size": 10,
        "active_connections": 5,
        "waiting_connections": 0
      },
      "postgresql": {
        "status": "connected",
        "pool_size": 20,
        "active_connections": 8,
        "waiting_connections": 0
      }
    },
    "tables": {
      "tdengine": {
        "count": 5,
        "classifications": [
          "TICK_DATA",
          "MINUTE_KLINE",
          "ORDER_BOOK_DEPTH",
          "LEVEL2_SNAPSHOT",
          "INDEX_QUOTES"
        ]
      },
      "postgresql": {
        "count": 29,
        "categories": [
          "日线市场数据",
          "参考数据",
          "衍生数据",
          "交易数据",
          "元数据"
        ]
      }
    }
  },
  "timestamp": "2025-11-28T11:30:00.123456Z"
}
```

**GET /api/system/database/health**
```json
{
  "success": true,
  "code": 0,
  "message": "数据库健康检查完成",
  "data": {
    "summary": {
      "total_databases": 2,
      "healthy": 2,
      "unhealthy": 0,
      "status": "all_healthy"
    },
    "databases": {
      "tdengine": {
        "status": "healthy",
        "version": "3.3.0",
        "last_checked": "2025-11-28T11:30:00Z"
      },
      "postgresql": {
        "status": "healthy",
        "version": "17.0",
        "last_checked": "2025-11-28T11:30:00Z"
      }
    }
  },
  "timestamp": "2025-11-28T11:30:00.123456Z"
}
```

---

### 3.3 交易 API (`/api/trade/*`)

**GET /api/trade/portfolio**
```json
{
  "success": true,
  "code": 0,
  "message": "获取投资组合概览成功",
  "data": {
    "total_assets": 1000000,
    "available_cash": 250000,
    "position_value": 750000,
    "total_profit": 50000,
    "profit_rate": 0.05
  },
  "timestamp": "2025-11-28T11:30:00.123456Z"
}
```

**GET /api/trade/positions**
```json
{
  "success": true,
  "code": 0,
  "message": "获取持仓列表成功",
  "data": [
    {
      "id": 1,
      "symbol": "000001",
      "stock_name": "平安银行",
      "quantity": 1000,
      "cost_price": 10.5,
      "current_price": 11.2,
      "position_value": 11200,
      "profit": 700,
      "profit_rate": 0.0667
    }
  ],
  "pagination": null,
  "timestamp": "2025-11-28T11:30:00.123456Z"
}
```

**GET /api/trade/trades**
```json
{
  "success": true,
  "code": 0,
  "message": "获取交易历史成功",
  "data": [
    {
      "id": 1,
      "trade_date": "2025-11-28",
      "trade_type": "buy",
      "symbol": "000001",
      "stock_name": "平安银行",
      "quantity": 100,
      "price": 10.5,
      "trade_amount": 1050,
      "remark": "买入"
    }
  ],
  "pagination": {
    "total": 500,
    "page": 1,
    "page_size": 20,
    "total_pages": 25
  },
  "timestamp": "2025-11-28T11:30:00.123456Z"
}
```

**GET /api/trade/statistics**
```json
{
  "success": true,
  "code": 0,
  "message": "获取交易统计成功",
  "data": {
    "total_trades": 500,
    "buy_count": 250,
    "sell_count": 250,
    "realized_profit": 45000,
    "win_rate": 0.6,
    "average_profit_per_trade": 90
  },
  "timestamp": "2025-11-28T11:30:00.123456Z"
}
```

**POST /api/trade/execute**
```json
{
  "success": true,
  "code": 0,
  "message": "交易执行成功",
  "data": {
    "trade_id": 501,
    "type": "buy",
    "symbol": "000001",
    "quantity": 100,
    "price": 10.5,
    "trade_amount": 1050,
    "status": "completed",
    "executed_at": "2025-11-28T11:30:00Z"
  },
  "timestamp": "2025-11-28T11:30:00.123456Z"
}
```

---

### 3.4 系统 API (`/api/system/*`)

**GET /api/system/health**
```json
{
  "success": true,
  "code": 0,
  "message": "系统健康检查通过",
  "data": {
    "status": "healthy",
    "components": {
      "api": "healthy",
      "database": "healthy",
      "cache": "healthy"
    }
  },
  "timestamp": "2025-11-28T11:30:00.123456Z"
}
```

---

## 4. 实现清单

### Phase 1: 已完成 (2 个端点)
- [x] `/api/announcement/stats` - 添加 `success` 字段
- [x] `/api/system/database/stats` - 添加 `connections` 和 `tables` 字段

### Phase 2: Week 1 优先处理 (需标准化)

#### 公告 API (5 个端点)
- [ ] `/api/announcement/list` - 验证并更新格式
- [ ] `/api/announcement/today` - 验证并更新格式
- [ ] `/api/announcement/important` - 验证并更新格式
- [ ] `/api/announcement/monitor-rules` - 验证并更新格式
- [ ] `/api/announcement/triggered-records` - 验证并更新格式

#### 数据库 API (1 个端点)
- [ ] `/api/system/database/health` - 验证并更新格式

#### 交易 API (6 个端点)
- [ ] `/api/trade/portfolio` - 验证并更新格式
- [ ] `/api/trade/positions` - 验证并更新格式
- [ ] `/api/trade/trades` - 验证并更新格式
- [ ] `/api/trade/statistics` - 验证并更新格式
- [ ] `/api/trade/execute` - 验证并更新格式
- [ ] `/api/trade/health` - 验证并更新格式

#### 系统 API (1 个端点)
- [ ] `/api/system/health` - 验证并更新格式

#### 其他 API (待清单)
- [ ] ... (待补充完整的 25+ 端点列表)

---

## 5. 验证方法

### 自动化验证脚本

```python
# validate_api_standards.py
import requests
import json

STANDARDS = {
    "success": bool,
    "code": int,
    "data": (dict, list, type(None)),
    "timestamp": str,
}

OPTIONAL = {
    "message": str,
    "pagination": dict,
}

def validate_response(url, response_data):
    """验证 API 响应是否符合标准"""
    errors = []

    # 检查必需字段
    for field, expected_type in STANDARDS.items():
        if field not in response_data:
            errors.append(f"缺少必需字段: {field}")
        elif not isinstance(response_data[field], expected_type):
            errors.append(f"字段 {field} 类型错误: 期望 {expected_type}, 实际 {type(response_data[field])}")

    # 检查分页字段
    if isinstance(response_data.get("data"), list) and response_data.get("data"):
        if "pagination" not in response_data:
            errors.append("列表返回必须包含 pagination 字段")

    return errors

# 测试所有端点
endpoints = [
    "http://localhost:8000/api/announcement/stats",
    "http://localhost:8000/api/system/database/stats",
    # ... 更多端点
]

for endpoint in endpoints:
    try:
        response = requests.get(endpoint, timeout=5)
        data = response.json()
        errors = validate_response(endpoint, data)

        if errors:
            print(f"❌ {endpoint}")
            for error in errors:
                print(f"   - {error}")
        else:
            print(f"✅ {endpoint}")
    except Exception as e:
        print(f"❌ {endpoint}: {str(e)}")
```

### 测试验证

```bash
# 运行所有端点标准化验证
python validate_api_standards.py

# 预期输出
# ✅ /api/announcement/stats
# ✅ /api/system/database/stats
# ❌ /api/announcement/list
#    - 缺少 pagination 字段
# ... 更多
```

---

## 6. 迁移指南

### 对于每个需要更新的端点

#### Step 1: 理解当前结构
```python
# 当前代码示例
@router.get("/list")
async def get_list():
    return [
        {"id": 1, "name": "Item 1"},
        {"id": 2, "name": "Item 2"},
    ]
```

#### Step 2: 更新为标准格式
```python
from datetime import datetime, timezone

@router.get("/list")
async def get_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    # 获取数据
    data = [...]
    total = len(data)

    # 返回标准化格式
    return {
        "success": True,
        "code": 0,
        "message": "获取列表成功",
        "data": data,
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
```

#### Step 3: 更新测试期望
```javascript
// 测试代码更新
test('should fetch list with pagination', async ({ page }) => {
  const response = await page.request.get('/api/list?page=1&page_size=20')
  const data = await response.json()

  // 验证标准字段
  expect(data.success).toBe(true)
  expect(data.code).toBe(0)
  expect(data.data).toBeDefined()
  expect(data.pagination).toBeDefined()
  expect(data.pagination.total).toBeGreaterThanOrEqual(0)
  expect(data.timestamp).toBeDefined()
})
```

---

## 7. 质量检查清单

### 部署前检查
- [ ] 所有必需字段都存在
- [ ] 字段类型正确
- [ ] 分页字段正确配置
- [ ] 时间戳格式为 ISO 8601
- [ ] 错误响应格式一致
- [ ] E2E 测试全部通过

### 部署后验证
- [ ] 运行自动化验证脚本
- [ ] 手动测试关键端点
- [ ] 验证 E2E 测试通过率
- [ ] 检查 API 文档更新

---

## 8. 性能影响

### 预期性能变化

| 指标 | 修改前 | 修改后 | 影响 |
|------|--------|--------|------|
| 响应体大小 | 基准 | +5-10% | 轻微增加 (添加元数据) |
| 响应时间 | 基准 | +1-2ms | 轻微增加 (JSON 序列化) |
| 网络传输 | 基准 | 基准 | 无变化 (gzip 压缩) |

### 优化建议
- 启用响应压缩 (gzip/brotli)
- 缓存常用端点的响应
- 使用 CDN 加速静态 API 响应

---

## 9. 文档更新

### 更新项

- [ ] API 文档 (OpenAPI/Swagger)
- [ ] SDK 文档
- [ ] 前端开发指南
- [ ] 测试文档

### 示例: OpenAPI/Swagger 更新

```yaml
components:
  schemas:
    ApiResponse:
      type: object
      required:
        - success
        - code
        - data
        - timestamp
      properties:
        success:
          type: boolean
          description: 请求是否成功
        code:
          type: integer
          description: 业务状态码
        message:
          type: string
          description: 消息描述
        data:
          type: object
          description: 返回数据
        timestamp:
          type: string
          format: date-time
          description: 响应时间戳
        pagination:
          $ref: '#/components/schemas/Pagination'

    Pagination:
      type: object
      properties:
        total:
          type: integer
        page:
          type: integer
        page_size:
          type: integer
        total_pages:
          type: integer
```

---

## 10. 故障排除

### 常见问题

**Q: 为什么需要添加 `success` 字段?**
A: 统一的状态字段使客户端能够统一处理响应，无需检查 HTTP 状态码。

**Q: 什么时候包含 `pagination` 字段?**
A: 仅当返回列表数据时。对于单个对象或统计数据，可以省略。

**Q: 时间戳格式要求?**
A: 必须是 ISO 8601 格式，推荐包含时区: `2025-11-28T11:30:00.123456Z`

**Q: 如何处理错误响应?**
A: 使用相同的格式，但设置 `success: false` 和相应的 `code` 值。

---

## 11. 版本历史

| 版本 | 日期 | 变更 | 状态 |
|------|------|------|------|
| 1.0 | 2025-11-28 | 初版规范 | 现行 |

---

## 12. 相关资源

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [JSON API 标准](https://jsonapi.org/)
- [REST API 最佳实践](https://restfulapi.net/)
- [项目 API 文档](../api/)

---

**规范维护**: 后端开发团队
**最后更新**: 2025-11-28
**下次审查**: 2025-12-05
