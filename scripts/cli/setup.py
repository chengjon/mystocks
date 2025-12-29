#!/usr/bin/env python3
"""
API契约管理CLI工具安装脚本
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8") if (this_directory / "README.md").exists() else ""

setup(
    name="api-contract-sync",
    version="1.0.0",
    author="MyStocks Team",
    author_email="team@example.com",
    description="API契约管理CLI工具 - 管理OpenAPI契约版本、差异检测、验证和同步",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/mystocks-api-contract",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.1.0",
        "rich>=13.0.0",
        "requests>=2.31.0",
        "PyYAML>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "api-contract-sync=api_contract_sync:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
