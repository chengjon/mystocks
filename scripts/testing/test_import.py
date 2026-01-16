print("测试开始")
import sys
import os

# 添加项目根目录到Python路径
project_root = r"d:/MyData/GITHUB/mystocks"
sys.path.insert(0, project_root)

print("Python路径:")
for i, path in enumerate(sys.path):
    print(f"  {i}: {path}")

print("\n当前工作目录:", os.getcwd())

print("\n尝试导入...")
try:
    from src.adapters.customer_adapter import CustomerDataSource

    print("✓ 导入成功")

    print("\n尝试创建实例...")
    source = CustomerDataSource()
    print("✓ 实例创建成功")

except Exception as e:
    print(f"✗ 出现错误: {e}")
    import traceback

    traceback.print_exc()

print("测试结束")
