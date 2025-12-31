#!/usr/bin/env python3
"""
API契约注册脚本
将增强后的契约注册到契约管理系统数据库
"""

import sys
import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))


class ContractRegistrar:
    """契约注册器"""

    def __init__(self):
        self.registered_count = 0
        self.failed_count = 0
        self.skipped_count = 0

    def load_contract(self, contract_file: Path) -> Dict[str, Any]:
        """加载契约文件"""
        with open(contract_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def generate_openapi_spec(self, contract: Dict[str, Any]) -> Dict[str, Any]:
        """从契约生成OpenAPI规范片段"""
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": f"{contract['module']} API",
                "version": contract.get('metadata', {}).get('version', '1.0.0'),
                "description": contract.get('description', ''),
            },
            "paths": {
                contract['path']: {
                    contract['method'].lower(): {
                        "summary": contract.get('summary', ''),
                        "description": contract.get('description', ''),
                        "tags": contract.get('tags', []),
                        "parameters": [],
                        "responses": {
                            "200": {
                                "description": "成功",
                                "content": {
                                    "application/json": {
                                        "schema": contract.get('response', {}).get('data_schema', {})
                                    }
                                }
                            }
                        },
                    }
                }
            },
        }

        # 添加请求参数
        for param_name, param_info in contract.get('request', {}).get('params', {}).items():
            if param_info.get('in') != 'body':
                param = {
                    "name": param_name,
                    "in": param_info.get('in', 'query'),
                    "required": param_info.get('required', False),
                    "description": param_info.get('description', ''),
                    "schema": {
                        "type": "string"
                    }
                }
                spec["paths"][contract["path"]][contract["method"].lower()]["parameters"].append(param)

        # 添加请求体
        if 'body' in contract.get('request', {}).get('params', {}):
            body_schema = contract['request']['params']['body'].get('schema', {})
            spec["paths"][contract["path"]][contract["method"].lower()]["requestBody"] = {
                "content": {
                    "application/json": {
                        "schema": body_schema
                    }
                }
            }

        # 添加错误响应
        error_codes = contract.get('response', {}).get('error_codes', [])
        for error in error_codes:
            http_status = str(error.get('http_status', 500))
            spec["paths"][contract["path"]][contract["method"].lower()]["responses"][http_status] = {
                "description": error.get('message', ''),
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "code": {"type": "integer"},
                                "message": {"type": "string"},
                                "data": {"type": "null"}
                            }
                        }
                    }
                }
            }

        return spec

    def register_contract_to_db(self, contract: Dict[str, Any]) -> bool:
        """
        注册契约到数据库

        注意：这是模拟注册，实际实现需要连接到contract模块的数据库
        """
        try:
            # 这里应该调用 contract 模块的服务来注册契约
            # 由于我们只是生成契约文件，这里模拟注册过程

            api_id = contract['api_id']
            module = contract['module']
            priority = contract['priority']
            version = contract.get('metadata', {}).get('version', '1.0.0')

            # 生成契约版本记录（模拟）
            contract_record = {
                "name": f"{module}-api-contract",
                "version": version,
                "api_id": api_id,
                "priority": priority,
                "spec": self.generate_openapi_spec(contract),
                "description": contract.get('summary', ''),
                "tags": contract.get('tags', []) + [priority],
                "is_active": True,
                "created_at": datetime.now().isoformat(),
            }

            # 保存到注册记录文件（模拟数据库）
            self._save_registration_record(contract_record)

            return True

        except Exception as e:
            print(f"  ❌ 注册失败 {api_id}: {e}")
            return False

    def _save_registration_record(self, record: Dict[str, Any]):
        """保存注册记录（模拟数据库存储）"""
        registration_dir = Path("web/backend/contracts/registered")
        registration_dir.mkdir(parents=True, exist_ok=True)

        api_id = record['api_id']
        record_file = registration_dir / f"{api_id}.json"

        with open(record_file, 'w', encoding='utf-8') as f:
            json.dump(record, f, indent=2, ensure_ascii=False)

    def generate_registration_index(self) -> Dict[str, Any]:
        """生成注册索引"""
        registration_dir = Path("web/backend/contracts/registered")
        if not registration_dir.exists():
            return {}

        index = {
            "generated_at": datetime.now().isoformat(),
            "total_registered": 0,
            "by_priority": {"P0": 0, "P1": 0, "P2": 0},
            "by_module": {},
            "contracts": [],
        }

        for record_file in registration_dir.glob("*.json"):
            with open(record_file, 'r') as f:
                record = json.load(f)

            index["total_registered"] += 1
            priority = record.get('priority', 'P2')
            index["by_priority"][priority] += 1

            module = record.get('name', '').split('-')[0]
            if module not in index["by_module"]:
                index["by_module"][module] = 0
            index["by_module"][module] += 1

            index["contracts"].append({
                "api_id": record["api_id"],
                "module": module,
                "priority": priority,
                "version": record["version"],
            })

        # 保存索引
        index_file = registration_dir / "index.json"
        with open(index_file, 'w') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)

        return index

    def register_all_contracts(self, contracts_dir: Path):
        """注册所有高优先级契约"""
        print(f"📝 注册高优先级契约到管理系统...")
        print(f"   源目录: {contracts_dir}\n")

        # 查找所有契约文件
        contract_files = list(contracts_dir.rglob("*.yaml"))
        contract_files = [f for f in contract_files if f.name != "index.yaml"]

        # 筛选高优先级契约
        p0_p1_files = []
        for contract_file in contract_files:
            try:
                contract = self.load_contract(contract_file)
                if contract.get('priority') in ['P0', 'P1']:
                    p0_p1_files.append((contract_file, contract))
            except Exception as e:
                print(f"  ⚠️  加载失败 {contract_file.name}: {e}")
                continue

        print(f"📋 发现 {len(p0_p1_files)} 个高优先级契约待注册\n")

        # 注册每个契约
        for i, (contract_file, contract) in enumerate(p0_p1_files, 1):
            # 检查是否已增强
            if contract.get('metadata', {}).get('enhanced_version'):
                success = self.register_contract_to_db(contract)
                if success:
                    self.registered_count += 1
                else:
                    self.failed_count += 1
            else:
                self.skipped_count += 1

            if i % 20 == 0:
                print(f"  进度: {i}/{len(p0_p1_files)} (注册: {self.registered_count}, 失败: {self.failed_count}, 跳过: {self.skipped_count})")

        # 生成索引
        print(f"\n📋 生成注册索引...")
        index = self.generate_registration_index()

        print(f"\n✅ 注册完成:")
        print(f"  总计: {len(p0_p1_files)} 个契约")
        print(f"  注册: {self.registered_count} 个")
        print(f"  失败: {self.failed_count} 个")
        print(f"  跳过: {self.skipped_count} 个 (未增强)")

        print(f"\n📊 注册统计:")
        print(f"  P0: {index['by_priority']['P0']} 个")
        print(f"  P1: {index['by_priority']['P1']} 个")
        print(f"  模块数: {len(index['by_module'])} 个")


def main():
    """主函数"""
    contracts_dir = Path("web/backend/contracts")

    if not contracts_dir.exists():
        print(f"❌ 契约目录不存在: {contracts_dir}")
        return

    # 创建注册器
    registrar = ContractRegistrar()

    # 注册所有契约
    registrar.register_all_contracts(contracts_dir)

    print(f"\n📁 注册记录位于: web/backend/contracts/registered/")


if __name__ == "__main__":
    main()
