#  iccc数据库 MongoDB 数据库配置
MongoDB IP: localhost:27017
USERNAME=mongo
DBNAME = iccc
PASSWORD=c790414J



# MongoDB 数据库配置
MongoDB IP: localhost:27017
USERNAME=mongo
PASSWORD=c790414J



# 监控数据库配置（MySQL）

MONITOR_DB_URL=mysql+pymysql://root:c790414J@192.168.123.104:3306/db_monitor

MONITOR_DB_HOST=192.168.123.104

MONITOR_DB_USER=root

MONITOR_DB_PASSWORD=c790414J

MONITOR_DB_PORT=3306

MONITOR_DB_DATABASE=db_monitor


 

# TDengine 连接参数(这个taosdata是正确密码）

TDENGINE_HOST=192.168.123.104

TDENGINE_USER=root

TDENGINE_PASSWORD=taosdata

TDENGINE_PORT=6030

TDENGINE_REST_PORT=6041

TDENGINE_DATABASE=market_data


 

# PostgreSQL 连接参数 (TimescaleDB)

POSTGRESQL_HOST=192.168.123.104

POSTGRESQL_USER=postgres

POSTGRESQL_PASSWORD=c790414J

POSTGRESQL_PORT=5438

POSTGRESQL_DATABASE=mystocks


 

# Redis 连接参数

REDIS_HOST=192.168.123.104

REDIS_PORT=6379

REDIS_PASSWORD=

REDIS_DB=1


 

# MySQL 连接参数

MYSQL_HOST=192.168.123.104

MYSQL_USER=root

MYSQL_PASSWORD=c790414J

MYSQL_PORT=3306

MYSQL_DATABASE=quant_research


 

# MariaDB 连接参数

MARIADB_HOST=192.168.123.104

MARIADB_USER=root

MARIADB_PASSWORD=c790414J

MARIADB_PORT=3307

MARIADB_DATABASE=quant_research


 

# 实时市场数据配置

MARKET_SYMBOL=hs

SAVE_AS_REALTIME=true

SAVE_AS_TICK=false

CACHE_EXPIRE_SECONDS=300

REDIS_FIXATION_INTERVAL_SECONDS=300

ADD_TIMESTAMP_COLUMN=true

ENABLE_DATA_VALIDATION=true

MAX_RETRY_ATTEMPTS=3

LOG_LEVEL=INFO



Grafana Configuration (可视化监控专用)

GRAFANA_HOST=192.168.123.104
GRAFANA_PORT=3000
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=mystocks2025
GRAFANA_ROOT_URL=http://192.168.123.104:3000
GRAFANA_DOMAIN=192.168.123.104
GRAFANA_ALLOW_SIGN_UP=false
GRAFANA_ANONYMOUS_ENABLED=false
GRAFANA_TIMEZONE=Asia/Shanghai
GRAFANA_LOG_LEVEL=info
GRAFANA_NETWORK=mystocks-monitoring
GRAFANA_DATA_VOLUME=/volume5/docker5/Grafana
GRAFANA_CONTAINER_NAME=mystocks-grafana



# MyStocks 监控栈环境变量配置

# 更新日期: 2025-12-24


 

# ==================== Grafana 配置 ====================

GRAFANA_HOST=192.168.123.104

GRAFANA_PORT=3000

GRAFANA_ADMIN_USER=admin

GRAFANA_ADMIN_PASSWORD=mystocks2025

GRAFANA_ROOT_URL=http://192.168.123.104:3000

GRAFANA_DOMAIN=192.168.123.104

GRAFANA_ALLOW_SIGN_UP=false

GRAFANA_ANONYMOUS_ENABLED=false

GRAFANA_TIMEZONE=Asia/Shanghai

GRAFANA_LOG_LEVEL=info

GRAFANA_NETWORK=mystocks-monitoring

GRAFANA_DATA_VOLUME=/volume5/docker5/Grafana

GRAFANA_CONTAINER_NAME=mystocks-grafana


 

# ==================== Prometheus 配置 ====================

PROMETHEUS_HOST=192.168.123.104

PROMETHEUS_PORT=9090

PROMETHEUS_DATA_VOLUME=./data/prometheus

PROMETHEUS_CONTAINER_NAME=mystocks-prometheus

PROMETHEUS_RETENTION=30d


 

# ==================== AlertManager 配置 ====================

ALERTMANAGER_HOST=192.168.123.104

ALERTMANAGER_PORT=9093

ALERTMANAGER_DATA_VOLUME=/volume5/docker5/AlertManager

ALERTMANAGER_CONTAINER_NAME=mystocks-alertmanager


 

# ==================== Node Exporter 配置 ====================

NODE_EXPORTER_PORT=9100

NODE_EXPORTER_CONTAINER_NAME=mystocks-node-exporter


 

# ==================== MyStocks 后端配置 ====================

MYSTOCKS_BACKEND_HOST=192.168.123.104

MYSTOCKS_BACKEND_PORT=8000


 

# ==================== Docker 网络配置 ====================

COMPOSE_PROJECT_NAME=mystocks-monitoring

NETWORK_NAME=mystocks-monitoring

GRAFANA_DATA_VOLUME=./data/grafana

# MyStocks 监控栈环境变量配置
# 用于配置 Prometheus, Grafana, Loki, Tempo 等监控组件
# ==================== 容器名称配置 ====================
PROMETHEUS_CONTAINER_NAME=mystocks-prometheus
GRAFANA_CONTAINER_NAME=mystocks-grafana
LOKI_CONTAINER_NAME=mystocks-loki
TEMPO_CONTAINER_NAME=mystocks-tempo
NODE_EXPORTER_CONTAINER_NAME=mystocks-node-exporter
# ==================== 端口配置 ====================
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
LOKI_PORT=3100
LOKI_GRPC_PORT=9096
TEMPO_PORT=3200
TEMPO_OTLP_GRPC_PORT=4317
TEMPO_OTLP_HTTP_PORT=4318
NODE_EXPORTER_PORT=9100
# ==================== Grafana 配置 ====================
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin
GRAFANA_ALLOW_SIGN_UP=false
GRAFANA_ROOT_URL=http://localhost:3000
GRAFANA_DOMAIN=localhost
GRAFANA_LOG_LEVEL=info
# ==================== 数据保留配置 ====================
PROMETHEUS_RETENTION=30d
# ==================== 数据卷配置 ====================
PROMETHEUS_DATA_VOLUME=/data/docker/prometheus
GRAFANA_DATA_VOLUME=/data/docker/grafana
LOKI_DATA_VOLUME=/data/docker/loki
TEMPO_DATA_VOLUME=/data/docker/tempo
# ==================== OpenTelemetry 追踪配置 ====================
# 采样率配置 (10% 采样率，生产环境推荐)
OTEL_TRACES_SAMPLER=parentbased_traceidratio
OTEL_TRACES_SAMPLER_ARG=0.1
# 服务名称
OTEL_SERVICE_NAME=mystocks-backend
OTEL_SERVICE_VERSION=1.0.0
# 追踪导出配置
OTEL_EXPORTER_OTLP_ENDPOINT=http://tempo:4317
OTEL_EXPORTER_OTLP_INSECURE=true
# ==================== 性能优化配置 ====================
# Prometheus 抓取间隔
PROMETHEUS_SCRAPE_INTERVAL=15s
PROMETHEUS_EVALUATION_INTERVAL=15s
# Tempo 存储配置
TEMPO_STORAGE_BACKEND=local
TEMPO_RETENTION_PERIOD=24h
# ==================== 安全配置 ====================
# 注意: 生产环境请使用强密码和HTTPS
GRAFANA_SECURITY_ENCRYPTION_KEY=your-secret-key-here
PROMETHEUS_WEB_CONFIG_FILE=

