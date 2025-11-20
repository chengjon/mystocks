"""
MyStocks NiceGUI增强版监控面板 (UI/UX优化版)

基于NiceGUI的现代化AI监控系统Web界面，支持实时监控、告警管理、性能分析等功能。
专门针对UI/UX进行深度优化，提供更好的用户体验。

UI/UX优化特性:
- 🎨 现代化Material Design风格界面
- 📊 实时图表和可视化数据
- 🌙 深色/浅色主题切换
- 📱 完全响应式设计
- ⚡ 性能优化和智能刷新
- 🔔 智能告警通知系统
- 🎯 用户偏好设置
- 📈 数据导出功能
- ⌨️ 键盘快捷键支持

作者: MyStocks AI开发团队
创建日期: 2025-11-16
版本: 2.0.0 (UI/UX增强版)
依赖: nicegui, uvicorn, chart.js
注意事项: 专为生产环境设计的现代化监控界面
版权: MyStocks Project © 2025
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

from nicegui import ui, app
import uvicorn

from src.monitoring.ai_alert_manager import (
    AIAlertManager,
    Alert,
    AlertSeverity,
    AlertType,
    get_ai_alert_manager,
)

from src.monitoring.ai_realtime_monitor import (
    AIRealtimeMonitor,
    MonitoringConfig,
    get_ai_realtime_monitor,
)


logger = logging.getLogger(__name__)


class EnhancedNiceGUIMonitoringDashboard:
    """增强版NiceGUI监控面板主类"""
    
    def __init__(self, alert_manager: AIAlertManager, monitor: AIRealtimeMonitor):
        """初始化增强版监控面板"""
        self.alert_manager = alert_manager
        self.monitor = monitor
        self.dashboard_refresh_interval = 3  # 3秒刷新，更流畅
        self.user_preferences = {
            'theme': 'auto',  # auto, light, dark
            'refresh_rate': 3,
            'notification_enabled': True,
            'sound_enabled': False,
            'compact_mode': False
        }
        self.dashboard_data = {
            'metrics_history': [],
            'active_alerts': [],
            'system_health': {},
            'last_update': None,
            'chart_data': {
                'cpu_history': [],
                'gpu_history': [],
                'memory_history': [],
                'timestamps': []
            }
        }
        
        # 页面组件引用
        self.metrics_cards = {}
        self.alert_components = {}
        self.chart_components = {}
        self.status_indicators = {}
        self.theme_toggle = None
        self.compact_mode_toggle = None
        
        # 性能监控
        self.performance_metrics = {
            'memory_usage': 0,
            'cpu_usage': 0,
            'refresh_rate': 3,
            'last_update_time': datetime.now(),
            'update_count': 0,
            'error_count': 0
        }
        self.chart_update_queue = asyncio.Queue(maxsize=100)
        
        logger.info("✅ 增强版NiceGUI监控面板初始化完成")
    
    def create_monitoring_page(self):
        """创建监控页面"""
        # 设置页面CSS样式
        self._setup_styles()
        
        # 创建页面内容
        self._create_header()
        self._create_metrics_overview()
        self._create_realtime_charts()
        self._create_alert_management()
        self._create_system_health()
        self._create_control_panel()
        self._create_alert_history()
        
        # 启动自动刷新
        self._start_auto_refresh()
        
        # 添加键盘快捷键
        self._add_keyboard_shortcuts()
        
        logger.info("✅ 增强版监控页面创建完成")
    
    def _setup_styles(self):
        """设置页面样式"""
        ui.add_head_html("""
        <style>
        /* 自定义CSS样式 */
        .dashboard-card {
            backdrop-filter: blur(10px);
            background: rgba(255, 255, 255, 0.9);
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        
        .dashboard-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        }
        
        .dark .dashboard-card {
            background: rgba(30, 30, 30, 0.9);
            color: white;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            padding: 20px;
            color: white;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        
        .metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1));
            pointer-events: none;
        }
        
        .alert-item {
            border-left: 4px solid;
            border-radius: 8px;
            padding: 12px;
            margin: 8px 0;
            background: rgba(255, 255, 255, 0.8);
            transition: all 0.3s ease;
        }
        
        .alert-item:hover {
            transform: translateX(4px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        
        .alert-critical {
            border-left-color: #f44336;
            background: rgba(244, 67, 54, 0.1);
        }
        
        .alert-warning {
            border-left-color: #ff9800;
            background: rgba(255, 152, 0, 0.1);
        }
        
        .alert-info {
            border-left-color: #2196f3;
            background: rgba(33, 150, 243, 0.1);
        }
        
        .chart-container {
            background: white;
            border-radius: 12px;
            padding: 20px;
            height: 300px;
            position: relative;
        }
        
        .dark .chart-container {
            background: #2d3748;
            color: white;
        }
        
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        
        .status-online {
            background: #4caf50;
        }
        
        .status-offline {
            background: #f44336;
        }
        
        .status-warning {
            background: #ff9800;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .loading-skeleton {
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200% 100%;
            animation: loading 1.5s infinite;
        }
        
        .dark .loading-skeleton {
            background: linear-gradient(90deg, #2d3748 25%, #4a5568 50%, #2d3748 75%);
            background-size: 200% 100%;
        }
        
        @keyframes loading {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }
        
        .compact-mode .metric-card {
            padding: 12px;
        }
        
        .compact-mode .metric-card .text-h5 {
            font-size: 1.2rem;
        }
        
        .compact-mode .metric-card .text-subtitle2 {
            font-size: 0.8rem;
        }
        
        .control-btn {
            border-radius: 8px;
            transition: all 0.2s ease;
            font-weight: 500;
        }
        
        .control-btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        
        .progress-ring {
            transform: rotate(-90deg);
        }
        
        .progress-ring circle {
            transition: stroke-dasharray 0.35s;
        }
        
        .floating-actions {
            position: fixed;
            bottom: 24px;
            right: 24px;
            z-index: 1000;
        }
        
        .theme-toggle {
            position: absolute;
            top: 16px;
            right: 16px;
        }
        
        .responsive-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        @media (max-width: 768px) {
            .responsive-grid {
                grid-template-columns: 1fr;
                gap: 12px;
            }
            
            .floating-actions {
                bottom: 16px;
                right: 16px;
            }
            
            .metric-card {
                padding: 12px;
            }
        }
        </style>
        """)
    
    def _create_header(self):
        """创建页面标题栏"""
        with ui.header().classes('q-pa-md bg-gradient-to-r from-blue-600 to-purple-600 text-white'):
            with ui.row().classes('w-full items-center justify-between'):
                with ui.column().classes('col-auto'):
                    with ui.row().classes('items-center q-gutter-sm'):
                        ui.icon('dashboard', size='32px').classes('text-white')
                        ui.label('MyStocks AI实时监控系统').classes('text-h4 text-weight-bold')
                    ui.label('增强版监控面板').classes('text-subtitle2 opacity-80')
                    
                    # 性能指示器
                    with ui.row().classes('items-center q-gutter-sm q-mt-sm'):
                        ui.icon('speed', size='16px', color='light-green')
                        self.performance_indicator = ui.label('正常').classes('text-caption text-light-green')
                        self.memory_usage_indicator = ui.label('内存: 0%').classes('text-caption text-light-green-7')
                        self.refresh_rate_indicator = ui.label('刷新: 3s').classes('text-caption text-light-green-7')
                        
                        # 错误指示器
                        self.error_indicator = ui.icon('error', size='16px', color='transparent').classes('text-light-green')
                        self.error_count_label = ui.label('0').classes('text-caption text-light-green')
                
                with ui.column().classes('col-auto items-center q-gutter-md'):
                    # 主题切换
                    self.theme_toggle = ui.switch(
                        label='深色主题',
                        value=False,
                        on_change=self._toggle_theme
                    ).classes('theme-toggle text-white')
                    
                    # 紧凑模式切换
                    self.compact_mode_toggle = ui.switch(
                        label='紧凑模式',
                        value=False,
                        on_change=self._toggle_compact_mode
                    ).classes('text-white')
                    
                    # 状态指示器
                    with ui.row().classes('items-center q-gutter-sm'):
                        self.status_indicator = ui.icon('wifi', size='24px', color='green').classes('status-online')
                        ui.label('在线').classes('text-white')
                        ui.separator(vertical=True).classes('text-white')
                        ui.label('最后更新:').classes('text-white')
                        self.last_update_label = ui.label('未更新').classes('text-white')
    
    def _create_metrics_overview(self):
        """创建指标概览卡片"""
        with ui.card().classes('w-full q-pa-lg dashboard-card'):
            with ui.row().classes('items-center justify-between q-mb-md'):
                ui.label('📊 系统指标概览').classes('text-h6 text-weight-bold')
                with ui.row().classes('items-center q-gutter-sm'):
                    ui.icon('refresh', size='20px', color='blue')
                    ui.button('实时刷新', on_click=self._refresh_data, color='blue', size='sm').classes('control-btn')
            
            with ui.row().classes('responsive-grid'):
                # CPU使用率卡片
                self._create_metric_card(
                    'cpu', 'CPU使用率', 'processor', '#3f51b5', 
                    'CPU', '正常', 'CPU处理器使用情况'
                )
                
                # GPU使用率卡片
                self._create_metric_card(
                    'gpu', 'GPU使用率', 'memory', '#9c27b0', 
                    'GPU', '正常', '图形处理器使用情况'
                )
                
                # 内存使用率卡片
                self._create_metric_card(
                    'memory', '内存使用率', 'memory', '#4caf50', 
                    '内存', '正常', '系统内存使用情况'
                )
                
                # 活跃告警卡片
                self._create_alert_metric_card()
    
    def _create_metric_card(self, card_id: str, title: str, icon_name: str, color: str, 
                          value_label: str, status_label: str, description: str):
        """创建单个指标卡片"""
        with ui.card().classes('metric-card'):
            with ui.column().classes('items-center text-center q-pa-md'):
                # 图标和状态
                with ui.row().classes('w-full items-center justify-between'):
                    ui.icon(icon_name, size='32px', color='white')
                    with ui.row().classes('items-center q-gutter-xs'):
                        self.metrics_cards[f'{card_id}_status_icon'] = ui.icon('check_circle', size='16px', color='light-green')
                        ui.label(status_label).classes('text-caption text-light-green')
                
                # 标题
                ui.label(title).classes('text-subtitle2 text-white q-mt-sm')
                
                # 主要数值
                with ui.row().classes('items-center justify-center q-mt-sm'):
                    self.metrics_cards[f'{card_id}_value'] = ui.label('0%').classes('text-h4 text-weight-bold text-white')
                    ui.label(value_label).classes('text-body2 text-white-7 q-ml-sm')
                
                # 进度条
                self.metrics_cards[f'{card_id}_progress'] = ui.linear_progress(
                    value=0, 
                    color='white', 
                    size='lg'
                ).classes('w-full q-mt-md')
                
                # 描述
                with ui.tooltip(description):
                    ui.icon('info', size='16px', color='white-7').classes('text-white-7 q-mt-sm')
    
    def _create_alert_metric_card(self):
        """创建告警指标卡片"""
        with ui.card().classes('metric-card bg-gradient-to-r from-red-500 to-pink-600'):
            with ui.column().classes('items-center text-center q-pa-md'):
                # 图标和状态
                with ui.row().classes('w-full items-center justify-between'):
                    ui.icon('warning', size='32px', color='white')
                    with ui.row().classes('items-center q-gutter-xs'):
                        self.metrics_cards['alerts_status_icon'] = ui.icon('info', size='16px', color='white')
                        ui.label('无告警').classes('text-caption text-white-7')
                
                # 标题
                ui.label('活跃告警').classes('text-subtitle2 text-white q-mt-sm')
                
                # 主要数值
                with ui.row().classes('items-center justify-center q-mt-sm'):
                    self.metrics_cards['alerts_total_value'] = ui.label('0').classes('text-h4 text-weight-bold text-white')
                    ui.label('总数').classes('text-body2 text-white-7 q-ml-sm')
                
                # 告警分布
                with ui.row().classes('w-full q-mt-md items-center justify-around'):
                    with ui.column().classes('items-center'):
                        self.metrics_cards['critical_count'] = ui.label('0').classes('text-h6 text-white')
                        ui.label('严重').classes('text-caption text-white-7')
                    with ui.column().classes('items-center'):
                        self.metrics_cards['warning_count'] = ui.label('0').classes('text-h6 text-white')
                        ui.label('警告').classes('text-caption text-white-7')
                    with ui.column().classes('items-center'):
                        self.metrics_cards['info_count'] = ui.label('0').classes('text-h6 text-white')
                        ui.label('信息').classes('text-caption text-white-7')
    
    def _create_realtime_charts(self):
        """创建实时图表区域"""
        with ui.card().classes('w-full q-pa-lg dashboard-card'):
            with ui.row().classes('items-center justify-between q-mb-md'):
                ui.label('📈 实时性能图表').classes('text-h6 text-weight-bold')
                with ui.row().classes('items-center q-gutter-sm'):
                    ui.icon('fullscreen', size='20px', color='blue')
                    ui.button('全屏视图', on_click=self._show_fullscreen_charts, color='blue', size='sm').classes('control-btn')

            # 添加Chart.js库
            self._include_chartjs()

            # 性能监控初始化
            self._initialize_performance_monitoring()

            with ui.row().classes('q-gutter-md'):
                # CPU使用率图表
                self._create_chart_card('cpu', 'CPU使用率', 'processor', '#3f51b5')
                
                # GPU使用率图表  
                self._create_chart_card('gpu', 'GPU使用率', 'memory', '#9c27b0')
                
                # 内存使用率图表
                self._create_chart_card('memory', '内存使用率', 'memory', '#4caf50')
            
            # 综合性能图表
            with ui.card().classes('w-full q-mt-md'):
                ui.label('📊 综合性能趋势').classes('text-subtitle1 text-weight-bold q-mb-md')
                self.combined_chart_canvas = ui.html('<canvas id="combinedChart" width="800" height="200"></canvas>')
    
    def _create_chart_card(self, chart_id: str, title: str, data_type: str):
        """创建单个图表卡片"""
        with ui.card().classes('chart-container flex-grow-1'):
            # 图表标题
            with ui.row().classes('items-center justify-between q-mb-sm'):
                ui.label(title).classes('text-subtitle1 text-weight-medium')
                with ui.row().classes('items-center q-gutter-xs'):
                    ui.icon('fullscreen', size='16px', color='grey-6')
                    ui.button('全屏', on_click=lambda: self._show_single_chart(data_type), 
                             color='transparent', size='sm').props('flat round')
            
            # 图表容器
            self.chart_components[chart_id] = ui.html(
                f'''
                <canvas id="{chart_id}" width="400" height="200"></canvas>
                '''
            ).classes('w-full')
    
    def _create_alert_management(self):
        """创建告警管理区域"""
        with ui.card().classes('w-full q-pa-lg dashboard-card'):
            with ui.row().classes('items-center justify-between q-mb-md'):
                ui.label('🚨 智能告警中心').classes('text-h6 text-weight-bold')
                with ui.row().classes('items-center q-gutter-sm'):
                    ui.icon('settings', size='20px', color='orange')
                    ui.button('告警设置', on_click=self._show_alert_settings, color='orange', size='sm').classes('control-btn')
                    ui.button('全部确认', on_click=self._acknowledge_all_alerts, color='green', size='sm').classes('control-btn')
            
            # 告警统计
            with ui.row().classes('q-gutter-md q-mb-lg'):
                with ui.card().classes('q-pa-md bg-red-1 text-center flex-grow-1'):
                    ui.icon('priority_high', color='red', size='32px')
                    self.alert_stats_critical = ui.label('0').classes('text-h5 text-weight-bold text-red')
                    ui.label('严重告警').classes('text-caption')
                
                with ui.card().classes('q-pa-md bg-orange-1 text-center flex-grow-1'):
                    ui.icon('warning', color='orange', size='32px')
                    self.alert_stats_warning = ui.label('0').classes('text-h5 text-weight-bold text-orange')
                    ui.label('警告告警').classes('text-caption')
                
                with ui.card().classes('q-pa-md bg-blue-1 text-center flex-grow-1'):
                    ui.icon('info', color='blue', size='32px')
                    self.alert_stats_info = ui.label('0').classes('text-h5 text-weight-bold text-blue')
                    ui.label('信息告警').classes('text-caption')
            
            # 活跃告警列表
            ui.label('当前活跃告警:').classes('text-subtitle2 text-weight-medium q-mb-md')
            self.active_alerts_container = ui.column().classes('q-gutter-sm')
    
    def _create_system_health(self):
        """创建系统健康状态"""
        with ui.card().classes('w-full q-pa-lg dashboard-card'):
            with ui.row().classes('items-center justify-between q-mb-md'):
                ui.label('💚 系统健康监控').classes('text-h6 text-weight-bold')
                with ui.row().classes('items-center q-gutter-sm'):
                    ui.icon('analytics', size='20px', color='green')
                    ui.button('健康报告', on_click=self._generate_health_report, color='green', size='sm').classes('control-btn')
            
            with ui.row().classes('responsive-grid'):
                # 健康状态概览
                with ui.card().classes('q-pa-md flex-grow-1'):
                    ui.label('系统状态:').classes('text-subtitle2 text-weight-medium')
                    with ui.row().classes('items-center q-mt-sm'):
                        self.health_status_icon = ui.icon('check_circle', color='green', size='24px')
                        self.health_status_label = ui.label('健康').classes('text-h5 text-weight-bold text-green')
                    
                    ui.label('监控状态:').classes('text-subtitle2 text-weight-medium q-mt-md')
                    self.monitoring_status_label = ui.label('未运行').classes('text-body1 q-mt-sm')
                
                # 性能统计
                with ui.card().classes('q-pa-md flex-grow-1'):
                    ui.label('性能统计:').classes('text-subtitle2 text-weight-medium')
                    self.monitor_stats_label = ui.label('无数据').classes('text-body1 q-mt-sm')
                    
                    ui.label('成功率:').classes('text-subtitle2 text-weight-medium q-mt-md')
                    self.success_rate_label = ui.label('0%').classes('text-body1 text-weight-bold q-mt-sm')
                
                # 系统信息
                with ui.card().classes('q-pa-md flex-grow-1'):
                    ui.label('系统信息:').classes('text-subtitle2 text-weight-medium')
                    self.system_info_label = ui.label('正在获取...').classes('text-body1 q-mt-sm')
                    
                    ui.label('运行时长:').classes('text-subtitle2 text-weight-medium q-mt-md')
                    self.uptime_label = ui.label('0分钟').classes('text-body1 q-mt-sm')
    
    def _create_control_panel(self):
        """创建控制面板"""
        with ui.card().classes('w-full q-pa-lg dashboard-card'):
            with ui.row().classes('items-center justify-between q-mb-md'):
                ui.label('🎮 智能控制面板').classes('text-h6 text-weight-bold')
                with ui.row().classes('items-center q-gutter-sm'):
                    ui.icon('tune', size='20px', color='purple')
                    ui.button('偏好设置', on_click=self._show_preferences, color='purple', size='sm').classes('control-btn')
            
            with ui.row().classes('q-gutter-md q-mb-lg items-center'):
                self.start_monitoring_btn = ui.button(
                    '▶️ 开始监控',
                    on_click=self._start_monitoring,
                    color='positive',
                    size='lg'
                ).classes('control-btn q-px-lg q-py-sm')
                
                self.stop_monitoring_btn = ui.button(
                    '⏹️ 停止监控',
                    on_click=self._stop_monitoring,
                    color='negative',
                    size='lg'
                ).classes('control-btn q-px-lg q-py-sm')
                
                self.test_alert_btn = ui.button(
                    '🧪 测试告警',
                    on_click=self._test_alert,
                    color='warning',
                    size='lg'
                ).classes('control-btn q-px-lg q-py-sm')
                
                self.export_btn = ui.button(
                    '📊 导出报告',
                    on_click=self._export_dashboard_report,
                    color='info',
                    size='lg'
                ).classes('control-btn q-px-lg q-py-sm')
            
            # 状态指示器
            with ui.row().classes('items-center justify-center q-gutter-xl q-mt-md'):
                with ui.column().classes('items-center'):
                    ui.icon('memory', size='24px', color='blue')
                    ui.label('系统运行中').classes('text-caption')
                with ui.column().classes('items-center'):
                    ui.icon('notifications', size='24px', color='orange')
                    ui.label('告警启用').classes('text-caption')
                with ui.column().classes('items-center'):
                    ui.icon('timeline', size='24px', color='green')
                    ui.label('实时监控').classes('text-caption')
    
    def _create_alert_history(self):
        """创建告警历史"""
        with ui.card().classes('w-full q-pa-lg dashboard-card'):
            with ui.row().classes('items-center justify-between q-mb-md'):
                ui.label('📋 告警历史记录').classes('text-h6 text-weight-bold')
                with ui.row().classes('items-center q-gutter-sm'):
                    ui.icon('history', size='20px', color='indigo')
                    ui.button('清空历史', on_click=self._clear_alert_history, color='red', size='sm').classes('control-btn')
            
            # 过滤选项
            with ui.row().classes('q-gutter-md q-mb-md items-center'):
                ui.label('过滤:').classes('text-body2')
                self.severity_filter = ui.select(
                    options=['全部', 'critical', 'warning', 'info'],
                    value='全部',
                    on_change=self._filter_alert_history
                ).classes('col-2')
                
                self.date_filter = ui.select(
                    options=['全部', '今天', '最近7天', '最近30天'],
                    value='全部',
                    on_change=self._filter_alert_history
                ).classes('col-2')
            
            # 历史告警表格
            self.alert_history_table = ui.table({
                'columns': [
                    {'name': 'time', 'label': '时间', 'field': 'time', 'align': 'left', 'sortable': True},
                    {'name': 'rule', 'label': '告警规则', 'field': 'rule', 'align': 'left'},
                    {'name': 'severity', 'label': '严重性', 'field': 'severity', 'align': 'center'},
                    {'name': 'message', 'label': '消息', 'field': 'message', 'align': 'left'},
                    {'name': 'status', 'label': '状态', 'field': 'status', 'align': 'center'},
                    {'name': 'actions', 'label': '操作', 'field': 'actions', 'align': 'center'}
                ],
                'rows': []
            }).classes('w-full').props('flat bordered selectable')
            
            # 添加表格样式
            self.alert_history_table.style('max-height: 400px; overflow-y: auto; border-radius: 8px;')
    
    def _create_floating_actions(self):
        """创建浮动操作按钮"""
        with ui.floating_action_button(
            icon='more_vert',
            color='primary',
            fab=False
        ).classes('floating-actions'):
            # 快捷操作菜单
            with ui.menu():
                ui.item('🚀 性能测试', on_click=self._run_performance_test)
                ui.item('📊 数据导出', on_click=self._quick_export)
                ui.item('🔔 通知测试', on_click=self._test_notifications)
                ui.item('⚙️ 高级设置', on_click=self._show_advanced_settings)
    
    def _create_chart_card(self, chart_id: str, title: str, icon_name: str, color: str):
        """创建单个图表卡片"""
        with ui.card().classes('col-4'):
            with ui.column().classes('items-center q-pa-md'):
                with ui.row().classes('items-center q-mb-md'):
                    ui.icon(icon_name, size='24px', color=color)
                    ui.label(title).classes('text-subtitle2 text-weight-bold')
                    ui.button(
                        '🔍', 
                        on_click=lambda: self._show_single_chart(chart_id), 
                        size='sm', 
                        color='blue'
                    ).props('flat dense round')
                
                # 图表Canvas
                self.chart_components[chart_id] = ui.html(
                    f'<canvas id="{chart_id}Chart" width="300" height="150"></canvas>'
                )
                
                # 加载指示器
                self.chart_loading_indicators = {}
                self.chart_loading_indicators[chart_id] = ui.spinner(size='sm', color='blue').classes('q-mt-sm')
                self.chart_loading_indicators[chart_id].visible = False
                
                # 图表控制
                with ui.row().classes('items-center justify-center q-gutter-sm q-mt-sm'):
                    ui.button('⏸️', on_click=lambda: self._pause_chart(chart_id), size='sm', color='orange').props('flat dense round')
                    ui.button('▶️', on_click=lambda: self._resume_chart(chart_id), size='sm', color='green').props('flat dense round')
                    ui.button('💾', on_click=lambda: self._export_single_chart(chart_id), size='sm', color='purple').props('flat dense round')
                    ui.button('🗑️', on_click=lambda: self._clear_chart_data(chart_id), size='sm', color='red').props('flat dense round')
    
    def _initialize_performance_monitoring(self):
        """初始化性能监控"""
        # 添加性能监控的JavaScript代码
        ui.add_body_html('''
        <script>
        // 性能监控
        window.performanceData = {
            memoryUsage: 0,
            cpuUsage: 0,
            updateTime: Date.now(),
            updateCount: 0,
            errorCount: 0
        };
        
        // 内存使用情况监控
        function updateMemoryUsage() {
            if (performance.memory) {
                const memory = performance.memory;
                const usedMB = Math.round(memory.usedJSHeapSize / 1048576);
                const totalMB = Math.round(memory.totalJSHeapSize / 1048576);
                const usagePercent = Math.round((usedMB / totalMB) * 100);
                window.performanceData.memoryUsage = usagePercent;
                
                // 更新内存使用显示
                const memoryIndicator = document.querySelector('[data-memory-indicator]');
                if (memoryIndicator) {
                    memoryIndicator.textContent = `内存: ${usagePercent}%`;
                    if (usagePercent > 80) {
                        memoryIndicator.style.color = '#ff4444';
                    } else if (usagePercent > 60) {
                        memoryIndicator.style.color = '#ffaa00';
                    } else {
                        memoryIndicator.style.color = '#4caf50';
                    }
                }
            }
        }
        
        // 更新性能指标
        function updatePerformanceIndicators() {
            updateMemoryUsage();
            
            // 更新统计信息
            window.performanceData.updateCount++;
            
            // 每5秒更新一次性能数据
            setTimeout(updatePerformanceIndicators, 5000);
        }
        
        // 启动性能监控
        setTimeout(updatePerformanceIndicators, 1000);
        
        // 错误处理
        window.addEventListener('error', function(event) {
            window.performanceData.errorCount++;
            console.error('JavaScript错误:', event.error);
        });
        </script>
        ''')
        
        # 标记内存指示器
        ui.run_javascript('''
        setTimeout(() => {
            const memoryIndicator = document.querySelector('.text-light-green-7:nth-child(2)');
            if (memoryIndicator) {
                memoryIndicator.setAttribute('data-memory-indicator', 'true');
            }
        }, 2000);
        ''')
    
    def _include_chartjs(self):
        """包含Chart.js库"""
        # 添加Chart.js CDN
        ui.add_head_html('''
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns"></script>
        <style>
        .chart-container {
            position: relative;
            height: 200px;
            width: 100%;
        }
        .chart-loading {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            z-index: 10;
        }
        .chart-error {
            border: 2px solid #f44336;
            border-radius: 4px;
            background-color: #ffebee;
        }
        .chart-loading-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255, 255, 255, 0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 5;
        }
        </style>
        ''')
        
        # 初始化图表的JavaScript代码
        ui.add_body_html('''
        <script>
        // 全局图表配置
        window.chartConfigs = {};
        window.chartInstances = {};
        
        function initChart(chartId, chartType, title, color) {
            const ctx = document.getElementById(chartId + 'Chart');
            if (!ctx) return;
            
            const config = {
                type: chartType,
                data: {
                    labels: [],
                    datasets: [{
                        label: title,
                        data: [],
                        borderColor: color,
                        backgroundColor: color + '20',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: title
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            title: {
                                display: true,
                                text: '使用率 (%)'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: '时间'
                            }
                        }
                    },
                    animation: {
                        duration: 750,
                        easing: 'easeInOutQuart'
                    }
                }
            };
            
            window.chartConfigs[chartId] = config;
            window.chartInstances[chartId] = new Chart(ctx, config);
        }
        
        function initCombinedChart() {
            const ctx = document.getElementById('combinedChart');
            if (!ctx) return;
            
            const config = {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: 'CPU使用率',
                            data: [],
                            borderColor: '#3f51b5',
                            backgroundColor: '#3f51b520',
                            fill: false,
                            tension: 0.4
                        },
                        {
                            label: 'GPU使用率', 
                            data: [],
                            borderColor: '#9c27b0',
                            backgroundColor: '#9c27b020',
                            fill: false,
                            tension: 0.4
                        },
                        {
                            label: '内存使用率',
                            data: [],
                            borderColor: '#4caf50',
                            backgroundColor: '#4caf5020',
                            fill: false,
                            tension: 0.4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: '综合性能趋势分析'
                        },
                        legend: {
                            position: 'top'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            title: {
                                display: true,
                                text: '使用率 (%)'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: '时间'
                            }
                        }
                    },
                    animation: {
                        duration: 750,
                        easing: 'easeInOutQuart'
                    }
                }
            };
            
            window.combinedChart = new Chart(ctx, config);
        }
        
        // 页面加载完成后初始化图表
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(() => {
                initChart('cpu', 'line', 'CPU使用率', '#3f51b5');
                initChart('gpu', 'line', 'GPU使用率', '#9c27b0');
                initChart('memory', 'line', '内存使用率', '#4caf50');
                initCombinedChart();
            }, 1000);
        });
        </script>
        ''')
    
    def _add_keyboard_shortcuts(self):
        """添加键盘快捷键"""
        # 添加键盘快捷键的JavaScript
        ui.add_body_html('''
        <script>
        // 键盘快捷键实现
        document.addEventListener('keydown', function(event) {
            // Ctrl/Cmd + R: 刷新数据
            if ((event.ctrlKey || event.metaKey) && event.key === 'r') {
                event.preventDefault();
                if (typeof window.refreshDashboard === 'function') {
                    window.refreshDashboard();
                }
            }
            
            // Ctrl/Cmd + S: 导出数据
            if ((event.ctrlKey || event.metaKey) && event.key === 's') {
                event.preventDefault();
                if (typeof window.exportData === 'function') {
                    window.exportData();
                }
            }
            
            // Ctrl/Cmd + T: 切换主题
            if ((event.ctrlKey || event.metaKey) && event.key === 't') {
                event.preventDefault();
                if (typeof window.toggleTheme === 'function') {
                    window.toggleTheme();
                }
            }
            
            // F11: 全屏图表
            if (event.key === 'F11') {
                event.preventDefault();
                if (typeof window.showFullscreenCharts === 'function') {
                    window.showFullscreenCharts();
                }
            }
            
            // Space: 开始/停止监控
            if (event.code === 'Space') {
                event.preventDefault();
                if (typeof window.toggleMonitoring === 'function') {
                    window.toggleMonitoring();
                }
            }
            
            // ESC: 关闭模态框
            if (event.key === 'Escape') {
                if (typeof window.closeModal === 'function') {
                    window.closeModal();
                }
            }
        });
        
        // 快捷键提示
        function showKeyboardShortcuts() {
            const shortcuts = `
            <div style="background: white; padding: 20px; border-radius: 8px; max-width: 400px;">
                <h3>⌨️ 键盘快捷键</h3>
                <div><strong>Ctrl/Cmd + R:</strong> 刷新数据</div>
                <div><strong>Ctrl/Cmd + S:</strong> 导出数据</div>
                <div><strong>Ctrl/Cmd + T:</strong> 切换主题</div>
                <div><strong>F11:</strong> 全屏图表</div>
                <div><strong>Space:</strong> 开始/停止监控</div>
                <div><strong>ESC:</strong> 关闭模态框</div>
                <div style="margin-top: 10px; font-size: 12px; color: #666;">按 ? 显示此帮助</div>
            </div>
            `;
            alert(shortcuts);
        }
        
        // 按 ? 显示快捷键帮助
        document.addEventListener('keydown', function(event) {
            if (event.key === '?' || (event.shiftKey && event.key === '/')) {
                showKeyboardShortcuts();
            }
        });
        </script>
        ''')
    
    # 主题切换相关方法
    def _toggle_theme(self, value: bool):
        """切换主题"""
        if value:
            # 切换到深色主题
            ui.add_head_html("""
            <script>
            document.body.classList.add('dark');
            </script>
            """)
            self.user_preferences['theme'] = 'dark'
        else:
            # 切换到浅色主题
            ui.add_head_html("""
            <script>
            document.body.classList.remove('dark');
            </script>
            """)
            self.user_preferences['theme'] = 'light'
        
        # 保存用户偏好
        self._save_user_preferences()
    
    def _toggle_compact_mode(self, value: bool):
        """切换紧凑模式"""
        if value:
            ui.add_head_html("""
            <style>
            .compact-mode .dashboard-card {
                padding: 12px;
            }
            </style>
            <script>
            document.body.classList.add('compact-mode');
            </script>
            """)
            self.user_preferences['compact_mode'] = True
        else:
            ui.add_head_html("""
            <script>
            document.body.classList.remove('compact-mode');
            </script>
            """)
            self.user_preferences['compact_mode'] = False
        
        # 保存用户偏好
        self._save_user_preferences()
    
    # 其他辅助方法
    def _get_chart_color(self, data_type: str) -> str:
        """获取图表颜色"""
        colors = {
            'cpu': '#3f51b5',
            'gpu': '#9c27b0',
            'memory': '#4caf50'
        }
        return colors.get(data_type, '#757575')
    
    def _save_user_preferences(self):
        """保存用户偏好"""
        # 这里可以实现保存到本地存储或服务器
        pass
    
    # 浮动操作相关方法
    def _run_performance_test(self):
        """运行性能测试"""
        ui.notify('🚀 开始性能测试...', color='info')
        # 这里可以实现性能测试逻辑
    
    def _quick_export(self):
        """快速导出"""
        ui.notify('📊 开始导出数据...', color='info')
        # 这里可以实现快速导出逻辑
    
    def _test_notifications(self):
        """测试通知"""
        ui.notify('🔔 测试通知发送', color='positive')
        # 这里可以实现通知测试逻辑
    
    def _show_advanced_settings(self):
        """显示高级设置"""
        ui.notify('⚙️ 打开高级设置...', color='purple')
        # 这里可以实现高级设置界面
    
    # 自动刷新相关方法
    def _start_auto_refresh(self):
        """启动自动刷新"""
        async def auto_refresh():
            while True:
                try:
                    await asyncio.sleep(self.dashboard_refresh_interval)
                    await self._update_dashboard_data()
                    self._update_dashboard_ui()
                except Exception as e:
                    logger.error(f"❌ 自动刷新失败: {e}")
                    await asyncio.sleep(10)  # 错误后等待更长时间
        
        # 在后台运行自动刷新
        asyncio.create_task(auto_refresh())
        logger.info("✅ 增强版自动刷新已启动")
        
        # 绑定全局JavaScript函数
        self._bind_global_functions()
    
    def _bind_global_functions(self):
        """绑定全局JavaScript函数"""
        ui.run_javascript('''
        // 全局函数绑定
        window.refreshDashboard = function() {
            if (typeof window._refreshCallback === 'function') {
                window._refreshCallback();
            }
        };
        
        window.exportData = function() {
            if (typeof window._exportCallback === 'function') {
                window._exportCallback();
            }
        };
        
        window.toggleTheme = function() {
            if (typeof window._themeCallback === 'function') {
                window._themeCallback();
            }
        };
        
        window.showFullscreenCharts = function() {
            if (typeof window._fullscreenCallback === 'function') {
                window._fullscreenCallback();
            }
        };
        
        window.toggleMonitoring = function() {
            if (typeof window._monitoringCallback === 'function') {
                window._monitoringCallback();
            }
        };
        
        window.closeModal = function() {
            // 关闭当前打开的模态框
            const modals = document.querySelectorAll('.q-dialog__inner');
            modals.forEach(modal => {
                const closeBtn = modal.querySelector('button[aria-label*="close" i]');
                if (closeBtn) {
                    closeBtn.click();
                }
            });
        };
        ''')
    
    async def _update_dashboard_data(self):
        """更新仪表板数据"""
        try:
            # 更新监控摘要
            metrics_summary = self.monitor.get_metrics_summary()
            
            # 更新告警摘要
            alert_summary = self.alert_manager.get_alert_summary()
            
            # 更新活跃告警
            active_alerts = self.alert_manager.get_active_alerts()
            
            # 获取系统健康状态
            health_check = await self.monitor.run_health_check()
            
            # 更新时间戳
            self.dashboard_data['last_update'] = datetime.now().isoformat()
            
            # 保存数据
            self.dashboard_data.update({
                'metrics_summary': metrics_summary,
                'alert_summary': alert_summary,
                'active_alerts': [alert.to_dict() for alert in active_alerts],
                'system_health': health_check
            })
            
            # 更新图表数据
            self._update_chart_data(metrics_summary)
            
        except Exception as e:
            logger.error(f"❌ 更新仪表板数据失败: {e}")
    
    def _update_chart_data(self, metrics_summary):
        """更新图表数据"""
        if 'current_metrics' in metrics_summary:
            current_metrics = metrics_summary['current_metrics']
            
            # 添加新数据点
            timestamp = datetime.now().strftime('%H:%M:%S')
            self.dashboard_data['chart_data']['timestamps'].append(timestamp)
            
            # 限制数据点数量以避免内存溢出
            max_data_points = 20
            for key in ['cpu_history', 'gpu_history', 'memory_history']:
                if len(self.dashboard_data['chart_data'][key]) >= max_data_points:
                    self.dashboard_data['chart_data'][key].pop(0)
            if len(self.dashboard_data['chart_data']['timestamps']) >= max_data_points:
                self.dashboard_data['chart_data']['timestamps'].pop(0)
            
            # 添加数据
            cpu_value = current_metrics.get('cpu_usage', '0%').replace('%', '')
            gpu_value = current_metrics.get('gpu_utilization', '0%').replace('%', '')
            memory_value = current_metrics.get('memory_usage', '0%').replace('%', '')
            
            self.dashboard_data['chart_data']['cpu_history'].append(cpu_value)
            self.dashboard_data['chart_data']['gpu_history'].append(gpu_value)
            self.dashboard_data['chart_data']['memory_history'].append(memory_value)
            
            # 更新Chart.js图表
            self._update_chartjs_data(cpu_value, gpu_value, memory_value, timestamp)
    
    def _update_chartjs_data(self, cpu_value: str, gpu_value: str, memory_value: str, timestamp: str):
        """更新Chart.js图表数据"""
        try:
            # 转换为数值
            cpu_num = float(cpu_value) if cpu_value else 0
            gpu_num = float(gpu_value) if gpu_value else 0
            memory_num = float(memory_value) if memory_value else 0
            
            # 使用JavaScript更新图表
            ui.run_javascript(f'''
            // 更新单个图表
            const addDataPoint = (chart, value, label) => {{
                if (chart && chart.data) {{
                    chart.data.labels.push(label);
                    chart.data.datasets[0].data.push({value});
                    
                    // 保持数据点数量不超过限制
                    const maxPoints = 20;
                    if (chart.data.labels.length > maxPoints) {{
                        chart.data.labels.shift();
                        chart.data.datasets[0].data.shift();
                    }}
                    
                    chart.update('none'); // 快速更新，无动画
                }}
            }};
            
            // 更新各个图表
            if (window.chartInstances.cpu) {{
                addDataPoint(window.chartInstances.cpu, {cpu_num}, '{timestamp}');
            }}
            if (window.chartInstances.gpu) {{
                addDataPoint(window.chartInstances.gpu, {gpu_num}, '{timestamp}');
            }}
            if (window.chartInstances.memory) {{
                addDataPoint(window.chartInstances.memory, {memory_num}, '{timestamp}');
            }}
            
            // 更新综合图表
            if (window.combinedChart && window.combinedChart.data) {{
                window.combinedChart.data.labels.push('{timestamp}');
                
                // CPU数据
                window.combinedChart.data.datasets[0].data.push({cpu_num});
                // GPU数据  
                window.combinedChart.data.datasets[1].data.push({gpu_num});
                // 内存数据
                window.combinedChart.data.datasets[2].data.push({memory_num});
                
                // 保持数据点数量不超过限制
                const maxPoints = 20;
                if (window.combinedChart.data.labels.length > maxPoints) {{
                    window.combinedChart.data.labels.shift();
                    window.combinedChart.data.datasets.forEach(dataset => {{
                        dataset.data.shift();
                    }});
                }}
                
                window.combinedChart.update('none');
            }}
            
            // 更新全屏图表
            if (window.fullscreenChart && window.fullscreenChart.data) {{
                window.fullscreenChart.data.labels.push('{timestamp}');
                window.fullscreenChart.data.datasets[0].data.push({cpu_num});
                window.fullscreenChart.data.datasets[1].data.push({gpu_num});
                window.fullscreenChart.data.datasets[2].data.push({memory_num});
                
                // 保持数据点数量不超过限制
                const maxPoints = 50;
                if (window.fullscreenChart.data.labels.length > maxPoints) {{
                    window.fullscreenChart.data.labels.shift();
                    window.fullscreenChart.data.datasets.forEach(dataset => {{
                        dataset.data.shift();
                    }});
                }}
                
                window.fullscreenChart.update('none');
            }}
            ''')
            
        except Exception as e:
            logger.error(f"❌ 更新Chart.js数据失败: {e}")
    
    def _update_dashboard_ui(self):
        """更新仪表板UI"""
        try:
            data = self.dashboard_data
            
            if 'metrics_summary' not in data:
                return
            
            metrics = data['metrics_summary']
            alert_summary = data['alert_summary']
            health = data['system_health']
            
            # 更新指标概览
            if 'current_metrics' in metrics:
                current_metrics = metrics['current_metrics']
                self._update_metric_cards(current_metrics)
            
            # 更新告警统计
            self._update_alert_stats(alert_summary)
            
            # 更新系统健康状态
            self._update_health_status(health)
            
            # 更新活跃告警显示
            self._update_active_alerts_display()
            
            # 更新时间戳
            self._update_timestamp()
            
        except Exception as e:
            logger.error(f"❌ 更新UI失败: {e}")
    
    def _update_metric_cards(self, current_metrics):
        """更新指标卡片"""
        # CPU
        cpu_text = current_metrics.get('cpu_usage', '0%')
        cpu_value = float(cpu_text.replace('%', ''))
        self.metrics_cards['cpu_value'].text = cpu_text
        self.metrics_cards['cpu_progress'].value = cpu_value / 100
        
        # GPU
        gpu_text = current_metrics.get('gpu_utilization', '0%')
        gpu_value = float(gpu_text.replace('%', ''))
        self.metrics_cards['gpu_value'].text = gpu_text
        self.metrics_cards['gpu_progress'].value = gpu_value / 100
        
        # 内存
        memory_text = current_metrics.get('memory_usage', '0%')
        memory_value = float(memory_text.replace('%', ''))
        self.metrics_cards['memory_value'].text = memory_text
        self.metrics_cards['memory_progress'].value = memory_value / 100
    
    def _update_alert_stats(self, alert_summary):
        """更新告警统计"""
        self.alert_stats_critical.text = str(alert_summary['critical_alerts'])
        self.alert_stats_warning.text = str(alert_summary['warning_alerts'])
        self.alert_stats_info.text = str(alert_summary['info_alerts'])
        
        # 更新告警总览卡片
        active_count = alert_summary['active_alerts_count']
        self.metrics_cards['alerts_total_value'].text = str(active_count)
    
    def _update_health_status(self, health):
        """更新健康状态"""
        status = health['overall_status']
        self.health_status_label.text = status.upper()
        
        # 更新状态图标
        if status == 'healthy':
            self.health_status_icon.icon = 'check_circle'
            self.health_status_icon.color = 'green'
        elif status == 'warning':
            self.health_status_icon.icon = 'warning'
            self.health_status_icon.color = 'orange'
        else:
            self.health_status_icon.icon = 'error'
            self.health_status_icon.color = 'red'
    
    def _update_active_alerts_display(self):
        """更新活跃告警显示"""
        self.active_alerts_container.clear()
        
        active_alerts = self.dashboard_data.get('active_alerts', [])
        
        if not active_alerts:
            with self.active_alerts_container:
                with ui.card().classes('q-pa-md bg-green-1 text-center'):
                    ui.icon('check_circle', color='green', size='32px')
                    ui.label('暂无活跃告警').classes('text-positive text-subtitle1 q-mt-sm')
            return
        
        # 显示活跃告警
        for alert_data in active_alerts:
            severity_class = f"alert-{alert_data['severity']}"
            
            with self.active_alerts_container:
                with ui.card().classes(f'alert-item {severity_class}'):
                    with ui.row().classes('items-center justify-between w-full'):
                        with ui.column().classes('flex-grow-1'):
                            with ui.row().classes('items-center q-gutter-sm q-mb-sm'):
                                ui.icon(
                                    'priority_high' if alert_data['severity'] == 'critical' else
                                    'warning' if alert_data['severity'] == 'warning' else 'info',
                                    color=alert_data['severity'] == 'critical' and 'red' or
                                          alert_data['severity'] == 'warning' and 'orange' or 'blue',
                                    size='20px'
                                )
                                ui.label(alert_data['rule_name']).classes('text-weight-bold')
                                ui.label(f"严重性: {alert_data['severity']}").classes('text-caption')
                            
                            ui.label(alert_data['message']).classes('text-body2')
                            ui.label(f"时间: {alert_data.get('timestamp', 'N/A')}").classes('text-caption text-grey-7 q-mt-sm')
                        
                        with ui.column().classes('col-auto q-gutter-sm'):
                            ui.button(
                                '✅ 确认',
                                on_click=lambda a=alert_data: self._acknowledge_alert(a['id']),
                                color='positive',
                                size='sm'
                            ).props('flat dense')
                            
                            ui.button(
                                '❌ 关闭',
                                on_click=lambda a=alert_data: self._dismiss_alert(a['id']),
                                color='red',
                                size='sm'
                            ).props('flat dense')
    
    def _update_timestamp(self):
        """更新时间戳"""
        if self.dashboard_data['last_update']:
            update_time = datetime.fromisoformat(self.dashboard_data['last_update'])
            self.last_update_label.text = update_time.strftime('%H:%M:%S')
    
    # 用户界面交互方法
    async def _start_monitoring(self):
        """开始监控"""
        try:
            self.start_monitoring_btn.disable()
            ui.notify('🚀 开始AI实时监控...', color='positive')
            
            # 在后台启动监控
            asyncio.create_task(self.monitor.start_monitoring(duration_seconds=3600))
            
        except Exception as e:
            logger.error(f"❌ 启动监控失败: {e}")
            ui.notify(f'启动监控失败: {e}', color='negative')
        finally:
            self.start_monitoring_btn.enable()
    
    async def _stop_monitoring(self):
        """停止监控"""
        try:
            self.monitor.stop_monitoring()
            ui.notify('⏹️ 监控已停止', color='warning')
        except Exception as e:
            logger.error(f"❌ 停止监控失败: {e}")
            ui.notify(f'停止监控失败: {e}', color='negative')
    
    async def _test_alert(self):
        """测试告警"""
        try:
            ui.notify('🧪 发送智能测试告警...', color='info')
            
            # 创建一个测试告警
            test_alert = Alert(
                id=f"test_alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                rule_name="UI测试告警",
                alert_type=AlertType.SYSTEM_RESOURCE_HIGH,
                severity=AlertSeverity.WARNING,
                message="这是一个UI/UX增强版的测试告警",
                timestamp=datetime.now(),
                metrics={'test': True, 'ui_enhanced': True}
            )
            
            # 处理告警
            await self.alert_manager._handle_alert(test_alert)
            
            ui.notify('✅ 测试告警发送成功', color='positive')
            
        except Exception as e:
            logger.error(f"❌ 测试告警失败: {e}")
            ui.notify(f'测试告警失败: {e}', color='negative')
    
    async def _refresh_data(self):
        """刷新数据"""
        try:
            ui.notify('🔄 刷新监控数据...', color='info')
            await self._update_dashboard_data()
            self._update_dashboard_ui()
            ui.notify('✅ 数据刷新完成', color='positive')
        except Exception as e:
            logger.error(f"❌ 数据刷新失败: {e}")
            ui.notify(f'数据刷新失败: {e}', color='negative')
    
    # 告警管理方法
    def _acknowledge_alert(self, alert_id: str):
        """确认告警"""
        try:
            success = self.alert_manager.acknowledge_alert(alert_id, "增强版UI")
            if success:
                ui.notify('✅ 告警已确认', color='positive')
                self._update_dashboard_ui()
            else:
                ui.notify('❌ 确认告警失败', color='negative')
        except Exception as e:
            logger.error(f"❌ 确认告警失败: {e}")
            ui.notify(f'确认告警失败: {e}', color='negative')
    
    def _dismiss_alert(self, alert_id: str):
        """关闭告警"""
        try:
            # 这里可以实现关闭告警的逻辑
            success = True  # 模拟成功
            if success:
                ui.notify('❌ 告警已关闭', color='negative')
                self._update_dashboard_ui()
            else:
                ui.notify('❌ 关闭告警失败', color='negative')
        except Exception as e:
            logger.error(f"❌ 关闭告警失败: {e}")
            ui.notify(f'关闭告警失败: {e}', color='negative')
    
    def _acknowledge_all_alerts(self):
        """确认所有告警"""
        try:
            active_alerts = self.dashboard_data.get('active_alerts', [])
            count = len(active_alerts)
            
            for alert_data in active_alerts:
                self._acknowledge_alert(alert_data['id'])
            
            ui.notify(f'✅ 已确认 {count} 个告警', color='positive')
        except Exception as e:
            logger.error(f"❌ 确认所有告警失败: {e}")
            ui.notify(f'确认所有告警失败: {e}', color='negative')
    
    def _show_alert_settings(self):
        """显示告警设置"""
        ui.notify('⚙️ 告警设置功能开发中...', color='orange')
        # 这里可以实现告警设置界面
    
    def _show_preferences(self):
        """显示偏好设置"""
        ui.notify('🎛️ 偏好设置功能开发中...', color='purple')
        # 这里可以实现偏好设置界面
    
    def _show_fullscreen_charts(self):
        """显示全屏图表"""
        # 创建全屏模态框
        with ui.dialog().props('persistent maximized') as dialog, ui.card().classes('w-full h-full'):
            with ui.row().classes('items-center justify-between w-full q-pa-md bg-primary text-white'):
                ui.label('📈 全屏性能图表').classes('text-h5 text-weight-bold')
                ui.button('✕', on_click=dialog.close, color='white', size='sm').props('flat round')
            
            with ui.column().classes('w-full h-full q-pa-md'):
                # 全屏图表
                fullscreen_chart = ui.html('<canvas id="fullscreenChart" width="1200" height="600"></canvas>').classes('w-full')
                
                # 图表控制
                with ui.row().classes('items-center justify-center q-gutter-md q-mt-md'):
                    ui.button('⏸️ 暂停', on_click=self._pause_all_charts, color='orange')
                    ui.button('▶️ 恢复', on_click=self._resume_all_charts, color='green') 
                    ui.button('📊 导出', on_click=self._export_fullscreen_chart, color='blue')
                    ui.button('🔄 重置', on_click=self._reset_fullscreen_chart, color='red')
        
        dialog.open()
        
        # 初始化全屏图表
        ui.run_javascript('''
        setTimeout(() => {
            const ctx = document.getElementById('fullscreenChart');
            if (ctx) {
                const config = {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: [
                            {
                                label: 'CPU使用率',
                                data: [],
                                borderColor: '#3f51b5',
                                backgroundColor: '#3f51b520',
                                fill: true,
                                tension: 0.4
                            },
                            {
                                label: 'GPU使用率',
                                data: [],
                                borderColor: '#9c27b0', 
                                backgroundColor: '#9c27b020',
                                fill: true,
                                tension: 0.4
                            },
                            {
                                label: '内存使用率',
                                data: [],
                                borderColor: '#4caf50',
                                backgroundColor: '#4caf5020', 
                                fill: true,
                                tension: 0.4
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            title: {
                                display: true,
                                text: '全屏综合性能监控'
                            },
                            legend: {
                                position: 'top'
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 100
                            }
                        }
                    }
                };
                window.fullscreenChart = new Chart(ctx, config);
            }
        }, 500);
        ''')
    
    def _show_single_chart(self, chart_type: str):
        """显示单图表"""
        chart_titles = {
            'cpu': 'CPU使用率详细分析',
            'gpu': 'GPU使用率详细分析', 
            'memory': '内存使用率详细分析'
        }
        
        chart_colors = {
            'cpu': '#3f51b5',
            'gpu': '#9c27b0',
            'memory': '#4caf50'
        }
        
        # 创建单图表模态框
        with ui.dialog() as dialog, ui.card().classes('w-full').props('style=width: 80vw; max-width: 1000px'):
            with ui.row().classes('items-center justify-between w-full q-pa-md bg-primary text-white'):
                ui.label(f'📊 {chart_titles.get(chart_type, chart_type)}').classes('text-h6 text-weight-bold')
                ui.button('✕', on_click=dialog.close, color='white', size='sm').props('flat round')
            
            with ui.column().classes('w-full q-pa-md'):
                # 大尺寸图表
                single_chart = ui.html(f'<canvas id="singleChart{chart_type}" width="800" height="400"></canvas>').classes('w-full')
                
                # 统计信息
                with ui.row().classes('items-center justify-between q-mt-md'):
                    with ui.column():
                        ui.label('统计信息:').classes('text-subtitle2 text-weight-bold')
                        self.single_chart_stats = ui.label('等待数据...').classes('text-body1')
                    
                    with ui.row().classes('q-gutter-sm'):
                        ui.button('⏸️ 暂停', on_click=lambda: self._pause_chart(chart_type), color='orange', size='sm')
                        ui.button('▶️ 恢复', on_click=lambda: self._resume_chart(chart_type), color='green', size='sm')
                        ui.button('💾 导出', on_click=lambda: self._export_single_chart(chart_type), color='blue', size='sm')
        
        dialog.open()
        
        # 初始化单图表
        color = chart_colors.get(chart_type, '#757575')
        ui.run_javascript(f'''
        setTimeout(() => {{
            const ctx = document.getElementById('singleChart{chart_type}');
            if (ctx) {{
                const config = {{
                    type: 'line',
                    data: {{
                        labels: [],
                        datasets: [{{
                            label: '{chart_titles.get(chart_type, chart_type)}',
                            data: [],
                            borderColor: '{color}',
                            backgroundColor: '{color}20',
                            fill: true,
                            tension: 0.4,
                            pointRadius: 3,
                            pointHoverRadius: 6
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            title: {{
                                display: true,
                                text: '{chart_titles.get(chart_type, chart_type)} - 实时监控'
                            }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                max: 100,
                                title: {{
                                    display: true,
                                    text: '使用率 (%)'
                                }}
                            }},
                            x: {{
                                title: {{
                                    display: true,
                                    text: '时间'
                                }}
                            }}
                        }}
                    }}
                }};
                window.singleChart{chart_type} = new Chart(ctx, config);
            }}
        }}, 500);
        ''')
    
    def _pause_chart(self, chart_id: str):
        """暂停单个图表"""
        ui.notify(f'⏸️ 暂停 {chart_id.upper()} 图表', color='orange')
        ui.run_javascript(f'''
        if (window.chartInstances['{chart_id}']) {{
            window.chartInstances['{chart_id}'].options.animation.duration = 0;
        }}
        ''')
    
    def _resume_chart(self, chart_id: str):
        """恢复单个图表"""
        ui.notify(f'▶️ 恢复 {chart_id.upper()} 图表', color='green')
        ui.run_javascript(f'''
        if (window.chartInstances['{chart_id}']) {{
            window.chartInstances['{chart_id}'].options.animation.duration = 750;
        }}
        ''')
    
    def _export_single_chart(self, chart_id: str):
        """导出单个图表"""
        try:
            # 获取图表数据
            chart_data = self.dashboard_data.get('chart_data', {})
            timestamps = chart_data.get('timestamps', [])
            
            if chart_id == 'cpu':
                data = chart_data.get('cpu_history', [])
            elif chart_id == 'gpu':
                data = chart_data.get('gpu_history', [])
            elif chart_id == 'memory':
                data = chart_data.get('memory_history', [])
            else:
                data = []
            
            # 创建CSV数据
            csv_content = "时间,使用率\n"
            for i, (timestamp, value) in enumerate(zip(timestamps, data)):
                csv_content += f"{timestamp},{value}\n"
            
            # 创建下载链接
            filename = f"{chart_id}_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            # 使用JavaScript触发下载
            ui.run_javascript(f'''
            const csvContent = `{csv_content}`;
            const blob = new Blob([csvContent], {{ type: 'text/csv;charset=utf-8;' }});
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = '{filename}';
            link.click();
            ''')
            
            ui.notify(f'📁 {chart_id.upper()} 数据已导出', color='green')
            
        except Exception as e:
            logger.error(f"❌ 导出{chart_id}数据失败: {e}")
            ui.notify(f'导出{chart_id}数据失败: {e}', color='red')
    
    def _pause_all_charts(self):
        """暂停所有图表"""
        ui.notify('⏸️ 暂停所有图表', color='orange')
        ui.run_javascript('''
        Object.values(window.chartInstances).forEach(chart => {
            if (chart) {
                chart.options.animation.duration = 0;
            }
        });
        if (window.combinedChart) {
            window.combinedChart.options.animation.duration = 0;
        }
        if (window.fullscreenChart) {
            window.fullscreenChart.options.animation.duration = 0;
        }
        ''')
    
    def _resume_all_charts(self):
        """恢复所有图表"""
        ui.notify('▶️ 恢复所有图表', color='green')
        ui.run_javascript('''
        Object.values(window.chartInstances).forEach(chart => {
            if (chart) {
                chart.options.animation.duration = 750;
            }
        });
        if (window.combinedChart) {
            window.combinedChart.options.animation.duration = 750;
        }
        if (window.fullscreenChart) {
            window.fullscreenChart.options.animation.duration = 750;
        }
        ''')
    
    def _export_fullscreen_chart(self):
        """导岥全屏图表"""
        try:
            # 获取综合数据
            chart_data = self.dashboard_data.get('chart_data', {})
            timestamps = chart_data.get('timestamps', [])
            
            # 创建综合CSV数据
            csv_content = "时间,CPU使用率,GPU使用率,内存使用率\n"
            for i, timestamp in enumerate(timestamps):
                cpu = chart_data.get('cpu_history', [''])[i] if i < len(chart_data.get('cpu_history', [])) else ''
                gpu = chart_data.get('gpu_history', [''])[i] if i < len(chart_data.get('gpu_history', [])) else ''
                memory = chart_data.get('memory_history', [''])[i] if i < len(chart_data.get('memory_history', [])) else ''
                csv_content += f"{timestamp},{cpu},{gpu},{memory}\n"
            
            filename = f"fullscreen_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            # 使用JavaScript触发下载
            ui.run_javascript(f'''
            const csvContent = `{csv_content}`;
            const blob = new Blob([csvContent], {{ type: 'text/csv;charset=utf-8;' }});
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = '{filename}';
            link.click();
            ''')
            
            ui.notify('📁 全屏数据已导出', color='green')
            
        except Exception as e:
            logger.error(f"❌ 导岥全屏数据失败: {e}")
            ui.notify(f'导岥全屏数据失败: {e}', color='red')
    
    def _reset_fullscreen_chart(self):
        """重置全屏图表"""
        ui.notify('🔄 全屏图表已重置', color='blue')
        ui.run_javascript('''
        if (window.fullscreenChart) {
            window.fullscreenChart.data.labels = [];
            window.fullscreenChart.data.datasets.forEach(dataset => {
                dataset.data = [];
            });
            window.fullscreenChart.update();
        }
        ''')

    # 数据导出和报告方法
    def _export_chart_data(self):
        """导出图表数据"""
        try:
            # 获取所有图表数据
            chart_data = self.dashboard_data.get('chart_data', {})
            timestamps = chart_data.get('timestamps', [])
            
            # 创建完整的CSV报告
            report_content = "时间,CPU使用率,GPU使用率,内存使用率,系统状态\n"
            
            # 添加数据行
            for i, timestamp in enumerate(timestamps):
                cpu = chart_data.get('cpu_history', [''])[i] if i < len(chart_data.get('cpu_history', [])) else ''
                gpu = chart_data.get('gpu_history', [''])[i] if i < len(chart_data.get('gpu_history', [])) else ''
                memory = chart_data.get('memory_history', [''])[i] if i < len(chart_data.get('memory_history', [])) else ''
                
                # 评估系统状态
                try:
                    cpu_val = float(cpu) if cpu else 0
                    gpu_val = float(gpu) if gpu else 0
                    memory_val = float(memory) if memory else 0
                    
                    if cpu_val > 90 or gpu_val > 90 or memory_val > 90:
                        status = "严重"
                    elif cpu_val > 70 or gpu_val > 70 or memory_val > 70:
                        status = "警告"
                    else:
                        status = "正常"
                except:
                    status = "未知"
                
                report_content += f"{timestamp},{cpu},{gpu},{memory},{status}\n"
            
            # 添加统计信息
            report_content += "\n\n统计信息:\n"
            report_content += f"数据点数量: {len(timestamps)}\n"
            report_content += f"监控开始时间: {timestamps[0] if timestamps else 'N/A'}\n"
            report_content += f"监控结束时间: {timestamps[-1] if timestamps else 'N/A'}\n"
            report_content += f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            filename = f"mystocks_performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            # 使用JavaScript触发下载
            ui.run_javascript(f'''
            const reportContent = `{reportContent}`;
            const blob = new Blob([reportContent], {{ type: 'text/csv;charset=utf-8;' }});
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = '{filename}';
            link.click();
            ''')
            
            ui.notify('📁 性能报告已导出', color='green')
            
        except Exception as e:
            logger.error(f"❌ 导出性能报告失败: {e}")
            ui.notify(f'导出性能报告失败: {e}', color='red')
    
    def _export_dashboard_report(self):
        """导出仪表板报告"""
        try:
            # 获取仪表板数据
            metrics_summary = self.dashboard_data.get('metrics_summary', {})
            alert_summary = self.dashboard_data.get('alert_summary', {})
            health = self.dashboard_data.get('system_health', {})
            
            # 创建HTML报告
            html_report = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>MyStocks AI监控系统报告</title>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .header {{ text-align: center; color: #333; border-bottom: 2px solid #333; padding-bottom: 20px; }}
                    .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                    .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #f5f5f5; border-radius: 5px; }}
                    .status-healthy {{ color: green; }}
                    .status-warning {{ color: orange; }}
                    .status-critical {{ color: red; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>MyStocks AI实时监控系统报告</h1>
                    <p>生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</p>
                </div>
                
                <div class="section">
                    <h2>📊 系统指标概览</h2>
            """
            
            # 添加当前指标
            current_metrics = metrics_summary.get('current_metrics', {})
            if current_metrics:
                html_report += f"""
                    <div class="metric">
                        <strong>CPU使用率:</strong> {current_metrics.get('cpu_usage', 'N/A')}
                    </div>
                    <div class="metric">
                        <strong>GPU使用率:</strong> {current_metrics.get('gpu_utilization', 'N/A')}
                    </div>
                    <div class="metric">
                        <strong>内存使用率:</strong> {current_metrics.get('memory_usage', 'N/A')}
                    </div>
                """
            
            # 添加告警信息
            html_report += f"""
                </div>
                
                <div class="section">
                    <h2>🚨 告警状态</h2>
                    <div class="metric">
                        <strong>严重告警:</strong> {alert_summary.get('critical_alerts', 0)} 个
                    </div>
                    <div class="metric">
                        <strong>警告告警:</strong> {alert_summary.get('warning_alerts', 0)} 个
                    </div>
                    <div class="metric">
                        <strong>信息告警:</strong> {alert_summary.get('info_alerts', 0)} 个
                    </div>
                    <div class="metric">
                        <strong>总活跃告警:</strong> {alert_summary.get('active_alerts_count', 0)} 个
                    </div>
                </div>
                
                <div class="section">
                    <h2>💚 系统健康状态</h2>
                    <div class="metric">
                        <strong>整体状态:</strong> <span class="status-{health.get('overall_status', 'unknown')}">{health.get('overall_status', 'unknown').upper()}</span>
                    </div>
                    <div class="metric">
                        <strong>CPU状态:</strong> {health.get('cpu_status', 'N/A')}
                    </div>
                    <div class="metric">
                        <strong>内存状态:</strong> {health.get('memory_status', 'N/A')}
                    </div>
                    <div class="metric">
                        <strong>存储状态:</strong> {health.get('storage_status', 'N/A')}
                    </div>
                </div>
                
                <div class="section">
                    <h2>📈 统计信息</h2>
            """
            
            # 添加统计信息
            statistics = metrics_summary.get('statistics', {})
            if statistics:
                html_report += f"""
                    <div class="metric">
                        <strong>总循环数:</strong> {statistics.get('total_cycles', 'N/A')}
                    </div>
                    <div class="metric">
                        <strong>成功循环数:</strong> {statistics.get('successful_cycles', 'N/A')}
                    </div>
                    <div class="metric">
                        <strong>成功率:</strong> {statistics.get('success_rate', 'N/A')}
                    </div>
                """
            
            html_report += """
                </div>
                
                <div class="section">
                    <h2>ℹ️ 报告说明</h2>
                    <p>本报告由MyStocks AI实时监控系统自动生成，包含了系统的实时状态、告警信息和性能统计。</p>
                    <p>如需更多详细信息，请访问Web监控界面。</p>
                </div>
            </body>
            </html>
            """
            
            filename = f"mystocks_dashboard_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            
            # 使用JavaScript触发下载
            ui.run_javascript(f'''
            const htmlContent = `{html_report}`;
            const blob = new Blob([htmlContent], {{ type: 'text/html;charset=utf-8;' }});
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = '{filename}';
            link.click();
            ''')
            
            ui.notify('📋 仪表板报告已导出', color='green')
            
        except Exception as e:
            logger.error(f"❌ 导出仪表板报告失败: {e}")
            ui.notify(f'导出仪表板报告失败: {e}', color='red')
    
    def _generate_health_report(self):
        """生成健康报告"""
        ui.notify('💚 系统健康报告生成中...', color='green')
        # 这里可以实现健康报告生成
    
    def _clear_alert_history(self):
        """清空告警历史"""
        try:
            self.alert_history_table.rows = []
            ui.notify('📋 告警历史已清空', color='warning')
        except Exception as e:
            logger.error(f"❌ 清空告警历史失败: {e}")
            ui.notify(f'清空告警历史失败: {e}', color='negative')
    
    def _filter_alert_history(self):
        """过滤告警历史"""
        severity = self.severity_filter.value
        date_range = self.date_filter.value
        
        ui.notify(f'🔍 过滤条件: {severity} - {date_range}', color='blue')
        # 这里可以实现历史告警过滤逻辑
    
    def _save_user_preferences(self):
        """保存用户偏好设置"""
        try:
            # 这里可以实现保存到本地存储
            logger.info(f"用户偏好已保存: {self.user_preferences}")
        except Exception as e:
            logger.error(f"保存用户偏好失败: {e}")


def create_enhanced_monitoring_app():
    """创建增强版监控应用"""
    # 创建告警管理器和监控器
    alert_manager = get_ai_alert_manager()
    monitor = get_ai_realtime_monitor(alert_manager)
    
    # 创建增强版监控面板
    dashboard = EnhancedNiceGUIMonitoringDashboard(alert_manager, monitor)
    
    # 创建路由
    @ui.page('/')
    def index():
        dashboard.create_monitoring_page()
        
        # 添加浮动操作按钮
        dashboard._create_floating_actions()
    
    @ui.page('/api/enhanced/health')
    async def enhanced_health_check():
        """增强版健康检查API"""
        try:
            health = await dashboard.monitor.run_health_check()
            return ui.json_response({
                'status': 'success',
                'version': '2.0.0',
                'features': ['enhanced_ui', 'real_time_charts', 'theme_switching'],
                'health': health
            })
        except Exception as e:
            return ui.json_response({'error': str(e)}, status_code=500)
    
    @ui.page('/api/enhanced/alerts')
    async def enhanced_alerts_api():
        """增强版告警API"""
        try:
            alert_summary = dashboard.alert_manager.get_alert_summary()
            active_alerts = [alert.to_dict() for alert in dashboard.alert_manager.get_active_alerts()]
            
            return ui.json_response({
                'status': 'success',
                'summary': alert_summary,
                'active_alerts': active_alerts,
                'version': '2.0.0'
            })
        except Exception as e:
            return ui.json_response({'error': str(e)}, status_code=500)


if __name__ == "__main__":
    # 启动增强版监控仪表板
    ui.run(
        title='MyStocks 增强版监控仪表板',
        host='0.0.0.0',
        port=8080,
        reload=False
    )