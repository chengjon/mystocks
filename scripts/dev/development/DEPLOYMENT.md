# MyStocks 监控系统部署指南

## 当前状态

✅ **已部署**:
- Prometheus (http://localhost:9090)
- Grafana (http://localhost:3000)

❌ **待部署**:
- Loki (日志聚合)
- Tempo (分布式追踪)

---

## 部署 Loki 和 Tempo

### 步骤 1: 下载 Docker 镜像

由于网络限制，请使用自定义命令下载镜像：

```bash
# 下载 Loki 镜像
docker_pull_acc grafana/loki:latest

# 下载 Tempo 镜像
docker_pull_acc grafana/tempo:latest
```

**如果 docker_pull_acc 命令不存在，请尝试以下方法：**

#### 方法 A: 使用国内镜像源（需要手动指定）
```bash
# 如果可以使用阿里云镜像加速器
# 已配置在 /etc/docker/daemon.json 中
systemctl restart docker
docker pull registry.cn-hangzhou.aliyuncs.com/grafana/loki:latest
docker tag registry.cn-hangzhou.aliyuncs.com/grafana/loki:latest grafana/loki:latest
```

#### 方法 B: 离线导入（如果有镜像文件）
```bash
docker load < loki-latest.tar
docker load < tempo-latest.tar
```

### 步骤 2: 验证镜像已下载

```bash
docker images | grep -E "(loki|tempo)"
```

应该看到：
```
grafana/loki        latest    xxxxx
grafana/tempo       latest    xxxxx
```

### 步骤 3: 运行部署脚本

```bash
cd /opt/claude/mystocks_phase6_monitoring/monitoring-stack
./deploy-loki-tempo.sh
```

### 步骤 4: 验证服务运行

```bash
# 检查容器状态
docker ps | grep -E "(mystocks-loki|mystocks-tempo)"

# 测试服务端点
curl http://localhost:3100/ready
curl http://localhost:3200/ready

# 查看日志（如果有问题）
docker logs mystocks-loki --tail 50
docker logs mystocks-tempo --tail 50
```

---

## 配置 Grafana 数据源

### 访问 Grafana

URL: http://localhost:3000
用户名: admin
密码: admin

### 添加 Loki 数据源

1. 登录后，点击左侧菜单 **Configuration** → **Data Sources**
2. 点击 **Add data source**
3. 选择 **Loki**
4. 配置如下：
   - **Name**: Loki
   - **URL**: `http://mystocks-loki:3100` (或 `http://host.docker.internal:3100`)
5. 点击 **Save & Test**
6. 应该看到 "Data source is working"

### 添加 Tempo 数据源

1. 点击左侧菜单 **Configuration** → **Data Sources**
2. 点击 **Add data source**
3. 选择 **Tempo**
4. 配置如下：
   - **Name**: Tempo
   - **URL**: `http://mystocks-tempo:3200` (或 `http://host.docker.internal:3200`)
5. 点击 **Save & Test**
6. 应该看到 "Data source is working"

---

## 监控系统访问地址汇总

| 服务     | 地址                      | 用途                 |
|----------|---------------------------|----------------------|
| Prometheus | http://localhost:9090     | 指标存储和查询       |
| Grafana    | http://localhost:3000     | 可视化仪表板         |
| Loki       | http://localhost:3100     | 日志聚合 API         |
| Tempo      | http://localhost:3200     | 追踪数据 API         |

---

## 验证完整监控链路

### 1. 生成测试数据

```bash
# 触发一些 API 请求
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/market/symbols
curl http://localhost:8000/api/system/health
```

### 2. 在 Prometheus 中查询指标

访问 http://localhost:9090，执行查询：
```
up{job="mystocks-backend"}
rate(http_request_duration_seconds_sum[5m])
```

### 3. 在 Grafana Loki 中查询日志

访问 http://localhost:3000 → Explore → 选择 Loki
查询示例：
```
{job="mystocks_backend", level="INFO"}
```

### 4. 在 Grafana Tempo 中查看追踪

访问 http://localhost:3000 → Explore → 选择 Tempo
点击 "Search Traces" 查看追踪链路

---

## 故障排查

### 问题 1: docker_pull_acc 命令不存在

**解决**:
检查是否有其他下载脚本或镜像仓库配置：
```bash
# 查找相关脚本
find ~ -name "*docker*" -type f 2>/dev/null

# 检查是否有其他镜像
docker images | grep grafana
```

### 问题 2: 容器启动失败

**解决**:
```bash
# 查看容器日志
docker logs mystocks-loki
docker logs mystocks-tempo

# 检查端口占用
netstat -tulpn | grep -E "(3100|3200)"
```

### 问题 3: Grafana 无法连接数据源

**解决**:
- 检查容器是否在同一网络：`docker inspect mystocks-grafana | grep Networks`
- 尝试使用 `host.docker.internal` 代替容器名
- 确保服务正在运行：`docker ps`

### 问题 4: 配置文件路径错误

**解决**:
```bash
# 检查配置文件是否存在
ls -la /opt/claude/mystocks_phase6_monitoring/monitoring-stack/config/

# 确保配置文件已挂载到容器
docker inspect mystocks-loki | grep -A 5 Mounts
```

---

## 生产环境建议

### 安全配置

1. **修改 Grafana 默认密码**:
   ```bash
   # 在 Grafana UI 中修改 admin 密码
   ```

2. **限制外部访问**:
   ```yaml
   # 修改 docker-compose，只绑定本地网络
   ports:
     - "127.0.0.1:9090:9090"
     - "127.0.0.1:3000:3000"
   ```

3. **启用 HTTPS**:
   ```bash
   # 使用 Nginx 反向代理并配置 SSL 证书
   ```

### 数据持久化

确保数据目录已正确挂载：
```bash
# 检查数据目录
ls -la /opt/claude/mystocks_phase6_monitoring/monitoring-stack/data/

# 设置定期备份
crontab -e
# 添加: 0 2 * * * tar -czf /backup/mystocks-monitoring-$(date +\%Y\%m\%d).tar.gz /opt/claude/mystocks_phase6_monitoring/monitoring-stack/data/
```

### 性能优化

1. **调整 Prometheus 保留时间**:
   ```yaml
   # prometheus.yml
   storage.tsdb.retention.time=30d
   ```

2. **优化 Loki 配置**:
   ```yaml
   # loki-config.yaml
   limits_config:
     max_streams_match_per_query: 1000
   ```

3. **配置告警**:
   ```bash
   # 在 Prometheus 中配置告警规则
   # 在 AlertManager 中配置通知渠道
   ```

---

## 下一步

完成部署后，可以：
1. 创建自定义 Grafana Dashboard
2. 配置告警规则和通知渠道
3. 设置自动数据备份
4. 集成更多监控指标

查看相关文档：
- Prometheus 配置: `config/monitoring/prometheus.yml`
- Loki 配置: `config/monitoring/loki-config.yaml`
- Tempo 配置: `config/monitoring/tempo-config.yaml`
- 告警规则: `config/monitoring/alerting.yaml`
