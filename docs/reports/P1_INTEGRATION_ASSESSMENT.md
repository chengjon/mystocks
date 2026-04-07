# P1 优先级页面 API 集成评估报告

> **历史分析说明**:
> 本文件是阶段性分析、审计、评估或复盘材料，不是当前基线、当前实施优先级或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内问题分级、差距判断、风险结论、审阅意见和建议动作如未重新复核，应视为历史分析结果，不得直接当作当前事实。


**评估日期**: 2025-11-26
**范围**: P1 优先级页面的 API 集成现状和改进计划

---

## 📊 整体现状

| 页面 | 文件名 | 状态 | API 集成 | 优先级 |
|------|-------|------|--------|--------|
| **股票列表** | Stocks.vue | ✅ 已集成 | dataApi.getStocksBasic() | P1 |
| **股票详情** | StockDetail.vue | 🔍 需评估 | 待检查 | P1 |
| **风险监控** | RiskMonitor.vue | 🔍 需评估 | 待检查 | P1 |
| **监控仪表板** | MonitoringDashboard.vue | ❌ 不存在 | - | P1 |
| **回测分析** | BacktestAnalysis.vue | 🔍 需评估 | 待检查 | P1 |
| **实时监控** | RealTimeMonitor.vue | 🔍 需评估 | 待检查 | P1 |

---

## ✅ 已集成的 P1 页面

### 1. Stocks.vue - 股票列表页面

**状态**: ✅ 完整集成

**已集成的 API 调用**:
```javascript
// 行业列表
dataApi.getStocksIndustries()

// 概念列表
dataApi.getStocksConcepts()

// 股票基础信息
dataApi.getStocksBasic(params)
```

**功能**:
- ✅ 搜索股票代码或名称
- ✅ 按行业筛选
- ✅ 按概念筛选
- ✅ 按市场筛选 (上海/深圳)
- ✅ 排序功能
- ✅ 分页加载

**集成完整度**: 100% 🎯

---

## 🔍 待评估的 P1 页面

### 1. StockDetail.vue - 股票详情页面

**当前状态**: 需要详细评估

**快速检查**:
```bash
grep -n "import.*api\|dataApi\|stockApi\|fetch\|axios" Stocks/StockDetail.vue
```

**推荐集成**:
- 股票基本信息 API
- 股票价格历史 API
- 股票财务指标 API
- 股票公告 API

---

### 2. RiskMonitor.vue - 风险监控页面

**当前状态**: 需要详细评估

**推荐集成**:
- 风险指标 API
- 投资组合风险分析 API
- 风险告警 API (可能已通过 SSE/WebSocket)

---

### 3. BacktestAnalysis.vue - 回测分析页面

**当前状态**: 需要详细评估

**推荐集成**:
- 回测结果 API
- 性能指标 API
- 交易记录 API

---

### 4. RealTimeMonitor.vue - 实时监控页面

**当前状态**: 需要详细评估

**推荐集成**:
- 实时数据流 API (WebSocket)
- 市场数据 API
- 组合持仓 API

---

## 📋 P1 集成任务列表

### 第 1 批：页面评估 (2 小时)

- [ ] 检查 StockDetail.vue 现有 API 集成情况
- [ ] 检查 RiskMonitor.vue 现有 API 集成情况
- [ ] 检查 BacktestAnalysis.vue 现有 API 集成情况
- [ ] 检查 RealTimeMonitor.vue 现有 API 集成情况
- [ ] 生成详细的集成缺口分析

### 第 2 批：高优先级缺口补充 (3-4 小时)

- [ ] 为缺少主 API 的页面补充完整集成
- [ ] 实现错误处理和降级机制
- [ ] 添加加载状态指示

### 第 3 批：测试和验证 (2 小时)

- [ ] 为 P1 页面编写 E2E 测试
- [ ] 性能测试
- [ ] 浏览器兼容性测试

---

## 🎯 集成标准 (参考 Market.vue P0 实现)

### 必须包含

1. **主 API 集成**
   ```javascript
   // 主接口
   const response = await api.primaryMethod()

   // 备选接口（可选）
   const response = response || await api.fallbackMethod()
   ```

2. **错误处理**
   ```javascript
   try {
     // API 调用
   } catch (error) {
     // 显示错误或使用缓存数据
     ElMessage.error('加载失败')
   }
   ```

3. **加载状态**
   ```javascript
   const loading = ref(false)

   const loadData = async () => {
     loading.value = true
     try {
       // API 调用
     } finally {
       loading.value = false
     }
   }
   ```

4. **数据转换**
   ```javascript
   // 兼容多种数据源的字段名
   const stocks = data.map(item => ({
     code: item.code || item.symbol,
     name: item.name || item.title,
     price: item.price || item.close
   }))
   ```

---

## 📈 进度跟踪

### 完成度指标

```
P0 优先级: 4/4 页面完成 = 100% ✅
P1 优先级: 1/6 页面完成 = 16.7% 🔄

总体 API 集成进度:
  P0 (4 页面)  + P1 (1 已完成) = 5/10 = 50%
```

### 估计工作量

| 阶段 | 任务 | 预计时间 |
|------|------|--------|
| 评估 | 检查 5 个待评估页面 | 2 小时 |
| 开发 | 补充 API 集成 + 错误处理 | 3-4 小时 |
| 测试 | E2E + 性能测试 | 2 小时 |
| **合计** | - | **7-8 小时** |

---

## 🚀 推荐执行计划

### 今天 (立即)
- [x] 完成 P0 修复和验证
- [x] 运行全面 E2E 测试 (77.8% 通过)
- [x] 优化构建配置
- [ ] **检查 5 个 P1 页面的 API 集成情况**

### 明天
- [ ] 补充缺少的 API 集成
- [ ] 编写 P1 E2E 测试
- [ ] 更新 API 覆盖率统计

### 后天
- [ ] 推进 P2 优先级页面集成
- [ ] 完成整体 API 文档更新
- [ ] 提交代码审查

---

## 📌 关键指标

**当前状态**:
- ✅ 构建无错误
- ✅ P0 完成 (4/4 = 100%)
- 🔄 P1 进行中 (1/6 = 16.7%)
- 📊 总体 API 集成: ~20-25%

**目标**:
- P1 完成 (6/6 = 100%)
- 总体 API 集成 >= 35%
- 用户可用功能 >= 50%

---

**下一步**: 详细评估 StockDetail.vue, RiskMonitor.vue, BacktestAnalysis.vue, RealTimeMonitor.vue 的 API 集成情况
