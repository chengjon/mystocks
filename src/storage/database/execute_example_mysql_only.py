from database_manager import DatabaseTableManager, DatabaseType
import os
from dotenv import load_dotenv
from db_utils import create_databases_safely

# 确保加载正确路径的.env文件
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(env_path)
print("环境变量加载完成")

# 初始化管理器
manager = DatabaseTableManager()
print("管理器初始化完成")

# 使用安全的数据库创建函数
create_databases_safely()

# 创建仅包含MySQL的配置
mysql_only_config = """
tables:
  - database_type: "MySQL"
    database_name: "test_db"
    table_name: "test_table"
    columns:
      - name: "id"
        type: "INT"
        primary_key: true
        nullable: false
      - name: "name"
        type: "VARCHAR"
        length: 100
        nullable: false
      - name: "description"
        type: "TEXT"
        nullable: true
    # 连接参数将从环境变量中自动获取
"""

# 写入临时配置文件
temp_config_file = os.path.join(os.path.dirname(__file__), "mysql_only_config.yaml")
with open(temp_config_file, "w", encoding="utf-8") as f:
    f.write(mysql_only_config)

# 测试批量创建（仅MySQL）
print(f"正在读取MySQL配置文件: {temp_config_file}")
results = manager.batch_create_tables(temp_config_file)
print("批量创建结果:", results)

# 单独创建表测试
print("\n=== 单独创建表测试 ===")
columns = [
    {"name": "id", "type": "INT", "primary_key": True, "nullable": False},
    {"name": "data", "type": "VARCHAR", "length": 255, "nullable": True},
]

print("开始创建表...")
success = manager.create_table(DatabaseType.MYSQL, "test_db", "my_table", columns)
print(f"创建表结果: {success}")

# 修改表结构
print("\n=== 修改表结构测试 ===")
alterations = [{"operation": "ADD", "name": "new_col", "type": "INT", "nullable": True}]

success = manager.alter_table(DatabaseType.MYSQL, "test_db", "my_table", alterations)
print(f"修改表结果: {success}")

# 删除表
print("\n=== 删除表测试 ===")
success = manager.drop_table(DatabaseType.MYSQL, "test_db", "my_table")
print(f"删除表结果: {success}")

# 关闭所有连接
manager.close_all_connections()
print("\n=== 测试完成 ===")

# 清理临时文件
try:
    os.remove(temp_config_file)
    print("临时配置文件已清理")
except Exception:
    pass
