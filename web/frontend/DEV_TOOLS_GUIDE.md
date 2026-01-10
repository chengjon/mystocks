# 开发工具使用指南

本指南说明如何使用配置的开发工具（ESLint、Prettier、Stylelint、Git Hooks）。

---

## 📦 已配置的工具

### 1. ESLint
**配置文件**: `.eslintrc.cjs`

**功能**:
- TypeScript类型检查
- Vue 3最佳实践
- Import排序和分组
- 代码质量规则

**命令**:
```bash
# 检查代码
npm run lint

# 自动修复
npm run lint:fix
```

### 2. Prettier
**配置文件**: `.prettierrc`, `.prettierignore`

**功能**:
- 统一代码格式
- 120字符行宽
- 单引号、无分号
- Vue/SCSS/TypeScript支持

**命令**:
```bash
# 格式化代码
npm run format

# 检查格式
npm run format:check
```

### 3. Stylelint
**配置文件**: `.stylelintrc.json`, `.stylelintignore`

**功能**:
- SCSS/CSS语法检查
- Vue scoped样式支持
- 自动修复样式问题

**命令**:
```bash
# 检查样式
npm run stylelint

# 自动修复
npm run stylelint:fix
```

### 4. Git Hooks (Husky + lint-staged)
**配置目录**: `.husky/`

**功能**:
- Pre-commit自动检查
- 只检查staged文件
- 自动修复可修复的问题
- TypeScript类型检查（可跳过）

**使用**:
```bash
# 正常提交（运行所有检查）
git commit -m "feat: add new feature"

# 跳过TypeScript类型检查
SKIP_TYPE_CHECK=true git commit -m "feat: add feature (skip type check)"

# 跳过所有hooks（不推荐）
git commit --no-verify -m "feat: add feature"
```

---

## 🚀 快速开始

### 安装依赖

```bash
# 运行自动安装脚本
bash scripts/setup-dev-tools.sh

# 或手动安装
npm install --save-dev \
  eslint \
  eslint-plugin-vue \
  @typescript-eslint/parser \
  @typescript-eslint/eslint-plugin \
  @vue/eslint-config-typescript \
  @vue/eslint-config-prettier \
  prettier \
  stylelint \
  stylelint-config-standard-scss \
  stylelint-config-recommended-vue \
  stylelint-scss \
  husky \
  lint-staged
```

### VS Code集成

安装推荐扩展：
- ESLint
- Prettier - Code formatter
- Stylelint
- Volar (Vue 3)

VS Code设置 (`.vscode/settings.json`):
```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true,
    "source.fixAll.stylelint": true
  },
  "eslint.validate": [
    "javascript",
    "javascriptreact",
    "typescript",
    "typescriptreact",
    "vue"
  ],
  "stylelint.validate": ["css", "scss"]
}
```

---

## 📋 规则配置说明

### ESLint规则

**TypeScript规则**:
- `@typescript-eslint/no-explicit-any: warn` - 警告使用any类型
- `@typescript-eslint/no-unused-vars: warn` - 警告未使用变量
- `@typescript-eslint/no-non-null-assertion: warn` - 警告非空断言

**Vue规则**:
- `vue/multi-word-component-names: off` - 允许单词组件名
- `vue/no-v-html: warn` - 警告使用v-html
- `vue/require-default-prop: off` - 不强制默认props

**通用规则**:
- `prefer-const: warn` - 建议使用const
- `no-var: error` - 禁止使用var
- `import/order: warn` - Import分组和排序

### Prettier规则

- 120字符行宽
- 单引号
- 无分号
- 2空格缩进
- 尾随逗号：省略

### Stylelint规则

- 支持SCSS语法
- Vue scoped样式支持
- Tailwind CSS at-rules支持
- CSS颜色函数传统语法

---

## 🔧 常见问题

### Q1: Pre-commit hook失败怎么办？

**A**: 查看错误信息：
- 如果是格式问题：运行 `npm run format:fix`
- 如果是类型错误：修复TypeScript错误或使用 `SKIP_TYPE_CHECK=true`
- 如果是lint错误：运行 `npm run lint:fix`

### Q2: 如何临时禁用某条规则？

**A**: 使用注释禁用：
```typescript
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const data: any = getData()
```

### Q3: 格式化冲突？

**A**: ESLint和Prettier已配置为兼容，如有问题：
1. 优先使用Prettier格式化
2. ESLint只检查代码质量，不负责格式
3. 运行 `npm run format:fix` 然后 `npm run lint:fix`

### Q4: Git hook太慢？

**A**: 优化建议：
1. 只检查staged文件（已配置）
2. 跳过类型检查：`SKIP_TYPE_CHECK=true git commit`
3. 禁用hook（不推荐）：`git commit --no-verify`

---

## 📚 参考资料

- [ESLint文档](https://eslint.org/)
- [Prettier文档](https://prettier.io/)
- [Stylelint文档](https://stylelint.io/)
- [Husky文档](https://typicode.github.io/husky/)
- [lint-staged文档](https://github.com/okonet/lint-staged)

---

**最后更新**: 2026-01-10  
**维护者**: MyStocks Frontend Team
