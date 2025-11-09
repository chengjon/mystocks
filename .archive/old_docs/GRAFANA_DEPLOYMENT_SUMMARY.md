# Grafana监控面板部署总结

**创建日期**: 2025-10-12
**目标**: 在NAS (192.168.123.104) 上部署Grafana监控面板
**状态**: ✅ 配置就绪,待部署

---

## 📦 已创建的文件

### 1. 核心配置文件 (4个)

```
monitoring/
├── grafana-datasource.yml              # PostgreSQL数据源配置
├── grafana-dashboard-provider.yml      # Dashboard提供者配置
├── grafana_dashboard.json              # 监控面板JSON定义
└── docker-compose-grafana.yml          # Docker Compose配置
```

### 2. 文档文件 (3个)

```
monitoring/
├── grafana_setup.md                    # 详细部署指南
├── NAS_GRAFANA_DEPLOYMENT.md           # NAS专用部署指南
└── deploy_grafana_to_nas.sh            # 自动部署脚本
```

---

## 🚀 快速部署方法

### 方法1: 自动部署 (推荐)

```bash
cd /mnt/wd_mycode/mystocks_spec/monitoring
./deploy_grafana_to_nas.sh
```

**脚本会自动完成**:
1. ✅ 检查配置文件
2. ✅ 测试NAS连接
3. ✅ 创建目录结构
4. ✅ 上传配置文件
5. ✅ 启动Docker容器
6. ✅ 验证部署状态

**预计时间**: 5-10分钟 (包括下载镜像)

---

### 方法2: 手动部署

#### 步骤1: 上传文件到NAS

```bash
cd /mnt/wd_mycode/mystocks_spec/monitoring

# 创建目录
ssh admin@192.168.123.104 "mkdir -p /volume1/docker/mystocks-grafana/{data,config/provisioning/{datasources,dashboards}}"

# 上传配置文件
scp grafana-datasource.yml admin@192.168.123.104:/volume1/docker/mystocks-grafana/config/provisioning/datasources/
scp grafana-dashboard-provider.yml admin@192.168.123.104:/volume1/docker/mystocks-grafana/config/provisioning/dashboards/
scp grafana_dashboard.json admin@192.168.123.104:/volume1/docker/mystocks-grafana/config/provisioning/dashboards/
scp docker-compose-grafana.yml admin@192.168.123.104:/volume1/docker/mystocks-grafana/docker-compose.yml
```

#### 步骤2: 启动容器

```bash
# SSH到NAS
ssh admin@192.168.123.104

# 启动Grafana
cd /volume1/docker/mystocks-grafana
docker-compose up -d

# 查看日志
docker-compose logs -f
```

---

## 📊 监控面板说明

### 面板布局 (13个Panel)

| Panel ID | 名称 | 类型 | 位置 | 说明 |
|---------|------|------|------|------|
| 1 | 今日操作总数 | Stat | 左上 | 24小时内操作总数 |
| 2 | 慢查询数量 | Stat | 中上 | >5秒的查询数 |
| 3 | 未解决告警 | Stat | 右上 | OPEN/ACKNOWLEDGED告警 |
| 4 | 平均查询时间 | Stat | 最右上 | 24小时平均响应时间 |
| 5 | 查询时间趋势 | Time Series | 左中 | 5分钟聚合时序图 |
| 6 | 数据库性能对比 | Bar Chart | 右中 | 各数据库性能对比 |
| 7 | 慢查询Top 10 | Table | 全宽 | 最慢的10个查询 |
| 8 | 质量检查状态分布 | Pie Chart | 左下 | PASS/WARNING/FAIL占比 |
| 9 | 质量检查趋势 | Time Series | 右下 | 按维度的质量趋势 |
| 10 | 告警级别分布 | Bar Gauge | 左底 | CRITICAL/WARNING/INFO分布 |
| 11 | 未解决告警列表 | Table | 中底 | 详细告警列表 |
| 12 | 操作类型分布 | Pie Chart | 左底2 | SAVE/LOAD/UPDATE分布 |
| 13 | 操作成功率 | Table | 右底2 | 各数据库成功率 |

### 数据源配置

```yaml
数据源名称: MyStocks-Monitoring
类型: PostgreSQL
主机: 192.168.123.104:5438
数据库: mystocks_monitoring
用户: postgres
密码: Cheng.20241017 (已配置在文件中)
```

### 刷新设置

- **自动刷新**: 30秒
- **默认时间范围**: 最近24小时
- **可选时间范围**: 1小时 / 6小时 / 24小时 / 7天 / 30天

---

## 🔧 关键SQL查询

### 1. 今日操作总数

```sql
SELECT COUNT(*) as total_operations
FROM operation_logs
WHERE created_at >= NOW() - INTERVAL '24 hours';
```

### 2. 慢查询统计

```sql
SELECT COUNT(*)
FROM performance_metrics
WHERE is_slow_query = TRUE
  AND created_at >= NOW() - INTERVAL '24 hours';
```

### 3. 查询时间趋势

```sql
SELECT
  DATE_TRUNC('minute', created_at) +
    INTERVAL '5 minute' * FLOOR(EXTRACT(EPOCH FROM created_at - DATE_TRUNC('minute', created_at))/300) AS time,
  AVG(metric_value) as avg,
  MAX(metric_value) as max,
  MIN(metric_value) as min
FROM performance_metrics
WHERE metric_type = 'QUERY_TIME'
  AND created_at >= NOW() - INTERVAL '24 hours'
GROUP BY time
ORDER BY time;
```

### 4. 数据库性能对比

```sql
SELECT
  database_type,
  COUNT(*) as query_count,
  ROUND(AVG(metric_value)::NUMERIC, 2) as avg_time_ms,
  MAX(metric_value) as max_time_ms
FROM performance_metrics
WHERE metric_type = 'QUERY_TIME'
  AND created_at >= NOW() - INTERVAL '24 hours'
GROUP BY database_type
ORDER BY AVG(metric_value) DESC;
```

---

## ✅ 部署后验证清单

### 基本验证

- [ ] 访问 http://192.168.123.104:3000 成功
- [ ] 使用 admin / mystocks2025 登录成功
- [ ] 数据源"MyStocks-Monitoring"显示为绿色(已连接)
- [ ] 监控面板已自动加载

### 数据验证

- [ ] "今日操作总数"显示数字 (非0)
- [ ] "查询时间趋势"显示折线图
- [ ] "数据库性能对比"显示条形图
- [ ] 所有面板无"No Data"错误

### 功能验证

- [ ] 时间范围切换正常 (1小时/24小时/7天)
- [ ] 自动刷新正常 (30秒刷新一次)
- [ ] 面板可以拖拽调整大小
- [ ] 可以导出面板为PNG/PDF

---

## 🐛 常见问题

### Q1: 面板显示"No Data"

**原因**: 监控数据库中没有数据

**解决**:
```bash
# 运行测试生成监控数据
cd /mnt/wd_mycode/mystocks_spec
python test_monitoring_with_redis.py
```

### Q2: 数据源连接失败

**原因**: PostgreSQL连接配置错误

**解决**:
1. 验证PostgreSQL可访问:
   ```bash
   psql -h 192.168.123.104 -p 5438 -U postgres -d mystocks_monitoring
   ```
2. 检查密码是否正确 (grafana-datasource.yml)
3. 检查防火墙设置

### Q3: 容器启动失败

**原因**: 端口冲突或权限问题

**解决**:
```bash
# 检查端口占用
netstat -tuln | grep 3000

# 修改端口 (如果3000被占用)
# 编辑 docker-compose.yml: ports: - "3001:3000"

# 检查权限
chmod 777 /volume1/docker/mystocks-grafana/data
```

---

## 📱 访问方式

### 1. 浏览器访问
- **局域网**: http://192.168.123.104:3000
- **登录**: admin / mystocks2025

### 2. 移动App访问
- **iOS App**: Grafana (App Store)
- **Android App**: Grafana (Google Play)
- **Server URL**: http://192.168.123.104:3000

### 3. API访问
```bash
# 获取健康状态
curl http://192.168.123.104:3000/api/health

# 获取Dashboard列表 (需认证)
curl -u admin:mystocks2025 \
  http://192.168.123.104:3000/api/search?type=dash-db
```

---

## 🔐 安全建议

### 1. 立即修改默认密码

登录后: Profile → Change Password

### 2. 创建只读用户

```bash
curl -X POST http://admin:mystocks2025@192.168.123.104:3000/api/admin/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Viewer",
    "login": "viewer",
    "password": "viewer123",
    "role": "Viewer"
  }'
```

### 3. 配置HTTPS (生产环境)

编辑docker-compose.yml添加证书挂载:
```yaml
volumes:
  - /volume1/docker/ssl:/etc/grafana/ssl:ro
environment:
  - GF_SERVER_PROTOCOL=https
  - GF_SERVER_CERT_FILE=/etc/grafana/ssl/cert.pem
  - GF_SERVER_CERT_KEY=/etc/grafana/ssl/key.pem
```

---

## 📈 性能优化

### 1. 增加容器资源

```yaml
# docker-compose.yml
deploy:
  resources:
    limits:
      memory: 512M
      cpus: '1'
    reservations:
      memory: 256M
      cpus: '0.5'
```

### 2. 优化查询缓存

```ini
# grafana.ini
[database]
cache_ttl = 3600

[dataproxy]
timeout = 30
```

### 3. 启用查询缓存

在面板设置中:
- Query Options → Cache timeout: 300 (5分钟)

---

## 📚 相关文档

1. **详细部署指南**: `monitoring/grafana_setup.md`
2. **NAS部署指南**: `monitoring/NAS_GRAFANA_DEPLOYMENT.md`
3. **监控系统报告**: `PHASE5_US3_COMPLETION_REPORT.md`
4. **Grafana官方文档**: https://grafana.com/docs/

---

## 🎯 下一步计划

### 可选增强

1. **配置邮件告警**
   - 编辑grafana.ini配置SMTP
   - 设置告警规则和通知渠道

2. **集成Slack通知**
   - 创建Slack Webhook
   - 配置通知渠道

3. **添加自定义面板**
   - 业务指标监控
   - 用户行为分析

4. **配置反向代理**
   - 使用NAS的Web Station
   - 配置域名访问

---

## ✨ 总结

**已完成**:
- ✅ 4个核心配置文件
- ✅ 13个监控面板
- ✅ 自动部署脚本
- ✅ 完整文档

**部署方式**:
- 🚀 自动部署: `./deploy_grafana_to_nas.sh`
- 📖 手动部署: 参考NAS_GRAFANA_DEPLOYMENT.md

**访问地址**:
- 🌐 http://192.168.123.104:3000
- 👤 admin / mystocks2025

**预计时间**:
- ⏱️ 自动部署: 5-10分钟
- ⏱️ 手动部署: 15-30分钟

---

**准备就绪!** 🎉

现在可以运行 `./deploy_grafana_to_nas.sh` 开始部署!
