# Web Frontend V2导航系统规范

> **专题方案说明**:
> 本文件用于描述某一专题能力的规格边界、变更提案或专题约束，服务于 OpenSpec 的方案管理与差异追踪。
> 它不自动等同于“当前已上线实现”或仓库共享治理规则的唯一真相源；执行时需同时核对 `architecture/STANDARDS.md`、审批状态、当前代码实现以及相关 `openspec/specs/` 正式规格。


**Specification ID**: `web-frontend-navigation-v2`
**Status**: 🔄 Ready for Implementation
**Version**: 1.0
**Created**: 2026-01-21
**Author**: Claude Code (Main CLI)

---

## 📋 规范概述

本规范定义了MyStocks Web前端V2导航系统的技术要求和验收标准。该系统旨在将29个ArtDeco页面组件集成到统一的路由和菜单系统中，提供完整的用户导航体验。

### 规范范围

- **路由系统**: 29个ArtDeco组件的路由配置
- **菜单系统**: 基于域分组的菜单结构
- **API集成**: 120+后端API端点的集成
- **实时更新**: WebSocket支持的市场数据推送
- **类型安全**: TypeScript严格类型定义

### 规范约束

- **技术栈**: Vue 3.4+, TypeScript 5.0+, Vue Router 4.x
- **设计系统**: ArtDeco (金色主题 #D4AF37)
- **后端API**: FastAPI (Port 8000)
- **部署**: PM2进程管理
- **质量门禁**: TypeScript错误 < 100

---

## 功能需求

### FR-1: 路由系统

**需求描述**: 系统必须提供完整的路由配置，支持29个ArtDeco页面组件的访问。

**验收标准**:
- [ ] 所有29个组件可通过URL直接访问
- [ ] 路由配置使用懒加载模式
- [ ] 路由元信息包含完整信息（title, icon, breadcrumb, apiEndpoint等）
- [ ] 404错误正确处理
- [ ] 路由跳转无控制台错误

**测试用例**:
```typescript
describe('Router Configuration', () => {
  it('should have 29+ routes registered', () => {
    const router = createRouter()
    const routes = router.getRoutes()
    expect(routes.length).toBeGreaterThanOrEqual(29)
  })

  it('should navigate to trading signals page', async () => {
    const router = createRouter()
    await router.push('/trading/signals')
    expect(router.currentRoute.value.name).toBe('trading-signals')
  })
})
```

**优先级**: P0 (Must Have)

---

### FR-2: 菜单系统

**需求描述**: 系统必须提供分组的菜单系统，支持5大域（Trading, Strategy, Market, Risk, System）。

**验收标准**:
- [ ] 菜单按域分组显示
- [ ] 每个菜单项包含图标、标签、描述
- [ ] 实时更新的菜单项显示动态指示器
- [ ] 菜单点击正确跳转
- [ ] 当前路由菜单项高亮显示

**UI规格**:
```
┌──────────────────────────────┐
│ Trading ⚡                   │
│   📡 交易信号 ●             │  ← 实时更新指示器
│   📋 交易历史                │
│   📊 持仓监控                │
│   📈 交易统计                │
├──────────────────────────────┤
│ Strategy ⚙️                  │
│   ⚙️ 策略管理                │
│   🎯 策略优化                │
│   🔬 回测分析                │
└──────────────────────────────┘
```

**优先级**: P0 (Must Have)

---

### FR-3: API集成

**需求描述**: 系统必须集成现有的120+后端API端点，支持数据获取和展示。

**验收标准**:
- [ ] 所有API调用使用统一的apiClient
- [ ] API响应符合UnifiedResponse<T>格式
- [ ] API错误正确处理和显示
- [ ] API超时和重试机制
- [ ] API调用日志记录

**性能要求**:
- API响应时间 < 2秒 (95th percentile)
- API重试次数最多3次
- API超时时间10秒

**优先级**: P0 (Must Have)

---

### FR-4: 实时数据更新

**需求描述**: 系统必须支持WebSocket实时数据推送，用于市场数据和交易信号。

**验收标准**:
- [ ] WebSocket连接自动建立
- [ ] 支持频道订阅和取消订阅
- [ ] 连接断开自动重连（最多5次）
- [ ] 实时数据更新显示到UI
- [ ] WebSocket状态显示

**频道清单**:
- `trading:signals` - 交易信号
- `market:realtime` - 实时行情
- `market:quotes` - 市场报价
- `risk:alerts` - 风险告警

**优先级**: P1 (Should Have)

---

### FR-5: 面包屑导航

**需求描述**: 系统必须提供面包屑导航，显示当前页面在菜单结构中的位置。

**验收标准**:
- [ ] 面包屑显示完整路径（如：Trading > Signals）
- [ ] 面包屑支持点击跳转
- [ ] 面包屑自动从路由元信息生成
- [ ] 面包屑样式符合ArtDeco设计

**UI规格**:
```
Home > Trading > Signals
```

**优先级**: P0 (Must Have)

---

## 非功能需求

### NFR-1: 性能

**需求描述**: 系统必须满足性能要求，提供流畅的用户体验。

**性能指标**:
| 指标 | 目标 | 测量方法 |
|------|------|----------|
| 首屏加载时间 | < 2秒 | Lighthouse |
| 页面切换时间 | < 500ms | Performance API |
| Time to Interactive | < 3秒 | Lighthouse |
| Bundle大小 | < 500KB (gzipped) | Build report |

**优化策略**:
- 路由懒加载
- API响应缓存
- 组件代码分割
- 虚拟滚动（长列表）

**优先级**: P0 (Must Have)

---

### NFR-2: 类型安全

**需求描述**: 系统必须严格使用TypeScript类型，避免运行时类型错误。

**质量指标**:
| 指标 | 当前 | 目标 |
|------|------|------|
| TypeScript错误 | 90 | < 80 |
| any类型使用 | 15处 | 0 |
| 类型覆盖率 | 85% | 95% |

**验收标准**:
- [ ] 无`any`类型使用
- [ ] 所有API响应有类型定义
- [ ] 所有组件Props有类型定义
- [ ] 所有路由meta有类型定义

**优先级**: P0 (Must Have)

---

### NFR-3: 浏览器兼容性

**需求描述**: 系统必须在主流桌面浏览器上正常运行。

**支持浏览器**:
- Chrome 120+ ✅
- Firefox 120+ ✅
- Safari 17+ ✅
- Edge 120+ ✅

**不支持**:
- ❌ 移动浏览器
- ❌ 平板浏览器
- ❌ IE11

**测试方法**: Playwright跨浏览器测试

**优先级**: P1 (Should Have)

---

### NFR-4: 可访问性

**需求描述**: 系统必须满足基本的可访问性要求。

**验收标准**:
- [ ] 所有交互元素可键盘访问
- [ ] 所有图片有alt文本
- [ ] 颜色对比度 >= 4.5:1
- [ ] 表单输入有标签
- [ ] 焦点状态可见

**测试工具**: Axe DevTools

**优先级**: P2 (Could Have)

---

## 技术约束

### TC-1: 设计系统

**约束**: 所有页面必须使用ArtDeco设计系统。

**设计令牌**:
```css
--artdeco-bg-global: #0A0A0A;
--artdeco-gold-primary: #D4AF37;
--artdeco-gold-hover: #F2E8C4;
--artdeco-border-default: rgba(212, 175, 55, 0.2);
--artdeco-font-heading: 'Marcellus', serif;
--artdeco-font-body: 'Josefin Sans', sans-serif;
```

**验证方法**: CSS变量检查

---

### TC-2: 组件库

**约束**: 必须使用现有的ArtDeco组件库（64个组件）。

**可用组件**:
- Base组件: 13个（ArtDecoCard, ArtDecoButton, 等）
- Core组件: 11个（ArtDecoBreadcrumb, ArtDecoTopBar, 等）
- Specialized组件: 30个（ArtDecoTable, ArtDecoFilterBar, 等）
- Advanced组件: 10个

**禁止**:
- ❌ 创建重复的组件
- ❌ 使用其他UI库（Element Plus除外）

**优先级**: P0 (Must Have)

---

### TC-3: API后端

**约束**: 必须使用现有的FastAPI后端（Port 8000）。

**API端点总数**: 120+

**API域名**:
- `/api/market/*` - 市场数据
- `/api/trading/*` - 交易管理
- `/api/strategy/*` - 策略管理
- `/api/analysis/*` - 投资分析
- `/api/monitoring/*` - 监控

**CORS配置**: 前端端口3000-3009已授权

---

## 数据模型

### DM-1: 路由元信息

```typescript
interface RouteMeta {
  title: string                    // 页面标题
  icon: string                     // 图标 (emoji)
  breadcrumb: string               // 面包屑文本
  requiresAuth: boolean            // 认证要求
  apiEndpoint?: string             // API端点
  apiMethod?: 'GET' | 'POST'       // API方法
  liveUpdate?: boolean             // 实时更新
  wsChannel?: string               // WebSocket频道
  priority?: 'primary' | 'secondary' // 菜单优先级
}
```

### DM-2: 菜单项

```typescript
interface MenuItem {
  path: string                     // 路由路径
  label: string                    // 显示标签
  icon: string                     // 图标
  description: string              // 描述
  apiEndpoint: string              // API端点
  apiMethod: 'GET' | 'POST' | 'PUT' | 'DELETE'
  liveUpdate: boolean              // 实时更新
  wsChannel?: string               // WebSocket频道
  priority: 'primary' | 'secondary'
}
```

### DM-3: 统一API响应

```typescript
interface UnifiedResponse<T = any> {
  success: boolean                 // 成功标志
  code: number                     // 状态码
  message: string                  // 消息
  data: T                          // 数据
  timestamp: string                // 时间戳
  request_id: string               // 请求ID
  errors: Record<string, string[]> | null  // 错误详情
}
```

---

## 集成点

### IN-1: ArtDecoLayout集成

**集成方式**: 所有路由使用ArtDecoLayout作为父组件

```typescript
{
  path: '/trading',
  component: () => import('@/layouts/ArtDecoLayout.vue'),
  children: [
    // 子路由
  ]
}
```

**集成组件**:
- ArtDecoBreadcrumb
- ArtDecoTopBar
- ArtDecoFooter (可选)

---

### IN-2: API Client集成

**集成方式**: 通过apiClient统一调用后端API

```typescript
import apiClient from '@/api/apiClient'

const response = await apiClient.get<UnifiedResponse<DataType>>(
  '/api/endpoint'
)
```

**拦截器**:
- Request: 添加auth token
- Response: 统一错误处理

---

### IN-3: WebSocket集成

**集成方式**: 通过WebSocketService订阅实时数据

```typescript
import { wsService } from '@/services/websocketService'

wsService.subscribe('channel:name', (data) => {
  // 处理实时数据
})
```

**连接管理**:
- 自动重连
- 订阅管理
- 错误处理

---

## 测试策略

### TS-1: 单元测试

**范围**: Service层和工具函数

**工具**: Vitest

**覆盖率目标**: >80%

```typescript
describe('Market Adapter', () => {
  it('should fetch market overview', async () => {
    // 测试代码
  })
})
```

---

### TS-2: 集成测试

**范围**: API集成和数据流

**工具**: Vitest + MSW (Mock Service Worker)

```typescript
describe('API Integration', () => {
  it('should integrate with backend API', async () => {
    // 测试代码
  })
})
```

---

### TS-3: E2E测试

**范围**: 完整用户流程

**工具**: Playwright

**测试脚本**: `run-comprehensive-e2e.js`

**关键测试场景**:
1. 导航到所有29个页面
2. 验证面包屑导航
3. 验证菜单点击跳转
4. 验证API数据加载
5. 验证实时数据更新

---

## 部署策略

### DS-1: 开发环境

**命令**:
```bash
cd web/frontend
npm run dev -- --port 3001
```

**配置**: Vite dev server

---

### DS-2: 生产环境

**命令**:
```bash
npm run build
pm2 start ecosystem.config.js
```

**进程管理**: PM2 cluster模式 (2 instances)

**健康检查**:
- 前端健康检查端点
- PM2进程监控
- 日志聚合

---

## 验收标准

### AC-1: 功能完整性

- [ ] 所有29个页面可访问
- [ ] 菜单系统完整
- [ ] API集成完整
- [ ] WebSocket实时更新正常

### AC-2: 质量标准

- [ ] TypeScript错误 < 80
- [ ] 单元测试覆盖率 > 80%
- [ ] E2E测试全部通过
- [ ] Lighthouse分数 > 90

### AC-3: 性能标准

- [ ] 首屏加载 < 2秒
- [ ] 页面切换 < 500ms
- [ ] Bundle大小 < 500KB

### AC-4: 文档完整性

- [ ] 路由配置文档
- [ ] API集成文档
- [ ] 组件使用文档
- [ ] 部署文档

---

## 风险和缓解措施

### RISK-1: TypeScript错误增加

**风险**: 新增代码可能引入更多TypeScript错误

**概率**: Medium

**影响**: High（影响质量门禁）

**缓解措施**:
1. 严格遵循TypeScript最佳实践
2. 从源头定义精确类型
3. 避免使用`any`类型
4. 持续监控错误数量

---

### RISK-2: API性能问题

**风险**: 后端API响应慢，影响前端性能

**概率**: Medium

**影响**: High（影响用户体验）

**缓解措施**:
1. 实施API响应缓存
2. 添加loading状态
3. 设置合理的超时时间
4. 实施重试机制

---

### RISK-3: WebSocket连接不稳定

**风险**: WebSocket连接频繁断开

**概率**: Low

**影响**: Medium（实时数据受影响）

**缓解措施**:
1. 实施自动重连机制
2. 添加连接状态指示
3. 提供降级方案（轮询）
4. 监控连接质量

---

## 版本控制

### v1.0 (2026-01-21)

**初始版本**:
- 29个ArtDeco组件路由集成
- 5大域菜单系统
- API集成框架
- WebSocket实时更新支持
- TypeScript类型安全

---

## 附录

### A: 组件清单

详见 `proposal.md` 第三章 "现有ArtDeco组件清单"

### B: API端点清单

详见 `docs/api/README_PLATFORM.md`

### C: 相关文档

- **设计文档**: `design.md`
- **任务清单**: `tasks.md`
- **项目提案**: `proposal.md`

---

**规范版本**: v1.0
**最后更新**: 2026-01-21
**维护者**: Claude Code (Main CLI)
**审批状态**: ✅ Ready for Implementation
