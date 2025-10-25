#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MySQL到PostgreSQL迁移脚本

简洁实用的数据迁移工具
遵循原则: 简洁 > 复杂, 可维护 > 功能丰富

使用方法:
    python scripts/migrate_mysql_to_postgresql.py [--dry-run]

作者: MyStocks Team
日期: 2025-10-19
"""

import os
import sys
from datetime import datetime
import pymysql
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库配置
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

# MySQL到PostgreSQL类型映射
TYPE_MAPPING = {
    'int': 'INTEGER',
    'bigint': 'BIGINT',
    'varchar': 'VARCHAR',
    'text': 'TEXT',
    'datetime': 'TIMESTAMP',
    'date': 'DATE',
    'decimal': 'NUMERIC',
    'float': 'REAL',
    'double': 'DOUBLE PRECISION',
    'tinyint': 'SMALLINT',
}


def get_mysql_tables():
    """获取MySQL所有表"""
    conn = pymysql.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return tables


def get_table_structure(table_name):
    """获取MySQL表结构"""
    conn = pymysql.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()
    cursor.execute(f"DESCRIBE `{table_name}`")
    columns = cursor.fetchall()
    cursor.close()
    conn.close()
    return columns


def convert_mysql_type_to_postgres(mysql_type):
    """转换MySQL类型到PostgreSQL"""
    mysql_type_lower = mysql_type.lower()

    for mysql_prefix, pg_type in TYPE_MAPPING.items():
        if mysql_type_lower.startswith(mysql_prefix):
            # 仅VARCHAR保留长度信息，其他类型不保留
            if 'varchar' in mysql_type_lower and '(' in mysql_type:
                length = mysql_type[mysql_type.index('('):]
                return f"{pg_type}{length}"
            return pg_type

    # 默认返回TEXT
    return 'TEXT'


def create_postgresql_table(table_name, columns, dry_run=False):
    """在PostgreSQL中创建表"""
    # 生成CREATE TABLE语句
    column_defs = []
    for col in columns:
        col_name = col[0]
        col_type = convert_mysql_type_to_postgres(col[1])
        nullable = "NOT NULL" if col[2] == 'NO' else ""

        # 处理主键
        if col[3] == 'PRI':
            if 'int' in col[1].lower():
                column_defs.append(f"{col_name} SERIAL PRIMARY KEY")
            else:
                column_defs.append(f"{col_name} {col_type} PRIMARY KEY {nullable}")
        else:
            column_defs.append(f"{col_name} {col_type} {nullable}")

    create_sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        {','.join(column_defs)}
    );
    """

    print(f"  CREATE TABLE {table_name}")
    if dry_run:
        print(f"    [DRY-RUN] {create_sql[:100]}...")
        return

    # 执行创建
    conn = psycopg2.connect(**POSTGRES_CONFIG)
    cursor = conn.cursor()
    cursor.execute(create_sql)
    conn.commit()
    cursor.close()
    conn.close()


def migrate_table_data(table_name, dry_run=False):
    """迁移表数据"""
    # 从MySQL读取数据
    mysql_conn = pymysql.connect(**MYSQL_CONFIG)
    mysql_cursor = mysql_conn.cursor()
    mysql_cursor.execute(f"SELECT * FROM `{table_name}`")
    rows = mysql_cursor.fetchall()

    # 获取列名
    mysql_cursor.execute(f"DESCRIBE `{table_name}`")
    columns = [col[0] for col in mysql_cursor.fetchall()]

    mysql_cursor.close()
    mysql_conn.close()

    row_count = len(rows)
    print(f"  迁移 {row_count} 行数据")

    if dry_run or row_count == 0:
        if dry_run:
            print(f"    [DRY-RUN] 将迁移 {row_count} 行")
        return row_count

    # 插入到PostgreSQL
    pg_conn = psycopg2.connect(**POSTGRES_CONFIG)
    pg_cursor = pg_conn.cursor()

    # 使用execute_values批量插入
    insert_sql = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES %s"
    execute_values(pg_cursor, insert_sql, rows)

    pg_conn.commit()
    pg_cursor.close()
    pg_conn.close()

    return row_count


def verify_migration(table_name):
    """验证迁移结果"""
    # MySQL行数
    mysql_conn = pymysql.connect(**MYSQL_CONFIG)
    mysql_cursor = mysql_conn.cursor()
    mysql_cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
    mysql_count = mysql_cursor.fetchone()[0]
    mysql_cursor.close()
    mysql_conn.close()

    # PostgreSQL行数
    pg_conn = psycopg2.connect(**POSTGRES_CONFIG)
    pg_cursor = pg_conn.cursor()
    pg_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    pg_count = pg_cursor.fetchone()[0]
    pg_cursor.close()
    pg_conn.close()

    if mysql_count == pg_count:
        print(f"  ✓ 验证通过: {pg_count} 行")
        return True
    else:
        print(f"  ✗ 验证失败: MySQL={mysql_count}, PostgreSQL={pg_count}")
        return False


def main():
    """主函数"""
    dry_run = '--dry-run' in sys.argv

    print("=" * 70)
    print("MySQL → PostgreSQL 数据迁移")
    print("=" * 70)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"模式: {'DRY-RUN (仅模拟)' if dry_run else '正式迁移'}")
    print()

    # 获取所有表
    tables = get_mysql_tables()
    print(f"发现 {len(tables)} 个MySQL表")
    print()

    total_rows = 0
    success_tables = []
    failed_tables = []

    # 迁移每个表
    for i, table in enumerate(tables, 1):
        print(f"[{i}/{len(tables)}] 迁移表: {table}")

        try:
            # 获取表结构
            columns = get_table_structure(table)

            # 创建PostgreSQL表
            create_postgresql_table(table, columns, dry_run)

            # 迁移数据
            row_count = migrate_table_data(table, dry_run)
            total_rows += row_count

            # 验证（非dry-run模式）
            if not dry_run and row_count > 0:
                if verify_migration(table):
                    success_tables.append(table)
                else:
                    failed_tables.append(table)
            else:
                success_tables.append(table)

            print()

        except Exception as e:
            print(f"  ✗ 错误: {e}")
            failed_tables.append(table)
            print()

    # 总结
    print("=" * 70)
    print("迁移总结")
    print("=" * 70)
    print(f"总表数: {len(tables)}")
    print(f"成功: {len(success_tables)}")
    print(f"失败: {len(failed_tables)}")
    print(f"总行数: {total_rows}")
    print()

    if failed_tables:
        print("失败的表:")
        for table in failed_tables:
            print(f"  - {table}")
        print()

    print(f"完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    return len(failed_tables) == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
