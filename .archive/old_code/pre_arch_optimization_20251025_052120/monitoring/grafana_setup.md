# Grafana监控面板部署指南

**创建人**: Claude
**版本**: 2.0.0
**批准日期**: 2025-09-01
**最后修订**: 2025-10-16
**本次修订内容**: Grafana监控设置

---

**版本**: 1.0.0
**创建日期**: 2025-10-12
**适用系统**: MyStocks v2.0.0

---

## 📊 概览

本指南介绍如何部署Grafana监控面板，实现MyStocks系统的可视化监控。

### 监控面板功能

- ✅ 实时性能指标展示
- ✅ 慢查询趋势分析
- ✅ 数据质量监控
- ✅ 告警历史查询
- ✅ 操作统计汇总

---

## 🚀 快速部署

### 步骤1: 安装Grafana

#### 方法A: Docker部署 (推荐)

```bash
# 1. 创建Grafana数据目录
mkdir -p /opt/mystocks/grafana/data
chmod 777 /opt/mystocks/grafana/data

# 2. 启动Grafana容器
docker run -d \
  --name mystocks-grafana \
  -p 3000:3000 \
  -v /opt/mystocks/grafana/data:/var/lib/grafana \
  -e GF_SECURITY_ADMIN_PASSWORD=mystocks2025 \
  grafana/grafana:latest

# 3. 验证启动
docker logs mystocks-grafana
```

#### 方法B: 系统安装

```bash
# Ubuntu/Debian
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install grafana

# 启动服务
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
```

**访问地址**: http://localhost:3000
**默认账号**: admin / mystocks2025

---

### 步骤2: 配置PostgreSQL数据源

1. 登录Grafana (http://localhost:3000)
2. 进入 **Configuration** → **Data Sources**
3. 点击 **Add data source**
4. 选择 **PostgreSQL**
5. 配置连接参数：

```yaml
Name: MyStocks-Monitoring
Host: 192.168.123.104:5438
Database: mystocks_monitoring
User: postgres
Password: [your-password]
SSL Mode: disable
Version: 17+
```

6. 点击 **Save & Test** 验证连接

---

### 步骤3: 导入监控面板

#### 自动导入 (推荐)

```bash
# 使用提供的JSON配置文件
cd /mnt/wd_mycode/mystocks_spec/monitoring
curl -X POST http://admin:mystocks2025@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @grafana_dashboard.json
```

#### 手动导入

1. 进入 **Create** → **Import**
2. 上传 `grafana_dashboard.json` 文件
3. 选择数据源: **MyStocks-Monitoring**
4. 点击 **Import**

---

## 📈 监控面板说明

### 面板1: 系统概览 (Overview)

**刷新间隔**: 30秒

| 指标 | 说明 | 数据源 |
|-----|------|--------|
| 今日操作总数 | 24小时内所有操作数量 | operation_logs |
| 慢查询数量 | 执行时间>5秒的查询 | performance_metrics |
| 告警总数 | 未解决的告警 | alert_records |
| 平均查询时间 | 24小时平均响应时间 | performance_metrics |

**SQL示例**:
```sql
-- 今日操作总数
SELECT COUNT(*) as total_operations
FROM operation_logs
WHERE created_at >= NOW() - INTERVAL '24 hours';
```

---

### 面板2: 性能监控 (Performance)

#### 2.1 查询时间趋势图

```sql
SELECT
  time_bucket('5 minutes', created_at) AS time,
  AVG(metric_value) as avg_time,
  MAX(metric_value) as max_time,
  MIN(metric_value) as min_time
FROM performance_metrics
WHERE metric_type = 'QUERY_TIME'
  AND created_at >= NOW() - INTERVAL '24 hours'
GROUP BY time
ORDER BY time;
```

**可视化**: 时间序列图 (Time series)
**Y轴**: 毫秒 (ms)
**图例**: AVG (平均), MAX (最大), MIN (最小)

#### 2.2 慢查询Top 10

```sql
SELECT
  metric_name,
  classification,
  database_type,
  metric_value as execution_time_ms,
  query_sql
FROM performance_metrics
WHERE is_slow_query = TRUE
  AND created_at >= NOW() - INTERVAL '7 days'
ORDER BY metric_value DESC
LIMIT 10;
```

**可视化**: 表格 (Table)
**列**: 操作名称, 分类, 数据库类型, 执行时间, SQL语句

#### 2.3 数据库性能对比

```sql
SELECT
  database_type,
  COUNT(*) as query_count,
  AVG(metric_value) as avg_time_ms,
  MAX(metric_value) as max_time_ms
FROM performance_metrics
WHERE metric_type = 'QUERY_TIME'
  AND created_at >= NOW() - INTERVAL '24 hours'
GROUP BY database_type
ORDER BY avg_time_ms DESC;
```

**可视化**: 柱状图 (Bar chart)

---

### 面板3: 数据质量监控 (Data Quality)

#### 3.1 质量检查状态分布

```sql
SELECT
  check_status,
  COUNT(*) as count
FROM data_quality_checks
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY check_status;
```

**可视化**: 饼图 (Pie chart)
**颜色**: PASS (绿色), WARNING (黄色), FAIL (红色)

#### 3.2 各维度质量趋势

```sql
SELECT
  time_bucket('1 hour', created_at) AS time,
  check_type,
  COUNT(CASE WHEN check_status = 'FAIL' THEN 1 END) as failed_checks,
  COUNT(CASE WHEN check_status = 'WARNING' THEN 1 END) as warning_checks
FROM data_quality_checks
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY time, check_type
ORDER BY time;
```

**可视化**: 堆叠区域图 (Stacked area)

#### 3.3 表级质量报告

```sql
SELECT
  table_name,
  classification,
  database_type,
  AVG(missing_rate) as avg_missing_rate,
  AVG(data_delay_seconds) as avg_delay_seconds,
  COUNT(*) as check_count
FROM data_quality_checks
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY table_name, classification, database_type
ORDER BY avg_missing_rate DESC;
```

**可视化**: 表格 (Table)

---

### 面板4: 告警监控 (Alerts)

#### 4.1 告警级别分布

```sql
SELECT
  alert_level,
  COUNT(*) as count,
  SUM(occurrence_count) as total_occurrences
FROM alert_records
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY alert_level
ORDER BY
  CASE alert_level
    WHEN 'CRITICAL' THEN 1
    WHEN 'WARNING' THEN 2
    WHEN 'INFO' THEN 3
  END;
```

**可视化**: 条形图 (Bar gauge)

#### 4.2 未解决告警列表

```sql
SELECT
  alert_id,
  alert_level,
  alert_type,
  alert_title,
  alert_message,
  occurrence_count,
  created_at,
  NOW() - created_at as age
FROM alert_records
WHERE alert_status IN ('OPEN', 'ACKNOWLEDGED')
ORDER BY
  CASE alert_level
    WHEN 'CRITICAL' THEN 1
    WHEN 'WARNING' THEN 2
    WHEN 'INFO' THEN 3
  END,
  created_at DESC
LIMIT 20;
```

**可视化**: 表格 (Table)
**高亮**: CRITICAL (红色), WARNING (黄色)

#### 4.3 告警趋势图

```sql
SELECT
  time_bucket('1 hour', created_at) AS time,
  alert_type,
  COUNT(*) as count
FROM alert_records
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY time, alert_type
ORDER BY time;
```

**可视化**: 时间序列图 (Time series)

---

### 面板5: 操作统计 (Operations)

#### 5.1 操作类型分布

```sql
SELECT
  operation_type,
  COUNT(*) as count,
  SUM(record_count) as total_records
FROM operation_logs
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY operation_type;
```

**可视化**: 饼图 (Pie chart)

#### 5.2 数据分类操作热力图

```sql
SELECT
  time_bucket('15 minutes', created_at) AS time,
  classification,
  COUNT(*) as operation_count
FROM operation_logs
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY time, classification
ORDER BY time;
```

**可视化**: 热力图 (Heatmap)

#### 5.3 操作成功率

```sql
SELECT
  target_database,
  COUNT(*) as total,
  COUNT(CASE WHEN operation_status = 'SUCCESS' THEN 1 END) as success,
  COUNT(CASE WHEN operation_status = 'FAILED' THEN 1 END) as failed,
  ROUND(
    COUNT(CASE WHEN operation_status = 'SUCCESS' THEN 1 END)::NUMERIC /
    COUNT(*)::NUMERIC * 100,
    2
  ) as success_rate
FROM operation_logs
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY target_database;
```

**可视化**: 表格 (Table) + 进度条

---

## 🎨 面板配置建议

### 刷新间隔

- **概览面板**: 30秒
- **性能监控**: 1分钟
- **数据质量**: 5分钟
- **告警监控**: 30秒
- **操作统计**: 1分钟

### 时间范围

- **默认**: 最近24小时
- **可选**: 最近1小时, 最近7天, 最近30天, 自定义

### 告警规则

在Grafana中配置告警规则 (Alert Rules):

```yaml
# 慢查询告警
慢查询数量过多:
  条件: COUNT(is_slow_query=TRUE) > 10 (5分钟内)
  级别: WARNING
  通知渠道: Email, Slack

# 数据质量告警
数据质量检查失败:
  条件: COUNT(check_status='FAIL') > 5 (1小时内)
  级别: CRITICAL
  通知渠道: Email, PagerDuty

# 系统告警
未解决告警堆积:
  条件: COUNT(alert_status='OPEN') > 20
  级别: WARNING
  通知渠道: Slack
```

---

## 🔧 高级配置

### 1. 配置告警通知渠道

#### 邮件通知

编辑 `/etc/grafana/grafana.ini`:

```ini
[smtp]
enabled = true
host = smtp.example.com:587
user = alerts@example.com
password = secret
from_address = grafana@example.com
from_name = MyStocks Monitoring
```

#### Slack通知

1. 进入 **Alerting** → **Notification channels**
2. 点击 **New channel**
3. 类型选择 **Slack**
4. 配置Webhook URL
5. 测试并保存

### 2. 用户权限管理

```bash
# 创建只读用户
curl -X POST http://admin:mystocks2025@localhost:3000/api/admin/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Viewer",
    "email": "viewer@example.com",
    "login": "viewer",
    "password": "viewer123",
    "role": "Viewer"
  }'
```

### 3. API Token生成

```bash
# 生成API Token用于自动化
curl -X POST http://admin:mystocks2025@localhost:3000/api/auth/keys \
  -H "Content-Type: application/json" \
  -d '{
    "name": "mystocks-automation",
    "role": "Admin",
    "secondsToLive": 31536000
  }'
```

---

## 📱 移动访问

Grafana支持移动端浏览器访问，推荐使用Grafana官方移动应用：

- **iOS**: https://apps.apple.com/app/grafana/id1475826620
- **Android**: https://play.google.com/store/apps/details?id=com.grafana.mobile

---

## 🐛 故障排查

### 问题1: 无法连接PostgreSQL

```bash
# 检查PostgreSQL连接
psql -h 192.168.123.104 -p 5438 -U postgres -d mystocks_monitoring

# 检查防火墙
sudo ufw allow 5438/tcp
```

### 问题2: 面板显示"No Data"

```bash
# 检查监控数据库是否有数据
psql -h 192.168.123.104 -p 5438 -U postgres -d mystocks_monitoring -c "
SELECT
  (SELECT COUNT(*) FROM operation_logs) as operations,
  (SELECT COUNT(*) FROM performance_metrics) as metrics,
  (SELECT COUNT(*) FROM data_quality_checks) as quality_checks,
  (SELECT COUNT(*) FROM alert_records) as alerts;
"
```

### 问题3: Grafana性能慢

```ini
# 优化配置 (/etc/grafana/grafana.ini)
[database]
max_open_conn = 50
max_idle_conn = 10

[dataproxy]
timeout = 30
keep_alive_seconds = 30
```

---

## 📚 相关资源

- **Grafana官方文档**: https://grafana.com/docs/
- **PostgreSQL数据源文档**: https://grafana.com/docs/grafana/latest/datasources/postgres/
- **告警规则文档**: https://grafana.com/docs/grafana/latest/alerting/
- **仪表板最佳实践**: https://grafana.com/docs/grafana/latest/best-practices/

---

## ✅ 部署清单

- [ ] 安装Grafana (Docker或系统安装)
- [ ] 配置PostgreSQL数据源
- [ ] 导入监控面板JSON配置
- [ ] 配置刷新间隔和时间范围
- [ ] 设置告警规则
- [ ] 配置通知渠道 (邮件/Slack)
- [ ] 创建用户和权限
- [ ] 测试所有面板数据显示
- [ ] 配置移动端访问
- [ ] 文档交接

---

**部署完成后访问**: http://localhost:3000/d/mystocks-monitoring

**预计部署时间**: 30-60分钟

**维护负责人**: [待填写]

---

*本文档最后更新: 2025-10-12*
