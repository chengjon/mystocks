# MyStocks Vue前端ArtDeco集成修复实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 修复MyStocks Vue前端的ArtDeco集成问题，确保dayjs正常工作、ArtDeco组件被正确使用、设计系统完整集成，前端服务器稳定运行。

**Architecture:** 分阶段系统性修复，从底层依赖问题开始，逐步集成ArtDeco组件和设计系统，最后验证整体功能。采用最小化干预策略，确保每次修复都能验证结果。

**Tech Stack:** Vue 3 + Vite + TypeScript + Element Plus + ArtDeco组件库 + SCSS设计系统

## Phase 1: 修复dayjs问题

### Task 1.1: 分析dayjs导入错误原因

**Files:**
- Read: `web/frontend/package.json`
- Read: `web/frontend/vite.config.ts`
- Read: `web/frontend/src/components/market/LongHuBangPanel.vue`
- Read: `web/frontend/src/components/artdeco/specialized/ArtDecoDateRange.vue`

**Step 1: 检查当前dayjs状态**
检查package.json中dayjs版本是否正确
检查vite.config.ts中的exclude配置是否导致问题

**Step 2: 尝试恢复dayjs导入**
在LongHuBangPanel.vue中取消dayjs注释，测试导入是否成功

**Step 3: 运行前端开发服务器**
```bash
cd web/frontend
npm run dev
```
检查控制台是否还有dayjs相关错误

**Step 4: 提交修复**
```bash
git add web/frontend/src/components/market/LongHuBangPanel.vue
git commit -m "fix: restore dayjs import in LongHuBangPanel component"
```

### Task 1.2: 修复vite.config.ts中dayjs配置

**Files:**
- Modify: `web/frontend/vite.config.ts:157-164`

**Step 1: 移除dayjs的exclude配置**
从optimizeDeps.exclude中移除'dayjs'

**Step 2: 测试dayjs导入**
运行npm run dev，检查dayjs是否能正常导入

**Step 3: 清理缓存**
```bash
rm -rf web/frontend/node_modules/.vite
npm run dev
```

**Step 4: 提交配置修复**
```bash
git add web/frontend/vite.config.ts
git commit -m "fix: remove dayjs from vite optimizeDeps exclude"
```

### Task 1.3: 恢复所有组件中的dayjs使用

**Files:**
- Modify: `web/frontend/src/components/artdeco/specialized/ArtDecoDateRange.vue:26-27,50-61`

**Step 1: 取消ArtDecoDateRange中的dayjs注释**
恢复dayjs导入和相关功能

**Step 2: 测试组件功能**
运行前端服务器，检查ArtDecoDateRange组件是否正常工作

**Step 3: 提交dayjs恢复**
```bash
git add web/frontend/src/components/artdeco/specialized/ArtDecoDateRange.vue
git commit -m "fix: restore dayjs usage in ArtDecoDateRange component"
```

## Phase 2: 集成ArtDeco组件

### Task 2.1: 验证ArtDeco组件库结构

**Files:**
- Read: `web/frontend/src/components/artdeco/index.ts`
- Read: `web/frontend/src/components/artdeco/base/index.ts`
- Read: `web/frontend/src/components/artdeco/core/index.ts`
- Read: `web/frontend/src/components/artdeco/advanced/index.ts`
- Read: `web/frontend/src/components/artdeco/specialized/index.ts`

**Step 1: 检查组件导出**
验证所有组件都正确导出

**Step 2: 检查组件数量**
统计每个类别的组件数量

**Step 3: 验证组件文件存在性**
确保所有导出的组件文件都存在

### Task 2.2: 更新vite.config.ts的ArtDeco组件配置

**Files:**
- Modify: `web/frontend/vite.config.ts:57-62`

**Step 1: 确认ArtDeco组件目录配置正确**
确保dirs配置指向正确的artdeco目录

**Step 2: 测试组件自动导入**
运行构建检查components.d.ts是否生成

**Step 3: 提交配置更新**
```bash
git add web/frontend/vite.config.ts
git commit -m "fix: verify ArtDeco component auto-import configuration"
```

### Task 2.3: 替换现有Element Plus组件为ArtDeco组件

**Files:**
- Read: `web/frontend/src/App.vue`
- Read: `web/frontend/src/layout/index.vue`
- Modify: 需要更新的Vue文件

**Step 1: 识别需要替换的组件**
在App.vue和layout文件中查找Element Plus组件使用

**Step 2: 替换为ArtDeco组件**
将el-button等替换为ArtDecoButton等

**Step 3: 测试页面渲染**
运行前端服务器，检查页面是否正常显示

**Step 4: 提交组件替换**
```bash
git add web/frontend/src/App.vue web/frontend/src/layout/index.vue
git commit -m "feat: replace Element Plus components with ArtDeco components"
```

### Task 2.4: 更新路由和页面使用ArtDeco组件

**Files:**
- Read: `web/frontend/src/router/index.ts`
- Modify: 路由配置中的页面组件

**Step 1: 检查路由中使用的页面组件**
查看哪些页面需要更新

**Step 2: 在页面中使用ArtDeco组件**
更新页面模板使用ArtDeco组件

**Step 3: 测试路由导航**
确保所有页面都能正常导航

**Step 4: 提交页面更新**
```bash
git add web/frontend/src/router/index.ts
git commit -m "feat: update pages to use ArtDeco components"
```

## Phase 3: 集成ArtDeco设计系统

### Task 3.1: 验证ArtDeco样式文件

**Files:**
- Read: `web/frontend/src/styles/artdeco-tokens.scss`
- Read: `web/frontend/src/styles/artdeco-patterns.scss`
- Read: `web/frontend/src/main.js:16-27`

**Step 1: 检查样式文件完整性**
验证所有CSS变量都定义正确

**Step 2: 确认样式导入顺序**
检查main.js中的样式导入顺序是否正确

**Step 3: 测试样式应用**
运行前端服务器，检查ArtDeco样式是否生效

### Task 3.2: 更新样式导入配置

**Files:**
- Modify: `web/frontend/src/main.js:16-27`

**Step 1: 确保ArtDeco样式在最后导入**
调整样式导入顺序，确保ArtDeco样式有最高优先级

**Step 2: 添加缺失的样式导入**
如果有遗漏的样式文件，添加到导入列表

**Step 3: 测试样式覆盖**
检查ArtDeco样式是否正确覆盖Element Plus样式

**Step 4: 提交样式导入更新**
```bash
git add web/frontend/src/main.js
git commit -m "fix: update ArtDeco styles import order and completeness"
```

### Task 3.3: 验证CSS变量应用

**Files:**
- Read: `web/frontend/src/styles/element-plus-artdeco.scss`
- Read: `web/frontend/src/styles/bloomberg-terminal-override.scss`

**Step 1: 检查CSS变量使用**
验证ArtDeco CSS变量在样式文件中正确使用

**Step 2: 测试变量解析**
运行构建检查是否有CSS变量错误

**Step 3: 修复变量引用问题**
如果有变量未定义，添加缺失的定义

**Step 4: 提交CSS变量修复**
```bash
git add web/frontend/src/styles/element-plus-artdeco.scss
git commit -m "fix: verify and fix ArtDeco CSS variables usage"
```

## Phase 4: 验证修复效果

### Task 4.1: 运行Playwright测试

**Files:**
- Run: `web/frontend/playwright.config.ts`

**Step 1: 启动测试环境**
```bash
cd web/frontend
npm run test:e2e
```

**Step 2: 检查测试结果**
验证所有测试是否通过

**Step 3: 修复失败的测试**
根据测试结果修复问题

**Step 4: 提交测试修复**
```bash
git add web/frontend/tests/
git commit -m "fix: resolve failing Playwright tests"
```

### Task 4.2: 验证前端服务器稳定性

**Files:**
- Run: `web/frontend/package.json`

**Step 1: 启动前端服务器**
```bash
cd web/frontend
npm run dev
```

**Step 2: 测试页面加载**
检查页面是否正常渲染，无空白内容

**Step 3: 测试导航功能**
验证所有路由都能正常工作

**Step 4: 检查控制台错误**
确保没有JavaScript运行时错误

### Task 4.3: 验证ArtDeco风格应用

**Files:**
- Inspect: 浏览器开发者工具

**Step 1: 检查ArtDeco组件使用**
验证页面中使用了ArtDeco组件

**Step 2: 检查设计系统应用**
确认ArtDeco颜色、字体、间距等都正确应用

**Step 3: 测试响应式设计**
验证在不同屏幕尺寸下的显示效果

**Step 4: 提交验证报告**
```bash
# 创建验证报告
echo "# ArtDeco集成验证报告
- ✅ dayjs正常工作
- ✅ ArtDeco组件正常使用
- ✅ 设计系统正确应用
- ✅ 前端服务器稳定运行
- ✅ 页面内容正常显示" > docs/reports/artdeco-integration-verification.md

git add docs/reports/artdeco-integration-verification.md
git commit -m "docs: add ArtDeco integration verification report"
```