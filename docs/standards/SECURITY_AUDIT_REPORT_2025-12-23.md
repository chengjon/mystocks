# 🔒 MyStocks 项目安全审计报告

**审计日期**: 2025-12-23
**审计范围**: 代码库硬编码敏感信息检查、.gitignore 配置验证、敏感文件泄露检查
**严重程度**: 🔴 高危

---

## 📊 执行摘要

本次安全审计发现了 **严重的安全问题**，需要立即修复：

1. **🔴 严重**: 硬编码的数据库密码已提交到 Git 历史中
2. **🟡 中等**: 硬编码的内网 IP 地址分散在多处代码中
3. **🟢 良好**: .gitignore 配置总体完善，但存在少量遗漏

---

## 🚨 严重安全问题

### 1. 硬编码数据库密码（高危）

#### 问题 1.1: `src/monitoring/monitoring_service.py:180`

```python
self.monitor_db_url = (
    "mysql+pymysql://root:your-postgresql-password@localhost:3306/db_monitor"
)
```

**暴露信息**:
- 用户名: `root`
- 密码: `your-postgresql-password`
- IP 地址: `localhost`
- 端口: `3306`
- 数据库: `db_monitor`

**风险等级**: 🔴 严重
**影响**: 数据库完全暴露，任何人访问代码库即可获得数据库完全访问权限

#### 问题 1.2: `.archive/sensitive-backups/_.env.backup.20251124_232409`

**已提交到 Git 的敏感信息**:

```bash
# TDengine Configuration
TDENGINE_PASSWORD=taosdata

# PostgreSQL Configuration
POSTGRESQL_PASSWORD=your-postgresql-password

# Monitoring Database URL
MONITOR_DB_URL=postgresql://postgres:your-postgresql-password@localhost:5438/mystocks
```

**风险等级**: 🔴 严重
**影响**: 生产环境数据库凭证已泄露到 Git 历史记录中

**文件位置**: `.archive/sensitive-backups/_.env.backup.20251124_232409`
**状态**: ✅ 已被 .gitignore 忽略（未来不会再次提交）
**问题**: ⚠️ 已在 Git 历史中，需要清除历史记录

---

## 🟡 中等安全问题

### 2. 硬编码 IP 地址

虽然内网 IP 地址不如密码敏感，但硬编码仍然违反最佳实践：

| 文件 | 行号 | 硬编码内容 |
|------|------|------------|
| `src/monitoring/monitoring_service.py` | 116 | `"host": os.getenv("MONITOR_DB_HOST", "localhost")` |
| `src/storage/access/modules/redis.py` | 45 | `host=os.getenv("REDIS_HOST", "localhost")` |
| `src/storage/database/connection_manager.py` | 123 | `host=os.getenv("POSTGRESQL_HOST", "localhost")` |
| `src/storage/database/connection_manager.py` | 169 | `host=os.getenv("MYSQL_HOST", "localhost")` |
| `src/storage/database/connection_manager.py` | 208 | `host=os.getenv("REDIS_HOST", "localhost")` |

**建议**: 统一使用环境变量，移除硬编码的默认值

---

## ✅ 良好配置

### 3. .gitignore 配置检查

**总体评价**: 🟢 完善

`.gitignore` 文件已正确配置：

```gitignore
# 环境变量文件
.env
.env.*
.env.local
config/.env
config/.env.*

# 敏感备份文件
.archive/sensitive-backups/

# 证书和密钥文件
*.key
*.pem
*.pfx
*.p12

# 数据库文件
*.db
*.sqlite
*.sqlite3
```

**发现问题**:

1. ❌ `config/.env.simplified` 被 git 跟踪（应该在 .gitignore 中）
2. ❌ `config/realtime_market_config.env` 被 git 跟踪（配置文件）
3. ❌ `config/redis_fixation_config.env` 被 git 跟踪（配置文件）
4. ❌ `config/simple_config.env` 被 git 跟踪（配置文件）

**建议**: 将这些配置文件移至 `.env.example` 或添加到 .gitignore

---

## 🔧 修复建议

### 立即执行（P0 - 严重）

#### 1. 清除 Git 历史中的敏感信息

```bash
# 备份当前分支
git checkout -b backup-before-security-fix

# 使用 BFG Repo-Cleaner 或 git-filter-repo 清除敏感文件
# 安装 git-filter-repo
pip install git-filter-repo

# 清除敏感备份文件
git filter-repo --path .archive/sensitive-backups/_.env.backup.20251124_232409 --invert-paths

# 强制推送到远程（⚠️ 警告：这会重写 Git 历史）
git push origin --force --all
```

#### 2. 修复代码中的硬编码密码

**文件**: `src/monitoring/monitoring_service.py`

**当前代码**（第 177-181 行）:
```python
if not self.monitor_db_url:
    logger.warning("未配置监控数据库URL，使用默认配置")
    self.monitor_db_url = (
        "mysql+pymysql://root:your-postgresql-password@localhost:3306/db_monitor"
    )
```

**修复后**:
```python
if not self.monitor_db_url:
    logger.warning("未配置监控数据库URL，无法启动监控服务")
    raise ValueError("MONITOR_DB_URL 环境变量必须设置")
```

#### 3. 更改所有暴露的密码

**立即执行以下操作**:

1. **TDengine 数据库** (`taosdata`):
   ```bash
   # 在 TDengine 中更改 root 密码
   taos -h localhost -P 6030 -u root -p
   # 执行: ALTER USER root PASS '新密码';
   ```

2. **PostgreSQL 数据库** (`your-postgresql-password`):
   ```bash
   # 在 PostgreSQL 中更改 postgres 密码
   psql -h localhost -p 5438 -U postgres
   # 执行: ALTER USER postgres WITH PASSWORD '新密码';
   ```

3. **MySQL/MariaDB 数据库** (`your-postgresql-password`):
   ```bash
   # 在 MySQL 中更改 root 密码
   mysql -h localhost -u root -p
   # 执行: ALTER USER 'root'@'%' IDENTIFIED BY '新密码';
   ```

---

### 短期修复（P1 - 高优先级）

#### 4. 移除硬编码的 IP 地址

将所有硬编码的 IP 地址改为环境变量：

**示例修复** (`src/monitoring/monitoring_service.py`):

```python
# 修复前
"host": os.getenv("MONITOR_DB_HOST", "localhost"),

# 修复后
"host": os.getenv("MONITOR_DB_HOST"),  # 移除默认值，强制使用环境变量
```

**需要在 .env 文件中添加**:
```bash
MONITOR_DB_HOST=localhost
POSTGRESQL_HOST=localhost
REDIS_HOST=localhost
```

#### 5. 更新 .gitignore

在 `.gitignore` 中添加：

```gitignore
# 配置文件（仅保留示例）
config/*.env
!config/*.env.example
config/.env.simplified
```

#### 6. 清理已提交的配置文件

```bash
# 从 Git 中移除配置文件，但保留本地副本
git rm --cached config/.env.simplified
git rm --cached config/realtime_market_config.env
git rm --cached config/redis_fixation_config.env
git rm --cached config/simple_config.env

# 提交删除
git commit -m "security: remove sensitive config files from tracking"
```

---

### 长期改进（P2 - 中优先级）

#### 7. 实施安全最佳实践

1. **使用密钥管理服务**
   - 考虑使用 HashiCorp Vault、AWS Secrets Manager 或 Azure Key Vault
   - 避免在 .env 文件中存储生产环境凭证

2. **Pre-commit Hooks**
   - 添加敏感信息检测到 pre-commit hooks
   - 使用 `git-secrets` 或 `truffleHog` 扫描提交

3. **环境变量验证**
   - 在应用启动时验证必需的环境变量
   - 如果缺少关键配置，拒绝启动（而非使用硬编码默认值）

4. **定期安全审计**
   - 每月运行 `git-secrets --scan` 检查新提交
   - 使用 Bandit 进行 Python 代码安全扫描

---

## 🛡️ Pre-commit Hook 配置建议

创建 `.git/hooks/pre-commit`（或添加到 `.pre-commit-config.yaml`）:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/commitizen-tools/commitizen
    rev: v3.12.0
    hooks:
      - id: commitizen
        stages: [commit-msg]

  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
        exclude: package.lock.json

  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.8
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
```

---

## 📋 修复检查清单

- [ ] **P0**: 清除 Git 历史中的敏感文件（使用 git-filter-repo）
- [ ] **P0**: 更改所有暴露的数据库密码
- [ ] **P0**: 修复 `src/monitoring/monitoring_service.py` 中的硬编码密码
- [ ] **P1**: 移除所有硬编码的 IP 地址
- [ ] **P1**: 更新 .gitignore 排除配置文件
- [ ] **P1**: 从 Git 跟踪中移除配置文件
- [ ] **P2**: 配置 pre-commit hooks 防止未来泄露
- [ ] **P2**: 设置应用启动时的环境变量验证
- [ ] **P2**: 考虑实施密钥管理服务

---

## 📞 联系信息

如有疑问或需要协助，请查看：
- 项目安全文档: `docs/security/SECURITY_BEST_PRACTICES.md`
- 环境配置指南: `config/.env.example`

---

**报告生成时间**: 2025-12-23
**下次审计建议**: 2025-01-23（每月一次）

---

*此报告由 Claude Code 自动生成*
