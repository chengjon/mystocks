# Week 2 数据库评估和备份计划

**日期**: 2025-10-20 开始
**状态**: 📋 待执行
**目标**: 评估当前4个数据库的实际使用情况，为简化架构做准备

---

## 🎯 Week 2 目标

根据EXECUTIVE_SUMMARY.md的建议，Week 2的核心任务：

1. ✅ **评估数据库实际使用** - 了解每个数据库的真实数据量和使用情况
2. ✅ **完整备份所有数据** - 确保数据安全，为后续迁移做准备
3. ✅ **分析查询模式** - 了解应用的实际数据访问需求
4. ✅ **制定迁移计划** - 基于评估结果制定详细的数据库简化方案
5. ✅ **验证方案可行性** - 通过POC验证PostgreSQL能否满足需求

---

## 📊 当前数据库状态（假设）

### 4个数据库

| 数据库 | 用途 | 预期数据量 | 实际数据量 | 状态 |
|--------|------|-----------|----------|------|
| **TDengine** | 高频时序数据 | 大量 | ❓ 待评估 | 待评估 |
| **PostgreSQL** | 历史分析数据 | 中等 | ❓ 待评估 | 待评估 |
| **MySQL** | 元数据/参考数据 | 小 | ❓ 待评估 | 待评估 |
| **Redis** | 缓存/实时数据 | 小 | ❓ 待评估 | 待评估 |

### 评估问题

根据架构审查，需要回答：

1. **数据量问题**
   - 实际存储了多少数据？
   - 是否真的需要4个数据库？
   - 数据增长速度如何？

2. **使用模式问题**
   - 哪些表/数据库被频繁使用？
   - 哪些是冷数据？
   - 查询模式是什么样的？

3. **性能需求问题**
   - 实际查询延迟要求是什么？
   - 是否真的需要毫秒级响应？
   - 并发用户数是多少？

---

## 📅 Week 2 详细计划

### Day 1 (周一): 数据库使用情况评估

**时间**: 3-4小时

#### 任务1: 连接和健康检查 (1小时)

```bash
# 检查所有数据库连接状态
python3 << 'EOF'
from db_manager.database_manager import DatabaseTableManager
from data_access import TDengineDataAccess, PostgreSQLDataAccess, MySQLDataAccess, RedisDataAccess

print("=== 数据库连接检查 ===")

# TDengine
try:
    td = TDengineDataAccess()
    print("✓ TDengine: 连接成功")
except Exception as e:
    print(f"✗ TDengine: {e}")

# PostgreSQL
try:
    pg = PostgreSQLDataAccess()
    print("✓ PostgreSQL: 连接成功")
except Exception as e:
    print(f"✗ PostgreSQL: {e}")

# MySQL
try:
    mysql = MySQLDataAccess()
    print("✓ MySQL: 连接成功")
except Exception as e:
    print(f"✗ MySQL: {e}")

# Redis
try:
    redis = RedisDataAccess()
    print("✓ Redis: 连接成功")
except Exception as e:
    print(f"✗ Redis: {e}")
EOF
```

**输出**: 数据库连接状态报告

#### 任务2: 数据量统计 (2小时)

创建评估脚本 `scripts/week2/assess_databases.py`:

```python
"""
数据库评估脚本
评估所有数据库的实际使用情况
"""
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from db_manager.database_manager import DatabaseTableManager
from data_access import TDengineDataAccess, PostgreSQLDataAccess, MySQLDataAccess, RedisDataAccess

class DatabaseAssessor:
    """数据库评估器"""

    def __init__(self):
        self.results = {}

    def assess_tdengine(self) -> Dict[str, Any]:
        """评估TDengine使用情况"""
        print("\n=== 评估 TDengine ===")

        try:
            td = TDengineDataAccess()

            # 获取数据库列表
            databases = td.execute("SHOW DATABASES")
            print(f"数据库数量: {len(databases)}")

            results = {
                "status": "success",
                "databases": [],
                "total_size_mb": 0,
                "total_rows": 0,
                "tables": []
            }

            # 评估每个数据库
            for db in databases:
                db_name = db[0]
                if db_name.startswith('information_schema') or db_name == 'performance_schema':
                    continue

                print(f"\n数据库: {db_name}")
                td.execute(f"USE {db_name}")

                # 获取表列表
                tables = td.execute("SHOW TABLES")
                print(f"  表数量: {len(tables)}")

                db_info = {
                    "name": db_name,
                    "table_count": len(tables),
                    "tables": []
                }

                # 评估每个表
                for table in tables:
                    table_name = table[0]

                    # 获取行数
                    try:
                        count_result = td.execute(f"SELECT COUNT(*) FROM {table_name}")
                        row_count = count_result[0][0] if count_result else 0

                        # 估算大小（简化）
                        sample = td.execute(f"SELECT * FROM {table_name} LIMIT 1")

                        table_info = {
                            "name": table_name,
                            "rows": row_count,
                            "estimated_size_mb": row_count * 0.001  # 粗略估计
                        }

                        db_info["tables"].append(table_info)
                        results["total_rows"] += row_count

                        print(f"    {table_name}: {row_count:,} 行")
                    except Exception as e:
                        print(f"    {table_name}: 评估失败 - {e}")

                results["databases"].append(db_info)

            return results

        except Exception as e:
            print(f"TDengine评估失败: {e}")
            return {"status": "error", "message": str(e)}

    def assess_postgresql(self) -> Dict[str, Any]:
        """评估PostgreSQL使用情况"""
        print("\n=== 评估 PostgreSQL ===")

        try:
            pg = PostgreSQLDataAccess()

            # 获取所有表
            query = """
                SELECT
                    schemaname,
                    tablename,
                    pg_total_relation_size(schemaname||'.'||tablename) as size_bytes,
                    n_live_tup as row_count
                FROM pg_stat_user_tables
                ORDER BY size_bytes DESC;
            """

            tables = pg.execute(query)

            results = {
                "status": "success",
                "total_size_mb": 0,
                "total_rows": 0,
                "tables": []
            }

            for table in tables:
                schema, name, size_bytes, rows = table
                size_mb = size_bytes / 1024 / 1024

                results["tables"].append({
                    "schema": schema,
                    "name": name,
                    "size_mb": round(size_mb, 2),
                    "rows": rows or 0
                })

                results["total_size_mb"] += size_mb
                results["total_rows"] += (rows or 0)

                print(f"  {schema}.{name}: {size_mb:.2f} MB, {rows:,} 行")

            print(f"\n总计: {results['total_size_mb']:.2f} MB, {results['total_rows']:,} 行")

            return results

        except Exception as e:
            print(f"PostgreSQL评估失败: {e}")
            return {"status": "error", "message": str(e)}

    def assess_mysql(self) -> Dict[str, Any]:
        """评估MySQL使用情况"""
        print("\n=== 评估 MySQL ===")

        try:
            mysql = MySQLDataAccess()

            # 获取当前数据库
            current_db = mysql.execute("SELECT DATABASE()")[0][0]
            print(f"当前数据库: {current_db}")

            # 获取表信息
            query = """
                SELECT
                    table_name,
                    table_rows,
                    data_length,
                    index_length
                FROM information_schema.TABLES
                WHERE table_schema = %s
                ORDER BY data_length DESC;
            """

            tables = mysql.execute(query, (current_db,))

            results = {
                "status": "success",
                "database": current_db,
                "total_size_mb": 0,
                "total_rows": 0,
                "tables": []
            }

            for table in tables:
                name, rows, data_len, index_len = table
                total_size = (data_len + index_len) / 1024 / 1024

                results["tables"].append({
                    "name": name,
                    "rows": rows or 0,
                    "size_mb": round(total_size, 2)
                })

                results["total_size_mb"] += total_size
                results["total_rows"] += (rows or 0)

                print(f"  {name}: {total_size:.2f} MB, {rows:,} 行")

            print(f"\n总计: {results['total_size_mb']:.2f} MB, {results['total_rows']:,} 行")

            return results

        except Exception as e:
            print(f"MySQL评估失败: {e}")
            return {"status": "error", "message": str(e)}

    def assess_redis(self) -> Dict[str, Any]:
        """评估Redis使用情况"""
        print("\n=== 评估 Redis ===")

        try:
            redis = RedisDataAccess()

            # 获取基本信息
            info = redis.client.info()

            # 获取key数量
            db_keys = redis.client.dbsize()

            # 获取内存使用
            used_memory = info.get('used_memory_human', 'Unknown')

            # 采样一些keys
            sample_keys = []
            for key in redis.client.scan_iter(count=10):
                key_type = redis.client.type(key).decode('utf-8')
                sample_keys.append({
                    "key": key.decode('utf-8') if isinstance(key, bytes) else key,
                    "type": key_type
                })
                if len(sample_keys) >= 100:
                    break

            results = {
                "status": "success",
                "total_keys": db_keys,
                "used_memory": used_memory,
                "sample_keys": sample_keys[:10]  # 只保存前10个样本
            }

            print(f"  总Key数量: {db_keys:,}")
            print(f"  内存使用: {used_memory}")
            print(f"  Key样本:")
            for key in sample_keys[:5]:
                print(f"    - {key['key']} ({key['type']})")

            return results

        except Exception as e:
            print(f"Redis评估失败: {e}")
            return {"status": "error", "message": str(e)}

    def generate_report(self):
        """生成评估报告"""
        print("\n" + "="*60)
        print("数据库评估报告")
        print("="*60)

        # 评估所有数据库
        self.results["tdengine"] = self.assess_tdengine()
        self.results["postgresql"] = self.assess_postgresql()
        self.results["mysql"] = self.assess_mysql()
        self.results["redis"] = self.assess_redis()

        # 生成总结
        print("\n" + "="*60)
        print("总结")
        print("="*60)

        total_size = 0
        total_rows = 0

        for db_name, db_result in self.results.items():
            if db_result.get("status") == "success":
                size = db_result.get("total_size_mb", 0)
                rows = db_result.get("total_rows", 0)
                total_size += size
                total_rows += rows

                print(f"\n{db_name.upper()}:")
                print(f"  大小: {size:.2f} MB")
                print(f"  行数: {rows:,}")

        print(f"\n总计:")
        print(f"  总大小: {total_size:.2f} MB")
        print(f"  总行数: {total_rows:,}")

        # 保存结果
        import json
        report_file = f"database_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"\n详细报告已保存到: {report_file}")

        return self.results


if __name__ == "__main__":
    assessor = DatabaseAssessor()
    assessor.generate_report()
```

**输出**: `database_assessment_YYYYMMDD_HHMMSS.json`

#### 任务3: 查询模式分析 (1小时)

创建 `scripts/week2/analyze_query_patterns.py`:

```python
"""
查询模式分析脚本
分析应用的实际数据访问需求
"""

import os
import sys
import re
from collections import Counter
from pathlib import Path

# 分析代码中的数据库查询
def analyze_query_patterns():
    """分析项目中的查询模式"""

    print("=== 查询模式分析 ===\n")

    # 查找所有Python文件
    py_files = list(Path('.').rglob('*.py'))

    queries = {
        "select": [],
        "insert": [],
        "update": [],
        "delete": [],
        "tdengine_specific": [],
        "redis_ops": []
    }

    # 数据库操作关键词
    patterns = {
        "select": r'SELECT\s+.*?FROM',
        "insert": r'INSERT\s+INTO',
        "update": r'UPDATE\s+\w+',
        "delete": r'DELETE\s+FROM',
        "tdengine": r'(CREATE\s+TABLE|STABLE|TAG)',
        "redis": r'(redis\.get|redis\.set|redis\.hget)'
    }

    for py_file in py_files:
        if 'test' in str(py_file) or '__pycache__' in str(py_file):
            continue

        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

                # 查找各类查询
                for pattern_name, pattern in patterns.items():
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        for match in matches:
                            queries.get(pattern_name, []).append({
                                "file": str(py_file),
                                "query": match
                            })
        except:
            pass

    # 统计
    print("查询类型统计:")
    print(f"  SELECT: {len(queries['select'])} 次")
    print(f"  INSERT: {len(queries['insert'])} 次")
    print(f"  UPDATE: {len(queries['update'])} 次")
    print(f"  DELETE: {len(queries['delete'])} 次")
    print(f"  TDengine特定: {len(queries['tdengine_specific'])} 次")
    print(f"  Redis操作: {len(queries['redis_ops'])} 次")

    # 分析最常访问的表
    tables = Counter()
    for q in queries['select']:
        match = re.search(r'FROM\s+(\w+)', q['query'], re.IGNORECASE)
        if match:
            tables[match.group(1)] += 1

    print("\n最常查询的表:")
    for table, count in tables.most_common(10):
        print(f"  {table}: {count} 次")

    return queries

if __name__ == "__main__":
    analyze_query_patterns()
```

**检查点**:
- [ ] 所有数据库连接状态
- [ ] 每个数据库的实际数据量
- [ ] 查询模式统计

---

### Day 2 (周二): 完整数据备份

**时间**: 4-5小时

#### 任务1: 创建备份脚本 (1小时)

创建 `scripts/week2/backup_all_databases.sh`:

```bash
#!/bin/bash
# 数据库完整备份脚本

BACKUP_DIR="/opt/claude/mystocks_backup/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "=== 数据库备份 ==="
echo "备份目录: $BACKUP_DIR"

# 1. TDengine 备份
echo -e "\n1. 备份 TDengine..."
# TDengine备份命令（需要根据实际情况调整）
# taosdump -o "$BACKUP_DIR/tdengine" -A

# 2. PostgreSQL 备份
echo -e "\n2. 备份 PostgreSQL..."
pg_dump -h localhost -U postgres mystocks > "$BACKUP_DIR/postgresql_mystocks.sql"

# 3. MySQL 备份
echo -e "\n3. 备份 MySQL..."
mysqldump -h localhost -u root mystocks > "$BACKUP_DIR/mysql_mystocks.sql"

# 4. Redis 备份
echo -e "\n4. 备份 Redis..."
redis-cli --rdb "$BACKUP_DIR/redis_dump.rdb"

# 5. 配置文件备份
echo -e "\n5. 备份配置文件..."
cp table_config.yaml "$BACKUP_DIR/"
cp .env.example "$BACKUP_DIR/"

# 压缩备份
echo -e "\n6. 压缩备份..."
tar -czf "$BACKUP_DIR.tar.gz" -C "$(dirname $BACKUP_DIR)" "$(basename $BACKUP_DIR)"

echo -e "\n备份完成！"
echo "备份位置: $BACKUP_DIR.tar.gz"
du -sh "$BACKUP_DIR.tar.gz"
```

#### 任务2: 执行备份 (2小时)

```bash
# 执行备份
chmod +x scripts/week2/backup_all_databases.sh
./scripts/week2/backup_all_databases.sh
```

#### 任务3: 验证备份 (1小时)

```bash
# 验证备份完整性
tar -tzf /opt/claude/mystocks_backup/YYYYMMDD_HHMMSS.tar.gz | head -20

# 检查备份大小
du -sh /opt/claude/mystocks_backup/
```

**检查点**:
- [ ] 所有数据库备份完成
- [ ] 备份文件完整性验证
- [ ] 备份大小记录
- [ ] 恢复测试（可选）

---

### Day 3 (周三): 数据量和查询模式分析

**时间**: 3-4小时

#### 任务1: 分析评估报告 (2小时)

```python
# 分析Day 1生成的评估报告
import json

with open('database_assessment_YYYYMMDD_HHMMSS.json', 'r') as f:
    data = json.load(f)

# 生成分析报告
print("=== 数据量分析 ===")
# 详细分析各数据库使用情况
```

#### 任务2: 性能基准测试 (2小时)

```python
# 测试关键查询的性能
# 记录响应时间
# 分析是否真的需要毫秒级响应
```

**检查点**:
- [ ] 数据量分析报告
- [ ] 性能基准数据
- [ ] 冷热数据识别

---

### Day 4 (周四): 制定数据库迁移计划

**时间**: 4-5小时

#### 基于评估结果制定方案

**方案A: 激进简化（推荐）**
```
4个数据库 → 1个 PostgreSQL + TimescaleDB

迁移策略:
1. TDengine → PostgreSQL + TimescaleDB (时序插件)
2. MySQL → PostgreSQL (统一到同一个数据库)
3. Redis → 按需保留或删除
```

**方案B: 保守简化**
```
4个数据库 → 2个

迁移策略:
1. MySQL → PostgreSQL (合并)
2. TDengine → 评估后决定是否保留
3. Redis → 按需保留
```

**输出**: WEEK2_MIGRATION_PLAN.md

---

### Day 5 (周五): POC验证

**时间**: 4-5小时

#### 验证PostgreSQL能否替代TDengine

```sql
-- 创建TimescaleDB超表
CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE stock_minute_test (
    time TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(20),
    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    close NUMERIC,
    volume BIGINT
);

SELECT create_hypertable('stock_minute_test', 'time');

-- 测试插入性能
-- 测试查询性能
-- 对比TDengine
```

**检查点**:
- [ ] PostgreSQL性能测试
- [ ] TimescaleDB测试
- [ ] 性能对比报告
- [ ] 迁移方案最终确定

---

## 📋 Week 2 交付物

### 文档

1. **DATABASE_ASSESSMENT_REPORT.md** - 数据库评估报告
2. **WEEK2_MIGRATION_PLAN.md** - 数据库迁移计划
3. **POC_VALIDATION_REPORT.md** - POC验证报告

### 数据

1. **database_assessment_YYYYMMDD.json** - 评估数据
2. **backup_YYYYMMDD.tar.gz** - 完整备份
3. **performance_baseline.json** - 性能基准

### 脚本

1. **scripts/week2/assess_databases.py** - 评估脚本
2. **scripts/week2/backup_all_databases.sh** - 备份脚本
3. **scripts/week2/poc_test.sql** - POC测试脚本

---

## ⚠️ 风险和注意事项

### 数据安全

1. ✅ 备份前验证存储空间充足
2. ✅ 多个备份副本（本地+远程）
3. ✅ 测试恢复流程

### 评估准确性

1. ✅ 在生产环境或接近生产的环境评估
2. ✅ 评估时考虑未来增长
3. ✅ 包含峰值时段的数据

### 决策依据

1. ✅ 基于实际数据，不是假设
2. ✅ 考虑团队技术能力
3. ✅ 考虑维护成本

---

## 📊 成功标准

Week 2结束时应达到：

- [ ] 所有数据库评估完成
- [ ] 完整备份已创建并验证
- [ ] 数据量和查询模式清晰
- [ ] 迁移计划已制定
- [ ] POC验证通过
- [ ] 团队对方案达成共识

---

## 🚀 下一步

Week 2完成后：
- Week 3-4: 执行核心重构
- Week 5: 数据库Schema简化
- Week 6-7: 数据迁移
- Week 8: 验收上线

---

**制定日期**: 2025-10-19
**预计开始**: 2025-10-20
**预计完成**: 2025-10-24
**负责人**: 重构团队

---

*Week 2是关键的评估和决策周，务必基于实际数据做决策。*
