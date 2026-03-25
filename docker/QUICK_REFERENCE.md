# MyStocks Docker 配置快速参考

> 当前 canonical 路径为根级 `docker/`。`config/docker/` 与 `config/docker-infra/` 为兼容层。

## 🚀 一键启动

```bash
# 启动所有服务
cd /opt/claude/mystocks_spec/docker
./scripts/start-all.sh

# 停止所有服务
./scripts/stop-all.sh
```

## 🔗 服务访问

| 服务 | 地址 | 认证 | 说明 |
|------|------|------|------|
| Prometheus | http://localhost:9090 | 无 | 指标收集和查询 |
| Grafana | http://localhost:3000 | admin/mystocks2025 | 可视化仪表板 |
| Redis | localhost:6379 | password via `.env` | app_cache=1 / monitoring=0 |
| MongoDB | localhost:27017 | admin/mystocks2025 | 文档数据库 |
| AlertManager | http://localhost:9093 | 无 | 告警管理 |

## 📁 关键文件

| 路径 | 说明 |
|------|------|
| `docker/prometheus.yml` | Prometheus 独立配置 |
| `docker/grafana.yml` | Grafana 独立配置 |
| `docker/docker-compose.prod.yml` | Redis 生产配置 |
| `docker/mongodb.yml` | MongoDB 独立配置 |
| `docker/monitoring-stack.yml` | 完整监控栈配置 |
| `.env` | 环境变量配置 |
| `config/alerts/mystocks-alerts.yml` | 告警规则配置 |

## 🛠 常用命令

```bash
# 查看服务状态
docker-compose -f docker/monitoring-stack.yml ps

# 查看日志
docker-compose -f docker/monitoring-stack.yml logs [service_name]

# 重启服务
docker-compose -f docker/monitoring-stack.yml restart [service_name]

# 重新加载 Prometheus 配置
curl -X POST http://localhost:9090/-/reload

# 进入容器
docker exec -it mystocks-prometheus sh
docker exec -it mystocks-grafana bash
docker exec -it mystocks-redis redis-cli
docker exec -it mystocks-mongodb mongosh
```

## 🔧 环境变量配置 (.env)

```bash
# 核心端口配置
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
REDIS_PORT=6379
REDIS_APP_CACHE_DB=1
REDIS_CELERY_BROKER_DB=0
MONGODB_PORT=27017
MONGODB_AUTH_SOURCE=admin
ALERTMANAGER_PORT=9093

# 认证信息
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=mystocks2025
REDIS_PASSWORD=change_me
MONGODB_ROOT_USERNAME=admin
MONGODB_ROOT_PASSWORD=mystocks2025
BYAPI_KEY=your_active_byapi_key
BYAPI_BASE_URL=https://api.biyingapi.com
TUSHARE_TOKEN=your_tushare_token

# 数据持久化路径
PROMETHEUS_DATA_PATH=./data/prometheus
GRAFANA_DATA_PATH=./data/grafana
MONGODB_DATA_PATH=./data/mongodb
```

初始化本地数据源凭据文件：

```bash
cp docker/data-source-credentials.env.example .env.data-sources.local
vim .env.data-sources.local
```

数据源凭据约束：

- `BYAPI_KEY` 和 `TUSHARE_TOKEN` 只从本地 env / secrets 注入。
- 不提交真实凭据到 Git。

## 📊 监控指标

### MyStocks 后端指标 (37个)
- HTTP 请求计数和延迟
- WebSocket 连接数
- 交易信号生成和准确度
- 系统资源使用情况
- 数据库查询性能

### 访问方式
```bash
# 后端指标端点
curl http://localhost:8000/metrics

# Prometheus 查询
curl http://localhost:9090/api/v1/query?query=up

# Grafana 数据源配置
http://prometheus:9090  (容器内)
http://localhost:9090   (宿主机)
```

## 🔍 故障排除

### 端口冲突
```bash
# 修改 .env 文件中的端口
PROMETHEUS_PORT=9091
GRAFANA_PORT=3001
```

### 网络问题
```bash
# 重建网络
docker network rm mystocks-network
./scripts/start-all.sh
```

### 权限问题
```bash
# 修复配置文件权限
chmod 644 config/prometheus/prometheus.yml
chmod -R 644 config/alerts/
```

### 数据卷问题
```bash
# 查看数据卷
docker volume ls | grep mystocks

# 删除数据卷（谨慎操作）
docker volume rm mystocks-prometheus_data
```

## 📈 监控仪表板

### 预配置的 Grafana 仪表板
- **交易信号监控**: 信号准确度、成功率、生成速率
- **系统性能**: HTTP 请求、数据库连接、内存使用
- **业务指标**: 股票数据更新、策略执行状态

### 导入自定义仪表板
```bash
# 复制仪表板 JSON 文件到配置目录
cp your-dashboard.json data/grafana/dashboards/

# 重启 Grafana 以加载新仪表板
docker restart mystocks-grafana
```

## 🔔 告警配置

### 告警规则位置
- `config/alerts/mystocks-alerts.yml`

### 主要告警规则
- 交易信号准确度低 (< 60%)
- HTTP 错误率高 (> 5%)
- 数据库连接失败
- 系统资源使用过高

### 告警通知
- 配置文件: `config/alertmanager/alertmanager.yml`
- 支持邮件、Webhook、Slack 等通知方式

## 📝 日志管理

```bash
# 查看所有服务日志
docker-compose -f docker/monitoring-stack.yml logs

# 查看特定服务日志
docker logs mystocks-prometheus
docker logs mystocks-grafana
docker logs mystocks-mongodb

# 实时跟踪日志
docker logs -f mystocks-prometheus
```

## 🔄 备份恢复

```bash
# 备份数据卷（示例：MongoDB）
docker run --rm \
  -v mystocks-mongodb_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/mongodb-backup-$(date +%Y%m%d).tar.gz -C /data .

# 恢复数据卷
docker run --rm \
  -v mystocks-mongodb_data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/mongodb-backup-20241219.tar.gz -C /data
```

## 🎯 性能优化建议

1. **Prometheus**: 调整 `--storage.tsdb.retention.time` 限制数据保留时间
2. **MongoDB**: 配置适当的 WiredTiger 缓存大小
3. **Grafana**: 定期清理不用的仪表板和数据源
4. **网络**: 使用自定义 Docker 网络提高容器间通信效率

## 📚 相关文档

- [Prometheus 官方文档](https://prometheus.io/docs/)
- [Grafana 官方文档](https://grafana.com/docs/)
- [Docker Compose 参考](https://docs.docker.com/compose/)
- [MyStocks 项目文档](../docs/)
## Redis 运行时检查

```bash
scripts/dev/check_redis_runtime_health.sh
```
