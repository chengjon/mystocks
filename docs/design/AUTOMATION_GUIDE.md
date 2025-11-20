# Figma 自动化脚本使用指南

> **脚本功能**: 一键批量创建 MyStocks 设计系统的所有颜色样式、文本样式和基础组件
> **预计执行时间**: 30 秒
> **难度**: ⭐☆☆☆☆ (非常简单)

---

## 📋 脚本将创建的内容

### ✅ 颜色样式（25 个）

| 类别 | 数量 | 样式名称示例 |
|------|------|-------------|
| **主色调** | 5 | Primary/Blue, Success/Green, Danger/Red, Warning/Orange, Info/Gray |
| **金融专用色** | 5 | Financial/Up, Financial/Down, Financial/Flat, Financial/Up Limit, Financial/Down Limit |
| **背景色** | 5 | Background/Page, Background/Card, Background/Hover, Background/Selected |
| **边框色** | 3 | Border/Default, Border/Light, Border/Focus |
| **文本色** | 4 | Text/Primary, Text/Regular, Text/Secondary, Text/Placeholder |

### ✅ 文本样式（11 个）

| 类别 | 数量 | 样式名称示例 |
|------|------|-------------|
| **标题** | 4 | Heading/XL (28px), Heading/L (24px), Heading/M (20px), Heading/S (18px) |
| **正文** | 4 | Body/Regular (14px), Body/Secondary, Caption (13px), Small (12px) |
| **数字** | 3 | Number/Large (32px), Number/Medium (20px), Number/Small (14px) |

### ✅ 基础组件（8 个）

| 组件名称 | 变体数量 | 说明 |
|---------|---------|------|
| **Button** | 5 | Primary, Success, Warning, Danger, Info |
| **** | 3 | Up (涨), Down (跌), Flat (平) |

---

## 🚀 使用步骤（5 分钟）

### 步骤 1: 登录 Figma（1 分钟）

```
1. 访问: https://www.figma.com
2. 登录您的账号（如果还没注册，使用 Google 账号快速注册）
3. 创建新文件: 点击 "New design file"
4. 命名: "MyStocks Design System"
```

---

### 步骤 2: 打开插件开发模式（1 分钟）

```
方法 1: 通过菜单
1. 菜单栏 → Plugins → Development → New Plugin...
2. 在弹出窗口中选择: "Run once"
3. 插件名称输入: "MyStocks Automation"
4. 点击 "Save" 或 "Next"

方法 2: 快捷键（推荐）
1. Windows: Ctrl + Alt + P
   macOS: Cmd + Option + P
2. 输入: "development"
3. 选择 "Development → New Plugin"
```

**您会看到代码编辑器窗口**:
```
┌─────────────────────────────────────────┐
│ Plugin: MyStocks Automation             │
├─────────────────────────────────────────┤
│ // This plugin will run as a one-off... │
│                                         │
│ figma.closePlugin();                    │
│                                         │
│                                         │
└─────────────────────────────────────────┘
```

---

### 步骤 3: 复制粘贴脚本（1 分钟）

#### 3.1 获取脚本内容

**方法 A: 从本地文件复制**
```bash
# 文件路径
/opt/claude/mystocks_spec/docs/design/figma-automation-script.js

# 打开文件并全选复制 (Ctrl+A / Cmd+A)
```

**方法 B: 直接复制（如果看到下面的脚本）**
```
见下方完整脚本代码
```

#### 3.2 粘贴到编辑器

```
1. 在 Figma 插件编辑器中全选现有代码 (Ctrl+A / Cmd+A)
2. 删除 (Delete / Backspace)
3. 粘贴复制的脚本内容 (Ctrl+V / Cmd+V)
4. 确认脚本完整粘贴（应该有 400+ 行代码）
```

---

### 步骤 4: 运行脚本（1 分钟）

```
1. 点击编辑器右下角的 "Run" 按钮
   或按快捷键: Ctrl+Enter (Win) / Cmd+Enter (Mac)

2. 等待执行完成（约 30 秒）

3. 查看控制台输出:
   - 应该看到进度信息
   - 每个样式创建都有 ✓ 标记
   - 最后显示 "✅ 自动化脚本执行完成!"

4. Figma 右下角会显示通知:
   "✅ MyStocks 组件创建完成! 请查看左侧面板。"
```

**控制台输出示例**:
```
========================================
MyStocks Figma 自动化脚本
========================================

【步骤 1/4】创建颜色样式
----------------------------------------
✓ 创建颜色样式: Primary/Blue (#409EFF)
✓ 创建颜色样式: Success/Green (#67C23A)
✓ 创建颜色样式: Danger/Red (#F56C6C)
...
颜色样式创建完成: 成功 25 个, 失败 0 个

【步骤 2/4】创建文本样式
----------------------------------------
加载字体...
✓ 加载字体: Inter Regular
✓ 创建文本样式: Heading/XL (28px)
✓ 创建文本样式: Body/Regular (14px)
...
文本样式创建完成: 成功 11 个, 失败 0 个

【步骤 3/4】创建按钮组件
----------------------------------------
✓ 创建按钮组件: Primary
✓ 创建按钮组件: Success
...
按钮组件创建完成

【步骤 4/4】创建  组件
----------------------------------------
✓ 创建  组件: Up
✓ 创建  组件: Down
✓ 创建  组件: Flat
 组件创建完成

========================================
✅ 自动化脚本执行完成!
========================================
颜色样式: 25 个
文本样式: 11 个
按钮组件: 5 种类型
 组件: 3 种变体
```

---

### 步骤 5: 验证结果（1 分钟）

#### 5.1 检查颜色样式

```
1. 左侧面板 → Assets (图标像 4 个方块)
2. 点击 "Local styles"
3. 展开 "Fill" (填充样式)
4. 应该看到:
   ├─ Primary/
   │  └─ Blue
   ├─ Success/
   │  └─ Green
   ├─ Financial/
   │  ├─ Up
   │  ├─ Down
   │  └─ Flat
   ...（共 25 个颜色样式）
```

#### 5.2 检查文本样式

```
1. 在 Assets 面板中
2. 展开 "Text" (文本样式)
3. 应该看到:
   ├─ Heading/
   │  ├─ XL (28px)
   │  ├─ L (24px)
   │  ├─ M (20px)
   │  └─ S (18px)
   ├─ Body/
   │  ├─ Regular (14px)
   │  └─ Secondary (14px)
   ├─ Number/
   │  ├─ Large (32px)
   │  ├─ Medium (20px)
   │  └─ Small (14px)
   ...（共 11 个文本样式）
```

#### 5.3 检查组件

```
1. 在画布上应该看到:
   - "Button Components" 框架（包含 5 个按钮）
   - " Components" 框架（包含 3 个 ）

2. 在 Assets 面板中
3. 点击 "Components"
4. 应该看到:
   ├─ Button/
   │  ├─ Primary
   │  ├─ Success
   │  ├─ Warning
   │  ├─ Danger
   │  └─ Info
   └─ /
      ├─ Up
      ├─ Down
      └─ Flat
```

---

## ✅ 完成后的下一步

### 选项 1: 继续在 Figma 中完善设计

```
1. 基于创建的组件设计页面
2. 参考文档:
   - MYSTOCKS_DESIGN_SPECIFICATION.md (页面模板)
   - COMPONENT_LIBRARY_SPECIFICATION.md (更多组件)
3. 使用已创建的颜色和文本样式保持一致性
```

### 选项 2: 立即导入 Pixso

```
1. Figma 右上角 → Share → Copy link
2. 设置: "Anyone with the link can view"
3. 访问 Pixso: https://pixso.cn
4. 导入 → 导入 Figma 文件 → 粘贴链接
5. 等待导入完成
```

---

## ❓ 常见问题

### Q1: 脚本运行时报错 "Cannot find font"

**原因**: 系统缺少所需字体

**解决方案**:
```
脚本会自动回退到默认字体 (Inter)
不影响样式创建，只是字体名称不同
您可以在 Figma 中手动更改字体
```

### Q2: 颜色样式创建成功，但文本样式失败

**原因**: 字体加载问题

**解决方案**:
```
1. 手动创建缺失的文本样式
2. 参考 TEXT_STYLES 对象中的定义
3. 或使用 Figma 默认字体 (Inter)
```

### Q3: 组件位置不对，或看不到组件

**原因**: 画布缩放问题

**解决方案**:
```
1. 按 Shift + 1 (缩放至适应全部内容)
2. 或手动滚动画布查找
3. 组件位置:
   - Button Components: (0, 0)
   -  Components: (0, 450)
```

### Q4: 运行后没有任何反应

**原因**: 脚本未正确粘贴或执行

**解决方案**:
```
1. 确认完整粘贴了所有代码（约 400+ 行）
2. 检查控制台是否有错误信息
3. 重新粘贴脚本并再次运行
4. 确保 Figma 文件处于编辑模式（不是查看模式）
```

### Q5: 我想修改颜色值怎么办？

**解决方案**:
```
方法 1: 修改脚本中的 COLORS 对象
- 找到对应的颜色定义
- 修改 value 值（Hex 格式）
- 重新运行脚本

方法 2: 在 Figma 中手动修改
- Assets → Local styles → 找到颜色样式
- 右键 → Edit style
- 修改颜色值
```

---

## 🔧 脚本自定义

### 修改颜色

在脚本中找到 `COLORS` 对象，修改颜色值:

```javascript
const COLORS = {
  primary: {
    name: "Primary/Blue",
    value: "#409EFF",  // ← 修改这里
    description: "主品牌色"
  },
  // ...
};
```

### 修改文本样式

在脚本中找到 `TEXT_STYLES` 对象，修改字体属性:

```javascript
const TEXT_STYLES = {
  "heading-xl": {
    name: "Heading/XL",
    fontSize: 28,      // ← 字号
    lineHeight: 36,    // ← 行高
    fontWeight: 600,   // ← 字重
    color: "#303133",  // ← 颜色
  },
  // ...
};
```

### 添加新的颜色或文本样式

```javascript
// 在 COLORS 对象中添加新颜色
const COLORS = {
  // ... 现有颜色
  "custom-color": {
    name: "Custom/MyColor",
    value: "#123456",
    description: "自定义颜色"
  },
};

// 在 TEXT_STYLES 对象中添加新样式
const TEXT_STYLES = {
  // ... 现有样式
  "custom-text": {
    name: "Custom/Text",
    fontSize: 16,
    lineHeight: 24,
    fontWeight: 400,
    color: "#000000",
  },
};
```

---

## 📖 相关文档

- `figma-automation-script.js` - 完整脚本源码
- `FIGMA_QUICK_START.md` - Figma 手动操作指南
- `MYSTOCKS_DESIGN_SPECIFICATION.md` - 设计规范文档
- `design-tokens.json` - 设计 Token 定义

---

## 💡 提示

1. **脚本是幂等的**: 可以多次运行，重复运行会创建重复样式（名称后加数字）
2. **建议第一次运行**: 在空白文件中运行，避免与现有样式冲突
3. **保存脚本**: 可以将脚本保存为 Figma 插件，方便重复使用
4. **定制化**: 根据项目需求修改脚本中的颜色、字体定义

---

**祝您使用愉快！如有问题，请参考常见问题章节或查阅相关文档。** 🎨
