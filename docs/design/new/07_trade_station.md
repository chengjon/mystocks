# 07 实战交易台 (Trade Station)

## 1. 页面概览
**功能定位**: 资金与指令的交汇点。支持模拟盘与实盘的交易指令下达及资产管理。
**视觉焦点**: 交易下单区的操作明确性，以及持仓盈亏的实时跳动。

## 2. 布局结构

### 2.1 资产账户栏 (Account Header)
*   **组件**: `AssetStrip`
*   **数据**:
    *   **总资产**: 动态数字。
    *   **可用资金**: 下单可用余额。
    *   **股票市值**: 当前持仓总值。
    *   **当日盈亏**: 绝对值与百分比。
*   **API**: `GET /api/v1/trade/account`

### 2.2 下单面板 (Order Entry - Left)
*   **组件**: `OrderForm`
*   **Tabs**: 买入 (Buy) / 卖出 (Sell) / 撤单 (Cancel).
*   **表单项**:
    *   **代码**: 输入代码，自动显示名称/现价/涨跌停价。
    *   **价格**: 限价 (Limit) / 市价 (Market).
    *   **数量**: 可用资金/持仓自动计算最大可买/可卖数量。快捷比例按钮 (1/4, 1/2, All).
*   **按钮**: 超大号 "买入" (红) / "卖出" (绿) 按钮。
*   **API**: `POST /api/v1/trade/orders`

### 2.3 持仓与订单 (Positions & Orders - Right)
*   **组件**: `TradeTabs`
*   **Tab 1: 当前持仓 (Positions)**
    *   列表: 代码, 名称, 持仓量, 可卖量, 成本价, 现价, 浮动盈亏, 盈亏比例。
    *   操作: 快速 "卖出" / "T+0" 按钮。
    *   **API**: `GET /api/v1/trade/positions`
*   **Tab 2: 当日委托 (Working Orders)**
    *   列表: 时间, 代码, 方向, 价格, 数量, 已成, 状态.
    *   操作: "撤单" 按钮。
    *   **API**: `GET /api/v1/trade/orders?status=open`
*   **Tab 3: 当日成交 (Fills)**
    *   列表: 成交时间, 代码, 价格, 数量, 金额.

## 3. 交互设计
*   **防误触**: 下单按钮点击后弹出二次确认框 (包含预估手续费信息)。
*   **刷新机制**: 资产与持仓数据通过 WebSocket 实时推送，或下单后立即触发刷新。

## 4. API 映射汇总
| 组件区域 | 核心 API 端点 | 请求方式 | 备注 |
| :--- | :--- | :--- | :--- |
| 账户资产 | `/api/v1/trade/account` | GET | |
| 持仓查询 | `/api/v1/trade/positions` | GET | |
| 委托下单 | `/api/v1/trade/orders` | POST | |
| 撤单 | `/api/v1/trade/orders/{id}` | DELETE | |
