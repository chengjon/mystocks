# MyStocks NiceGUI迁移指南

## 📋 概述

本文档详细说明如何从MyStocks标准架构迁移到NiceGUI前端架构，为mystocks_nice分支提供完整的迁移指导和最佳实践。

**适用分支**: mystocks_nice (基于NiceGUI的前端方案)  
**基于架构**: mystocks_spec (主分支)  
**文档目标**: 帮助mystocks_nice团队快速理解NiceGUI实现方案  
**更新状态**: 完整迁移指南

---

## 🏗️ 架构差异分析

### 当前架构 vs NiceGUI架构

| 组件类型 | 当前架构 (mystocks_spec) | NiceGUI架构 (mystocks_nice) | 差异说明 |
|---------|--------------------------|----------------------------|----------|
| **前端框架** | Vue.js + Element Plus | NiceGUI + Quasar | 切换到Python直接生成前端 |
| **状态管理** | Vuex/Pinia | 全局Python变量 | 简化状态管理，使用Python直接控制 |
| **API通信** | HTTP/REST + WebSocket | 直接方法调用 | 无需HTTP通信，直接Python调用 |
| **路由管理** | Vue Router | 无路由(单页应用) | NiceGUI自动处理路由 |
| **组件开发** | .vue + 模板语法 | Python类 + decorators | 直接用Python编写UI |
| **样式管理** | SASS/SCSS + CSS | CSS + Tailwind | 支持CSS框架集成 |
| **实时更新** | WebSocket连接 | 实时刷新 + 观察者模式 | 简化实时数据更新机制 |
| **打包构建** | Vite/Webpack | 自动构建 | NiceGUI自动处理构建 |

### 技术栈对比

#### 当前架构技术栈
```yaml
frontend:
  framework: "Vue.js 3.x"
  ui_library: "Element Plus"
  state_management: "Pinia"
  router: "Vue Router"
  bundler: "Vite"
  language: "TypeScript"
  styling: "SCSS + Tailwind"
  websocket: "socket.io-client"

backend:
  framework: "FastAPI"
  api_design: "RESTful"
  real_time: "WebSocket"
  data_format: "JSON"
```

#### NiceGUI架构技术栈
```yaml
frontend:
  framework: "NiceGUI"
  ui_library: "Quasar Components"
  state_management: "Python Global Variables"
  router: "Automatic Routing"
  bundler: "Automatic Build"
  language: "Python"
  styling: "Tailwind CSS"
  real_time: "Uvicorn + Auto Refresh"

backend:
  framework: "FastAPI + NiceGUI"
  api_design: "Direct Method Calls"
  real_time: "Auto Refresh + Observers"
  data_format: "Python Objects"
  state_sync: "Reactive Variables"
```

---

## 🚀 迁移策略

### 渐进式迁移策略

#### 阶段1: 基础架构迁移 (Week 1-2)
**目标**: 建立NiceGUI基础项目结构
- [ ] 设置NiceGUI项目环境
- [ ] 配置FastAPI集成
- [ ] 实现基础页面布局
- [ ] 迁移核心CSS样式

#### 阶段2: 核心组件迁移 (Week 3-4)
**目标**: 迁移主要功能组件
- [ ] 迁移AI策略管理界面
- [ ] 迁移监控系统面板
- [ ] 迁移GPU状态展示
- [ ] 迁移数据可视化组件

#### 阶段3: 高级功能迁移 (Week 5-6)
**目标**: 实现高级功能和优化
- [ ] 迁移实时数据更新
- [ ] 迁移高级图表组件
- [ ] 迁移用户交互功能
- [ ] 性能优化和测试

### 组件映射表

| Vue.js组件 | NiceGUI等效实现 | 迁移复杂度 | 关键差异 |
|------------|----------------|------------|----------|
| `<template>` | `@ui.page()` 装饰器 | 低 | 使用Python装饰器定义页面 |
| `<script setup>` | 类方法实现 | 中 | 逻辑移到Python类方法 |
| `ref()` | `ui.query()` + reactive | 中 | 使用NiceGUI的查询和反应式 |
| `computed` | Lambda + 缓存 | 中 | Python lambda函数 |
| `watch()` | 观察者模式 | 中 | `ui.watch()` 方法 |
| `<el-button>` | `ui.button()` | 低 | 直接使用NiceGUI按钮 |
| `<el-table>` | `ui.table()` | 中 | NiceGUI表格组件 |
| `<el-dialog>` | `ui.dialog()` | 低 | NiceGUI对话框 |
| `<el-form>` | `ui.form()` | 中 | 表单处理方式不同 |
| Router路由 | 自动路由 | 低 | NiceGUI自动处理 |

### API接口适配策略

#### 当前API设计模式
```python
# FastAPI 传统方式
@app.get("/api/strategies")
async def get_strategies():
    return {"strategies": strategy_list}

@app.websocket("/ws/realtime")
async def websocket_endpoint(websocket):
    await websocket.accept()
    while True:
        data = await get_realtime_data()
        await websocket.send_json(data)
```

#### NiceGUI适配方式
```python
# NiceGUI 集成方式
from nicegui import ui, app

# 直接页面方法 - 无需HTTP调用
@ui.page('/strategies')
async def strategies_page():
    strategies = await get_strategies()
    ui.table(strategies)
    
# 实时更新 - 使用观察者
@ui.page('/monitoring')
async def monitoring_page():
    data = ui.query('#real-time-data')
    
    async def update_data():
        new_data = await get_realtime_data()
        data.set_text(str(new_data))
    
    ui.timer(interval=1.0, callback=update_data)
```

---

## 📝 迁移实施步骤

### 环境搭建 (阶段1)

#### 1. 创建NiceGUI项目结构
```python
# mystocks_nice/main.py
from nicegui import ui, app
from fastapi import FastAPI
import uvicorn

# 创建NiceGUI应用
app = FastAPI()
ui = ui.with_app(app)

# 基础配置
app.title = "MyStocks AI - NiceGUI"
app.version = "1.0.0"

# 全局状态管理
class GlobalState:
    def __init__(self):
        self.current_user = None
        self.strategies = []
        self.monitoring_data = {}
        self.gpu_status = {}

global_state = GlobalState()
```

#### 2. 设置基础页面结构
```python
# mystocks_nice/layouts/main_layout.py
from nicegui import ui
from typing import Callable

class MainLayout:
    def __init__(self, title: str = "MyStocks AI"):
        self.title = title
        self.setup_layout()
    
    def setup_layout(self):
        """设置主布局"""
        # 设置页面标题
        ui.add_head_html('''
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>MyStocks AI</title>
            <script src="https://unpkg.com/axios/dist/axios.min.js"></script>
            <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
        ''')
        
        # 主导航栏
        with ui.header().classes('bg-blue-900 text-white'):
            ui.label('MyStocks AI').classes('text-xl font-bold')
            with ui.row().classes('ml-auto space-x-4'):
                ui.link('主页', '/').classes('hover:underline')
                ui.link('AI策略', '/strategies').classes('hover:underline')
                ui.link('监控', '/monitoring').classes('hover:underline')
                ui.link('GPU状态', '/gpu').classes('hover:underline')
                ui.link('系统', '/system').classes('hover:underline')
        
        # 主内容区域
        self.content_area = ui.element().classes('container mx-auto px-4 py-8')

# 使用示例
layout = MainLayout()
```

#### 3. 迁移核心样式
```css
/* mystocks_nice/static/css/custom.css */

/* 主色调和主题 */
:root {
    --primary-color: #1e3a8a; /* 蓝色主题 */
    --secondary-color: #3b82f6;
    --success-color: #10b981;
    --warning-color: #f59e0b;
    --error-color: #ef4444;
    --background-color: #f8fafc;
}

/* AI策略卡片样式 */
.strategy-card {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    padding: 16px;
    margin: 8px 0;
    border-left: 4px solid var(--primary-color);
}

/* 监控面板样式 */
.monitor-panel {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 12px;
    padding: 20px;
}

/* GPU状态指示器 */
.gpu-status-indicator {
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-right: 8px;
}

.gpu-status-indicator.active {
    background-color: var(--success-color);
    animation: pulse 2s infinite;
}

.gpu-status-indicator.inactive {
    background-color: var(--error-color);
}

/* 表格样式优化 */
.data-table {
    background: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.data-table th {
    background-color: var(--primary-color);
    color: white;
    padding: 12px;
    text-align: left;
}

.data-table td {
    padding: 12px;
    border-bottom: 1px solid #e2e8f0;
}

.data-table tr:hover {
    background-color: #f7fafc;
}

/* 动画效果 */
@keyframes pulse {
    0% {
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
    }
    70% {
        box-shadow: 0 0 0 10px rgba(16, 185, 129, 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
    }
}

.fade-in {
    animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
```

### 核心组件迁移 (阶段2)

#### 1. 迁移AI策略管理界面
```python
# mystocks_nice/pages/strategies.py
from nicegui import ui, app
from typing import List, Dict
import asyncio
from datetime import datetime

@ui.page('/strategies')
async def strategies_page():
    """AI策略管理页面"""
    from layouts.main_layout import MainLayout
    
    # 使用主布局
    layout = MainLayout("AI策略管理")
    
    with layout.content_area:
        # 页面标题
        ui.label('AI策略管理').classes('text-3xl font-bold text-gray-800 mb-8')
        
        # 策略统计卡片
        with ui.row().classes('mb-8 space-x-4'):
            await create_stat_card("活跃策略", "12", "text-green-600")
            await create_stat_card("总收益", "+23.45%", "text-blue-600")
            await create_stat_card("胜率", "67.8%", "text-purple-600")
            await create_stat_card("夏普比率", "1.42", "text-orange-600")
        
        # 策略列表区域
        with ui.card().classes('w-full mb-6'):
            ui.label('策略列表').classes('text-xl font-semibold mb-4')
            
            # 工具栏
            with ui.row().classes('mb-4 space-x-2'):
                ui.button('新建策略', icon='add').classes('bg-blue-500 text-white')
                ui.button('批量操作', icon='settings').classes('bg-gray-500 text-white')
                ui.button('导出数据', icon='download').classes('bg-green-500 text-white')
            
            # 策略表格
            await create_strategies_table()
        
        # 策略性能图表区域
        with ui.row().classes('space-x-6'):
            # 收益曲线图
            with ui.card().classes('flex-1'):
                ui.label('收益曲线').classes('text-lg font-semibold mb-4')
                ui.html('''
                    <div id="profit-chart" style="height: 300px; background: #f8fafc; border-radius: 8px; display: flex; align-items: center; justify-content: center;">
                        <p>收益曲线图表</p>
                    </div>
                ''').classes('fade-in')
            
            # 风险分布图
            with ui.card().classes('flex-1'):
                ui.label('风险分布').classes('text-lg font-semibold mb-4')
                ui.html('''
                    <div id="risk-chart" style="height: 300px; background: #f8fafc; border-radius: 8px; display: flex; align-items: center; justify-content: center;">
                        <p>风险分布图表</p>
                    </div>
                ''').classes('fade-in')

async def create_stat_card(title: str, value: str, color_class: str):
    """创建统计卡片"""
    with ui.card().classes('bg-white p-6 rounded-lg shadow-md flex-1'):
        ui.label(title).classes('text-sm text-gray-600 mb-2')
        ui.label(value).classes(f'text-2xl font-bold {color_class}')

async def create_strategies_table():
    """创建策略表格"""
    # 模拟策略数据
    strategies_data = [
        {
            "name": "动量突破策略",
            "type": "技术分析",
            "status": "运行中",
            "return": "+15.2%",
            "sharpe": "1.23",
            "max_drawdown": "-8.5%",
            "last_updated": "2025-11-16 14:30"
        },
        {
            "name": "均值回归策略",
            "type": "统计套利",
            "status": "暂停",
            "return": "+8.7%",
            "sharpe": "0.89",
            "max_drawdown": "-12.3%",
            "last_updated": "2025-11-16 13:15"
        },
        {
            "name": "机器学习策略",
            "type": "ML基础",
            "status": "运行中",
            "return": "+23.4%",
            "sharpe": "1.67",
            "max_drawdown": "-6.1%",
            "last_updated": "2025-11-16 14:45"
        }
    ]
    
    # 创建表格头部
    table_header = """
    <tr class="bg-blue-900 text-white">
        <th class="px-4 py-3 text-left">策略名称</th>
        <th class="px-4 py-3 text-left">类型</th>
        <th class="px-4 py-3 text-left">状态</th>
        <th class="px-4 py-3 text-left">收益率</th>
        <th class="px-4 py-3 text-left">夏普比率</th>
        <th class="px-4 py-3 text-left">最大回撤</th>
        <th class="px-4 py-3 text-left">更新时间</th>
        <th class="px-4 py-3 text-left">操作</th>
    </tr>
    """
    
    # 创建表格行
    table_rows = ""
    for strategy in strategies_data:
        status_color = "green" if strategy["status"] == "运行中" else "red"
        return_color = "text-green-600" if strategy["return"].startswith("+") else "text-red-600"
        
        table_rows += f"""
        <tr class="hover:bg-gray-50 transition-colors">
            <td class="px-4 py-3 font-medium">{strategy['name']}</td>
            <td class="px-4 py-3">{strategy['type']}</td>
            <td class="px-4 py-3">
                <span class="px-2 py-1 rounded-full text-xs text-white bg-{status_color}-500">
                    {strategy['status']}
                </span>
            </td>
            <td class="px-4 py-3 font-semibold {return_color}">{strategy['return']}</td>
            <td class="px-4 py-3">{strategy['sharpe']}</td>
            <td class="px-4 py-3 text-red-600">{strategy['max_drawdown']}</td>
            <td class="px-4 py-3 text-gray-600">{strategy['last_updated']}</td>
            <td class="px-4 py-3">
                <button class="text-blue-600 hover:text-blue-800 mr-2">编辑</button>
                <button class="text-green-600 hover:text-green-800 mr-2">启用</button>
                <button class="text-red-600 hover:text-red-800">删除</button>
            </td>
        </tr>
        """
    
    # 生成完整表格HTML
    table_html = f"""
    <div class="overflow-x-auto">
        <table class="w-full bg-white rounded-lg overflow-hidden shadow-lg">
            <thead>{table_header}</thead>
            <tbody>{table_rows}</tbody>
        </table>
    </div>
    """
    
    ui.html(table_html).classes('fade-in')
```

#### 2. 迁移监控系统面板
```python
# mystocks_nice/pages/monitoring.py
from nicegui import ui, app
import asyncio
from datetime import datetime
import json

@ui.page('/monitoring')
async def monitoring_page():
    """监控系统页面"""
    from layouts.main_layout import MainLayout
    
    layout = MainLayout("系统监控")
    
    with layout.content_area:
        ui.label('系统监控').classes('text-3xl font-bold text-gray-800 mb-8')
        
        # 系统概览区域
        with ui.row().classes('mb-8 space-x-4'):
            await create_monitor_card("AI策略状态", "12/15 运行中", "success")
            await create_monitor_card("GPU利用率", "78.5%", "warning")
            await create_monitor_card("系统负载", "2.3/4 核心", "info")
            await create_monitor_card("内存使用", "67.2%", "warning")
        
        # 实时监控面板
        with ui.card().classes('w-full mb-6'):
            ui.label('实时监控').classes('text-xl font-semibold mb-4')
            
            # 实时数据展示
            real_time_container = ui.element().classes('grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6')
            
            # 启动实时数据更新
            ui.timer(interval=2.0, callback=lambda: update_real_time_data(real_time_container))
        
        # 告警面板
        with ui.card().classes('w-full mb-6'):
            ui.label('系统告警').classes('text-xl font-semibold mb-4')
            
            # 告警列表
            await create_alert_list()
        
        # 性能图表
        with ui.row().classes('space-x-6'):
            # CPU使用率图表
            with ui.card().classes('flex-1'):
                ui.label('CPU使用率').classes('text-lg font-semibold mb-4')
                await create_performance_chart('cpu', 'CPU使用率 (%)')
            
            # 内存使用图表
            with ui.card().classes('flex-1'):
                ui.label('内存使用率').classes('text-lg font-semibold mb-4')
                await create_performance_chart('memory', '内存使用率 (%)')

async def create_monitor_card(title: str, value: str, status: str):
    """创建监控状态卡片"""
    status_colors = {
        "success": "bg-green-500",
        "warning": "bg-yellow-500", 
        "error": "bg-red-500",
        "info": "bg-blue-500"
    }
    
    with ui.card().classes(f'bg-white p-6 rounded-lg shadow-md flex-1'):
        # 状态指示器
        ui.html(f'<div class="w-4 h-4 rounded-full {status_colors[status]} mb-3"></div>')
        ui.label(title).classes('text-sm text-gray-600 mb-2')
        ui.label(value).classes('text-xl font-bold text-gray-800')

async def create_alert_list():
    """创建告警列表"""
    alerts_data = [
        {
            "level": "warning",
            "message": "GPU温度过高 (82°C)",
            "time": "2分钟前",
            "source": "GPU监控"
        },
        {
            "level": "info", 
            "message": "新策略已成功部署",
            "time": "5分钟前",
            "source": "AI策略引擎"
        },
        {
            "level": "success",
            "message": "系统备份完成",
            "time": "1小时前",
            "source": "系统管理"
        }
    ]
    
    alerts_html = ""
    for alert in alerts_data:
        level_colors = {
            "warning": "border-l-yellow-400 bg-yellow-50",
            "info": "border-l-blue-400 bg-blue-50", 
            "success": "border-l-green-400 bg-green-50",
            "error": "border-l-red-400 bg-red-50"
        }
        
        icon_emoji = {
            "warning": "⚠️",
            "info": "ℹ️",
            "success": "✅", 
            "error": "❌"
        }
        
        alerts_html += f"""
        <div class="border-l-4 {level_colors[alert['level']]} p-4 mb-3 rounded-r-lg">
            <div class="flex justify-between items-start">
                <div class="flex items-center">
                    <span class="mr-2">{icon_emoji[alert['level']]}</span>
                    <div>
                        <p class="font-medium text-gray-800">{alert['message']}</p>
                        <p class="text-sm text-gray-600">{alert['source']}</p>
                    </div>
                </div>
                <span class="text-xs text-gray-500">{alert['time']}</span>
            </div>
        </div>
        """
    
    ui.html(alerts_html).classes('fade-in')

async def update_real_time_data(container):
    """更新实时数据"""
    # 这里可以连接实际的监控系统API
    current_time = datetime.now().strftime("%H:%M:%S")
    
    data_html = f"""
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div class="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-4 rounded-lg">
            <h3 class="text-sm font-medium opacity-90">实时收益</h3>
            <p class="text-2xl font-bold">+{current_time.split(':')[2]}%</p>
            <p class="text-xs opacity-75">更新时间: {current_time}</p>
        </div>
        <div class="bg-gradient-to-r from-green-500 to-green-600 text-white p-4 rounded-lg">
            <h3 class="text-sm font-medium opacity-90">策略胜率</h3>
            <p class="text-2xl font-bold">67.8%</p>
            <p class="text-xs opacity-75">+2.3% 较昨日</p>
        </div>
        <div class="bg-gradient-to-r from-purple-500 to-purple-600 text-white p-4 rounded-lg">
            <h3 class="text-sm font-medium opacity-90">活跃连接</h3>
            <p class="text-2xl font-bold">1,247</p>
            <p class="text-xs opacity-75">+12 较昨日</p>
        </div>
    </div>
    """
    
    container.clear()
    with container:
        ui.html(data_html)

async def create_performance_chart(chart_type: str, title: str):
    """创建性能图表"""
    # 生成模拟图表数据
    chart_data = []
    for i in range(24):
        import random
        value = random.randint(20, 80)
        chart_data.append(value)
    
    chart_html = f"""
    <div id="{chart_type}-chart" style="height: 250px; background: #f8fafc; border-radius: 8px; padding: 16px;">
        <div class="flex items-end justify-between h-full">
            {''.join([f'<div class="bg-blue-500 rounded-t" style="height: {value}%; width: 3.5%; margin: 0 1px;"></div>' for value in chart_data])}
        </div>
        <div class="flex justify-between text-xs text-gray-500 mt-2">
            <span>00:00</span>
            <span>12:00</span>
            <span>23:59</span>
        </div>
    </div>
    """
    
    ui.html(chart_html).classes('fade-in')
```

#### 3. 迁移GPU状态展示
```python
# mystocks_nice/pages/gpu.py
from nicegui import ui, app
import asyncio
import json

@ui.page('/gpu')
async def gpu_page():
    """GPU状态页面"""
    from layouts.main_layout import MainLayout
    
    layout = MainLayout("GPU状态")
    
    with layout.content_area:
        ui.label('GPU状态监控').classes('text-3xl font-bold text-gray-800 mb-8')
        
        # GPU概览
        with ui.row().classes('mb-8 space-x-4'):
            await create_gpu_overview_card()
            await create_gpu_performance_card()
            await create_gpu_memory_card()
            await create_gpu_temperature_card()
        
        # 详细状态
        with ui.card().classes('w-full mb-6'):
            ui.label('GPU详细信息').classes('text-xl font-semibold mb-4')
            await create_gpu_details_table()
        
        # GPU监控图表
        with ui.row().classes('space-x-6'):
            # GPU使用率趋势
            with ui.card().classes('flex-1'):
                ui.label('GPU使用率趋势').classes('text-lg font-semibold mb-4')
                await create_gpu_utilization_chart()
            
            # 内存使用趋势
            with ui.card().classes('flex-1'):
                ui.label('内存使用趋势').classes('text-lg font-semibold mb-4')
                await create_gpu_memory_chart()
        
        # 实时监控
        with ui.card().classes('w-full'):
            ui.label('实时监控').classes('text-xl font-semibold mb-4')
            
            # 实时GPU数据展示
            gpu_realtime_container = ui.element()
            ui.timer(interval=1.0, callback=lambda: update_gpu_realtime_data(gpu_realtime_container))

async def create_gpu_overview_card():
    """创建GPU概览卡片"""
    with ui.card().classes('bg-white p-6 rounded-lg shadow-md flex-1'):
        ui.html('<div class="w-4 h-4 bg-green-500 rounded-full mb-3 animate-pulse"></div>')
        ui.label('GPU状态').classes('text-sm text-gray-600 mb-2')
        ui.label('正常').classes('text-xl font-bold text-green-600')
        ui.label('NVIDIA RTX 2080').classes('text-xs text-gray-500 mt-2')

async def create_gpu_performance_card():
    """创建GPU性能卡片"""
    with ui.card().classes('bg-white p-6 rounded-lg shadow-md flex-1'):
        ui.label('使用率').classes('text-sm text-gray-600 mb-2')
        ui.label('78.5%').classes('text-xl font-bold text-blue-600')
        ui.label('CUDA核心活跃').classes('text-xs text-gray-500 mt-2')

async def create_gpu_memory_card():
    """创建GPU内存卡片"""
    with ui.card().classes('bg-white p-6 rounded-lg shadow-md flex-1'):
        ui.label('显存使用').classes('text-sm text-gray-600 mb-2')
        ui.label('6.2GB / 8GB').classes('text-xl font-bold text-purple-600')
        
        # 显存使用进度条
        usage_percentage = (6.2 / 8.0) * 100
        ui.html(f'''
            <div class="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div class="bg-purple-600 h-2 rounded-full" style="width: {usage_percentage}%;"></div>
            </div>
        ''')

async def create_gpu_temperature_card():
    """创建GPU温度卡片"""
    with ui.card().classes('bg-white p-6 rounded-lg shadow-md flex-1'):
        ui.label('GPU温度').classes('text-sm text-gray-600 mb-2')
        ui.label('73°C').classes('text-xl font-bold text-orange-600')
        ui.label('正常范围').classes('text-xs text-gray-500 mt-2')

async def create_gpu_details_table():
    """创建GPU详细信息表格"""
    gpu_details = [
        {"属性": "GPU型号", "值": "NVIDIA GeForce RTX 2080"},
        {"属性": "CUDA版本", "值": "11.8"},
        {"属性": "驱动版本", "值": "472.12"},
        {"属性": "计算能力", "值": "7.5"},
        {"属性": "流处理器", "值": "2944"},
        {"属性": "核心频率", "值": "1515 MHz"},
        {"属性": "显存类型", "值": "GDDR6"},
        {"属性": "显存频率", "值": "1750 MHz"}
    ]
    
    table_html = """
    <div class="overflow-x-auto">
        <table class="w-full bg-white rounded-lg overflow-hidden shadow-lg">
            <thead class="bg-blue-900 text-white">
                <tr>
                    <th class="px-4 py-3 text-left">属性</th>
                    <th class="px-4 py-3 text-left">值</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for detail in gpu_details:
        table_html += f"""
                <tr class="hover:bg-gray-50">
                    <td class="px-4 py-3 font-medium text-gray-800">{detail['属性']}</td>
                    <td class="px-4 py-3 text-gray-600">{detail['值']}</td>
                </tr>
        """
    
    table_html += """
            </tbody>
        </table>
    </div>
    """
    
    ui.html(table_html).classes('fade-in')

async def create_gpu_utilization_chart():
    """创建GPU使用率图表"""
    # 模拟24小时GPU使用率数据
    import random
    gpu_usage_data = [random.randint(40, 90) for _ in range(24)]
    
    chart_html = f"""
    <div style="height: 250px; background: #f8fafc; border-radius: 8px; padding: 16px;">
        <canvas id="gpu-utilization-chart" width="400" height="200"></canvas>
        <script>
            const ctx = document.getElementById('gpu-utilization-chart').getContext('2d');
            const data = {json.dumps(gpu_usage_data)};
            
            // 简化的图表绘制
            ctx.clearRect(0, 0, 400, 200);
            ctx.strokeStyle = '#3b82f6';
            ctx.lineWidth = 2;
            ctx.beginPath();
            
            for (let i = 0; i < data.length; i++) {{
                const x = (i / (data.length - 1)) * 380 + 10;
                const y = 190 - (data[i] / 100) * 160;
                
                if (i === 0) {{
                    ctx.moveTo(x, y);
                }} else {{
                    ctx.lineTo(x, y);
                }}
            }}
            
            ctx.stroke();
        </script>
    </div>
    """
    
    ui.html(chart_html)

async def create_gpu_memory_chart():
    """创建GPU内存图表"""
    import random
    memory_data = [random.randint(60, 85) for _ in range(24)]
    
    chart_html = f"""
    <div style="height: 250px; background: #f8fafc; border-radius: 8px; padding: 16px;">
        <canvas id="gpu-memory-chart" width="400" height="200"></canvas>
        <script>
            const ctx = document.getElementById('gpu-memory-chart').getContext('2d');
            const data = {json.dumps(memory_data)};
            
            // 简化的图表绘制
            ctx.clearRect(0, 0, 400, 200);
            ctx.strokeStyle = '#8b5cf6';
            ctx.lineWidth = 2;
            ctx.beginPath();
            
            for (let i = 0; i < data.length; i++) {{
                const x = (i / (data.length - 1)) * 380 + 10;
                const y = 190 - (data[i] / 100) * 160;
                
                if (i === 0) {{
                    ctx.moveTo(x, y);
                }} else {{
                    ctx.lineTo(x, y);
                }}
            }}
            
            ctx.stroke();
        </script>
    </div>
    """
    
    ui.html(chart_html)

async def update_gpu_realtime_data(container):
    """更新GPU实时数据"""
    import random
    from datetime import datetime
    
    current_time = datetime.now().strftime("%H:%M:%S")
    
    # 模拟实时GPU数据
    gpu_data = {
        "utilization": random.randint(60, 90),
        "memory_used": round(random.uniform(5.0, 7.5), 1),
        "temperature": random.randint(65, 80),
        "power_usage": random.randint(150, 220),
        "fan_speed": random.randint(30, 70)
    }
    
    realtime_html = f"""
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div class="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-4 rounded-lg">
            <h3 class="text-sm font-medium opacity-90">GPU使用率</h3>
            <p class="text-2xl font-bold">{gpu_data['utilization']}%</p>
            <p class="text-xs opacity-75">更新时间: {current_time}</p>
        </div>
        <div class="bg-gradient-to-r from-purple-500 to-purple-600 text-white p-4 rounded-lg">
            <h3 class="text-sm font-medium opacity-90">显存使用</h3>
            <p class="text-2xl font-bold">{gpu_data['memory_used']}GB</p>
            <p class="text-xs opacity-75">总共 8.0GB</p>
        </div>
        <div class="bg-gradient-to-r from-orange-500 to-orange-600 text-white p-4 rounded-lg">
            <h3 class="text-sm font-medium opacity-90">GPU温度</h3>
            <p class="text-2xl font-bold">{gpu_data['temperature']}°C</p>
            <p class="text-xs opacity-75">风扇: {gpu_data['fan_speed']}%</p>
        </div>
    </div>
    """
    
    container.clear()
    with container:
        ui.html(realtime_html)
```

---

## 🔧 高级功能迁移 (阶段3)

### 1. 性能优化实现

#### GPU内存优化管理器
```python
# mystocks_nice/core/performance_optimizer.py
import cupy as cp
import cudf
import rmm
from typing import Optional, Dict, Any
import logging
from nicegui import ui
import asyncio

class PerformanceOptimizer:
    """性能优化管理器"""
    
    def __init__(self):
        self.gpu_id = 0
        self.memory_pool = None
        self.cache = {}
        self.optimization_enabled = True
        
    def initialize_gpu_optimization(self):
        """初始化GPU优化"""
        try:
            # 设置设备
            cp.cuda.runtime.setDevice(self.gpu_id)
            
            # 初始化RMM内存池
            rmm.reinitialize(
                pool_allocator=True,
                managed_memory=True,
                initial_pool_size=1e9,  # 1GB初始池
                max_pool_size=8e9,      # 8GB最大池
                devices=[self.gpu_id]
            )
            
            # 获取CuPy内存池
            self.memory_pool = cp.get_default_memory_pool()
            self.memory_pool.set_limit(fraction=0.8)
            
            # 预编译常用内核
            self._precompile_kernels()
            
            self.optimization_enabled = True
            logging.info("✅ GPU性能优化初始化完成")
            
        except Exception as e:
            logging.error(f"GPU优化初始化失败: {e}")
            self.optimization_enabled = False
    
    def _precompile_kernels(self):
        """预编译GPU内核"""
        # 快速移动平均内核
        @cp.fuse
        def fast_moving_average(data, window):
            cumsum = cp.cumsum(data, dtype=cp.float32)
            return cp.divide(
                cp.subtract(cumsum[window:], cumsum[:-window]),
                window
            )
        
        # 快速RSI计算内核
        @cp.fuse
        def fast_rsi(prices, period=14):
            deltas = cp.diff(prices)
            gains = cp.where(deltas > 0, deltas, 0)
            losses = cp.where(deltas < 0, -deltas, 0)
            
            avg_gains = cp.convolve(gains, cp.ones(period), 'valid') / period
            avg_losses = cp.convolve(losses, cp.ones(period), 'valid') / period
            
            rs = cp.divide(avg_gains, cp.add(avg_losses, 1e-10))
            rsi = cp.subtract(100, cp.divide(100, cp.add(1, rs)))
            
            return rsi
        
        # 存储编译好的内核
        self.compiled_kernels = {
            'moving_average': fast_moving_average,
            'rsi': fast_rsi
        }
    
    def optimize_strategy_calculation(self, strategy_data: Dict[str, Any]) -> Dict[str, Any]:
        """优化策略计算"""
        if not self.optimization_enabled:
            return strategy_data
        
        try:
            # 检查缓存
            cache_key = hash(str(strategy_data))
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            # 使用GPU加速计算
            gpu_df = cudf.from_pandas(strategy_data['data'])
            
            # GPU加速技术指标计算
            if 'close_prices' in gpu_df.columns:
                # 使用预编译的内核
                gpu_df['ma_20'] = self.compiled_kernels['moving_average'](
                    gpu_df['close_prices'], 20
                )
                gpu_df['ma_50'] = self.compiled_kernels['moving_average'](
                    gpu_df['close_prices'], 50
                )
                gpu_df['rsi'] = self.compiled_kernels['rsi'](
                    gpu_df['close_prices']
                )
            
            # 转换为pandas并缓存结果
            optimized_data = gpu_df.to_pandas()
            self.cache[cache_key] = optimized_data
            
            # 清理过期缓存
            self._cleanup_cache()
            
            return optimized_data
            
        except Exception as e:
            logging.error(f"策略计算优化失败: {e}")
            return strategy_data
    
    def _cleanup_cache(self):
        """清理过期缓存"""
        if len(self.cache) > 100:  # 保持缓存大小在100以内
            # 简单的LRU清理策略
            cache_items = list(self.cache.items())
            self.cache = dict(cache_items[-50:])  # 保留最新的50项
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        try:
            metrics = {
                "gpu_memory_used": cp.cuda.MemoryInfo().total - cp.cuda.MemoryInfo().free,
                "gpu_memory_total": cp.cuda.MemoryInfo().total,
                "memory_pool_usage": self.memory_pool.used_bytes() if self.memory_pool else 0,
                "cache_size": len(self.cache),
                "optimization_enabled": self.optimization_enabled
            }
            
            # GPU利用率(模拟)
            metrics["gpu_utilization"] = self._get_gpu_utilization()
            
            return metrics
            
        except Exception as e:
            logging.error(f"获取性能指标失败: {e}")
            return {"error": str(e)}
    
    def _get_gpu_utilization(self) -> float:
        """获取GPU利用率"""
        # 这里应该调用实际的GPU监控API
        # 目前返回模拟数据
        import random
        return random.uniform(60.0, 90.0)

# 全局性能优化器实例
performance_optimizer = PerformanceOptimizer()
```

#### 组件懒加载管理器
```python
# mystocks_nice/core/lazy_loading_manager.py
from nicegui import ui, app
import asyncio
from typing import Dict, Callable, Any
import logging

class LazyLoadingManager:
    """组件懒加载管理器"""
    
    def __init__(self):
        self.loaded_components = set()
        self.component_loaders = {}
        self.loading_states = {}
        
    def register_component(self, name: str, loader: Callable, priority: int = 0):
        """注册组件加载器"""
        self.component_loaders[name] = {
            'loader': loader,
            'priority': priority,
            'loaded': False
        }
        logging.info(f"📝 注册组件加载器: {name} (优先级: {priority})")
    
    async def load_component(self, component_name: str, force_reload: bool = False) -> bool:
        """加载组件"""
        if component_name in self.loaded_components and not force_reload:
            return True
        
        if component_name not in self.component_loaders:
            logging.error(f"❌ 组件加载器未注册: {component_name}")
            return False
        
        try:
            self.loading_states[component_name] = "loading"
            logging.info(f"🔄 开始加载组件: {component_name}")
            
            # 执行加载器
            loader = self.component_loaders[component_name]['loader']
            await loader()
            
            # 标记为已加载
            self.loaded_components.add(component_name)
            self.component_loaders[component_name]['loaded'] = True
            self.loading_states[component_name] = "loaded"
            
            logging.info(f"✅ 组件加载完成: {component_name}")
            return True
            
        except Exception as e:
            self.loading_states[component_name] = "error"
            logging.error(f"❌ 组件加载失败: {component_name} - {e}")
            return False
    
    async def preload_critical_components(self):
        """预加载关键组件"""
        # 按优先级排序
        sorted_components = sorted(
            self.component_loaders.items(),
            key=lambda x: x[1]['priority'],
            reverse=True
        )
        
        critical_components = [name for name, _ in sorted_components[:3]]  # 预加载前3个
        
        logging.info(f"🚀 预加载关键组件: {critical_components}")
        
        for component_name in critical_components:
            await self.load_component(component_name)
    
    async def check_component_status(self, component_name: str) -> str:
        """检查组件状态"""
        return self.loading_states.get(component_name, "unknown")

# 全局懒加载管理器实例
lazy_loading_manager = LazyLoadingManager()
```

### 2. WebSocket实时数据更新

#### 实时数据管理器
```python
# mystocks_nice/core/realtime_data_manager.py
from nicegui import ui, app
import asyncio
import json
from typing import Dict, Any, Callable
import logging
from datetime import datetime, timedelta

class RealtimeDataManager:
    """实时数据管理器"""
    
    def __init__(self):
        self.subscribers = {}
        self.data_sources = {}
        self.update_intervals = {}
        self.last_updates = {}
        
    def register_data_source(self, name: str, source_func: Callable, interval: float = 1.0):
        """注册数据源"""
        self.data_sources[name] = {
            'func': source_func,
            'interval': interval,
            'last_data': None
        }
        self.update_intervals[name] = interval
        logging.info(f"📊 注册数据源: {name} (间隔: {interval}s)")
    
    def subscribe(self, data_source: str, callback: Callable, component_id: str):
        """订阅数据更新"""
        if data_source not in self.subscribers:
            self.subscribers[data_source] = {}
        
        self.subscribers[data_source][component_id] = callback
        logging.info(f"📡 组件 {component_id} 订阅数据源: {data_source}")
    
    async def start_monitoring(self):
        """开始监控所有数据源"""
        for data_source_name in self.data_sources:
            asyncio.create_task(self._monitor_data_source(data_source_name))
    
    async def _monitor_data_source(self, data_source_name: str):
        """监控单个数据源"""
        while True:
