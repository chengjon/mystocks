# 问财股票筛选器 V2 功能更新总结

## 📋 更新日期
2025-10-18

## 🎯 需求概述

用户提出的4个主要改进需求：

1. 增加自定义查询输入框
2. 将卡片布局改为树形结构
3. 优化表格显示（列名、格式、新增列）
4. 显示查询语句详细内容

## ✅ 已实现功能

### 1. 自定义查询功能 ✅

**功能描述**：
- 在标题下方新增输入框，接受用户输入的自然语言查询
- 输入框右侧有"查询"按钮
- 返回结果格式与预定义查询(qs_1-qs_9)一致

**实现细节**：
- **前端组件**：`WencaiPanelV2.vue`
  - 输入框最大长度：500字符
  - 带字数统计
  - 支持清空按钮
  - 查询按钮loading状态

- **后端API**：
  - 端点：`POST /api/market/wencai/custom-query`
  - Schema：`WencaiCustomQueryRequest`
  - 响应：`WencaiCustomQueryResponse`
  - 特点：实时查询，不保存到数据库

**使用示例**：
```
输入：请列出今天涨幅超过5%的股票
输入：量比大于2且换手率大于5%的股票
输入：最近5天有涨停的创业板股票
```

### 2. 树形结构布局 ✅

**功能描述**：
- 左侧使用 Element Plus Tree 组件
- 包含4个顶级目录：
  - 默认查询（包含 qs_1 到 qs_9）
  - 分组 A（用户自定义）
  - 分组 B（用户自定义）
  - 分组 C（用户自定义）

**实现细节**：
- 文件夹图标（Folder）+ 文档图标（Document）
- 点击查询节点：显示查询语句（不执行）
- 鼠标悬停：显示"执行"按钮
- 点击"执行"：实际执行查询

**UI特点**：
- 默认全部展开
- 高亮当前选中节点
- 操作按钮仅在悬停时显示

### 3. 优化的表格显示 ✅

**列显示优化**：

| 原始列名 | 新列名 | 宽度 | 对齐 | 格式 | 说明 |
|---------|--------|------|------|------|------|
| - | 序号 | 80px | 居中 | 整数 | 新增，自增 |
| 股票代码 | 股票代码 | 100px | 居中 | - | 保留 |
| 股票简称 | 股票简称 | 120px | 居中 | - | 保留 |
| 最新价 | 最新价 | 100px | 右对齐 | 3位小数 | 格式化 |
| 最新涨跌幅 | 涨跌幅 | 100px | 右对齐 | 2位小数+% | 改名+格式化+颜色 |
| 涨停次数 | 涨停次数 | 100px | 居中 | - | 保留 |
| 量比 | 量比 | 100px | 右对齐 | 3位小数 | 格式化 |
| 换手率 | 换手率 | 100px | 右对齐 | 3位小数 | 格式化 |
| 振幅 | 振幅 | 100px | 右对齐 | 3位小数 | 格式化 |
| - | 查询日期 | 120px | 居中 | YYYY/MM/DD | 新增 |
| - | 操作 | 120px | 居中 | 按钮 | 新增，固定右侧 |

**删除的列**：
- ❌ 代码（与股票代码重复）
- ❌ 名称（与股票简称重复）
- ❌ a股市值(不含限售股)
- ❌ market_code

**格式化规则**：
- 字体大小：14px（比V1大）
- 表头背景：#f5f7fa
- 涨跌幅颜色：
  - 正数：红色 (#f56c6c)
  - 负数：绿色 (#67c23a)
  - 零：默认
- 数值对齐：右对齐
- 文本对齐：居中

### 4. 查询语句显示 ✅

**功能描述**：
- 在表格上方显示完整查询语句
- 使用 Element Plus Tag 组件
- 背景色：#f5f7fa

**显示时机**：
1. 点击树形节点查询时
2. 执行预定义查询后
3. 执行自定义查询后

**格式**：
```
[查询语句：请列举出20天内出现过涨停板，且今日涨幅大于3%的股票]
```

### 5. 加入分组功能 ✅

**功能描述**：
- 每行数据有"加入分组"按钮
- 点击后弹出对话框
- 可选择4个分组：默认、分组A、分组B、分组C

**实现细节**：
- **UI实现**：完成 ✅
- **数据持久化**：未实现（下个版本）

**对话框内容**：
- 显示股票代码和简称
- 分组下拉选择器
- 确定/取消按钮

## 🔧 技术实现

### 后端改动

#### 1. 新增 Schema
```python
# app/schemas/wencai_schemas.py

class WencaiCustomQueryRequest(BaseModel):
    query_text: str  # 5-500字符
    pages: int  # 1-5页

class WencaiCustomQueryResponse(BaseModel):
    success: bool
    message: str
    query_text: str
    total_records: int
    results: List[Dict[str, Any]]
    columns: List[str]
    fetch_time: datetime
```

#### 2. 新增 API 端点
```python
# app/api/wencai.py

@router.post("/custom-query")
async def execute_custom_query(
    request: WencaiCustomQueryRequest,
    db: Session = Depends(get_db)
) -> WencaiCustomQueryResponse:
    # 直接调用适配器，不保存到数据库
    service = WencaiService(db=db)
    df = service.adapter.fetch_data(
        query=request.query_text,
        pages=request.pages
    )
    # 返回结果
```

#### 3. API 配置更新
```javascript
// src/config/api.js
wencai: {
  customQuery: `${API_BASE_URL}/api/market/wencai/custom-query`,
  // ...其他端点
}
```

### 前端改动

#### 1. 新组件
- **文件**：`src/components/market/WencaiPanelV2.vue`
- **大小**：约 700 行代码
- **复杂度**：高（树形结构 + 表格 + 多个对话框）

#### 2. 组件结构
```vue
<template>
  <!-- 头部卡片：标题 + 自定义输入 -->
  <el-card class="header-card">
    <自定义查询输入框 + 查询按钮>
  </el-card>

  <!-- 主体：左右布局 -->
  <div class="main-content">
    <!-- 左侧：树形结构 -->
    <el-card class="tree-card">
      <el-tree>
        默认查询 (qs_1~qs_9)
        分组 A
        分组 B
        分组 C
      </el-tree>
    </el-card>

    <!-- 右侧：结果表格 -->
    <el-card class="result-card">
      <查询语句显示>
      <el-table>
        10个数据列 + 操作列
      </el-table>
      <el-pagination />
    </el-card>
  </div>

  <!-- 分组对话框 -->
  <el-dialog v-model="groupDialogVisible">
    <分组选择器>
  </el-dialog>
</template>
```

#### 3. 关键方法
```javascript
// 执行自定义查询
const executeCustomQuery = async () => {
  const response = await fetch(API_ENDPOINTS.wencai.customQuery, {
    method: 'POST',
    body: JSON.stringify({
      query_text: customQueryText.value,
      pages: 1
    })
  })
  // 处理结果
}

// 格式化数字（3位小数）
const formatNumber = (value, decimals = 3) => {
  return num.toFixed(decimals)
}

// 格式化百分比（2位小数）
const formatPercent = (value) => {
  return `${num.toFixed(2)}%`
}

// 涨跌幅颜色
const getPriceChangeClass = (value) => {
  if (num > 0) return 'price-up'    // 红色
  if (num < 0) return 'price-down'  // 绿色
  return ''
}
```

#### 4. 路由更新
```javascript
// src/router/index.js
{
  path: 'market-data/wencai',
  component: () => import('@/components/market/WencaiPanelV2.vue'),
  // 从 WencaiPanel.vue 改为 WencaiPanelV2.vue
}
```

## 📊 功能对比

| 功能 | V1 版本 | V2 版本 |
|-----|---------|---------|
| 查询方式 | 仅预定义(qs_1~qs_9) | 预定义 + 自定义文本 |
| 布局方式 | 卡片网格 | 树形结构 |
| 表格列数 | 13列（含重复） | 11列（优化后） |
| 数值格式 | 不统一 | 统一（2位/3位小数） |
| 涨跌幅显示 | 无颜色 | 红涨绿跌 |
| 查询语句 | 不显示完整 | 显示完整内容 |
| 序号列 | 无 | 有（自增） |
| 查询日期 | 无 | 有（自动填充） |
| 分组功能 | 无 | 有（UI已实现） |
| 字体大小 | 12px（太小） | 14px |

## 📁 文件清单

### 新增文件
1. `/opt/claude/mystocks_spec/web/backend/app/schemas/wencai_schemas.py` (修改)
   - 新增 `WencaiCustomQueryRequest`
   - 新增 `WencaiCustomQueryResponse`

2. `/opt/claude/mystocks_spec/web/backend/app/api/wencai.py` (修改)
   - 新增 `execute_custom_query` 端点
   - 新增 `datetime` 导入

3. `/opt/claude/mystocks_spec/web/frontend/src/components/market/WencaiPanelV2.vue` (新增)
   - 完整重构的组件
   - 约 700 行代码

4. `/opt/claude/mystocks_spec/web/frontend/src/config/api.js` (修改)
   - 新增 `customQuery` 端点配置

5. `/opt/claude/mystocks_spec/web/frontend/src/router/index.js` (修改)
   - 路由指向 WencaiPanelV2.vue

6. `/opt/claude/mystocks_spec/web/frontend/WENCAI_V2_TEST_GUIDE.md` (新增)
   - 详细测试指南

7. `/opt/claude/mystocks_spec/web/frontend/WENCAI_V2_SUMMARY.md` (本文件)
   - 功能更新总结

## 🎯 测试状态

### 已测试 ✅
- [x] 后端 `/custom-query` API 正常工作
- [x] 后端返回正确格式的数据
- [x] 前端组件编译成功
- [x] 路由配置正确

### 待用户测试 ⏳
- [ ] 自定义查询输入框功能
- [ ] 树形结构布局显示
- [ ] 表格列格式化
- [ ] 涨跌幅颜色显示
- [ ] 查询语句显示
- [ ] 加入分组对话框
- [ ] CSV导出功能
- [ ] 分页功能

## 🚀 使用方法

### 启动服务
```bash
# 后端
cd /opt/claude/mystocks_spec/web/backend
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &

# 前端
cd /opt/claude/mystocks_spec/web/frontend
npm run dev
```

### 访问系统
1. 打开浏览器：`http://localhost:3001`
2. 登录：admin / admin123
3. 导航：市场数据 → 问财筛选
4. 开始使用新功能

### 自定义查询示例
```
请列出今天涨幅超过5%的股票
量比大于2且换手率大于5%的股票
最近5天有涨停的创业板股票
市值小于100亿且涨幅大于3%的股票
```

## ⚠️ 已知限制

1. **分组数据不持久化**
   - 当前仅UI实现
   - 数据未保存到数据库
   - 刷新后分组信息丢失

2. **自定义查询不保存**
   - 结果不保存到数据库
   - 无历史记录功能
   - 刷新后结果消失

3. **分组固定**
   - 只有4个分组：默认、A、B、C
   - 不支持创建/删除/重命名分组

## 🔮 未来改进方向

### 短期（V2.1）
- [ ] 实现分组数据持久化（后端表+API）
- [ ] 支持查看分组内的股票列表
- [ ] 支持从分组中移除股票
- [ ] 添加查询模板（常用查询示例）

### 中期（V2.2）
- [ ] 保存常用自定义查询
- [ ] 查询历史记录功能
- [ ] 自定义分组名称
- [ ] 支持更多分组（不限于A/B/C）

### 长期（V3.0）
- [ ] 高级筛选器（拖拽式条件组合）
- [ ] 实时监控（价格变动提醒）
- [ ] 批量导入/导出分组
- [ ] 分组间的股票对比分析

## 📞 支持

**文档位置**：
- 测试指南：`/opt/claude/mystocks_spec/web/frontend/WENCAI_V2_TEST_GUIDE.md`
- 功能总结：`/opt/claude/mystocks_spec/web/frontend/WENCAI_V2_SUMMARY.md`（本文件）
- Vue调试指南：`/opt/claude/mystocks_spec/web/frontend/VUE_DEBUGGING_GUIDE.md`
- 快速参考：`/opt/claude/mystocks_spec/web/frontend/QUICK_REFERENCE.md`

**遇到问题时**：
1. 查看测试指南中的"常见问题排查"
2. 运行 `./quick-debug.sh src/components/market/WencaiPanelV2.vue`
3. 检查浏览器 Console 错误
4. 查看后端日志：`tail -f /tmp/backend.log`

---

**版本**: V2.0
**创建日期**: 2025-10-18
**作者**: Claude Code
**状态**: ✅ 开发完成，待用户测试
