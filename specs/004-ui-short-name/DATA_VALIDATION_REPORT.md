# 数据模型与API契约验证报告

**Feature**: 004-ui-short-name (Market Data UI/UX Improvements)
**日期**: 2025-10-26
**架构师**: Database Architecture Team
**状态**: 🔴 发现关键问题

---

## 执行摘要

本报告对Feature 004的3个核心数据实体（FontPreference、WencaiQuery、WatchlistStock）进行了前后端数据格式一致性验证。

**关键发现**:
- ✅ **FontPreference**: 数据一致性良好
- ⚠️ **WencaiQuery**: 存在字段映射差异，需要数据转换层
- 🔴 **WatchlistStock**: **严重数据模型不匹配**，无法满足Spec需求

---

## 1. FontPreference 数据验证 ✅

### 数据模型

```typescript
// 前端: LocalStorage
interface FontPreference {
  fontSize: "12px" | "14px" | "16px" | "18px" | "20px"
}
```

### 存储位置

- **LocalStorage Key**: `user_preferences`
- **Pinia Store**: `web/frontend/src/stores/preferences.ts`
- **应用方式**: CSS变量 `--font-size-base`

### 验证结果

| 验证项 | 状态 | 说明 |
|--------|------|------|
| 数据格式一致性 | ✅ | 前端自管理，无后端依赖 |
| 持久化机制 | ✅ | LocalStorage正常工作 |
| 实时生效 | ✅ | CSS变量即时更新 (FR-015) |
| 跨页面同步 | ✅ | Pinia全局状态管理 |

### 建议

**无需修改** - 设计合理，符合需求。

---

## 2. WencaiQuery 数据验证 ⚠️

### 数据模型对比

#### 前端配置文件 (`wencai-queries.json`)
```json
{
  "version": "1.0",
  "queries": [
    {
      "id": "qs_1",                    // ⚠️ 字符串类型
      "name": "高市值蓝筹股",           // ⚠️ 后端无此字段
      "description": "...",
      "conditions": {                   // ⚠️ 后端无此字段
        "market_cap_min": 100000000000,
        "turnover_rate_min": 0.5,
        "order_by": "market_cap",
        "limit": 50
      }
    }
  ]
}
```

#### 后端数据库模型 (`WencaiQuery`)
```python
class WencaiQuery(Base):
    __tablename__ = 'wencai_queries'

    id = Column(Integer, primary_key=True)        # ⚠️ 整数类型
    query_name = Column(String(20), unique=True)  # "qs_1"
    query_text = Column(Text, nullable=False)     # ⚠️ 前端无此字段
    description = Column(String(255))
    is_active = Column(Boolean, default=True)     # ⚠️ 前端无此字段
    created_at = Column(TIMESTAMP)                # ⚠️ 前端无此字段
    updated_at = Column(TIMESTAMP)                # ⚠️ 前端无此字段
```

#### API响应格式 (`GET /api/market/wencai/queries`)
```python
class WencaiQueryInfo(BaseModel):
    id: int                              # ⚠️ 与前端id类型不一致
    query_name: str                      # "qs_1"
    query_text: str                      # 自然语言查询
    description: Optional[str]
    is_active: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
```

### 字段映射差异表

| 前端字段 | 后端字段 | 类型匹配 | 说明 |
|----------|----------|----------|------|
| id (string) | query_name (string) | ✅ | 语义匹配，但命名不同 |
| - | id (int) | ❌ | 前端无此字段 |
| name | - | ❌ | 后端无对应字段 |
| description | description | ✅ | 完全匹配 |
| conditions (object) | query_text (text) | ❌ | **需要转换层** |
| - | is_active (bool) | ❌ | 前端无此字段 |
| - | created_at | ❌ | 前端无此字段 |
| - | updated_at | ❌ | 前端无此字段 |

### 关键问题

#### 问题1: `conditions` → `query_text` 转换缺失

**前端期望**:
```json
{
  "conditions": {
    "market_cap_min": 100000000000,
    "turnover_rate_min": 0.5
  }
}
```

**后端存储**:
```python
query_text = "市值超过1000亿，流动性好的蓝筹股"  # 自然语言
```

**问题**: 前端的结构化查询条件无法直接转换为问财API的自然语言查询。

**影响**:
- 前端配置文件可能被忽略
- 后端数据库中的9个预设查询可能与前端配置不一致

#### 问题2: `id` 字段类型不一致

- **前端**: `"qs_1"` (字符串)
- **后端**: `1` (整数主键)

**潜在风险**: 前端使用字符串ID查询时需要额外映射。

### 验证结果

| 验证项 | 状态 | 问题 |
|--------|------|------|
| 字段名称一致性 | ⚠️ | `name`字段缺失 |
| 数据类型一致性 | ⚠️ | `id`类型不匹配 |
| 条件对象转换 | 🔴 | `conditions` → `query_text`缺少转换逻辑 |
| API响应完整性 | ✅ | API响应包含所有必要字段 |

### 建议方案

#### 方案A: 前端适配后端 (推荐)

**修改**: `wencai-queries.json`
```json
{
  "queries": [
    {
      "query_name": "qs_1",              // 改用query_name
      "name": "高市值蓝筹股",             // 保留UI显示用
      "query_text": "市值超过1000亿的蓝筹股",  // 添加自然语言查询
      "description": "..."
    }
  ]
}
```

**优点**:
- 与后端API完全对齐
- 无需修改后端代码
- 9个预设查询易于维护

**缺点**: 需要手动维护自然语言查询文本

#### 方案B: 后端添加条件解析器

**修改**: 添加`conditions`字段和解析逻辑
```python
class WencaiQuery(Base):
    query_text = Column(Text)      # 自然语言
    conditions = Column(JSON)      # 结构化条件 (新增)

    def generate_query_text(self):
        """从conditions自动生成query_text"""
        pass
```

**优点**: 前端配置更清晰
**缺点**: 需要实现复杂的条件→自然语言转换器

### 推荐方案

**采用方案A**，理由：
1. 问财API本身使用自然语言查询
2. 结构化条件无法精确表达所有查询场景
3. 实现成本低，维护简单

---

## 3. WatchlistStock 数据验证 🔴 **严重问题**

### Spec需求分析

**User Story 3** (FR-026, FR-027):
> 系统必须使用选项卡样式布局，提供4个选项卡: "用户自选"、"系统自选"、"策略自选"、"监控列表"

**期望数据模型**:
```typescript
interface WatchlistStock {
  symbol: string
  name: string
  category: "user" | "system" | "strategy" | "monitor"  // ⚠️ 关键字段
  groupId: number      // 用于分组高亮
  groupName: string    // 用于分组显示
}
```

### 实际数据库设计

```sql
-- watchlist_groups 表
CREATE TABLE watchlist_groups (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    group_name VARCHAR(100) NOT NULL,  -- "默认分组", "自定义分组名"
    created_at TIMESTAMP,
    UNIQUE(user_id, group_name)
);

-- user_watchlist 表
CREATE TABLE user_watchlist (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    group_id INTEGER REFERENCES watchlist_groups(id),
    stock_code VARCHAR(20) NOT NULL,   -- 映射到symbol
    stock_name VARCHAR(100),           -- 映射到name
    added_at TIMESTAMP,
    notes TEXT,

    -- ❌ 缺少category字段！

    UNIQUE(user_id, group_id, stock_code)
);
```

### API端点分析

#### 现有API
```python
# watchlist.py
@router.get("/", response_model=List[WatchlistItem])
async def get_my_watchlist(user: User):
    """获取当前用户的自选股列表"""
    # ❌ 返回所有自选股，无法按category过滤
    pass

@router.get("/group/{group_id}")
async def get_watchlist_by_group(group_id: int, user: User):
    """按分组ID获取自选股"""
    # ✅ 支持按group_id查询，但不是按category
    pass
```

#### 缺失的API
```python
# ❌ 不存在
@router.get("/")
async def get_watchlist(category: str = Query(...)):
    """按category查询自选股"""
    pass
```

### 前端实现分析

```vue
<!-- WatchlistTabs.vue -->
<template>
  <el-tab-pane name="user" label="用户自选">
    <WatchlistTable :group="user" />  <!-- ⚠️ 传递category作为group -->
  </el-tab-pane>
  <el-tab-pane name="system" label="系统自选">
    <WatchlistTable :group="system" />
  </el-tab-pane>
  <el-tab-pane name="strategy" label="策略自选">
    <WatchlistTable :group="strategy" />
  </el-tab-pane>
  <el-tab-pane name="monitor" label="监控列表">
    <WatchlistTable :group="monitor" />
  </el-tab-pane>
</template>
```

```javascript
// WatchlistTable.vue
props: {
  group: {
    type: String,
    validator: (value) => ['user', 'system', 'strategy', 'monitor'].includes(value)
    // ⚠️ 前端期望category，但后端没有此字段
  }
}

// Mock数据生成器（说明前端目前使用假数据）
const generateMockData = (group) => {
  const groupNames = {
    user: ['分组1', '分组2', '分组3'],
    system: ['系统推荐A', '系统推荐B'],
    strategy: ['价值投资', '成长投资'],
    monitor: ['重点关注', '风险监控']
  }
  // ...
}
```

### 数据模型不匹配矩阵

| 需求层 | 期望字段 | 实际字段 | 状态 |
|--------|----------|----------|------|
| **Spec** | category (user/system/strategy/monitor) | ❌ 无 | 🔴 缺失 |
| **Spec** | groupId (用于同category内分组) | ✅ group_id | ✅ 匹配 |
| **Spec** | groupName (用于高亮显示) | ✅ group_name | ✅ 匹配 |
| **前端** | symbol | stock_code | ⚠️ 需映射 |
| **前端** | name | stock_name | ⚠️ 需映射 |
| **API** | WatchlistItem.symbol | ✅ 已映射 | ✅ 匹配 |
| **API** | WatchlistItem.display_name | ✅ 已映射 | ✅ 匹配 |

### 关键问题

#### 🔴 问题1: 缺少`category`字段

**影响范围**: **阻塞User Story 3实现**

**问题描述**:
- 数据库设计中没有category字段来区分user/system/strategy/monitor
- 无法实现Spec要求的4个选项卡功能
- 前端目前使用mock数据，无法连接真实后端

**根因分析**:
数据库设计采用了`group_id + group_name`的单层分组设计，而Spec需求是**双层分组**:
1. **第一层**: category (user/system/strategy/monitor) - 选项卡级别
2. **第二层**: group (分组1/分组2/...) - 组内高亮级别

**示例**:
```
用户自选 (category=user)
  ├─ 分组1 (group_name="分组1")  ← 高亮颜色A
  │   ├─ 600519 贵州茅台
  │   └─ 000858 五粮液
  └─ 分组2 (group_name="分组2")  ← 高亮颜色B
      └─ 600036 招商银行

系统自选 (category=system)
  └─ 系统推荐A (group_name="系统推荐A")  ← 高亮颜色C
      └─ 601318 中国平安
```

#### 🔴 问题2: API端点缺失

**缺少的API**:
```python
GET /api/watchlist?category=user      # 获取用户自选
GET /api/watchlist?category=system    # 获取系统自选
GET /api/watchlist?category=strategy  # 获取策略自选
GET /api/watchlist?category=monitor   # 获取监控列表
```

**现有API的局限**:
```python
GET /api/watchlist/               # 返回所有自选股（无法区分category）
GET /api/watchlist/group/{id}     # 按group_id查询（不是按category）
```

### 验证结果

| 验证项 | 状态 | 问题 |
|--------|------|------|
| 数据库schema完整性 | 🔴 | 缺少category字段 |
| API端点完整性 | 🔴 | 缺少按category查询的端点 |
| 前后端数据格式一致性 | 🔴 | 前端期望category，后端无此概念 |
| 字段名映射 | ⚠️ | symbol/stock_code需通过API层映射 |
| 分组高亮功能可行性 | ✅ | group_id/group_name支持 |

### 解决方案对比

#### 方案A: 添加category字段 (推荐)

**数据库迁移**:
```sql
-- 1. 为watchlist_groups添加category字段
ALTER TABLE watchlist_groups
ADD COLUMN category VARCHAR(20) DEFAULT 'user'
CHECK (category IN ('user', 'system', 'strategy', 'monitor'));

-- 2. 创建category索引
CREATE INDEX idx_groups_user_category ON watchlist_groups(user_id, category);

-- 3. 更新唯一约束
ALTER TABLE watchlist_groups
DROP CONSTRAINT watchlist_groups_user_id_group_name_key;

ALTER TABLE watchlist_groups
ADD CONSTRAINT watchlist_groups_unique_category_group
UNIQUE(user_id, category, group_name);
```

**API修改**:
```python
# 新增API端点
@router.get("/")
async def get_watchlist(
    category: str = Query(..., regex="^(user|system|strategy|monitor)$"),
    user: User = Depends(get_current_user)
):
    """按category获取自选股列表"""
    service = get_watchlist_service()
    return service.get_watchlist_by_category(user.id, category)
```

**Service修改**:
```python
def get_watchlist_by_category(self, user_id: int, category: str) -> List[Dict]:
    """按category查询自选股"""
    with self._get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            select_sql = """
            SELECT w.*, g.group_name, g.category
            FROM user_watchlist w
            JOIN watchlist_groups g ON w.group_id = g.id
            WHERE g.user_id = %s AND g.category = %s
            ORDER BY w.added_at DESC
            """
            cur.execute(select_sql, (user_id, category))
            rows = cur.fetchall()
            return [serialize_row(dict(row)) for row in rows]
```

**优点**:
- ✅ 完全满足Spec需求
- ✅ 支持双层分组（category + group）
- ✅ 数据库设计清晰，易于查询
- ✅ 前端无需修改组件逻辑

**缺点**:
- ⚠️ 需要数据库迁移
- ⚠️ 需要修改后端Service和API

**实施步骤**:
1. 编写数据库迁移脚本
2. 修改watchlist_service.py添加category支持
3. 修改watchlist.py API添加category查询端点
4. 前端修改WatchlistTable组件调用新API
5. 执行集成测试验证

#### 方案B: 使用group_name约定 (不推荐)

**思路**: 不添加category字段，而是通过group_name的命名约定来区分category

```python
# group_name约定规则
{
  "user_分组1": category=user,
  "user_分组2": category=user,
  "system_推荐A": category=system,
  "strategy_价值": category=strategy,
  "monitor_关注": category=monitor
}
```

**优点**:
- ✅ 无需数据库迁移

**缺点**:
- 🔴 依赖命名约定，容易出错
- 🔴 查询性能差（需要LIKE匹配）
- 🔴 用户体验差（group_name包含前缀）
- 🔴 维护困难，不符合数据库设计规范

**结论**: **不推荐此方案**

#### 方案C: 前端本地映射 (临时方案)

**思路**: 前端维护一个group_id → category的映射表

```typescript
// 前端映射配置
const categoryMapping = {
  1: 'user',      // group_id=1 → 用户自选
  2: 'user',
  3: 'system',    // group_id=3 → 系统自选
  4: 'strategy',
  5: 'monitor'
}
```

**优点**:
- ✅ 无需后端修改

**缺点**:
- 🔴 硬编码group_id，不灵活
- 🔴 多用户环境下group_id冲突
- 🔴 无法动态添加分组
- 🔴 违反数据驱动原则

**结论**: **仅作为临时方案，不适合生产环境**

### 推荐方案

**强烈推荐采用方案A**，理由：

1. **符合需求**: 完全满足Spec中的4个选项卡需求
2. **数据完整性**: 通过数据库约束确保category的有效性
3. **查询性能**: 通过索引支持高效的category查询
4. **可扩展性**: 未来可轻松添加新的category类型
5. **维护性**: 数据库设计清晰，业务逻辑简单

### 数据迁移脚本

```sql
-- File: /opt/claude/mystocks_spec/web/backend/migrations/add_category_to_watchlist.sql
-- Description: Add category field to support 4-tab watchlist layout

BEGIN;

-- Step 1: Add category column
ALTER TABLE watchlist_groups
ADD COLUMN category VARCHAR(20) DEFAULT 'user' NOT NULL;

-- Step 2: Add CHECK constraint
ALTER TABLE watchlist_groups
ADD CONSTRAINT check_category_valid
CHECK (category IN ('user', 'system', 'strategy', 'monitor'));

-- Step 3: Create index for efficient category filtering
CREATE INDEX idx_groups_user_category ON watchlist_groups(user_id, category);

-- Step 4: Update UNIQUE constraint to include category
ALTER TABLE watchlist_groups
DROP CONSTRAINT IF EXISTS watchlist_groups_user_id_group_name_key;

ALTER TABLE watchlist_groups
ADD CONSTRAINT watchlist_groups_unique_category_group
UNIQUE(user_id, category, group_name);

-- Step 5: Create default groups for existing users (if any)
-- This assumes user_id=1 exists; adjust as needed
INSERT INTO watchlist_groups (user_id, category, group_name)
VALUES
    (1, 'user', '默认分组'),
    (1, 'system', '系统推荐'),
    (1, 'strategy', '策略自选'),
    (1, 'monitor', '监控列表')
ON CONFLICT DO NOTHING;

COMMIT;
```

---

## 4. API契约测试任务

### 4.1 WencaiQuery API测试

#### 测试场景1: 获取所有查询列表
```bash
# Request
GET /api/market/wencai/queries
Authorization: Bearer {token}

# Expected Response (200 OK)
{
  "queries": [
    {
      "id": 1,
      "query_name": "qs_1",
      "query_text": "市值超过1000亿的蓝筹股",
      "description": "高市值蓝筹股",
      "is_active": true,
      "created_at": "2025-10-17T09:00:00",
      "updated_at": "2025-10-17T09:00:00"
    },
    ...
  ],
  "total": 9
}

# Validation Points:
✅ total应等于9（qs_1到qs_9）
✅ 每个query_name应匹配正则: ^qs_[1-9]$
✅ 所有is_active应为true
✅ created_at和updated_at应为有效ISO8601时间戳
```

#### 测试场景2: 执行预设查询
```bash
# Request
POST /api/market/wencai/query
Content-Type: application/json
{
  "query_name": "qs_9",
  "pages": 1
}

# Expected Response (200 OK)
{
  "success": true,
  "message": "查询执行成功",
  "query_name": "qs_9",
  "total_records": 45,
  "new_records": 12,
  "duplicate_records": 33,
  "table_name": "wencai_qs_9",
  "fetch_time": "2025-10-26T10:30:00"
}

# Validation Points:
✅ total_records = new_records + duplicate_records
✅ table_name应为"wencai_qs_9"
✅ fetch_time应为最近时间戳（与当前时间差<5分钟）
```

#### 测试场景3: 获取查询结果
```bash
# Request
GET /api/market/wencai/results/qs_9?limit=10&offset=0

# Expected Response (200 OK)
{
  "query_name": "qs_9",
  "total": 45,
  "results": [
    {
      "股票代码": "000001",
      "股票简称": "平安银行",
      "ROE": "16.5%",
      "fetch_time": "2025-10-26T10:30:00"
    },
    ...
  ],
  "columns": ["股票代码", "股票简称", "ROE", "fetch_time"],
  "latest_fetch_time": "2025-10-26T10:30:00"
}

# Validation Points:
✅ results.length应等于min(limit, total)
✅ columns数组应包含所有results中的字段
✅ latest_fetch_time应与results[0].fetch_time匹配
```

#### 边界条件测试
```bash
# Case 1: 无效的query_name
POST /api/market/wencai/query
{"query_name": "qs_10", "pages": 1}
Expected: 400 Bad Request
Error: "query_name must be in format 'qs_N' where N is 1-9"

# Case 2: pages超出范围
POST /api/market/wencai/query
{"query_name": "qs_1", "pages": 20}
Expected: 422 Unprocessable Entity
Error: "pages must be between 1 and 10"

# Case 3: 查询不存在的结果
GET /api/market/wencai/results/qs_999
Expected: 404 Not Found
```

### 4.2 WatchlistStock API测试

#### 测试场景1: 获取所有自选股
```bash
# Request (现有API)
GET /api/watchlist/
Authorization: Bearer {token}

# Current Response
[
  {
    "id": 1,
    "stock_code": "600519",
    "stock_name": "贵州茅台",
    "added_at": "2025-10-20T15:30:00",
    "notes": "重点关注"
  }
]

# ❌ Problem: 无法区分category
```

#### 测试场景2: 按category获取自选股 (需实现)
```bash
# Request (新API - 需实现)
GET /api/watchlist?category=user
Authorization: Bearer {token}

# Expected Response (200 OK)
[
  {
    "id": 1,
    "symbol": "600519",           # 映射自stock_code
    "name": "贵州茅台",            # 映射自stock_name
    "category": "user",           # 新增字段
    "group_id": 1,
    "group_name": "分组1",
    "latest_price": 1680.50,
    "change_percent": 1.23,
    "added_at": "2025-10-20T15:30:00",
    "notes": "重点关注"
  }
]

# Validation Points:
✅ 所有记录的category应等于"user"
✅ group_name应有明确值（不为空）
✅ symbol和name应正确映射
```

#### 测试场景3: 按分组获取自选股
```bash
# Request
GET /api/watchlist/group/1
Authorization: Bearer {token}

# Expected Response
[
  {
    "id": 1,
    "symbol": "600519",
    "name": "贵州茅台",
    "group_id": 1,
    "group_name": "分组1"
  }
]

# Validation Points:
✅ 所有记录的group_id应等于1
✅ group_name应一致
```

#### 边界条件测试
```bash
# Case 1: 空自选股列表
GET /api/watchlist?category=system
Expected: 200 OK
Response: []

# Case 2: 无效的category
GET /api/watchlist?category=invalid
Expected: 422 Unprocessable Entity
Error: "category must be one of: user, system, strategy, monitor"

# Case 3: 大数据量分页
GET /api/watchlist?category=user&limit=1000
Expected: 200 OK
Validation: 验证响应时间<2秒，记录数≤1000
```

---

## 5. 边界条件测试清单

### 5.1 空数据场景

| 测试项 | API | 输入 | 期望输出 | 验证点 |
|--------|-----|------|----------|--------|
| 空自选股列表 | GET /api/watchlist?category=user | user_id=新用户 | `[]` | ✅ 空数组，不报错 |
| 空问财结果 | GET /api/market/wencai/results/qs_1 | 数据库无结果 | `{"total": 0, "results": []}` | ✅ total=0 |
| 空分组 | GET /api/watchlist/groups | 用户无分组 | `[]` | ✅ 空数组 |

### 5.2 大数据量场景

| 测试项 | 数据量 | 期望性能 | 验证点 |
|--------|--------|----------|--------|
| 自选股分页 | 1000条 | <2秒 | ✅ 分页正常，前端渲染流畅 |
| 问财查询结果 | 500条 | <3秒 | ✅ 分页控件自动显示 |
| 筛选操作 | 5000条 | <5秒 | ✅ 前端分页不卡顿 |

**压力测试脚本**:
```python
# 生成测试数据
import psycopg2

conn = psycopg2.connect("postgresql://mystocks@localhost/mystocks")
cur = conn.cursor()

# 插入1000条自选股
for i in range(1000):
    cur.execute("""
        INSERT INTO user_watchlist (user_id, group_id, stock_code, stock_name)
        VALUES (1, 1, %s, %s)
    """, (f"60{i:04d}", f"测试股票{i}"))

conn.commit()
```

### 5.3 错误响应处理

| 错误类型 | 触发条件 | HTTP状态码 | 前端处理 |
|----------|----------|------------|----------|
| 404 Not Found | 查询不存在的query_name | 404 | ✅ 显示"查询不存在" |
| 500 Internal Error | 数据库连接失败 | 500 | ✅ 显示"服务器错误，请稍后重试" |
| 401 Unauthorized | token过期 | 401 | ✅ 重定向到登录页 |
| 422 Validation Error | 无效的category参数 | 422 | ✅ 显示参数错误提示 |
| Network Timeout | 请求超时(>30s) | - | ✅ 显示"网络超时" |

**前端错误处理验证**:
```javascript
// 验证点: 前端应该有统一的错误处理
try {
  const res = await dataApi.getWatchlist('invalid_category')
} catch (error) {
  if (error.response.status === 422) {
    ElMessage.error('参数错误')  // ✅ 应该显示友好错误信息
  }
}
```

---

## 6. 数据迁移任务

### 6.1 是否需要迁移?

| 实体 | 迁移需求 | 优先级 | 理由 |
|------|----------|--------|------|
| FontPreference | ❌ 否 | - | 纯前端LocalStorage |
| WencaiQuery | ⚠️ 可选 | P2 | 建议同步前端配置到数据库 |
| WatchlistStock | ✅ **必须** | P0 | **阻塞User Story 3** |

### 6.2 Watchlist数据迁移方案

#### 迁移脚本

```sql
-- File: web/backend/migrations/002_add_watchlist_category.sql
-- Description: Add category field to support 4-tab watchlist layout
-- Author: Database Architecture Team
-- Date: 2025-10-26

-- ============================================
-- Phase 1: Schema Modification
-- ============================================

BEGIN;

-- 1.1 Add category column with default value
ALTER TABLE watchlist_groups
ADD COLUMN category VARCHAR(20) DEFAULT 'user' NOT NULL;

-- 1.2 Add CHECK constraint for valid categories
ALTER TABLE watchlist_groups
ADD CONSTRAINT check_category_valid
CHECK (category IN ('user', 'system', 'strategy', 'monitor'));

-- 1.3 Create index for efficient category filtering
CREATE INDEX idx_groups_user_category ON watchlist_groups(user_id, category);

-- 1.4 Update UNIQUE constraint
ALTER TABLE watchlist_groups
DROP CONSTRAINT IF EXISTS watchlist_groups_user_id_group_name_key;

ALTER TABLE watchlist_groups
ADD CONSTRAINT watchlist_groups_unique_category_group
UNIQUE(user_id, category, group_name);

COMMIT;

-- ============================================
-- Phase 2: Data Migration
-- ============================================

BEGIN;

-- 2.1 Update existing groups to 'user' category (already set by DEFAULT)
-- No action needed

-- 2.2 Create default groups for other categories for each user
INSERT INTO watchlist_groups (user_id, category, group_name)
SELECT DISTINCT user_id, 'system', '系统推荐'
FROM watchlist_groups
ON CONFLICT DO NOTHING;

INSERT INTO watchlist_groups (user_id, category, group_name)
SELECT DISTINCT user_id, 'strategy', '策略自选'
FROM watchlist_groups
ON CONFLICT DO NOTHING;

INSERT INTO watchlist_groups (user_id, category, group_name)
SELECT DISTINCT user_id, 'monitor', '监控列表'
FROM watchlist_groups
ON CONFLICT DO NOTHING;

COMMIT;

-- ============================================
-- Phase 3: Validation
-- ============================================

-- Verify all groups have valid categories
SELECT category, COUNT(*)
FROM watchlist_groups
GROUP BY category;

-- Expected output:
-- category  | count
-- ----------+-------
-- user      | N
-- system    | M
-- strategy  | M
-- monitor   | M
```

#### 迁移验证检查

```sql
-- Check 1: All groups have valid categories
SELECT COUNT(*) FROM watchlist_groups
WHERE category NOT IN ('user', 'system', 'strategy', 'monitor');
-- Expected: 0

-- Check 2: Each user has default groups for all categories
SELECT user_id, category, COUNT(*)
FROM watchlist_groups
GROUP BY user_id, category
ORDER BY user_id, category;
-- Expected: Each user should have at least 1 group per category

-- Check 3: No duplicate (user_id, category, group_name) combinations
SELECT user_id, category, group_name, COUNT(*)
FROM watchlist_groups
GROUP BY user_id, category, group_name
HAVING COUNT(*) > 1;
-- Expected: 0 rows
```

#### 回滚脚本

```sql
-- File: web/backend/migrations/002_add_watchlist_category_rollback.sql
-- Description: Rollback category field addition

BEGIN;

-- Remove new constraints
ALTER TABLE watchlist_groups
DROP CONSTRAINT IF EXISTS check_category_valid;

ALTER TABLE watchlist_groups
DROP CONSTRAINT IF EXISTS watchlist_groups_unique_category_group;

-- Remove index
DROP INDEX IF EXISTS idx_groups_user_category;

-- Restore original UNIQUE constraint
ALTER TABLE watchlist_groups
ADD CONSTRAINT watchlist_groups_user_id_group_name_key
UNIQUE(user_id, group_name);

-- Remove category column
ALTER TABLE watchlist_groups
DROP COLUMN IF EXISTS category;

COMMIT;
```

### 6.3 Wencai查询数据同步 (可选)

**目标**: 将前端配置文件`wencai-queries.json`中的9个查询同步到数据库

```python
# File: web/backend/scripts/sync_wencai_queries.py
import json
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.wencai_data import WencaiQuery

def sync_wencai_queries():
    """同步前端配置到数据库"""

    # 1. Load frontend config
    with open('web/frontend/src/config/wencai-queries.json', 'r', encoding='utf-8') as f:
        config = json.load(f)

    # 2. Connect to database
    db: Session = SessionLocal()

    try:
        for query in config['queries']:
            # 3. Convert conditions to natural language query_text
            # TODO: Implement conditions → query_text conversion
            query_text = f"{query['name']} - {query['description']}"

            # 4. Upsert query
            db_query = db.query(WencaiQuery).filter(
                WencaiQuery.query_name == query['id']
            ).first()

            if db_query:
                db_query.query_text = query_text
                db_query.description = query['description']
            else:
                db_query = WencaiQuery(
                    query_name=query['id'],
                    query_text=query_text,
                    description=query['description'],
                    is_active=True
                )
                db.add(db_query)

        db.commit()
        print(f"✅ Synced {len(config['queries'])} queries to database")

    except Exception as e:
        db.rollback()
        print(f"❌ Sync failed: {e}")
    finally:
        db.close()

if __name__ == '__main__':
    sync_wencai_queries()
```

---

## 7. 总结与建议

### 7.1 关键问题汇总

| 实体 | 问题等级 | 问题描述 | 影响 | 优先级 |
|------|----------|----------|------|--------|
| **WatchlistStock** | 🔴 **严重** | 缺少category字段 | 阻塞US3实现 | **P0** |
| **WatchlistStock** | 🔴 **严重** | API端点缺失 | 前端无法获取数据 | **P0** |
| **WencaiQuery** | ⚠️ 中等 | 前后端字段映射不一致 | 配置文件可能被忽略 | P1 |
| **WencaiQuery** | ⚠️ 中等 | conditions无法转换为query_text | 功能实现不完整 | P2 |
| **FontPreference** | ✅ 正常 | 无问题 | 无影响 | - |

### 7.2 推荐实施路径

#### 阶段1: 修复WatchlistStock (P0 - 立即执行)

**任务清单**:
1. ✅ 编写数据库迁移脚本 (`002_add_watchlist_category.sql`)
2. ✅ 在测试环境执行迁移并验证
3. ✅ 修改`watchlist_service.py`添加`get_watchlist_by_category()`方法
4. ✅ 修改`watchlist.py` API添加category查询端点
5. ✅ 更新`WatchlistTable.vue`调用新API
6. ✅ 执行集成测试
7. ✅ 在生产环境执行迁移

**验收标准**:
- [ ] 4个选项卡可正常切换
- [ ] 每个选项卡显示正确category的股票
- [ ] 同一选项卡内按group_name高亮显示
- [ ] API响应时间<500ms

#### 阶段2: 优化WencaiQuery (P1 - 本周完成)

**任务清单**:
1. ✅ 修改前端配置文件，添加`query_text`字段
2. ✅ 编写同步脚本`sync_wencai_queries.py`
3. ✅ 执行同步，确保数据库与前端配置一致
4. ✅ 验证API返回的query信息与前端配置匹配

**验收标准**:
- [ ] 9个预设查询可正常执行
- [ ] 查询结果正确显示在右侧面板
- [ ] 前端配置与数据库数据一致

#### 阶段3: 边界条件测试 (P2 - 下周完成)

**任务清单**:
1. ✅ 执行空数据场景测试
2. ✅ 执行大数据量性能测试
3. ✅ 执行错误响应处理测试
4. ✅ 编写自动化测试脚本

### 7.3 风险评估

| 风险项 | 概率 | 影响 | 缓解措施 |
|--------|------|------|----------|
| 数据库迁移失败 | 低 | 高 | 1. 先在测试环境验证<br>2. 准备回滚脚本<br>3. 备份生产数据 |
| API性能下降 | 中 | 中 | 1. 添加category索引<br>2. 实施缓存策略<br>3. 监控查询性能 |
| 前端兼容性问题 | 低 | 中 | 1. 保持API向后兼容<br>2. 渐进式迁移 |
| 数据一致性问题 | 低 | 高 | 1. 添加数据库约束<br>2. 后端数据验证<br>3. 定期数据审计 |

### 7.4 最终建议

#### 立即行动项 (本周必须完成):
1. ✅ **执行Watchlist数据库迁移** (阻塞US3)
2. ✅ **实现按category查询的API端点**
3. ✅ **修改前端WatchlistTable组件**

#### 后续优化项 (下周完成):
1. ⚠️ 同步Wencai前端配置到数据库
2. ⚠️ 编写完整的集成测试套件
3. ⚠️ 添加API性能监控

#### 长期改进项 (迭代优化):
1. 实现条件对象→自然语言的智能转换器
2. 添加实时数据同步机制
3. 优化大数据量查询性能

---

## 附录A: 完整测试清单

### A.1 FontPreference测试

- [X] LocalStorage读写测试
- [X] CSS变量应用测试
- [X] 跨页面同步测试
- [X] 浏览器兼容性测试 (Chrome, Firefox, Edge)

### A.2 WencaiQuery测试

- [ ] GET /api/market/wencai/queries - 获取所有查询
- [ ] GET /api/market/wencai/queries/{name} - 获取单个查询
- [ ] POST /api/market/wencai/query - 执行查询
- [ ] GET /api/market/wencai/results/{name} - 获取结果
- [ ] POST /api/market/wencai/custom-query - 自定义查询
- [ ] 边界条件: 无效query_name
- [ ] 边界条件: pages超出范围
- [ ] 边界条件: 查询结果为空

### A.3 WatchlistStock测试

- [ ] GET /api/watchlist?category=user - 获取用户自选
- [ ] GET /api/watchlist?category=system - 获取系统自选
- [ ] GET /api/watchlist?category=strategy - 获取策略自选
- [ ] GET /api/watchlist?category=monitor - 获取监控列表
- [ ] GET /api/watchlist/group/{id} - 按分组查询
- [ ] POST /api/watchlist/add - 添加自选股
- [ ] DELETE /api/watchlist/remove/{symbol} - 删除自选股
- [ ] 边界条件: 无效category
- [ ] 边界条件: 空自选股列表
- [ ] 边界条件: 1000+条自选股分页

---

## 附录B: 数据库Schema对比

### B.1 迁移前
```sql
CREATE TABLE watchlist_groups (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    group_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, group_name)
);
```

### B.2 迁移后
```sql
CREATE TABLE watchlist_groups (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    category VARCHAR(20) DEFAULT 'user' NOT NULL,  -- 新增
    group_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT check_category_valid
        CHECK (category IN ('user', 'system', 'strategy', 'monitor')),

    UNIQUE(user_id, category, group_name)  -- 修改
);

CREATE INDEX idx_groups_user_category ON watchlist_groups(user_id, category);  -- 新增
```

---

**报告结束**

如有疑问，请联系数据库架构团队。
