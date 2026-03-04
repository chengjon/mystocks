#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks Web前端状态检查和展示脚本

展示前端页面结构和功能
"""

import requests
import os
from datetime import datetime

FRONTEND_PORT = int(os.getenv("FRONTEND_PORT", "3020"))
FRONTEND_BACKUP_PORT = int(os.getenv("FRONTEND_BACKUP_PORT", "3021"))
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8020"))
BACKEND_BACKUP_PORT = int(os.getenv("BACKEND_BACKUP_PORT", "8021"))


def check_service_status():
    """检查服务状态"""
    print("🚀 MyStocks Web前端服务状态检查")
    print("=" * 60)
    print(f"📅 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 检查前端服务
    frontend_ports = [FRONTEND_PORT, FRONTEND_BACKUP_PORT]
    frontend_url = None

    print("🔍 检查前端服务...")
    for port in frontend_ports:
        try:
            response = requests.get(f"http://localhost:{port}", timeout=2)
            if response.status_code == 200:
                frontend_url = f"http://localhost:{port}"
                print(f"   ✅ 前端服务运行在端口 {port}")
                break
        except requests.exceptions.RequestException:
            continue

    if not frontend_url:
        print("   ❌ 前端服务未找到")

    # 检查后端服务
    backend_ports = [BACKEND_PORT, BACKEND_BACKUP_PORT]
    backend_url = None

    print("\n🔍 检查后端服务...")
    for port in backend_ports:
        try:
            response = requests.get(f"http://localhost:{port}/docs", timeout=2)
            if response.status_code == 200:
                backend_url = f"http://localhost:{port}"
                print(f"   ✅ 后端服务运行在端口 {port}")
                break
        except requests.exceptions.RequestException:
            continue

    if not backend_url:
        print("   ❌ 后端服务未找到")

    return frontend_url, backend_url


def show_frontend_features():
    """展示前端页面功能"""
    print("\n🎨 MyStocks Web前端功能展示")
    print("=" * 60)

    features = [
        {
            "title": "📊 仪表盘 (Dashboard)",
            "path": "/dashboard",
            "description": "市场概览、关键指标、实时数据图表",
            "features": ["市场统计", "热力图", "龙头板块", "实时行情"],
        },
        {
            "title": "📈 市场行情 (Market)",
            "path": "/market",
            "description": "股票列表、价格监控、技术指标",
            "features": ["实时行情", "涨跌幅排行", "成交量分析", "技术指标"],
        },
        {
            "title": "🔍 TDX行情 (Tdx Market)",
            "path": "/tdx-market",
            "description": "通达信数据集成、深度行情分析",
            "features": ["TDX数据", "深度行情", "自定义指标", "多周期分析"],
        },
        {
            "title": "💰 资金流向 (Fund Flow)",
            "path": "/market-data/fund-flow",
            "description": "主力资金流向分析、散户资金监控",
            "features": ["主力净流入", "散户资金", "资金趋势", "行业资金"],
        },
        {
            "title": "📊 ETF行情 (ETF)",
            "path": "/market-data/etf",
            "description": "ETF价格跟踪、指数基金分析",
            "features": ["ETF列表", "折溢价率", "成交量分析", "跟踪误差"],
        },
        {
            "title": "🎯 竞价抢筹 (Chip Race)",
            "path": "/market-data/chip-race",
            "description": "开盘竞价抢筹、收盘竞价分析",
            "features": ["开盘竞价", "收盘竞价", "抢筹分析", "资金博弈"],
        },
        {
            "title": "🐉 龙虎榜 (Long Hu Bang)",
            "path": "/market-data/lhb",
            "description": "龙虎榜数据、大单交易分析",
            "features": ["龙虎榜数据", "大单监控", "机构动向", "游资分析"],
        },
        {
            "title": "🤖 问财筛选 (Wencai)",
            "path": "/market-data/wencai",
            "description": "智能问财查询、股票筛选",
            "features": ["自然语言查询", "智能筛选", "自定义条件", "结果导出"],
        },
        {
            "title": "📋 股票管理 (Stocks)",
            "path": "/stocks",
            "description": "股票池管理、关注列表",
            "features": ["股票池", "关注列表", "标签管理", "批量操作"],
        },
        {
            "title": "📊 数据分析 (Analysis)",
            "path": "/analysis",
            "description": "综合数据分析、报表生成",
            "features": ["数据挖掘", "统计分析", "报表生成", "趋势预测"],
        },
        {
            "title": "📈 技术分析 (Technical)",
            "path": "/technical",
            "description": "技术指标分析、图表展示",
            "features": ["K线图", "技术指标", "形态识别", "买卖信号"],
        },
        {
            "title": "⚠️ 风险监控 (Risk Monitor)",
            "path": "/risk",
            "description": "风险指标监控、预警系统",
            "features": ["风险评估", "异常监控", "预警机制", "风险报告"],
        },
        {
            "title": "🔴 实时监控 (Real-time)",
            "path": "/realtime",
            "description": "实时数据监控、动态图表",
            "features": ["实时行情", "动态更新", "告警通知", "状态监控"],
        },
        {
            "title": "💼 策略管理 (Strategy)",
            "path": "/strategy",
            "description": "交易策略配置、回测分析",
            "features": ["策略编辑", "参数调优", "回测分析", "实盘验证"],
        },
        {
            "title": "📊 回测分析 (Backtest)",
            "path": "/backtest",
            "description": "策略回测、性能分析",
            "features": ["历史回测", "性能指标", "风险评估", "对比分析"],
        },
        {
            "title": "📝 任务管理 (Tasks)",
            "path": "/tasks",
            "description": "后台任务监控、调度管理",
            "features": ["任务列表", "执行状态", "调度配置", "日志查看"],
        },
        {
            "title": "⚙️ 系统设置 (Settings)",
            "path": "/settings",
            "description": "系统配置、用户偏好",
            "features": ["系统配置", "用户偏好", "界面主题", "数据源设置"],
        },
        {
            "title": "🏗️ 系统架构 (Architecture)",
            "path": "/system/architecture",
            "description": "系统架构图、技术文档",
            "features": ["架构图", "模块关系", "技术选型", "部署方案"],
        },
        {
            "title": "🗄️ 数据库监控 (Database)",
            "path": "/system/database-monitor",
            "description": "数据库状态监控、性能分析",
            "features": ["连接状态", "性能监控", "查询分析", "空间使用"],
        },
    ]

    for i, feature in enumerate(features, 1):
        print(f"{i:2d}. {feature['title']}")
        print(f"    路径: {feature['path']}")
        print(f"    描述: {feature['description']}")
        print(f"    功能: {', '.join(feature['features'])}")
        print()


def show_access_info():
    """展示访问信息"""
    print("🌐 MyStocks Web服务访问信息")
    print("=" * 60)

    print("📱 前端访问地址:")
    print(f"   - 本地访问: http://localhost:{FRONTEND_PORT}")
    print(f"   - 网络访问: http://0.0.0.0:{FRONTEND_PORT}")
    print("   - 浏览器支持: Chrome, Firefox, Safari, Edge")
    print()

    print("🔧 后端API服务:")
    print(f"   - API文档: http://localhost:{BACKEND_PORT}/docs")
    print(f"   - API接口: http://localhost:{BACKEND_PORT}/api")
    print(f"   - 健康检查: http://localhost:{BACKEND_PORT}/health")
    print()

    print("👤 默认登录账户:")
    print("   管理员账户:")
    print("     - 用户名: admin")
    print("     - 密码: admin123")
    print("   普通用户:")
    print("     - 用户名: user")
    print("     - 密码: user123")
    print()

    print("💡 使用提示:")
    print("   - 前端支持响应式设计，移动端友好")
    print("   - 集成Mock数据系统，可脱离数据库运行")
    print("   - 支持实时数据更新和WebSocket连接")
    print("   - 提供完整的技术指标和分析工具")
    print("   - 集成交付策略管理和回测功能")


def main():
    """主函数"""
    # 检查服务状态
    frontend_url, backend_url = check_service_status()

    # 展示前端功能
    show_frontend_features()

    # 展示访问信息
    show_access_info()

    # 总结
    print("=" * 60)
    print("✅ MyStocks Web前端系统准备就绪！")
    print(f"🌐 前端地址: {frontend_url or '未启动'}")
    print(f"🔧 后端地址: {backend_url or '未启动'}")
    print()
    print("🚀 现在您可以:")
    print("   1. 在浏览器中访问前端地址")
    print("   2. 查看完整的股票交易管理功能")
    print("   3. 使用Mock数据进行开发和测试")
    print("   4. 体验现代化的Web界面和交互")


if __name__ == "__main__":
    main()
