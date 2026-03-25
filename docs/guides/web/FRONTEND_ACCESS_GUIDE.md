# 🎉 MyStocks ArtDeco 前端 - 访问指南

**日期**: 2025-12-30
**状态**: ✅ 成功启动，可以访问

---

## 🌐 访问地址

### 本地访问（推荐）
```
http://localhost:3020/
```

### 网络访问（如需从其他设备访问）
- http://10.255.255.254:3020/
- http://172.26.26.12:3020/

---

## 🎨 主要页面

| 页面 | 路径 | 说明 |
|------|------|------|
| **仪表盘** | `/dashboard` | ArtDeco 风格主页，市场概览 |
| **股票详情** | `/stock-detail/[symbol]` | 个股详情，ArtDeco 图表 |
| **技术分析** | `/technical` | 技术指标分析页面 |
| **指标库** | `/indicators` | 技术指标展示 |
| **市场行情** | `/market` | 实时行情数据 |
| **风险监控** | `/risk` | 风险监控仪表盘 |
| **公告监控** | `/announcement` | 公告监控页面 |
| **策略管理** | `/strategy` | 量化策略管理 |
| **回测分析** | `/backtest` | 回测分析工具 |

---

## 🖼️ 您将看到的 ArtDeco 特征

### 视觉设计
- ✅ **黑金配色** - 黑曜石黑背景 + 金属金色强调
- ✅ **Marcellus 字体** - 古典罗马风格标题
- ✅ **Josefin Sans 字体** - 几何复古正文字体
- ✅ **全大写排版** - 标题全部大写，0.2em 字间距
- ✅ **尖角设计** - 零圆角，锐利边缘
- ✅ **几何装饰** - L 形角落、阶梯角、钻石形图标

### 交互效果
- ✅ **卡片悬停** - 金色边框从 30% → 100% 不透明度，向上提升 8px
- ✅ **按钮悬停** - 金色发光效果增强（300ms 过渡）
- ✅ **输入聚焦** - 底部金色边框 + 光晕阴影
- ✅ **平滑过渡** - 所有动画 300-500ms，机械式流畅感

### 页面元素
- ✅ **罗马数字** - I, II, III, IV 章节编号
- ✅ **金色分割线** - 标题上下方的装饰线条
- ✅ **日光放射效果** - 头部背景的放射状渐变
- ✅ **对角线交叉阴影** - 背景的细微纹理图案
- ✅ **双边框框架** - 卡片和图表的框架套框架

---

## ✅ 问题已解决

### 1. 504 Outdated Optimize Dep 错误
**原因**: Vite 依赖优化缓存损坏
**解决**: 清除 `node_modules/.vite` 缓存并重启

### 2. CSP frame-ancestors 警告
**原因**: `frame-ancestors` 指令不能在 meta 标签中使用
**解决**: 从 CSP meta 标签中移除该指令

### 3. 端口配置
**原因**: 原配置使用 3000-3010 范围（不符合项目规范）
**解决**: 更新为 3020-3029（项目规范的前端端口范围）

---

## 🚀 服务器信息

```
状态: ✅ 正在运行
端口: 3020
进程ID: 51843
启动时间: 2025-12-30 16:45
Vite 版本: 5.4.20
```

---

## 📝 启动命令

### 开发模式（推荐）
```bash
cd web/frontend
npm run dev
```

### 快速启动（跳过类型生成）
```bash
cd web/frontend
npm run dev:no-types
```

### 生产构建
```bash
cd web/frontend
npm run build
```

---

## 🛠️ 故障排除

### 如果页面无法加载

1. **检查服务器状态**
   ```bash
   lsof -i :3020
   ```

2. **查看服务器日志**
   ```bash
   tail -f /tmp/frontend-dev3.log
   ```

3. **清除缓存并重启**
   ```bash
   cd web/frontend
   rm -rf node_modules/.vite
   pkill -f "mystocks_spec/web/frontend"
   npm run dev:no-types
   ```

4. **检查浏览器控制台**
   - 按 F12 打开开发者工具
   - 查看 Console 标签页的错误信息
   - 查看 Network 标签页的请求状态

### 常见错误

**错误**: "Failed to load resource: 504 (Outdated Optimize Dep)"
- **解决**: 清除 Vite 缓存：`rm -rf node_modules/.vite`

**错误**: "Cannot find module"
- **解决**: 安装依赖：`npm install`

**错误**: "Port 3020 is already in use"
- **解决**: 更换端口或终止占用进程：`pkill -f vite`

---

## 🎨 ArtDeco 设计系统文档

完整的设计系统文档位于：
- **实施指南**: `/docs/web/ART_DECO_IMPLEMENTATION_REPORT.md`
- **快速参考**: `/docs/web/ART_DECO_QUICK_REFERENCE.md`
- **组件展示**: `/docs/web/ART_DECO_COMPONENT_SHOWCASE.md`
- **最终报告**: `/docs/web/ART_DECO_FINAL_REPORT.md`

---

## 🎊 开始使用

1. **打开浏览器**
2. **访问**: http://localhost:3020/
3. **体验全新的 Art Deco 装饰艺术风格界面！**

---

**提示**: 如果您看到黑金配色、几何装饰和 Marcellus 字体，说明 ArtDeco 样式已成功加载！🎉

**生成时间**: 2025-12-30 16:47
**项目**: MyStocks 量化交易平台
**版本**: ArtDeco Frontend v1.0
