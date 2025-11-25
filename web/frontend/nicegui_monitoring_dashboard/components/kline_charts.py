# K线图表相关功能


K线图表相关功能


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
    


def create_kline_dashboard():
    """创建K线监控仪表板实例"""
    try:
        logger.info("🚀 启动MyStocks AI K线监控仪表板")
        
        # 创建仪表板实例
        dashboard = EnhancedKlineMonitoringDashboard()
        
        # 设置页面标题和图标
        ui.title("MyStocks AI K线监控仪表板")
        ui.icon("monitor")
        
        return dashboard
        
    except Exception as e:
        logger.error(f"❌ 创建K线监控仪表板失败: {e}")
        raise

