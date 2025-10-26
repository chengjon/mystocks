# Data Model Design

**Feature**: UI系统改进 - 字体系统、问财查询、自选股重构
**Date**: 2025-10-26
**Status**: Draft

## Overview

本文档定义了UI系统改进所需的数据结构。由于这是纯前端功能，大部分数据结构用于前端状态管理和配置。

## 数据实体

### 1. FontPreference (字体偏好设置)

**用途**: 存储用户的字体大小偏好设置

**存储位置**: LocalStorage (`preferences.fontSize`)

**数据结构**:
```typescript
interface FontPreference {
  fontSize: string  // CSS值，如 "12px", "14px", "16px", "18px", "20px"
  updatedAt?: number  // 可选：最后更新时间戳
}
```

**值域约束**:
- `fontSize`: 必须是以下值之一：`"12px"`, `"14px"`, `"16px"`, `"18px"`, `"20px"`
- `updatedAt`: Unix时间戳（毫秒）

**默认值**:
```javascript
{
  fontSize: '16px',
  updatedAt: Date.now()
}
```

**验证规则**:
- FR-002: fontSize必须在5个等级中选择
- 如果读取到无效值，回退到默认值16px

---

### 2. WencaiQuery (问财预设查询)

**用途**: 定义9个预设的问财查询模板

**存储位置**: 前端配置文件 (`config/wencaiQueries.js`)

**数据结构**:
```typescript
interface WencaiQuery {
  id: string          // 查询唯一标识，如 "qs_1", "qs_2", ...
  name: string        // 查询名称，用于UI显示
  description: string // 查询描述，解释查询目的
  query: string       // 问财查询语句
  category: string    // 查询分类，如 "趋势"、"突破"、"资金"
  icon?: string       // 可选：图标名称
}
```

**示例**:
```javascript
{
  id: 'qs_1',
  name: '连续上涨股票',
  description: '查询连续3天以上上涨的股票',
  query: '连续3天以上上涨',
  category: '趋势',
  icon: 'TrendCharts'
}
```

**集合约束**:
- 必须包含恰好9个查询（qs_1到qs_9）
- 每个id必须唯一
- FR-009: 全部9个查询必须在默认查询列表中显示

---

### 3. WatchlistStock (自选股)

**用途**: 自选股列表中的股票项

**数据来源**: 后端API (`/api/watchlist/*`)

**数据结构**:
```typescript
interface WatchlistStock {
  // 基础字段
  symbol: string       // 股票代码，如 "000001"
  name: string         // 股票名称，如 "平安银行"
  market: string       // 市场，如 "SZ"（深圳）、"SH"（上海）

  // 分类字段
  category: WatchlistCategory  // 所属类别
  groupId: number      // 分组ID，用于高亮显示
  groupName: string    // 分组名称，如 "分组1"、"分组2"

  // 行情字段（可选，根据API返回）
  latestPrice?: number    // 最新价
  changePercent?: number  // 涨跌幅
  volume?: number         // 成交量

  // 元数据
  addedAt: number      // 添加时间戳
  updatedAt: number    // 更新时间戳
}

enum WatchlistCategory {
  USER = 'user',       // 用户自选
  SYSTEM = 'system',   // 系统自选
  STRATEGY = 'strategy', // 策略自选
  MONITOR = 'monitor'  // 监控列表
}
```

**分组高亮规则**:
- FR-016: 使用`groupId % 4`循环分配4种高亮颜色
- Group 0 → 蓝色系
- Group 1 → 绿色系
- Group 2 → 红色系
- Group 3 → 黄色系

---

### 4. TabState (标签页状态)

**用途**: 记住用户在自选股页面选择的标签页

**存储位置**: LocalStorage (`watchlist.activeTab`)

**数据结构**:
```typescript
interface TabState {
  activeTab: WatchlistCategory  // 当前激活的标签页
  scrollPositions?: {            // 可选：每个标签页的滚动位置
    [key in WatchlistCategory]?: number
  }
}
```

**默认值**:
```javascript
{
  activeTab: 'user',
  scrollPositions: {}
}
```

**验证规则**:
- FR-019: 页面刷新后恢复activeTab
- FR-018: 可选地恢复每个标签页的滚动位置

---

## 状态管理（Pinia Store）

### PreferencesStore

**文件**: `stores/preferences.js`

**State**:
```javascript
{
  fontSize: '16px',          // 当前字体大小
  // 未来可扩展其他偏好设置
}
```

**Actions**:
```javascript
{
  updatePreference(key, value),  // 更新偏好设置并持久化
  loadPreferences(),             // 从LocalStorage加载偏好
  resetPreferences()             // 重置为默认值
}
```

**Getters**:
```javascript
{
  fontSizeValue: (state) => parseInt(state.fontSize),  // 提取数字值
  fontSizeLabel: (state) => FONT_SIZE_LABELS[state.fontSize]  // 获取标签
}
```

---

### WatchlistStore (可选)

如果需要前端缓存自选股数据：

**State**:
```javascript
{
  stocks: {
    user: [],
    system: [],
    strategy: [],
    monitor: []
  },
  activeTab: 'user',
  loading: false,
  error: null
}
```

**Actions**:
```javascript
{
  async fetchWatchlist(category),  // 从API获取自选股
  setActiveTab(category),          // 切换标签页
  saveActiveTab()                  // 持久化标签页状态
}
```

---

## 数据流图

### 字体系统数据流

```
┌─────────────────┐
│ FontSizeSetting │ 用户选择字体大小
│     Component   │
└────────┬────────┘
         │ handleFontSizeChange('18px')
         ▼
┌─────────────────┐
│ PreferencesStore│ 更新state.fontSize
│  (Pinia)        │ + localStorage.setItem()
└────────┬────────┘
         │ CSS Variables更新
         ▼
┌─────────────────┐
│ document.       │ setProperty('--font-size-base', '18px')
│ documentElement │
└────────┬────────┘
         │ 浏览器重新渲染
         ▼
┌─────────────────┐
│ All Vue         │ 字体大小立即更新
│ Components      │
└─────────────────┘
```

### 问财查询数据流

```
┌─────────────────┐
│ WencaiPanel     │ 用户点击预设查询
│  Component      │
└────────┬────────┘
         │ selectQuery('qs_3')
         ▼
┌─────────────────┐
│ wencaiQueries.js│ 查找query对象
│   (Config)      │
└────────┬────────┘
         │ { query: '主力资金净流入排名前20' }
         ▼
┌─────────────────┐
│ dataApi.        │ POST /api/market/wencai/query
│ wencaiQuery()   │
└────────┬────────┘
         │ response.data
         ▼
┌─────────────────┐
│ WencaiPanel     │ 显示查询结果
│ Results Table   │ + 高亮当前查询来源
└─────────────────┘
```

### 自选股数据流

```
┌─────────────────┐
│ WatchlistTabs   │ 用户切换标签页
│   Component     │
└────────┬────────┘
         │ switchTab('strategy')
         ▼
┌─────────────────┐
│ WatchlistStore  │ setActiveTab('strategy')
│  (Pinia)        │ + saveActiveTab()
└────────┬────────┘
         │ 触发数据加载
         ▼
┌─────────────────┐
│ dataApi.        │ GET /api/watchlist?category=strategy
│ getWatchlist()  │
└────────┬────────┘
         │ WatchlistStock[]
         ▼
┌─────────────────┐
│ WatchlistTable  │ 渲染表格
│   Component     │ + 应用分组高亮
└─────────────────┘
```

---

## 数据验证

### 前端验证规则

1. **字体大小验证**:
```javascript
const VALID_FONT_SIZES = ['12px', '14px', '16px', '18px', '20px']

function validateFontSize(fontSize) {
  return VALID_FONT_SIZES.includes(fontSize)
}
```

2. **查询ID验证**:
```javascript
function validateQueryId(queryId) {
  return /^qs_[1-9]$/.test(queryId)
}
```

3. **分类验证**:
```javascript
const VALID_CATEGORIES = ['user', 'system', 'strategy', 'monitor']

function validateCategory(category) {
  return VALID_CATEGORIES.includes(category)
}
```

---

## 边界条件

### 字体系统
- **最小值**: 12px（辅助文字最小10px，仍可读）
- **最大值**: 20px（主标题最大28px，避免过大）
- **降级**: LocalStorage不可用时，使用内存状态

### 问财查询
- **API超时**: 5秒后显示错误提示
- **空结果**: 显示el-empty组件
- **查询失败**: 保持界面可用，显示错误消息

### 自选股
- **空列表**: 每个标签页显示el-empty
- **数据量**: 支持1000+条数据，使用虚拟滚动（可选优化）
- **网络错误**: 显示重试按钮

---

## 性能考虑

1. **CSS Variables计算**: 使用`calc()`动态计算字体层级，避免手动计算
2. **LocalStorage读写**: 仅在必要时读写，避免频繁操作
3. **表格渲染**: 使用Element Plus的虚拟滚动（如果数据量>1000）
4. **标签页懒加载**: 使用`lazy`属性延迟加载非激活标签页

---

## 扩展性

### 未来可能的扩展

1. **字体族选择**: 在PreferencesStore添加`fontFamily`字段
2. **自定义查询**: 在WencaiQuery添加`isCustom`字段
3. **自选股排序**: 在TabState添加`sortConfig`字段
4. **多列分组**: 支持二级分组（group和subgroup）

---

## 总结

本数据模型设计遵循以下原则：
- **简洁性**: 仅定义必要的数据结构
- **扩展性**: 预留未来扩展空间
- **类型安全**: 使用TypeScript接口定义（文档层面）
- **配置驱动**: 符合项目宪法的配置驱动原则
