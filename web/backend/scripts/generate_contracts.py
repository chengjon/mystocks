#!/usr/bin/env python3
"""
API契约模板生成脚本
从catalog.yaml为所有API生成标准化契约YAML文件
"""

import json
import yaml
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ContractTemplate:
    """API契约模板"""
    api_id: str
    module: str
    path: str
    method: str
    summary: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)
    priority: str = "P2"
    request_params: Dict[str, Any] = field(default_factory=dict)
    response_code: int = 200
    response_data: Dict[str, Any] = field(default_factory=dict)
    error_codes: List[Dict[str, Any]] = field(default_factory=list)
    examples: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "api_id": self.api_id,
            "module": self.module,
            "path": self.path,
            "method": self.method,
            "summary": self.summary,
            "description": self.description,
            "tags": self.tags,
            "priority": self.priority,
            "request": {
                "params": self.request_params,
            },
            "response": {
                "code": self.response_code,
                "data": self.response_data,
                "error_codes": self.error_codes,
            },
            "examples": self.examples,
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "version": "1.0.0",
                **self.metadata,
            },
        }


def load_catalog(catalog_file: Path) -> List[Dict]:
    """加载catalog.yaml"""
    print(f"📖 加载API目录: {catalog_file}")

    with open(catalog_file, 'r', encoding='utf-8') as f:
        catalog = yaml.safe_load(f)

    apis = catalog.get('apis', [])
    print(f"✓ 加载 {len(apis)} 个API端点")
    return apis


def load_openapi_schema() -> Dict:
    """加载OpenAPI完整schema用于提取详细信息"""
    openapi_file = Path("/tmp/openapi.json")
    if openapi_file.exists():
        with open(openapi_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def extract_response_schema(openapi_data: Dict, path: str, method: str) -> Dict[str, Any]:
    """从OpenAPI schema提取响应结构"""
    try:
        path_obj = openapi_data.get("paths", {}).get(path, {})
        method_obj = path_obj.get(method.lower(), {})
        responses = method_obj.get("responses", {})
        success_response = responses.get("200", {})
        content = success_response.get("content", {})
        json_content = content.get("application/json", {})
        schema = json_content.get("schema", {})

        return schema
    except Exception:
        return {}


def extract_request_body_schema(openapi_data: Dict, path: str, method: str) -> Optional[Dict]:
    """从OpenAPI schema提取请求体结构"""
    try:
        path_obj = openapi_data.get("paths", {}).get(path, {})
        method_obj = path_obj.get(method.lower(), {})
        request_body = method_obj.get("requestBody", {})
        content = request_body.get("content", {})
        json_content = content.get("application/json", {})
        schema = json_content.get("schema", {})

        return schema
    except Exception:
        return None


def generate_contract_template(api: Dict, openapi_data: Dict) -> ContractTemplate:
    """为单个API生成契约模板"""
    # 基础信息
    template = ContractTemplate(
        api_id=api['api_id'],
        module=api['module'],
        path=api['path'],
        method=api['method'],
        summary=api.get('summary', ''),
        description=api.get('description', ''),
        tags=api.get('tags', []),
        priority=api.get('priority', 'P2'),
    )

    # 请求参数
    request_params = api.get('request_params', {})
    template.request_params = request_params

    # 从OpenAPI提取响应结构
    response_schema = extract_response_schema(
        openapi_data, api['path'], api['method']
    )
    if response_schema:
        template.response_data = {"schema": response_schema}

    # 提取请求体schema
    request_body_schema = extract_request_body_schema(
        openapi_data, api['path'], api['method']
    )
    if request_body_schema:
        template.request_params['body'] = {
            'in': 'body',
            'required': True,
            'schema': request_body_schema,
        }

    # 标准错误码
    template.error_codes = [
        {
            "code": "SUCCESS",
            "http_status": 200,
            "message": "操作成功",
        },
        {
            "code": "BAD_REQUEST",
            "http_status": 400,
            "message": "请求参数错误",
        },
        {
            "code": "UNAUTHORIZED",
            "http_status": 401,
            "message": "未授权访问",
        },
        {
            "code": "INTERNAL_SERVER_ERROR",
            "http_status": 500,
            "message": "服务器内部错误",
        },
    ]

    # 示例（基础结构）
    template.examples = {
        "request": {
            "params": {},
        },
        "response": {
            "success": True,
            "message": "操作成功",
            "data": None,
        },
    }

    # 元数据
    template.metadata = {
        "stable": api['priority'] == 'P0',
        "deprecated": False,
    }

    return template


def save_contract_file(contract: ContractTemplate, output_dir: Path):
    """保存单个契约文件"""
    # 按模块分组
    module_dir = output_dir / contract.module
    module_dir.mkdir(parents=True, exist_ok=True)

    # 文件名: api_id.yaml
    filename = f"{contract.api_id}.yaml"
    file_path = module_dir / filename

    # 转换为YAML并保存
    contract_dict = contract.to_dict()
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(contract_dict, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


def generate_contracts_index(contracts_dir: Path):
    """生成契约索引文件"""
    index = {
        "version": "1.0.0",
        "generated_at": datetime.now().isoformat(),
        "total_contracts": 0,
        "modules": {},
    }

    # 遍历所有模块目录
    if contracts_dir.exists():
        for module_dir in contracts_dir.iterdir():
            if module_dir.is_dir():
                contracts = list(module_dir.glob("*.yaml"))
                index["modules"][module_dir.name] = {
                    "path": f"contracts/{module_dir.name}",
                    "total_contracts": len(contracts),
                    "contracts": [c.stem for c in sorted(contracts)],
                }
                index["total_contracts"] += len(contracts)

    # 保存索引
    index_file = contracts_dir / "index.yaml"
    with open(index_file, 'w', encoding='utf-8') as f:
        yaml.dump(index, f, allow_unicode=True, default_flow_style=False)

    return index


def main():
    """主函数"""
    # 定义路径
    catalog_file = Path("docs/api/catalog.yaml")
    contracts_dir = Path("contracts")

    # 加载catalog
    apis = load_catalog(catalog_file)

    # 加载OpenAPI schema
    print("📖 加载OpenAPI schema...")
    openapi_data = load_openapi_schema()
    print(f"✓ OpenAPI schema已加载")

    # 为每个API生成契约
    print(f"\n🔨 生成契约模板...")
    success_count = 0
    for api in apis:
        try:
            contract = generate_contract_template(api, openapi_data)
            save_contract_file(contract, contracts_dir)
            success_count += 1

            if success_count % 50 == 0:
                print(f"  进度: {success_count}/{len(apis)}")
        except Exception as e:
            print(f"  ❌ 生成失败 {api['api_id']}: {e}")

    print(f"\n✓ 成功生成 {success_count}/{len(apis)} 个契约模板")

    # 生成索引
    print(f"\n📋 生成契约索引...")
    index = generate_contracts_index(contracts_dir)
    print(f"✓ 索引已生成: {contracts_dir}/index.yaml")
    print(f"  总计: {index['total_contracts']} 个契约")
    print(f"  模块数: {len(index['modules'])} 个")

    # 统计信息
    print(f"\n📊 契约模板统计:")
    for module_name, module_info in sorted(index['modules'].items()):
        print(f"  {module_name}: {module_info['total_contracts']} 个")

    print(f"\n📁 契约文件目录:")
    print(f"  {contracts_dir.absolute()}")


if __name__ == "__main__":
    main()
