# 登录 API 优雅降级 - 监控告警指南

**日期**: 2025-10-28
**修复方案**: 登录 API MFA 查询失败处理 + 完善的监控告警
**提交记录**:
- commit 238fdfa: 初始修复（优雅降级）
- commit f438cec: 监控告警增强

---

## 📋 执行摘要

本文档说明如何通过完善的监控告警机制来确保优雅降级模式不会掩盖底层的持续性故障（如数据库损坏或连接问题）。

**核心原则**: 优雅降级 + 主动监控 = 用户体验 + 问题可见性

---

## 🔍 实现的监控点

### 1. 单次失败事件监控 (WARNING 级别)

**事件名**: `mfa_check_failed`
**记录时机**: 每次 MFA 数据库查询失败时
**日志级别**: `WARNING`

**日志示例**:
```python
logger.warning(
    "mfa_check_failed",
    username="admin",
    error="ProgrammingError: relation 'user_model' does not exist",
    failure_count=1,
    event_type="graceful_degradation_triggered",
)
```

**监控系统应该**:
- 捕获所有 `mfa_check_failed` 事件
- 记录失败原因和用户名
- 用于理解单次故障原因

**示例告警规则** (Prometheus/Loki):
```yaml
# 捕获 MFA 检查失败事件
- alert: MFACheckFailure
  expr: logs_mfa_check_failed_total > 0
  for: 1m
  annotations:
    summary: "MFA database check failed for user {{ $labels.username }}"
    description: "Error: {{ $labels.error }}"
```

---

### 2. 持续性故障告警 (ERROR 级别)

**事件名**: `mfa_persistent_failure_alert`
**记录时机**: 连续失败次数 ≥ 5 次时
**日志级别**: `ERROR`
**严重程度**: `HIGH`

**日志示例**:
```python
logger.error(
    "mfa_persistent_failure_alert",
    failure_count=5,
    threshold=5,
    message="MFA database checks have failed persistently. This may indicate a database corruption or connectivity issue.",
    severity="HIGH",
    action_required="Investigate database health and MFA tables immediately",
)
```

**这表示**:
- 数据库问题不是临时的
- 可能的根本原因:
  - 数据库表损坏
  - 连接池耗尽
  - 权限问题
  - 磁盘空间满

**监控系统应该**:
- **立即告警**: 发送 Slack/钉钉/Email 通知
- **自动检查**: 触发数据库健康检查脚本
- **生成报告**: 记录告警时间和持续时间
- **发起工单**: 自动创建 incident ticket

**示例告警规则** (Prometheus/Loki):
```yaml
# 捕获持续性故障告警
- alert: MFAPersistentFailure
  expr: logs_mfa_persistent_failure_alert_total > 0
  for: 0m  # 立即触发
  annotations:
    summary: "CRITICAL: MFA database has persistent failures"
    description: "Failure count: {{ $labels.failure_count }}, Action: {{ $labels.action_required }}"
    severity: critical
    runbook_url: "https://wiki.company.com/mfa-db-recovery"
```

---

### 3. 失败计数器重置

**重置条件**: MFA 查询成功时
**重置机制**: 自动设置 `_mfa_query_failure_count = 0`
**目的**: 区分临时故障 vs 持续故障

**工作流程**:
```
失败 1 次 → WARNING (graceful degradation)
失败 2 次 → WARNING
...
失败 5 次 → ERROR + HIGH severity alert
...
失败 10 次 → ERROR alert (已分别触发 5 次)
↓
成功 1 次 → 计数重置为 0
↓
失败 1 次 → WARNING (新的故障周期开始)
```

---

## 📊 推荐的监控配置

### 配置 1: Prometheus + Alertmanager (推荐)

**步骤 1**: 配置 log exporter
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'auth-api'
    static_configs:
      - targets: ['localhost:8000']

  - job_name: 'auth-logs'
    static_configs:
      - targets: ['localhost:9144']  # loki-exporter
```

**步骤 2**: 创建告警规则
```yaml
# alert_rules.yml
groups:
  - name: auth_alerts
    rules:
      - alert: MFACheckFailure
        expr: increase(mfa_check_failed_total[5m]) > 0
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "MFA check failed: {{ $value }} times in 5 minutes"

      - alert: MFAPersistentDatabaseFailure
        expr: mfa_failure_count >= 5
        for: 0m
        labels:
          severity: critical
        annotations:
          summary: "CRITICAL: MFA database persistent failure detected"
          runbook: "https://wiki/mfa-recovery"
```

**步骤 3**: Alertmanager 配置
```yaml
# alertmanager.yml
route:
  receiver: 'default-receiver'
  group_by: ['alertname', 'severity']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h

  routes:
    - match:
        severity: critical
      receiver: 'pagerduty-on-call'
      continue: true

receivers:
  - name: 'default-receiver'
    slack_configs:
      - api_url: 'https://hooks.slack.com/...'
        channel: '#alerts'

  - name: 'pagerduty-on-call'
    pagerduty_configs:
      - service_key: 'YOUR_SERVICE_KEY'
```

---

### 配置 2: Loki + Grafana (适合已有 ELK 的场景)

**日志查询** (Loki LogQL):
```loki
# 查询所有 MFA 检查失败
{job="auth-api"} | json | event_type="graceful_degradation_triggered"

# 查询持续性故障告警
{job="auth-api"} | json | event_type="mfa_persistent_failure_alert"

# 计算失败频率
rate({job="auth-api"} | json | event_type="graceful_degradation_triggered" [5m])
```

**Grafana Dashboard Panel**:
```json
{
  "title": "MFA Database Health",
  "targets": [
    {
      "expr": "rate(mfa_check_failed_total[5m])",
      "legendFormat": "Failures/5m"
    },
    {
      "expr": "mfa_failure_count",
      "legendFormat": "Current failure count"
    }
  ],
  "thresholds": [
    {
      "value": 0,
      "color": "green"
    },
    {
      "value": 5,
      "color": "red",
      "op": "gt"
    }
  ]
}
```

---

### 配置 3: ELK + Kibana (适合已有 Elasticsearch 的场景)

**Kibana 告警**:
```json
{
  "trigger": {
    "schedule": {
      "interval": "1m"
    }
  },
  "input": {
    "search": {
      "indices": ["logs-auth-api"],
      "body": {
        "query": {
          "bool": {
            "must": [
              {
                "range": {
                  "@timestamp": {
                    "gte": "now-5m"
                  }
                }
              },
              {
                "match": {
                  "event_type": "graceful_degradation_triggered"
                }
              }
            ]
          }
        }
      }
    }
  },
  "condition": {
    "compare": {
      "ctx.payload.hits.total": {
        "gt": 0
      }
    }
  },
  "actions": {
    "send_email": {
      "email": {
        "to": "devops@company.com",
        "subject": "MFA Database Check Failures Detected",
        "body": "Failure count: {{ ctx.payload.hits.total }}"
      }
    }
  }
}
```

---

## 🔧 手动诊断步骤

当收到 `mfa_persistent_failure_alert` 时：

### 步骤 1: 确认告警

```bash
# 查看最近的 auth 日志
docker logs mystocks-backend | grep "mfa_persistent_failure_alert"

# 统计失败次数
docker logs mystocks-backend | grep "mfa_check_failed" | wc -l
```

### 步骤 2: 检查数据库连接

```bash
# 测试 PostgreSQL 连接
psql -h 192.168.123.104 -U postgres -d mystocks -c "SELECT 1"

# 检查连接状态
psql -h 192.168.123.104 -U postgres -d mystocks -c "\conninfo"
```

### 步骤 3: 验证 MFA 表

```bash
# 检查表是否存在
psql -h 192.168.123.104 -U postgres -d mystocks \
  -c "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"

# 检查表结构
psql -h 192.168.123.104 -U postgres -d mystocks \
  -c "\d user_model"
psql -h 192.168.123.104 -U postgres -d mystocks \
  -c "\d mfa_secret"
```

### 步骤 4: 检查用户表

```bash
# 查询特定用户
psql -h 192.168.123.104 -U postgres -d mystocks \
  -c "SELECT * FROM user_model WHERE username='admin'"

# 查询 MFA 设置
psql -h 192.168.123.104 -U postgres -d mystocks \
  -c "SELECT * FROM mfa_secret WHERE user_id=1"
```

### 步骤 5: 数据库修复

如果发现表损坏：

```bash
# 检查 PostgreSQL 日志
tail -50 /var/log/postgresql/postgresql.log

# 运行数据库完整性检查
psql -h 192.168.123.104 -U postgres -d mystocks \
  -c "REINDEX TABLE user_model; REINDEX TABLE mfa_secret;"

# 如果需要恢复，从备份还原
pg_restore -h 192.168.123.104 -U postgres -d mystocks /backup/mystocks_backup.dump
```

---

## 📈 性能指标

### 关键监控指标

| 指标 | 正常值 | 警告值 | 严重值 |
|------|--------|---------|----------|
| MFA 检查成功率 | > 99% | 95-99% | < 95% |
| 连续失败次数 | 0 | 1-4 | ≥ 5 |
| 恢复时间 | < 1m | 1-5m | > 5m |
| 告警频率 | 0/day | 1-5/day | > 5/day |

### 建议的监控阈值

```yaml
# Prometheus alerting rules
- alert: MFACheckFailureWarning
  expr: mfa_failure_count >= 1
  for: 2m
  annotations:
    severity: warning
    description: "MFA check started failing {{ $value }} times"

- alert: MFACheckFailureCritical
  expr: mfa_failure_count >= 5
  for: 0m
  annotations:
    severity: critical
    description: "MFA check persistent failure - IMMEDIATE ACTION REQUIRED"
```

---

## 🔄 故障恢复流程

### 短期响应 (0-5 分钟)

1. **确认告警**: 验证是否真实故障
2. **通知团队**: Slack/页面告警
3. **启动调查**: 检查最近的日志和数据库状态
4. **快速修复**: 重启 API 服务或数据库连接池

### 中期响应 (5-30 分钟)

1. **根本原因分析**: 检查 PostgreSQL 错误日志
2. **验证表完整性**: 运行 REINDEX
3. **检查权限**: 验证用户权限和表访问
4. **性能调查**: 检查是否有慢查询阻塞

### 长期改进 (1-7 天)

1. **事后分析**: 记录故障原因和改进措施
2. **测试改进**: 添加自动化测试覆盖 MFA 查询失败
3. **文档更新**: 更新 runbook 和故障排查指南
4. **容量规划**: 评估是否需要增加连接池或数据库资源

---

## ✅ 验证清单

在部署到生产环境前，请确认：

- [ ] 监控系统已配置并测试
- [ ] 告警规则已激活
- [ ] 通知渠道已验证 (Slack/Email/PagerDuty)
- [ ] 故障恢复文档已准备
- [ ] 团队已培训
- [ ] 备份恢复流程已测试
- [ ] 数据库备份计划已执行

---

## 📞 故障排查流程图

```
登录请求
  ↓
[用户认证] → 通过 / 失败
  ↓
成功 → [MFA 检查]
      ├─ 成功 → [返回 token]
      └─ 异常 → [记录 WARNING 日志]
                 ↓
            [失败计数+1]
                 ↓
         [计数 >= 5?]
         ├─ 否 → [继续登录流程]
         └─ 是 → [记录 ERROR + 告警]
                 ↓
            [监控系统捕获]
                 ↓
            [告警通知]
                 ↓
            [团队响应]
```

---

## 📚 相关文档

- [登录 API BUG 修复报告](./login_api_verification_report.md)
- [BUG 修复规范](../BUG修复AI协作规范.md)
- [系统监控部署指南](./monitoring_deployment.md)

---

**文档版本**: v1.0
**最后更新**: 2025-10-28
**作者**: Claude AI Code Assistant

