# 本地开发环境配置指南（.env 设置）

**日期**: 2025-11-30
**目标**: 安全地为本地开发设置数据库凭证，无需提交至 Git

---

## ⚠️ 重要提示

本地 `.env` 文件包含**真实数据库凭证**，**绝对不能提交至 Git**。

- `.env.example` 包含占位符，已提交至 Git ✅
- `.env` 包含真实凭证，已添加至 `.gitignore` ✅
- 所有环境配置统一使用根目录 `.env` 文件 ✅

---

## 快速开始（2 步）

### 步骤 1：复制示例文件

```bash
cd /opt/claude/mystocks_spec
cp .env.example .env
```

### 步骤 2：编辑本地凭证

编辑 `.env` 文件，替换占位符为实际凭证：

```bash
# 使用你喜欢的编辑器（nano / vim / code）
nano .env
```

**需要替换的字段**：

| 占位符 | 替换为 | 说明 |
|------|-------|------|
| `your-postgres-password` | 实际 PostgreSQL 密码 | 数据仓库访问凭证 |
| `your-tdengine-password` | 实际 TDengine 密码 | 时序数据库访问凭证 |
| `your-jwt-secret-key` | 强随机字符串 | JWT 认证密钥 |

### 步骤 3：验证配置

验证 `.env` 文件已添加至 `.gitignore`（禁止提交）：

```bash
# 应该显示 "On branch xxx, nothing to commit"
git status | grep .env  # 不应有输出

# 验证凭证是否正确加载
python -c "import os; print('✅ 凭证已加载') if os.getenv('POSTGRESQL_PASSWORD') else print('❌ 凭证未加载')"
```

---

## 详细配置说明

### PostgreSQL 配置

```bash
POSTGRESQL_HOST=localhost
POSTGRESQL_PORT=5438
POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=your-postgres-password  # ← 替换为实际密码
POSTGRESQL_DATABASE=mystocks

# 监控数据库 URL（自动使用上述凭证）
MONITOR_DB_URL=postgresql://postgres:your-postgres-password@localhost:5438/mystocks
```

**如何获取密码**：
- 联系数据库管理员获取生产密码
- 本地测试可使用任意密码（确保数据库服务配置相同）

### TDengine 配置

```bash
TDENGINE_HOST=localhost
TDENGINE_PORT=6030
TDENGINE_USER=root
TDENGINE_PASSWORD=your-tdengine-password  # ← 替换为实际密码
TDENGINE_DATABASE=market_data
TDENGINE_REST_PORT=6041
```

### JWT 安全密钥

```bash
JWT_SECRET_KEY=your-jwt-secret-key  # ← 生成强随机字符串
```

**生成安全密钥**（推荐）：

```bash
# 使用 Python 生成强随机密钥
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# 输出示例:
# a7x_9kL3z8mN2pQ5wR1vT4bY6cH9jF2dG7eI8

# 复制输出内容到 .env 文件中的 JWT_SECRET_KEY
```

---

## 验证清单

完成配置后，逐项验证：

- [ ] `.env` 文件已创建（从 `.env.example` 复制）
- [ ] `.env` 文件已编辑，所有占位符已替换为实际凭证
- [ ] `config/.env` 文件已创建（从 `config/.env.data_sources.example` 复制）
- [ ] `git status` 不显示 `.env` 或 `.env.production` 文件（已被 `.gitignore` 忽略）
- [ ] 本地应用程序能连接到数据库（无连接错误）
- [ ] E2E 测试运行正常，无端口连接错误

---

## 常见问题

### Q1：不小心在 .env 中放了真实凭证，应该怎么办？

**A**：不用担心，`.env` 已在 `.gitignore` 中，Git 不会追踪它。但为了安全：

1. **立即轮换凭证**（如果曾被不小心共享）：
   ```bash
   # 通知数据库管理员更改密码
   # 从数据库管理员获取新密码
   ```

2. 在 `.env` 中更新新凭证：
   ```bash
   nano .env
   # 替换为新凭证
   ```

### Q2：能否在 `.env.example` 中放实际凭证作为"通用"密码？

**A**：**绝对不行**！

- `.env.example` 被提交至 Git
- 任何查看代码的人都能看到这些凭证
- 这是严重的安全漏洞 🔴

### Q3：CI/CD 环境如何管理凭证？

**A**：CI/CD 环境（GitHub Actions / GitLab CI）使用**密钥管理系统**：

```bash
# GitHub Actions 示例
env:
  POSTGRESQL_PASSWORD: ${{ secrets.DB_PASSWORD }}
  TDENGINE_PASSWORD: ${{ secrets.TDENGINE_PASS }}

# 凭证存储在 Settings → Secrets，不在代码中
```

详见：[SECURITY_FOLLOWUP_PLAN_20251130.md](/opt/claude/mystocks_spec/docs/standards/SECURITY_FOLLOWUP_PLAN_20251130.md) 中的 "CI/CD Secret Management"

---

## 重要的 Git 命令

### 查看本地 .env 是否被忽略

```bash
# 应输出 0（表示 .env 不被追踪）
git status --porcelain | grep -E "^\s*\.env" | wc -l
```

### 确认 .env 在 .gitignore 中

```bash
# 应输出 .env 的忽略规则
git check-ignore -v .env
```

### 意外提交凭证的紧急恢复

**如果不小心提交了凭证至 Git**（立即执行）：

```bash
# 1. 停止提交进程
git reset --soft HEAD~1

# 2. 移除凭证文件
git reset HEAD .env

# 3. 编辑文件，删除真实凭证
nano .env

# 4. 重新提交（不含凭证）
git add -u  # 只提交已追踪的更改
git commit -m "fix: Remove accidentally committed credentials"

# 5. 轮换数据库凭证
# 联系数据库管理员立即更改密码
```

---

## 相关文档

- **硬编码治理分级指南**: [HARDCODING_GOVERNANCE_TIERING_GUIDE.md](./security/HARDCODING_GOVERNANCE_TIERING_GUIDE.md)
- **P0 轮换处置模板**: [PHASE0_CREDENTIAL_ROTATION_GUIDE.md](PHASE0_CREDENTIAL_ROTATION_GUIDE.md)
- **安全审计报告**: [SECURITY_AUDIT_REPORT_20251130.md](SECURITY_AUDIT_REPORT_20251130.md)
- **安全快速参考**: [SECURITY_QUICK_REFERENCE.md](SECURITY_QUICK_REFERENCE.md)
- **后续安全计划**: [SECURITY_FOLLOWUP_PLAN_20251130.md](SECURITY_FOLLOWUP_PLAN_20251130.md)

---

## 硬编码治理必需环境变量（2026-02-15 起）

> 本节为补充规范，不替代现有环境配置说明。

以下变量在运行代码中已切换为“缺失即失败”或“仅开发环境本地回退”策略：

```bash
# Backend / Database
POSTGRESQL_HOST=
POSTGRESQL_PORT=
POSTGRESQL_USER=
POSTGRESQL_PASSWORD=
POSTGRESQL_DATABASE=

MYSQL_HOST=
MYSQL_PORT=
MYSQL_USER=
MYSQL_PASSWORD=
MYSQL_DATABASE=

TDENGINE_HOST=
TDENGINE_PORT=
TDENGINE_USER=
TDENGINE_PASSWORD=
TDENGINE_DATABASE=

# Encryption
ENCRYPTION_MASTER_PASSWORD=

# Monitoring DB (optional override)
MONITOR_DB_HOST=
MONITOR_DB_PORT=
MONITOR_DB_USER=
MONITOR_DB_PASSWORD=
MONITOR_DB_NAME=

# Frontend runtime endpoints
VITE_API_BASE_URL=
VITE_WS_BASE_URL=

# TDX server pool override (optional)
TDX_SERVER_POOL_FILE=
TDX_NETWORK_SERVERS=
```

### 启动失败策略

- 非开发环境（`APP_ENV/ENVIRONMENT` 非 `dev/development/test/local`）缺失关键连接参数时，服务应直接失败启动。
- 密码类变量（如 `POSTGRESQL_PASSWORD`、`TDENGINE_PASSWORD`、`ENCRYPTION_MASTER_PASSWORD`）缺失时，禁止使用任何明文默认值。
- 前端地址配置建议通过 `.env.*` 管理，避免在组件/服务中散落 URL 字面量。

---

## 获取帮助

如有问题，请：

1. 查看上述相关文档
2. 联系数据库管理员（关于凭证）
3. 联系安全负责人（关于凭证泄露问题）

**最后更新**: 2025-11-30
**版本**: 1.0
