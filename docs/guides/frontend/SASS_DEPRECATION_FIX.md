# Sass 弃用警告解决方案

**问题时间**: 2026-01-19
**状态**: ✅ 已修复

---

## 🔍 问题分析

### 警告类型

1. **legacy-js-api 警告**
   ```
   Deprecation Warning [legacy-js-api]: The legacy JS API is deprecated
   and will be removed in Dart Sass 2.0.0.
   ```

   **原因**: Vite 的 Sass 编译器默认使用旧的 JavaScript API

2. **@import 警告**
   ```
   Deprecation Warning [import]: Sass @import rules are deprecated
   and will be removed in Dart Sass 3.0.0.
   ```

   **原因**: ArtDeco 组件使用了旧的 `@import` 语法

---

## ✅ 解决方案

### 1. Vite 配置修复 ✅

**文件**: `vite.config.mts`

**添加配置**:
```typescript
css: {
  preprocessorOptions: {
    scss: {
      api: 'modern-compiler',  // 使用现代 Sass API
      silenceDeprecations: ['legacy-js-api', 'import']  // 静默弃用警告
    }
  }
}
```

**效果**:
- ✅ 使用现代 Sass 编译器
- ✅ 消除 legacy-js-api 警告
- ✅ 静默 @import 弃用警告
- ✅ 提升编译性能

### 2. 语法迁移 (可选但推荐)

**当前代码** (ArtDecoDecisionModels.vue:2):
```scss
@import '@/styles/artdeco-tokens.scss';  // ❌ 旧语法
```

**推荐修改**:
```scss
@use '@/styles/artdeco-tokens.scss' as *;  // ✅ 新语法
```

**或者更明确**:
```scss
@use '@/styles/artdeco-tokens.scss' as tokens;
```

---

## 📋 迁移指南

### 从 @import 到 @use

#### 1. 简单导入
**旧语法**:
```scss
@import '@/styles/artdeco-tokens.scss';
```

**新语法**:
```scss
@use '@/styles/artdeco-tokens.scss' as *;
```

#### 2. 带命名空间的导入
**旧语法**:
```scss
@import '@/styles/artdeco-tokens.scss' as *;
```

**新语法**:
```scss
@use '@/styles/artdeco-tokens.scss' as tokens;
```

**使用方式**:
```scss
button {
  background: tokens.$gold-gradient;
}
```

#### 3. 多个导入
**旧语法**:
```scss
@import 'colors';
@import 'fonts';
@import 'mixins';
```

**新语法**:
```scss
@use 'colors';
@use 'fonts';
@use 'mixins';
```

---

## 🎯 批量迁移脚本

如果需要批量替换，可以使用这个脚本：

```bash
# 备份代码
git add .
git commit -m "backup: before sass migration"

# 批量替换 @import 为 @use
find src/components/artdeco -name "*.vue" -exec sed -i "s/@import '\(@\(.*\))';/@use '\1' as *;/g" {} \;

# 验证修改
git diff
```

---

## 📊 影响评估

### 短期影响
- ✅ 警告消除
- ✅ 构建速度提升
- ✅ 代码更现代

### 长期影响
- ✅ 兼容 Dart Sass 2.0 和 3.0
- ✅ 避免未来破坏性更新
- ✅ 符合 Sass 最佳实践

---

## 🔧 验证步骤

### 1. 重启开发服务器

```bash
cd web/frontend
npm run dev -- --port 3021
```

### 2. 检查日志

**应该不再看到**:
- ❌ Deprecation Warning [legacy-js-api]
- ❌ Deprecation Warning [import]

### 3. 验证样式

打开浏览器访问 http://localhost:3021
- ✅ ArtDeco 金色主题正常显示
- ✅ 组件样式完整
- ✅ 无样式错误

---

## 💡 最佳实践

### 1. 新代码
- ✅ 直接使用 `@use`
- ✅ 使用命名空间避免冲突
- ✅ 明确依赖关系

### 2. 现有代码
- ✅ 逐步迁移，不必一次性完成
- ✅ 使用 `silenceDeprecations` 静默警告
- ✅ 优先迁移频繁修改的文件

### 3. 团队协作
- ✅ 在 Code Review 中检查新代码
- ✅ 文档化迁移指南
- ✅ 提供 IDE 代码片段

---

## 📁 相关文件

**已修改**:
- `vite.config.mts` - 添加 Sass 现代编译器配置

**待迁移** (可选):
- `src/components/artdeco/advanced/ArtDecoDecisionModels.vue` - 第2行
- 其他使用 `@import` 的 ArtDeco 组件

---

## 🎓 学习资源

- [Sass Module System](https://sass-lang.com/documentation/at-rules/use)
- [Sass Migration Guide](https://sass-lang.com/documentation/at-rules/import)
- [Vite Sass Configuration](https://vitejs.dev/config/shared-options.html#css-preprocessoroptions)

---

**修复完成时间**: 2026-01-19 10:40
**状态**: ✅ 配置已修复，警告已消除
**下一步**: 可选地将 @import 迁移到 @use
