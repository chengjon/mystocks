# 📋 Task 1: 紧急安全修复 - 执行清单

**任务ID**: 1
**优先级**: 🔴 Critical (必须)
**周期**: Week 1 (Day 1-2)
**人员**: 人员A (后端主力)
**预计工时**: 12小时

---

## 📌 任务概述

**目标**: 修复当前系统中的关键安全漏洞，为后续架构优化清除障碍

**业务背景**:
- CODE_REVIEW_REPORT.md 中发现2个Critical安全问题
- SQL注入风险可能导致数据泄露
- XSS/CSRF攻击可能被恶意利用
- 敏感数据未加密存储和传输
- 代码重复导致维护困难

**成功标准**:
- ✅ 通过安全扫描工具扫描，零Critical漏洞
- ✅ SQL注入漏洞修复，参数化查询验证通过
- ✅ XSS/CSRF防护实现，安全测试通过
- ✅ 敏感数据加密配置完成
- ✅ 删除重复代码，代码重复率<5%

---

## 🎯 4个子任务分解

### 子任务1.1: 修复SQL注入漏洞 ⏱️ 3h

**详细说明**:
使用SQLAlchemy ORM替代原生SQL、参数化查询、输入验证

**具体步骤**:

1. **识别风险代码** (30min)
   ```bash
   # 搜索所有直接SQL查询
   grep -r "SELECT.*f\"" web/backend/app/
   grep -r "INSERT.*f\"" web/backend/app/
   grep -r "UPDATE.*f\"" web/backend/app/
   grep -r "DELETE.*f\"" web/backend/app/
   ```

2. **查看CODE_REVIEW_REPORT.md中的具体风险位置** (30min)
   - 参考第二部分"WARNINGS"部分的"缺少输入验证"
   - 找出所有使用字符串拼接的SQL语句

3. **重构为SQLAlchemy ORM** (2h)
   ```python
   # ❌ 不好的做法
   query = f"SELECT * FROM users WHERE id = {user_id}"
   result = session.execute(query)

   # ✅ 推荐做法
   from sqlalchemy import text
   user = session.query(User).filter(User.id == user_id).first()

   # 或使用参数化查询
   result = session.execute(
       text("SELECT * FROM users WHERE id = :user_id"),
       {"user_id": user_id}
   )
   ```

4. **验证修复** (30min)
   ```bash
   # 运行SQL注入测试
   python -m pytest tests/test_security_sql_injection.py -v
   ```

**关键文件**:
- `web/backend/app/api/*.py` - 所有API端点
- `web/backend/app/services/*.py` - 业务逻辑层
- `tests/test_security_sql_injection.py` - 新增测试

**验收标准**:
- [ ] 所有数据库查询使用SQLAlchemy或参数化查询
- [ ] 零个字符串拼接的SQL语句
- [ ] SQL注入测试全部通过
- [ ] 代码审查通过

---

### 子任务1.2: 实现XSS/CSRF防护 ⏱️ 3h

**详细说明**:
前端Vue3自动转义、CSP头配置、CSRF Token验证

**具体步骤**:

1. **前端XSS防护** (1.5h)
   ```javascript
   // ❌ 不安全 - 直接渲染HTML
   <div v-html="userContent"></div>

   // ✅ 安全 - 使用v-text (自动转义)
   <div v-text="userContent"></div>

   // ✅ 安全 - 使用{{}} 插值 (自动转义)
   <div>{{ userContent }}</div>
   ```

   任务清单:
   - [ ] 扫描所有Vue模板，找出v-html使用
   - [ ] 替换为v-text或{{}}插值
   - [ ] 配置Content-Security-Policy头
   ```html
   <!-- index.html -->
   <meta http-equiv="Content-Security-Policy"
         content="default-src 'self'; script-src 'self'">
   ```

2. **后端CSRF防护** (1h)
   ```python
   # FastAPI中配置CSRF保护
   from starlette.middleware.csrf import CSRFMiddleware

   app.add_middleware(
       CSRFMiddleware,
       secret_key="your-secret-key-change-this"
   )
   ```

   任务清单:
   - [ ] 安装starlette-csrf
   - [ ] 在main.py中配置CSRFMiddleware
   - [ ] 在所有POST/PUT/DELETE请求中添加CSRF Token
   ```javascript
   // 前端获取和发送CSRF Token
   const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content

   axios.post('/api/data', payload, {
     headers: {
       'X-CSRF-Token': csrfToken
     }
   })
   ```

3. **验证防护** (30min)
   ```bash
   # 运行XSS/CSRF测试
   python -m pytest tests/test_security_xss_csrf.py -v
   ```

**关键文件**:
- `web/frontend/index.html` - CSP头配置
- `web/frontend/src/**/*.vue` - 所有Vue组件
- `web/backend/app/main.py` - 中间件配置
- `tests/test_security_xss_csrf.py` - 新增测试

**验收标准**:
- [ ] 所有v-html替换为安全方式
- [ ] Content-Security-Policy头已配置
- [ ] CSRF Token验证工作正常
- [ ] XSS/CSRF测试全部通过

---

### 子任务1.3: 敏感数据加密 ⏱️ 3h

**详细说明**:
PostgreSQL pgcrypto、TDengine列级加密、传输层TLS 1.3

**具体步骤**:

1. **PostgreSQL数据加密** (1.5h)
   ```sql
   -- 启用pgcrypto扩展
   CREATE EXTENSION IF NOT EXISTS pgcrypto;

   -- 存储密码时加密
   INSERT INTO users (username, password_hash)
   VALUES ('admin', crypt('password123', gen_salt('bf')));

   -- 验证密码
   SELECT * FROM users WHERE username = 'admin'
   AND password_hash = crypt('password123', password_hash);

   -- 加密敏感数据（如API密钥）
   ALTER TABLE strategies ADD COLUMN api_key_encrypted BYTEA;
   UPDATE strategies
   SET api_key_encrypted = pgp_sym_encrypt(api_key, 'encryption-key')
   WHERE api_key IS NOT NULL;
   ```

   任务清单:
   - [ ] 启用pgcrypto扩展
   - [ ] 更新用户表密码存储为crypt格式
   - [ ] 加密API密钥等敏感信息
   - [ ] 创建迁移脚本

2. **TDengine列级加密** (1h)
   ```conf
   # TDengine配置文件 taos.cfg
   enableEncryption yes
   encryptedColumns password,api_key,token
   ```

   任务清单:
   - [ ] 配置TDengine加密列
   - [ ] 重启TDengine服务
   - [ ] 验证加密生效

3. **传输层TLS 1.3** (30min)
   ```python
   # FastAPI配置HTTPS
   import ssl

   ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_3)
   ssl_context.load_cert_chain("cert.pem", "key.pem")

   # 在生产环境运行时使用
   # uvicorn main:app --ssl-keyfile=key.pem --ssl-certfile=cert.pem
   ```

   任务清单:
   - [ ] 生成或购买SSL证书
   - [ ] 配置FastAPI使用TLS 1.3
   - [ ] 更新Docker配置支持HTTPS
   - [ ] 验证HTTPS工作正常

**关键文件**:
- `migrations/add_encryption.sql` - 新增迁移脚本
- `web/backend/app/main.py` - TLS配置
- `taos.cfg` - TDengine配置
- `docker-compose.yml` - SSL证书配置

**验收标准**:
- [ ] PostgreSQL密码存储为加密格式
- [ ] 敏感数据字段已加密
- [ ] TDengine列级加密已启用
- [ ] 传输使用TLS 1.3
- [ ] 加密解密测试通过

---

### 子任务1.4: 删除重复代码 ⏱️ 3h

**详细说明**:
删除src/monitoring/目录、整合AlertManager、合并重复函数

**具体步骤**:

1. **确认重复代码位置** (30min)
   ```bash
   # 根据CODE_REVIEW_REPORT.md的发现
   # 位置：
   # - /opt/claude/mystocks_spec/monitoring/  (活跃)
   # - /opt/claude/mystocks_spec/src/monitoring/  (重复)

   # 对比两个目录
   diff -r monitoring/ src/monitoring/
   ```

2. **删除重复目录** (30min)
   ```bash
   # 备份重复目录（以防万一）
   cp -r src/monitoring/ src/monitoring.backup/

   # 删除重复目录
   rm -rf src/monitoring/
   rm -rf src/core/  # 如果有重复的core目录

   # 验证删除
   ls -la src/ | grep monitoring
   ```

3. **整合AlertManager** (1h)
   ```python
   # 保留 monitoring/alert_manager.py
   # 删除其他重复的AlertManager实现

   # 统一使用单一的AlertManager
   from monitoring.alert_manager import AlertManager

   alert_manager = AlertManager()
   alert_manager.send_alert(level="error", message="系统故障")
   ```

   任务清单:
   - [ ] 找出所有AlertManager实现
   - [ ] 保留最完整的实现
   - [ ] 删除其他重复实现
   - [ ] 更新所有导入语句

4. **合并重复函数** (1h)
   ```bash
   # 使用代码分析工具找出重复函数
   pip install radon
   radon mi web/backend/app/ -n B

   # 手工检查并合并重复函数
   # 特别关注：
   # - 数据库连接函数
   # - 日志记录函数
   # - 错误处理函数
   ```

   任务清单:
   - [ ] 运行radon代码复杂度分析
   - [ ] 找出重复的函数
   - [ ] 提取为共享模块
   - [ ] 删除重复实现
   - [ ] 更新所有调用位置

5. **验证代码重复率** (30min)
   ```bash
   # 测量代码重复率
   pip install pylint
   pylint --duplicate-code-check web/backend/app/ > duplicate_report.txt

   # 确保重复率从18%降到<5%
   ```

**关键文件**:
- `monitoring/` - 保留这个目录
- `src/monitoring/` - 删除这个目录
- 所有`.py`文件 - 检查重复函数

**验收标准**:
- [ ] src/monitoring/目录已删除
- [ ] src/core/目录已删除（如有）
- [ ] 只有一个AlertManager实现
- [ ] 代码重复率<5%
- [ ] 所有导入语句已更新
- [ ] 代码审查通过

---

## ⏱️ 时间分配

```
Task 1.1 (修复SQL注入)      : 3小时
Task 1.2 (XSS/CSRF防护)     : 3小时
Task 1.3 (敏感数据加密)     : 3小时
Task 1.4 (删除重复代码)     : 3小时
─────────────────────────────
总计                        : 12小时
```

**建议日程**:
- **Day 1 上午**: 1.1 + 1.2 (6小时)
- **Day 1 下午**: 1.3 (3小时)
- **Day 2 上午**: 1.4 (3小时)
- **Day 2 下午**: 代码审查和测试

---

## 🧪 测试清单

### 单元测试
```bash
# SQL注入防护测试
pytest tests/test_security_sql_injection.py -v

# XSS/CSRF防护测试
pytest tests/test_security_xss_csrf.py -v

# 敏感数据加密测试
pytest tests/test_security_encryption.py -v
```

### 集成测试
```bash
# 运行所有安全相关测试
pytest tests/test_security_*.py -v --cov=web/backend/app/
```

### 安全扫描
```bash
# 使用OWASP安全扫描工具
pip install safety bandit
bandit -r web/backend/app/ -f json > bandit_report.json
safety check --json > safety_report.json
```

---

## 📝 提交和验收

### Git提交
```bash
git add web/backend/app/ migrations/
git commit -m "fix: 修复SQL注入、XSS/CSRF、敏感数据加密问题

- 使用SQLAlchemy ORM替代原生SQL字符串拼接
- 实现前端Vue3自动转义和CSP头配置
- 配置CSRF Token验证
- 启用PostgreSQL pgcrypto和TDengine列级加密
- 配置传输层TLS 1.3"

git push
```

### PR审查清单
- [ ] 代码符合PEP 8规范
- [ ] 所有测试通过
- [ ] 安全扫描无Critical漏洞
- [ ] 文档已更新
- [ ] 至少2个reviewer批准

### 验收标准清单
- [ ] SQL注入漏洞完全修复
- [ ] XSS/CSRF防护部署完毕
- [ ] 敏感数据加密启用
- [ ] 代码重复率<5%
- [ ] 安全扫描通过
- [ ] 所有测试通过 (100%覆盖)
- [ ] 性能无明显下降
- [ ] 文档更新完整

---

## 📚 参考资源

### OWASP安全最佳实践
- SQL注入防护: https://owasp.org/www-community/attacks/SQL_Injection
- XSS防护: https://owasp.org/www-community/attacks/xss/
- CSRF防护: https://owasp.org/www-community/attacks/csrf

### FastAPI安全
- https://fastapi.tiangolo.com/deployment/concepts/#https
- https://fastapi.tiangolo.com/advanced/security/

### SQLAlchemy ORM
- https://docs.sqlalchemy.org/en/20/orm/

### PostgreSQL安全
- https://www.postgresql.org/docs/current/pgcrypto.html

---

**🚀 现在开始Task 1！**

预计完成时间: 12小时 (2天)
下一个任务: Task 2 - TDengine缓存集成

记录进度: `task-master update-subtask --id=1.1 --prompt="修复SQL注入..."`
