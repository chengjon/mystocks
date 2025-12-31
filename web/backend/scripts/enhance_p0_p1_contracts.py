#!/usr/bin/env python3
"""
高优先级API契约增强脚本
为P0和P1 API添加详细的请求/响应结构、Pydantic模型和示例
"""

import json
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime


class ContractEnhancer:
    """契约增强器"""

    def __init__(self):
        self.openapi_data = self._load_openapi()
        self.error_codes = self._load_error_codes()
        self.enhanced_count = 0
        self.skipped_count = 0

    def _load_openapi(self) -> Dict:
        """加载OpenAPI schema"""
        openapi_file = Path("/tmp/openapi.json")
        if openapi_file.exists():
            with open(openapi_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _load_error_codes(self) -> Dict[str, Any]:
        """加载错误码定义"""
        error_codes = {
            "SUCCESS": {"code": 0, "http_status": 200, "message": "操作成功"},
            "BAD_REQUEST": {"code": 1000, "http_status": 400, "message": "请求参数错误"},
            "VALIDATION_ERROR": {"code": 1001, "http_status": 422, "message": "输入参数验证失败"},
            "UNAUTHORIZED": {"code": 6001, "http_status": 401, "message": "未授权访问"},
            "FORBIDDEN": {"code": 6002, "http_status": 403, "message": "禁止访问"},
            "NOT_FOUND": {"code": 2004, "http_status": 404, "message": "资源不存在"},
            "INTERNAL_SERVER_ERROR": {"code": 9000, "http_status": 500, "message": "服务器内部错误"},
            "EXTERNAL_SERVICE_ERROR": {"code": 9001, "http_status": 502, "message": "外部服务错误"},
        }
        return error_codes

    def extract_schema_structure(self, schema: Dict, indent: int = 0) -> Dict[str, Any]:
        """递归提取schema结构"""
        if not schema or not isinstance(schema, dict):
            return {}

        schema_type = schema.get('type')
        ref = schema.get('$ref')

        # 处理$ref引用
        if ref:
            ref_name = ref.split('/')[-1]
            return {"$ref": ref_name, "type": "object"}

        # 处理object类型
        if schema_type == 'object':
            properties = schema.get('properties', {})
            required = schema.get('required', [])

            result = {
                "type": "object",
                "properties": {},
                "required_fields": required,
            }

            for prop_name, prop_schema in properties.items():
                result["properties"][prop_name] = self.extract_schema_structure(prop_schema, indent + 1)

            return result

        # 处理array类型
        elif schema_type == 'array':
            items = schema.get('items', {})
            return {
                "type": "array",
                "items": self.extract_schema_structure(items, indent + 1),
            }

        # 处理基本类型
        else:
            result = {"type": schema_type}

            if 'description' in schema:
                result['description'] = schema['description']

            if 'enum' in schema:
                result['enum'] = schema['enum']

            if 'format' in schema:
                result['format'] = schema['format']

            if 'default' in schema:
                result['default'] = schema['default']

            return result

    def get_response_schema(self, path: str, method: str) -> Optional[Dict]:
        """从OpenAPI获取响应schema"""
        try:
            path_obj = self.openapi_data.get("paths", {}).get(path, {})
            method_obj = path_obj.get(method.lower(), {})
            responses = method_obj.get("responses", {})
            success_response = responses.get("200", {})

            # 检查是否是UnifiedResponse格式
            content = success_response.get("content", {})
            json_content = content.get("application/json", {})
            schema = json_content.get("schema", {})

            return schema if schema else None
        except Exception:
            return None

    def get_request_body_schema(self, path: str, method: str) -> Optional[Dict]:
        """从OpenAPI获取请求体schema"""
        try:
            path_obj = self.openapi_data.get("paths", {}).get(path, {})
            method_obj = path_obj.get(method.lower(), {})
            request_body = method_obj.get("requestBody")

            if not request_body:
                return None

            content = request_body.get("content", {})
            json_content = content.get("application/json", {})
            schema = json_content.get("schema", {})

            return schema if schema else None
        except Exception:
            return None

    def generate_example_from_schema(self, schema: Dict, data_type: str = "response") -> Any:
        """从schema生成示例数据"""
        if not schema:
            return None

        schema_type = schema.get('type')
        ref = schema.get('$ref')

        # 处理$ref引用
        if ref:
            # 简化处理：返回引用名称
            return f"<{ref.split('/')[-1]}>"

        # 处理object类型
        if schema_type == 'object':
            properties = schema.get('properties', {})
            example = {}
            for prop_name, prop_schema in properties.items():
                example[prop_name] = self.generate_example_from_schema(prop_schema, data_type)
            return example

        # 处理array类型
        elif schema_type == 'array':
            items = schema.get('items', {})
            item_example = self.generate_example_from_schema(items, data_type)
            return [item_example] if item_example else []

        # 处理基本类型
        else:
            if 'example' in schema:
                return schema['example']
            if 'default' in schema:
                return schema['default']

            # 根据类型返回默认示例
            type_examples = {
                'string': '',
                'integer': 0,
                'number': 0.0,
                'boolean': True,
            }
            return type_examples.get(schema_type, None)

    def enhance_contract(self, contract_file: Path) -> bool:
        """增强单个契约文件"""
        try:
            with open(contract_file, 'r', encoding='utf-8') as f:
                contract = yaml.safe_load(f)

            api_path = contract['path']
            method = contract['method']
            priority = contract['priority']

            # 只处理P0和P1
            if priority not in ['P0', 'P1']:
                return False

            enhanced = False

            # 1. 增强响应结构
            response_schema = self.get_response_schema(api_path, method)
            if response_schema:
                # 提取data字段的schema（如果使用UnifiedResponse）
                data_schema = response_schema.get('properties', {}).get('data', {})
                if data_schema:
                    extracted_schema = self.extract_schema_structure(data_schema)
                    if extracted_schema:
                        contract['response']['data_schema'] = extracted_schema
                        enhanced = True

            # 2. 增强请求体结构
            request_schema = self.get_request_body_schema(api_path, method)
            if request_schema:
                extracted_request = self.extract_schema_structure(request_schema)
                if extracted_request:
                    if 'body' not in contract['request']['params']:
                        contract['request']['params']['body'] = {}
                    contract['request']['params']['body']['schema'] = extracted_request
                    enhanced = True

            # 3. 增强示例
            if response_schema:
                example_data = self.generate_example_from_schema(
                    response_schema.get('properties', {}).get('data')
                )
                if example_data:
                    contract['examples']['response']['data'] = example_data
                    enhanced = True

            # 4. 添加详细的错误码映射
            if contract['module'] in ['market', 'strategy', 'trade', 'data']:
                # 为核心模块添加更多错误码
                module_errors = self._get_module_specific_errors(contract['module'])
                if module_errors:
                    # 合并通用错误码和模块特定错误码
                    existing_codes = {e['code'] for e in contract['response']['error_codes']}
                    for error in module_errors:
                        if error['code'] not in existing_codes:
                            contract['response']['error_codes'].append(error)
                    enhanced = True

            # 5. 添加Pydantic模型引用
            pydantic_models = self._get_pydantic_models(contract['module'], api_path, method)
            if pydantic_models:
                contract['pydantic_models'] = pydantic_models
                enhanced = True

            # 6. 添加速率限制信息
            if priority == 'P0':
                contract['rate_limit'] = {
                    "default": "100/minute",
                    "burst": "200/minute",
                }
                enhanced = True

            # 7. 添加缓存策略
            cache_policy = self._get_cache_policy(contract['module'], api_path)
            if cache_policy:
                contract['cache'] = cache_policy
                enhanced = True

            if enhanced:
                # 更新元数据
                contract['metadata']['enhanced_at'] = datetime.now().isoformat()
                contract['metadata']['enhanced_version'] = "2.0"

                # 保存增强后的契约
                with open(contract_file, 'w', encoding='utf-8') as f:
                    yaml.dump(contract, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

                self.enhanced_count += 1
                return True
            else:
                self.skipped_count += 1
                return False

        except Exception as e:
            print(f"  ❌ 增强失败 {contract_file.name}: {e}")
            return False

    def _get_module_specific_errors(self, module: str) -> List[Dict[str, Any]]:
        """获取模块特定错误码"""
        module_error_map = {
            'market': [
                {"code": "MARKET_DATA_NOT_FOUND", "http_status": 404, "message": "行情数据不存在"},
                {"code": "MARKET_DATA_UNAVAILABLE", "http_status": 503, "message": "行情服务暂时不可用"},
                {"code": "SYMBOL_INVALID", "http_status": 400, "message": "股票代码格式错误"},
            ],
            'strategy': [
                {"code": "STRATEGY_NOT_FOUND", "http_status": 404, "message": "策略不存在"},
                {"code": "STRATEGY_ALREADY_RUNNING", "http_status": 409, "message": "策略已在运行中"},
                {"code": "STRATEGY_PARAMETER_INVALID", "http_status": 400, "message": "策略参数无效"},
            ],
            'trade': [
                {"code": "ORDER_NOT_FOUND", "http_status": 404, "message": "订单不存在"},
                {"code": "INSUFFICIENT_FUNDS", "http_status": 400, "message": "资金不足"},
                {"code": "ORDER_REJECTED", "http_status": 403, "message": "订单被拒绝"},
            ],
            'data': [
                {"code": "DATA_SOURCE_ERROR", "http_status": 502, "message": "数据源错误"},
                {"code": "DATA_NOT_FOUND", "http_status": 404, "message": "数据不存在"},
            ],
        }
        return module_error_map.get(module, [])

    def _get_pydantic_models(self, module: str, path: str, method: str) -> Dict[str, str]:
        """获取Pydantic模型引用"""
        models = {}

        # 基于模块和路径推断模型名称
        if module == 'market':
            if '/stocks' in path:
                models['response'] = 'StockInfoList'
                models['request'] = 'StockQueryParams'
            elif '/kline' in path:
                models['response'] = 'KlineData'
                models['request'] = 'KlineQueryParams'
        elif module == 'strategy':
            if method == 'POST':
                models['request'] = 'StrategyCreateRequest'
            models['response'] = 'StrategyResponse'
        elif module == 'trade':
            if '/orders' in path:
                models['response'] = 'OrderResponse'
                models['request'] = 'OrderCreateRequest'

        return models

    def _get_cache_policy(self, module: str, path: str) -> Optional[Dict[str, Any]]:
        """获取缓存策略"""
        # 为GET请求的market和data模块添加缓存策略
        if module in ['market', 'data'] and path.startswith('/api/'):
            return {
                "enabled": True,
                "ttl": 60,  # 60秒
                "strategy": "LRU",
            }
        return None

    def enhance_all_contracts(self, contracts_dir: Path):
        """增强所有高优先级契约"""
        print(f"🔨 增强P0和P1优先级契约...")
        print(f"   目录: {contracts_dir}\n")

        # 查找所有契约文件
        contract_files = list(contracts_dir.rglob("*.yaml"))
        contract_files = [f for f in contract_files if f.name != "index.yaml"]

        # 筛选P0和P1契约
        p0_p1_files = []
        for contract_file in contract_files:
            try:
                with open(contract_file, 'r') as f:
                    contract = yaml.safe_load(f)
                    if contract.get('priority') in ['P0', 'P1']:
                        p0_p1_files.append(contract_file)
            except Exception:
                continue

        print(f"📋 发现 {len(p0_p1_files)} 个高优先级契约 (P0+P1)\n")

        # 增强每个契约
        for i, contract_file in enumerate(p0_p1_files, 1):
            self.enhance_contract(contract_file)

            if i % 20 == 0:
                print(f"  进度: {i}/{len(p0_p1_files)} (增强: {self.enhanced_count}, 跳过: {self.skipped_count})")

        print(f"\n✅ 增强完成:")
        print(f"  总计: {len(p0_p1_files)} 个高优先级契约")
        print(f"  增强: {self.enhanced_count} 个")
        print(f"  跳过: {self.skipped_count} 个")


def main():
    """主函数"""
    contracts_dir = Path("web/backend/contracts")

    if not contracts_dir.exists():
        print(f"❌ 契约目录不存在: {contracts_dir}")
        return

    # 创建增强器
    enhancer = ContractEnhancer()

    # 增强所有契约
    enhancer.enhance_all_contracts(contracts_dir)

    print(f"\n📁 增强后的契约位于: {contracts_dir.absolute()}")


if __name__ == "__main__":
    main()
