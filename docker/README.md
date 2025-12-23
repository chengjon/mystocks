# MyStocks Docker Compose 配置

本目录包含 MyStocks 监控基础设施的 Docker Compose 配置文件。

## 📁 文件结构

```
docker/
├── README.md                    # 本文件
├── prometheus.yml              # Prometheus 独立配置
├── grafana.yml                 # Grafana 独立配置
├── mongodb.yml                 # MongoDB 独立配置
├── monitoring-stack.yml        # 完整监控栈配置
├── docker-compose.yml          # 主项目配置（链接到上面文件）
└── scripts/
    ├── start-all.sh           # 启动所有服务
    ├── stop-all.sh            # 停止所有服务
    └── backup-data.sh         # 备份数据卷
```

## 🚀 快速启动

### 1. 环境准备
```bash
# 复制环境变量配置
cp ../.env.example .env

# 编辑配置文件（根据需要修改密码和端口）
vim .env
```

### 2. 启动选项

#### 选项 A: 启动完整监控栈（推荐）
```bash
docker-compose -f monitoring-stack.yml --env-file .env up -d
```

#### 选项 B: 单独启动服务
```bash
# 启动 Prometheus
docker-compose -f prometheus.yml --env-file .env up -d

# 启动 Grafana
docker-compose -f grafana.yml --env-file .env up -d

# 启动 MongoDB
docker-compose -f mongodb.yml --env-file .env up -d
```

#### 选项 C: 使用脚本
```bash
# 启动所有服务
./scripts/start-all.sh

# 停止所有服务
./scripts/stop-all.sh
```

## 🔗 服务访问地址

| 服务 | 地址 | 用户名 | 密码 |
|------|------|--------|------|
| Prometheus | http://localhost:9090 | - | - |
| Grafana | http://localhost:3000 | admin | mystocks2025 |
| MongoDB | localhost:27018 | admin | mystocks2025 |
| AlertManager | http://localhost:9093 | - | - |

## 📊 配置说明

### 环境变量配置 (.env)

```bash
# Prometheus
PROMETHEUS_PORT=9090
PROMETHEUS_CONFIG_PATH=./config/prometheus/prometheus.yml
PROMETHEUS_ALERTS_PATH=./config/alerts
PROMETHEUS_RETENTION=200h

# Grafana
GRAFANA_PORT=3000
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=mystocks2025

# MongoDB
MONGODB_PORT=27018
MONGODB_ROOT_USERNAME=admin
MONGODB_ROOT_PASSWORD=mystocks2025
MONGODB_DATABASE=mystocks

# 网络配置
DOCKER_NETWORK_SUBNET=172.20.0.0/16
```

### 数据持久化

所有服务都配置了数据卷持久化：
- `prometheus_data`: Prometheus 时间序列数据
- `grafana_data`: Grafana 仪表板和配置
- `mongodb_data`: MongoDB 数据库文件
- `alertmanager_data`: AlertManager 配置

## 🔧 维护操作

### 查看服务状态
```bash
docker-compose -f monitoring-stack.yml ps
```

### 查看日志
```bash
# 查看所有服务日志
docker-compose -f monitoring-stack.yml logs

# 查看特定服务日志
docker-compose -f monitoring-stack.yml logs prometheus
docker-compose -f monitoring-stack.yml logs grafana
```

### 重启服务
```bash
# 重启所有服务
docker-compose -f monitoring-stack.yml restart

# 重启特定服务
docker-compose -f monitoring-stack.yml restart prometheus
```

### 更新配置
```bash
# 重新加载 Prometheus 配置
curl -X POST http://localhost:9090/-/reload

# 重启服务应用新配置
docker-compose -f monitoring-stack.yml up -d --force-recreate
```

## 🛠 故障排除

### 端口冲突
如果端口被占用，修改 `.env` 文件中的端口配置：
```bash
PROMETHEUS_PORT=9091  # 改为其他端口
GRAFANA_PORT=3001     # 改为其他端口
```

### 权限问题
```bash
# 确保配置文件权限正确
chmod 644 config/prometheus/prometheus.yml
chmod -R 644 config/alerts/
```

### 网络问题
如果容器间网络不通，重新创建网络：
```bash
docker network rm mystocks-network
docker-compose -f monitoring-stack.yml up -d
```

## 📁 目录映射

| 容器内路径 | 宿主机路径 | 说明 |
|-------------|-------------|------|
| `/etc/prometheus/prometheus.yml` | `./config/prometheus/prometheus.yml` | Prometheus 配置 |
| `/etc/prometheus/alerts/` | `./config/alerts/` | 告警规则 |
| `/var/lib/grafana/` | `grafana_data` | Grafana 数据 |
| `/data/db/` | `mongodb_data` | MongoDB 数据 |
| `/etc/grafana/provisioning/` | `./data/grafana/provisioning/` | Grafana 自动配置 |

## 🔄 备份与恢复

### 备份数据
```bash
# 备份所有数据卷
./scripts/backup-data.sh

# 手动备份特定数据
docker run --rm -v mystocks-mongodb_data:/data -v $(pwd):/backup alpine tar czf /backup/mongodb-backup.tar.gz -C /data .
```

### 恢复数据
```bash
# 恢复 MongoDB 数据
docker run --rm -v mystocks-mongodb_data:/data -v $(pwd):/backup alpine tar xzf /backup/mongodb-backup.tar.gz -C /data
```

## 📈 监控指标

服务启动后，可以通过以下端点访问监控指标：

- **MyStocks 后端指标**: http://localhost:8000/metrics
- **Prometheus 目标状态**: http://localhost:9090/targets
- **Grafana 仪表板**: http://localhost:3000

## 🔒 安全建议

1. **修改默认密码**: 生产环境中请修改 `.env` 文件中的默认密码
2. **网络安全**: 考虑使用反向代理和 HTTPS
3. **访问控制**: 配置防火墙规则限制端口访问
4. **定期备份**: 设置自动备份策略
5. **监控告警**: 配置告警规则监控系统状态