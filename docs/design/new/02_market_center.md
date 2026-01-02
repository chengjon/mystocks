# 02 市场行情中心 (Market Center)

## 1. 页面概览
**功能定位**: 深度看盘与技术分析的核心工作台。提供类似通达信/同花顺的专业级看盘体验。
**视觉焦点**: 位于中央的专业K线图，辅以右侧的盘口数据。

## 2. 布局结构 (Three-Pane Layout)

采用经典的 **左侧列表 - 中间图表 - 右侧盘口** 布局。

### 2.1 左侧：行情列表与导航 (Market Navigator)
*   **宽度**: 280px
*   **组件**: `StockListPanel`
*   **功能**:
    *   **搜索**: 顶部固定搜索框，支持拼音/代码搜索。
    *   **分组Tabs**:
        *   **自选 (Watchlist)**: 用户关注的股票。
        *   **主要指数 (Indices)**: 宽基指数。
        *   **行业/概念 (Sectors)**: 板块涨幅排行。
    *   **列表**: 显示 代码/名称/现价/涨跌幅。
        *   支持按涨跌幅排序。
        *   **ArtDeco**: 选中行使用金色边框高亮，背景色加深。
*   **API**:
    *   `GET /api/v1/watchlist/groups` (获取分组)
    *   `GET /api/v1/market/quotes?list_id=...` (获取列表实时数据)

### 2.2 中间：专业K线图表 (Pro Chart)
*   **组件**: `KlineChartWidget` (基于 Klinechart 库)
*   **功能**:
    *   **多周期切换**: 分时, 1m, 5m, 15m, 30m, 60m, Day, Week, Month。
    *   **主图指标**: MA, BOLL, EMA, SAR等 (叠加在K线上)。
    *   **副图指标**: MACD, KDJ, RSI, WR, CCI, VOL (底部显示，支持多开)。
    *   **工具栏**: 画线工具 (趋势线, 斐波那契), 缩放, 十字光标。
    *   **特色功能**: 标注买卖点 (从交易记录映射)。
*   **API**:
    *   `GET /api/v1/market/kline?symbol=...&period=...&limit=...`
    *   `GET /api/v1/technical/indicators` (获取计算好的指标数据，或者前端基于K线计算)

### 2.3 右侧：盘口与深度 (Order Book & Depth)
*   **宽度**: 300px
*   **组件**: `Level1QuotePanel`
*   **功能**:
    *   **五档/十档盘口**: 卖五~卖一 / 买一~买五。
        *   显示 价格 | 量 | 挂单数(如可用)。
        *   使用红/绿文字区分价格相对于昨收的涨跌。
        *   **量条**: 背景显示量的相对长度条 (ArtDeco: 使用半透明金色/银色条)。
    *   **逐笔成交 (Tick)**: 实时滚动的最新成交记录 (时间/价格/量/方向)。
    *   **基本资料 (F10摘要)**: 市盈率, 市净率, 总市值, 流通市值, 换手率。
*   **API**:
    *   `GET /api/v1/market/quotes?symbol=...&detail=true` (含盘口)
    *   `GET /api/v1/market/ticks?symbol=...` (如果支持)

## 3. 底部：扩展信息面板 (Bottom Panel - Collapsible)
*   **位置**: 图表下方，可折叠。
*   **Tabs**:
    *   **资金流向**: 该股的主力/超大/大/中/小单分布。
    *   **龙虎榜**: 关联的龙虎榜数据 (`GET /api/v1/market/lhb`).
    *   **相关资讯**: 个股新闻/公告 (`GET /api/v1/announcement`).

## 4. 交互设计
*   **联动**: 左侧点击股票 -> 中间K线刷新 + 右侧盘口刷新 -> 浏览器URL参数更新 (方便分享)。
*   **键盘精灵**: 输入代码直接弹出搜索框并跳转。
*   **图表交互**: 滚轮缩放，拖拽平移，双击全屏。

## 5. API 映射汇总
| 组件区域 | 核心 API 端点 | 请求方式 | 备注 |
| :--- | :--- | :--- | :--- |
| K线数据 | `/api/v1/market/kline` | GET | 核心接口 |
| 实时报价 | `/api/v1/market/quotes` | GET/WS | 需高频刷新 |
| 龙虎榜 | `/api/v1/market/lhb` | GET | 个股关联数据 |
| 搜索 | `/api/v1/market/search` | GET | 模糊匹配 |
