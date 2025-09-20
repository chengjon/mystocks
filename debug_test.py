import sys
import os

# 强制刷新输出
sys.stdout.flush()

print("=" * 50)
print("DEBUG测试开始")
print("=" * 50)
sys.stdout.flush()

# 检查Python版本
print(f"Python版本: {sys.version}")
sys.stdout.flush()

# 检查当前工作目录
print(f"当前工作目录: {os.getcwd()}")
sys.stdout.flush()

# 检查项目目录是否存在
project_path = r"d:/MyData/GITHUB/mystocks"
print(f"项目目录是否存在: {os.path.exists(project_path)}")
sys.stdout.flush()

# 列出项目目录内容
if os.path.exists(project_path):
    print("项目目录内容:")
    for item in os.listdir(project_path):
        print(f"  {item}")
sys.stdout.flush()

# 检查adapters目录
adapters_path = os.path.join(project_path, "adapters")
print(f"adapters目录是否存在: {os.path.exists(adapters_path)}")
sys.stdout.flush()

if os.path.exists(adapters_path):
    print("adapters目录内容:")
    for item in os.listdir(adapters_path):
        print(f"  {item}")
sys.stdout.flush()

# 检查customer_adapter.py文件
customer_adapter_path = os.path.join(adapters_path, "customer_adapter.py")
print(f"customer_adapter.py文件是否存在: {os.path.exists(customer_adapter_path)}")
sys.stdout.flush()

# 尝试读取文件内容
if os.path.exists(customer_adapter_path):
    try:
        with open(customer_adapter_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"customer_adapter.py文件大小: {len(content)} 字符")
            sys.stdout.flush()
    except Exception as e:
        print(f"读取customer_adapter.py文件失败: {e}")
        sys.stdout.flush()

print("=" * 50)
print("DEBUG测试结束")
print("=" * 50)
sys.stdout.flush()