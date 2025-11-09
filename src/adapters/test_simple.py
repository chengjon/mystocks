"""
简化测试脚本，用于检查Customer适配器是否能正常导入和初始化
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

print("Python路径:")
for path in sys.path:
    print(f"  {path}")

print("\n尝试导入CustomerDataSource...")

try:
    from src.adapters.customer_adapter import CustomerDataSource

    print("✓ 成功导入CustomerDataSource")

    print("\n尝试创建CustomerDataSource实例...")
    try:
        customer_source = CustomerDataSource()
        print("✓ 成功创建CustomerDataSource实例")
        print(f"  efinance可用: {customer_source.efinance_available}")
        print(f"  easyquotation可用: {customer_source.easyquotation_available}")
    except Exception as e:
        print(f"✗ 创建CustomerDataSource实例失败: {e}")

except ImportError as e:
    print(f"✗ 导入CustomerDataSource失败: {e}")
    print("\n尝试直接从文件导入...")
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "customer_adapter",
            os.path.join(project_root, "adapters", "customer_adapter.py"),
        )
        customer_adapter_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(customer_adapter_module)
        CustomerDataSource = customer_adapter_module.CustomerDataSource
        print("✓ 通过文件导入成功")

        print("\n尝试创建CustomerDataSource实例...")
        customer_source = CustomerDataSource()
        print("✓ 成功创建CustomerDataSource实例")
        print(f"  efinance可用: {customer_source.efinance_available}")
        print(f"  easyquotation可用: {customer_source.easyquotation_available}")
    except Exception as e:
        print(f"✗ 直接文件导入也失败了: {e}")

print("\n测试完成。")
