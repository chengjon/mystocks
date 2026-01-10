"""
Database Migration Script for DDD Tables
在真实 PostgreSQL 数据库中创建 DDD 系列表
"""
import sys
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# 确保路径
sys.path.append(os.getcwd())
load_dotenv()

from src.storage.database.database_manager import Base
# 导入所有模型以确保它们在 Base.metadata 中注册
from src.infrastructure.persistence.models import (
    StrategyModel, 
    OrderModel, 
    PortfolioModel, 
    PositionModel, 
    TransactionModel
)

def create_tables():
    # 尝试构建连接串
    db_url = os.getenv("MONITOR_DB_URL")
    if not db_url:
        host = os.getenv("POSTGRESQL_HOST", "localhost")
        port = os.getenv("POSTGRESQL_PORT", "5432")
        user = os.getenv("POSTGRESQL_USER", "postgres")
        pw = os.getenv("POSTGRESQL_PASSWORD", "")
        db = os.getenv("POSTGRESQL_DATABASE", "mystocks")
        db_url = f"postgresql://{user}:{pw}@{host}:{port}/{db}"

    print(f"Connecting to: {db_url.split('@')[-1]}")
    
    try:
        # 使用 PostgreSQL
        engine = create_engine(db_url)
        
        # 打印即将创建的表
        print("\nTables to be created:")
        for table in Base.metadata.tables.keys():
            if table.startswith("ddd_"):
                print(f" - {table}")
        
        # 创建表
        Base.metadata.create_all(engine)
        print("\n✅ Success: All DDD tables created successfully in PostgreSQL.")
        
    except Exception as e:
        print(f"\n❌ Failed to create tables: {e}")

if __name__ == "__main__":
    create_tables()
