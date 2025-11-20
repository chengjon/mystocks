#!/usr/bin/env python3
"""
创建新表脚本

根据cmd8.md的要求创建新表：
1. TDengine: minute_kline表（适配 TICK_DATA 高频时序数据特性）
2. PostgreSQL+TimescaleDB: industry_classify、concept_classify、stock_industry_concept表（适配 REFERENCE_DATA 静态参考数据特性）

创建日期: 2025-11-17
"""

import os
import sys
import pandas as pd
from datetime import datetime
from typing import Dict, Any

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.data_access.tdengine_access import TDengineDataAccess
from src.data_access.postgresql_access import PostgreSQLDataAccess


def create_tdengine_tables():
    """创建TDengine表"""
    print("开始创建TDengine表...")
    
    try:
        # 初始化TDengine访问对象
        td_access = TDengineDataAccess()
        
        # 创建minute_kline超表
        # 根据table_config.yaml中的定义
        schema = {
            'ts': 'TIMESTAMP',
            'open': 'FLOAT',
            'high': 'FLOAT',
            'low': 'FLOAT',
            'close': 'FLOAT',
            'volume': 'BIGINT',
            'amount': 'FLOAT'
        }
        
        tags = {
            'symbol': 'BINARY(20)',
            'frequency': 'BINARY(10)'
        }
        
        # 创建超表
        td_access.create_stable('minute_kline', schema, tags)
        print("✅ TDengine minute_kline超表创建成功")
        
        # 创建一些示例子表（可选）
        # 这里我们只创建超表，具体的子表会在数据插入时动态创建
        
    except Exception as e:
        print(f"❌ TDengine表创建失败: {e}")
        raise
    finally:
        # 关闭连接
        try:
            td_access.close()
        except:
            pass


def create_postgresql_tables():
    """创建PostgreSQL表"""
    print("开始创建PostgreSQL表...")
    
    try:
        # 初始化PostgreSQL访问对象
        pg_access = PostgreSQLDataAccess()
        
        # 1. 创建industry_classifications表
        industry_schema = {
            'industry_code': 'VARCHAR(20)',
            'industry_name': 'VARCHAR(100)',
            'stock_count': 'INTEGER',
            'up_count': 'INTEGER',
            'down_count': 'INTEGER',
            'leader_stock': 'VARCHAR(20)',
            'latest_price': 'NUMERIC(10,4)',
            'change_percent': 'NUMERIC(8,4)',
            'change_amount': 'NUMERIC(10,4)',
            'volume': 'BIGINT',
            'amount': 'NUMERIC(15,2)',
            'total_market_value': 'NUMERIC(20,2)',
            'turnover_rate': 'NUMERIC(8,4)',
            'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
        }
        
        pg_access.create_table('industry_classifications', industry_schema, 'industry_code')
        print("✅ PostgreSQL industry_classifications表创建成功")
        
        # 2. 创建concept_classifications表
        concept_schema = {
            'concept_code': 'VARCHAR(20)',
            'concept_name': 'VARCHAR(100)',
            'stock_count': 'INTEGER',
            'up_count': 'INTEGER',
            'down_count': 'INTEGER',
            'leader_stock': 'VARCHAR(20)',
            'latest_price': 'NUMERIC(10,4)',
            'change_percent': 'NUMERIC(8,4)',
            'change_amount': 'NUMERIC(10,4)',
            'volume': 'BIGINT',
            'amount': 'NUMERIC(15,2)',
            'total_market_value': 'NUMERIC(20,2)',
            'turnover_rate': 'NUMERIC(8,4)',
            'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
        }
        
        pg_access.create_table('concept_classifications', concept_schema, 'concept_code')
        print("✅ PostgreSQL concept_classifications表创建成功")
        
        # 3. 创建stock_industry_concept_relations表
        relation_schema = {
            'relation_id': 'BIGSERIAL PRIMARY KEY',
            'symbol': 'VARCHAR(20)',
            'category_type': 'VARCHAR(20)',
            'category_code': 'VARCHAR(20)',
            'category_name': 'VARCHAR(100)',
            'is_active': 'BOOLEAN DEFAULT TRUE',
            'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
        }
        
        pg_access.create_table('stock_industry_concept_relations', relation_schema)
        print("✅ PostgreSQL stock_industry_concept_relations表创建成功")
        
        # 创建索引
        try:
            conn = pg_access._get_connection()
            cursor = conn.cursor()
            
            # 为stock_industry_concept_relations表创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_stock_industry_concept_symbol ON stock_industry_concept_relations (symbol)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_stock_industry_concept_type ON stock_industry_concept_relations (category_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_stock_industry_concept_name ON stock_industry_concept_relations (category_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_stock_industry_concept_symbol_type ON stock_industry_concept_relations (symbol, category_type)")
            
            conn.commit()
            cursor.close()
            pg_access._return_connection(conn)
            print("✅ PostgreSQL索引创建成功")
        except Exception as e:
            print(f"⚠️  PostgreSQL索引创建警告: {e}")
            
    except Exception as e:
        print(f"❌ PostgreSQL表创建失败: {e}")
        raise
    finally:
        # 关闭连接
        try:
            pg_access.close()
        except:
            pass


def main():
    """主函数"""
    print("开始执行建表脚本...")
    print(f"当前时间: {datetime.now()}")
    print("=" * 50)
    
    try:
        # 创建TDengine表
        create_tdengine_tables()
        print()
        
        # 创建PostgreSQL表
        create_postgresql_tables()
        print()
        
        print("=" * 50)
        print("✅ 所有表创建成功!")
        
    except Exception as e:
        print("=" * 50)
        print(f"❌ 建表脚本执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()