# 前端代码质量修复与重构执行方案 (优化版)

## 背景
本项目代码中存在大量 TypeScript 错误及缩进不统一（2空格 vs 4空格）的问题。本方案基于现有项目配置（Vue 3 + TypeScript + Vite），旨在快速、批量、安全地修复格式问题，并为后续逻辑修复打好基础。

## 核心原则
1.  **工具优先**：利用 Prettier 和 ESLint 自动解决 90% 的格式与缩进问题。
2.  **统一标准**：前端统一采用 **4空格** 缩进，与后端（Python）保持一致，提升全栈开发体验。
3.  **兼容现有**：修改现有配置文件（`.prettierrc`, `.eslintrc.cjs`），避免新建配置文件导致冲突。

---

## 执行步骤

### 步骤 1：标准化配置文件 (Standardize Configs)

目标：将缩进统一为 4 空格，并启用 Vue 组件内的 Script/Style 缩进。

**操作对象**：`web/frontend/.prettierrc`

**配置变更**：
```json
{
  "semi": false,
  "singleQuote": true,
  "printWidth": 120,
  "tabWidth": 4,              // 核心变更：2 -> 4
  "useTabs": false,
  "trailingComma": "none",
  "bracketSpacing": true,
  "arrowParens": "avoid",
  "endOfLine": "lf",
  "vueIndentScriptAndStyle": true, // 核心变更：false -> true (使Vue文件内部层级更清晰)
  "htmlWhitespaceSensitivity": "ignore",
  "overrides": [
    {
      "files": "*.vue",
      "options": { "parser": "vue" }
    },
    {
      "files": ["*.ts", "*.tsx"],
      "options": { "parser": "typescript" }
    }
  ]
}
```

### 步骤 2：一键批量修复 (Batch Fix)

目标：利用工具自动重写文件，物理修复所有格式和缩进错误。

**执行命令**（在 `web/frontend` 目录下）：

```bash
# 1. Prettier 暴力格式化
# 作用：按照新配置重写所有文件，统一缩进和风格
npx prettier --write "src/**/*.{vue,ts,js,json}"

# 2. ESLint 智能修复
# 作用：修复基于 AST 语法的格式问题（如 Import 排序、未使用的变量清理等）
npm run lint
```

### 步骤 3：类型检查与兜底 (Type Check & Verification)

目标：格式问题解决后，聚焦真正的逻辑和类型错误。

**执行命令**：
```bash
# 使用 vue-tsc 进行准确的类型检查
npm run type-check
```

**后续处理**：
对于 `type-check` 扫描出的逻辑错误（如模块丢失、类型不匹配），需要开发人员根据报错信息逐个手动修复。

---

## 长效维护 (Prevention)

1.  **IDE 配置**：确保 VS Code 安装 Prettier 插件，并勾选 "Format On Save"。
2.  **Git Hooks**：项目已配置 `lint-staged`，后续提交代码时会自动触发格式化，无需手动运行。
