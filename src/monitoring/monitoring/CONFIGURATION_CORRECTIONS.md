# 配置修正说明

**创建日期**: 2025-10-12
**重要性**: ⚠️ 必读

---

## 🔧 配置差异说明

### 1. 数据库区分

系统使用**两个独立的PostgreSQL数据库**：

| 数据库 | 名称 | 用途 | 配置位置 |
|-------|------|------|---------|
| **业务数据库** | `mystocks` | 存储股票行情、交易数据等 | .env文件第17行 |
| **监控数据库** | `mystocks_monitoring` | 存储监控日志、性能指标、告警 | Grafana配置 |

**为什么需要两个数据库？**
- ✅ **隔离**: 监控数据不影响业务数据
- ✅ **安全**: 监控数据库故障不影响业务
- ✅ **性能**: 避免监控查询影响业务查询
- ✅ **管理**: 可以独立设置保留策略

---

## 🔐 正确的配置参数

### 从.env文件读取的正确密码

```bash
POSTGRESQL_PASSWORD=c790414J  # ← 这是正确的密码
```

### Grafana数据源配置（修正后）

```yaml
Name: MyStocks-Monitoring
Host: 192.168.123.104:5438
Database: mystocks_monitoring    # ← 监控数据库（需要创建）
User: postgres
Password: c790414J               # ← 修正：使用.env中的密码
SSL Mode: disable
Version: 15                      # ← 修正：选择15（Grafana最高支持）
TimescaleDB: ☐ (不勾选)
```

---

## 📝 配置步骤（修正版）

### 步骤1: 创建监控数据库

在NAS或开发机上执行：

```bash
# 使用正确的密码连接
export PGPASSWORD='c790414J'

# 创建监控数据库
psql -h 192.168.123.104 -p 5438 -U postgres -d postgres -c "
CREATE DATABASE mystocks_monitoring
  WITH OWNER = postgres
       ENCODING = 'UTF8'
       LC_COLLATE = 'en_US.utf8'
       LC_CTYPE = 'en_US.utf8'
       TEMPLATE = template0;
"

# 初始化监控schema
psql -h 192.168.123.104 -p 5438 -U postgres -d mystocks_monitoring \
  -f /mnt/wd_mycode/mystocks_spec/monitoring/init_monitoring_db.sql

# 验证表创建
psql -h 192.168.123.104 -p 5438 -U postgres -d mystocks_monitoring -c "
SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;
"
```

**预期输出**:
```
        tablename
--------------------------
 alert_records
 data_quality_checks
 operation_logs
 performance_metrics
(4 rows)
```

---

### 步骤2: 更新Grafana数据源配置文件

修正 `monitoring/grafana-datasource.yml`:

```yaml
apiVersion: 1

datasources:
  - name: MyStocks-Monitoring
    type: postgres
    access: proxy
    url: 192.168.123.104:5438
    database: mystocks_monitoring
    user: postgres
    secureJsonData:
      password: 'c790414J'      # ← 修正密码
    jsonData:
      sslmode: 'disable'
      postgresVersion: 1500     # ← 修正版本号（对应PostgreSQL 15）
      timescaledb: false
    editable: true
    isDefault: true
```

---

### 步骤3: Grafana手动配置（浏览器）

访问 http://192.168.123.104:3000 后配置：

#### PostgreSQL数据源配置

```
导航: Configuration → Data Sources → Add data source → PostgreSQL

配置参数:
  Name: MyStocks-Monitoring
  Host: 192.168.123.104:5438
  Database: mystocks_monitoring       ← 监控数据库
  User: postgres
  Password: c790414J                  ← 使用.env中的密码
  SSL Mode: disable
  Version: 15                         ← 选择15（最接近17的版本）
  TimescaleDB support: ☐ (不勾选)

点击: Save & test
```

**关于PostgreSQL版本选择**:

虽然实际版本是17.6，但Grafana当前最高支持到15:
- ✅ **可以选择15** - 完全兼容，功能正常
- ✅ PostgreSQL向后兼容，15的驱动可以连接17版本
- ✅ 只是数据类型和一些新特性可能不支持，但不影响监控查询

---

## 🔄 更新已部署的配置

### 方法1: 重新部署容器（推荐）

1. 修改 `monitoring/grafana-datasource.yml` 中的密码
2. 在NAS上重启Grafana容器：

```bash
ssh admin@192.168.123.104
cd /volume1/docker/mystocks-grafana
docker-compose down
docker-compose up -d
```

### 方法2: 手动配置（如果方法1不可行）

直接在Grafana Web界面手动配置数据源（按照上述步骤3）

---

## ✅ 验证配置正确性

### 测试1: 数据库连接

```bash
export PGPASSWORD='c790414J'
psql -h 192.168.123.104 -p 5438 -U postgres -d mystocks_monitoring -c "
SELECT COUNT(*) as table_count
FROM information_schema.tables
WHERE table_schema = 'public';
"
```

预期输出: `table_count = 4` (或更多，包括视图)

### 测试2: 监控数据查询

```bash
export PGPASSWORD='c790414J'
psql -h 192.168.123.104 -p 5438 -U postgres -d mystocks_monitoring -c "
SELECT COUNT(*) as operation_count FROM operation_logs;
SELECT COUNT(*) as metric_count FROM performance_metrics;
SELECT COUNT(*) as quality_check_count FROM data_quality_checks;
SELECT COUNT(*) as alert_count FROM alert_records;
"
```

### 测试3: Grafana数据源

在Grafana中:
1. Configuration → Data Sources → MyStocks-Monitoring
2. 滚动到底部点击 **Test**
3. 应该看到绿色 ✓ "Database Connection OK"

---

## 📊 正确的配置总结

| 配置项 | 业务数据库 | 监控数据库 |
|-------|-----------|-----------|
| **数据库名** | mystocks | mystocks_monitoring |
| **主机** | 192.168.123.104:5438 | 192.168.123.104:5438 |
| **用户** | postgres | postgres |
| **密码** | c790414J | c790414J |
| **用途** | 股票业务数据 | 系统监控数据 |
| **Grafana连接** | ❌ 不需要 | ✅ 需要 |

---

## 🚨 常见错误

### ❌ 错误1: 使用了错误的密码

```
错误密码: Cheng.20241017
正确密码: c790414J
```

### ❌ 错误2: 连接到业务数据库

```
错误: Database: mystocks
正确: Database: mystocks_monitoring
```

### ❌ 错误3: PostgreSQL版本不匹配

```
实际版本: 17.6
Grafana选项: 最高15
解决方案: 选择15即可，完全兼容
```

---

## 📝 快速修正检查清单

配置前请检查：

- [ ] 监控数据库 `mystocks_monitoring` 已创建
- [ ] 4张监控表已创建（operation_logs, performance_metrics, data_quality_checks, alert_records）
- [ ] 密码使用 `c790414J`（来自.env文件）
- [ ] PostgreSQL版本选择 `15`
- [ ] 数据库名称为 `mystocks_monitoring`（不是mystocks）

---

## 📞 需要帮助？

如果配置仍有问题：

1. 检查密码是否正确: `c790414J`
2. 检查数据库是否存在: `psql ... -l | grep monitoring`
3. 检查表是否创建: `psql ... -d mystocks_monitoring -c "\dt"`
4. 查看本文档的"验证配置正确性"部分

---

**文档版本**: 1.0.0
**最后更新**: 2025-10-12

⚠️ **重要**: 请使用本文档中修正后的配置参数
