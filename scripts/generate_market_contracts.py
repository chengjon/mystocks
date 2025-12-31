#!/usr/bin/env python3
"""生成Market API契约文件

生成Market v1/v2 API的契约，这些是补充的P1 API契约。

Author: Backend CLI (Claude Code)
Date: 2025-12-31
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Any

# Market API端点列表（从实际代码提取）
MARKET_APIS = {
    "market": [
        # Market v1 API (market.py)
        {"path": "/api/market/fund-flow", "method": "GET", "desc": "查询资金流向"},
        {"path": "/api/market/fund-flow/refresh", "method": "POST", "desc": "刷新资金流向数据"},
        {"path": "/api/market/etf/list", "method": "GET", "desc": "查询ETF列表"},
        {"path": "/api/market/etf/refresh", "method": "POST", "desc": "刷新ETF数据"},
        {"path": "/api/market/chip-race", "method": "GET", "desc": "查询竞价抢筹"},
        {"path": "/api/market/chip-race/refresh", "method": "POST", "desc": "刷新抢筹数据"},
        {"path": "/api/market/lhb", "method": "GET", "desc": "查询龙虎榜"},
        {"path": "/api/market/lhb/refresh", "method": "POST", "desc": "刷新龙虎榜数据"},
        {"path": "/api/market/quotes", "method": "GET", "desc": "查询实时行情"},
        {"path": "/api/market/stocks", "method": "GET", "desc": "查询股票列表"},
        {"path": "/api/market/kline", "method": "GET", "desc": "查询K线数据"},
        {"path": "/api/market/heatmap", "method": "GET", "desc": "获取市场热力图数据"},
        {"path": "/api/market/health", "method": "GET", "desc": "市场数据API健康检查"},

        # Market v2 API (market_v2.py)
        {"path": "/api/market-v2/fund-flow", "method": "GET", "desc": "查询个股资金流向"},
        {"path": "/api/market-v2/fund-flow/refresh", "method": "POST", "desc": "刷新资金流向数据"},
        {"path": "/api/market-v2/etf/list", "method": "GET", "desc": "查询ETF列表"},
        {"path": "/api/market-v2/etf/refresh", "method": "POST", "desc": "刷新ETF数据"},
        {"path": "/api/market-v2/lhb", "method": "GET", "desc": "查询龙虎榜"},
        {"path": "/api/market-v2/lhb/refresh", "method": "POST", "desc": "刷新龙虎榜数据"},
        {"path": "/api/market-v2/sector/fund-flow", "method": "GET", "desc": "查询行业/概念资金流向"},
        {"path": "/api/market-v2/sector/fund-flow/refresh", "method": "POST", "desc": "刷新行业/概念资金流向"},
        {"path": "/api/market-v2/dividend", "method": "GET", "desc": "查询股票分红配送"},
        {"path": "/api/market-v2/dividend/refresh", "method": "POST", "desc": "刷新股票分红配送数据"},
        {"path": "/api/market-v2/blocktrade", "method": "GET", "desc": "查询股票大宗交易"},
        {"path": "/api/market-v2/blocktrade/refresh", "method": "POST", "desc": "刷新股票大宗交易数据"},
        {"path": "/api/market-v2/refresh-all", "method": "POST", "desc": "批量刷新所有市场数据"},
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

    # 判断是否需要认证（健康检查不需要）
    auth_required = method in ["POST", "PUT", "DELETE", "PATCH"] and "health" not in path

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
        "auth_required": auth_required,
        "rate_limit": "60/minute",
        "tags": [module, "p1", "market"],
        "created_at": "2025-12-31",
        "updated_at": "2025-12-31"
    }

    return contract, api_id


def main():
    """主函数"""
    output_dir = Path("/opt/claude/mystocks_phase7_backend/contracts/p1")
    output_dir.mkdir(parents=True, exist_ok=True)

    total_created = 0

    print(f"\n🚀 开始生成Market API契约文件")
    print(f"   输出目录: {output_dir}")
    print()

    for module, apis in MARKET_APIS.items():
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

    # 更新索引文件
    index_file = output_dir / "index.yaml"
    existing_index = {}
    if index_file.exists():
        with open(index_file, "r", encoding="utf-8") as f:
            existing_index = yaml.safe_load(f) or {}

    # 更新market模块
    if "contracts" not in existing_index:
        existing_index["contracts"] = {}
    existing_index["contracts"]["market"] = [
        generate_api_id("market", i, api["method"], api["path"])
        for i, api in enumerate(MARKET_APIS["market"], 1)
    ]
    existing_index["total_apis"] = existing_index.get("total_apis", 0) + total_created

    with open(index_file, "w", encoding="utf-8") as f:
        yaml.dump(existing_index, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print("=" * 60)
    print(f"✅ Market API契约生成完成!")
    print(f"   总计: {total_created}个契约")
    print(f"   输出: {output_dir}")
    print()


if __name__ == "__main__":
    main()
