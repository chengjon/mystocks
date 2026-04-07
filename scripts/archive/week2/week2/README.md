# Week 2 数据库评估脚本

> **历史归档说明**:
> 本文件属于脚本协作过程中的历史消息、归档记录或已处理通知，用于保留当时的沟通与流转痕迹。
> 它不代表当前待执行指令或实时状态；继续引用前应核对最新任务分配、当前目录内容与现行执行口径。


本目录包含Week 2数据库评估和备份所需的所有脚本。

## 📁 脚本列表

### 1. assess_databases.py
**用途**: 评估所有数据库的实际使用情况

**功能**:
- 连接TDengine, PostgreSQL, MySQL, Redis
- 统计每个数据库的数据量
- 统计表数量和行数
- 生成详细的JSON评估报告

**使用方法**:
```bash
cd /opt/claude/mystocks_spec
python3 scripts/week2/assess_databases.py
```

**输出**: `database_assessment_YYYYMMDD_HHMMSS.json`

---

### 2. backup_all_databases.sh
**用途**: 完整备份所有数据库

**功能**:
- 备份TDengine数据
- 备份PostgreSQL数据
- 备份MySQL数据
- 备份Redis数据
- 备份配置文件
- 压缩所有备份

**使用方法**:
```bash
cd /opt/claude/mystocks_spec
chmod +x scripts/week2/backup_all_databases.sh
./scripts/week2/backup_all_databases.sh
```

**输出**: `/opt/claude/mystocks_backup/YYYYMMDD_HHMMSS.tar.gz`

---

### 3. analyze_query_patterns.py
**用途**: 分析项目中的查询模式

**功能**:
- 扫描所有Python文件
- 提取数据库查询
- 统计查询类型
- 识别最常访问的表

**使用方法**:
```bash
cd /opt/claude/mystocks_spec
python3 scripts/week2/analyze_query_patterns.py
```

---

### 4. poc_test.sql
**用途**: PostgreSQL + TimescaleDB POC测试

**功能**:
- 创建TimescaleDB超表
- 测试插入性能
- 测试查询性能
- 对比TDengine性能

**使用方法**:
```bash
psql -U postgres -d mystocks -f scripts/week2/poc_test.sql
```

---

## 🚀 快速开始

### Day 1: 评估

```bash
# 1. 评估所有数据库
python3 scripts/week2/assess_databases.py

# 2. 分析查询模式
python3 scripts/week2/analyze_query_patterns.py
```

### Day 2: 备份

```bash
# 备份所有数据
chmod +x scripts/week2/backup_all_databases.sh
./scripts/week2/backup_all_databases.sh

# 验证备份
tar -tzf /opt/claude/mystocks_backup/YYYYMMDD_HHMMSS.tar.gz | head -20
```

### Day 5: POC测试

```bash
# 运行POC测试
psql -U postgres -d mystocks -f scripts/week2/poc_test.sql
```

---

## 📊 预期输出

执行完所有脚本后，应该得到：

1. **database_assessment_YYYYMMDD_HHMMSS.json** - 详细的数据库评估数据
2. **backup_YYYYMMDD_HHMMSS.tar.gz** - 完整的数据库备份
3. **query_patterns.txt** - 查询模式分析报告
4. **poc_results.txt** - POC测试结果

---

## ⚠️ 注意事项

### 权限要求
- 需要对所有数据库的读取权限
- 需要备份目录的写入权限
- backup脚本需要执行权限

### 磁盘空间
- 评估脚本: 几乎不占用额外空间
- 备份脚本: 需要至少2倍于当前数据量的空间
- 建议保留至少10GB空闲空间

### 运行时间
- assess_databases.py: 5-15分钟（取决于数据量）
- backup_all_databases.sh: 10-30分钟（取决于数据量）
- analyze_query_patterns.py: 2-5分钟
- poc_test.sql: 5-10分钟

---

## 🔧 故障排除

### 数据库连接失败
```bash
# 检查数据库服务状态
systemctl status postgresql
systemctl status mysql
systemctl status redis
systemctl status taosd  # TDengine

# 检查连接配置
cat .env
```

### 备份失败
```bash
# 检查磁盘空间
df -h

# 检查目录权限
ls -la /opt/claude/

# 手动创建备份目录
sudo mkdir -p /opt/claude/mystocks_backup
sudo chown $USER:$USER /opt/claude/mystocks_backup
```

### Python依赖缺失
```bash
# 安装必要的依赖
pip install pymysql psycopg2-binary redis taospy
```

---

**创建日期**: 2025-10-19
**维护者**: 重构团队
