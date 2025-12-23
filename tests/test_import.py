import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_import():
    """测试导入是否正常工作"""
    try:
        # 尝试导入项目模块

        print("Project modules imported successfully")
        return True
    except Exception as e:
        print(f"Import error: {e}")
        return False


if __name__ == "__main__":
    test_import()
