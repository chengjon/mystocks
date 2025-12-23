# 问财集成快速参考

## 📋 概述

将AIstock项目的问财筛选功能集成到MyStocks Web后端，作为市场行情模块的扩展功能。

**完整规划文档**: [WENCAI_INTEGRATION_PLAN.md](./WENCAI_INTEGRATION_PLAN.md)

---

## 🎯 核心功能

- ✅ 9个预定义查询语句（技术面、资金流、热度排行等）
- ✅ 问财API数据获取
- ✅ 智能数据清理和去重
- ✅ MySQL存储
- ✅ RESTful API接口
- ✅ 后台任务调度（每日9:00自动刷新）

---

## 📂 新增文件清单

### 核心文件（必须实现）

```
web/backend/app/
├── adapters/
│   └── wencai_adapter.py          # 问财数据源适配器
├── services/
│   └── wencai_service.py          # 问财数据服务
├── models/
│   └── wencai_data.py             # ORM模型
├── schemas/
│   └── wencai_schemas.py          # Pydantic Schema
├── api/
│   └── wencai.py                  # API路由（新文件）
└── tasks/
    └── wencai_tasks.py            # Celery后台任务

web/backend/migrations/
└── wencai_init.sql                # 数据库初始化脚本
```

---

## 🔌 API端点列表

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/market/wencai/queries` | GET | 获取所有可用查询 |
| `/api/market/wencai/query` | POST | 执行指定查询 |
| `/api/market/wencai/results/{query_name}` | GET | 获取查询结果 |
| `/api/market/wencai/refresh/{query_name}` | POST | 刷新查询数据 |
| `/api/market/wencai/history/{query_name}` | GET | 获取历史数据 |

---

## 🗄️ 数据库表

### `wencai_queries` - 查询定义表
存储9个预定义查询的配置信息

### `wencai_qs_1` ~ `wencai_qs_9` - 查询结果表
动态创建，每个查询对应一个表，存储筛选结果

---

## 🔄 实施步骤

### Phase 1: 基础集成（6-8小时）
1. 创建适配器层 (`wencai_adapter.py`)
2. 创建数据模型 (`wencai_data.py`)
3. 创建服务层 (`wencai_service.py`)
4. 创建Schema (`wencai_schemas.py`)
5. 创建API路由 (`wencai.py`)
6. 执行数据库迁移 (`wencai_init.sql`)

### Phase 2: 后台任务（2-3小时）
7. 创建Celery任务 (`wencai_tasks.py`)
8. 配置定时调度

### Phase 3: 测试（3-4小时）
9. 单元测试
10. 集成测试
11. API文档

---

## 🚀 快速开始

### 1. 执行数据库迁移
```bash
mysql -u root -p wencai < web/backend/migrations/wencai_init.sql
```

### 2. 添加环境变量
```env
# .env
WENCAI_TIMEOUT=30
WENCAI_RETRY_COUNT=3
WENCAI_DEFAULT_PAGES=1
WENCAI_AUTO_REFRESH=true
```

### 3. 安装依赖（已包含）
```bash
cd web/backend
pip install -r requirements.txt
```

### 4. 启动后端服务
```bash
uvicorn app.main:app --reload
```

### 5. 测试API
```bash
# 获取所有查询
curl http://localhost:8000/api/market/wencai/queries

# 执行查询
curl -X POST http://localhost:8000/api/market/wencai/query \
  -H "Content-Type: application/json" \
  -d '{"query_name": "qs_9", "pages": 1}'
```

---

## 📊 架构简图

```
前端 → API路由 → 服务层 → 适配器 → 问财API
                    ↓
                 MySQL数据库
                    ↓
                Celery任务调度
```

---

## 🔐 安全和性能

- **限流**: 10次/分钟
- **认证**: 继承JWT认证
- **缓存**: Redis 15分钟缓存
- **异步**: 后台任务处理长查询

---

## 📝 核心代码示例

### 适配器 (`wencai_adapter.py`)
```python
class WencaiDataSource:
    def call_wencai_api(self, query: str, pages: int = 1) -> pd.DataFrame:
        """调用问财API获取数据"""
        # 实现API调用逻辑
```

### 服务 (`wencai_service.py`)
```python
class WencaiService:
    def fetch_and_save(self, query_name: str, pages: int = 1) -> Dict:
        """获取并保存查询结果"""
        # 1. 调用适配器
        # 2. 清理数据
        # 3. 去重
        # 4. 保存到数据库
```

### API路由 (`wencai.py`)
```python
@router.post("/query")
async def execute_query(request: WencaiQueryRequest):
    """执行查询"""
    return await wencai_service.fetch_and_save(
        request.query_name,
        request.pages
    )
```

---

## 📚 9个预定义查询

| 查询 | 说明 |
|------|------|
| qs_1 | 涨停+量比+换手率筛选 |
| qs_2 | 资金流入持续为正 |
| qs_3 | 高换手率 |
| qs_4 | 成交量放量 |
| qs_5 | 新股高换手 |
| qs_6 | 板块资金流向 |
| qs_7 | 低价活跃股 |
| qs_8 | 热度排行 |
| qs_9 | 技术形态筛选（MACD+KDJ金叉） |

---

## ⏱️ 时间估算

- **基础集成**: 6-8小时
- **后台任务**: 2-3小时
- **测试文档**: 3-4小时
- **总计**: 15-21小时

---

## ✅ 验收标准

- [ ] 9个查询均可执行
- [ ] 数据去重正常工作
- [ ] API响应正常
- [ ] 后台任务正常调度
- [ ] 单元测试覆盖率 > 80%

---

## 📞 下一步

1. 阅读完整规划: [WENCAI_INTEGRATION_PLAN.md](./WENCAI_INTEGRATION_PLAN.md)
2. 开始Phase 1: 基础集成
3. 按顺序实现文件清单中的各个模块

---

**创建日期**: 2025-10-17
**文档版本**: 1.0.0
**状态**: ✅ 已完成
