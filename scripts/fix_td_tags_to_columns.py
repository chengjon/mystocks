#!/usr/bin/env python3
import taos
import sys

# Connect to TDengine
try:
    conn = taos.connect(
        host='192.168.123.104',
        port=6030,
        user='root',
        password='taosdata',
        database='market_data'
    )
    cursor = conn.cursor()
except Exception as e:
    print(f"Failed to connect to TDengine: {e}")
    sys.exit(1)

tables = [
    'minute_kline',
    'tick_data',
    'depth_data',
    'minute_kline_1min',
    'minute_kline_5min',
    'minute_kline_15min',
    'minute_kline_30min',
    'minute_kline_60min'
]

print("Starting migration: Converting txn_id and is_valid from TAGS to COLUMNS")

for table in tables:
    print(f"\nProcessing table: {table}")

    # 1. Drop Tags
    try:
        print("  Dropping TAG txn_id...")
        cursor.execute(f"ALTER STABLE {table} DROP TAG txn_id")
        print("  Success.")
    except Exception as e:
        print(f"  Failed/Skipped dropping txn_id tag: {e}")

    try:
        print("  Dropping TAG is_valid...")
        cursor.execute(f"ALTER STABLE {table} DROP TAG is_valid")
        print("  Success.")
    except Exception as e:
        print(f"  Failed/Skipped dropping is_valid tag: {e}")

    # 2. Add Columns
    try:
        print("  Adding COLUMN txn_id...")
        cursor.execute(f"ALTER STABLE {table} ADD COLUMN txn_id BINARY(64)")
        print("  Success.")
    except Exception as e:
        print(f"  Failed/Skipped adding txn_id column: {e}")

    try:
        print("  Adding COLUMN is_valid...")
        cursor.execute(f"ALTER STABLE {table} ADD COLUMN is_valid BOOL")
        print("  Success.")
    except Exception as e:
        print(f"  Failed/Skipped adding is_valid column: {e}")

print("\nMigration completed.")
cursor.close()
conn.close()
