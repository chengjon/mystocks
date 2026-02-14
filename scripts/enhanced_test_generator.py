"""增强测试生成器 - 向后兼容入口"""
from test_generator import *  # noqa: F401, F403
from test_generator.main import main  # noqa: F401

if __name__ == "__main__":
    main()
