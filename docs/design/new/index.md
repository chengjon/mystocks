# A股量化交易管理系统 - Web端设计方案 (ArtDeco版)

## 1. 设计概述

本设计方案旨在为A股量化交易管理系统打造一个专业、高效且具有独特美感的Web界面。基于**ArtDeco (装饰艺术)** 风格，结合现代数据可视化需求，创造出既复古奢华又清晰易读的专业交易终端体验。

### 1.1 设计理念
- **形式追随功能**: 在保持装饰艺术风格的同时，首要保证数据的清晰度和操作的高效性。
- **几何美学**: 大量运用对称、阶梯状造型、放射状线条和几何边框。
- **对比与质感**: 深色背景衬托金色/银色线条，营造高端、稳重的金融科技感。

### 1.2 视觉规范 (ArtDeco Modern)

#### 颜色系统
*   **背景色 (Backgrounds)**
    *   `Global Bg`: `#0F1215` (深邃黑蓝，接近午夜蓝)
    *   `Card Bg`: `#161B22` (略浅的黑蓝，用于卡片容器)
    *   `Header/Sidebar Bg`: `#0A0C0E` (极深黑)

*   **主色调 (Primary - The "Gold")**
    *   `Gold Primary`: `#D4AF37` (经典金属金，用于强调、选中态、边框)
    *   `Gold Hover`: `#F4CF57` (高亮金)
    *   `Gold Muted`: `#8A7120` (暗金，用于次级装饰)

*   **辅助色 (Secondary - The "Silver")**
    *   `Silver Text`: `#E5E4E2` (铂金灰，主要文本)
    *   `Silver Dim`: `#8B9BB4` (冷灰，次级文本/标签)

*   **语义色 (Semantic - A股红绿)**
    *   `Rise/Buy`: `#C94042` (宝石红 - A股涨) *注：保持A股习惯，红涨绿跌*
    *   `Fall/Sell`: `#3D9970` (祖母绿 - A股跌)
    *   `Info`: `#4A90E2` (蓝宝石)
    *   `Warning`: `#E67E22` (琥珀色)

#### 排版 (Typography)
*   **标题 (Headers)**: 采用无衬线几何字体 (Geometric Sans)，全大写，字间距加宽 (Letter-spacing: 1px)。
*   **正文/数据 (Body/Data)**: 等宽字体 (Monospace) 用于数字展示，确保对齐；清晰的无衬线字体用于文本。

#### 组件风格 (Component Style)
*   **卡片 (Cards)**:
    *   直角或极小圆角 (2px)。
    *   **双线边框**: 外层细金线 (1px solid #D4AF37)，内层深色衬垫。
    *   **角落装饰**: 卡片四角可添加装饰性直角线条。
*   **按钮 (Buttons)**:
    *   实心金底黑字 (Primary Action)。
    *   透明底金边框 (Secondary Action)。
    *   悬停效果：光泽扫描或亮度提升。
*   **图表 (Charts)**:
    *   背景透明。
    *   网格线使用极低透明度的金色或灰色。
    *   曲线颜色高亮高饱和度。

## 2. 页面架构与导航

采用经典的 **侧边栏 + 顶部栏 + 内容区** 布局。

### 2.1 侧边栏 (Sidebar)
*   宽度: 240px (固定)。
*   Logo: 顶部居中，ArtDeco风格几何Logo。
*   导航项:
    *   图标 + 文字。
    *   选中态：左侧金色竖条高亮，背景微亮，文字金色。
    *   分组：使用金色细分割线。

### 2.2 顶部栏 (Top Bar)
*   高度: 60px。
*   内容:
    *   左侧: 当前页面标题 (面包屑)。
    *   中间: 全局搜索框 (股票代码/策略名)，ArtDeco装饰边框。
    *   右侧:
        *   系统状态指示灯 (API连接、行情延迟、GPU负载)。
        *   通知铃铛。
        *   用户头像/账户信息。

### 2.3 内容区域 (Content Area)
*   栅格系统: 基于12列或24列栅格。
*   响应式: 适配 1920p (大屏交易), 1440p (标准), 1080p (最小适配)。

## 3. 页面清单 (Pages)

本设计包含以下核心页面：

| 序号 | 页面名称 | 英文标识 | 功能核心 | API 依赖 |
| :--- | :--- | :--- | :--- | :--- |
| 01 | **主控仪表盘** | Dashboard | 全局概览、核心指数、实时预警 | market, monitoring |
| 02 | **市场行情中心** | Market Center | 实时行情、多周期K线、板块资金 | market, tdx |
| 03 | **智能选股池** | Stock Screener | 股票池管理、条件选股、板块轮动 | market, technical |
| 04 | **数据深度分析** | Data Analysis | 财务分析、多维数据关联、IC分析 | data, market |
| 05 | **策略研配实验室** | Strategy Lab | 策略开发、参数配置、模型管理 | strategy |
| 06 | **回测竞技场** | Backtest Arena | 历史回测、性能报告、参数优化 | strategy, market |
| 07 | **实战交易台** | Trade Station | 模拟/实盘交易、持仓管理、订单流 | trade |
| 08 | **风险监控中心** | Risk Center | 账户风控、合规检查、系统日志 | monitoring, risk |
| 09 | **系统配置中心** | System Settings | 数据源配置、用户权限、API管理 | system, auth |

---

> **API 整合说明**:
> 所有页面设计均基于 `web/backend/app/api/VERSION_MAPPING.py` 中定义的 `/api/v1/` 和 `/api/v2/` 接口。
