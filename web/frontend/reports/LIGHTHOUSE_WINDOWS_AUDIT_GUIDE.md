# Lighthouse 审计指南 - Windows主机版

> **参考指南说明**:
> 本文件用于提供 Web 子系统的使用方法、操作指引、接口接入说明、排障提示或结构参考，帮助理解局部实现与协作方式。
> 其中的步骤、示例、端口、目录和操作建议应先与 `architecture/STANDARDS.md`、当前代码实现及最新验证结果核对；若涉及仓库执行流程、命令或协作约束，再补充参考根目录 `AGENTS.md`。本文件不得单独视为仓库共享规则或当前状态的唯一事实来源。


## 📋 概述

由于WSL2环境限制，本文档提供在Windows主机上运行Lighthouse审计的详细步骤。

## 🎯 审计目标页面

### 优先级1 - 核心页面 (必须审计)
1. http://localhost:3020 - 仪表盘 (Dashboard)
2. http://localhost:3020/market/list - 市场列表
3. http://localhost:3020/risk-monitor/overview - 风险监控
4. http://localhost:3020/strategy-hub/management - 策略管理

### 优先级2 - 重要页面 (建议审计)
5. http://localhost:3020/market/realtime - 实时行情
6. http://localhost:3020/market-data/fund-flow - 资金流向
7. http://localhost:3020/market-data/longhubang - 龙虎榜

## 🔧 方法1: 使用Chrome DevTools (推荐)

### 步骤:

#### 1. 确保开发服务器运行
```bash
# 在WSL2中检查服务器状态
lsof -i :3020
# 应该看到: COMMAND   PID USER   FD   TYPE  DEVICE SIZE/OFF NODE NAME
#          node    84265 ...    tcp  ...0.0.0.0:3020  LISTEN
```

#### 2. 在Windows浏览器中打开页面
- 打开Chrome浏览器 (推荐 v120+)
- 访问: `http://localhost:3020`
- 等待页面完全加载

#### 3. 打开Chrome DevTools
- **方法A**: 按F12键
- **方法B**: 右键点击页面 → "检查"
- **方法C**: Ctrl+Shift+I (Windows)

#### 4. 运行Lighthouse审计
1. 点击DevTools顶部的 **"Lighthouse"** 标签
2. 配置审计选项:
   - **Categories**:
     - ✅ Performance (性能)
     - ✅ Accessibility (可访问性)
     - ✅ Best Practices (最佳实践)
     - ✅ SEO (搜索引擎优化)
   - **Device**: Desktop (桌面)
   - **Throttling**: No throttling (首次审计，无节流)
3. 点击 **"Analyze page load"** 按钮
4. 等待审计完成 (约30-60秒)

#### 5. 保存报告
- 审计完成后，点击右上角的 **"Open report"** 按钮
- 报告会在新标签页打开
- 按 Ctrl+S 保存报告
- 保存位置: `web/frontend/reports/lighthouse-dashboard.html`
- 保存类型: "网页，完整"

#### 6. 记录关键指标
在报告中查找并记录以下数据:

**Performance分数** (0-100):
- First Contentful Paint (FCP)
- Largest Contentful Paint (LCP)
- Total Blocking Time (TBT)
- Cumulative Layout Shift (CLS)
- Speed Index

**Accessibility分数** (0-100):
- 颜色对比度问题数
- 图片alt属性缺失数
- 表单标签问题数

**Best Practices分数** (0-100):
- 警告数量
- 错误数量

**SEO分数** (0-100):
- Meta描述
- 结构化数据
- 可爬爬链接

#### 7. 对所有目标页面重复步骤2-6

## 🖥️ 方法2: 使用Lighthouse CLI (Windows)

### 前置条件:
1. 在Windows上安装Node.js
2. 打开Windows PowerShell或命令提示符

### 步骤:

#### 1. 安装Lighthouse (如果未安装)
```powershell
npm install -g lighthouse
```

#### 2. 运行审计
```powershell
# 进入项目目录
cd C:\path\to\mystocks_spec\web\frontend

# 审计仪表盘
lighthouse http://localhost:3020 --output=html --output-path=./reports/lighthouse-dashboard.html --preset=desktop

# 审计市场列表
lighthouse http://localhost:3020/market/list --output=html --output-path=./reports/lighthouse-market.html --preset=desktop

# 审计风险监控
lighthouse http://localhost:3020/risk-monitor/overview --output=html --output-path=./reports/lighthouse-risk.html --preset=desktop

# 审计策略管理
lighthouse http://localhost:3020/strategy-hub/management --output=html --output-path=./reports/lighthouse-strategy.html --preset=desktop
```

## 📊 预期结果与目标

### 当前预期分数 (基于代码分析)
| 指标 | 当前 | 目标 |
|------|------|------|
| Performance | 60-70 | 85+ |
| Accessibility | 93+ | 95+ |
| Best Practices | 85-90 | 95+ |
| SEO | 75-80 | 85+ |

### Core Web Vitals目标
| 指标 | 目标值 | 状态 |
|------|--------|------|
| FCP | < 1.8s | ⏳ |
| LCP | < 2.5s | ⏳ |
| TBT | < 200ms | ⏳ |
| CLS | < 0.1 | ⏳ |

## 📝 审计报告模板

创建审计结果汇总表:

```markdown
# Lighthouse审计结果汇总

## 审计日期
2025-12-26

## 审计环境
- 浏览器: Chrome [版本]
- 设备: Desktop
- 网络节流: None (首次审计)

## 页面审计结果

| 页面 | Performance | Accessibility | Best Practices | SEO | LCP | FCP | CLS |
|------|-------------|---------------|----------------|-----|-----|-----|-----|
| /dashboard | [分数] | [分数] | [分数] | [分数] | [时间] | [时间] | [值] |
| /market/list | [分数] | [分数] | [分数] | [分数] | [时间] | [时间] | [值] |
| /risk-monitor/overview | [分数] | [分数] | [分数] | [分数] | [时间] | [时间] | [值] |
| /strategy-hub/management | [分数] | [分数] | [分数] | [分数] | [时间] | [时间] | [值] |

## 主要发现

### Performance问题
1. [问题描述]
   - 影响: [影响范围]
   - 解决方案: [具体步骤]

### Accessibility问题
1. [问题描述]
   - 修复建议: [具体步骤]

## 优化建议

### 短期 (1周内)
- [ ] 优化1
- [ ] 优化2

### 中期 (2-4周)
- [ ] 优化1
- [ ] 优化2

## 下一步行动
- [ ] 审计剩余页面
- [ ] 实施高优先级修复
- [ ] 重新审计验证改进
```

## 🔍 常见问题排查

### 问题1: 页面无法访问
- **检查**: WSL2中开发服务器是否运行
  ```bash
  lsof -i :3020
  ```
- **解决**: 启动开发服务器
  ```bash
  cd web/frontend
  npm run dev
  ```

### 问题2: Lighthouse标签找不到
- **检查**: Chrome版本是否过旧
- **解决**: 更新Chrome到最新版本
  - 访问: chrome://settings/help
  - 点击"更新Google Chrome"

### 问题3: 审计超时
- **检查**: 页面是否有JavaScript错误
- **解决**: 打开Console标签查看错误信息
  ```javascript
  // 在Console中运行
  window.location.href
  ```

### 问题4: 报告无法保存
- **检查**: reports目录是否存在
- **解决**: 创建目录
  ```bash
  mkdir -p web/frontend/reports
  ```

## 📚 参考资源

- [Lighthouse官方文档](https://developer.chrome.com/docs/lighthouse/)
- [Core Web Vitals](https://web.dev/vitals/)
- [性能优化指南](https://web.dev/fast/)
- [可访问性指南](https://web.dev/accessibility/)

## ✅ 完成检查清单

审计完成后，确保:
- [ ] 所有目标页面已审计
- [ ] HTML报告已保存到`reports/`目录
- [ ] 关键指标已记录到汇总表
- [ ] 主要问题已识别和分类
- [ ] 优化建议已优先级排序
- [ ] 报告已提交给团队审查

---

**最后更新**: 2025-12-26
**版本**: 1.0
**状态**: Ready for use
