# 架构优化数据库备份策略

**版本**: 1.0
**生效日期**: 2025-10-25
**适用范围**: 002-arch-optimization 实施期间
**实施环境**: 远程数据库服务器 (192.168.123.104)

---

## 备份目标

在架构优化过程中，确保数据安全，支持任意时间点回滚，保证系统可恢复性。

---

## 数据库环境信息

### PostgreSQL (主数据库)
- **服务器**: 192.168.123.104:5438
- **版本**: PostgreSQL 17.6
- **数据库**: mystocks
- **用户**: postgres
- **扩展**: TimescaleDB (待在 T005 配置)
- **用途**: 所有非高频时序数据

### TDengine (时序数据库)
- **服务器**: 192.168.123.104:6030
- **版本**: TDengine 3.3.6.13
- **数据库**: market_data
- **用户**: root
- **用途**: 高频时序数据（tick、分钟线）

---

## 备份计划

### 1. PostgreSQL 备份

#### 全量备份（每日）

```bash
# 每天 00:00 执行
BACKUP_DIR="/opt/claude/mystocks_backup/postgresql"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

PGPASSWORD="c790414J" pg_dump \
  -h 192.168.123.104 \
  -p 5438 \
  -U postgres \
  -d mystocks \
  -F c -b -v \
  -f ${BACKUP_DIR}/mystocks_${TIMESTAMP}.backup

# 保留最近7天的备份
find ${BACKUP_DIR} -name "mystocks_*.backup" -mtime +7 -delete
```

#### 关键时间点备份

执行以下关键节点的备份（永久保留）：

- ✅ **实施前**: `pre_arch_optimization_20251025.backup` (已完成)
- ⏳ **Phase 2完成后**: `post_phase2_YYYYMMDD.backup`
- ⏳ **US2数据迁移前**: `pre_us2_migration_YYYYMMDD.backup`
- ⏳ **US2数据迁移后**: `post_us2_migration_YYYYMMDD.backup`
- ⏳ **US3架构优化前**: `pre_us3_refactor_YYYYMMDD.backup`
- ⏳ **US3架构优化后**: `post_us3_refactor_YYYYMMDD.backup`
- ⏳ **MVP完成**: `mvp_complete_YYYYMMDD.backup`
- ⏳ **实施完成**: `post_arch_optimization_YYYYMMDD.backup`

#### 执行备份命令

```bash
# 创建关键时间点备份
MILESTONE="phase2_complete"
DATE=$(date +%Y%m%d)
BACKUP_DIR="/opt/claude/mystocks_backup/postgresql/milestones"
mkdir -p ${BACKUP_DIR}

PGPASSWORD="c790414J" pg_dump \
  -h 192.168.123.104 \
  -p 5438 \
  -U postgres \
  -d mystocks \
  -F c -b -v \
  -f ${BACKUP_DIR}/${MILESTONE}_${DATE}.backup

echo "✅ 里程碑备份完成: ${MILESTONE}_${DATE}.backup"
```

---

### 2. TDengine 备份

#### 全量备份（每日）

```bash
# 每天 01:00 执行
BACKUP_DIR="/opt/claude/mystocks_backup/tdengine"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

taosdump \
  -h 192.168.123.104 \
  -P 6030 \
  -u root \
  -p taosdata \
  -o ${BACKUP_DIR}/tdengine_${TIMESTAMP} \
  -D market_data \
  -A

# 保留最近7天的备份
find ${BACKUP_DIR} -name "tdengine_*" -type d -mtime +7 -exec rm -rf {} \;
```

#### 关键时间点备份

```bash
# TDengine 关键里程碑备份
MILESTONE="phase2_complete"
DATE=$(date +%Y%m%d)
BACKUP_DIR="/opt/claude/mystocks_backup/tdengine/milestones"
mkdir -p ${BACKUP_DIR}

taosdump \
  -h 192.168.123.104 \
  -P 6030 \
  -u root \
  -p taosdata \
  -o ${BACKUP_DIR}/${MILESTONE}_${DATE} \
  -D market_data \
  -A

echo "✅ TDengine 里程碑备份完成: ${MILESTONE}_${DATE}"
```

---

### 3. 配置文件备份

```bash
# 每次修改配置后立即备份
CONFIG_BACKUP_DIR="/opt/claude/mystocks_backup/config"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p ${CONFIG_BACKUP_DIR}

# 备份关键配置文件
cp .env ${CONFIG_BACKUP_DIR}/.env.${TIMESTAMP}
cp table_config.yaml ${CONFIG_BACKUP_DIR}/table_config.yaml.${TIMESTAMP}
cp -r config/ ${CONFIG_BACKUP_DIR}/config_${TIMESTAMP}/

echo "✅ 配置文件备份完成: ${TIMESTAMP}"
```

---

## 恢复测试

### 每周执行恢复测试（每周五）

#### PostgreSQL 恢复测试

```bash
# 1. 创建测试数据库
PGPASSWORD="c790414J" psql \
  -h 192.168.123.104 \
  -p 5438 \
  -U postgres \
  -c "DROP DATABASE IF EXISTS mystocks_test;"

PGPASSWORD="c790414J" psql \
  -h 192.168.123.104 \
  -p 5438 \
  -U postgres \
  -c "CREATE DATABASE mystocks_test;"

# 2. 恢复最新备份
LATEST_BACKUP=$(ls -t /opt/claude/mystocks_backup/postgresql/mystocks_*.backup | head -1)

PGPASSWORD="c790414J" pg_restore \
  -h 192.168.123.104 \
  -p 5438 \
  -U postgres \
  -d mystocks_test \
  ${LATEST_BACKUP}

# 3. 验证表数量和数据
PGPASSWORD="c790414J" psql \
  -h 192.168.123.104 \
  -p 5438 \
  -U postgres \
  -d mystocks_test \
  -c "SELECT COUNT(*) as table_count FROM pg_tables WHERE schemaname='public';"

# 4. 清理测试数据库
PGPASSWORD="c790414J" psql \
  -h 192.168.123.104 \
  -p 5438 \
  -U postgres \
  -c "DROP DATABASE mystocks_test;"

echo "✅ PostgreSQL 恢复测试通过"
```

#### TDengine 恢复测试

```bash
# 1. 创建测试数据库
taos -h 192.168.123.104 -P 6030 -u root -p taosdata \
  -s "DROP DATABASE IF EXISTS market_data_test;"

taos -h 192.168.123.104 -P 6030 -u root -p taosdata \
  -s "CREATE DATABASE market_data_test;"

# 2. 恢复最新备份
LATEST_BACKUP=$(ls -td /opt/claude/mystocks_backup/tdengine/tdengine_* | head -1)

taosdump \
  -h 192.168.123.104 \
  -P 6030 \
  -u root \
  -p taosdata \
  -i ${LATEST_BACKUP} \
  -D market_data_test

# 3. 验证数据
taos -h 192.168.123.104 -P 6030 -u root -p taosdata \
  -s "USE market_data_test; SHOW TABLES;"

# 4. 清理测试数据库
taos -h 192.168.123.104 -P 6030 -u root -p taosdata \
  -s "DROP DATABASE market_data_test;"

echo "✅ TDengine 恢复测试通过"
```

---

## 备份存储策略

### 存储位置

- **主存储**: `/opt/claude/mystocks_backup/` (本地开发机)
- **远程存储**: 建议配置 NFS/CIFS 挂载到远程存储服务器
- **云存储**: 可选，推荐阿里云OSS或腾讯云COS (成本约0.12元/GB/月)

### 保留策略

| 备份类型 | 保留时间 | 存储位置 |
|---------|---------|---------|
| **每日全量备份** | 7天 | 本地 |
| **关键里程碑备份** | 永久 | 本地 + 远程 |
| **配置文件备份** | 30天 | 本地 |

### 存储空间预估

- PostgreSQL 备份: ~100MB/天 × 7天 = 700MB
- TDengine 备份: ~500MB/天 × 7天 = 3.5GB
- 里程碑备份: ~600MB × 8个 = 4.8GB
- **总计**: ~9GB (本地存储充足)

---

## 紧急恢复流程

### 场景 1: 数据损坏

**步骤**:
1. **立即停止所有服务**
   ```bash
   # 停止后端服务
   pkill -f "uvicorn"
   pkill -f "python.*main.py"
   ```

2. **评估损坏范围**
   ```bash
   # 检查数据库连接
   PGPASSWORD="c790414J" psql -h 192.168.123.104 -p 5438 -U postgres -d mystocks -c "\dt"
   ```

3. **选择恢复点**（选择最近的可用备份）
   ```bash
   ls -lht /opt/claude/mystocks_backup/postgresql/
   ```

4. **执行恢复**
   ```bash
   BACKUP_FILE="/path/to/backup.backup"

   # PostgreSQL恢复
   PGPASSWORD="c790414J" pg_restore \
     -h 192.168.123.104 \
     -p 5438 \
     -U postgres \
     -d mystocks \
     -c \
     ${BACKUP_FILE}
   ```

5. **验证数据完整性**
   ```bash
   # 运行数据质量检查
   python -c "from monitoring.data_quality_monitor import DataQualityMonitor; monitor = DataQualityMonitor(); monitor.run_all_checks()"
   ```

6. **恢复服务**
   ```bash
   # 重启服务
   cd /opt/claude/mystocks_spec/web/backend
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

---

### 场景 2: 代码回滚

**步骤**:
1. **Git回滚到备份时间点**
   ```bash
   # 查看提交历史
   git log --oneline --since="2025-10-25"

   # 回滚到指定commit
   git reset --hard <commit-hash>
   ```

2. **恢复配置文件**
   ```bash
   cp /opt/claude/mystocks_backup/config/.env.20251025_120000 .env
   ```

3. **恢复数据库**（参考场景1）

4. **测试系统功能**
   ```bash
   pytest tests/ -v
   ```

---

## 自动化备份脚本

### 创建每日备份脚本

```bash
# 创建脚本: scripts/daily_backup.sh
cat > scripts/daily_backup.sh << 'EOF'
#!/bin/bash
# 每日自动备份脚本

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="/opt/claude/mystocks_backup/logs/backup_${TIMESTAMP}.log"
mkdir -p $(dirname ${LOG_FILE})

exec > >(tee -a ${LOG_FILE})
exec 2>&1

echo "=== 开始每日备份: ${TIMESTAMP} ==="

# 1. PostgreSQL备份
echo "1. 备份 PostgreSQL..."
BACKUP_DIR="/opt/claude/mystocks_backup/postgresql"
mkdir -p ${BACKUP_DIR}

PGPASSWORD="c790414J" pg_dump \
  -h 192.168.123.104 \
  -p 5438 \
  -U postgres \
  -d mystocks \
  -F c -b -v \
  -f ${BACKUP_DIR}/mystocks_${TIMESTAMP}.backup

if [ $? -eq 0 ]; then
    echo "✅ PostgreSQL备份完成"
else
    echo "❌ PostgreSQL备份失败"
    exit 1
fi

# 2. TDengine备份
echo "2. 备份 TDengine..."
BACKUP_DIR="/opt/claude/mystocks_backup/tdengine"
mkdir -p ${BACKUP_DIR}

taosdump \
  -h 192.168.123.104 \
  -P 6030 \
  -u root \
  -p taosdata \
  -o ${BACKUP_DIR}/tdengine_${TIMESTAMP} \
  -D market_data \
  -A

if [ $? -eq 0 ]; then
    echo "✅ TDengine备份完成"
else
    echo "❌ TDengine备份失败"
    exit 1
fi

# 3. 清理旧备份（保留7天）
echo "3. 清理旧备份..."
find /opt/claude/mystocks_backup/postgresql -name "mystocks_*.backup" -mtime +7 -delete
find /opt/claude/mystocks_backup/tdengine -name "tdengine_*" -type d -mtime +7 -exec rm -rf {} \;
echo "✅ 旧备份清理完成"

# 4. 生成备份报告
echo ""
echo "=== 备份报告 ==="
echo "PostgreSQL备份数量: $(ls /opt/claude/mystocks_backup/postgresql/mystocks_*.backup 2>/dev/null | wc -l)"
echo "TDengine备份数量: $(ls -d /opt/claude/mystocks_backup/tdengine/tdengine_* 2>/dev/null | wc -l)"
echo "总存储占用: $(du -sh /opt/claude/mystocks_backup/ | awk '{print $1}')"
echo ""
echo "=== 备份完成: ${TIMESTAMP} ==="
EOF

chmod +x scripts/daily_backup.sh
echo "✅ 每日备份脚本已创建: scripts/daily_backup.sh"
```

### 配置Cron定时任务（可选）

```bash
# 添加到crontab
(crontab -l 2>/dev/null; echo "0 0 * * * /opt/claude/mystocks_spec/scripts/daily_backup.sh") | crontab -

# 查看crontab
crontab -l
```

---

## 责任人

| 角色 | 姓名 | 联系方式 | 职责 |
|------|------|---------|------|
| **实施负责人** | [待定] | - | 整体实施协调和决策 |
| **备份管理员** | [待定] | - | 执行备份、监控备份状态 |
| **DBA** | [待定] | - | 数据库恢复、性能优化 |
| **紧急联系人** | [待定] | - | 紧急情况响应 |

---

## 备份检查清单

### 每日检查
- [ ] PostgreSQL 备份成功
- [ ] TDengine 备份成功
- [ ] 备份日志无错误
- [ ] 存储空间充足 (>5GB)

### 每周检查（每周五）
- [ ] 恢复测试通过
- [ ] 备份文件可读取
- [ ] 旧备份正确清理
- [ ] 备份报告发送给相关人员

### 里程碑检查
- [ ] 关键时间点备份完成
- [ ] 备份文件已复制到远程存储
- [ ] 备份元数据记录完整
- [ ] 恢复流程文档已更新

---

## 附录：快速参考命令

```bash
# 立即执行全量备份
./scripts/daily_backup.sh

# 创建里程碑备份
MILESTONE="phase2_complete"
PGPASSWORD="c790414J" pg_dump -h 192.168.123.104 -p 5438 -U postgres -d mystocks \
  -F c -f /opt/claude/mystocks_backup/postgresql/milestones/${MILESTONE}_$(date +%Y%m%d).backup

# 查看最近的备份
ls -lht /opt/claude/mystocks_backup/postgresql/ | head -5

# 测试数据库连接
PGPASSWORD="c790414J" psql -h 192.168.123.104 -p 5438 -U postgres -d mystocks -c "SELECT 1;"

# 查看备份存储占用
du -sh /opt/claude/mystocks_backup/

# 紧急恢复（最新备份）
LATEST=$(ls -t /opt/claude/mystocks_backup/postgresql/mystocks_*.backup | head -1)
PGPASSWORD="c790414J" pg_restore -h 192.168.123.104 -p 5438 -U postgres -d mystocks -c ${LATEST}
```

---

**文档版本**: 1.0
**创建日期**: 2025-10-25
**最后更新**: 2025-10-25
**审核状态**: ✅ 已完成
**下次审查**: Phase 2 完成后
