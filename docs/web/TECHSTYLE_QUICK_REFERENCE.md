# TechStyle v2.0 快速参考指南

**专业金融设计系统** - 10轮迭代优化成果

---

## 🎨 配色速查

### 主色调
```scss
--theme-accent: #0066CC;        // 深海军蓝 - 主色
--theme-accent-secondary: #0088FF;  // 中蓝 - 辅助
--theme-accent-tertiary: #00A3FF;   // 亮蓝 - 高光
```

### 金融市场颜色
```scss
--market-up: #EF4444;      // 红色 - 上涨
--market-down: #22C55E;    // 绿色 - 下跌
--market-flat: #94A3B8;    // 灰色 - 平盘
```

### 语义色
```scss
--theme-success: #22C55E;  // 成功
--theme-warning: #F59E0B;  // 警告
--theme-error: #EF4444;    // 错误
--theme-info: #0066CC;     // 信息
```

---

## 🎭 常用工具类

### 文本样式
```html
<h1 class="ts-gradient-text">渐变标题</h1>
<p class="ts-gradient-text subtle">微妙渐变</p>
```

### 卡片样式
```html
<div class="ts-card">标准卡片</div>
<div class="ts-card elevated">提升卡片</div>
<div class="ts-card floating">浮动卡片</div>
<div class="ts-card inset">内嵌卡片</div>
```

### 按钮样式
```html
<button class="ts-btn primary">主要按钮</button>
<button class="ts-btn secondary">次要按钮</button>
<button class="ts-btn ghost">幽灵按钮</button>
<button class="ts-btn raised">凸起按钮</button>
```

### 市场数据
```html
<span class="ts-market-up">+2.5%</span>
<span class="ts-market-down">-1.2%</span>
<span class="ts-market-flat">0.0%</span>

<span class="ts-market-badge up">买入</span>
<span class="ts-market-badge down">卖出</span>
```

### 标签/徽章
```html
<span class="ts-semantic-badge success">成功</span>
<span class="ts-semantic-badge warning">警告</span>
<span class="ts-semantic-badge error">错误</span>
<span class="ts-semantic-badge info">信息</span>
```

### 动画效果
```html
<div class="ts-hover-lift">悬停提升</div>
<div class="ts-hover-scale">悬停缩放</div>
<div class="ts-hover-glow">悬停发光</div>

<div class="ts-animate-fade-in">淡入</div>
<div class="ts-animate-slide-in">滑入</div>
<div class="ts-animate-bounce-in">弹入</div>
<div class="ts-animate-pulse">脉冲</div>
<div class="ts-animate-float">浮动</div>
```

### 装饰元素
```html
<!-- 状态指示器 -->
<span class="ts-status-indicator online">在线</span>
<span class="ts-status-indicator offline">离线</span>
<span class="ts-status-indicator busy">繁忙</span>
<span class="ts-status-indicator error">错误</span>

<!-- 信息框 -->
<div class="ts-info-box">默认信息框</div>
<div class="ts-info-box success">成功信息框</div>
<div class="ts-info-box warning">警告信息框</div>
<div class="ts-info-box error">错误信息框</div>

<!-- 分割线 -->
<hr class="ts-divider">
<hr class="ts-divider thick">
<hr class="ts-divider dashed">

<!-- 角落装饰 -->
<div class="ts-corner-decoration top-left"></div>
<div class="ts-corner-decoration top-right"></div>
<div class="ts-corner-decoration bottom-left"></div>
<div class="ts-corner-decoration bottom-right"></div>
```

### 渐变背景
```html
<div class="ts-gradient-bg">线性渐变背景</div>
<div class="ts-gradient-bg radial">径向渐变背景</div>
<div class="ts-gradient-overlay">叠加层</div>
```

### 表格样式
```html
<table class="ts-table">标准表格</table>
<table class="ts-table compact">紧凑表格</table>
<table class="ts-table spacious">宽松表格</table>
```

---

## 📐 间距系统

```scss
--spacing-xs:   0.25rem  // 4px
--spacing-sm:   0.5rem   // 8px
--spacing-md:   1rem     // 16px
--spacing-lg:   1.5rem   // 24px
--spacing-xl:   2rem     // 32px
--spacing-2xl:  2.5rem   // 40px
--spacing-3xl:  3rem     // 48px
--spacing-4xl:  4rem     // 64px
--spacing-section:    5rem     // 80px
--spacing-section-large: 7rem    // 112px
```

---

## ✏️ 字体比例

```scss
--text-xs:    0.75rem   // 12px
--text-sm:    0.875rem  // 14px
--text-base:  1rem      // 16px
--text-lg:    1.125rem  // 18px
--text-xl:    1.25rem   // 20px
--text-2xl:   1.5rem    // 24px
--text-3xl:   1.875rem  // 30px
--text-4xl:   2.25rem   // 36px
--text-5xl:   3rem      // 48px
```

---

## 🌗 深色模式

### 使用方法
```html
<!-- 浅色模式 -->
<html>

<!-- 深色模式 -->
<html data-theme="dark">
```

### 动态切换
```javascript
// 切换到深色模式
document.documentElement.setAttribute('data-theme', 'dark');

// 切换到浅色模式
document.documentElement.setAttribute('data-theme', 'light');
```

---

## 🎯 常见场景

### 1. 数据卡片
```html
<div class="ts-card elevated ts-hover-lift">
  <h3 class="ts-gradient-text">总资产</h3>
  <p class="ts-market-up">+12.5%</p>
  <span class="ts-market-badge up">盈利</span>
</div>
```

### 2. 操作按钮组
```html
<div class="flex gap-2">
  <button class="ts-btn primary ts-hover-lift">确认</button>
  <button class="ts-btn secondary ts-hover-scale">取消</button>
  <button class="ts-btn ghost">详情</button>
</div>
```

### 3. 状态面板
```html
<div class="ts-card">
  <div class="flex items-center gap-2 mb-4">
    <span class="ts-status-indicator online"></span>
    <span>系统正常运行</span>
  </div>
  <div class="ts-info-box success">
    所有数据已同步完成
  </div>
</div>
```

### 4. 市场数据表格
```html
<table class="ts-table spacious">
  <thead>
    <tr>
      <th>代码</th>
      <th>名称</th>
      <th>现价</th>
      <th>涨跌幅</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>600519</td>
      <td>贵州茅台</td>
      <td>1680.50</td>
      <td class="ts-market-up">+1.25%</td>
    </tr>
  </tbody>
</table>
```

---

## 🚀 最佳实践

### DO ✅
- 使用 `ts-gradient-text` 强调标题
- 使用 `ts-market-up/down` 显示涨跌
- 使用 `ts-hover-lift` 提升卡片交互
- 使用 `ts-semantic-badge` 标记状态
- 使用 `ts-table` 展示数据表格

### DON'T ❌
- 不要混用Web3和TechStyle类
- 不要硬编码颜色值
- 不要过度使用动画
- 不要忽略深色模式适配
- 不要破坏现有样式

---

## 📦 相关文件

- **主文件**: `/web/frontend/src/styles/techstyle-tokens.scss` (1,191行)
- **文档**: `/docs/web/TECHSTYLE_THEME_IMPROVEMENT_REPORT.md`
- **快速参考**: 本文件

---

## 🔗 快速链接

- [完整改进报告](./TECHSTYLE_THEME_IMPROVEMENT_REPORT.md)
- [主样式文件](../../web/frontend/src/styles/techstyle-tokens.scss)
- [Web3主题文档](../../web/frontend/src/styles/web3-tokens.scss)

---

**版本**: TechStyle v2.0
**更新**: 2025-12-31
**作者**: MyStocks Frontend Team
