#!/usr/bin/env python3
"""MyStocks 端口服务状态展示脚本
展示3000-3010端口上的服务运行状态
"""

import os
import socket
from datetime import datetime

import requests


FRONTEND_PORT = int(os.getenv("FRONTEND_PORT", "3020"))
FRONTEND_BACKUP_PORT = int(os.getenv("FRONTEND_BACKUP_PORT", "3021"))
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8020"))
BACKEND_BACKUP_PORT = int(os.getenv("BACKEND_BACKUP_PORT", "8021"))


def check_port_status(port):
    """检查端口状态"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(("localhost", port))
        sock.close()
        return result == 0
    except:
        return False


def get_service_info(port):
    """获取服务信息"""
    try:
        response = requests.get(f"http://localhost:{port}", timeout=2)
        if response.status_code == 200:
            # 尝试从HTML获取标题
            title_start = response.text.find("<title>")
            title_end = response.text.find("</title>")
            if title_start != -1 and title_end != -1:
                title = response.text[title_start + 7 : title_end].strip()
                return f"Web服务 - {title}"
            return "Web服务 - 正常运行"
    except:
        pass

    return "未知服务"


def show_port_status():
    """展示端口状态"""
    print(f"🔍 MyStocks 端口服务状态检查 ({FRONTEND_PORT}/{FRONTEND_BACKUP_PORT}/{BACKEND_PORT}/{BACKEND_BACKUP_PORT})")
    print("=" * 70)
    print(f"📅 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    services_info = {
        FRONTEND_PORT: {
            "name": "MyStocks Web前端",
            "description": "Vue.js + Element Plus 前端界面",
            "url": f"http://localhost:{FRONTEND_PORT}",
            "features": ["股票管理", "市场行情", "技术分析", "策略回测"],
        },
        FRONTEND_BACKUP_PORT: {
            "name": "预留端口",
            "description": "可用于WebSocket或API服务",
            "url": f"http://localhost:{FRONTEND_BACKUP_PORT}",
            "features": ["WebSocket", "实时数据", "推送通知"],
        },
        BACKEND_PORT: {
            "name": "MyStocks Web后端",
            "description": "FastAPI后端API服务",
            "url": f"http://localhost:{BACKEND_PORT}",
            "features": ["REST API", "数据库接口", "Mock数据", "实时数据"],
        },
        BACKEND_BACKUP_PORT: {
            "name": "MyStocks Web后端(备用)",
            "description": "FastAPI后端API服务备用端口",
            "url": f"http://localhost:{BACKEND_BACKUP_PORT}",
            "features": ["备用端口", "故障切换"],
        },
    }

    for port in sorted(services_info.keys()):
        is_running = check_port_status(port)
        status_icon = "✅" if is_running else "❌"

        print(f"{status_icon} 端口 {port}: ", end="")

        if is_running:
            if port in services_info:
                info = services_info[port]
                print(f"{info['name']} - {info['description']}")
                print(f"    🌐 访问地址: {info['url']}")
                print(f"    🔧 主要功能: {', '.join(info['features'])}")
            else:
                service_info = get_service_info(port)
                print(f"{service_info}")
        else:
            print("空闲")

        print()

    # 特殊显示常用端口
    print("=" * 70)
    print("📋 常用服务端口详情:")
    print()

    if check_port_status(FRONTEND_PORT):
        print(f"🌐 前端服务 (端口 {FRONTEND_PORT}):")
        print("   - 技术栈: Vue 3 + Element Plus + Vite")
        print("   - 主要页面: 仪表盘、市场行情、技术分析、策略管理")
        print("   - 数据源: 集成Mock数据系统，支持真实API切换")
        print("   - 特性: 响应式设计、实时更新、现代化UI")
        print()

    if check_port_status(BACKEND_PORT):
        print(f"🔧 后端服务 (端口 {BACKEND_PORT}):")
        print("   - 技术栈: FastAPI + Python 3.12")
        print(f"   - API文档: http://localhost:{BACKEND_PORT}/docs")
        print("   - 集成模块: 股票数据、技术指标、策略管理")
        print("   - 特性: 自动文档生成、Mock数据切换、CORS支持")
        print()
    else:
        print(f"⚠️ 后端服务 (端口 {BACKEND_PORT}): 未运行")
        print(
            f"   启动命令: cd /opt/claude/mystocks_spec/web/backend && uvicorn app.main:app --reload --host 0.0.0.0 --port {BACKEND_PORT}",
        )
        print()


def show_quick_commands():
    """显示快速命令"""
    print("🚀 MyStocks 快速启动命令")
    print("=" * 70)

    commands = [
        {
            "title": "启动前端服务",
            "command": "cd /opt/claude/mystocks_spec/web/frontend && npm run dev",
            "port": str(FRONTEND_PORT),
            "description": "启动Vue.js前端开发服务器",
        },
        {
            "title": "启动后端服务",
            "command": f"cd /opt/claude/mystocks_spec/web/backend && uvicorn app.main:app --reload --host 0.0.0.0 --port {BACKEND_PORT}",
            "port": str(BACKEND_PORT),
            "description": "启动FastAPI后端API服务",
        },
        {
            "title": "同时启动前后端",
            "command": "cd /opt/claude/mystocks_spec && ./web/start_dev.sh",
            "port": f"{FRONTEND_PORT} + {BACKEND_PORT}",
            "description": "启动开发环境的完整Web服务",
        },
        {
            "title": "运行Mock数据测试",
            "command": "python scripts/tests/test_enhanced_mock_data.py",
            "port": "N/A",
            "description": "测试Mock数据系统功能",
        },
    ]

    for cmd in commands:
        print(f"📝 {cmd['title']}:")
        print(f"   端口: {cmd['port']}")
        print(f"   命令: {cmd['command']}")
        print(f"   说明: {cmd['description']}")
        print()


def show_usage_guide():
    """显示使用指南"""
    print("💡 MyStocks Web前端使用指南")
    print("=" * 70)

    guide = [
        {
            "title": "🌐 访问前端界面",
            "steps": [
                f"打开浏览器访问 http://localhost:{FRONTEND_PORT}",
                "系统会自动加载登录页面",
                "使用默认账户登录 (admin/admin123)",
                "进入仪表盘查看系统概览",
            ],
        },
        {
            "title": "📊 核心功能模块",
            "steps": [
                "仪表盘: 查看市场概况和关键指标",
                "市场行情: 实时股票价格和涨跌幅",
                "技术分析: K线图和技术指标分析",
                "策略管理: 配置和回测交易策略",
                "问财筛选: 智能股票查询和筛选",
            ],
        },
        {
            "title": "🔧 开发调试",
            "steps": [
                "前端代码位于 /web/frontend/src/",
                "使用浏览器开发者工具调试",
                "支持热重载，修改代码自动刷新",
                "查看控制台日志了解运行状态",
            ],
        },
        {
            "title": "📱 响应式设计",
            "steps": [
                "支持桌面端、平板和移动设备",
                "自适应屏幕尺寸和分辨率",
                "移动端提供优化的触控体验",
                "支持横屏和竖屏切换",
            ],
        },
    ]

    for section in guide:
        print(f"{section['title']}:")
        for i, step in enumerate(section["steps"], 1):
            print(f"   {i}. {step}")
        print()


def main():
    """主函数"""
    show_port_status()
    show_quick_commands()
    show_usage_guide()

    print("=" * 70)
    print("✅ MyStocks Web系统状态检查完成！")
    print()
    print("🎯 立即体验:")
    print(f"   1. 访问 http://localhost:{FRONTEND_PORT} 开始使用")
    print("   2. 浏览各个功能模块体验完整功能")
    print("   3. 使用Mock数据进行开发和测试")
    print(f"   4. 查看API文档 http://localhost:{BACKEND_PORT}/docs")


if __name__ == "__main__":
    main()
