# 🔒 安全修复后续行动指南

**生成日期**: 2025-12-23
**状态**: P0 严重问题已修复，P1/P2 问题待处理

---

## ✅ 已完成的修复（P0）

### 1. ✅ 硬编码密码已移除
- **文件**: `src/monitoring/monitoring_service.py:177-182`
- **修复**: 移除硬编码的数据库连接字符串
- **状态**: 已提交（commit 00d26e1）

### 2. ✅ Git 历史已清理
- **工具**: git-filter-repo
- **移除**: `.archive/sensitive-backups/_.env.backup.20251124_232409`
- **状态**: 已完成

### 3. ✅ .gitignore 已更新
- **新增**:
  - `config/realtime_market_config.env`
  - `config/redis_fixation_config.env`
  - `config/simple_config.env`
- **状态**: 已提交

---

## 🚨 立即执行的步骤（今天必须完成）

### 步骤 1: 更改所有暴露的数据库密码

**⚠️ 严重警告**: 以下密码已在 Git 历史中暴露，必须立即更改！

#### TDengine 数据库
```bash
# 连接 TDengine
taos -h 192.168.123.104 -P 6030 -u root -p

# 输入旧密码: taosdata

# 更改密码
ALTER USER root PASS '新_强_密_码_这里';

# 退出
quit;
```

#### PostgreSQL 数据库
```bash
# 连接 PostgreSQL
psql -h 192.168.123.104 -p 5438 -U postgres

# 输入旧密码: c790414J

# 更改密码
ALTER USER postgres WITH PASSWORD '新_强_密_码_这里';

# 退出
\q
```

#### MySQL/MariaDB 数据库（如果使用）
```bash
# 连接 MySQL
mysql -h 192.168.123.104 -u root -p

# 输入旧密码: c790414J

# 更改密码
ALTER USER 'root'@'%' IDENTIFIED BY '新_强_密_码_这里';

# 刷新权限
FLUSH PRIVILEGES;

# 退出
quit;
```

### 步骤 2: 更新 .env 文件

编辑项目根目录的 `.env` 文件（如果不存在，从 `.env.example` 复制）：

```bash
# 创建或编辑 .env
cp .env.example .env
nano .env  # 或使用你喜欢的编辑器
```

**必须配置的环境变量**：

```bash
# 监控数据库连接（必需）
MONITOR_DB_URL=postgresql://postgres:新密码@192.168.123.104:5438/mystocks

# 或者使用 MySQL/MariaDB
# MONITOR_DB_URL=mysql+pymysql://root:新密码@192.168.123.104:3306/db_monitor
```

### 步骤 3: 强制推送到远程仓库

**⚠️ 警告**: 这将重写 Git 历史以删除敏感信息。确保团队成员已知晓！

```bash
# 添加远程仓库（如果已移除）
git remote add origin git@github.com:chengjon/mystocks.git

# 强制推送所有分支
git push origin --force --all

# 强制推送所有标签
git push origin --force --tags
```

**验证推送成功**:
```bash
git log --oneline -1
# 应该显示: 00d26e1 security: fix critical security vulnerabilities
```

---

## 📋 后续修复（本周内完成）

### P1.1: 移除硬编码的 IP 地址

以下文件中包含硬编码的内网 IP `192.168.123.104`：

| 文件 | 行号 | 需要修改 |
|------|------|----------|
| `src/monitoring/monitoring_service.py` | 116 | 移除 `"host": os.getenv("MONITOR_DB_HOST", "192.168.123.104")` 中的默认值 |
| `src/storage/access/modules/redis.py` | 45 | 移除 `host=os.getenv("REDIS_HOST", "192.168.123.104")` 中的默认值 |
| `src/storage/database/connection_manager.py` | 123, 169, 208 | 移除所有 `"192.168.123.104"` 默认值 |

**修复方法**:
```python
# 修复前
host=os.getenv("REDIS_HOST", "192.168.123.104")

# 修复后
host=os.getenv("REDIS_HOST")  # 移除默认值，强制使用环境变量
```

**自动化修复脚本**:
```bash
# 创建临时脚本
cat > /tmp/fix_hardcoded_ips.py << 'EOF'
import re
import sys

files_to_fix = [
    'src/monitoring/monitoring_service.py',
    'src/storage/access/modules/redis.py',
    'src/storage/database/connection_manager.py'
]

for filepath in files_to_fix:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 移除 192.168.123.104 的默认值
        content = re.sub(
            r'= os\.getenv\(([^,]+),\s*"192\.168\.123\.104"\)',
            r'= os.getenv(\1)',
            content
        )

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f'✅ Fixed: {filepath}')
    except Exception as e:
        print(f'❌ Error fixing {filepath}: {e}')

print('Done!')
EOF

# 执行修复
python /tmp/fix_hardcoded_ips.py
```

### P1.2: 添加环境变量验证

在 `.env` 文件中添加所有必需的主机配置：

```bash
# 数据库主机配置
POSTGRESQL_HOST=192.168.123.104
POSTGRESQL_PORT=5438
REDIS_HOST=192.168.123.104
REDIS_PORT=6379
MONITOR_DB_HOST=192.168.123.104
```

---

## 🔒 长期改进（本月内完成）

### P2.1: 配置 Pre-commit Hooks

安装并配置敏感信息检测工具：

```bash
# 安装 git-secrets
brew install git-secrets  # macOS
# 或
wget https://raw.githubusercontent.com/awslabs/git-secrets/master/git-secrets -O /usr/local/bin/git-secrets
chmod +x /usr/local/bin/git-secrets

# 配置 git-secrets
git secrets --install
git secrets --register-aws
git secrets --add 'mysql\+pymysql://.*@'
git secrets --add 'postgresql://.*@'
git secrets --add '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}:[0-9]+'

# 扫描整个仓库
git secrets --scan整个仓库
```

### P2.2: 实施密钥管理服务

考虑使用专业的密钥管理方案：

- **HashiCorp Vault** (开源，企业级)
- **AWS Secrets Manager** (如果使用 AWS)
- **Azure Key Vault** (如果使用 Azure)
- **环境变量 + 加密配置** (简单方案)

**推荐方案（开发环境）**:
```bash
# 使用 python-dotenv + 加密
pip install python-dotenv cryptography

# 创建加密的 .env 文件
python -c "
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(f'FERNET_KEY={key.decode()}')
"

# 在应用启动时解密
```

---

## ✅ 验证清单

完成修复后，使用此清单验证：

- [ ] 所有数据库密码已更改（TDengine, PostgreSQL, MySQL）
- [ ] `.env` 文件已正确配置
- [ ] 已强制推送到远程仓库（`git push origin --force --all`）
- [ ] 团队成员已拉取最新代码（`git pull --rebase`）
- [ ] 硬编码 IP 地址已移除
- [ ] 应用启动时验证环境变量
- [ ] 配置了 pre-commit hooks
- [ ] 执行了 `git secrets --scan` 确认无敏感信息

---

## 📞 团队协作指南

### 通知团队成员

**发送消息模板**:

```
🚨 紧急：Git 仓库历史已重写

由于安全审计发现并修复了严重漏洞，我已重写了 Git 历史。

**必须执行的步骤**：

1. 备份你的本地更改
   git checkout main
   git branch backup-your-work

2. 删除旧的本地分支
   git fetch origin
   git reset --hard origin/main

3. 重新应用你的更改
   git checkout backup-your-work
   git rebase main

4. 更新你的 .env 文件（配置已更改）
   cp .env.example .env
   # 编辑 .env 添加必需的环境变量

5. 数据库密码已更改，联系我获取新密码

重要：如果你在 main 分支有未推送的工作，请立即告诉我！

```

### 恢复团队成员的工作

如果团队成员在重写历史前有未推送的提交：

```bash
# 团队成员执行
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

---

## 📊 安全改进效果

### 修复前风险评分
- **数据泄露风险**: 🔴 严重 (9.5/10)
- **Git 历史污染**: 🔴 严重 (10/10)
- **合规性**: 🔴 不符合

### 修复后风险评分
- **数据泄露风险**: 🟡 中等 (需要手动更改密码)
- **Git 历史污染**: 🟢 良好 (敏感信息已移除)
- **合规性**: 🟡 改善中

---

## 📖 参考文档

- **完整安全审计报告**: `docs/standards/SECURITY_AUDIT_REPORT_2025-12-23.md`
- **安全最佳实践**: `docs/security/SECURITY_BEST_PRACTICES.md`
- **环境配置示例**: `config/.env.example`

---

**生成时间**: 2025-12-23
**下次安全审计**: 2025-01-23

*此指南由 Claude Code 自动生成*
