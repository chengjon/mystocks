# Technical Design Document

**Change ID**: `refactor-web-frontend-menu-architecture`
**Version**: 1.0
**Last Updated**: 2026-01-09

---

## Context

### Background

MyStocks Web前端当前存在严重的架构问题，阻碍了用户体验和开发效率：

**菜单架构问题**：
- 15个扁平一级菜单超过用户短期记忆容量（7±2原则）
- 功能分类混乱（如"市场行情" vs "实时监控"高度重叠）
- 缺乏功能域逻辑分组

**技术债务问题**：
- 依赖包过大：369MB node_modules，5MB bundle
- 3套样式系统并存（Element Plus + ArtDeco + Pro-Fintech）
- TypeScript配置不当：`strict: false`，仅20%类型覆盖
- 测试覆盖率极低：仅5%

**性能问题**：
- 首屏加载时间：5秒+
- 缺少代码分割、懒加载、API缓存
- ECharts未按需引入
- WebSocket连接管理混乱（多标签页N个连接）

### Constraints

**平台约束**：
- ✅ 仅支持桌面端（1280x720+）
- ❌ 不支持移动端/平板端
- ❌ 不考虑响应式设计（@media queries for mobile）

**技术栈约束**：
- Vue 3.4+（Composition API）
- TypeScript 5.3+（渐进式迁移）
- Element Plus（按需引入）
- Vite 5.x（构建工具）
- FastAPI后端（保持不变）

**时间约束**：
- 总体工期：18-21周
- 每个Phase独立验证和可回滚

### Stakeholders

**用户**：
- 专业量化交易员（需要高效工具）
- 新用户（需要低学习曲线）
- 专家用户（需要快捷键和快速导航）

**开发团队**：
- 前端工程师（需要类型安全和开发效率）
- UI/UX设计师（需要Design Token系统）
- 测试工程师（需要测试基础设施）

---

## Goals / Non-Goals

### Goals ✅

1. **菜单架构重组**
   - 15个一级菜单 → 6大功能域
   - 认知负荷降低60%
   - 功能发现时间减少40%

2. **性能优化**
   - Bundle大小减少60%（5.0MB → 2.0MB）
   - 首屏加载时间减少50%（5.0s → 2.5s）
   - Lighthouse性能分数提升30%（65 → 85）

3. **样式统一**
   - 3套样式系统 → 1套Design Token
   - 移除ArtDeco依赖
   - Bloomberg Terminal风格

4. **开发体验提升**
   - TypeScript覆盖率：20% → 90%
   - 测试覆盖率：5% → 60%
   - 构建时间减少44%（45s → 25s）

5. **用户体验增强**
   - Command Palette（Ctrl+K快速导航）
   - WebSocket单例模式（避免连接爆炸）
   - 面包屑导航
   - 键盘快捷键支持

### Non-Goals ❌

1. **移动端适配**（明确排除）
   - 不支持手机/平板设备
   - 不实现响应式布局
   - 不优化触摸交互

2. **后端API变更**（保持不变）
   - FastAPI端点不变
   - WebSocket协议不变
   - 数据库架构不变

3. **业务逻辑变更**（仅前端架构）
   - 不改变交易流程
   - 不改变数据处理逻辑
   - 不改变风控规则

4. **GPU加速功能**（已有其他变更覆盖）
   - GPU回测UI（由 `frontend-optimization-six-phase` 覆盖）
   - 性能监控Dashboard（由 `frontend-optimization-six-phase` 覆盖）

---

## Decisions

### Decision 1: 功能域驱动架构

**决策**：采用6大功能域架构重组菜单

**理由**：
- 符合MECE原则（相互独立，完全穷尽）
- 符合量化交易用户心智模型
- 层级深度控制在2-3级（符合认知心理学）

**替代方案**：
- **选项A**：保持15个扁平菜单（拒绝：认知负荷过高）
- **选项B**：4大功能域（拒绝：分组过粗，仍然混乱）
- **选项C**：8大功能域（拒绝：分组过细，增加层级）

**实施**：
```
Dashboard (仪表盘)
├─ Market Data (市场数据域)
├─ Analysis (选股分析域)
├─ Strategy (策略回测域)
├─ Trading (交易管理域)
├─ Risk (风险监控域)
└─ Settings (系统设置域)
```

### Decision 2: Design Token系统优先建立

**决策**：在Phase 1优先建立Design Token系统，再进行样式迁移

**理由**：
- 避免"先污染后治理"的返工
- 确保样式一致性
- 降低后续迁移工作量

**替代方案**：
- **选项A**：边迁移边定义Token（拒绝：容易不一致）
- **选项B**：最后统一Token（拒绝：大量返工）

**实施**：
```scss
// web/frontend/src/styles/theme-tokens.scss
:root {
  // Bloomberg暗色主题
  --color-bg-primary: #1a1a1a;
  --color-text-primary: #ffffff;
  --color-accent: #ff6b35;

  // 8px基准间距系统
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;

  // 字体系统
  --font-family-mono: 'JetBrains Mono', monospace;
}
```

### Decision 3: WebSocket单例模式

**决策**：使用单例模式管理WebSocket连接，确保全局唯一连接

**理由**：
- 避免多标签页连接数爆炸（N个标签页从N个连接 → 1个连接）
- 节省90% WebSocket连接资源
- 提升稳定性（自动重连 + 心跳检测）

**替代方案**：
- **选项A**：每个组件独立连接（拒绝：资源浪费）
- **选项B**：连接池（拒绝：过度设计，WebSocket不适合）

**实施**：
```typescript
// web/frontend/src/utils/websocket-manager.ts
class WebSocketManager {
  private static instance: WebSocketManager | null = null

  static getInstance(): WebSocketManager {
    if (!this.instance) {
      this.instance = new WebSocketManager()
    }
    return this.instance
  }

  subscribe(messageType: string, callback: Function) {
    // 多组件订阅同一连接
  }
}
```

### Decision 4: Command Palette功能

**决策**：添加Command Palette（Ctrl+K）快速导航功能

**理由**：
- 提升专家用户效率30%+
- 功能发现时间减少40%
- 符合专业工具标准（VSCode、Notion、Bloomberg）

**替代方案**：
- **选项A**：仅菜单导航（拒绝：专家用户效率低）
- **选项B**：搜索框（拒绝：不够快捷，无法快速跳转）

**实施**：
```vue
<!-- web/frontend/src/components/shared/CommandPalette.vue -->
<template>
  <div v-if="isOpen" class="command-palette">
    <input @keydown.ctrl.k="open" />
    <ul v-for="result in searchResults">
      <li @click="navigate(result)">{{ result.title }}</li>
    </ul>
  </div>
</template>
```

### Decision 5: TypeScript渐进式迁移

**决策**：采用渐进式TypeScript迁移策略（allowJs: true → strict: true）

**理由**：
- 避免"大爆炸"重写风险
- 允许JS/TS共存
- 每个Phase独立验证

**替代方案**：
- **选项A**：一次性全部迁移（拒绝：风险太高）
- **选项B**：不迁移TypeScript（拒绝：失去类型安全收益）

**实施**：
```json
// tsconfig.json
{
  "compilerOptions": {
    "allowJs": true,        // JS/TS共存
    "checkJs": false,       // 不检查JS文件
    "strict": true,         // 启用严格模式（仅TS文件）
    "target": "ES2020"
  }
}
```

### Decision 6: 移除ArtDeco依赖

**决策**：完全移除ArtDeco依赖，使用Element Plus + Design Token

**理由**：
- 3套样式系统导致混乱
- ArtDeco维护不活跃
- Element Plus功能更完善

**替代方案**：
- **选项A**：保留ArtDeco（拒绝：3套系统成本高）
- **选项B**：完全自研（拒绝：重复造轮子）

**实施**：
```bash
npm uninstall @artdeco/vue
rm -rf src/styles/artdeco-*.scss
```

### Decision 7: Bloomberg Terminal设计风格

**决策**：采用Bloomberg Terminal暗色主题作为设计风格

**理由**：
- 符合专业金融工具定位
- 信息密度高
- 长时间使用不疲劳
- 国际专业标准

**替代方案**：
- **选项A**：浅色主题（拒绝：不适合长时间使用）
- **选项B**：自定义暗色主题（拒绝：需大量设计工作）

**实施**：
```scss
// Bloomberg暗色主题特征
- 背景：深灰/黑色系（#1a1a1a, #2d2d2d）
- 文本：高对比白色（#ffffff）
- 强调色：橙红色（#ff6b35）
- 涨跌色：绿色（#00d924）/红色（#ff4757）
- 字体：等宽字体用于数字（JetBrains Mono）
```

### Decision 8: 路由嵌套架构

**决策**：采用嵌套路由架构，每个功能域一个Layout组件

**理由**：
- 清晰的层级结构
- Layout组件复用
- 面包屑导航自动生成
- 符合Vue Router最佳实践

**替代方案**：
- **选项A**：扁平路由（拒绝：无法复用Layout）
- **选项B**：动态路由（拒绝：过度复杂）

**实施**：
```javascript
// router/index.js
{
  path: '/market',
  component: () => import('@/layouts/MarketLayout.vue'),
  children: [
    { path: 'list', component: MarketList },
    { path: 'realtime', component: RealTimeMonitor }
  ]
}
```

### Decision 9: 明确桌面端策略

**决策**：明确声明仅支持桌面端（1280x720+），不考虑移动端

**理由**：
- 专业量化交易工具需要大屏幕
- 移动端适配会牺牲桌面端性能
- 避免无效工作

**替代方案**：
- **选项A**：支持移动端（拒绝：成本高，收益低）
- **选项B**：响应式设计（拒绝：增加bundle大小30%）

**实施**：
```markdown
## 平台支持策略

**本项目仅支持 Web 桌面端** (1280x720+)

**不支持平台**：
- ❌ 移动设备（手机、平板）
- ❌ 触摸优化
- ❌ 响应式布局（@media queries for mobile）
```

---

## Risks / Trade-offs

### Risk 1: 用户学习曲线

**风险**：老用户习惯了旧菜单位置，新架构需要适应

**概率**：Medium
**影响**：Medium

**缓解措施**：
- ✅ 向后兼容重定向（旧URL自动跳转）
- ✅ 新功能引导教程（首次登录提示）
- ✅ Command Palette快速导航（降低学习成本）
- ✅ 渐进式发布（Phase by phase）

**应急方案**：
- 如果用户反馈强烈，保留"经典菜单"选项（可选切换）

### Risk 2: 样式迁移工作量

**风险**：迁移所有组件样式到Design Token工作量可能超出预期

**概率**：High
**影响**：Medium

**缓解措施**：
- ✅ Design Token优先建立（Phase 1）
- ✅ 分批迁移（先核心组件，后次要组件）
- ✅ 建立自动化检查（ESLint规则禁止硬编码颜色）
- ✅ 提供迁移脚本（自动替换常见模式）

**应急方案**：
- 如果时间不足，优先迁移核心页面（Dashboard, Market, Analysis）

### Risk 3: WebSocket连接稳定性

**风险**：单例模式可能成为单点故障，影响所有组件

**概率**：Low
**影响**：High

**缓解措施**：
- ✅ 自动重连机制（指数退避）
- ✅ 心跳检测（30秒ping）
- ✅ 连接状态管理（在线/离线提示）
- ✅ CPU降级方案（WebSocket失败时轮询API）

**应急方案**：
- 如果单例模式不稳定，回退到每个组件独立连接

### Risk 4: TypeScript strict模式导致编译错误

**风险**：启用strict模式可能暴露大量类型错误，阻塞开发

**概率**：Medium
**影响**：Medium

**缓解措施**：
- ✅ 渐进式迁移（allowJs: true共存）
- ✅ 优先迁移核心组件（30%）
- ✅ 使用 `@ts-ignore` 临时标记（逐步修复）
- ✅ 类型定义补全（`src/types/`目录）

**应急方案**：
- 如果strict模式阻塞严重，临时降级到 `checkJs: false`

### Risk 5: 性能优化回退

**风险**：代码分割、懒加载等优化可能导致页面加载变慢

**概率**：Low
**影响**：High

**缓解措施**：
- ✅ 每Phase性能基准测试（Lighthouse）
- ✅ 性能预算设置（Budgets: Bundle < 2.0MB）
- ✅ Core Web Vitals监控（CLS, FID, LCP）
- ✅ 性能回归告警（CI/CD集成）

**应急方案**：
- 如果性能下降，回滚到上一Phase的Git tag

---

## Migration Plan

### Phase-by-Phase Migration

**Phase 1: 基础架构重构** (3-4周)
```bash
# 创建Git tag
git tag -a phase1-design-token -m "Design Token系统完成"

# 验证
npm run build
npm run test

# 如果验证失败，回滚
git checkout phase1-design-token
```

**Phase 2: 菜单重构** (4-5周)
```bash
# 创建Git tag
git tag -a phase2-menu-refactor -m "菜单重构完成"

# 验证
npm run build
npm run test
npm run e2e

# 如果验证失败，回滚
git checkout phase2-menu-refactor
```

**Phase 3: 样式统一** (3-4周)
```bash
# 创建Git tag
git tag -a phase3-style-unification -m "样式统一完成"

# 验证
npm run build
npm run test
# 视觉回归测试（截图对比）

# 如果验证失败，回滚
git checkout phase3-style-unification
```

**Phase 4: 性能优化** (4-5周)
```bash
# 创建Git tag
git tag -a phase4-performance -m "性能优化完成"

# 验证
npm run build
npm run lighthouse  # Lighthouse性能测试
# Bundle大小检查

# 如果验证失败，回滚
git checkout phase4-performance
```

**Phase 5: 测试基础设施** (4-5周)
```bash
# 创建Git tag
git tag -a phase5-testing -m "测试基础设施完成"

# 验证
npm run test        # 单元测试
npm run e2e         # E2E测试
npm run coverage    # 覆盖率报告

# 如果验证失败，回滚
git checkout phase5-testing
```

### Rollback Plan

**单组件回滚**（30分钟）：
```bash
# 回滚单个组件
git revert <commit-hash>
npm install && npm run build
```

**单Phase回滚**（2小时）：
```bash
# 回滚到上一个Phase的tag
git checkout phase1-design-token
npm install && npm run build && npm run test
```

**完整回滚**（4小时）：
```bash
# 回滚到最初状态
git checkout main
git branch -D refactor-web-frontend-menu-architecture
npm install && npm run build
```

---

## Open Questions

### Q1: Command Palette是否需要本地存储用户偏好？

**问题**：是否需要记住用户最常用的功能，优化搜索结果排序？

**建议**：Phase 2先实现基础功能，Phase 4根据用户反馈决定是否添加

### Q2: WebSocket单例模式是否需要支持多个连接（备用连接）？

**问题**：是否需要实现主备连接切换机制，提升可用性？

**建议**：Phase 1实现单例 + 自动重连，Phase 4根据稳定性决定是否添加备用连接

### Q3: Design Token是否需要支持多主题切换（暗色/浅色）？

**问题**：是否需要预留主题切换能力（如未来的浅色主题）？

**建议**：Phase 1专注暗色主题，CSS变量架构支持未来扩展

### Q4: TypeScript迁移是否需要100%覆盖？

**问题**：是否所有代码都必须迁移到TypeScript？

**建议**：目标是90%覆盖率，允许10%辅助代码保持JavaScript（如配置文件）

---

## Implementation Notes

### 与其他OpenSpec变更的协调

**`frontend-optimization-six-phase`**（图表/AI/GPU功能）：
- **共享资源**：Design Token系统（避免重复工作）
- **避免冲突**：各自聚焦不同领域（菜单架构 vs 图表AI）
- **时间协调**：可并行开发，但需协调集成测试

### 代码审查检查清单

**新增代码必须满足**：
- [ ] 使用Design Token（禁止硬编码颜色/间距）
- [ ] TypeScript类型完整（无 `any` 类型）
- [ ] 单元测试覆盖率 > 80%
- [ ] E2E测试覆盖核心场景
- [ ] Lighthouse性能分数 > 80
- [ ] 无ESLint错误
- [ ] 无Console警告

**修改代码必须满足**：
- [ ] 向后兼容（路由重定向）
- [ ] 保持现有功能不变
- [ ] 性能不回退（Lighthouse对比）
- [ ] 视觉回归测试通过

---

**文档版本**: v1.0
**作者**: Claude Code (Main CLI)
**审核者**: Pending
**最后更新**: 2026-01-09
