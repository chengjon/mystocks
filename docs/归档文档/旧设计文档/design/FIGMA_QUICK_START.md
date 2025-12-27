# Figma 快速上手指南 - MyStocks 设计导入 Pixso

> **目标**: 30分钟内完成 MyStocks 设计，导出并导入到 Pixso
> **难度**: ⭐⭐☆☆☆ (简单)
> **费用**: 完全免费

---

## 🚀 快速开始（30分钟流程）

### ⏱️ 第 1-5 分钟: 注册并设置 Figma

#### 步骤 1: 访问 Figma 官网

```
URL: https://www.figma.com
```

#### 步骤 2: 注册免费账号

**3种注册方式**:
1. **Google 账号** (推荐 - 最快)
   - 点击 "Sign up with Google"
   - 选择您的 Google 账号
   - 授权登录

2. **邮箱注册**
   - 输入邮箱地址
   - 设置密码
   - 验证邮箱

3. **Apple ID**
   - 点击 "Sign up with Apple"
   - 使用 Apple ID 登录

#### 步骤 3: 完成新手引导

```
1. 选择角色: Designer / Developer (选 Designer)
2. 团队规模: Solo / Small team (选 Solo)
3. 使用场景: UI Design (选择此项)
4. 点击 "Get started"
```

---

### ⏱️ 第 6-10 分钟: 获取 Element Plus UI Kit

#### 步骤 4: 访问 Figma Community

**方法 1: 通过搜索**
```
1. 点击左侧 "Community" 图标
2. 搜索栏输入: "Element Plus"
3. 找到官方 UI Kit (通常有蓝色徽章)
4. 点击 "Duplicate" (复制到您的项目)
```

**方法 2: 直接访问链接**
```
URL: https://www.figma.com/community/search?model_type=files&q=element%20plus

或者搜索其他高质量组件库:
- "Element UI"
- "Ant Design"
- "Element Plus Components"
```

**如果找不到现成 UI Kit，使用替代方案**:
```
1. 搜索 "Dashboard UI Kit"
2. 选择任一免费 UI Kit
3. 我们将基于此进行定制
```

#### 步骤 5: 重命名文件

```
1. 双击文件名
2. 改为: "MyStocks Design System"
3. Enter 确认
```

---

### ⏱️ 第 11-15 分钟: 安装插件并导入设计 Token

#### 步骤 6: 安装 Tokens Studio 插件

```
1. 菜单栏 → Plugins → Browse plugins in Community
2. 搜索: "Tokens Studio for Figma"
3. 找到官方插件 (Tokens Studio 团队开发)
4. 点击 "Install"
5. 点击 "Run" 运行插件
```

**插件界面说明**:
```
┌─────────────────────────────────────┐
│ Tokens Studio                       │
├─────────────────────────────────────┤
│ [Load from file]                    │
│ [Load from JSON]                    │
│ [Apply tokens]                      │
└─────────────────────────────────────┘
```

#### 步骤 7: 导入 design-tokens.json

**上传文件到 Figma**:

由于 Figma 在浏览器中运行，您需要先访问本地文件：

```bash
# 文件路径
/opt/claude/mystocks_spec/docs/design/design-tokens.json
```

**导入步骤**:
```
1. 在 Tokens Studio 插件中点击 "Load from file"
2. 点击 "Select JSON file"
3. 浏览到: /opt/claude/mystocks_spec/docs/design/design-tokens.json
4. 点击 "Open"
5. 等待导入完成（约 5 秒）
```

**如果无法直接访问文件系统**（浏览器限制）:

**替代方案 - 复制粘贴 JSON**:
```
1. 打开本地文件: design-tokens.json
2. 全选内容 (Ctrl+A / Cmd+A)
3. 复制 (Ctrl+C / Cmd+C)
4. 在 Tokens Studio 插件中点击 "Load from JSON"
5. 粘贴内容 (Ctrl+V / Cmd+V)
6. 点击 "Import"
```

#### 步骤 8: 应用 Token 到样式

```
1. 在 Tokens Studio 插件中点击 "Apply tokens"
2. 勾选以下选项:
   ✅ Create color styles
   ✅ Create text styles
   ✅ Create effect styles
3. 点击 "Apply"
4. 等待应用完成（约 10 秒）
```

**验证导入成功**:
```
1. 关闭 Tokens Studio 插件
2. 左侧面板 → Assets (图标像 4个方块)
3. 查看 "Local styles":
   - Colors: 应该看到 Primary/Blue, Success/Green 等
   - Text: 应该看到 Heading/XL, Body/Regular 等
```

---

### ⏱️ 第 16-25 分钟: 创建核心组件

#### 步骤 9: 创建按钮组件

##### 9.1 创建基础矩形

```
1. 按 R 键 (Rectangle 工具)
2. 在画布上绘制矩形
3. 右侧属性面板设置:
   - W (宽度): 120 (自动调整)
   - H (高度): 32
   - Fill (填充): Primary/Blue (从样式中选择)
   - Corner radius (圆角): 4
```

##### 9.2 添加文本

```
1. 按 T 键 (Text 工具)
2. 在矩形中间点击
3. 输入: "按钮文字"
4. 右侧属性面板设置:
   - Text style: Body/Regular
   - Fill: #FFFFFF (白色)
   - Alignment: Center (水平和垂直居中)
```

##### 9.3 调整布局

```
1. 选中矩形 (点击矩形边框)
2. 右侧面板 → Auto layout (快捷键 Shift+A)
3. 设置内边距:
   - Horizontal padding: 20
   - Vertical padding: 12
   - Item spacing: 0
4. 矩形会自动调整大小适应文本
```

##### 9.4 创建组件

```
1. 选中整个按钮 (矩形+文本)
2. 右键 → Create component
   或快捷键: Ctrl+Alt+K (Win) / Cmd+Option+K (Mac)
3. 命名: "Button/Primary/Default"
```

##### 9.5 创建变体

```
1. 复制按钮 4 次 (Ctrl+D / Cmd+D)
2. 排列在一行
3. 修改每个副本:
   - Button/Primary/Default (保持不变)
   - Button/Success/Default (填充改为 Success/Green)
   - Button/Warning/Default (填充改为 Warning/Orange)
   - Button/Danger/Default (填充改为 Danger/Red)
   - Button/Default/Default (填充改为 White, 边框 1px #DCDFE6, 文本改为 #606266)

4. 全选 5 个按钮
5. 右键 → Combine as variants
6. 现在您有一个带 5 种类型的按钮组件
```

#### 步骤 10: 创建  组件

##### 10.1 创建数值文本

```
1. 按 T 键创建文本框
2. 输入: "12.34"
3. 设置样式:
   - Text style: Number/Small (如果已导入)
   - 或手动设置: 14px, SF Mono/Monaco, Medium (500)
   - Fill: Financial/Up (#F56C6C 红色)
```

##### 10.2 添加涨跌图标

**使用文本符号**:
```
1. 创建新文本框
2. 输入: "▲" (三角形向上)
3. 设置:
   - Font size: 12px
   - Fill: Financial/Up (#F56C6C)
```

**或使用 Figma 图标**:
```
1. 插件 → Browse plugins → 搜索 "Iconify"
2. 安装并运行
3. 搜索 "arrow up"
4. 选择简单的三角形图标
5. 设置颜色为 Financial/Up
```

##### 10.3 添加涨跌幅文本

```
1. 创建文本框
2. 输入: "(+2.50%)"
3. 设置:
   - Font size: 12px
   - Fill: Financial/Up (#F56C6C)
   - Opacity: 80%
```

##### 10.4 组合成 Auto layout

```
1. 选中 3 个元素 (图标、数值、涨跌幅)
2. 按 Shift+A (Auto layout)
3. 设置:
   - Direction: Horizontal
   - Gap: 4
   - Alignment: Center
```

##### 10.5 创建组件并添加变体

```
1. 选中整个组合 → Create component
2. 命名: "/Up/Default"
3. 复制 2 次创建变体:
   - /Down/Default (颜色改为 Financial/Down #67C23A 绿色, 图标改为 ▼)
   - /Flat/Default (颜色改为 Financial/Flat #909399 灰色, 图标改为 —)
4. 全选 3 个 → Combine as variants
```

#### 步骤 11: 创建 StockCard 组件

##### 11.1 创建卡片容器

```
1. 按 R 键绘制矩形
2. 设置:
   - W: 360
   - H: 200 (自动调整)
   - Fill: Background/Card (#FFFFFF)
   - Corner radius: 8
   - Effect: Drop shadow
     - X: 0, Y: 2, Blur: 4, Color: #000000 5%
```

##### 11.2 添加内容

**顶部: 股票信息**
```
1. 股票代码:
   - Text: "000001"
   - Style: Heading/M (#303133, 20px, Medium)

2. 股票名称:
   - Text: "平安银行"
   - Style: Body/Regular (#606266, 14px)

3. 标签:
   - 创建小矩形: 高度 20px, 圆角 2px
   - 填充: Info/Gray (#909399) 10% 透明度
   - 添加文本: "银行" (12px, #909399)
   - Auto layout: padding 4px 8px
```

**中间: 当前价格**
```
1. 插入  组件 (从 Assets 面板拖拽)
2. 切换到 Large 尺寸变体
3. 修改数值为实际价格
```

**底部: 指标网格**
```
1. 创建 3 列网格:
   Column 1: "涨跌额" +
   Column 2: "成交量" + "123.45万"
   Column 3: "换手率" + "1.23%"

2. 标签样式:
   - Text: Caption (12px, #909399)

3. 数值样式:
   - Text: Body/Regular (14px, #303133)
   - 或使用  组件
```

**最底部: 操作按钮**
```
1. 插入 Button 组件 (Default 变体)
2. 文本改为 "自选"
3. 添加星形图标 (可选)

4. 插入 Button 组件 (Primary 变体)
5. 文本改为 "详情"
```

##### 11.3 应用 Auto layout

```
1. 选中卡片内所有元素
2. 按 Shift+A
3. 设置:
   - Direction: Vertical
   - Gap: 12
   - Padding: 16
   - Horizontal resizing: Fixed (360px)
   - Vertical resizing: Hug contents
```

##### 11.4 创建组件

```
1. 选中整个卡片 → Create component
2. 命名: "StockCard/Default"
```

---

### ⏱️ 第 26-30 分钟: 导出并导入 Pixso

#### 步骤 12: 整理和导出

##### 12.1 整理页面

```
1. 创建新页面:
   - 左侧面板 → 右键 Pages → New page
   - 命名: "Components" (组件库)
   - 命名: "Pages" (页面模板)

2. 移动组件到 Components 页面:
   - 拖拽所有组件到 Components 页面
```

##### 12.2 导出 .fig 文件

```
1. 菜单栏 → File → Save as .fig
   或快捷键: Ctrl+Shift+S (Win) / Cmd+Shift+S (Mac)

2. 保存位置:
   - 如果使用浏览器版 Figma: 下载到本地
   - 文件名: "MyStocks_Design_v1.0.fig"

3. 等待导出完成（约 10 秒）
```

**如果菜单中没有 "Save as .fig" 选项**:

**替代方法 - 导出选定帧**:
```
1. 选中所有组件和页面 (Ctrl+A / Cmd+A)
2. 右键 → Copy as PNG/SVG
3. 或使用 File → Export → 选择 PDF 格式

注意: Pixso 最佳兼容 .fig 格式
如无法导出 .fig，请使用下面的方法
```

**在线共享方法** (无需下载):
```
1. 点击右上角 "Share" 按钮
2. 设置权限: "Anyone with the link can view"
3. 复制链接
4. 在 Pixso 中使用 "导入 Figma 链接" 功能
```

#### 步骤 13: 导入到 Pixso

##### 13.1 登录 Pixso

```
URL: https://pixso.cn
```

##### 13.2 导入文件

**方法 1: 本地文件导入** (.fig 文件)
```
1. 点击 "导入" 按钮
2. 选择 "从本地导入"
3. 文件类型: Figma (.fig)
4. 选择文件: MyStocks_Design_v1.0.fig
5. 点击 "开始导入"
6. 等待导入完成（约 1-3 分钟）
```

**方法 2: Figma 链接导入** (推荐)
```
1. 在 Pixso 点击 "导入"
2. 选择 "导入 Figma 文件"
3. 粘贴 Figma 分享链接
4. 点击 "导入"
5. Pixso 会自动抓取 Figma 文件并导入
```

##### 13.3 验证导入结果

检查以下内容:
```
✅ 颜色样式 (Primary, Success, Danger, Financial 等)
✅ 文本样式 (Heading/XL, Body/Regular, Number/Large 等)
✅ 组件库
   ├─ Button (5 种类型变体)
   ├─  (3 种涨跌变体)
   └─ StockCard
✅ 页面结构
✅ 图层组织
```

如果有样式丢失:
```
1. 检查字体是否存在 (PingFang SC / Microsoft YaHei)
2. 手动重新创建缺失的颜色样式
3. 调整组件变体设置
```

---

## 🎯 完成！

您现在已经:
- ✅ 在 Figma 中创建了 MyStocks 设计系统
- ✅ 导入了设计 Token
- ✅ 创建了核心组件 (Button, , StockCard)
- ✅ 成功导入到 Pixso

---

## 📚 进阶步骤（可选）

### 创建更多组件

参考 `COMPONENT_LIBRARY_SPECIFICATION.md` 继续创建:

1. **表格组件**
   - 表格头部
   - 表格行（普通、斑马纹、悬停、选中）
   - 单元格类型

2. **搜索栏组件**
   - 输入框 + 搜索按钮
   - 自动完成下拉框
   - 搜索结果项

3. **图表组件**
   - K线图占位框
   - 图例组件
   - 坐标轴标签

### 创建页面模板

参考 `MYSTOCKS_DESIGN_SPECIFICATION.md` 的页面模板章节:

1. **仪表盘页面**
   - 顶部导航栏
   - 侧边栏菜单
   - 统计卡片网格
   - 图表区域
   - 数据表格

2. **股票列表页**
   - 面包屑导航
   - 查询表单
   - 数据表格
   - 分页器

3. **股票详情页**
   - 基本信息卡片
   - K线图 Tab
   - 指标 Tab
   - 历史数据 Tab

---

## ❓ 常见问题

### Q1: Figma 是否完全免费？

**A**: 是的，个人使用完全免费。
- 免费版限制: 最多 3 个项目文件
- 无限制使用所有设计功能
- 无限制使用插件
- 对于我们的单个项目来说完全够用

### Q2: 如果找不到 Element Plus UI Kit 怎么办？

**A**: 使用替代方案:
```
1. 搜索其他 UI Kit:
   - "Dashboard UI Kit"
   - "Admin Template"
   - "Material Design Kit"

2. 或者从零开始创建组件
   - 参考 COMPONENT_LIBRARY_SPECIFICATION.md
   - 按照步骤 9-11 逐个创建组件
```

### Q3: design-tokens.json 导入失败？

**A**: 手动创建样式:
```
1. 打开 design-tokens.json 查看颜色值
2. 在 Figma 中手动创建颜色样式:
   - 创建矩形 → 填充颜色 → 创建样式
3. 创建文本样式:
   - 创建文本 → 设置字体/大小 → 创建样式
```

### Q4: Pixso 导入后组件错位？

**A**: 调整方法:
```
1. 检查 Auto layout 设置
2. 重新设置间距和对齐
3. 简化过于复杂的嵌套层级
```

### Q5: 无法导出 .fig 文件？

**A**: 使用在线共享方法:
```
1. Figma 右上角 "Share" → 复制链接
2. Pixso → 导入 → 导入 Figma 链接
3. Pixso 会自动同步 Figma 文件
```

---

## 🔗 相关文档

- `MYSTOCKS_DESIGN_SPECIFICATION.md` - 完整设计规范
- `COMPONENT_LIBRARY_SPECIFICATION.md` - 组件库详细定义
- `design-tokens.json` - 设计 Token 数据
- `PIXSO_IMPORT_GUIDE.md` - Pixso 导入通用指南
- `SKETCH_MANUAL_GUIDE.md` - Sketch 替代方案

---

## 💬 需要帮助？

如果在操作过程中遇到问题:
1. 检查本文档的"常见问题"章节
2. 参考相关设计文档
3. 咨询 Figma Community 或 Pixso 客服

祝您设计愉快！🎨
