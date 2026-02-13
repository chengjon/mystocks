"""
Pytest 配置文件 - 项目根目录

此文件用于配置 pytest 的全局行为，包括：
1. 设置 PYTHONPATH
2. 定义共享 fixtures
3. 配置测试钩子
"""
import sys
from pathlib import Path

# 排除有问题的目录，防止 pytest 收集
collect_ignore = [
    "scripts/",
    "smart_ai_tests/",
    "src/gpu/api_system/tests/",
    "src/storage/database/test_jupyter_compatibility.py",
    "src/storage/database/test_multi_directory.py",
    "src/storage/database/test_tdengine.py",
    "src/adapters/test_financial_adapter.py",
    "src/interfaces/adapters/test_financial_adapter.py",
    "tests/test_esm_compatibility.py",
    "tests/unit/storage/access/test_base.py",
    "web/backend/scripts/",
    "web/backend/tests/test_data_source_factory.py",
    "services/a-stock-realtime/test_client.py",
]

collect_ignore_glob = [
    "*_real.py",
    "scripts/**/*.py",
    "smart_ai_tests/**/*.py",
]

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 添加 src 目录到 Python 路径
src_dir = project_root / 'src'
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))


def pytest_configure(config):
    """Pytest 配置钩子"""
    # 设置自定义标记
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "network: marks tests requiring network access"
    )
    config.addinivalue_line(
        "markers", "gpu: marks tests requiring GPU support"
    )


def pytest_collection_modifyitems(config, items):
    """修改收集到的测试项"""
    for item in items:
        # 自动为慢速测试添加 slow 标记
        if "slow" in item.nodeid.lower():
            item.add_marker(pytest.mark.slow)

        # 自动为网络测试添加 network 标记
        if "network" in item.nodeid.lower() or "external" in item.nodeid.lower():
            item.add_marker(pytest.mark.network)


# 导入 pytest
import pytest
