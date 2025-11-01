#!/bin/bash
# 数据库完整备份脚本
# Week 2 Day 2 - 完整数据备份

set -e  # 遇到错误立即退出

BACKUP_BASE="/opt/claude/mystocks_backup"
BACKUP_DIR="$BACKUP_BASE/$(date +%Y%m%d_%H%M%S)"

echo "======================================================================"
echo "MyStocks 数据库备份工具"
echo "Week 2 Day 2 - 完整数据备份"
echo "======================================================================"
echo ""
echo "备份目录: $BACKUP_DIR"
echo ""

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 函数：检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 函数：备份成功标记
mark_success() {
    echo "[$1] ✓ 备份成功"
}

# 函数：备份失败标记
mark_failure() {
    echo "[$1] ✗ 备份失败: $2"
}

# ====================================================================
# 1. TDengine 备份
# ====================================================================
echo "1. 备份 TDengine..."
echo "----------------------------------------------------------------------"

if command_exists taosdump; then
    # 使用taosdump备份
    if taosdump -o "$BACKUP_DIR/tdengine" -A 2>&1 | tee "$BACKUP_DIR/tdengine_backup.log"; then
        mark_success "TDengine"
    else
        mark_failure "TDengine" "taosdump 执行失败"
    fi
else
    echo "  警告: taosdump 未安装，跳过TDengine备份"
    echo "  建议: 手动导出重要数据"
    mark_failure "TDengine" "taosdump 未安装"
fi

# ====================================================================
# 2. PostgreSQL 备份
# ====================================================================
echo ""
echo "2. 备份 PostgreSQL..."
echo "----------------------------------------------------------------------"

if command_exists pg_dump; then
    # 读取环境变量
    PGHOST="${POSTGRESQL_HOST:-localhost}"
    PGUSER="${POSTGRESQL_USER:-postgres}"
    PGDB="${POSTGRESQL_DATABASE:-mystocks}"

    # 备份所有数据库
    if pg_dump -h "$PGHOST" -U "$PGUSER" "$PGDB" > "$BACKUP_DIR/postgresql_${PGDB}.sql" 2>&1; then
        mark_success "PostgreSQL"
        # 压缩
        gzip "$BACKUP_DIR/postgresql_${PGDB}.sql"
    else
        mark_failure "PostgreSQL" "pg_dump 执行失败"
    fi

    # 备份schema only（快速）
    pg_dump -h "$PGHOST" -U "$PGUSER" -s "$PGDB" > "$BACKUP_DIR/postgresql_${PGDB}_schema.sql" 2>&1
else
    echo "  警告: pg_dump 未安装"
    mark_failure "PostgreSQL" "pg_dump 未安装"
fi

# ====================================================================
# 3. MySQL 备份
# ====================================================================
echo ""
echo "3. 备份 MySQL..."
echo "----------------------------------------------------------------------"

if command_exists mysqldump; then
    MYSQL_HOST="${MYSQL_HOST:-localhost}"
    MYSQL_USER="${MYSQL_USER:-root}"
    MYSQL_DB="${MYSQL_DATABASE:-mystocks}"

    # 备份数据
    if mysqldump -h "$MYSQL_HOST" -u "$MYSQL_USER" "$MYSQL_DB" > "$BACKUP_DIR/mysql_${MYSQL_DB}.sql" 2>&1; then
        mark_success "MySQL"
        # 压缩
        gzip "$BACKUP_DIR/mysql_${MYSQL_DB}.sql"
    else
        mark_failure "MySQL" "mysqldump 执行失败"
    fi

    # 备份schema only
    mysqldump -h "$MYSQL_HOST" -u "$MYSQL_USER" -d "$MYSQL_DB" > "$BACKUP_DIR/mysql_${MYSQL_DB}_schema.sql" 2>&1
else
    echo "  警告: mysqldump 未安装"
    mark_failure "MySQL" "mysqldump 未安装"
fi

# ====================================================================
# 4. Redis 备份
# ====================================================================
echo ""
echo "4. 备份 Redis..."
echo "----------------------------------------------------------------------"

if command_exists redis-cli; then
    # 使用SAVE命令创建RDB快照
    redis-cli SAVE >/dev/null 2>&1

    # 查找Redis RDB文件
    REDIS_RDB=$(redis-cli CONFIG GET dir | tail -1)/$(redis-cli CONFIG GET dbfilename | tail -1)

    if [ -f "$REDIS_RDB" ]; then
        cp "$REDIS_RDB" "$BACKUP_DIR/redis_dump.rdb"
        mark_success "Redis"
    else
        mark_failure "Redis" "找不到RDB文件: $REDIS_RDB"
    fi
else
    echo "  警告: redis-cli 未安装"
    mark_failure "Redis" "redis-cli 未安装"
fi

# ====================================================================
# 5. 配置文件和重要文件备份
# ====================================================================
echo ""
echo "5. 备份配置文件和重要文件..."
echo "----------------------------------------------------------------------"

# 备份配置文件
FILES_TO_BACKUP=(
    "table_config.yaml"
    ".env.example"
    "requirements.txt"
    "CLAUDE.md"
    "README.md"
)

for file in "${FILES_TO_BACKUP[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$BACKUP_DIR/"
        echo "  ✓ $file"
    else
        echo "  ✗ $file (不存在)"
    fi
done

mark_success "配置文件"

# ====================================================================
# 6. 生成备份元数据
# ====================================================================
echo ""
echo "6. 生成备份元数据..."
echo "----------------------------------------------------------------------"

cat > "$BACKUP_DIR/backup_metadata.txt" << EOF
MyStocks 数据库备份
=====================

备份时间: $(date '+%Y-%m-%d %H:%M:%S')
备份目录: $BACKUP_DIR
主机名: $(hostname)
用户: $(whoami)

数据库版本:
-----------
EOF

# 添加数据库版本信息
if command_exists psql; then
    echo "PostgreSQL: $(psql --version 2>/dev/null | head -1)" >> "$BACKUP_DIR/backup_metadata.txt"
fi

if command_exists mysql; then
    echo "MySQL: $(mysql --version 2>/dev/null | head -1)" >> "$BACKUP_DIR/backup_metadata.txt"
fi

if command_exists redis-cli; then
    echo "Redis: $(redis-cli --version 2>/dev/null | head -1)" >> "$BACKUP_DIR/backup_metadata.txt"
fi

if command_exists taos; then
    echo "TDengine: $(taos --version 2>/dev/null | head -1)" >> "$BACKUP_DIR/backup_metadata.txt"
fi

echo "" >> "$BACKUP_DIR/backup_metadata.txt"
echo "备份文件列表:" >> "$BACKUP_DIR/backup_metadata.txt"
echo "-----------" >> "$BACKUP_DIR/backup_metadata.txt"
ls -lh "$BACKUP_DIR" >> "$BACKUP_DIR/backup_metadata.txt"

mark_success "元数据"

# ====================================================================
# 7. 压缩备份
# ====================================================================
echo ""
echo "7. 压缩备份..."
echo "----------------------------------------------------------------------"

cd "$BACKUP_BASE"
ARCHIVE_NAME="$(basename $BACKUP_DIR).tar.gz"

if tar -czf "$ARCHIVE_NAME" "$(basename $BACKUP_DIR)" 2>&1; then
    mark_success "压缩"
    echo "  压缩文件: $BACKUP_BASE/$ARCHIVE_NAME"
    echo "  压缩大小: $(du -sh "$BACKUP_BASE/$ARCHIVE_NAME" | cut -f1)"
else
    mark_failure "压缩" "tar 执行失败"
fi

# ====================================================================
# 8. 备份总结
# ====================================================================
echo ""
echo "======================================================================"
echo "备份完成总结"
echo "======================================================================"

echo ""
echo "备份位置:"
echo "  原始目录: $BACKUP_DIR"
echo "  压缩文件: $BACKUP_BASE/$ARCHIVE_NAME"

echo ""
echo "备份大小:"
echo "  原始大小: $(du -sh "$BACKUP_DIR" | cut -f1)"
if [ -f "$BACKUP_BASE/$ARCHIVE_NAME" ]; then
    echo "  压缩大小: $(du -sh "$BACKUP_BASE/$ARCHIVE_NAME" | cut -f1)"
fi

echo ""
echo "验证备份:"
echo "  tar -tzf $BACKUP_BASE/$ARCHIVE_NAME | head -20"

echo ""
echo "恢复测试（可选）:"
echo "  mkdir -p /tmp/restore_test"
echo "  tar -xzf $BACKUP_BASE/$ARCHIVE_NAME -C /tmp/restore_test"

echo ""
echo "下一步:"
echo "  1. 验证备份完整性"
echo "  2. 将备份复制到远程位置（推荐）"
echo "  3. 进入Week 2 Day 3 - 数据分析"

echo ""
echo "======================================================================"
echo "备份工具执行完成"
echo "======================================================================"
