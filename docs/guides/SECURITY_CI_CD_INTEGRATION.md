# MyStocks 安全CI/CD集成指南

## 概述

本文档详细说明了如何将安全测试集成到 MyStocks 项目的 CI/CD 流程中，确保代码质量和安全性在每次提交和部署时都得到验证。

## 架构概览

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CI/CD 安全测试流程                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐  │
│  │   开发环境      │    │   CI/CD 流程     │    │   生产环境      │  │
│  │                 │    │                 │    │                 │  │
│  │ - 本地安全检查  │───▶│ - 自动化扫描    │───▶│ - 部署前验证    │  │
│  │ - 预提交钩子    │    │ - 质量门禁      │    │ - 运行时监控    │  │
│  │ - 手动测试      │    │ - 报告生成      │    │ - 实时告警      │  │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## CI/CD 工作流

### 1. 主安全工作流 (.github/workflows/security-testing.yml)

#### 触发条件
- `push` 到 `main` 或 `develop` 分支
- `pull_request` 到 `main` 或 `develop` 分支
- 每天凌晨2点的定时扫描

#### 主要阶段

```yaml
# 1. 安全扫描阶段 (SAST)
security-scan:
  - Bandit 静态代码分析
  - Safety 依赖漏洞扫描
  - Semgrep 深度安全扫描

# 2. 依赖检查阶段
dependency-check:
  - pip-audit 依赖安全审计

# 3. Python安全测试阶段
python-security-tests:
  - OWASP Top 10 安全测试
  - 认证安全测试

# 4. 前端安全测试阶段
frontend-security-tests:
  - npm audit 依赖检查
  - Snyk 安全扫描

# 5. 安全报告生成阶段
security-report:
  - 汇总所有安全扫描结果
  - 生成安全测试报告

# 6. 安全质量门禁阶段
security-gate:
  - 验证安全指标是否达标
  - 阻止不安全的代码合并

# 7. 部署前最终验证
pre-deployment-security:
  - 关键安全点最终检查
  - 确保部署就绪

# 8. 安全通知阶段
security-notification:
  - 发送测试结果通知
  - 记录安全状态
```

#### 质量门禁规则

```yaml
# 安全质量门禁标准
security-gate:
  critical:
    - 严重安全问题: 0个
    - 关键漏洞依赖: 0个

  high:
    - 高危问题: ≤5个
    - 安全测试失败: ≤2项

  medium:
    - 中等问题: ≤10个
    - 漏洞依赖: ≤5个
```

### 2. 代码质量工作流 (.github/workflows/code-quality.yml)

#### 主要功能
- **代码风格检查**: Black, isort, Flake8
- **静态分析**: Pylint with security profile
- **测试覆盖率**: 至少80%覆盖率
- **性能基准**: 性能回归检测
- **复杂度分析**: 代码复杂度监控
- **安全合规**: 安全编码规范检查

### 3. 预提交钩子 (.pre-commit-config-security.yaml)

#### 钩子类型
```yaml
# 本地安全检查
- Bandit 安全扫描
- Safety 依赖检查
- OWASP Top 10 测试
- 认证安全测试
- 密码策略检查
- SQL注入检查
- XSS防护检查
- 硬编码密钥检查
- 文件上传安全检查
- 会话管理检查
- CSRF保护检查
- 权限验证检查
- 输入验证检查
- 错误处理安全检查
- 日志安全检查
- 配置安全检查

# 第三方工具
- Pylint 安全分析
- Flake8 安全检查
- Grype 漏洞扫描
- Docker/Kubernetes 安全基准
```

#### 使用方式
```bash
# 安装预提交钩子
pre-commit install

# 运行所有钩子
pre-commit run --all-files

# 跳过特定钩子
pre-commit run --hook-skip bandit --all-files
```

## 安全测试工具集成

### 1. 静态应用安全测试 (SAST)

#### Bandit - Python安全扫描
```bash
# 基本扫描
bandit -r src/

# JSON格式输出
bandit -r src/ -f json -o bandit-report.json

# 指定配置文件
bandit -r src/ -c bandit-config.yaml
```

#### Semgrep - 深度安全扫描
```bash
# 自动配置扫描
semgrep --config auto --json -o semgrep-report.json src/

# 自定义规则扫描
semgrep --config p/security -r src/

# 集成到CI/CD
semgrep --ci --upload-build semgrep-report.json
```

### 2. 依赖漏洞扫描

#### Safety - Python依赖安全检查
```bash
# 检查已知漏洞
safety check --json --output safety-report.json

# 检查特定依赖
safety check --package django

# 创建忽略列表
safety check --ignore Django==3.2.0
```

#### Pip-audit - 依赖安全审计
```bash
# 审计当前环境
pip-audit --json --output pip-audit-report.json

# 审计特定文件
pip-audit --requirement requirements.txt

# 检查哈希完整性
pip-audit --require-hashes
```

### 3. 动态应用安全测试 (DAST)

#### OWASP ZAP - 动态扫描
```bash
# 启动ZAP代理
zap.sh -daemon -port 8080

# 运行扫描
zap-baseline.py -t http://localhost:3000 -g zap-report.html

# 生成报告
python scripts/dast/zap_generate_report.py
```

#### SQLmap - SQL注入测试
```bash
# 基本注入测试
sqlmap -u "http://localhost:8000/api/users?id=1" --batch

# POST请求测试
sqlmap -r request.txt --batch

# 数据库枚举
sqlmap -u "http://localhost:8000/api/users?id=1" --dbs
```

### 4. 软件成分分析 (SCA)

#### Grype - 容器镜像扫描
```bash
# 扫描构建的镜像
grype mystocks:latest -o json > grype-report.json

# 扫描目录
grype ./ -o json > grype-directory-report.json

# 忽略特定漏洞
grype ./ -o json > grype-report.json --ignore CVE-2021-1234
```

#### Dependabot - 自动依赖更新
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    assignees:
      - "security-team"
    reviewers:
      - "maintainers"
```

## 安全测试最佳实践

### 1. 开发阶段安全实践

#### 代码编写阶段
- 使用安全的编码标准
- 定期运行本地安全检查
- 遵循安全开发生命周期 (SDLC)
- 使用 IDE 安全插件实时检测

#### 提交阶段
- 预提交钩子自动运行
- 所有安全检查必须通过
- 提交信息包含安全相关标记

#### 审查阶段
- 至少一名安全专家审查
- 使用安全审查清单
- 高风险代码需要多人审查

### 2. CI/CD 阶段安全实践

#### 自动化扫描
- 每次提交都运行安全扫描
- 定期进行深度安全测试
- 集成多种安全工具

#### 质量门禁
- 设置合理的安全阈值
- 严重安全问题必须修复
- 建立漏洞响应流程

#### 报告和通知
- 生成可读的安全报告
- 实时通知安全事件
- 跟踪漏洞修复进度

### 3. 部署阶段安全实践

#### 部署前验证
- 运行最终安全检查
- 验证配置文件安全
- 检查依赖项完整性

#### 部署后监控
- 实时监控安全事件
- 日志分析和异常检测
- 自动响应安全威胁

## 安全测试配置

### 1. 环境变量配置

```bash
# GitHub Secrets
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
SNYK_TOKEN=sk_...
GH_TOKEN=ghp_...

# 安全工具配置
BANDIT_CONFIG=bandit-config.yaml
SEMGREP_CONFIG=.semgrepignore
PYLINTRC=.pylintrc
```

### 2. 安全配置文件

#### .bandit
```ini
[bandit]
skips: B101,B601
exclude_dirs: tests,venv
severity_level: high
confidence_level: medium
```

#### .semgrepignore
```
# 测试文件
test_*
*_test.py

# 第三方库
venv/
.env
node_modules/
```

#### .pylintrc
```ini
[MESSAGES CONTROL]
disable=import-error,C0111,C0103

[FORMAT]
max-line-length=88

[BASIC]
good-names=id,x,y

[SIMILARITIES]
min-similarity-lines=5
```

### 3. 安全测试脚本配置

#### scripts/dev/check_password_policy.py
- 检查密码哈希算法
- 验证密码强度要求
- 检测明文密码存储

#### scripts/dev/check_sql_injection.py
- 检测SQL注入风险
- 验证参数化查询使用
- 检查ORM使用情况

## 故障排除

### 常见问题

#### 1. Bandit扫描失败
```bash
# 解决方案：更新Bandit配置
echo "[bandit]" > .bandit
echo "skips = B101,B601" >> .bandit
echo "exclude_dirs = tests,venv" >> .bandit
```

#### 2. 安全测试超时
```yaml
# 在GitHub Actions中增加超时时间
steps:
  - name: Security tests
    timeout-minutes: 30
```

#### 3. 依赖检查失败
```bash
# 更新安全工具
pip install --upgrade bandit safety semgrep

# 清理pip缓存
pip cache purge
```

### 性能优化

#### 1. 并行执行
```yaml
jobs:
  security-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        check: [bandit, safety, semgrep]
      max-parallel: 3
```

#### 2. 缓存优化
```yaml
steps:
  - name: Cache dependencies
    uses: actions/cache@v3
    with:
      path: ~/.cache/pip
      key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

## 监控和报告

### 1. 安全指标监控

#### 关键指标
- 安全漏洞数量（按严重程度分类）
- 测试覆盖率（目标：80%+）
- 修复响应时间（目标：72小时内）
- 安全测试通过率

#### 监控工具
- GitHub Security Alerts
- Slack 通知
- Grafana 仪表板
- 定期安全报告

### 2. 报告生成

#### 自动报告
```bash
# 生成安全报告
python scripts/security/generate_security_report.py

# 发送邮件报告
python scripts/security/send_security_email.py

# 更新安全状态页
python scripts/security/update_security_dashboard.py
```

### 3. 持续改进

#### 定期审查
- 每月审查安全测试结果
- 更新安全配置和规则
- 改进检测能力
- 培训开发团队

#### 流程优化
- 根据实际风险调整扫描频率
- 优化质量门禁阈值
- 集成新的安全工具
- 改进响应流程

## 总结

通过将安全测试全面集成到 CI/CD 流程中，MyStocks 项目实现了：

1. **自动化安全检查** - 每次提交都进行安全扫描
2. **质量门禁** - 确保只有安全的代码才能合并
3. **持续监控** - 实时监控项目安全状态
4. **快速响应** - 及时发现和修复安全问题
5. **团队协作** - 建立安全开发和审查文化

这种集成化的安全测试流程显著提高了项目的安全性和代码质量，为用户数据和安全运行提供了强有力的保障。

## 相关资源

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [OWASP 安全测试指南](https://owasp.org/www-project-security-testing-guide/)
- [Bandit 文档](https://bandit.readthedocs.io/)
- [Semgrep 文档](https://semgrep.dev/)
- [OWASP Top 10](https://owasp.org/Top10/)