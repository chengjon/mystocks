# pylint: disable=import-error,no-name-in-module
import os

from database_manager import DatabaseTableManager, DatabaseType
from db_utils import create_databases_safely
from dotenv import load_dotenv

# 确保加载正确路径的.env文件
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(env_path)
print("环境变量加载完成")

# 初始化管理器
manager = DatabaseTableManager()
print("管理器初始化完成")

# 使用安全的数据库创建函数
create_databases_safely()

# 批量创建表 - 使用正确的配置文件路径
config_file = os.path.join(os.path.dirname(__file__), "table_config.yaml")
print(f"正在读取配置文件: {config_file}")
results = manager.batch_create_tables(config_file)
print("批量创建结果:", results)

# 单独创建表
columns = [
    {"name": "id", "type": "INT", "primary_key": True, "nullable": False},
    {"name": "data", "type": "VARCHAR", "length": 255, "nullable": True},
]

# 使用环境变量中配置的数据库，移除硬编码的连接参数
print("开始创建表...")
success = manager.create_table(
    DatabaseType.MYSQL,
    "test_db",  # 使用与table_config.yaml一致的数据库名
    "my_table",
    columns,
)
print(f"创建表结果: {success}")

# 修改表结构
alterations = [{"operation": "ADD", "name": "new_col", "type": "INT", "nullable": True}]

success = manager.alter_table(
    DatabaseType.MYSQL,
    "test_db",  # 使用与table_config.yaml一致的数据库名
    "my_table",
    alterations,
)

# 删除表
success = manager.drop_table(
    DatabaseType.MYSQL,
    "test_db",
    "my_table",  # 使用与table_config.yaml一致的数据库名
)

# 关闭所有连接
manager.close_all_connections()
