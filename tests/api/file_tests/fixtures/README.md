# Test Data Fixtures for API File-Level Testing

> **参考指南说明**:
> 本文件用于说明测试目录中的使用方法、执行入口、部署步骤、操作手册或局部参考，帮助理解测试层面的实践方式。
> 其中的命令、路径、步骤与示例应与 `architecture/STANDARDS.md`、当前测试实现和最新验证结果一并核对，不应单独充当共享规则或当前状态的唯一事实来源。


# This directory contains test data fixtures for file-level API testing.
# Fixtures are organized by API module and provide consistent test data
# for isolated testing environments.

# File structure:
# fixtures/
# ├── market_data.json      # Market data test fixtures
# ├── strategy_data.json    # Strategy management test fixtures
# ├── risk_data.json        # Risk management test fixtures
# ├── trade_data.json       # Trading test fixtures
# ├── auth_data.json        # Authentication test fixtures
# └── announcement_data.json # Announcement test fixtures