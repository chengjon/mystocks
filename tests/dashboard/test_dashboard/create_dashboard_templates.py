#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试仪表盘

提供实时测试监控、可视化界面和交互式控制面板
"""

from datetime import datetime, timedelta
from pathlib import Path


def create_dashboard_templates():
    """创建HTML模板"""
    template_dir = Path(__file__).parent / "templates"
    template_dir.mkdir(exist_ok=True)

    dashboard_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MyStocks 测试仪表盘</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .dashboard-container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }
        .metric-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .metric-name {
            font-size: 16px;
            font-weight: 600;
            color: #333;
        }
        .metric-icon {
            font-size: 24px;
        }
        .metric-value {
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }
        .metric-details {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 14px;
            color: #666;
        }
        .trend-up { color: #e74c3c; }
        .trend-down { color: #27ae60; }
        .trend-neutral { color: #7f8c8d; }
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .chart-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 15px;
            color: #333;
        }
        .test-executions {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .test-execution {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            border-bottom: 1px solid #eee;
        }
        .test-execution:last-child {
            border-bottom: none;
        }
        .test-name {
            font-weight: 500;
            color: #333;
        }
        .test-status {
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
        }
        .status-running { background: #e3f2fd; color: #1976d2; }
        .status-passed { background: #e8f5e8; color: #2e7d32; }
        .status-failed { background: #ffebee; color: #c62828; }
        .status-skipped { background: #fff3e0; color: #f57c00; }
        .status-pending { background: #f5f5f5; color: #757575; }
        .progress-bar {
            width: 100px;
            height: 8px;
            background: #eee;
            border-radius: 4px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background: #667eea;
            transition: width 0.3s ease;
        }
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
        }
        .status-indicator-running { background: #1976d2; animation: pulse 2s infinite; }
        .status-indicator-passed { background: #2e7d32; }
        .status-indicator-failed { background: #c62828; }
        .status-indicator-skipped { background: #f57c00; }
        .status-indicator-pending { background: #757575; }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        .alert {
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 10px;
        }
        .alert-critical { background: #ffebee; border-left: 4px solid #c62828; }
        .alert-high { background: #fff3e0; border-left: 4px solid #f57c00; }
        .alert-medium { background: #fff8e1; border-left: 4px solid #ffa000; }
        .alert-low { background: #f3e5f5; border-left: 4px solid #7b1fa2; }
        .last-updated {
            text-align: center;
            color: #666;
            font-size: 14px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="dashboard-container">
        <div class="header">
            <h1>🚀 MyStocks 测试仪表盘</h1>
            <p>实时监控测试执行状态和系统性能</p>
        </div>

        <div class="metrics-grid" id="metrics-grid">
            <!-- 指标卡片将在这里动态生成 -->
        </div>

        <div class="charts-grid">
            <div class="chart-container">
                <div class="chart-title">测试执行状态分布</div>
                <div id="test-status-chart"></div>
            </div>
            <div class="chart-container">
                <div class="chart-title">CPU使用率趋势</div>
                <div id="cpu-trend-chart"></div>
            </div>
            <div class="chart-container">
                <div class="chart-title">资源监控</div>
                <div id="resource-gauges"></div>
            </div>
        </div>

        <div class="test-executions">
            <div class="chart-title">测试执行状态</div>
            <div id="test-executions-list">
                <!-- 测试执行列表将在这里动态生成 -->
            </div>
        </div>

        <div class="last-updated" id="last-updated">
            最后更新: --
        </div>
    </div>

    <script>
        // Socket.IO连接
        const socket = io();

        // 连接成功
        socket.on('connected', function(data) {
            console.log('已连接到仪表盘服务器');
            loadDashboardData();
        });

        // 指标更新
        socket.on('metrics_update', function(data) {
            updateMetrics(data);
        });

        // 测试执行更新
        socket.on('test_execution_update', function(data) {
            updateTestExecution(data);
        });

        // 告警触发
        socket.on('alert_triggered', function(data) {
            showAlert(data);
        });

        // 加载仪表盘数据
        function loadDashboardData() {
            fetch('/api/metrics')
                .then(response => response.json())
                .then(data => updateMetrics(data));

            fetch('/api/test-executions')
                .then(response => response.json())
                .then(data => updateTestExecutions(data));

            updateCharts();
        }

        // 更新指标显示
        function updateMetrics(data) {
            const metricsGrid = document.getElementById('metrics-grid');
            metricsGrid.innerHTML = '';

            data.metrics.forEach(metric => {
                const card = document.createElement('div');
                card.className = 'metric-card';

                const trendClass = `trend-${metric.trend}`;
                const trendIcon = metric.trend === 'up' ? '↗️' : metric.trend === 'down' ? '↘️' : '➡️';

                card.innerHTML = `
                    <div class="metric-header">
                        <span class="metric-name">${metric.name}</span>
                        <span class="metric-icon">${metric.icon}</span>
                    </div>
                    <div class="metric-value">${metric.value} ${metric.unit}</div>
                    <div class="metric-details">
                        <span class="${trendClass}">${trendIcon} ${Math.abs(metric.change).toFixed(1)}%</span>
                        <span>阈值: ${metric.threshold || '无'}</span>
                    </div>
                `;

                metricsGrid.appendChild(card);
            });

            document.getElementById('last-updated').textContent =
                `最后更新: ${new Date().toLocaleString()}`;
        }

        // 更新测试执行列表
        function updateTestExecutions(data) {
            const listContainer = document.getElementById('test-executions-list');
            listContainer.innerHTML = '';

            data.executions.forEach(execution => {
                const item = document.createElement('div');
                item.className = 'test-execution';

                const statusClass = `status-${execution.status}`;
                const statusIcon = getStatusIcon(execution.status);
                const progressWidth = (execution.progress * 100) + '%';

                item.innerHTML = `
                    <div>
                        <div class="test-name">
                            <span class="status-indicator status-indicator-${execution.status}"></span>
                            ${execution.name}
                        </div>
                        <div style="font-size: 12px; color: #666; margin-top: 5px;">
                            ${execution.current_step || '等待执行...'}
                        </div>
                    </div>
                    <div style="text-align: right;">
                        <div class="test-status ${statusClass}">${execution.status.toUpperCase()}</div>
                        <div style="font-size: 12px; color: #666; margin-top: 5px;">
                            ${execution.duration.toFixed(1)}s
                        </div>
                        <div class="progress-bar" style="width: 100px; margin: 5px 0;">
                            <div class="progress-fill" style="width: ${progressWidth}"></div>
                        </div>
                    </div>
                `;

                listContainer.appendChild(item);
            });
        }

        // 更新图表
        function updateCharts() {
            // 更新测试状态饼图
            fetch('/api/test-executions')
                .then(response => response.json())
                .then(data => {
                    const statusCounts = {};
                    data.executions.forEach(execution => {
                        statusCounts[execution.status] = (statusCounts[execution.status] || 0) + 1;
                    });

                    const trace = {
                        values: Object.values(statusCounts),
                        labels: Object.keys(statusCounts),
                        type: 'pie',
                        hole: 0.3
                    };

                    const layout = {
                        title: '测试执行状态分布',
                        title_x: 0.5
                    };

                    Plotly.newPlot('test-status-chart', [trace], layout);
                });

            // 更新CPU趋势图
            fetch('/api/history/1h')
                .then(response => response.json())
                .then(data => {
                    const cpuData = data.cpu_usage || [];
                    if (cpuData.length > 0) {
                        const trace = {
                            x: cpuData.map(d => d.timestamp),
                            y: cpuData.map(d => d.value),
                            type: 'scatter',
                            mode: 'lines+markers',
                            name: 'CPU使用率'
                        };

                        const layout = {
                            title: 'CPU使用率趋势',
                            xaxis: { title: '时间' },
                            yaxis: { title: '使用率(%)' },
                            title_x: 0.5
                        };

                        Plotly.newPlot('cpu-trend-chart', [trace], layout);
                    }
                });
        }

        // 获取状态图标
        function getStatusIcon(status) {
            const icons = {
                'running': '🔄',
                'passed': '✅',
                'failed': '❌',
                'skipped': '⏭️',
                'pending': '⏳'
            };
            return icons[status] || '❓';
        }

        // 显示告警
        function showAlert(alertData) {
            const alertContainer = document.createElement('div');
            alertContainer.className = `alert alert-${alertData.severity}`;

            alertContainer.innerHTML = `
                <strong>🚨 ${alertData.name}</strong><br>
                ${alertData.message}<br>
                <small>时间: ${new Date(alertData.timestamp).toLocaleString()}</small>
            `;

            document.body.insertBefore(alertContainer, document.body.firstChild);

            // 5秒后自动移除
            setTimeout(() => {
                alertContainer.remove();
            }, 5000);
        }

        // 定期刷新数据
        setInterval(loadDashboardData, 10000);
    </script>
</body>
</html>
    """

    with open(template_dir / "dashboard.html", "w", encoding="utf-8") as f:
        f.write(dashboard_template)


def demo_test_dashboard():
    """演示测试仪表盘功能"""
    print("🚀 演示测试仪表盘功能")

    # 创建仪表盘
    dashboard = TestDashboard(host="localhost", port=5000, debug=True)

    # 添加一些示例指标
    dashboard.add_metric(
        DashboardMetric(
            name="测试覆盖率",
            value=85.5,
            unit="%",
            trend="up",
            change=5.2,
            threshold=80.0,
            color="green",
            icon="📈",
            description="当前测试覆盖率",
        )
    )

    dashboard.add_metric(
        DashboardMetric(
            name="API响应时间",
            value=234.5,
            unit="ms",
            trend="down",
            change=-12.3,
            threshold=500.0,
            color="blue",
            icon="⚡",
            description="平均API响应时间",
        )
    )

    dashboard.add_metric(
        DashboardMetric(
            name="测试成功率",
            value=98.2,
            unit="%",
            trend="neutral",
            change=0.0,
            threshold=95.0,
            color="green",
            icon="🎯",
            description="测试执行成功率",
        )
    )

    # 添加测试执行
    demo_test = TestExecutionStatus(
        test_id="test_001",
        name="用户登录测试",
        status="running",
        progress=0.65,
        start_time=datetime.now() - timedelta(minutes=5),
        duration=300.0,
        current_step="验证登录接口响应",
        total_steps=5,
        completed_steps=3,
    )
    dashboard.add_test_execution(demo_test)

    demo_test2 = TestExecutionStatus(
        test_id="test_002",
        name="数据库连接测试",
        status="passed",
        progress=1.0,
        start_time=datetime.now() - timedelta(minutes=10),
        duration=45.2,
        total_steps=3,
        completed_steps=3,
    )
    dashboard.add_test_execution(demo_test2)

    # 创建模板文件
    create_dashboard_templates()

    print("✅ 仪表盘准备完成")
    print(f"📊 指标数量: {len(dashboard.metrics)}")
    print(f"🔄 测试执行: {len(dashboard.test_executions)}")
    print(f"🚨 告警规则: {len(dashboard.alerts)}")
    print(f"🌐 访问地址: http://{dashboard.host}:{dashboard.port}")
    print("📋 API端点: /api/metrics, /api/test-executions, /api/alerts")

    return dashboard


