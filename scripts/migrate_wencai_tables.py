#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""迁移wencai问财表数据"""

import pymysql
import psycopg2
from psycopg2.extras import execute_values
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()

# 配置
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE'),
    'port': int(os.getenv('MYSQL_PORT', 3306))
}

POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRESQL_HOST'),
    'user': os.getenv('POSTGRESQL_USER'),
    'password': os.getenv('POSTGRESQL_PASSWORD'),
    'database': os.getenv('POSTGRESQL_DATABASE'),
    'port': int(os.getenv('POSTGRESQL_PORT', 5432))
}

def migrate_wencai_table(mysql_table, pg_table, column_map=None):
    """迁移问财表数据，支持列名映射"""
    # 从MySQL读取
    mysql_conn = pymysql.connect(**MYSQL_CONFIG)
    mysql_cursor = mysql_conn.cursor()
    mysql_cursor.execute(f"SELECT * FROM `{mysql_table}`")
    rows = mysql_cursor.fetchall()

    # 获取MySQL列名
    mysql_cursor.execute(f"DESCRIBE `{mysql_table}`")
    mysql_columns = [col[0] for col in mysql_cursor.fetchall()]

    # 应用列名映射
    if column_map:
        pg_columns = [column_map.get(col, col) for col in mysql_columns]
    else:
        pg_columns = mysql_columns

    mysql_cursor.close()
    mysql_conn.close()

    print(f"迁移 {mysql_table} -> {pg_table}: {len(rows)} 行")

    if len(rows) == 0:
        return

    # 插入到PostgreSQL
    pg_conn = psycopg2.connect(**POSTGRES_CONFIG)
    pg_cursor = pg_conn.cursor()

    insert_sql = f'INSERT INTO {pg_table} ({",".join(pg_columns)}) VALUES %s'
    execute_values(pg_cursor, insert_sql, rows)

    pg_conn.commit()
    pg_cursor.close()
    pg_conn.close()

    print(f"  ✓ 完成")

if __name__ == '__main__':
    # 迁移wencai_qs_1（列名映射：移除括号）
    print("=== 迁移wencai_qs_1 ===")
    migrate_wencai_table('wencai_qs_1', 'wencai_qs_1', {
        'a股市值(不含限售股)': 'a股市值'
    })

    # 迁移wencai_qs_2（列名映射：冒号改下划线）
    print("\n=== 迁移wencai_qs_2 ===")
    migrate_wencai_table('wencai_qs_2', 'wencai_qs_2', {
        '涨跌幅:前复权': '涨跌幅_前复权',
        '涨跌幅:前复权_2': '涨跌幅_前复权_2',
        '涨跌幅:前复权_3': '涨跌幅_前复权_3',
        '涨跌幅:前复权_4': '涨跌幅_前复权_4',
        '涨跌幅:前复权_5': '涨跌幅_前复权_5'
    })

    print("\n✓ 所有问财表数据迁移完成")
