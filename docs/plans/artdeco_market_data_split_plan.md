# ArtDeco Market Data 拆分方案

**文件**: web/frontend/src/views/artdeco-pages/ArtDecoMarketData.vue (3,238行)
**状态**: 执行中
**目标**: 拆分为7个子组件，严格遵循"一组件多Tab"架构原则

---

## 📊 当前结构分析

### 发现的Tabs

根据文件内容分析，发现以下Tab：
1. **市场概览** (Market Overview)
2. **实时行情** (Realtime Quotes)
3. **技术指标** (Technical Indicators)
4. **资金流向** (Fund Flow)
5. **ETF行情** (ETF Quotes)
6. **概念板块** (Concept Sectors)
7. **竞价抢筹** (Auction)

### 文件大小
- **原始行数**: 3,238行
- **目标模块数**: 7个子组件
- **目标平均行数**: ~400行/组件
- **最大行数**: < 500行

---

## 🎯 拆分方案（遵循"一组件多Tab"原则）

```
views/artdeco-pages/market/
├── components/                      # 子组件目录（不在路由中）
│   ├── MarketDataOverview.vue      # 市场概览（~400行）
│   ├── MarketRealtime.vue          # 实时行情（~400行）
│   ├── MarketTechnical.vue         # 技术指标（~400行）
│   ├── MarketFundFlow.vue          # 资金流向（~400行）
│   ├── MarketETF.vue               # ETF行情（~400行）
│   ├── MarketConcept.vue           # 概念板块（~400行）
│   └── MarketAuction.vue           # 竞价抢筹（~400行）
└── ArtDecoMarketData.vue          # 父组件（重构后~500行）
```

### Composables

```
composables/useMarketData.ts        # 市场数据逻辑（~600行）
```

---

## 📋 拆分步骤

### Phase 1: 准备工作 (1小时)

#### Task 1.1: 分析文件结构
- [ ] 确认所有Tab内容
- [ ] 分析组件依赖关系
- [ ] 识别共享逻辑和状态

#### Task 1.2: 创建目录结构
- [ ] 创建 `views/artdeco-pages/market/components/` 目录
- [ ] 创建 `composables/` 目录（如果不存在）

---

### Phase 2: 提取子组件 (4-6小时)

#### Task 2.1: 提取 MarketDataOverview.vue
- [ ] 抽取市场概览Tab内容
- [ ] 创建 `MarketDataOverview.vue` 组件
- [ ] 提取相关状态和方法
- [ ] 目标: ~400行

#### Task 2.2: 提取 MarketRealtime.vue
- [ ] 抽取实时行情Tab内容
- [ ] 创建 `MarketRealtime.vue` 组件
- [ ] 提取WebSocket连接逻辑
- [ ] 目标: ~400行

#### Task 2.3: 提取 MarketTechnical.vue
- [ ] 抽取技术指标Tab内容
- [ ] 创建 `MarketTechnical.vue` 组件
- [ ] 提取图表渲染逻辑
- [ ] 目标: ~400行

#### Task 2.4: 提取 MarketFundFlow.vue
- [ ] 抽取资金流向Tab内容
- [ ] 创建 `MarketFundFlow.vue` 组件
- [ ] 提取数据筛选逻辑
- [ ] 目标: ~400行

#### Task 2.5: 提取 MarketETF.vue
- [ ] 抽取ETF行情Tab内容
- [ ] 创建 `MarketETF.vue` 组件
- [ ] 目标: ~400行

#### Task 2.6: 提取 MarketConcept.vue
- [ ] 抽取概念板块Tab内容
- [ ] 创建 `MarketConcept.vue` 组件
- [ ] 提取板块列表逻辑
- [ ] 目标: ~400行

#### Task 2.7: 提取 MarketAuction.vue
- [ ] 抽取竞价抢筹Tab内容
- [ ] 创建 `MarketAuction.vue` 组件
- [ ] 提取竞价逻辑
- [ ] 目标: ~400行

---

### Phase 3: 创建Composable (1-2小时)

#### Task 3.1: 提取共享逻辑
- [ ] 识别所有子组件共享的数据获取逻辑
- [ ] 提取WebSocket管理
- [ ] 提取数据筛选逻辑
- [ ] 提取状态管理

#### Task 3.2: 创建 useMarketData.ts
- [ ] 创建 `composables/useMarketData.ts`
- [ ] 封装数据获取方法
- [ ] 封装WebSocket管理
- [ ] 封装数据筛选
- [ ] 目标: ~600行

---

### Phase 4: 重构父组件 (1-2小时)

#### Task 4.1: 重构 ArtDecoMarketData.vue
- [ ] 删除所有Tab内容的template
- [ ] 保留父组件结构（导航、状态管理）
- [ ] 导入所有子组件
- [ ] 管理Tab切换状态（`activeTab`）
- [ ] 根据当前Tab动态加载对应的子组件
- [ ] 通过Props传递配置，通过Emit接收事件
- [ ] 目标: ~500行

---

### Phase 5: 集成PAGE_CONFIG (1-2小时)

#### Task 5.1: 集成配置系统
- [ ] 父组件导入 `PAGE_CONFIG` 从 `@/config/pageConfig`
- [ ] 根据当前Tab动态获取 `apiEndpoint` 和 `wsChannel`
- [ ] 将配置通过Props传递给子组件

#### Task 5.2: 更新子组件
- [ ] 子组件接收配置Props
- [ ] 使用配置中的API端点
- [ ] 使用配置中的WebSocket频道
- [ ] 移除硬编码路径

---

### Phase 6: 测试验证 (1-2小时)

#### Task 6.1: 单元测试
- [ ] 测试每个子组件的独立性
- [ ] 测试Composable函数
- [ ] 测试父组件Tab切换
- [ ] 测试PAGE_CONFIG集成

#### Task 6.2: 集成测试
- [ ] 验证完整页面功能
- [ ] 验证Tab切换无闪烁
- [ ] 验证WebSocket重连
- [ ] 验证数据筛选功能

---

## ⏱ 时间估算

| 阶段 | 任务 | 预计时间 |
|--------|------|----------|
| Phase 1: 准备工作 | 2个子任务 | 1小时 |
| Phase 2: 提取子组件 | 7个子任务 | 4-6小时 |
| Phase 3: 创建Composable | 2个子任务 | 1-2小时 |
| Phase 4: 重构父组件 | 1个子任务 | 1-2小时 |
| Phase 5: 集成PAGE_CONFIG | 2个子任务 | 1-2小时 |
| Phase 6: 测试验证 | 2个子任务 | 1-2小时 |
| **总计** | **16个子任务** | **~10-14小时** |

---

## 📋 交付物

1. **子组件文件** (8个)
   - `views/artdeco-pages/market/components/MarketDataOverview.vue`
   - `views/artdeco-pages/market/components/MarketRealtime.vue`
   - `views/artdeco-pages/market/components/MarketTechnical.vue`
   - `views/artdeco-pages/market/components/MarketFundFlow.vue`
   - `views/artdeco-pages/market/components/MarketETF.vue`
   - `views/artdeco-pages/market/components/MarketConcept.vue`
   - `views/artdeco-pages/market/components/MarketAuction.vue`

2. **Composable文件** (1个)
   - `views/artdeco-pages/composables/useMarketData.ts`

3. **重构后的父组件** (1个)
   - `views/artdeco-pages/ArtDecoMarketData.vue` (保留作为父组件)

---

## ✅ 验收标准

### 文件拆分验收
- [ ] 每个子组件 < 500行
- [ ] 父组件 < 500行
- [ ] 每个组件职责单一
- [ ] 模块间依赖清晰
- [ ] 不创建新路由（保持原页面路由）

### 功能验收
- [ ] 所有Tab功能保持不变
- [ ] UI功能保持不变
- [ ] 页面性能无明显下降（±5%）
- [ ] Tab切换平滑无闪烁

### 架构原则验收
- [ ] 严格遵循"一组件多Tab"架构原则
- [ ] 子组件模式正确实现
- [ ] 父组件编排正确实现
- [ ] 不创建新路由（子组件在父组件内动态加载）
- [ ] PAGE_CONFIG集成正确实现

---

## 🚀 后续行动

1. **立即执行**: 开始 Phase 1 - 准备工作
2. **创建分支**: `refactor/artdeco-market-data-split` 分支
3. **持续提交**: 每完成一个子组件提交一次
4. **测试优先**: 每个组件创建后立即测试

---

## 📝 注意事项

1. **架构原则**: 严格遵循ArtDeco"一组件多Tab"原则
2. **路由管理**: 不创建新路由，子组件在父组件内动态加载
3. **配置驱动**: 完整集成PAGE_CONFIG系统
4. **向后兼容**: 确保所有功能保持不变
5. **性能优化**: 注意Tab切换性能，避免重渲染

---

**方案版本**: v1.0
**创建时间**: 2026-01-30T07:45:00Z
**状态**: 待批准和执行
