# MyStocks 深色主题快速验证指南
# Quick Theme Verification Guide

## 验证步骤

### 1. 启动开发服务器

```bash
cd /opt/claude/mystocks_spec/web/frontend
npm run dev
```

服务器将运行在 `http://localhost:3020` (或 3003)

### 2. 验证清单

#### 全局主题
- [ ] 页面背景是深蓝色 (`#0B0F19`)
- [ ] 卡片背景是中蓝色 (`#232936`)
- [ ] 主文本是白色
- [ ] 次要文本是浅灰色

#### A股市场颜色
- [ ] 上涨数字是红色 (`#FF5252`)
- [ ] 下跌数字是绿色 (`#00E676`)
- [ ] 平盘数字是灰色 (`#B0B3B8`)

#### Element Plus 组件
- [ ] Card 组件有深色背景
- [ ] Table 继行悬停效果正常
- [ ] Button 组件颜色正确
- [ ] Input 输入框背景正确
- [ ] Select 下拉菜单深色主题
- [ ] Tag 标签颜色正确

#### 页面验证
- [ ] Dashboard 页面显示正常
- [ ] Stocks 页面价格涨跌颜色正确
- [ ] StrategyManagement 页面深色主题
- [ ] BacktestAnalysis 页面收益率颜色
- [ ] TechnicalAnalysis 页面指标颜色

### 3. 常见问题

**Q: 页面显示白色背景？**
A: 清除浏览器缓存并硬刷新 (Ctrl+Shift+R)

**Q: Element Plus 组件颜色不对？**
A: 检查 `main.js` 中导入顺序：
```javascript
// 正确的导入顺序
import 'element-plus/theme-chalk/dark/css-vars.css'
import './styles/theme-dark.scss'
import './styles/theme-apply.scss'
import './styles/index.scss'
```

**Q: A股颜色（红涨绿跌）显示反了？**
A: 确保使用正确的类名：
- 涨: `text-up` (红色)
- 跌: `text-down` (绿色)

### 4. 调试工具

#### 检查 CSS 变量

在浏览器控制台运行：
```javascript
// 检查主背景色
getComputedStyle(document.body).getPropertyValue('--bg-primary')

// 检查上涨颜色
getComputedStyle(document.body).getPropertyValue('--color-up')

// 检查下跌颜色
getComputedStyle(document.body).getPropertyValue('--color-down')
```

#### 验证主题加载

```javascript
// 应该看到这些变量
console.log(getComputedStyle(document.documentElement))
```

### 5. 性能检查

打开 Chrome DevTools → Performance，录制页面加载：
- CSS 解析时间应该 < 100ms
- 首次内容绘制 (FCP) < 1.8s
- 页面可交互时间 (TTI) < 3.9s

---

## 验证报告模板

### 日期：__________

### 浏览器：Chrome _______ Firefox _______ Safari _______

### 验证结果：

| 项目 | 通过 | 备注 |
|------|------|------|
| 全局主题 | [ ] | |
| A股颜色 | [ ] | |
| Element Plus | [ ] | |
| Dashboard | [ ] | |
| Stocks | [ ] | |
| StrategyManagement | [ ] | |
| BacktestAnalysis | [ ] | |
| TechnicalAnalysis | [ ] | |
| 响应式 (移动端) | [ ] | |
| 性能 | [ ] | |

### 问题描述：

_______________________________________________________________
_______________________________________________________________

### 建议改进：

_______________________________________________________________
_______________________________________________________________

---

## 快速修复

### 颜色不对

在组件 `<style>` 中添加：
```scss
.my-component {
  background-color: var(--bg-card) !important;
  color: var(--text-primary) !important;
}
```

### 类名不生效

确保在 `theme-apply.scss` 中定义：
```scss
.my-custom-class {
  color: var(--text-primary) !important;
}
```

### 优先级问题

使用 `!important` 或更具体的选择器：
```scss
// 方法 1: 使用 !important
.my-class {
  color: var(--color-up) !important;
}

// 方法 2: 使用更具体的选择器
.parent .child .my-class {
  color: var(--color-up);
}
```

---

**文档版本**: 1.0
**更新时间**: 2025-12-26
