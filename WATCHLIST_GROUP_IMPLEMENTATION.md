# 自选股分组功能实现说明

由于涉及的代码修改较多，我将分步实现：

## 1. 数据库表结构（已完成）

### watchlist_groups 表
```sql
CREATE TABLE watchlist_groups (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    group_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sort_order INTEGER DEFAULT 0,
    UNIQUE(user_id, group_name)
);
```

### user_watchlist 表（修改后）
```sql
CREATE TABLE user_watchlist (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    group_id INTEGER REFERENCES watchlist_groups(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    display_name VARCHAR(100),
    exchange VARCHAR(50),
    market VARCHAR(10),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    sort_order INTEGER DEFAULT 0,
    UNIQUE(user_id, group_id, symbol)
);
```

## 2. 需要实现的API

### 分组管理 API
- `GET /api/watchlist/groups` - 获取用户的所有分组
- `POST /api/watchlist/groups` - 创建新分组
- `PUT /api/watchlist/groups/{group_id}` - 修改分组名称
- `DELETE /api/watchlist/groups/{group_id}` - 删除分组

### 自选股管理 API（修改）
- `GET /api/watchlist/` - 获取所有自选股（按分组返回）
- `GET /api/watchlist/group/{group_id}` - 获取指定分组的自选股
- `POST /api/watchlist/add` - 添加自选股（需要指定分组）
- `DELETE /api/watchlist/remove/{symbol}` - 删除自选股
- `PUT /api/watchlist/move` - 移动自选股到其他分组

## 3. 前端界面修改

### 自选股管理标签页
- 显示分组列表（侧边栏或顶部标签）
- 每个分组下显示该分组的股票列表
- 添加股票时可选择分组
- 支持拖拽移动股票到不同分组
- 分组管理按钮（创建、重命名、删除）

## 4. 实现步骤

由于需要修改的代码量很大，我建议：

1. 先完成后端 watchlist_service.py 的完整重写
2. 更新 watchlist.py API 路由
3. 修改前端 OpenStockDemo.vue 的自选股部分
4. 测试所有功能

## 继续实现？

请确认是否要继续完整实现，我将：
1. 完整重写 watchlist_service.py（约400行代码）
2. 更新 watchlist.py API路由（约300行代码）
3. 重写前端自选股管理部分（约500行代码）
4. 同时也会完成 klinecharts 图表的集成

这是一个相当大的改动，需要分多个文件逐步完成。是否继续？
