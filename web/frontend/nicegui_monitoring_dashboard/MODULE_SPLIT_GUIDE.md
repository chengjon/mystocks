# 模块化拆分说明

## 源文件
```
/opt/claude/mystocks_spec/web/frontend/nicegui_monitoring_dashboard_kline.py
```

## 拆分方案

该文件已按照《代码文件长度优化规范》拆分为以下模块：

### 主入口文件
- `nicegui_monitoring_dashboard_kline.py`: 主入口文件，包含原有导入和启动函数

### 核心文件
- `core.py`: 核心类和功能实现

### 组件文件
- `components/kline_charts.py`: K线图表相关功能 (16 个函数)
- `components/realtime_charts.py`: 实时图表功能 (10 个函数)
- `components/alert_panel.py`: 告警面板功能 (3 个函数)
- `components/control_panel.py`: 控制面板功能 (8 个函数)
- `components/floating_actions.py`: 浮动操作按钮功能 (1 个函数)
- `components/utility.py`: 通用工具函数 (16 个函数)

### 组件索引
- `components/__init__.py`: 组件索引文件，导入所有组件模块

## 使用说明

拆分后的代码保持向后兼容性，可以通过以下方式使用：

```python
# 直接导入主文件（推荐）
from web.frontend.nicegui_monitoring_dashboard import create_and_run_monitoring_app

# 或者按组件导入（高级用法）
from web.frontend.nicegui_monitoring_dashboard.components.kline_charts import *
from web.frontend.nicegui_monitoring_dashboard.core import EnhancedKlineMonitoringDashboard
```

## 注意事项

- 拆分后的模块应保持功能的独立性和完整性
- 注意避免循环导入，特别是通过__init__.py统一暴露接口
- 为每个模块添加适当的文档说明其功能和用法

## 函数分布详情

### K线图表相关函数
_create_kline_charts, _include_klinechart_libs, _create_kline_controls, _create_kline_chart_containers, _initialize_klinecharts, _create_realtime_charts, _create_chart_card, _load_kline_data, _show_fullscreen_kline, _update_chart_data, _update_kline_realtime_data, _update_chartjs_data, _scroll_to_kline, _show_fullscreen_charts, _show_single_chart, create_kline_dashboard

### 告警相关函数
_create_alert_panel, _clear_all_alerts, _show_alert_settings

### 控制相关函数
_create_theme_toggle, _create_kline_controls, _create_control_panel, _on_symbol_change, _change_timeframe, _toggle_indicators, _toggle_theme, _toggle_auto_refresh

### 操作相关函数
_create_floating_actions

### 通用工具函数
__init__, _initialize_dashboard, _create_header, _create_metrics_cards, _initialize_performance_monitoring, _show_timeframe_options, _show_indicator_settings, _update_ui_display, _update_performance_metrics, _export_dashboard_data, _share_dashboard, _manual_refresh, _add_keyboard_shortcuts, _setup_auto_refresh, _get_adaptive_interval, _show_dashboard_report
