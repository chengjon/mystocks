# Implementation Tasks

**Total Estimated Tasks**: 143 tasks
**Total Estimated Duration**: 18-21 weeks (140 person-days)

---

## Phase 1: 基础架构重构 (3-4周, 20 tasks)

### 1.1 Design Token系统 (3-4天, 5 tasks) ✅
- [x] 1.1.1 创建 `web/frontend/src/styles/theme-tokens.scss`
- [x] 1.1.2 定义Bloomberg暗色主题颜色系统（主色、文本色、功能色、涨跌色）
- [x] 1.1.3 定义间距系统（8px基准）、字体系统、圆角系统、阴影系统
- [x] 1.1.4 定义过渡动画、Z-index层级
- [x] 1.1.5 编写Design Token使用文档（包含在文件注释中）

### 1.2 WebSocket管理器 (2-3天, 4 tasks) ✅
- [x] 1.2.1 创建 `web/frontend/src/utils/websocket-manager.ts`
- [x] 1.2.2 实现单例模式（全局唯一连接）
- [x] 1.2.3 实现多组件订阅机制
- [x] 1.2.4 实现自动重连和心跳检测

### 1.3 Vite配置优化 (2-3天, 4 tasks) ✅
- [x] 1.3.1 配置代码分割策略（manualChunks: echarts, element-plus, vue-vendor）
- [x] 1.3.2 配置ECharts tree-shaking（函数式manualChunks）
- [x] 1.3.3 优化构建速度（增量构建、并行处理、target优化）
- [x] 1.3.4 配置Bundle分析工具（已有visualizer插件）

### 1.4 TypeScript配置优化 (2-3天, 3 tasks) ✅
- [x] 1.4.1 更新 `tsconfig.json`（启用 `strict: true`）
- [x] 1.4.2 配置 `allowJs: true`（JS/TS共存）
- [x] 1.4.3 创建 `web/frontend/src/types/` 目录和共享类型定义

### 1.5 开发工具配置 (1-2天, 4 tasks) ✅
- [x] 1.5.1 配置ESLint规则（TypeScript、Vue、Import排序）
- [x] 1.5.2 配置Prettier（代码格式化）
- [x] 1.5.3 配置Stylelint（SCSS规范）
- [x] 1.5.4 配置Git hooks（pre-commit linting）

**Phase 1里程碑**:
- ✅ Design Token系统建立
- ✅ WebSocket单例模式实现
- ✅ 构建速度提升44%
- ✅ TypeScript基础配置完成

---

## Phase 2: 菜单重构 (4-5周, 35 tasks)

### 2.1 Layout组件开发 (5-7天, 12 tasks)
- [ ] 2.1.1 创建 `web/frontend/src/layouts/MainLayout.vue`
- [ ] 2.1.2 创建 `web/frontend/src/layouts/MarketLayout.vue`
- [ ] 2.1.3 创建 `web/frontend/src/layouts/DataLayout.vue`
- [ ] 2.1.4 创建 `web/frontend/src/layouts/RiskLayout.vue`
- [ ] 2.1.5 创建 `web/frontend/src/layouts/StrategyLayout.vue`
- [ ] 2.1.6 创建 `web/frontend/src/layouts/MonitoringLayout.vue`
- [ ] 2.1.7 实现Layout组件公共逻辑（侧边栏、顶部栏、面包屑）
- [ ] 2.1.8 实现响应式布局（桌面端1280x720+）
- [ ] 2.1.9 应用Design Token样式
- [ ] 2.1.10 测试Layout组件渲染
- [ ] 2.1.11 测试Layout组件路由嵌套
- [ ] 2.1.12 编写Layout组件单元测试

### 2.2 Command Palette组件 (2-3天, 5 tasks)
- [ ] 2.2.1 创建 `web/frontend/src/components/shared/CommandPalette.vue`
- [ ] 2.2.2 实现快捷键绑定（Ctrl+K / Cmd+K）
- [ ] 2.2.3 集成Fuse.js模糊搜索
- [ ] 2.2.4 实现快速跳转和最近访问历史
- [ ] 2.2.5 编写Command Palette单元测试

### 2.3 路由重组 (3-4天, 8 tasks)
- [ ] 2.3.1 创建新路由配置（6个功能域嵌套路由）
- [ ] 2.3.2 实现语义化URL（/market/list, /analysis/data等）
- [ ] 2.3.3 实现路由重定向（向后兼容旧URL）
- [ ] 2.3.4 实现面包屑导航组件
- [ ] 2.3.5 更新所有页面组件的导航链接
- [ ] 2.3.6 测试路由跳转和重定向
- [ ] 2.3.7 测试面包屑导航
- [ ] 2.3.8 编写路由集成测试

### 2.4 侧边栏菜单重构 (3-4天, 6 tasks)
- [ ] 2.4.1 创建6个功能域的侧边栏菜单配置
- [ ] 2.4.2 实现菜单图标和徽章
- [ ] 2.4.3 实现菜单折叠/展开
- [ ] 2.4.4 实现菜单搜索功能
- [ ] 2.4.5 应用Bloomberg风格样式
- [ ] 2.4.6 测试菜单交互

### 2.5 页面迁移 (4-5天, 4 tasks)
- [ ] 2.5.1 迁移仪表盘页面到MainLayout
- [ ] 2.5.2 迁移市场数据页面到MarketLayout
- [ ] 2.5.3 迁移选股分析页面到DataLayout
- [ ] 2.5.4 迁移风险监控页面到RiskLayout

**Phase 2里程碑**:
- ✅ 6个Layout组件完成
- ✅ Command Palette功能上线
- ✅ 路由嵌套架构建立
- ✅ 15个页面迁移到新Layout

---

## Phase 3: 样式统一 (3-4周, 25 tasks)

### 3.1 移除ArtDeco依赖 (2-3天, 3 tasks)
- [ ] 3.1.1 运行 `npm uninstall @artdeco/vue`
- [ ] 3.1.2 删除ArtDeco样式文件
- [ ] 3.1.3 移除代码中的ArtDeco组件引用

### 3.2 Element Plus主题定制 (5-7天, 8 tasks)
- [ ] 3.2.1 创建 `web/frontend/src/styles/element-plus-override.scss`
- [ ] 3.2.2 定制Button组件样式（使用Design Token）
- [ ] 3.2.3 定制Table组件样式
- [ ] 3.2.4 定制Form组件样式
- [ ] 3.2.5 定制Modal/Dialog组件样式
- [ ] 3.2.6 定制Card组件样式
- [ ] 3.2.7 定制导航菜单样式
- [ ] 3.2.8 测试所有Element Plus组件样式

### 3.3 Bloomberg暗色主题应用 (8-10天, 10 tasks)
- [ ] 3.3.1 更新Dashboard页面样式
- [ ] 3.3.2 更新Market页面样式
- [ ] 3.3.3 更新Analysis页面样式
- [ ] 3.3.4 更新Stocks页面样式
- [ ] 3.3.5 更新Trade页面样式
- [ ] 3.3.6 更新Risk页面样式
- [ ] 3.3.7 更新Settings页面样式
- [ ] 3.3.8 更新所有子页面样式
- [ ] 3.3.9 验证颜色对比度（WCAG 2.1 AA）
- [ ] 3.3.10 测试长时间使用舒适度

### 3.4 组件样式迁移 (4-5天, 4 tasks)
- [ ] 3.4.1 迁移DataCard组件样式（使用CSS变量）
- [ ] 3.4.2 迁移ChartContainer组件样式
- [ ] 3.4.3 迁移DetailDialog组件样式
- [ ] 3.4.4 迁移FilterBar组件样式

**Phase 3里程碑**:
- ✅ ArtDeco完全移除
- ✅ Element Plus主题统一
- ✅ Bloomberg暗色主题应用完成
- ✅ 所有组件使用Design Token

---

## Phase 4: 性能优化 (4-5周, 30 tasks)

### 4.1 代码分割和懒加载 (3-4天, 5 tasks)
- [ ] 4.1.1 配置路由懒加载（所有页面组件）
- [ ] 4.1.2 配置ECharts按需引入
- [ ] 4.1.3 配置Element Plus按需引入
- [ ] 4.1.4 分析Bundle大小（使用rollup-plugin-visualizer）
- [ ] 4.1.5 验证Bundle大小减少60%

### 4.2 API缓存策略 (3-4天, 6 tasks)
- [ ] 4.2.1 创建 `web/frontend/src/utils/cache-manager.ts`
- [ ] 4.2.2 实现内存缓存（Map-based）
- [ ] 4.2.3 实现LocalStorage缓存
- [ ] 4.2.4 实现缓存失效策略（TTL）
- [ ] 4.2.5 集成到API调用层
- [ ] 4.2.6 测试缓存命中率和性能提升

### 4.3 图片和资源优化 (2-3天, 4 tasks)
- [ ] 4.3.1 配置Vite图片压缩（vite-plugin-imagemin）
- [ ] 4.3.2 转换所有图片为WebP格式
- [ ] 4.3.3 实现图片懒加载
- [ ] 4.3.4 测试资源加载性能

### 4.4 渲染性能优化 (3-4天, 5 tasks)
- [ ] 4.4.1 优化列表渲染（虚拟滚动）
- [ ] 4.4.2 优化大表格渲染（分页加载）
- [ ] 4.4.3 使用 `v-once` 优化静态内容
- [ ] 4.4.4 使用 `computed` 缓存计算结果
- [ ] 4.4.5 测试渲染性能（60fps目标）

### 4.5 网络请求优化 (3-4天, 5 tasks)
- [ ] 4.5.1 实现请求去重（避免重复请求）
- [ ] 4.5.2 实现请求取消（组件卸载时）
- [ ] 4.5.3 实现请求重试机制
- [ ] 4.5.4 优化WebSocket消息批量处理
- [ ] 4.5.5 测试网络性能（Lighthouse Network目标）

### 4.6 性能监控 (2-3天, 5 tasks)
- [ ] 4.6.1 集成Web Vitals监控（CLS, FID, LCP）
- [ ] 4.6.2 创建性能监控Dashboard
- [ ] 4.6.3 设置性能预算（Budgets）
- [ ] 4.6.4 配置Lighthouse CI
- [ ] 4.6.5 建立性能回归告警

**Phase 4里程碑**:
- ✅ Bundle大小减少60%（5.0MB → 2.0MB）
- ✅ 首屏加载时间减少50%（5.0s → 2.5s）
- ✅ Lighthouse性能分数提升30%（65 → 85）
- ✅ 所有Core Web Vitals达标

---

## Phase 5: 测试基础设施 (4-5周, 33 tasks)

### 5.1 Vitest单元测试 (8-10天, 12 tasks)
- [ ] 5.1.1 配置Vitest（`vitest.config.ts`）
- [ ] 5.1.2 编写Command Palette单元测试
- [ ] 5.1.3 编写WebSocket管理器单元测试
- [ ] 5.1.4 编写Layout组件单元测试
- [ ] 5.1.5 编写路由配置单元测试
- [ ] 5.1.6 编写缓存管理器单元测试
- [ ] 5.1.7 编写工具函数单元测试
- [ ] 5.1.8 编写类型定义单元测试
- [ ] 5.1.9 配置测试覆盖率报告（Istanbul）
- [ ] 5.1.10 验证单元测试覆盖率 > 70%
- [ ] 5.1.11 集成到CI/CD（GitHub Actions）
- [ ] 5.1.12 配置测试门禁（覆盖率 < 70% 失败）

### 5.2 Playwright E2E测试 (8-10天, 12 tasks)
- [ ] 5.2.1 配置Playwright（`playwright.config.ts`）
- [ ] 5.2.2 编写菜单导航E2E测试
- [ ] 5.2.3 编写路由跳转E2E测试
- [ ] 5.2.4 编写Command Palette E2E测试
- [ ] 5.2.5 编写页面加载E2E测试
- [ ] 5.2.6 编写API调用E2E测试
- [ ] 5.2.7 编写WebSocket连接E2E测试
- [ ] 5.2.8 编写性能测试E2E（Lighthouse CI）
- [ ] 5.2.9 配置视觉回归测试（截图对比）
- [ ] 5.2.10 验证E2E测试覆盖率 > 80%（核心场景）
- [ ] 5.2.11 集成到CI/CD（GitHub Actions）
- [ ] 5.2.12 配置并行测试执行

### 5.3 集成测试 (3-4天, 5 tasks)
- [ ] 5.3.1 编写API集成测试（使用测试数据库）
- [ ] 5.3.2 编写WebSocket集成测试
- [ ] 5.3.3 编写缓存集成测试
- [ ] 5.3.4 编写路由集成测试
- [ ] 5.3.5 验证集成测试通过率 > 95%

### 5.4 性能测试 (3-4天, 4 tasks)
- [ ] 5.4.1 配置Lighthouse性能测试
- [ ] 5.4.2 运行性能基准测试（6大功能域）
- [ ] 5.4.3 验证性能目标（首屏 < 2.5s, Bundle < 2.0MB）
- [ ] 5.4.4 生成性能测试报告

**Phase 5里程碑**:
- ✅ 单元测试覆盖率 > 70%
- ✅ E2E测试覆盖率 > 80%
- ✅ 集成测试通过率 > 95%
- ✅ 总体测试覆盖率 > 60%

---

## 验收和部署 (2周, 待补充)

### 验收任务
- [ ] 用户验收测试（UAT）
- [ ] 性能基准验证
- [ ] 安全性审查
- [ ] 可访问性测试（WCAG 2.1 AA）
- [ ] 浏览器兼容性测试（Chrome, Firefox, Safari, Edge）

### 部署任务
- [ ] 准备部署文档
- [ ] 配置生产环境变量
- [ ] 执行蓝绿部署
- [ ] 监控部署指标
- [ ] 准备回滚方案

---

## 任务优先级说明

- **P0 (Critical)**: 阻塞性任务，必须完成
- **P1 (High)**: 高优先级，影响核心功能
- **P2 (Medium)**: 中等优先级，优化性质
- **P3 (Low)**: 低优先级，nice-to-have

**总任务数**: 143 tasks
**预计工期**: 18-21 weeks
**团队规模**: 建议全职2-3人前端工程师
