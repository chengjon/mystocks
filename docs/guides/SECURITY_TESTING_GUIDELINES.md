# MyStocks 项目安全测试指南

## 概述

本文档提供了 MyStocks 量化交易平台的安全测试框架和最佳实践。项目采用多层安全测试策略，包括静态应用安全测试（SAST）、动态应用安全测试（DAST）、依赖项安全扫描和渗透测试。

## 安全测试架构

### 1. 测试层次

```
┌─────────────────────────────────────────────────┐
│                渗透测试 (PT)                    │
│            (季度性 + 重大变更后)                 │
├─────────────────────────────────────────────────┤
│           动态应用安全测试 (DAST)                │
│            (CI/CD 自动化 + 部署前)               │
├─────────────────────────────────────────────────┤
│           静态应用安全测试 (SAST)                │
│            (提交时 + 代码审查)                  │
├─────────────────────────────────────────────────┤
│          依赖项安全扫描 (SCA)                   │
│            (CI/CD 自动化 + 每日)                 │
└─────────────────────────────────────────────────┘
```

### 2. 工具栈

| 测试类型 | 工具 | 频率 | 集成位置 |
|---------|------|------|----------|
| SAST | Bandit, Pylint | 每次 Git 提交 | pre-commit 钩子 |
| SAST | Semgrep | CI/CD 管道 | GitHub Actions |
| DAST | OWASP ZAP | 部署前 | CI/CD 管道 |
| DAST | SQLmap | 特定测试 | 手动执行 |
| SCA | Safety | 每日 | GitHub Actions |
| SCA | Dependabot | 每周 | GitHub Actions |
| 渗透测试 | 手动 + Burp Suite | 季度 + 重大变更后 | 手动执行 |

## 安全测试标准

### 1. OWASP Top 10 覆盖

| OWASP 风险 | 测试工具 | 状态 | 严重性 |
|------------|----------|------|--------|
| A01:2021 - 访问控制失效 | Bandit, Semgrep | ✅ 已实现 | 高 |
| A02:2021 - 加密机制失效 | Bandit, 手动测试 | ✅ 已实现 | 高 |
| A03:2021 - 注入 | Bandit, SQLmap | ✅ 已实现 | 高 |
| A04:2021 - 不安全设计 | 代码审查, Semgrep | ✅ 已实现 | 中 |
| A05:2021 - 安全配置错误 | Bandit, 配置扫描 | ✅ 已实现 | 中 |
| A06:2021 - 脆弱和过时的组件 | Safety, Dependabot | ✅ 已实现 | 中 |
| A07:2021 - 身份认证失效 | Bandit, 手动测试 | ✅ 已实现 | 高 |
| A08:2021 - 软件和数据完整性失效 | Semgrep, 手动测试 | ✅ 已实现 | 中 |
| A09:2021 - 安全日志和监控失效 | Bandit, 日志审计 | ✅ 已实现 | 中 |
| A10:2021 - 服务端请求伪造 | Semgrep, 手动测试 | ✅ 已实现 | 高 |

### 2. 严重性评级

| 级别 | 描述 | 响应时间 | 修复要求 |
|------|------|----------|----------|
| Critical (严重) | 远程代码执行, 权限提升 | 24小时内 | 必须修复 |
| High (高) | 数据泄露, 认证绕过 | 72小时内 | 必须修复 |
| Medium (中) | 信息泄露, 配置错误 | 1周内 | 应该修复 |
| Low (低) | 信息暴露, 最佳实践违反 | 2周内 | 可以修复 |

## 实施指南

### 1. SAST 静态代码分析

#### Bandit 配置
```bash
# .bandit 配置文件
[bandit]
exclude_dirs = tests,venv,node_modules,migrations
skips: B101,B601  # 跳过已知问题

# 运行测试
bandit -r src/ -f json -o bandit-report.json
```

#### Pylint 安全检查
```python
# 在 .pylintrc 中启用安全检查
[MESSAGES CONTROL]
enable=all
disable=

# 扫描安全相关问题
pylint --msg-template="{path}:{line}: {msg_id} ({symbol}) {msg}" \
       --disable=all \
       --enable=sql-injection,eval-used,dangerous-default-argument \
       src/
```

### 2. DAST 动态应用安全测试

#### OWASP ZAP 配置
```bash
# Docker 运行 ZAP
docker run -t owasp/zap2docker-stable \
  zap-baseline.py -t http://localhost:8000 \
  -g genconfig -a api_key

# 全面扫描
docker run -t owasp/zap2docker-stable \
  zap-baseline.py -t http://localhost:8000 \
  -c zap-rules -r zap-report.html
```

#### SQL 注入测试
```bash
# 使用 sqlmap 测试端点
sqlmap -u "http://localhost:8000/api/market/data" \
       --data "symbol=AAPL&limit=10" \
       --risk=3 --level=5 \
       --batch
```

### 3. SCA 依赖项安全扫描

#### Safety 扫描
```bash
# requirements.txt 安全检查
safety check --json --output safety-report.json

# 锁定文件扫描
safety check --file requirements-lock.txt --json
```

#### Dependabot 配置
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    assignees:
      - "security-team"
    reviewers:
      - "maintainers"
```

## CI/CD 集成

### GitHub Actions 工作流
```yaml
# .github/workflows/security.yml
name: Security Testing
on: [push, pull_request]

jobs:
  sast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Bandit
        run: bandit -r src/ -f json -o bandit-report.json
      - name: Run Safety
        run: safety check --json --output safety-report.json
      - name: Upload reports
        uses: actions/upload-artifact@v3
        with:
          name: security-reports
          path: |
            bandit-report.json
            safety-report.json

  dast:
    runs-on: ubuntu-latest
    if: github.event_name == 'push'
    steps:
      - uses: actions/checkout@v4
      - name: Start application
        run: |
          cd web/backend
          python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
      - name: Wait for health
        run: |
          until curl -f http://localhost:8000/health; do
            echo "Waiting for health check..."
            sleep 5
          done
      - name: Run ZAP
        run: |
          docker run --network host -t owasp/zap2docker-stable \
            zap-baseline.py -t http://localhost:8000 \
            -r zap-report.html
```

## 手动安全测试

### 1. 身份认证测试
```bash
# 弱密码测试
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'

# JWT 令牌测试
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Authorization: Bearer invalid_token"

# 权限提升测试
curl -X GET http://localhost:8000/api/admin/users \
  -H "Authorization: Bearer user_token"
```

### 2. API 安全测试
```bash
# 输入验证测试
curl -X GET "http://localhost:8000/api/market/data?symbol=<script>alert(1)</script>"

# SQL 注入测试
curl -X POST http://localhost:8000/api/trading/order \
  -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL\' OR 1=1--","quantity":100}'

# 文件上传测试
curl -X POST http://localhost:8000/api/upload \
  -F "file=@malicious.php"
```

## 报告和响应

### 1. 报告格式
```json
{
  "scan_id": "2025-01-15-001",
  "timestamp": "2025-01-15T10:00:00Z",
  "tool": "bandit",
  "findings": [
    {
      "code": "B601",
      "line_number": 42,
      "line": "subprocess.run(cmd)",
      "filename": "src/utils/helpers.py",
      "severity": "HIGH",
      "message": "subprocess call - check for execution of untrusted input",
      "more_info": "https://bandit.readthedocs.io/en/latest/"
    }
  ]
}
```

### 2. 严重性阈值
- **Critical**: 0 个 - 必须阻止部署
- **High**: ≤ 5 个 - 需要管理员批准
- **Medium**: ≤ 20 个 - 正常部署但需跟踪
- **Low**: 任意数量 - 记录但不阻止部署

### 3. 响应流程
1. **发现**: 自动报告创建并分配给开发团队
2. **分析**: 安全团队确认漏洞严重性和影响范围
3. **修复**: 开发团队实施修复方案
4. **验证**: 安全团队验证修复效果
5. **关闭**: 问题关闭，更新知识库

## 最佳实践

### 1. 安全编码
- 使用参数化查询防止 SQL 注入
- 实施严格的输入验证
- 使用 HTTPS 和 CSP 头
- 最小权限原则
- 定期更新依赖项

### 2. 密码管理
- 强制复杂密码策略
- 实施多因素认证
- 安全存储密码（bcrypt）
- 定期轮换密码

### 3. 日志和监控
- 记录安全事件
- 实施异常检测
- 告警机制
- 定期审计

## 安全培训

### 1. 开发团队培训
- OWASP Top 10 意识
- 安全编码最佳实践
- 漏洞修复流程
- 工具使用培训

### 2. 运维团队培训
- 安全配置管理
- 入侵检测系统
- 事件响应流程
- 合规性要求

## 持续改进

### 1. 定期审查
- 每月安全审查会议
- 季度风险评估
- 年度安全审计

### 2. 工具更新
- 定期更新安全工具
- 评估新工具集成
- 社区贡献参与

### 3. 流程优化
- 收集反馈改进流程
- 威胁情报整合
- 行业最佳实践跟进

## 附录

### A. 快速检查清单
- [ ] 所有端点都有认证和授权
- [ ] 输入验证已实现
- [ ] 错误信息不泄露敏感信息
- [ ] 使用安全的依赖项
- [ ] 配置文件安全存储
- [ ] 日志记录已配置
- [ ] 安全头已设置

### B. 紧急联系
- 安全负责人: security@mystocks.com
- 技术负责人: tech@mystocks.com
- 紧急热线: +86-xxx-xxxx-xxxx

### C. 参考资料
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [OWASP ZAP](https://owasp.org/www-project-zap/)