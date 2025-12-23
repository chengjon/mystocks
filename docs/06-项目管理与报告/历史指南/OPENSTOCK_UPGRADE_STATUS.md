# OpenStock 功能升级状态报告

## 📅 更新时间
2025-10-20 18:30

## ✅ 已完成的工作

### 1. 股票搜索功能升级 ✓
**状态**: 完成

**改动文件**:
- `web/backend/app/services/stock_search_service.py`

**实现内容**:
- ✅ 移除美股支持（删除 Finnhub API 调用）
- ✅ 添加港股（H股）搜索功能
  - 使用 AKShare 的 `stock_hk_spot_em()` 接口
  - 支持按代码和名称搜索
  - 返回统一格式的搜索结果
- ✅ 修改统一搜索接口
  - 支持自动市场检测（A股/港股）
  - 5位数字识别为港股代码
  - 6位数字识别为A股代码
  - 中文查询优先搜索A股
- ✅ 添加港股实时行情接口
- ✅ 添加港股新闻接口（预留）
- ✅ 更新缓存清除方法

**测试建议**:
```bash
# 搜索A股
curl -X GET "http://localhost:8000/api/stock-search/search?q=茅台&market=cn" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 搜索港股
curl -X GET "http://localhost:8000/api/stock-search/search?q=00700&market=hk" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 自动检测
curl -X GET "http://localhost:8000/api/stock-search/search?q=腾讯&market=auto" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. 自选股数据库升级 ✓
**状态**: 完成（基础结构）

**改动文件**:
- `web/backend/app/services/watchlist_service.py`
- `web/backend/app/api/watchlist.py`

**实现内容**:
- ✅ 创建分组表 `watchlist_groups`
  - 支持用户自定义分组名称
  - 包含排序字段 `sort_order`
- ✅ 修改自选股表 `user_watchlist`
  - 添加 `group_id` 外键
  - 添加 `market` 字段（CN/HK）
  - 修改唯一约束为 `(user_id, group_id, symbol)`
- ✅ 修复 `add_to_watchlist` 方法
  - 自动创建默认分组
  - 支持指定分组ID
  - 支持 market 参数
- ✅ 更新 API 模型
  - `AddWatchlistRequest` 添加 `market` 和 `group_id` 字段

## 🔄 进行中的工作

### 3. 自选股分组管理功能
**状态**: 数据库结构完成，API 待实现

**需要添加的 API**:
1. `GET /api/watchlist/groups` - 获取用户的所有分组
2. `POST /api/watchlist/groups` - 创建新分组
3. `PUT /api/watchlist/groups/{group_id}` - 修改分组名称
4. `DELETE /api/watchlist/groups/{group_id}` - 删除分组
5. `GET /api/watchlist/group/{group_id}` - 获取指定分组的自选股
6. `PUT /api/watchlist/move` - 移动自选股到其他分组

**需要修改的 Service 方法**:
```python
# watchlist_service.py 需要添加的方法
- get_user_groups(user_id)
- create_group(user_id, group_name)
- update_group(group_id, group_name)
- delete_group(group_id)
- get_watchlist_by_group(user_id, group_id)
- move_stock_to_group(user_id, symbol, from_group_id, to_group_id)
```

## ⏳ 待完成的工作

### 4. 前端界面改造
**状态**: 未开始

**需要修改的文件**:
- `web/frontend/src/views/OpenStockDemo.vue`

**需要实现的功能**:
1. **股票搜索标签页**
   - 修改市场选择：去掉"美股"，添加"港股"
   - 搜索结果显示市场标签（A股/H股）
   - 添加自选股时可选择分组

2. **自选股管理标签页**
   - 左侧显示分组列表
   - 右侧显示选中分组的股票
   - 分组管理功能
     * 创建新分组按钮
     * 重命名分组
     * 删除分组
     * 拖拽排序
   - 股票操作
     * 移动到其他分组
     * 删除股票
     * 编辑备注

3. **前端数据结构**
```javascript
// 分组数据结构
{
  groups: [
    {
      id: 1,
      name: '默认分组',
      stocks: [
        {
          symbol: '600000',
          display_name: '浦发银行',
          exchange: '上海证券交易所',
          market: 'CN',
          notes: '...',
          added_at: '...'
        }
      ]
    }
  ],
  currentGroupId: 1
}
```

### 5. 替换 TradingView 为 klinecharts
**状态**: 未开始

**需要修改的文件**:
- `web/frontend/index.html` - 删除 TradingView script标签
- `web/frontend/src/views/OpenStockDemo.vue` - TradingView 标签页

**klinecharts 集成步骤**:

1. 删除 TradingView 相关代码
```vue
<!-- 删除 index.html 中的 -->
<script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
```

2. 在 OpenStockDemo.vue 中实现 klinecharts
```vue
<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { init, dispose } from 'klinecharts'

const chartSymbol = ref('600000')
const chartMarket = ref('CN')
let chart = null

const loadKlineChart = async () => {
  // 清除旧图表
  if (chart) {
    dispose('kline-chart')
  }

  // 初始化图表
  chart = init('kline-chart')
  chart.setSymbol({ ticker: chartSymbol.value })
  chart.setPeriod({ span: 1, type: 'day' })

  // 从后端加载数据
  chart.setDataLoader({
    getBars: async ({ callback }) => {
      try {
        const response = await axios.get(`${API_BASE}/market/kline`, {
          params: {
            symbol: chartSymbol.value,
            market: chartMarket.value
          },
          headers: { Authorization: `Bearer ${getToken()}` }
        })
        callback(response.data)
      } catch (error) {
        console.error('加载K线数据失败:', error)
        callback([])
      }
    }
  })
}

onUnmounted(() => {
  if (chart) {
    dispose('kline-chart')
  }
})
</script>

<template>
  <div>
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="8">
        <el-input v-model="chartSymbol" placeholder="输入股票代码" />
      </el-col>
      <el-col :span="8">
        <el-select v-model="chartMarket">
          <el-option label="A股" value="CN" />
          <el-option label="H股" value="HK" />
        </el-select>
      </el-col>
      <el-col :span="8">
        <el-button type="primary" @click="loadKlineChart">加载图表</el-button>
      </el-col>
    </el-row>

    <div id="kline-chart" style="width:100%;height:600px"></div>
  </div>
</template>
```

3. 后端添加 K线数据接口（如果需要）
```python
@router.get("/market/kline")
async def get_kline_data(
    symbol: str,
    market: str = "CN",
    current_user: User = Depends(get_current_user)
):
    """获取K线数据"""
    # 调用 akshare 获取历史数据
    # 返回格式: [{ timestamp, open, high, low, close, volume }, ...]
```

## 📝 完整实施步骤

### 第一阶段：后端 API 完善（优先级：高）
1. 完成自选股分组管理 API
   - [ ] 实现 `watchlist_service.py` 的分组管理方法
   - [ ] 实现 `watchlist.py` 的分组管理路由
   - [ ] 测试所有 API 端点

### 第二阶段：前端界面改造（优先级：高）
1. 修改股票搜索
   - [ ] 更新市场选择选项
   - [ ] 添加分组选择功能
   - [ ] 传递 market 参数到后端

2. 重写自选股管理界面
   - [ ] 实现分组列表显示
   - [ ] 实现分组 CRUD 操作
   - [ ] 实现股票移动功能
   - [ ] 实现拖拽排序

### 第三阶段：图表替换（优先级：中）
1. 移除 TradingView
   - [ ] 删除 script 引用
   - [ ] 删除相关代码和文档

2. 集成 klinecharts
   - [ ] 实现基础图表显示
   - [ ] 添加后端K线数据接口
   - [ ] 测试图表功能

### 第四阶段：测试和优化（优先级：中）
1. 功能测试
   - [ ] 测试A股搜索
   - [ ] 测试港股搜索
   - [ ] 测试分组管理
   - [ ] 测试图表显示

2. 性能优化
   - [ ] 优化数据加载
   - [ ] 添加loading状态
   - [ ] 优化UI交互

## 🚀 快速继续开发指南

### 方案A：完整实现所有功能
如果要完整实现，建议按以下顺序：
1. 完成后端分组API（约2小时）
2. 重写前端自选股界面（约3小时）
3. 集成 klinecharts（约1小时）
4. 测试和修复（约1小时）

总计：约7小时

### 方案B：渐进式实现
建议优先完成核心功能：
1. 先完成自选股分组的后端API
2. 实现基础的前端分组显示（不含拖拽）
3. 暂时保留 TradingView，待后续替换

### 方案C：最小化改动
只完成必要功能：
1. 保持当前数据库结构（分组表已创建）
2. 暂时使用默认分组
3. 前端界面保持原样
4. 专注于修复自选股显示问题

## 📊 当前系统状态

**后端服务**: ✅ 运行正常
- 端口: 8000
- 股票搜索API已更新
- 自选股基础API可用

**前端服务**: ✅ 运行正常
- 端口: 3000
- 热更新已启用

**数据库**: ✅ 结构已更新
- PostgreSQL 连接正常
- 分组表已创建
- 自选股表已升级

## 🔗 相关文档

- `WATCHLIST_GROUP_IMPLEMENTATION.md` - 分组功能实现说明
- `OPENSTOCK_DEMO_PAGE_GUIDE.md` - 演示页面使用指南
- `OPENSTOCK_MIGRATION_SUMMARY.md` - 迁移总结
- `TRADINGVIEW_TROUBLESHOOTING.md` - TradingView 问题排查

## ⚠️ 注意事项

1. **数据库迁移**: 已有数据需要分配到默认分组
2. **向后兼容**: API 更改需要保证前端兼容
3. **测试覆盖**: 所有新功能需要充分测试
4. **用户体验**: 分组功能应该直观易用

---

**报告生成时间**: 2025-10-20 18:30
**下次更新**: 功能完成后
