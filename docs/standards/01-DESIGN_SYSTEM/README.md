# 设计系统

> **补充规范说明**:
> 本文件是项目补充标准、执行细则或专题规范，不是仓库共享规则的唯一事实来源。
> 仓库级共享规则总入口仍以 `architecture/STANDARDS.md` 为准；执行流程、命令与协作约束再参考根目录 `AGENTS.md`。本文件用于补充某一专题的执行细则、约束或参考模板。
>
> 若本文件与 `architecture/STANDARDS.md`、根目录 `AGENTS.md` 或当前已批准执行口径不一致，应优先遵循 `architecture/STANDARDS.md`、根目录 `AGENTS.md` 与当前实现；若无冲突，则按本文件的专题范围执行。


**版本**: v1.0.0
**最后更新**: 2025-12-25
**上级文档**: [UI_DESIGN_SYSTEM.md](../UI_DESIGN_SYSTEM.md)

---

## 📋 目录

本目录包含 MyStocks 的核心设计系统规范。

### 📄 文档列表

1. **[颜色系统](./color-system.md)** - Color System
   - 主题色
   - 功能色
   - 中性色
   - 涨跌色
   - 色彩无障碍

2. **[字体系统](./typography.md)** - Typography
   - 字体族
   - 字号系统
   - 行高与字间距
   - 字重
   - 文本样式

3. **[布局系统](./layout-system.md)** - Layout System
   - 网格系统
   - 间距系统
   - 响应式断点
   - 布局组件

4. **[设计 Tokens](./design-tokens.md)** - Design Tokens
   - 间距 Tokens
   - 圆角 Tokens
   - 阴影 Tokens
   - 动画 Tokens
   - Z-index 层级

---

## 🎨 设计系统概述

MyStocks 设计系统基于 **Element Plus 设计语言**，结合金融数据可视化的特殊需求，提供一致、专业、高效的设计规范。

### 核心原则

1. **一致性** - 统一的视觉语言和交互模式
2. **可扩展** - 模块化设计，易于扩展和定制
3. **可维护** - 设计驱动开发，Design Tokens 管理
4. **可访问** - 符合 WCAG 2.1 AA 标准

### 技术实现

```scss
// Design Tokens (SCSS 变量)
@import './tokens/colors';
@import './tokens/typography';
@import './tokens/spacing';
@import './tokens/borders';
@import './tokens/shadows';

// 组件样式
@import './components/buttons';
@import './components/forms';
@import './components/tables';
```

---

## 🌈 快速参考

### 颜色速查

| 用途 | 颜色值 | HEX | 使用场景 |
|-----|-------|-----|---------|
| **主色** | Primary | `#409EFF` | 按钮、链接、激活状态 |
| **成功** | Success | `#67C23A` | 成功提示、确认操作 |
| **警告** | Warning | `#E6A23C` | 警告提示、注意事项 |
| **危险** | Danger | `#F56C6C` | 错误提示、删除操作 |
| **信息** | Info | `#909399` | 信息提示、辅助文本 |
| **涨 (红)** | Rise | `#F56C6C` | 股价上涨、买入信号 |
| **跌 (绿)** | Fall | `#67C23A` | 股价下跌、卖出信号 |

### 字号速查

| 级别 | 字号 | 行高 | 用途 |
|-----|-----|------|------|
| **H1** | 24px | 1.5 | 页面标题 |
| **H2** | 20px | 1.5 | 区块标题 |
| **H3** | 18px | 1.5 | 卡片标题 |
| **Body** | 14px | 1.5 | 正文内容 |
| **Small** | 12px | 1.5 | 辅助文本 |
| **Tiny** | 10px | 1.5 | 标签、徽章 |

### 间距速查

| Token | 值 | 用途 |
|-------|---|------|
| `$spacing-xs` | 4px | 紧密间距 |
| `$spacing-sm` | 8px | 小间距 |
| `$spacing-md` | 16px | 默认间距 |
| `$spacing-lg` | 24px | 区块间距 |
| `$spacing-xl` | 32px | 大间距 |
| `$spacing-xxl` | 48px | 页面级间距 |

### 断点速查

| 断点 | 宽度 | 设备 |
|-----|------|------|
| **xs** | < 480px | 手机竖屏 |
| **sm** | ≥ 480px | 手机横屏 |
| **md** | ≥ 768px | 平板 |
| **lg** | ≥ 992px | 小桌面 |
| **xl** | ≥ 1200px | 桌面 |
| **xxl** | ≥ 1920px | 大桌面 |

---

## 🎯 使用指南

### 设计师

1. **Figma 设计稿**
   - 使用 Design Tokens 作为样式基础
   - 遵循颜色和字体规范
   - 使用 8px 网格系统

2. **设计交付**
   - 导出图标资源 (SVG/PNG)
   - 标注关键尺寸和间距
   - 说明交互状态和动画

### 前端开发者

1. **安装 Design Tokens**
   ```bash
   # 项目已包含，无需额外安装
   # 位置: web/frontend/src/styles/tokens/
   ```

2. **使用 SCSS 变量**
   ```scss
   .my-component {
     color: $text-primary;
     padding: $spacing-md;
     border-radius: $radius-md;
     box-shadow: $shadow-sm;
   }
   ```

3. **使用 Tailwind CSS (可选)**
   ```vue
   <template>
     <div class="p-4 rounded-lg shadow-sm text-primary">
       内容
     </div>
   </template>
   ```

---

## 📊 设计系统架构

```
设计系统
├── Design Tokens (设计变量)
│   ├── 颜色 Tokens
│   ├── 字体 Tokens
│   ├── 间距 Tokens
│   ├── 圆角 Tokens
│   └── 阴影 Tokens
│
├── Base Styles (基础样式)
│   ├── Reset (样式重置)
│   ├── Typography (排版)
│   └── Utilities (工具类)
│
├── Component Patterns (组件模式)
│   ├── Buttons (按钮)
│   ├── Forms (表单)
│   ├── Tables (表格)
│   ├── Cards (卡片)
│   └── Modals (弹窗)
│
└── Layout Patterns (布局模式)
    ├── Grid (网格)
    ├── Container (容器)
    └── Responsive (响应式)
```

---

## 🔧 自定义主题

### 覆盖 Element Plus 变量

```scss
// web/frontend/src/styles/element-variables.scss

@forward 'element-plus/theme-chalk/src/common/var.scss' with (
  // 主色
  $colors: (
    'primary': (
      'base': #409EFF,
    ),
  ),

  // 字体
  $font-family: (
    '': "'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif",
  ),

  // 圆角
  $border-radius: (
    'base': 4px,
  ),

  // 间距
  $spacing: (
    'base': 8px,
  ),
);
```

### 自定义 Design Tokens

```scss
// web/frontend/src/styles/tokens/custom.scss

// 自定义颜色
$custom-blue: #1890FF;
$custom-purple: #722ED1;

// 自定义间距
$custom-spacing: (
  'nano': 2px,
  'mega': 64px,
);

// 自定义阴影
$custom-shadow: (
  'inner': inset 0 2px 4px rgba(0, 0, 0, 0.1),
);
```

---

## ✅ 设计检查清单

在使用设计系统时，请确保：

- [ ] 使用 Design Tokens，避免硬编码值
- [ ] 遵循颜色规范，保持色彩一致性
- [ ] 使用正确的字号和行高
- [ ] 遵循 8px 网格系统
- [ ] 确保响应式布局在所有断点正常
- [ ] 测试深色主题（如果支持）
- [ ] 验证色彩对比度（WCAG AA）
- [ ] 测试键盘导航和屏幕阅读器

---

## 📚 相关资源

### Element Plus
- [Element Plus 官方文档](https://element-plus.org/)
- [Element Plus 设计指南](https://element-plus.org/en-US/guide/design.html)
- [Element Plus 主题定制](https://element-plus.org/en-US/guide/theming.html)

### 设计工具
- [Figma](https://www.figma.com/)
- [Adobe XD](https://www.adobe.com/products/xd.html)
- [Sketch](https://www.sketch.com/)

### 开发工具
- [Chrome DevTools](https://developers.google.com/web/tools/chrome-devtools)
- [Vue DevTools](https://devtools.vuejs.org/)
- [Sass Documentation](https://sass-lang.com/documentation)

---

## 🔄 更新日志

### v1.0.0 (2025-12-25)
- ✅ 初始版本
- ✅ 定义颜色系统
- ✅ 定义字体系统
- ✅ 定义布局系统
- ✅ 定义 Design Tokens

---

## 📞 联系方式

- **设计团队**: design@mystocks.com
- **前端团队**: frontend@mystocks.com
- **问题反馈**: [GitHub Issues](https://github.com/chengjon/mystocks/issues)

---

**文档版本**: v1.0.0
**最后更新**: 2025-12-25
**维护者**: UI Design Team
**位置**: `docs/standards/01-DESIGN_SYSTEM/README.md`
