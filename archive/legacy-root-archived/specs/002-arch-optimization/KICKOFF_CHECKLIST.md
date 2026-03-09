# 架构优化实施启动检查清单

**功能**: 002-arch-optimization
**日期**: 2025-10-25
**状态**: 准备启动

---

## ✅ 启动前检查（5分钟）

### 1. 环境检查

```bash
# 检查Python版本
python --version
# 预期: Python 3.12.x

# 检查conda环境
conda info --envs
# 预期: stock环境存在

# 激活环境
conda activate stock

# 检查关键依赖
pip list | grep -E "pandas|psycopg2|taospy|akshare|loguru"
```

**通过标准**:
- ✅ Python 3.12.x
- ✅ pandas ≥2.0.0
- ✅ psycopg2-binary ≥2.9.5
- ✅ taospy ≥2.7.2 (或taosws ≥0.3.0)
- ✅ akshare ≥1.12.0
- ✅ loguru ≥0.7.0

---

### 2. 数据库检查

```bash
# 检查PostgreSQL
psql -h localhost -U mystocks_user -d mystocks -c "SELECT version();"

# 检查TDengine
taos -h localhost -s "SELECT server_version();"
```

**通过标准**:
- ✅ PostgreSQL 14+ 可连接
- ✅ TDengine 3.0+ 可连接
- ✅ TimescaleDB扩展已安装（执行T005后检查）

---

### 3. Git状态检查

```bash
# 查看当前分支
git branch

# 查看工作区状态
git status

# 查看未提交的修改
git diff --stat
```

**通过标准**:
- ✅ 在主分支或其他稳定分支
- ✅ 工作区干净（或已暂存）
- ✅ 无冲突文件

---

### 4. 磁盘空间检查

```bash
# 检查可用空间
df -h /opt/claude/

# 检查数据库存储
du -sh /opt/claude/mystocks_spec/
```

**通过标准**:
- ✅ 可用空间 ≥ 10GB
- ✅ 数据库有足够扩展空间

---

### 5. 文档确认

```bash
# 验证所有核心文档存在
ls -lh specs/002-arch-optimization/
```

**必需文档**:
- ✅ spec.md
- ✅ plan.md
- ✅ research.md
- ✅ data-model.md
- ✅ tasks.md (v2)
- ✅ quickstart.md
- ✅ IMPLEMENTATION_READY_SUMMARY.md
- ✅ contracts/ (目录，3个文件)

---

## 🚀 Phase 1启动（第一天）

### T001: 创建备份

```bash
# 创建时间戳
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p archive/pre_arch_optimization_${TIMESTAMP}

# 备份核心文件
cp core.py archive/pre_arch_optimization_${TIMESTAMP}/
cp unified_manager.py archive/pre_arch_optimization_${TIMESTAMP}/
cp data_access.py archive/pre_arch_optimization_${TIMESTAMP}/
cp -r factory/ archive/pre_arch_optimization_${TIMESTAMP}/
cp -r monitoring/ archive/pre_arch_optimization_${TIMESTAMP}/
cp -r adapters/ archive/pre_arch_optimization_${TIMESTAMP}/

# 备份数据库配置
cp .env archive/pre_arch_optimization_${TIMESTAMP}/.env.backup

# 创建备份清单
ls -lhR archive/pre_arch_optimization_${TIMESTAMP}/ > archive/pre_arch_optimization_${TIMESTAMP}/BACKUP_MANIFEST.txt

echo "✅ T001完成: 备份已创建于 archive/pre_arch_optimization_${TIMESTAMP}/"
```

**验收标准**:
- ✅ 备份目录存在
- ✅ 所有核心文件已备份
- ✅ 备份清单生成

---

### T002: 验证开发环境依赖

```bash
# 创建依赖检查脚本
cat > scripts/check_dependencies.sh << 'EOF'
#!/bin/bash
echo "=== 架构优化环境依赖检查 ==="
echo ""

# 检查Python版本
echo "1. Python版本:"
python --version
if [[ $(python -c 'import sys; print(sys.version_info >= (3,12))') == "True" ]]; then
    echo "   ✅ Python 3.12+"
else
    echo "   ❌ Python版本不足（需要3.12+）"
    exit 1
fi
echo ""

# 检查关键依赖
echo "2. 关键依赖包:"
packages=("pandas>=2.0.0" "psycopg2-binary>=2.9.5" "taospy>=2.7.2" "akshare>=1.12.0" "loguru>=0.7.0")

for pkg in "${packages[@]}"; do
    pkg_name=$(echo $pkg | cut -d'>' -f1)
    if pip show $pkg_name > /dev/null 2>&1; then
        version=$(pip show $pkg_name | grep Version | cut -d' ' -f2)
        echo "   ✅ $pkg_name ($version)"
    else
        echo "   ❌ $pkg_name 未安装"
        exit 1
    fi
done
echo ""

# 检查数据库连接
echo "3. 数据库连接:"

# PostgreSQL
if psql -h localhost -U mystocks_user -d mystocks -c "SELECT 1;" > /dev/null 2>&1; then
    echo "   ✅ PostgreSQL 可连接"
else
    echo "   ❌ PostgreSQL 连接失败"
    exit 1
fi

# TDengine
if taos -h localhost -s "SELECT 1;" > /dev/null 2>&1; then
    echo "   ✅ TDengine 可连接"
else
    echo "   ⚠️  TDengine 连接失败（将在T005配置）"
fi
echo ""

echo "=== 环境检查完成 ==="
EOF

chmod +x scripts/check_dependencies.sh
./scripts/check_dependencies.sh
```

**验收标准**:
- ✅ Python 3.12+
- ✅ 所有5个关键依赖已安装
- ✅ PostgreSQL可连接
- ⚠️ TDengine可连接（或标记待配置）

---

### T003: 配置Git钩子和代码质量工具

```bash
# 创建pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# 架构优化pre-commit hook

echo "运行pre-commit检查..."

# 1. PEP8格式检查（仅检查staged的Python文件）
PYTHON_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')

if [ -n "$PYTHON_FILES" ]; then
    echo "检查Python代码格式..."

    # 使用black检查（不自动修复）
    if command -v black &> /dev/null; then
        black --check $PYTHON_FILES
        if [ $? -ne 0 ]; then
            echo "❌ 代码格式不符合PEP8，请运行: black $PYTHON_FILES"
            exit 1
        fi
    fi

    # 类型注解检查（仅警告）
    echo "检查类型注解..."
    for file in $PYTHON_FILES; do
        if ! grep -q "from typing import" "$file" && ! grep -q "import typing" "$file"; then
            echo "⚠️  $file 可能缺少类型注解"
        fi
    done
fi

echo "✅ Pre-commit检查通过"
exit 0
EOF

chmod +x .git/hooks/pre-commit

# 安装代码质量工具（如果未安装）
pip install black isort mypy -q

echo "✅ T003完成: Git hooks已配置"
```

**验收标准**:
- ✅ pre-commit hook已创建
- ✅ black、isort、mypy已安装
- ✅ 测试提交触发检查

---

### T004: 创建数据库备份策略文档

```bash
# 创建备份策略文档
cat > docs/backup_strategy_arch_optimization.md << 'EOF'
# 架构优化数据库备份策略

**版本**: 1.0
**生效日期**: 2025-10-25
**适用范围**: 002-arch-optimization实施期间

## 备份目标

在架构优化过程中，确保数据安全，支持任意时间点回滚。

## 备份计划

### 1. PostgreSQL备份

**全量备份**:
```bash
# 每天00:00执行
BACKUP_DIR="/opt/claude/mystocks_backup/postgresql"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

pg_dump -h localhost -U mystocks_user -d mystocks \
  -F c -b -v \
  -f ${BACKUP_DIR}/mystocks_${TIMESTAMP}.backup

# 保留最近7天的备份
find ${BACKUP_DIR} -name "mystocks_*.backup" -mtime +7 -delete
```

**关键时间点备份**:
- ✅ 实施前: `pre_arch_optimization_20251025.backup`
- ⏳ Phase 2完成后: `post_phase2_YYYYMMDD.backup`
- ⏳ US2数据迁移前: `pre_mysql_migration_YYYYMMDD.backup`
- ⏳ US2数据迁移后: `post_mysql_migration_YYYYMMDD.backup`
- ⏳ 实施完成后: `post_arch_optimization_YYYYMMDD.backup`

### 2. TDengine备份

**全量备份**:
```bash
# 每天01:00执行
BACKUP_DIR="/opt/claude/mystocks_backup/tdengine"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

taosdump -h localhost -u root -p taosdata \
  -o ${BACKUP_DIR}/tdengine_${TIMESTAMP} \
  -A

# 保留最近7天的备份
find ${BACKUP_DIR} -name "tdengine_*" -mtime +7 -exec rm -rf {} \;
```

### 3. MySQL备份（在US2迁移前）

**关键备份**:
```bash
# US2迁移前执行
BACKUP_DIR="/opt/claude/mystocks_backup/mysql"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mysqldump -h localhost -u root -p \
  --single-transaction --routines --triggers \
  mystocks > ${BACKUP_DIR}/mystocks_pre_migration_${TIMESTAMP}.sql
```

**迁移后保留**:
- MySQL备份保留2周作为安全网
- 验证PostgreSQL数据完整性后可删除

## 恢复测试

**每周执行恢复测试**:
```bash
# 测试PostgreSQL恢复
pg_restore -h localhost -U mystocks_user -d mystocks_test \
  ${BACKUP_DIR}/latest.backup

# 验证表数量和行数
psql -h localhost -U mystocks_user -d mystocks_test \
  -c "SELECT COUNT(*) FROM pg_tables WHERE schemaname='public';"
```

## 备份存储

- **主存储**: `/opt/claude/mystocks_backup/` (本地)
- **备份存储**: 外部存储/云存储（建议配置）
- **保留策略**:
  - 每日备份保留7天
  - 关键时间点备份永久保留
  - 压缩存储（gzip）

## 紧急恢复流程

**步骤**:
1. 停止所有服务
2. 评估损坏范围
3. 选择恢复点
4. 执行恢复
5. 验证数据完整性
6. 恢复服务

**恢复命令**:
```bash
# PostgreSQL恢复
pg_restore -h localhost -U mystocks_user -d mystocks -c \
  /path/to/backup.backup

# TDengine恢复
taosdump -h localhost -u root -p taosdata \
  -i /path/to/backup/
```

## 责任人

- **实施负责人**: [待定]
- **备份监控**: [待定]
- **紧急联系人**: [待定]

---

**文档版本**: 1.0
**最后更新**: 2025-10-25
EOF

echo "✅ T004完成: 备份策略文档已创建"
```

**验收标准**:
- ✅ 文档已创建
- ✅ 包含所有数据库备份策略
- ✅ 包含恢复测试流程

---

## ✅ Phase 1完成检查

完成T001-T004后，执行以下验证：

```bash
echo "=== Phase 1完成检查 ==="
echo ""

# 1. 检查备份
echo "1. 备份检查:"
if [ -d "archive/pre_arch_optimization_"* ]; then
    echo "   ✅ 备份目录存在"
    ls -lh archive/pre_arch_optimization_*/
else
    echo "   ❌ 备份目录不存在"
fi
echo ""

# 2. 检查依赖
echo "2. 依赖检查:"
./scripts/check_dependencies.sh
echo ""

# 3. 检查Git hooks
echo "3. Git hooks检查:"
if [ -x ".git/hooks/pre-commit" ]; then
    echo "   ✅ Pre-commit hook已配置"
else
    echo "   ❌ Pre-commit hook未配置"
fi
echo ""

# 4. 检查文档
echo "4. 备份策略文档:"
if [ -f "docs/backup_strategy_arch_optimization.md" ]; then
    echo "   ✅ 备份策略文档存在"
else
    echo "   ❌ 备份策略文档不存在"
fi
echo ""

echo "=== Phase 1检查完成 ==="
```

---

## 📋 Phase 2准备（第二天开始）

Phase 1完成后，可以开始Phase 2 Foundational（13个任务，10-12天）。

**关键任务**:
- T005-T010: Backend Infrastructure (5天)
- T011-T017: Web Foundation (5-7天) ⚠️**阻塞所有Web集成**

**详细步骤**: 参考 `quickstart.md` 和 `IMPLEMENTATION_READY_SUMMARY.md`

---

## 🎯 每日检查清单

实施期间，每天执行：

```bash
# 1. 拉取最新代码
git pull origin 002-arch-optimization

# 2. 运行测试
pytest tests/ -v --tb=short

# 3. 检查代码行数（每周五）
cloc core.py unified_manager.py data_access.py

# 4. 性能基准（每周五）
python tests/performance/test_baseline_latency.py

# 5. 提交进度
# 在tasks.md中标记完成的任务为 [x]
```

---

## 🚨 如遇问题

**问题**: 依赖安装失败
**解决**:
```bash
pip install -r requirements.txt --upgrade
conda update --all
```

**问题**: 数据库连接失败
**解决**:
```bash
# 检查服务状态
systemctl status postgresql
systemctl status taosd

# 重启服务
sudo systemctl restart postgresql
sudo systemctl restart taosd
```

**问题**: Git hook阻止提交
**解决**:
```bash
# 运行格式化
black .
isort .

# 或临时跳过（不推荐）
git commit --no-verify
```

---

## ✅ 启动确认

完成以上所有检查后，您可以：

1. ✅ 创建功能分支
```bash
git checkout -b 002-arch-optimization
git push -u origin 002-arch-optimization
```

2. ✅ 开始执行T001
```bash
# 按照上面的脚本执行
```

3. ✅ 更新进度
```bash
# 在tasks.md中标记:
# - [x] T001 ...
```

---

**准备就绪！开始实施吧！** 🚀

---

**文档位置**: `/opt/claude/mystocks_spec/specs/002-arch-optimization/KICKOFF_CHECKLIST.md`
**最后更新**: 2025-10-25
