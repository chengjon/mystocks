# TypeScript Extension System Repo-Truth Guide

> **权威来源声明**:
> 本文件是专题说明或状态说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

> **边界说明**:
> 本文档描述 `web/frontend/src/api/types/extensions/` 在当前仓库中的真实落地方式，用于指导日常维护、扩展与验证。
> 它不是历史实施方案的复述，也不替代 `architecture/STANDARDS.md`、OpenSpec proposal/design/specs 或前端全局质量门禁。
> 若方案文档、历史报告与当前代码不一致，应以当前代码、实际脚本输出与验证结果为准。

## 1. 当前结构

当前扩展类型系统的核心路径是：

- `web/frontend/src/api/types/extensions/index.ts`
- `web/frontend/src/api/types/extensions/strategy.ts`
- `web/frontend/src/api/types/extensions/common.ts`
- `web/frontend/src/api/types/extensions/ui.ts`
- `web/frontend/src/api/types/extensions/market/index.ts`
- `web/frontend/src/api/types/extensions/market/types-1.ts`
- `web/frontend/src/api/types/extensions/market/types-2.ts`

主类型入口是：

- `web/frontend/src/api/types/index.ts`

当前 repo-truth 不是把扩展类型直接平铺到顶层，而是通过命名空间方式公开：

```ts
export * as extensions from "./extensions";
```

这样做的原因很直接：

- 允许 `src/api/types/index.ts` 暴露扩展系统的统一入口
- 保持旧的顶层导出面不被 `extensions/common.ts` 中的 `APIResponse`、`PaginatedResponse`、`PaginationParams` 等名字污染
- 为后续继续扩展 `extensions/` 提供稳定边界

## 2. 命名约定

当前扩展类型的 repo-truth 命名约定是：

- 前端 ViewModel / UI-facing 类型优先使用 `*VM`
  - 例如 `StrategyVM`、`BacktestResultVM`、`PositionVM`
- 生成层或后端契约层的现有名字保持原状
  - 例如 `PositionItem`
- 共享工具型类型允许保留短名或通用名
  - 例如 `list<T>`、`date_type`
- 新增扩展类型时，默认不要复用已经在 `src/api/types/common/all.ts` 或其他顶层 barrel 公开过的名字
  - 如果语义不同，优先新增 `*VM`、`*View`、`*Summary` 这类后缀

一句话规则：

- 生成层保持契约名
- 扩展层优先显式区分 ViewModel / frontend-only 语义

## 3. 导入建议

当前推荐优先级是：

1. 直接从扩展域文件导入具体类型
2. 仅在需要“统一发现入口”时再使用根 barrel 的 `extensions` 命名空间
3. 如需验证 legacy root exports 与扩展层能否共存，可参考 compile-time smoke fixture：
   - `web/frontend/src/api/types/compatibility-smoke.ts`

推荐示例：

```ts
import type { StrategyVM, BacktestResultVM } from "@/api/types/extensions/strategy";
import type { MarketOverviewVM, KLineChartData } from "@/api/types/extensions/market";
import type { PositionVM, APIResponseVM } from "@/api/types/extensions/common";
import type { FormField, FormValidationSchema } from "@/api/types/extensions/ui";
```

如果只是做入口发现或文档化引用，也可以通过根 barrel 访问：

```ts
import { extensions } from "@/api/types";

type StrategyVM = extensions.StrategyVM;
type PositionVM = extensions.PositionVM;
```

不推荐的做法：

- 新增顶层 `export * from "./extensions"` 式平铺导出
- 在 `extensions/` 内继续制造与 `common/all.ts` 顶层公开类型同名、但语义不同的名字

## 4. 维护脚本

当前这套系统依赖 5 个本地脚本：

- `node scripts/validate-types.js`
  - 校验扩展目录、关键入口文件和主索引扩展导出是否存在
- `node scripts/check-type-conflicts.js`
  - 检查当前公开 surface 是否存在冲突
- `node scripts/audit-type-extension-quality.js`
  - 输出命名约定、顶层 JSDoc 覆盖情况，以及当前仍未被 `web/frontend/src` 消费的扩展类型清单
  - 当前会把 `list`、`date_type` 视为 repo-truth 允许保留的 legacy utility aliases，而不是命名违规
- `node scripts/generate-type-usage.js`
  - 输出扩展文件数、导出类型数、主索引扩展导出模式等 JSON summary
- `node scripts/generate-type-validation-report.js`
  - 归并 `validate-types`、`check-type-conflicts`、`audit-type-extension-quality`、`generate-type-usage` 和 `npm run type-check`
  - 默认把 JSON artifact 写入 `reports/analysis/typescript-extension-validation/`
  - 会同时生成：
    - 时间戳报告：`YYYYMMDDTHHMMSSZ-type-extension-validation-report.json`
    - 最新指针：`latest.json`
- `node scripts/generate-type-health-dashboard.js`
  - 读取 `type:report` 生成的 `latest.json`
  - 默认把静态 dashboard 写入 `reports/analysis/typescript-extension-validation/dashboard/`
  - 会同时生成：
    - 时间戳 HTML：`YYYYMMDDTHHMMSSZ-type-extension-health-dashboard.html`
    - 最新指针：`latest.html`

常用验证命令：

```bash
cd web/frontend
node scripts/validate-types.js
node scripts/check-type-conflicts.js
node scripts/audit-type-extension-quality.js
node scripts/generate-type-usage.js
node scripts/generate-type-validation-report.js
node scripts/generate-type-health-dashboard.js
npm run type-check
```

当前 `tsconfig.json` 已不再排除 `src/api/types/extensions/**/*`，因此 `npm run type-check` 会真实覆盖扩展类型，而不是绕过它们。

## 5. 新增类型时的最小流程

推荐按这个顺序做：

1. 选对域文件
   - strategy -> `extensions/strategy.ts`
   - market -> `extensions/market/*`
   - common utility / ViewModel helper -> `extensions/common.ts`
   - form / UI metadata -> `extensions/ui.ts`
2. 先确认名字不会和现有顶层公开 surface 冲突
3. 如有新的 market 子模块导出，先更新 `extensions/market/index.ts`
4. 跑脚本：
   - `node scripts/validate-types.js`
   - `node scripts/check-type-conflicts.js`
   - `node scripts/audit-type-extension-quality.js`
   - `npm run type-check`
5. 若需要统计或留存 artifact，再跑：
   - `node scripts/generate-type-usage.js`
   - `node scripts/generate-type-validation-report.js`

## 6. 常见边界

### 6.1 这套系统是不是自动生成的？

不是。当前 `extensions/` 是人工维护的 frontend-specific 类型层，不属于 `generate_frontend_types.py` 的自动生成产物。

### 6.2 为什么不直接导出到根索引顶层？

因为当前仓库已有顶层类型面，直接平铺会与现有 `common/all.ts` 公开名字发生冲突。命名空间导出是当前兼容性最稳的 repo-truth。

### 6.3 `TypeValidator.ts` 是不是已经成为主验证入口？

不是。当前真正可运行、可复核的本地入口是：

- `scripts/validate-types.js`
- `scripts/check-type-conflicts.js`
- `scripts/generate-type-usage.js`

`src/api/types/tools/validators/TypeValidator.ts` 仍是占位型实现，不能把它误当成当前主链路验证器。

### 6.4 质量审计是不是已经等于“无技术债”？

不是。当前质量审计脚本只证明两件事：

- 现有扩展类型名字符合当前 repo-truth 约定
- 顶层导出都有对应 JSDoc 注释

它不会把“仍未消费的扩展类型”自动洗成完成项。当前 `audit-type-extension-quality.js` 仍会报告一批未在 `web/frontend/src` 中被引用的扩展类型，因此 `No unused type definitions` 继续属于开放治理项，而不是已闭环项。

### 6.5 自动报告和单次脚本检查的区别是什么？

单次脚本检查适合本地快速确认：

- `validate-types`
- `check-type-conflicts`
- `audit-type-extension-quality`
- `type-check`

自动报告适合把这几项结果固定成可审计 artifact。当前推荐命令是：

```bash
cd web/frontend
node scripts/generate-type-validation-report.js
node scripts/generate-type-health-dashboard.js
```

如果需要指定输出目录：

```bash
cd web/frontend
node scripts/generate-type-validation-report.js --report-dir ../../reports/analysis/typescript-extension-validation
node scripts/generate-type-health-dashboard.js --report-dir ../../reports/analysis/typescript-extension-validation
```

当前 dashboard 是 repo-owned 的静态 HTML artifact，不依赖额外服务或运行时面板。它聚焦当前最重要的 repo-truth 信号：

- overall validation status
- validation / conflicts / naming / jsdoc / typecheck 五项检查结果
- exported extension type 数量
- 当前未使用扩展类型数量及名称

### 6.6 仓库里有没有“兼容性 smoke”证据？

有。当前 repo-truth 的 compile-time smoke fixture 是：

- `web/frontend/src/api/types/compatibility-smoke.ts`

它专门用于让 `npm run type-check` 同时覆盖：

- 旧的根级导出：`APIResponse`、`PaginationParams`、`UnifiedResponse`
- 新的扩展层导出：`StrategyVM`、`FormField`

这不是运行时模块，也不是业务页面依赖；它只是一个最小编译时夹具，用来证明“新增 `extensions` 命名空间之后，现有根级导出没有被破坏”。

## 7. 回滚计划

如果本专题扩展层在本地开发或专题分支上引入回归，当前 repo-truth 的最小回滚顺序是：

1. 回退 `web/frontend/src/api/types/index.ts` 中的 `export * as extensions from "./extensions";`
2. 删除或回退 `web/frontend/src/api/types/extensions/` 下新增或修改的专题类型
3. 删除或回退 `web/frontend/src/api/types/compatibility-smoke.ts`
4. 回退专题脚本入口：
   - `type:validate`
   - `type:check:conflicts`
   - `type:audit:quality`
   - `type:usage`
   - `type:report`
   - `type:dashboard`
5. 重新执行：
   - `node scripts/validate-types.js`
   - `node scripts/check-type-conflicts.js`
   - `npm run type-check`

如果只是某一批新增扩展类型有问题，而不是整套扩展系统失败，优先按 micro-batch 回退，不要一次性抹掉整条扩展线。

## 8. 变更完成判定

至少满足：

- 目标扩展类型落在正确域文件
- `extensions/index.ts` / `extensions/market/index.ts` 导出链路正确
- `node scripts/validate-types.js` 通过
- `node scripts/check-type-conflicts.js` 通过
- `node scripts/audit-type-extension-quality.js` 中 `naming.ok=true` 且 `jsdoc.ok=true`
- `npm run type-check` 通过
- 若需要留存证据，`node scripts/generate-type-validation-report.js` 可生成时间戳报告与 `latest.json`
- 若需要可读监控面板，`node scripts/generate-type-health-dashboard.js` 可从 `latest.json` 生成静态 HTML dashboard 与 `latest.html`

若只是历史方案、旧报告或计划文档更新，而没有上述脚本或类型检查证据，不能视为本系统已完成收口。
