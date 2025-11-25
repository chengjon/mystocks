# 核心类和功能

"""
nicegui_monitoring_dashboard_kline.py - 模块化拆分版
原始文件: /opt/claude/mystocks_spec/web/frontend/nicegui_monitoring_dashboard_kline.py
拆分时间: 2025-11-25 14:14:51
"""

class EnhancedKlineMonitoringDashboard:
    """增强版K线监控仪表板 - 使用Klinechart实现专业K线图表"""
    
    def __init__(self):
        """初始化监控仪表板"""
        self.alert_manager = AIAlertManager()
        self.monitor = AIRealtimeMonitor()
        
        # 仪表板数据存储
        self.dashboard_data = {
            'last_update': None,
            'chart_data': {
                'timestamps': [],
                'cpu_history': [],
                'gpu_history': [],
                'memory_history': [],
                'stock_data': {
                    'symbols': ['000001.SZ', '600000.SH', '000002.SZ'],
                    'kline_data': {},
                    'realtime_quotes': {}
                }
            },
            'metrics_summary': {},
            'alert_summary': {},
            'active_alerts': [],
            'system_health': {},
            'kline_config': {
                'chart_type': 'candlestick',
                'timeframe': '1m',
                'theme': 'light',
                'show_volume': True,
                'show_indicators': True
            }
        }
        
        # 图表实例存储
        self.chart_instances = {}
        self.kline_instances = {}
        
        # 性能指标
        self.performance_metrics = {
            'total_updates': 0,
            'avg_response_time': 0.0,
            'peak_cpu_usage': 0.0,
            'peak_gpu_usage': 0.0
        }
        
        # 主题状态
        self.is_dark_theme = False
        
        # 初始化仪表板
        self._initialize_dashboard()
    
    def _initialize_dashboard(self):
        """初始化仪表板界面"""
        logger.info("🚀 启动增强版K线监控仪表板")
        
        # 全局配置
        ui.query('body').style('background-color: #f5f5f5')
        
        # 主题切换按钮
        self._create_theme_toggle()
        
        # 主标题和状态栏
        self._create_header()
        
        # 指标卡片区域
        self._create_metrics_cards()
        
        # K线图表区域 (主要功能)
        self._create_kline_charts()
        
        # 实时性能图表
        self._create_realtime_charts()
        
        # 告警面板
        self._create_alert_panel()
        
        # 控制面板
        self._create_control_panel()
        
        # 浮动操作按钮
        self._create_floating_actions()
        
        # 键盘快捷键
        self._add_keyboard_shortcuts()
        
        # 定时数据更新
        self._setup_auto_refresh()
        
        logger.info("✅ K线监控仪表板初始化完成")
    
    def _create_theme_toggle(self):
        """创建主题切换按钮"""
        with ui.row().classes('theme-toggle items-center q-gutter-sm'):
            self.theme_icon = ui.icon('light_mode', size='24px', color='orange')
            ui.button('切换主题', on_click=self._toggle_theme, color='primary').classes('theme-btn')
    
    def _create_header(self):
        """创建页面头部"""
        with ui.card().classes('w-full q-pa-lg bg-primary text-white dashboard-card'):
            with ui.row().classes('items-center justify-between'):
                with ui.row().classes('items-center q-gutter-md'):
                    ui.icon('monitor', size='32px', color='white')
                    ui.label('MyStocks AI K线监控仪表板').classes('text-h4 text-weight-bold')
                    ui.badge('v2.0', color='orange', text_color='white')
                
                # 系统状态指示器
                with ui.row().classes('items-center q-gutter-md'):
                    self.status_indicator = ui.html('<span class="status-indicator status-normal"></span>')
                    self.status_text = ui.label('系统正常').classes('text-subtitle1')
                    
                    # 更新时间
                    self.update_time = ui.label('').classes('text-caption')
                    self.update_time.set_text(f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def _create_metrics_cards(self):
        """创建指标卡片"""
        with ui.row().classes('q-gutter-md q-pa-md items-stretch'):
            
            # 系统指标卡片
            with ui.card().classes('metric-card dashboard-card flex-grow-1'):
                with ui.column().classes('items-center'):
                    ui.icon('memory', size='32px', color='white')
                    self.metrics_cards['cpu_usage'] = ui.label('0%').classes('text-h4 text-weight-bold')
                    ui.label('CPU使用率').classes('text-caption text-white-7')
            
            with ui.card().classes('metric-card dashboard-card flex-grow-1'):
                with ui.column().classes('items-center'):
                    ui.icon('memory', size='32px', color='white')
                    self.metrics_cards['gpu_usage'] = ui.label('0%').classes('text-h4 text-weight-bold')
                    ui.label('GPU使用率').classes('text-caption text-white-7')
            
            with ui.card().classes('metric-card dashboard-card flex-grow-1'):
                with ui.column().classes('items-center'):
                    ui.icon('storage', size='32px', color='white')
                    self.metrics_cards['memory_usage'] = ui.label('0%').classes('text-h4 text-weight-bold')
                    ui.label('内存使用率').classes('text-caption text-white-7')
            
            # 告警统计卡片
            with ui.card().classes('metric-card dashboard-card flex-grow-1'):
                with ui.row().classes('w-full items-center justify-around'):
                    with ui.column().classes('items-center'):
                        self.metrics_cards['critical_count'] = ui.label('0').classes('text-h6 text-white')
                        ui.label('严重').classes('text-caption text-white-7')
                    with ui.column().classes('items-center'):
                        self.metrics_cards['warning_count'] = ui.label('0').classes('text-h6 text-white')
                        ui.label('警告').classes('text-caption text-white-7')
                    with ui.column().classes('items-center'):
                        self.metrics_cards['info_count'] = ui.label('0').classes('text-h6 text-white')
                        ui.label('信息').classes('text-caption text-white-7')
    
    def _create_kline_charts(self):
        """创建K线图表区域 - 使用Klinechart库"""
        with ui.card().classes('w-full q-pa-lg dashboard-card'):
            with ui.row().classes('items-center justify-between q-mb-md'):
                ui.label('📈 专业K线图表').classes('text-h6 text-weight-bold')
                with ui.row().classes('items-center q-gutter-sm'):
                    ui.icon('timeline', size='20px', color='blue')
                    ui.button('多周期切换', on_click=self._show_timeframe_options, color='blue', size='sm').classes('control-btn')
                    ui.button('指标设置', on_click=self._show_indicator_settings, color='orange', size='sm').classes('control-btn')
                    ui.button('全屏查看', on_click=self._show_fullscreen_kline, color='green', size='sm').classes('control-btn')
            
            # 添加Klinechart和轻量图表库
            self._include_klinechart_libs()
            
            # 股票选择和K线配置
            self._create_kline_controls()
            
            # K线图表容器
            self._create_kline_chart_containers()
    
    def _include_klinechart_libs(self):
        """包含Klinechart和相关库"""
        ui.add_head_html('''
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
        
        <!-- Klinechart K线图表库 - 主要K线库 -->
        <script src="https://cdn.jsdelivr.net/npm/klinechart@7.3.0/dist/klinechart.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/klinechart@7.3.0/dist/klinecharts.min.js"></script>
        
        <!-- Lightweight Charts - 轻量级K线库作为补充 -->
        <script src="https://cdn.jsdelivr.net/npm/lightweight-charts@4.1.1/dist/lightweight-charts.standalone.production.js"></script>
        
        <!-- TradingView Charting Library (可选) -->
        <script src="https://s3.tradingview.com/tv.js"></script>
        
        <!-- 通用数据可视化库 -->
        <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/dist/chart.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcode-generator/1.4.4/qrcode.min.js"></script>
        
        <style>
        :root {
            --primary-color: #2196F3;
            --secondary-color: #FF9800;
            --success-color: #4CAF50;
            --danger-color: #F44336;
            --warning-color: #FF9800;
            --info-color: #00BCD4;
        }
        body { font-family: 'Roboto', sans-serif; }
        
        /* K线图表容器样式 */
        .kline-chart-container {
            position: relative;
            height: 600px;
            width: 100%;
            margin: 20px 0;
            border-radius: 8px;
            overflow: hidden;
            background: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .kline-chart-header {
            padding: 15px;
            background: linear-gradient(135deg, var(--primary-color), var(--info-color));
            color: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .kline-controls {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .kline-timeframe-btn {
            padding: 5px 12px;
            border: 1px solid rgba(255,255,255,0.3);
            background: transparent;
            color: white;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .kline-timeframe-btn:hover, .kline-timeframe-btn.active {
            background: rgba(255,255,255,0.2);
        }
        
        .chart-loading-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255, 255, 255, 0.9);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        
        .chart-error {
            border: 2px solid var(--danger-color);
            border-radius: 4px;
            background-color: #ffebee;
        }
        
        .control-btn {
            margin: 0 5px;
            transition: all 0.3s ease;
        }
        
        .control-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        </style>
        ''')
    
    def _create_kline_controls(self):
        """创建K线控制面板"""
        with ui.row().classes('kline-controls w-full q-mb-md'):
            # 股票选择
            self.symbol_selector = ui.select(
                options=['000001.SZ', '600000.SH', '000002.SZ', '600036.SH', '000858.SZ'],
                value='000001.SZ',
                label='选择股票',
                on_change=self._on_symbol_change
            ).classes('flex-grow-1')
            
            # 周期选择
            with ui.row().classes('q-gutter-xs'):
                ui.label('周期:').classes('text-subtitle2')
                self.timeframe_buttons = {}
                timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w']
                for tf in timeframes:
                    btn = ui.button(tf, 
                                   on_click=lambda tf=tf: self._change_timeframe(tf),
                                   color='transparent',
                                   size='sm').classes('kline-timeframe-btn')
                    if tf == '1m':
                        btn.classes('kline-timeframe-btn active')
                    self.timeframe_buttons[tf] = btn
            
            # 指标控制
            with ui.row().classes('q-gutter-xs'):
                ui.label('指标:').classes('text-subtitle2')
                self.indicator_checkboxes = {
                    'ma': ui.checkbox('MA', value=True, on_change=self._toggle_indicators),
                    'rsi': ui.checkbox('RSI', value=False, on_change=self._toggle_indicators),
                    'macd': ui.checkbox('MACD', value=False, on_change=self._toggle_indicators)
                }
    
    def _create_kline_chart_containers(self):
        """创建K线图表容器"""
        # 主要K线图表
        with ui.card().classes('kline-chart-container'):
            self.kline_chart_header = ui.html('''
            <div class="kline-chart-header">
                <div>
                    <h4 id="kline-symbol">000001.SZ - 平安银行</h4>
                    <span id="kline-price">价格: --</span>
                    <span id="kline-change" style="margin-left: 15px;">涨跌幅: --</span>
                </div>
                <div>
                    <i class="fas fa-chart-line"></i>
                    <span style="margin-left: 8px;">实时K线图</span>
                </div>
            </div>
            ''')
            
            # Klinechart主图表容器
            self.kline_main_container = ui.html('''
            <div id="kline-main-chart" class="chart-container">
                <div class="chart-loading-overlay" id="kline-loading">
                    <div class="text-center">
                        <i class="fas fa-spinner fa-spin fa-2x text-primary"></i>
                        <div class="mt-2">加载K线数据中...</div>
                    </div>
                </div>
            </div>
            ''')
            
            # 初始化Klinechart实例
            self._initialize_klinecharts()
    
    def _initialize_klinecharts(self):
        """初始化Klinechart图表实例"""
        ui.run_javascript('''
        // 初始化Klinechart实例
        function initializeKlineCharts() {
            try {
                // 检查Klinechart库是否加载
                if (typeof window.klinecharts === 'undefined') {
                    console.warn('Klinechart库未加载，使用轻量级图表库');
                    initializeLightweightCharts();
                    return;
                }
                
                // 创建主K线图表实例
                window.klineChart = new klinecharts.KLineChart('kline-main-chart');
                
                // 配置图表参数
                window.klineChart.setStyles({
                    grid: {
                        horizontal: { display: true, color: '#e0e0e0' },
                        vertical: { display: true, color: '#e0e0e0' }
                    },
                    candle: {
                        type: 'candle_solid',
                        bar: {
                            upColor: '#26a69a',
                            downColor: '#ef5350',
                            noChangeColor: '#999999'
                        }
                    },
                    xAxis: {
                        tickText: { color: '#768492' },
                        tickLine: { color: '#768492' }
                    },
                    yAxis: {
                        tickText: { color: '#768492' },
                        tickLine: { color: '#768492' }
                    }
                });
                
                console.log('✅ Klinechart图表初始化成功');
                
                // 隐藏加载提示
                document.getElementById('kline-loading').style.display = 'none';
                
                // 加载示例数据
                loadSampleKlineData();
                
            } catch (error) {
                console.error('❌ Klinechart初始化失败:', error);
                // 降级到轻量级图表
                initializeLightweightCharts();
            }
        }
        
        // 初始化轻量级图表（备用方案）
        function initializeLightweightCharts() {
            try {
                const chart = LightweightCharts.createChart('kline-main-chart', {
                    layout: {
                        background: { color: '#ffffff' },
                        textColor: '#333',
                    },
                    grid: {
                        vertLines: { color: '#e0e0e0' },
                        horzLines: { color: '#e0e0e0' },
                    },
                    width: document.getElementById('kline-main-chart').clientWidth,
                    height: 500,
                });
                
                window.lightweightChart = chart;
                
                // 创建K线系列
                window.candlestickSeries = chart.addCandlestickSeries({
                    upColor: '#26a69a',
                    downColor: '#ef5350',
                    borderDownColor: '#ef5350',
                    borderUpColor: '#26a69a',
                    wickDownColor: '#ef5350',
                    wickUpColor: '#26a69a',
                });
                
                // 隐藏加载提示
                document.getElementById('kline-loading').style.display = 'none';
                
                // 加载示例数据
                loadSampleKlineData();
                
                console.log('✅ 轻量级图表初始化成功');
                
            } catch (error) {
                console.error('❌ 轻量级图表初始化失败:', error);
                showChartError();
            }
        }
        
        // 加载示例K线数据
        function loadSampleKlineData() {
            const now = Date.now();
            const data = [];
            
            // 生成模拟的K线数据
            for (let i = 100; i >= 0; i--) {
                const timestamp = now - (i * 60000); // 每分钟一个数据点
                const basePrice = 10 + Math.sin(i * 0.1) * 2;
                const volatility = Math.random() * 0.5;
                
                data.push({
                    timestamp: timestamp,
                    open: basePrice + (Math.random() - 0.5) * volatility,
                    high: basePrice + Math.random() * volatility + volatility,
                    low: basePrice - Math.random() * volatility - volatility,
                    close: basePrice + (Math.random() - 0.5) * volatility,
                    volume: Math.random() * 1000000
                });
            }
            
            // 使用Klinechart显示数据
            if (window.klineChart) {
                try {
                    window.klineChart.createDataSource('candle', data);
                    window.klineChart.applyNewData(data);
                } catch (error) {
                    console.error('Klinechart数据加载失败:', error);
                }
            }
            
            // 使用轻量级图表显示数据
            if (window.candlestickSeries) {
                window.candlestickSeries.setData(data);
            }
            
            // 更新股票信息显示
            updateStockInfo(data[data.length - 1]);
        }
        
        // 更新股票信息显示
        function updateStockInfo(latestData) {
            if (!latestData) return;
            
            const change = ((latestData.close - latestData.open) / latestData.open * 100).toFixed(2);
            const changeColor = change >= 0 ? 'text-success' : 'text-danger';
            
            document.getElementById('kline-price').textContent = `价格: ${latestData.close.toFixed(2)}`;
            document.getElementById('kline-change').innerHTML = `涨跌幅: <span class="${changeColor}">${change}%</span>`;
        }
        
        // 显示图表错误
        function showChartError() {
            document.getElementById('kline-main-chart').innerHTML = `
                <div class="chart-loading-overlay">
                    <div class="text-center text-danger">
                        <i class="fas fa-exclamation-triangle fa-2x"></i>
                        <div class="mt-2">图表加载失败</div>
                        <small>请检查网络连接和库加载状态</small>
                    </div>
                </div>
            `;
        }
        
        // 页面加载完成后初始化图表
        document.addEventListener('DOMContentLoaded', function() {
            // 延迟初始化以确保所有库都已加载
            setTimeout(initializeKlineCharts, 1000);
        });
        
        // 窗口大小改变时重新调整图表
        window.addEventListener('resize', function() {
            if (window.klineChart) {
                window.klineChart.resize();
            }
            if (window.lightweightChart) {
                window.lightweightChart.resize();
            }
        });
        ''')
    
    def _create_realtime_charts(self):
        """创建实时性能图表"""
        with ui.card().classes('w-full q-pa-lg dashboard-card'):
            with ui.row().classes('items-center justify-between q-mb-md'):
                ui.label('📊 实时性能监控').classes('text-h6 text-weight-bold')
                with ui.row().classes('items-center q-gutter-sm'):
                    ui.icon('fullscreen', size='20px', color='blue')
                    ui.button('全屏视图', on_click=self._show_fullscreen_charts, color='blue', size='sm').classes('control-btn')
            
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
                ui.label('📈 综合性能趋势').classes('text-subtitle1 text-weight-bold q-mb-md')
                self.combined_chart_canvas = ui.html('<canvas id="combinedChart" width="800" height="200"></canvas>')
    
    def _create_chart_card(self, chart_id: str, title: str, icon: str, color: str):
        """创建单个图表卡片"""
        with ui.card().classes('chart-container flex-grow-1'):
            # 图表标题
            with ui.row().classes('items-center justify-between q-mb-sm'):
                ui.label(title).classes('text-subtitle1 text-weight-medium')
                with ui.row().classes('items-center q-gutter-xs'):
                    ui.icon(icon, size='16px', color='grey-6')
                    ui.button('全屏', on_click=lambda: self._show_single_chart(chart_id), 
                             color='transparent', size='sm').props('flat round')
            
            # 图表容器
            canvas_id = f'{chart_id}Chart'
            self.chart_instances[chart_id] = ui.html(f'<canvas id="{canvas_id}" width="300" height="200"></canvas>')
            
            # 状态指示器
            with ui.row().classes('items-center justify-center q-mt-sm'):
                self.chart_status[chart_id] = ui.html('<i class="fas fa-circle text-success"></i>')
    
    def _initialize_performance_monitoring(self):
        """初始化性能监控"""
        ui.run_javascript('''
        // 性能监控图表初始化
        function initializePerformanceCharts() {
            const ctx = document.getElementById('combinedChart');
            if (!ctx) return;
            
            window.combinedChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: 'CPU使用率 (%)',
                            data: [],
                            borderColor: '#3f51b5',
                            backgroundColor: 'rgba(63, 81, 181, 0.1)',
                            tension: 0.4,
                            fill: true
                        },
                        {
                            label: 'GPU使用率 (%)',
                            data: [],
                            borderColor: '#9c27b0',
                            backgroundColor: 'rgba(156, 39, 176, 0.1)',
                            tension: 0.4,
                            fill: true
                        },
                        {
                            label: '内存使用率 (%)',
                            data: [],
                            borderColor: '#4caf50',
                            backgroundColor: 'rgba(76, 175, 80, 0.1)',
                            tension: 0.4,
                            fill: true
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                        }
                    },
                    interaction: {
                        mode: 'nearest',
                        axis: 'x',
                        intersect: false
                    }
                }
            });
        }
        
        // 页面加载时初始化
        setTimeout(initializePerformanceCharts, 500);
        ''')
    
    def _create_alert_panel(self):
        """创建告警面板"""
        with ui.card().classes('w-full q-pa-lg dashboard-card'):
            with ui.row().classes('items-center justify-between q-mb-md'):
                ui.label('🚨 实时告警').classes('text-h6 text-weight-bold')
                with ui.row().classes('items-center q-gutter-sm'):
                    ui.button('清除全部', on_click=self._clear_all_alerts, color='red', size='sm').classes('control-btn')
                    ui.button('设置', on_click=self._show_alert_settings, color='orange', size='sm').classes('control-btn')
            
            # 告警列表
            self.alert_list = ui.column().classes('q-gutter-sm')
    
    def _create_control_panel(self):
        """创建控制面板"""
        with ui.card().classes('w-full q-pa-lg dashboard-card'):
            with ui.row().classes('items-center justify-between q-mb-md'):
                ui.label('⚙️ 控制面板').classes('text-h6 text-weight-bold')
            
            with ui.row().classes('q-gutter-md'):
                ui.button('📊 导出数据', on_click=self._export_dashboard_data, color='primary').classes('control-btn')
                ui.button('📱 分享仪表板', on_click=self._share_dashboard, color='info').classes('control-btn')
                ui.button('🔄 刷新数据', on_click=self._manual_refresh, color='success').classes('control-btn')
                ui.button('⏸️ 暂停更新', on_click=self._toggle_auto_refresh, color='warning').classes('control-btn')
    
    def _create_floating_actions(self):
        """创建浮动操作按钮"""
        with ui.row().classes('floating-action'):
            ui.button('📈', on_click=self._scroll_to_kline, color='transparent').classes('fab-btn')
        
        # 浮动按钮样式
        ui.add_head_html('''
        <style>
        .floating-action {
            position: fixed;
            bottom: 30px;
            right: 30px;
            z-index: 1000;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            background: var(--primary-color);
            color: white;
            border: none;
            box-shadow: 0 10px 15px rgba(0,0,0,0.1);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
        }
        .floating-action:hover {
            transform: scale(1.1);
            background: var(--info-color);
        }
        .fab-btn {
            font-size: 24px !important;
            color: white !important;
        }
        </style>
        ''')
    
    # ==================== K线图表相关方法 ====================
    
    def _on_symbol_change(self, event):
        """股票代码变更事件"""
        selected_symbol = event.value
        logger.info(f"🔄 切换到股票: {selected_symbol}")
        
        # 更新图表标题
        ui.run_javascript(f'''
        document.getElementById('kline-symbol').textContent = '{selected_symbol} - 股票详情';
        ''')
        
        # 重新加载K线数据
        self._load_kline_data(selected_symbol)
    
    def _change_timeframe(self, timeframe: str):
        """切换K线周期"""
        logger.info(f"🔄 切换K线周期: {timeframe}")
        
        # 更新按钮样式
        for tf, btn in self.timeframe_buttons.items():
            if tf == timeframe:
                btn.classes('kline-timeframe-btn active')
            else:
                btn.classes('kline-timeframe-btn')
        
        # 更新图表
        ui.run_javascript(f'''
        if (window.klineChart) {{
            // 重新配置时间轴
            window.klineChart.createDataSource('xAxis', {{ timeScale: {{ timeVisible: true, secondsVisible: false }} }});
        }}
        if (window.lightweightChart) {{
            window.lightweightChart.timeScale().fitContent();
        }}
        ''')
        
        # 重新加载数据
        self._load_kline_data(self.symbol_selector.value, timeframe)
    
    def _toggle_indicators(self, event):
        """切换技术指标显示"""
        indicator_name = None
        for name, checkbox in self.indicator_checkboxes.items():
            if checkbox is event.sender:
                indicator_name = name
                break
        
        if indicator_name:
            is_checked = event.value
            logger.info(f"{'显示' if is_checked else '隐藏'} {indicator_name.upper()} 指标")
            
            ui.run_javascript(f'''
            // 这里可以添加指标切换逻辑
            console.log('切换指标: {indicator_name}', {is_checked});
            ''')
    
    def _load_kline_data(self, symbol: str, timeframe: str = '1m'):
        """加载K线数据"""
        logger.info(f"📊 加载K线数据: {symbol} ({timeframe})")
        
        # 显示加载提示
        ui.run_javascript('''
        document.getElementById('kline-loading').style.display = 'flex';
        ''')
        
        # 模拟数据加载延迟
        ui.run_javascript('''
        setTimeout(() => {
            // 重新生成随机数据
            const now = Date.now();
            const data = [];
            const dataPoints = timeframe === '1m' ? 100 : timeframe === '5m' ? 288 : timeframe === '1d' ? 365 : 100;
            const interval = timeframe === '1m' ? 60000 : timeframe === '5m' ? 300000 : timeframe === '1h' ? 3600000 : 86400000;
            
            for (let i = dataPoints; i >= 0; i--) {{
                const timestamp = now - (i * interval);
                const basePrice = 10 + Math.sin(i * 0.1) * 2;
                const volatility = Math.random() * 0.5;
                
                data.push({{
                    timestamp: timestamp,
                    open: basePrice + (Math.random() - 0.5) * volatility,
                    high: basePrice + Math.random() * volatility + volatility,
                    low: basePrice - Math.random() * volatility - volatility,
                    close: basePrice + (Math.random() - 0.5) * volatility,
                    volume: Math.random() * 1000000
                }});
            }}
            
            // 更新Klinechart数据
            if (window.klineChart) {{
                window.klineChart.applyNewData(data);
            }}
            
            // 更新轻量级图表数据
            if (window.candlestickSeries) {{
                window.candlestickSeries.setData(data);
            }}
            
            // 更新股票信息
            if (data.length > 0) {{
                updateStockInfo(data[data.length - 1]);
            }}
            
            // 隐藏加载提示
            document.getElementById('kline-loading').style.display = 'none';
        }}, 500);
        ''')
    
    def _show_timeframe_options(self):
        """显示周期选项"""
        with ui.dialog() as dialog, ui.card():
            ui.label('选择K线周期').classes('text-h6 text-weight-bold q-mb-md')
            
            timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w', '1M']
            for tf in timeframes:
                ui.button(tf, on_click=lambda tf=tf: [self._change_timeframe(tf), dialog.close()]).classes('q-ma-xs')
    
    def _show_indicator_settings(self):
        """显示指标设置"""
        with ui.dialog() as dialog, ui.card():
            ui.label('技术指标设置').classes('text-h6 text-weight-bold q-mb-md')
            
            with ui.column().classes('q-gutter-md'):
                with ui.row().classes('items-center'):
                    ui.checkbox('显示移动平均线 (MA)', value=True)
                    ui.select(options=[5, 10, 20, 60], value=20).classes('w-20')
                
                with ui.row().classes('items-center'):
                    ui.checkbox('显示RSI', value=False)
                    ui.select(options=[6, 12, 24], value=12).classes('w-20')
                
                with ui.row().classes('items-center'):
                    ui.checkbox('显示MACD', value=False)
                    ui.select(options=[12, 26], value=[12, 26]).classes('w-20')
            
            with ui.row().classes('q-mt-lg justify-end'):
                ui.button('取消', on_click=dialog.close).classes('q-mr-sm')
                ui.button('应用', on_click=dialog.close, color='primary')
    
    def _show_fullscreen_kline(self):
        """全屏显示K线图表"""
        with ui.dialog() as dialog, ui.card().classes('full-screen-dialog'):
            ui.label('📈 全屏K线图表').classes('text-h6 text-weight-bold q-mb-md')
            
            # 全屏K线容器
            fullscreen_kline = ui.html('''
            <div id="fullscreen-kline-chart" style="height: 70vh; width: 100%;"></div>
            ''')
            
            with ui.row().classes('justify-end q-mt-md'):
                ui.button('关闭', on_click=dialog.close, color='primary')
            
            # 初始化全屏图表
            ui.run_javascript('''
            const container = document.getElementById('fullscreen-kline-chart');
            
            // 创建全屏图表实例
            const fullscreenChart = klinecharts.KLineChart(container);
            
            // 加载数据（复用主图表数据）
            if (window.klineChart) {{
                try {{
                    const data = window.klineChart.getDataSource('candle').getData();
                    fullscreenChart.applyNewData(data);
                }} catch (error) {{
                    console.log('使用示例数据');
                }}
            }}
            
            container.addEventListener('dblclick', () => {{
                container.requestFullscreen().catch(err => {{
                    console.log('无法进入全屏模式:', err);
                }});
            }});
            ''')
    
    # ==================== 数据更新方法 ====================
    
    async def _update_dashboard_data(self):
        """更新仪表板数据"""
        try:
            # 获取监控数据
            metrics_summary = await self.monitor.get_metrics_summary()
            
            # 获取告警摘要
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
            
            # 更新UI显示
            self._update_ui_display()
            
            # 更新图表数据
            self._update_chart_data(metrics_summary)
            
            # 更新K线数据
            self._update_kline_realtime_data()
            
            logger.info(f"✅ 仪表板数据更新完成 (第{self.performance_metrics['total_updates']}次)")
            
        except Exception as e:
            logger.error(f"❌ 更新仪表板数据失败: {e}")
    
    def _update_ui_display(self):
        """更新UI显示"""
        try:
            current_metrics = self.dashboard_data['metrics_summary'].get('current_metrics', {})
            
            # 更新指标卡片
            self.metrics_cards['cpu_usage'].set_text(current_metrics.get('cpu_usage', '0%'))
            self.metrics_cards['gpu_usage'].set_text(current_metrics.get('gpu_utilization', '0%'))
            self.metrics_cards['memory_usage'].set_text(current_metrics.get('memory_usage', '0%'))
            
            # 更新告警统计
            alert_summary = self.dashboard_data['alert_summary']
            self.metrics_cards['critical_count'].set_text(str(alert_summary.get('critical_count', 0)))
            self.metrics_cards['warning_count'].set_text(str(alert_summary.get('warning_count', 0)))
            self.metrics_cards['info_count'].set_text(str(alert_summary.get('info_count', 0)))
            
            # 更新系统状态
            system_health = self.dashboard_data.get('system_health', {})
            if system_health.get('overall_status') == 'healthy':
                self.status_text.set_text('系统正常')
            else:
                self.status_text.set_text('需要关注')
            
            # 更新时间显示
            self.update_time.set_text(f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            logger.error(f"❌ 更新UI显示失败: {e}")
    
    def _update_chart_data(self, metrics_summary):
        """更新图表数据"""
        try:
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
                
                # 更新图表
                self._update_chartjs_data(cpu_value, gpu_value, memory_value, timestamp)
                
                # 更新性能指标
                self._update_performance_metrics(current_metrics)
            
        except Exception as e:
            logger.error(f"❌ 更新图表数据失败: {e}")
    
    def _update_kline_realtime_data(self):
        """更新K线实时数据"""
        try:
            # 模拟实时价格更新
            ui.run_javascript('''
            // 模拟实时数据更新
            if (window.klineChart || window.candlestickSeries) {{
                const lastTime = Date.now();
                const lastData = {{
                    timestamp: lastTime,
                    open: 10 + Math.random() * 2,
                    high: 11 + Math.random() * 2,
                    low: 9 + Math.random() * 2,
                    close: 10 + Math.random() * 2,
                    volume: Math.random() * 1000000
                }};
                
                // 更新Klinechart
                if (window.klineChart) {{
                    try {{
                        window.klineChart.createDataSource('candle').pushData([lastData]);
                    }} catch (error) {{
                        console.log('Klinechart实时更新失败:', error);
                    }}
                }}
                
                // 更新轻量级图表
                if (window.candlestickSeries) {{
                    window.candlestickSeries.update(lastData);
                }}
                
                // 更新价格显示
                updateStockInfo(lastData);
            }}
            ''')
            
        except Exception as e:
            logger.error(f"❌ 更新K线实时数据失败: {e}")
    
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
                
                // 保持数据点数量
                const maxPoints = 20;
                if (window.combinedChart.data.labels.length > maxPoints) {{
                    window.combinedChart.data.labels.shift();
                    window.combinedChart.data.datasets.forEach(dataset => {{
                        dataset.data.shift();
                    }});
                }}
                
                window.combinedChart.update('none');
            }}
            ''')
            
        except Exception as e:
            logger.error(f"❌ 更新Chart.js数据失败: {e}")
    
    def _update_performance_metrics(self, current_metrics):
        """更新性能指标"""
        try:
            cpu_usage = float(current_metrics.get('cpu_usage', '0%').replace('%', ''))
            gpu_usage = float(current_metrics.get('gpu_utilization', '0%').replace('%', ''))
            
            # 更新峰值指标
            self.performance_metrics['peak_cpu_usage'] = max(self.performance_metrics['peak_cpu_usage'], cpu_usage)
            self.performance_metrics['peak_gpu_usage'] = max(self.performance_metrics['peak_gpu_usage'], gpu_usage)
            
            # 计算平均响应时间
            self.performance_metrics['total_updates'] += 1
            
        except Exception as e:
            logger.error(f"❌ 更新性能指标失败: {e}")
    
    # ==================== 交互功能方法 ====================
    
    def _toggle_theme(self):
        """切换主题"""
        self.is_dark_theme = not self.is_dark_theme
        
        if self.is_dark_theme:
            self.theme_icon.set_name('dark_mode')
            theme_color = '#121212'
            text_color = '#ffffff'
        else:
            self.theme_icon.set_name('light_mode')
            theme_color = '#ffffff'
            text_color = '#333333'
        
        ui.run_javascript(f'''
        document.body.style.backgroundColor = '{theme_color}';
        document.body.style.color = '{text_color}';
        ''')
        
        logger.info(f"🔄 切换到{'深色' if self.is_dark_theme else '浅色'}主题")
    
    def _export_dashboard_data(self):
        """导出仪表板数据"""
        try:
            # 生成CSV格式数据
            csv_data = []
            for i, timestamp in enumerate(self.dashboard_data['chart_data']['timestamps']):
                csv_data.append({
                    '时间戳': timestamp,
                    'CPU使用率': self.dashboard_data['chart_data']['cpu_history'][i] if i < len(self.dashboard_data['chart_data']['cpu_history']) else '0',
                    'GPU使用率': self.dashboard_data['chart_data']['gpu_history'][i] if i < len(self.dashboard_data['chart_data']['gpu_history']) else '0',
                    '内存使用率': self.dashboard_data['chart_data']['memory_history'][i] if i < len(self.dashboard_data['chart_data']['memory_history']) else '0'
                })
            
            # 保存为CSV文件
            timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            csv_filename = f'/tmp/mystocks_dashboard_{timestamp_str}.csv'
            
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['时间戳', 'CPU使用率', 'GPU使用率', '内存使用率']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)
            
            # 显示下载链接
            ui.notify(f'✅ 数据已导出到: {csv_filename}', type='success')
            logger.info(f"📊 仪表板数据导出完成: {csv_filename}")
            
        except Exception as e:
            logger.error(f"❌ 导出数据失败: {e}")
            ui.notify(f'❌ 导出失败: {e}', type='negative')
    
    def _share_dashboard(self):
        """分享仪表板"""
        try:
            # 生成分享URL
            share_url = f"http://localhost:{nicegui.globals.app.port if hasattr(nicegui.globals.app, 'port') else 8080}/?dashboard={self.dashboard_data['last_update']}"
            
            ui.run_javascript(f'''
            // 复制分享链接到剪贴板
            navigator.clipboard.writeText('{share_url}').then(() => {{
                alert('✅ 分享链接已复制到剪贴板');
            }}).catch(() => {{
                prompt('请复制以下链接:', '{share_url}');
            }});
            ''')
            
            logger.info(f"📱 生成分享链接: {share_url}")
            
        except Exception as e:
            logger.error(f"❌ 生成分享链接失败: {e}")
    
    def _manual_refresh(self):
        """手动刷新数据"""
        ui.notify('🔄 正在刷新数据...', type='info')
        
        # 立即更新数据
        asyncio.create_task(self._update_dashboard_data())
        
        logger.info("🔄 手动刷新触发")
    
    def _toggle_auto_refresh(self):
        """切换自动刷新"""
        if hasattr(self, '_auto_refresh_enabled'):
            self._auto_refresh_enabled = not self._auto_refresh_enabled
        else:
            self._auto_refresh_enabled = False
        
        status = "开启" if self._auto_refresh_enabled else "关闭"
        ui.notify(f"🔄 自动刷新已{status}", type='info')
        
        logger.info(f"🔄 自动刷新{status}")
    
    def _scroll_to_kline(self):
        """滚动到K线图表区域"""
        ui.run_javascript('''
        document.querySelector('.kline-chart-container').scrollIntoView({ behavior: 'smooth' });
        ''')
    
    def _show_fullscreen_charts(self):
        """显示全屏图表"""
        with ui.dialog() as dialog, ui.card().classes('full-screen-dialog'):
            ui.label('📊 全屏性能图表').classes('text-h6 text-weight-bold q-mb-md')
            
            # 全屏图表容器
            fullscreen_canvas = ui.html('<canvas id="fullscreenChart" width="800" height="600"></canvas>')
            
            with ui.row().classes('justify-end q-mt-md'):
                ui.button('关闭', on_click=dialog.close, color='primary')
            
            # 创建全屏图表
            ui.run_javascript('''
            const ctx = document.getElementById('fullscreenChart');
            if (ctx) {
                new Chart(ctx, {
                    type: 'line',
                    data: window.combinedChart ? window.combinedChart.data : {
                        labels: [],
                        datasets: []
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: { beginAtZero: true, max: 100 }
                        }
                    }
                });
            }
            ''')
    
    def _show_single_chart(self, chart_id: str):
        """显示单个图表"""
        with ui.dialog() as dialog, ui.card().classes('chart-dialog'):
            title_map = {
                'cpu': 'CPU使用率图表',
                'gpu': 'GPU使用率图表',
                'memory': '内存使用率图表'
            }
            
            ui.label(title_map.get(chart_id, f'{chart_id}图表')).classes('text-h6 text-weight-bold q-mb-md')
            
            # 单个图表容器
            canvas_id = f'single{chart_id.title()}Chart'
            ui.html(f'<canvas id="{canvas_id}" width="600" height="400"></canvas>')
            
            with ui.row().classes('justify-end q-mt-md'):
                ui.button('关闭', on_click=dialog.close, color='primary')
            
            # 创建单图表
            ui.run_javascript(f'''
            const ctx = document.getElementById('{canvas_id}');
            if (ctx && window.chartInstances.{chart_id}) {{
                new Chart(ctx, window.chartInstances.{chart_id}.config);
            }}
            ''')
    
    def _clear_all_alerts(self):
        """清除所有告警"""
        self.alert_manager.clear_all_alerts()
        ui.notify('✅ 所有告警已清除', type='success')
        logger.info("🧹 所有告警已清除")
    
    def _show_alert_settings(self):
        """显示告警设置"""
        with ui.dialog() as dialog, ui.card():
            ui.label('告警设置').classes('text-h6 text-weight-bold q-mb-md')
            
            with ui.column().classes('q-gutter-md'):
                ui.checkbox('启用邮件告警', value=True)
                ui.checkbox('启用声音告警', value=False)
                ui.checkbox('启用浏览器通知', value=True)
                
                ui.label('告警阈值设置').classes('text-subtitle1')
                ui.slider(min=0, max=100, value=80, step=5).props('label-always')
                ui.label('CPU使用率阈值 (%)')
                
                ui.slider(min=0, max=100, value=90, step=5).props('label-always')
                ui.label('GPU使用率阈值 (%)')
            
            with ui.row().classes('q-mt-lg justify-end'):
                ui.button('取消', on_click=dialog.close).classes('q-mr-sm')
                ui.button('保存', on_click=dialog.close, color='primary')
    
    def _add_keyboard_shortcuts(self):
        """添加键盘快捷键"""
        ui.run_javascript('''
        document.addEventListener('keydown', function(event) {
            // Ctrl+R: 刷新数据
            if (event.ctrlKey && event.key === 'r') {
                event.preventDefault();
                // 触发刷新按钮点击事件
                window.location.reload();
            }
            
            // Ctrl+S: 导出数据
            if (event.ctrlKey && event.key === 's') {
                event.preventDefault();
                // 这里可以添加导出功能
                console.log('快捷键: Ctrl+S - 导出数据');
            }
            
            // F11: 切换全屏
            if (event.key === 'F11') {
                event.preventDefault();
                if (!document.fullscreenElement) {
                    document.documentElement.requestFullscreen();
                } else {
                    document.exitFullscreen();
                }
            }
            
            // Space: 暂停/恢复自动更新
            if (event.key === ' ' && event.target.tagName !== 'INPUT') {
                event.preventDefault();
                console.log('快捷键: Space - 暂停/恢复更新');
            }
            
            // Esc: 关闭对话框
            if (event.key === 'Escape') {
                // 关闭所有打开的对话框
                const dialogs = document.querySelectorAll('[role="dialog"]');
                dialogs.forEach(dialog => dialog.close());
            }
        });
        ''')
    
    def _setup_auto_refresh(self):
        """设置自动刷新"""
        async def auto_update():
            while True:
                try:
                    await asyncio.sleep(self._get_adaptive_interval())
                    if not hasattr(self, '_auto_refresh_enabled') or self._auto_refresh_enabled:
                        await self._update_dashboard_data()
                except Exception as e:
                    logger.error(f"❌ 自动刷新失败: {e}")
                    await asyncio.sleep(10)  # 错误时等待10秒再重试
        
        # 启动自动刷新任务
        asyncio.create_task(auto_update())
        logger.info("🔄 自动刷新任务已启动")
    
    def _get_adaptive_interval(self) -> int:
        """获取自适应刷新间隔"""
        # 根据系统负载动态调整刷新频率
        cpu_usage = float(self.dashboard_data['metrics_summary'].get('current_metrics', {}).get('cpu_usage', '0%').replace('%', ''))
        
        if cpu_usage > 80:
            return 10  # 高负载时降低刷新频率
        elif cpu_usage > 50:
            return 5   # 中等负载时保持正常刷新
        else:
            return 3   # 低负载时可以提高刷新频率
    
    def _show_dashboard_report(self):
        """显示仪表板报告"""
        try:
            # 生成报告数据
            report_data = {
                '仪表板': 'MyStocks AI K线监控仪表板',
                '版本': 'v2.0 (Klinechart版本)',
                '最后更新': self.dashboard_data['last_update'],
                '总更新次数': self.performance_metrics['total_updates'],
                '峰值CPU使用率': f"{self.performance_metrics['peak_cpu_usage']:.1f}%",
                '峰值GPU使用率': f"{self.performance_metrics['peak_gpu_usage']:.1f}%",
                '当前主题': '深色' if self.is_dark_theme else '浅色',
                '活跃告警数': len(self.dashboard_data['active_alerts']),
                '图表数据点数': len(self.dashboard_data['chart_data']['timestamps'])
            }
            
            # 显示报告对话框
            with ui.dialog() as dialog, ui.card().classes('q-pa-lg'):
                ui.label('📊 仪表板报告').classes('text-h6 text-weight-bold q-mb-md')
                
                with ui.column().classes('q-gutter-sm'):
                    for key, value in report_data.items():
                        ui.label(f'• {key}: {value}')
                
                with ui.row().classes('q-mt-lg justify-end'):
                    ui.button('关闭', on_click=dialog.close, color='primary')
            
            logger.info("📊 显示仪表板报告")
            
        except Exception as e:
            logger.error(f"❌ 显示报告失败: {e}")


# 注意：此文件是从原始文件模块化拆分而来，保持向后兼容性
# 原始功能仍可通过导入此文件和原始类名使用
