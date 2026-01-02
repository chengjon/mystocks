# 05 策略研配实验室 (Strategy Lab)

## 1. 页面概览
**功能定位**: 量化策略的孵化器。提供从策略定义、参数配置到模型选择的全流程管理。
**视觉焦点**: 代码/配置区域的整洁性，以及模型架构的可视化。

## 2. 布局结构

### 2.1 策略库列表 (Strategy Library - Left Sidebar)
*   **组件**: `StrategyList`
*   **内容**:
    *   卡片式列表展示现有策略。
    *   **状态指示**: 开发中 (Draft), 回测中 (Backtesting), 实盘中 (Live).
    *   **快速操作**: 复制, 编辑, 删除.
*   **API**: `GET /api/v1/strategy/strategies`

### 2.2 策略编辑器 (Strategy Editor - Main Area)
*   **组件**: `ConfigEditor` / `CodeEditor`
*   **模式**:
    *   **向导模式**: 表单式配置参数 (标的池, 买入条件, 卖出条件, 止损止盈, 仓位管理).
    *   **代码模式**: Python 代码编辑器 (Monaco Editor)，支持语法高亮和自动补全.
*   **核心配置项**:
    *   **基础**: 策略名称, 描述, 适用周期.
    *   **模型**: 选择依赖的 AI 模型 (`GET /api/v1/strategy/models`).
    *   **参数**: 定义策略超参数 (Hyperparameters) 及其默认值.
*   **API**:
    *   `GET /api/v1/strategy/definitions` (获取可用策略模板)
    *   `POST /api/v1/strategy/strategies` (保存配置)

### 2.3 模型管理面板 (Model Manager - Right Panel)
*   **组件**: `ModelCard`
*   **内容**:
    *   展示当前策略使用的机器学习模型信息 (如 LightGBM, LSTM).
    *   **版本控制**: 选择模型的具体版本 (v1.0, v1.1).
    *   **性能指标**: 该模型在验证集上的 AUC, IC 等指标.
*   **API**: `GET /api/v1/strategy/models`

## 3. 交互设计
*   **实时验证**: 编辑配置时，后台异步检查参数合法性。
*   **一键回测**: 编辑器顶部有 "Run Backtest" 按钮，直接携带当前配置跳转至 [回测竞技场]。

## 4. API 映射汇总
| 组件区域 | 核心 API 端点 | 请求方式 | 备注 |
| :--- | :--- | :--- | :--- |
| 策略列表 | `/api/v1/strategy/strategies` | GET | |
| 策略定义 | `/api/v1/strategy/definitions` | GET | 获取元数据 |
| 模型列表 | `/api/v1/strategy/models` | GET | |
