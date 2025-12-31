#!/usr/bin/env python3
"""批量生成P2 API契约文件"""

import os
import yaml
from pathlib import Path

# P2 API端点列表
P2_APIS = {
    "indicators": [
        {"path": "/api/indicators/registry", "method": "GET", "desc": "获取指标注册表"},
        {"path": "/api/indicators/registry/{category}", "method": "GET", "desc": "获取指定分类的指标"},
        {"path": "/api/indicators/calculate", "method": "POST", "desc": "计算技术指标"},
        {"path": "/api/indicators/calculate/batch", "method": "POST", "desc": "批量计算技术指标"},
        {"path": "/api/indicators/cache/stats", "method": "GET", "desc": "获取缓存统计信息"},
        {"path": "/api/indicators/cache/clear", "method": "POST", "desc": "清理指标计算缓存"},
        {"path": "/api/indicators/configs", "method": "POST", "desc": "创建指标配置"},
        {"path": "/api/indicators/configs", "method": "GET", "desc": "获取用户的指标配置列表"},
        {"path": "/api/indicators/configs/{config_id}", "method": "GET", "desc": "获取指定的指标配置详情"},
        {"path": "/api/indicators/configs/{config_id}", "method": "PUT", "desc": "更新指标配置"},
        {"path": "/api/indicators/configs/{config_id}", "method": "DELETE", "desc": "删除指标配置"},
    ],
    "announcement": [
        {"path": "/api/announcement/health", "method": "GET", "desc": "健康检查"},
        {"path": "/api/announcement/status", "method": "GET", "desc": "获取服务状态"},
        {"path": "/api/announcement/analyze", "method": "POST", "desc": "AI分析数据"},
        {"path": "/api/announcement/fetch", "method": "POST", "desc": "获取并保存公告"},
        {"path": "/api/announcement/list", "method": "GET", "desc": "查询公告列表"},
        {"path": "/api/announcement/today", "method": "GET", "desc": "获取今日公告"},
        {"path": "/api/announcement/important", "method": "GET", "desc": "获取重要公告"},
        {"path": "/api/announcement/stats", "method": "GET", "desc": "获取公告统计信息"},
        {"path": "/api/announcement/monitor-rules", "method": "GET", "desc": "获取监控规则列表"},
        {"path": "/api/announcement/monitor-rules", "method": "POST", "desc": "创建监控规则"},
        {"path": "/api/announcement/monitor-rules/{rule_id}", "method": "PUT", "desc": "更新监控规则"},
        {"path": "/api/announcement/monitor-rules/{rule_id}", "method": "DELETE", "desc": "删除监控规则"},
        {"path": "/api/announcement/triggered-records", "method": "GET", "desc": "获取触发记录列表"},
    ],
    "system": [
        {"path": "/api/system/health", "method": "GET", "desc": "系统健康检查"},
        {"path": "/api/system/adapters/health", "method": "GET", "desc": "适配器健康检查"},
        {"path": "/api/system/datasources", "method": "GET", "desc": "获取已配置的数据源列表"},
        {"path": "/api/system/test-connection", "method": "POST", "desc": "测试数据库连接"},
        {"path": "/api/system/logs", "method": "GET", "desc": "获取系统运行日志"},
        {"path": "/api/system/logs/summary", "method": "GET", "desc": "获取日志统计摘要"},
        {"path": "/api/system/architecture", "method": "GET", "desc": "获取系统架构信息"},
        {"path": "/api/system/database/health", "method": "GET", "desc": "数据库健康检查"},
        {"path": "/api/system/database/stats", "method": "GET", "desc": "数据库统计信息"},
        {"path": "/api/health", "method": "GET", "desc": "系统健康检查"},
        {"path": "/api/health/detailed", "method": "GET", "desc": "详细健康检查"},
        {"path": "/api/health/reports/{timestamp}", "method": "GET", "desc": "获取健康检查报告"},
        {"path": "/api/monitoring/alert-rules", "method": "GET", "desc": "获取告警规则列表"},
        {"path": "/api/monitoring/alert-rules", "method": "POST", "desc": "创建告警规则"},
        {"path": "/api/monitoring/alert-rules/{rule_id}", "method": "PUT", "desc": "更新告警规则"},
        {"path": "/api/monitoring/alert-rules/{rule_id}", "method": "DELETE", "desc": "删除告警规则"},
        {"path": "/api/monitoring/alerts", "method": "GET", "desc": "查询告警记录"},
        {"path": "/api/monitoring/alerts/{alert_id}/mark-read", "method": "POST", "desc": "标记告警为已读"},
        {"path": "/api/monitoring/alerts/mark-all-read", "method": "POST", "desc": "批量标记所有未读告警"},
        {"path": "/api/monitoring/realtime/{symbol}", "method": "GET", "desc": "获取单只股票的实时监控数据"},
        {"path": "/api/monitoring/realtime", "method": "GET", "desc": "获取实时监控数据列表"},
        {"path": "/api/monitoring/realtime/fetch", "method": "POST", "desc": "手动触发获取实时数据"},
        {"path": "/api/monitoring/dragon-tiger", "method": "GET", "desc": "获取龙虎榜数据"},
        {"path": "/api/monitoring/dragon-tiger/fetch", "method": "POST", "desc": "手动触发获取龙虎榜数据"},
        {"path": "/api/monitoring/summary", "method": "GET", "desc": "获取监控系统摘要"},
        {"path": "/api/monitoring/stats/today", "method": "GET", "desc": "获取今日统计数据"},
        {"path": "/api/monitoring/control/start", "method": "POST", "desc": "启动监控"},
        {"path": "/api/monitoring/control/stop", "method": "POST", "desc": "停止监控"},
        {"path": "/api/monitoring/control/status", "method": "GET", "desc": "获取监控状态"},
    ],
}

def generate_api_id(module, index, method, path):
    """生成API ID"""
    path_clean = path.replace("/", "_").replace("{", "").replace("}", "").strip("_")
    method_lower = method.lower()
    return f"p2_{module}_{index:02d}_{method_lower}_{path_clean}"

def create_contract(api_info, module, index):
    """创建单个API契约"""
    path = api_info["path"]
    method = api_info["method"]
    desc = api_info["desc"]
    
    api_id = generate_api_id(module, index, method, path)
    
    # 提取路径参数
    path_params = []
    if "{" in path:
        parts = path.split("/")
        for part in parts:
            if part.startswith("{") and part.endswith("}"):
                param_name = part[1:-1]
                path_params.append({
                    "name": param_name,
                    "type": "string",
                    "required": True,
                    "description": f"{param_name}参数"
                })
    
    # 构建请求参数
    request_params = {
        "path_params": path_params,
        "query_params": [],
        "body_params": {}
    } if method in ["POST", "PUT", "PATCH"] else {
        "path_params": path_params,
        "query_params": []
    }
    
    # 确定成功状态码
    success_code = 200
    if method == "POST":
        success_code = 201
    elif method == "DELETE":
        success_code = 204
    
    contract = {
        "api_id": api_id,
        "priority": "P2",
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
        "auth_required": method in ["POST", "PUT", "DELETE", "PATCH"],
        "rate_limit": "60/minute",
        "tags": [module, "p2"],
        "created_at": "2025-12-31",
        "updated_at": "2025-12-31"
    }
    
    return contract, api_id

def main():
    """主函数"""
    output_dir = Path("/opt/claude/mystocks_phase7_backend/contracts/p2")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    total_created = 0
    
    for module, apis in P2_APIS.items():
        print(f"\n处理模块: {module}")
        module_dir = output_dir / module
        module_dir.mkdir(exist_ok=True)
        
        for index, api_info in enumerate(apis, 1):
            contract, api_id = create_contract(api_info, module, index)
            contract_file = module_dir / f"{api_id}.yaml"
            with open(contract_file, "w", encoding="utf-8") as f:
                yaml.dump(contract, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            total_created += 1
            print(f"  ✓ {api_id}")
    
    # 生成索引文件
    index_file = output_dir / "index.yaml"
    with open(index_file, "w", encoding="utf-8") as f:
        yaml.dump({
            "priority": "P2",
            "total_apis": total_created,
            "modules": {module: len(apis) for module, apis in P2_APIS.items()},
            "created_at": "2025-12-31",
            "contracts": {
                module: [
                    generate_api_id(module, i, api["method"], api["path"])
                    for i, api in enumerate(apis, 1)
                ]
                for module, apis in P2_APIS.items()
            }
        }, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    print(f"\n✅ 契约生成完成! 总计: {total_created}个")
    print(f"   输出: {output_dir}")

if __name__ == "__main__":
    main()
