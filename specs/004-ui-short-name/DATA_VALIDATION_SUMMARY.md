# 数据验证总结 - Feature 004

**日期**: 2025-10-26
**状态**: 🔴 发现关键问题

---

## 快速诊断

| 数据实体 | 状态 | 问题等级 | 需要行动 |
|---------|------|---------|---------|
| **FontPreference** | ✅ 正常 | - | 无需修改 |
| **WencaiQuery** | ⚠️ 中等 | P1 | 建议修改前端配置 |
| **WatchlistStock** | 🔴 严重 | **P0** | **必须修复** |

---

## 核心问题

### 🔴 问题1: WatchlistStock缺少category字段

**影响**: **阻塞User Story 3实现**

**Spec需求**:
```
4个选项卡: 用户自选、系统自选、策略自选、监控列表
```

**实际数据库设计**:
```sql
user_watchlist (
  group_id,      -- ✅ 有
  group_name,    -- ✅ 有
  category       -- ❌ 缺失！
)
```

**后果**:
- 无法区分user/system/strategy/monitor四种类型
- API端点无法按category查询
- 前端无法实现4个选项卡功能

---

## 解决方案

### 方案: 添加category字段 (推荐)

#### Step 1: 数据库迁移
```sql
ALTER TABLE watchlist_groups
ADD COLUMN category VARCHAR(20) DEFAULT 'user' NOT NULL
CHECK (category IN ('user', 'system', 'strategy', 'monitor'));

CREATE INDEX idx_groups_user_category ON watchlist_groups(user_id, category);
```

#### Step 2: 新增API端点
```python
@router.get("/")
async def get_watchlist(category: str = Query(...)):
    """按category查询自选股"""
    return service.get_watchlist_by_category(user_id, category)
```

#### Step 3: 前端调用新API
```javascript
// WatchlistTable.vue
const loadData = async () => {
  const response = await dataApi.getWatchlist(props.group) // group = "user"/"system"/...
  tableData.value = response.data
}
```

---

## 实施路径

### 阶段1: 修复WatchlistStock (P0 - 立即执行)

**任务清单**:
- [ ] 执行数据库迁移脚本 (`002_add_watchlist_category.sql`)
- [ ] 修改`watchlist_service.py`添加`get_watchlist_by_category()`
- [ ] 修改`watchlist.py` API添加category查询端点
- [ ] 更新`WatchlistTable.vue`调用新API
- [ ] 执行集成测试

**验收标准**:
- [ ] 4个选项卡可正常切换
- [ ] 每个选项卡显示正确category的股票
- [ ] API响应时间<500ms

### 阶段2: 优化WencaiQuery (P1 - 本周完成)

**任务清单**:
- [ ] 修改前端配置文件，添加`query_text`字段
- [ ] 同步前端配置到数据库
- [ ] 验证9个预设查询正常工作

---

## 详细文档

完整的数据验证报告请查看:
👉 `DATA_VALIDATION_REPORT.md` (23页详细分析)

包含内容:
- 详细的数据模型对比
- 完整的API契约测试清单
- 边界条件测试用例
- 数据迁移脚本
- 回滚方案

---

**报告生成时间**: 2025-10-26
**下一步行动**: 执行数据库迁移修复WatchlistStock
