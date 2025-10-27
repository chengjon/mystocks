====== 简化版日志文件 ======
====== 已删除重复错误,仅保留每类问题的代表性示例 ======

========== 1. 菜单选择日志 ==========
index.vue:173 Menu selected: /dashboard
index.vue:173 Menu selected: /market
index.vue:173 Menu selected: /tdx-market
index.vue:173 Menu selected: /market-data/fund-flow
index.vue:173 Menu selected: /market-data/etf
index.vue:173 Menu selected: /market-data/chip-race
index.vue:173 Menu selected: /market-data/lhb
index.vue:173 Menu selected: /market-data/wencai
index.vue:173 Menu selected: /stocks
index.vue:173 Menu selected: /analysis
index.vue:173 Menu selected: /technical
index.vue:173 Menu selected: /indicators

========== 2. 性能警告 ==========
[Violation] Added non-passive event listener to a scroll-blocking <某些> 事件. 
建议: Consider marking event handler as 'passive' to make the page more responsive.
(此警告重复15次,已合并)

========== 3. ECharts DOM 错误 ==========
Dashboard.vue:405  [ECharts] Can't get DOM width or height. 
问题: dom.clientWidth and dom.clientHeight should not be 0
建议: You may need to call this in the callback of window.onload
影响方法: initLeadingSectorChart, initPriceDistributionChart, initCapitalFlowChart

========== 4. API 请求错误 ==========
GET http://localhost:3000/api/data/dashboard/summary 500 (Internal Server Error)
位置: Dashboard.vue:259 - loadDashboardData
错误处理: errorHandler.js:57 [ErrorHandler] 加载Dashboard数据失败

GET http://localhost:8000/api/market/wencai/queries 500 (Internal Server Error)
位置: WencaiPanelV2.vue:414 - loadQueries
(此错误出现2次)

========== 5. Vue Props 类型校验错误 ==========

5.1 ChipRaceTable - ElStatistic 组件
ChipRaceTable.vue:219 [Vue warn]: Invalid prop: type check failed for prop "value"
问题: Expected Number | Object, got String
错误示例:
  - value="177.97" (总净量)
  - value="1.78" (平均净量)
  - value="92.00" (上涨个股占比)

5.2 LongHuBangTable - ElStatistic 组件
LongHuBangTable.vue:304 [Vue warn]: Invalid prop: type check failed for prop "value"
问题: Expected Number | Object, got String
错误示例:
  - value="20.16" (总净买入额)
  - value="127.81" (总买入额)
  - value="107.65" (总卖出额)

5.3 IndicatorLibrary - ElTag 组件
select.vue:387 [Vue warn]: Invalid prop: validation failed for prop "type"
问题: Expected one of ["primary", "success", "info", "warning", "danger"], got value ""
(此错误重复多次,已合并)

========== 6. 其他信息 ==========
TdxMarket.vue:308 ❤️ Welcome to klinecharts. Version is 9.8.12
useUserPreferences.ts:57 [Preferences] Loaded: {fontSize: '16px', pageSizeFundFlow: 20, ...}

====== 问题汇总 ======
1. 非被动事件监听器性能问题 (15处)
2. ECharts DOM 尺寸获取失败 (3处)
3. API 请求500错误 (3处)
4. Props 类型错误 - 字符串应为数字 (6处)
5. Props 类型错误 - 空字符串应为枚举值 (多处)

====== 修复建议 ======
1. 添加 {passive: true} 到事件监听器
2. 确保 DOM 元素在初始化 ECharts 前已渲染完成(使用 nextTick 或 onMounted)
3. 检查后端 API 服务是否正常运行 (端口3000和8000)
4. 修正 ElStatistic 组件的 value 属性,将字符串转换为数字: parseFloat(value)
5. 修正 ElTag 组件的 type 属性,提供有效的枚举值或移除该属性
