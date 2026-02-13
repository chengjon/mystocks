# ArtDeco Design System Governance Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 建立 ArtDeco 设计系统“单一事实源（Single Source of Truth）”与自动治理机制，消除 token、文档、组件目录规范之间的漂移。

**Architecture:** 以 `artdeco-tokens.scss` + 轻量治理清单（manifest）作为事实源，新增自动校验脚本覆盖「token 使用规范 / 文档口径 / 目录铁律」。实现上只做治理与一致性改进，不引入新的视觉风格分支，保持现有 ArtDeco 生态稳定。

**Tech Stack:** Vue 3, SCSS, Node.js scripts, Stylelint, Vitest, Playwright (existing), OpenSpec。

---

### Task 0: OpenSpec 变更提案（先审批，后实现）

**Files:**
- Create: `openspec/changes/update-artdeco-design-governance/proposal.md`
- Create: `openspec/changes/update-artdeco-design-governance/tasks.md`
- Create: `openspec/changes/update-artdeco-design-governance/specs/artdeco-design-system/spec.md`

**Step 1: 写提案草案（为什么/改什么/影响）**

在 `proposal.md` 明确：
- Why: 当前文档与实现存在口径漂移（例如 v2/v3 叙述混杂）
- What: 建立治理清单、校验脚本、文档统一口径
- Impact: 不改变业务行为，只增强一致性与可维护性

**Step 2: 写任务清单**

在 `tasks.md` 中列出实现步骤，要求每项可独立验收。

**Step 3: 写 spec delta**

在 `spec.md` 用 `## ADDED Requirements` 增加治理要求（含 Scenario）。

**Step 4: 运行提案校验**

Run: `openspec validate update-artdeco-design-governance --strict`  
Expected: 校验通过，无格式错误。

**Step 5: 等待审批通过**

在 proposal 获批前，不进入实现步骤。

---

### Task 1: 建立 ArtDeco 治理清单（manifest）

**Files:**
- Create: `web/frontend/src/styles/artdeco-governance-manifest.json`
- Test: `web/frontend/tests/unit/styles/artdeco-governance-manifest.spec.ts`

**Step 1: 写失败测试（结构与关键字段）**

```ts
import manifest from '@/styles/artdeco-governance-manifest.json'
import { describe, it, expect } from 'vitest'

describe('artdeco governance manifest', () => {
  it('contains required sections', () => {
    expect(manifest.tokens).toBeDefined()
    expect(manifest.typography).toBeDefined()
    expect(manifest.spacing).toBeDefined()
    expect(manifest.docs).toBeDefined()
  })
})
```

**Step 2: 运行测试确认失败**

Run: `cd web/frontend && npm run test -- tests/unit/styles/artdeco-governance-manifest.spec.ts`  
Expected: FAIL（文件不存在或字段缺失）。

**Step 3: 写最小实现**

在 `artdeco-governance-manifest.json` 填入：
- token 版本与关键变量白名单
- 字体（Cinzel/Barlow/JetBrains Mono）
- 11 级 spacing 映射
- 核心文档路径列表

**Step 4: 运行测试确认通过**

Run: `cd web/frontend && npm run test -- tests/unit/styles/artdeco-governance-manifest.spec.ts`  
Expected: PASS。

**Step 5: Commit**

```bash
git add web/frontend/src/styles/artdeco-governance-manifest.json web/frontend/tests/unit/styles/artdeco-governance-manifest.spec.ts
git commit -m "feat(artdeco): add governance manifest baseline"
```

---

### Task 2: 统一核心文档口径（v3 基线）

**Files:**
- Modify: `docs/guides/ARTDECO_MASTER_INDEX.md`
- Modify: `web/frontend/ARTDECO_COMPONENTS_CATALOG.md`
- Modify: `docs/api/ArtDeco_System_Architecture_Summary.md`
- Modify: `docs/guides/ARTDECO_COMPONENT_GUIDE.md`

**Step 1: 写失败测试（文档口径关键字）**

Create test: `web/frontend/tests/unit/styles/artdeco-docs-consistency.spec.ts`

```ts
it('uses v3 governance language consistently', () => {
  expect(indexText).toContain('ArtDeco v3')
  expect(indexText).not.toContain('v2.0 Design System')
})
```

**Step 2: 运行测试确认失败**

Run: `cd web/frontend && npm run test -- tests/unit/styles/artdeco-docs-consistency.spec.ts`  
Expected: FAIL（当前文档存在旧口径）。

**Step 3: 写最小实现（仅口径与引用修正）**

- 统一为 v3/v3.1 术语
- 校正文档描述与组件规模说明
- 保留历史文档链接但标注归档/历史

**Step 4: 运行测试确认通过**

Run: `cd web/frontend && npm run test -- tests/unit/styles/artdeco-docs-consistency.spec.ts`  
Expected: PASS。

**Step 5: Commit**

```bash
git add docs/guides/ARTDECO_MASTER_INDEX.md web/frontend/ARTDECO_COMPONENTS_CATALOG.md docs/api/ArtDeco_System_Architecture_Summary.md docs/guides/ARTDECO_COMPONENT_GUIDE.md web/frontend/tests/unit/styles/artdeco-docs-consistency.spec.ts
git commit -m "docs(artdeco): align v3 governance wording and references"
```

---

### Task 3: 强化 Token 使用校验脚本

**Files:**
- Modify: `web/frontend/scripts/check-artdeco-tokens.js`
- Modify: `web/frontend/package.json`
- Test: `web/frontend/tests/unit/scripts/check-artdeco-tokens.spec.ts`

**Step 1: 写失败测试（重复变量/误报场景）**

```ts
it('flags duplicate custom properties and ignores comments', async () => {
  const result = await runChecker(sampleCss)
  expect(result.errors).toContain('duplicate custom property')
})
```

**Step 2: 运行测试确认失败**

Run: `cd web/frontend && npm run test -- tests/unit/scripts/check-artdeco-tokens.spec.ts`  
Expected: FAIL。

**Step 3: 写最小实现**

在脚本中新增：
- 自定义属性重复定义检测
- 更精确的样式块解析（减少 template/script 误报）
- 可配置白名单（如 `1px` 边框）

并新增 npm script：`"lint:artdeco:strict": "node scripts/check-artdeco-tokens.js --strict"`

**Step 4: 运行测试确认通过**

Run: `cd web/frontend && npm run test -- tests/unit/scripts/check-artdeco-tokens.spec.ts`  
Expected: PASS。

**Step 5: Commit**

```bash
git add web/frontend/scripts/check-artdeco-tokens.js web/frontend/package.json web/frontend/tests/unit/scripts/check-artdeco-tokens.spec.ts
git commit -m "feat(artdeco): harden token lint with strict governance checks"
```

---

### Task 4: 将治理检查接入日常验证流程

**Files:**
- Modify: `web/frontend/package.json`
- Modify: `docs/guides/ARTDECO_COMPONENT_GUIDE.md`
- Modify: `docs/guides/ARTDECO_MASTER_INDEX.md`

**Step 1: 写失败测试（命令可发现性）**

Create: `web/frontend/tests/unit/styles/artdeco-governance-cli.spec.ts`

```ts
it('exposes governance check script', () => {
  expect(pkg.scripts['lint:artdeco:strict']).toBeTruthy()
})
```

**Step 2: 运行测试确认失败**

Run: `cd web/frontend && npm run test -- tests/unit/styles/artdeco-governance-cli.spec.ts`  
Expected: FAIL。

**Step 3: 写最小实现**

- 在 package scripts 中加入治理命令
- 在指南文档中增加“提交前治理校验”步骤

**Step 4: 运行测试与治理命令**

Run: `cd web/frontend && npm run test -- tests/unit/styles/artdeco-governance-cli.spec.ts`  
Expected: PASS。

Run: `cd web/frontend && npm run lint:artdeco:strict`  
Expected: 输出治理检查结果，出现违规时非零退出。

**Step 5: Commit**

```bash
git add web/frontend/package.json docs/guides/ARTDECO_COMPONENT_GUIDE.md docs/guides/ARTDECO_MASTER_INDEX.md web/frontend/tests/unit/styles/artdeco-governance-cli.spec.ts
git commit -m "chore(artdeco): integrate governance checks into frontend workflow"
```

---

### Task 5: 端到端验证与回归

**Files:**
- Test: `web/frontend/design-token.test.ts` (existing)
- Test: `web/frontend/bloomberg-style.test.ts` (existing)

**Step 1: 运行单元测试（本次新增）**

Run: `cd web/frontend && npm run test -- tests/unit/styles tests/unit/scripts`  
Expected: PASS。

**Step 2: 运行既有设计回归测试**

Run: `cd web/frontend && npm run test:design-token`  
Expected: PASS。

Run: `cd web/frontend && npm run test:bloomberg`  
Expected: PASS。

**Step 3: 运行类型检查**

Run: `cd web/frontend && npm run type-check`  
Expected: PASS（或仅存在已知历史告警）。

**Step 4: 汇总变更说明**

将“治理能力、检查命令、失败示例”写入发布说明或 `TASK-REPORT.md`。

**Step 5: Commit（若前序尚有未提交项）**

```bash
git add -A
git commit -m "test(artdeco): verify governance pipeline and visual regression"
```

---

## 验收标准（Done）

- ArtDeco 文档入口、架构、组件目录、开发指南口径统一为 v3 基线。
- Token 治理清单存在且可被测试验证。
- `lint:artdeco:strict` 能稳定识别硬编码与重复 token 问题。
- 既有视觉回归（design-token/bloomberg）在治理改造后保持通过。
- OpenSpec change 通过 `--strict` 校验并处于已审批状态。
