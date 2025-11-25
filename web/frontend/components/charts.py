"""
MyStocks NiceGUI增强版监控面板 - 图表组件模块

作者: MyStocks AI开发团队
版本: 2.0.0 (UI/UX增强版)
日期: 2025-11-25
"""

from nicegui import ui


def create_realtime_charts(dashboard):
    """创建实时图表区域"""
    with ui.card().classes('w-full q-pa-lg dashboard-card'):
        with ui.row().classes('items-center justify-between q-mb-md'):
            ui.label('📈 实时性能图表').classes('text-h6 text-weight-bold')
            with ui.row().classes('items-center q-gutter-sm'):
                ui.icon('fullscreen', size='20px', color='blue')
                ui.button('全屏视图', on_click=dashboard._show_fullscreen_charts, color='blue', size='sm').classes('control-btn')

        # 添加Chart.js库
        dashboard._include_chartjs()

        # 性能监控初始化
        dashboard._initialize_performance_monitoring()

        with ui.row().classes('q-gutter-md'):
            # CPU使用率图表
            dashboard._create_chart_card('cpu', 'CPU使用率', 'processor', '#3f51b5')
            
            # GPU使用率图表  
            dashboard._create_chart_card('gpu', 'GPU使用率', 'memory', '#9c27b0')
            
            # 内存使用率图表
            dashboard._create_chart_card('memory', '内存使用率', 'memory', '#4caf50')
        
        # 综合性能图表
        with ui.card().classes('w-full q-mt-md'):
            ui.label('📊 综合性能趋势').classes('text-subtitle1 text-weight-bold q-mb-md')
            dashboard.combined_chart_canvas = ui.html('<canvas id="combinedChart" width="800" height="200"></canvas>')


# 将相关方法移动到dashboard对象中
def _create_chart_card(dashboard, chart_id, title, icon_name, color):
    """创建单个图表卡片"""
    with ui.card().classes('chart-container flex-grow-1'):
        # 图表标题
        with ui.row().classes('items-center justify-between q-mb-sm'):
            ui.label(title).classes('text-subtitle1 text-weight-medium')
            with ui.row().classes('items-center q-gutter-xs'):
                ui.icon('fullscreen', size='16px', color='grey-6')
                ui.button('全屏', on_click=lambda: dashboard._show_single_chart(chart_id), 
                         color='transparent', size='sm').props('flat round')
        
        # 图表容器
        dashboard.chart_components[chart_id] = ui.html(
            f'''
            <canvas id="{chart_id}" width="400" height="200"></canvas>
            '''
        ).classes('w-full')


# 添加这些方法到dashboard类中
EnhancedNiceGUIMonitoringDashboard._create_chart_card = _create_chart_card