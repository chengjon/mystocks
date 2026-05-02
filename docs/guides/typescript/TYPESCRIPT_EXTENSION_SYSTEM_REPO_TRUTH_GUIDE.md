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

推荐示例：

```ts
import type { StrategyVM, BacktestResultVM } from "@/api/types/extensions/strategy";
import type { MarketOverviewVM, KLineChartData } from "@/api/types/extensions/market";
import type { PositionVM, APIResponseVM } from "@/api/types/extensions/common";
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

当前这套系统依赖 3 个本地脚本：

- `node scripts/validate-types.js`
  - 校验扩展目录、关键入口文件和主索引扩展导出是否存在
- `node scripts/check-type-conflicts.js`
  - 检查当前公开 surface 是否存在冲突
- `node scripts/generate-type-usage.js`
  - 输出扩展文件数、导出类型数、主索引扩展导出模式等 JSON summary

常用验证命令：

```bash
cd web/frontend
node scripts/validate-types.js
node scripts/check-type-conflicts.js
node scripts/generate-type-usage.js
npm run type-check
```

当前 `tsconfig.json` 已不再排除 `src/api/types/extensions/**/*`，因此 `npm run type-check` 会真实覆盖扩展类型，而不是绕过它们。

## 5. 新增类型时的最小流程

推荐按这个顺序做：

1. 选对域文件
   - strategy -> `extensions/strategy.ts`
   - market -> `extensions/market/*`
   - common utility / ViewModel helper -> `extensions/common.ts`
2. 先确认名字不会和现有顶层公开 surface 冲突
3. 如有新的 market 子模块导出，先更新 `extensions/market/index.ts`
4. 跑脚本：
   - `node scripts/validate-types.js`
   - `node scripts/check-type-conflicts.js`
   - `npm run type-check`
5. 若需要统计或审计，再跑 `node scripts/generate-type-usage.js`

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

## 7. 变更完成判定

至少满足：

- 目标扩展类型落在正确域文件
- `extensions/index.ts` / `extensions/market/index.ts` 导出链路正确
- `node scripts/validate-types.js` 通过
- `node scripts/check-type-conflicts.js` 通过
- `npm run type-check` 通过

若只是历史方案、旧报告或计划文档更新，而没有上述脚本或类型检查证据，不能视为本系统已完成收口。
