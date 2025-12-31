#!/usr/bin/env python3
"""批量生成P1 API契约文件（扩展版）

生成所有P1级别API的契约，包括核心模块和扩展模块。

Author: Backend CLI (Claude Code)
Date: 2025-12-31
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Any

# P1 API端点列表（所有模块）
P1_APIS = {
    # 核心模块（已完成）
    "backtest": [
        {"path": "/api/v1/strategy/strategies", "method": "GET", "desc": "获取策略列表"},
        {"path": "/api/v1/strategy/strategies", "method": "POST", "desc": "创建新策略"},
        {"path": "/api/v1/strategy/strategies/{strategy_id}", "method": "GET", "desc": "获取策略详情"},
        {"path": "/api/v1/strategy/strategies/{strategy_id}", "method": "PUT", "desc": "更新策略"},
        {"path": "/api/v1/strategy/strategies/{strategy_id}", "method": "DELETE", "desc": "删除策略"},
        {"path": "/api/v1/strategy/models/train", "method": "POST", "desc": "启动模型训练"},
        {"path": "/api/v1/strategy/models/training/{task_id}/status", "method": "GET", "desc": "查询训练状态"},
        {"path": "/api/v1/strategy/models", "method": "GET", "desc": "获取模型列表"},
        {"path": "/api/v1/strategy/backtest/run", "method": "POST", "desc": "执行回测"},
        {"path": "/api/v1/strategy/backtest/results", "method": "GET", "desc": "获取回测结果列表"},
        {"path": "/api/v1/strategy/backtest/results/{backtest_id}", "method": "GET", "desc": "获取回测详细结果"},
        {"path": "/api/v1/strategy/backtest/results/{backtest_id}/chart-data", "method": "GET", "desc": "获取回测图表数据"},
        {"path": "/ws/backtest/{backtest_id}", "method": "WS", "desc": "回测进度WebSocket推送"},
        {"path": "/ws/status", "method": "GET", "desc": "获取WebSocket连接状态"},
    ],
    "risk": [
        {"path": "/api/v1/risk/var-cvar", "method": "POST", "desc": "计算VaR和CVaR"},
        {"path": "/api/v1/risk/beta", "method": "POST", "desc": "计算Beta系数"},
        {"path": "/api/v1/risk/dashboard", "method": "GET", "desc": "获取风险仪表盘数据"},
        {"path": "/api/v1/risk/metrics/history", "method": "GET", "desc": "获取风险指标历史"},
        {"path": "/api/v1/risk/alerts", "method": "GET", "desc": "获取风险预警规则"},
        {"path": "/api/v1/risk/alerts", "method": "POST", "desc": "创建风险预警规则"},
        {"path": "/api/v1/risk/alerts/{alert_id}", "method": "PUT", "desc": "更新风险预警规则"},
        {"path": "/api/v1/risk/alerts/{alert_id}", "method": "DELETE", "desc": "删除风险预警规则"},
        {"path": "/api/v1/risk/notifications/test", "method": "POST", "desc": "发送测试通知"},
        {"path": "/api/v1/risk/metrics/calculate", "method": "POST", "desc": "计算完整风险指标"},
        {"path": "/api/v1/risk/position/assess", "method": "POST", "desc": "评估仓位风险"},
        {"path": "/api/v1/risk/alerts/generate", "method": "POST", "desc": "生成风险告警"},
    ],
    "user": [
        {"path": "/api/v1/auth/login", "method": "POST", "desc": "用户登录获取访问令牌"},
        {"path": "/api/v1/auth/logout", "method": "POST", "desc": "用户登出"},
        {"path": "/api/v1/auth/me", "method": "GET", "desc": "获取当前用户信息"},
        {"path": "/api/v1/auth/refresh", "method": "POST", "desc": "刷新访问令牌"},
        {"path": "/api/v1/auth/users", "method": "GET", "desc": "获取用户列表（仅管理员）"},
        {"path": "/api/v1/auth/csrf/token", "method": "GET", "desc": "获取CSRF保护令牌"},
    ],
    # 新增模块
    "trade": [
        {"path": "/trade/health", "method": "GET", "desc": "交易API健康检查"},
        {"path": "/trade/portfolio", "method": "GET", "desc": "获取投资组合概览"},
        {"path": "/trade/positions", "method": "GET", "desc": "获取持仓列表"},
        {"path": "/trade/trades", "method": "GET", "desc": "获取交易记录列表"},
        {"path": "/trade/statistics", "method": "GET", "desc": "获取交易统计数据"},
        {"path": "/trade/execute", "method": "POST", "desc": "执行买卖交易"},
    ],
    "technical": [
        {"path": "/api/technical/indicators/trend", "method": "POST", "desc": "计算趋势指标"},
        {"path": "/api/technical/indicators/momentum", "method": "POST", "desc": "计算动量指标"},
        {"path": "/api/technical/indicators/volatility", "method": "POST", "desc": "计算波动性指标"},
        {"path": "/api/technical/indicators/volume", "method": "POST", "desc": "计算成交量指标"},
        {"path": "/api/technical/indicators/all", "method": "POST", "desc": "计算所有技术指标"},
        {"path": "/api/technical/analysis/signals", "method": "GET", "desc": "获取技术分析信号"},
        {"path": "/api/technical/analysis/patterns", "method": "GET", "desc": "识别技术形态"},
    ],
    "dashboard": [
        {"path": "/api/dashboard/summary", "method": "GET", "desc": "获取仪表盘汇总数据"},
        {"path": "/api/dashboard/market-overview", "method": "GET", "desc": "获取市场概览"},
        {"path": "/api/dashboard/health", "method": "GET", "desc": "仪表盘健康检查"},
    ],
    "data": [
        {"path": "/api/data/stocks/basic", "method": "GET", "desc": "获取股票基本信息"},
        {"path": "/api/data/stocks/industries", "method": "GET", "desc": "获取股票行业分类"},
        {"path": "/api/data/stocks/concepts", "method": "GET", "desc": "获取股票概念分类"},
        {"path": "/api/data/stocks/daily", "method": "GET", "desc": "获取股票日线数据"},
        {"path": "/api/data/markets/overview", "method": "GET", "desc": "获取市场概览数据"},
        {"path": "/api/data/stocks/search", "method": "GET", "desc": "股票搜索功能"},
        {"path": "/api/data/kline", "method": "GET", "desc": "获取K线数据"},
        {"path": "/api/data/stocks/kline", "method": "GET", "desc": "获取股票K线"},
        {"path": "/api/data/financial", "method": "GET", "desc": "获取财务数据"},
        {"path": "/api/data/markets/price-distribution", "method": "GET", "desc": "获取价格分布"},
        {"path": "/api/data/markets/hot-industries", "method": "GET", "desc": "获取热门行业"},
        {"path": "/api/data/markets/hot-concepts", "method": "GET", "desc": "获取热门概念"},
        {"path": "/api/data/stocks/intraday", "method": "GET", "desc": "获取日内数据"},
        {"path": "/api/data/stocks/{symbol}/detail", "method": "GET", "desc": "获取股票详情"},
        {"path": "/api/data/stocks/{symbol}/trading-summary", "method": "GET", "desc": "获取交易汇总"},
        {"path": "/api/data/test/factory", "method": "GET", "desc": "测试数据源工厂"},
    ],
    "sse": [
        {"path": "/sse/training", "method": "GET", "desc": "训练进度推送"},
        {"path": "/sse/backtest", "method": "GET", "desc": "回测进度推送"},
        {"path": "/sse/alerts", "method": "GET", "desc": "告警推送"},
        {"path": "/sse/dashboard", "method": "GET", "desc": "仪表盘数据推送"},
        {"path": "/sse/status", "method": "GET", "desc": "SSE服务状态"},
    ],
    "tasks": [
        {"path": "/api/tasks/register", "method": "POST", "desc": "注册任务"},
        {"path": "/api/tasks/{task_id}", "method": "DELETE", "desc": "删除任务"},
        {"path": "/api/tasks/", "method": "GET", "desc": "获取任务列表"},
        {"path": "/api/tasks/{task_id}", "method": "GET", "desc": "获取任务详情"},
        {"path": "/api/tasks/{task_id}/start", "method": "POST", "desc": "启动任务"},
        {"path": "/api/tasks/{task_id}/stop", "method": "POST", "desc": "停止任务"},
        {"path": "/api/tasks/executions/", "method": "GET", "desc": "获取执行记录"},
        {"path": "/api/tasks/executions/{execution_id}", "method": "GET", "desc": "获取执行详情"},
        {"path": "/api/tasks/statistics/", "method": "GET", "desc": "获取任务统计"},
        {"path": "/api/tasks/import", "method": "POST", "desc": "导入任务"},
        {"path": "/api/tasks/export", "method": "POST", "desc": "导出任务"},
        {"path": "/api/tasks/executions/cleanup", "method": "DELETE", "desc": "清理执行记录"},
        {"path": "/api/tasks/health", "method": "GET", "desc": "任务管理健康检查"},
        {"path": "/api/tasks/audit/logs", "method": "GET", "desc": "获取审计日志"},
        {"path": "/api/tasks/cleanup/audit", "method": "POST", "desc": "清理审计日志"},
    ],
}


def generate_api_id(module, index, method, path):
    """生成API ID"""
    path_clean = path.replace("/", "_").replace("{", "").replace("}", "_").strip("_")
    path_clean = path_clean.replace("-", "_")
    method_lower = method.lower()
    return f"p1_{module}_{index:02d}_{method_lower}_{path_clean}"


def extract_path_params(path: str) -> List[Dict[str, Any]]:
    """提取路径参数"""
    params = []
    if "{" in path:
        parts = path.split("/")
        for part in parts:
            if part.startswith("{") and part.endswith("}"):
                param_name = part[1:-1]
                params.append({
                    "name": param_name,
                    "type": "string",
                    "required": True,
                    "description": f"{param_name}参数"
                })
    return params


def create_contract(api_info: Dict[str, Any], module: str, index: int) -> tuple[Dict[str, Any], str]:
    """创建单个API契约"""
    path = api_info["path"]
    method = api_info["method"]
    desc = api_info["desc"]

    api_id = generate_api_id(module, index, method, path)

    # 提取路径参数
    path_params = extract_path_params(path)

    # 构建请求参数
    request_params: Dict[str, Any] = {
        "path_params": path_params,
        "query_params": []
    }

    # POST/PUT/PATCH请求添加body_params
    if method in ["POST", "PUT", "PATCH"]:
        request_params["body_params"] = {}

    # 确定成功状态码
    success_code = 200
    if method == "POST":
        success_code = 201
    elif method == "DELETE":
        success_code = 204

    contract = {
        "api_id": api_id,
        "priority": "P1",
        "module": module,
        "path": path,
        "method": method,
        "description": desc,
        "request_params": request_params,
        "response": {
            "success_code": success_code,
            "success_data": {},
            "error_codes": [400, 401, 404, 500]
        },
        "auth_required": method in ["POST", "PUT", "DELETE", "PATCH"] or module in ["user", "trade", "tasks"],
        "rate_limit": "60/minute",
        "tags": [module, "p1"],
        "created_at": "2025-12-31",
        "updated_at": "2025-12-31"
    }

    return contract, api_id


def main():
    """主函数"""
    output_dir = Path("/opt/claude/mystocks_phase7_backend/contracts/p1")
    output_dir.mkdir(parents=True, exist_ok=True)

    total_created = 0

    print(f"\n🚀 开始生成P1 API契约文件（所有模块）")
    print(f"   输出目录: {output_dir}")
    print()

    for module, apis in P1_APIS.items():
        print(f"📦 处理模块: {module} ({len(apis)}个端点)")
        module_dir = output_dir / module
        module_dir.mkdir(exist_ok=True)

        for index, api_info in enumerate(apis, 1):
            contract, api_id = create_contract(api_info, module, index)
            contract_file = module_dir / f"{api_id}.yaml"

            with open(contract_file, "w", encoding="utf-8") as f:
                yaml.dump(contract, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

            total_created += 1
            print(f"  ✓ {api_id}")

        print()

    # 生成索引文件
    index_file = output_dir / "index.yaml"
    with open(index_file, "w", encoding="utf-8") as f:
        yaml.dump({
            "priority": "P1",
            "total_apis": total_created,
            "modules": {module: len(apis) for module, apis in P1_APIS.items()},
            "created_at": "2025-12-31",
            "contracts": {
                module: [
                    generate_api_id(module, i, api["method"], api["path"])
                    for i, api in enumerate(apis, 1)
                ]
                for module, apis in P1_APIS.items()
            }
        }, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print("=" * 60)
    print(f"✅ P1 API契约生成完成!")
    print(f"   总计: {total_created}个契约")
    print(f"   输出: {output_dir}")
    print()
    print(f"📊 模块分布:")
    for module, count in {module: len(apis) for module, apis in P1_APIS.items()}.items():
        print(f"   - {module}: {count}个")
    print()


if __name__ == "__main__":
    main()
