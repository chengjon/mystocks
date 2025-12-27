"""
MyStocks NiceGUI增强版监控面板 - 核心模块

作者: MyStocks AI开发团队
版本: 2.0.0 (UI/UX增强版)
日期: 2025-11-25
"""

import asyncio
import logging
from datetime import datetime

from nicegui import ui

from src.monitoring.ai_alert_manager import (
    AIAlertManager,
    AlertSeverity,
)

from src.monitoring.ai_realtime_monitor import (
    AIRealtimeMonitor,
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
        # 导入所有组件模块
        from .components.header import create_header
        from .components.metrics import create_metrics_overview
        from .components.charts import create_realtime_charts
        from .components.alerts import create_alert_management
        from .components.system_health import create_system_health
        from .components.controls import create_control_panel
        from .components.alerts import create_alert_history
        from .components.controls import add_keyboard_shortcuts

        # 设置页面CSS样式
        self._setup_styles()

        # 创建页面内容
        create_header(self)
        create_metrics_overview(self)
        create_realtime_charts(self)
        create_alert_management(self)
        create_system_health(self)
        create_control_panel(self)
        create_alert_history(self)

        # 启动自动刷新
        self._start_auto_refresh()

        # 添加键盘快捷键
        add_keyboard_shortcuts(self)

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

    def _start_auto_refresh(self):
        """启动自动刷新"""
        self.refresh_task = ui.timer(self.dashboard_refresh_interval, self._refresh_data, active=True)
        logger.info(f"⏱️ 自动刷新已启动，间隔: {self.dashboard_refresh_interval}秒")

    def _refresh_data(self):
        """刷新数据"""
        try:
            # 更新性能指标
            self._update_performance_metrics()

            # 更新指标卡片
            self._update_metric_cards()

            # 更新图表数据
            self._update_chart_data()

            # 更新告警数据
            self._update_alert_data()

            # 更新系统健康状态
            self._update_system_health()

            # 更新最后更新时间和状态
            self.last_update_time = datetime.now().strftime('%H:%M:%S')
            if hasattr(self, 'last_update_label'):
                self.last_update_label.text = self.last_update_time

            # 更新性能指标
            self.performance_metrics['update_count'] += 1
            self.performance_metrics['last_update_time'] = datetime.now()
            self.performance_metrics['error_count'] = 0

            logger.info(f"✅ 监控数据已刷新 ({self.performance_metrics['update_count']})")

        except Exception as e:
            self.performance_metrics['error_count'] += 1
            logger.error(f"❌ 数据刷新错误: {e}")

    def _update_performance_metrics(self):
        """更新性能指标"""
        # 获取当前时间
        current_time = datetime.now()

        # 计算更新间隔
        if self.performance_metrics['last_update_time']:
            interval = (current_time - self.performance_metrics['last_update_time']).total_seconds()
            self.performance_metrics['refresh_rate'] = interval

        # 更新性能指标
        import psutil
        self.performance_metrics['memory_usage'] = psutil.virtual_memory().percent
        self.performance_metrics['cpu_usage'] = psutil.cpu_percent(interval=0.1)

        # 更新性能显示
        if hasattr(self, 'memory_usage_indicator'):
            self.memory_usage_indicator.text = f"内存: {self.performance_metrics['memory_usage']:.1f}%"

        if hasattr(self, 'refresh_rate_indicator'):
            self.refresh_rate_indicator.text = f"刷新: {self.performance_metrics['refresh_rate']:.1f}s"

    def _update_metric_cards(self):
        """更新指标卡片"""
        # 获取监控数据
        cpu_usage = self.performance_metrics['cpu_usage']
        gpu_usage = self.performance_metrics.get('gpu_usage', 0)
        memory_usage = self.performance_metrics['memory_usage']

        # 更新CPU指标
        if 'cpu_value' in self.metrics_cards:
            self.metrics_cards['cpu_value'].text = f"{cpu_usage:.1f}%"
            self.metrics_cards['cpu_progress'].value = cpu_usage / 100

            # 根据使用率设置状态
            if cpu_usage > 80:
                self.metrics_cards['cpu_status_icon'].name = 'warning'
                self.metrics_cards['cpu_status_icon'].color = 'orange'
                self.metrics_cards['cpu_progress'].color = 'red'
            elif cpu_usage > 60:
                self.metrics_cards['cpu_status_icon'].name = 'info'
                self.metrics_cards['cpu_status_icon'].color = 'orange'
                self.metrics_cards['cpu_progress'].color = 'orange'
            else:
                self.metrics_cards['cpu_status_icon'].name = 'check_circle'
                self.metrics_cards['cpu_status_icon'].color = 'light-green'
                self.metrics_cards['cpu_progress'].color = 'white'

        # 更新GPU指标
        if 'gpu_value' in self.metrics_cards:
            self.metrics_cards['gpu_value'].text = f"{gpu_usage:.1f}%"
            self.metrics_cards['gpu_progress'].value = gpu_usage / 100

            # 根据使用率设置状态
            if gpu_usage > 80:
                self.metrics_cards['gpu_status_icon'].name = 'warning'
                self.metrics_cards['gpu_status_icon'].color = 'orange'
                self.metrics_cards['gpu_progress'].color = 'red'
            elif gpu_usage > 60:
                self.metrics_cards['gpu_status_icon'].name = 'info'
                self.metrics_cards['gpu_status_icon'].color = 'orange'
                self.metrics_cards['gpu_progress'].color = 'orange'
            else:
                self.metrics_cards['gpu_status_icon'].name = 'check_circle'
                self.metrics_cards['gpu_status_icon'].color = 'light-green'
                self.metrics_cards['gpu_progress'].color = 'white'

        # 更新内存指标
        if 'memory_value' in self.metrics_cards:
            self.metrics_cards['memory_value'].text = f"{memory_usage:.1f}%"
            self.metrics_cards['memory_progress'].value = memory_usage / 100

            # 根据使用率设置状态
            if memory_usage > 80:
                self.metrics_cards['memory_status_icon'].name = 'warning'
                self.metrics_cards['memory_status_icon'].color = 'orange'
                self.metrics_cards['memory_progress'].color = 'red'
            elif memory_usage > 60:
                self.metrics_cards['memory_status_icon'].name = 'info'
                self.metrics_cards['memory_status_icon'].color = 'orange'
                self.metrics_cards['memory_progress'].color = 'orange'
            else:
                self.metrics_cards['memory_status_icon'].name = 'check_circle'
                self.metrics_cards['memory_status_icon'].color = 'light-green'
                self.metrics_cards['memory_progress'].color = 'white'

    def _update_chart_data(self):
        """更新图表数据"""
        # 获取时间戳
        timestamp = datetime.now().strftime('%H:%M:%S')

        # 添加到历史数据
        if not self.dashboard_data['chart_data']['timestamps']:
            self.dashboard_data['chart_data']['timestamps'] = []
            self.dashboard_data['chart_data']['cpu_history'] = []
            self.dashboard_data['chart_data']['gpu_history'] = []
            self.dashboard_data['chart_data']['memory_history'] = []

        # 添加新数据点
        self.dashboard_data['chart_data']['timestamps'].append(timestamp)
        self.dashboard_data['chart_data']['cpu_history'].append(self.performance_metrics['cpu_usage'])
        self.dashboard_data['chart_data']['gpu_history'].append(self.performance_metrics.get('gpu_usage', 0))
        self.dashboard_data['chart_data']['memory_history'].append(self.performance_metrics['memory_usage'])

        # 保持最近100个数据点
        if len(self.dashboard_data['chart_data']['timestamps']) > 100:
            self.dashboard_data['chart_data']['timestamps'].pop(0)
            self.dashboard_data['chart_data']['cpu_history'].pop(0)
            self.dashboard_data['chart_data']['gpu_history'].pop(0)
            self.dashboard_data['chart_data']['memory_history'].pop(0)

        # 更新图表数据
        ui.run_javascript(f'''
        if (window.chartInstances && window.chartInstances.cpu) {{
            window.chartInstances.cpu.data.labels.push('{timestamp}');
            window.chartInstances.cpu.data.datasets[0].data.push({self.performance_metrics['cpu_usage']});
            window.chartInstances.cpu.update('none');

            if (window.chartInstances.cpu.data.labels.length > 50) {{
                window.chartInstances.cpu.data.labels.shift();
                window.chartInstances.cpu.data.datasets[0].data.shift();
            }}
        }}

        if (window.chartInstances && window.chartInstances.memory) {{
            window.chartInstances.memory.data.labels.push('{timestamp}');
            window.chartInstances.memory.data.datasets[0].data.push({self.performance_metrics['memory_usage']});
            window.chartInstances.memory.update('none');

            if (window.chartInstances.memory.data.labels.length > 50) {{
                window.chartInstances.memory.data.labels.shift();
                window.chartInstances.memory.data.datasets[0].data.shift();
            }}
        }}

        if (window.chartInstances && window.chartInstances.combined) {{
            window.chartInstances.combined.data.labels.push('{timestamp}');
            window.chartInstances.combined.data.datasets[0].data.push({self.performance_metrics['cpu_usage']});
            window.chartInstances.combined.data.datasets[1].data.push({self.performance_metrics['memory_usage']});
            window.chartInstances.combined.update('none');

            if (window.chartInstances.combined.data.labels.length > 50) {{
                window.chartInstances.combined.data.labels.shift();
                window.chartInstances.combined.data.datasets[0].data.shift();
                window.chartInstances.combined.data.datasets[1].data.shift();
            }}
        }}
        ''')

    def _update_alert_data(self):
        """更新告警数据"""
        # 获取活跃告警
        active_alerts = self.alert_manager.get_active_alerts()

        # 更新告警数量
        if hasattr(self, 'alert_stats_critical'):
            critical_count = sum(1 for alert in active_alerts if alert.severity == AlertSeverity.CRITICAL)
            warning_count = sum(1 for alert in active_alerts if alert.severity == AlertSeverity.WARNING)
            info_count = sum(1 for alert in active_alerts if alert.severity == AlertSeverity.INFO)

            self.alert_stats_critical.text = str(critical_count)
            self.alert_stats_warning.text = str(warning_count)
            self.alert_stats_info.text = str(info_count)

            # 更新总计数
            if 'alerts_total_value' in self.metrics_cards:
                self.metrics_cards['alerts_total_value'].text = str(len(active_alerts))

                # 更新状态图标和文本
                if len(active_alerts) == 0:
                    self.metrics_cards['alerts_status_icon'].name = 'info'
                    self.metrics_cards['alerts_status_icon'].color = 'white'
                    ui.tooltip(self.metrics_cards['alerts_status_icon']).content = '无告警'
                elif critical_count > 0:
                    self.metrics_cards['alerts_status_icon'].name = 'priority_high'
                    self.metrics_cards['alerts_status_icon'].color = 'red'
                    ui.tooltip(self.metrics_cards['alerts_status_icon']).content = f'严重告警: {critical_count}'
                elif warning_count > 0:
                    self.metrics_cards['alerts_status_icon'].name = 'warning'
                    self.metrics_cards['alerts_status_icon'].color = 'orange'
                    ui.tooltip(self.metrics_cards['alerts_status_icon']).content = f'警告: {warning_count}'
                else:
                    self.metrics_cards['alerts_status_icon'].name = 'info'
                    self.metrics_cards['alerts_status_icon'].color = 'blue'
                    ui.tooltip(self.metrics_cards['alerts_status_icon']).content = f'信息: {info_count}'

        # 更新告警列表
        if hasattr(self, 'active_alerts_container') and len(active_alerts) != len(self.alert_components):
            self.active_alerts_container.clear()
            self.alert_components = {}

            for i, alert in enumerate(active_alerts):
                # 创建告警卡片
                with self.active_alerts_container:
                    self._create_alert_item(alert, i)

    def _update_system_health(self):
        """更新系统健康状态"""
        # 检查监控状态
        monitor_running = self.monitor.is_running() if hasattr(self.monitor, 'is_running') else False

        if monitor_running:
            self.monitoring_status_label.text = '正在运行'
            self.monitoring_status_label.classes = 'text-body1 text-positive'
            self.health_status_icon.name = 'check_circle'
            self.health_status_icon.color = 'green'
            self.health_status_label.text = '健康'
            self.health_status_label.classes = 'text-h5 text-weight-bold text-green'
        else:
            self.monitoring_status_label.text = '未运行'
            self.monitoring_status_label.classes = 'text-body1 text-negative'
            self.health_status_icon.name = 'error'
            self.health_status_icon.color = 'red'
            self.health_status_label.text = '离线'
            self.health_status_label.classes = 'text-h5 text-weight-bold text-negative'

        # 获取统计数据
        stats = self.monitor.get_stats() if hasattr(self.monitor, 'get_stats') else {}
        self.monitor_stats_label.text = str(len(stats))

        # 获取成功率
        success_rate = stats.get('success_rate', 0) * 100 if 'success_rate' in stats else 0
        self.success_rate_label.text = f"{success_rate:.1f}%"

        # 获取系统信息
        import platform
        system_info = f"{platform.system()} {platform.release()}"
        self.system_info_label.text = system_info

        # 计算运行时长
        start_time = stats.get('start_time') if 'start_time' in stats else datetime.now()
        if isinstance(start_time, str):
            try:
                start_time = datetime.fromisoformat(start_time)
            except ValueError:
                start_time = datetime.now()

        uptime = (datetime.now() - start_time).total_seconds()
        hours, remainder = divmod(int(uptime), 3600)
        minutes, seconds = divmod(remainder, 60)
        self.uptime_label.text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
