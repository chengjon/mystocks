# MyStocks Docker 配置安全指南

> **参考指南说明**:
> 本文件用于提供本地运行、部署配置、安全设置或操作步骤方面的参考信息，帮助理解项目配套环境与使用方式。
> 其中的命令、端口、路径和操作建议应与 `architecture/STANDARDS.md`、当前配置实现及最新验证结果一并核对，不应单独充当共享规则或当前状态的唯一事实来源。


## 🔒 安全配置概览

本指南说明了 MyStocks 监控基础设施的安全配置要求和最佳实践。

## 🚨 关键安全要求

### 1. 密码安全

**必须修改的默认密码**：
- Grafana 管理员密码（默认：`mystocks2025`）
- MongoDB 根密码（默认：`mystocks2025`）

**安全配置步骤**：
```bash
# 1. 复制环境变量模板
cp .env.example .env

# 2. 设置强密码
# 使用以下命令生成安全密码：
openssl rand -base64 16

# 3. 编辑 .env 文件
vim .env

# 4. 修改以下配置：
GRAFANA_ADMIN_PASSWORD=your_generated_secure_password_here
MONGODB_ROOT_PASSWORD=your_generated_secure_password_here
```

### 2. 镜像版本安全

所有 Docker 镜像已固定到具体版本：
- **Prometheus**: `v2.53.0`
- **Grafana**: `11.1.0`
- **MongoDB**: `7.0.5`
- **AlertManager**: `v0.27.0`

**更新检查**：
```bash
# 定期检查新版本和漏洞
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image prom/prometheus:v2.53.0
```

### 3. 网络安全

**自定义网络配置**：
- 网络名称：`mystocks-network`
- 子网：`172.20.0.0/16`
- 容器间通信隔离

**端口暴露**：
| 服务 | 端口 | 访问控制 | 建议 |
|------|------|----------|------|
| Prometheus | 9090 | 内部访问 | 生产环境建议反向代理 |
| Grafana | 3000 | 限制访问 | 配置防火墙规则 |
| MongoDB | 27018 | 仅内部访问 | 避免暴露到公网 |
| AlertManager | 9093 | 内部访问 | 生产环境建议反向代理 |

### 4. 资源限制

**已配置的资源限制**：
```yaml
# Prometheus
cpus: '2.0' (limit), '1.0' (reserved)
memory: 4G (limit), 2G (reserved)

# Grafana
cpus: '1.0' (limit), '0.5' (reserved)
memory: 2G (limit), 1G (reserved)

# MongoDB
cpus: '2.0' (limit), '1.0' (reserved)
memory: 4G (limit), 2G (reserved)
```

## 🔧 生产环境安全配置

### 1. 环境变量配置

**敏感信息处理**：
```bash
# 使用环境变量文件
chmod 600 .env

# 确保 .env 在 .gitignore 中
echo ".env" >> .gitignore
```

**必需的安全环境变量**：
```bash
# 强制要求的安全配置
GRAFANA_ADMIN_PASSWORD=<强密码>
MONGODB_ROOT_PASSWORD=<强密码>
JWT_SECRET_KEY=<随机的32字节密钥>

# 网络安全配置
CORS_ORIGINS=https://your-frontend-domain.com
```

### 2. 防火墙配置

**UFW 规则示例**：
```bash
# 仅允许必要端口
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 80/tcp    # HTTP (重定向到 HTTPS)

# 监控端口限制（可选）
sudo ufw allow from private-network/24 to any port 3000
sudo ufw allow from 10.0.0.0/8 to any port 9090

# 数据库端口（仅内网）
sudo ufw deny 27018
```

### 3. 反向代理配置

**Nginx 示例配置**：
```nginx
# Grafana 反向代理
server {
    listen 443 ssl http2;
    server_name grafana.yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Prometheus 反向代理
server {
    listen 443 ssl http2;
    server_name prometheus.yourdomain.com;

    # 基本认证
    auth_basic "Prometheus";
    auth_basic_user_file /etc/nginx/.htpasswd;

    location / {
        proxy_pass http://localhost:9090;
        proxy_set_header Host $host;
    }
}
```

### 4. 访问控制

**Grafana 用户管理**：
```bash
# 创建只读用户
curl -X POST \
  http://admin:password@localhost:3000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Viewer User",
    "email": "viewer@company.com",
    "login": "viewer",
    "password": "secure_password",
    "OrgId": 1
  }'
```

**MongoDB 用户管理**：
```javascript
// 创建应用用户
use mystocks;
db.createUser({
  user: "app_user",
  pwd: "secure_password",
  roles: [
    { role: "readWrite", db: "mystocks" }
  ]
});
```

## 🛡️ 安全检查清单

### 部署前检查

- [ ] 所有默认密码已更改
- [ ] 环境变量文件权限正确（600）
- [ ] Docker 镜像版本已固定
- [ ] 防火墙规则已配置
- [ ] SSL/TLS 证书已配置
- [ ] 监控告警已启用
- [ ] 备份策略已实施

### 定期安全检查

- [ ] 审查访问日志
- [ ] 检查容器漏洞
- [ ] 更新镜像版本
- [ ] 轮换密码
- [ ] 测试备份恢复

## 🔍 安全监控

### 关键安全指标

在 Grafana 中配置以下安全监控仪表板：

1. **认证失败监控**
   ```promql
   increase(mystocks_auth_failures_total[5m])
   ```

2. **异常访问模式**
   ```promql
   rate(mystocks_http_requests_total{status=~"4..5"}[5m])
   ```

3. **容器安全状态**
   ```promql
   up{job="docker-containers"}
   ```

### 告警规则

```yaml
# 安全告警规则
groups:
  - name: security_alerts
    rules:
      - alert: HighAuthFailureRate
        expr: rate(mystocks_auth_failures_total[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "高认证失败率检测到"

      - alert: ContainerSecurityIssue
        expr: up{job="docker-containers"} == 0
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "容器离线"
```

## 🔐 数据保护

### 加密配置

**传输加密**：
```bash
# MongoDB SSL 连接
MONGODB_URL=mongodb://user:pass@host:port/database?ssl=true&sslMode=require

# Prometheus HTTPS
PROMETHEUS_URL=https://prometheus.yourdomain.com
```

**静态数据加密**：
```yaml
# Docker Compose 卷加密
volumes:
  encrypted_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /path/to/encrypted/mount
```

### 备份安全

```bash
# 加密备份脚本
#!/bin/bash
BACKUP_DIR="/secure/backups"
ENCRYPTION_KEY="/path/to/key"

docker run --rm \
  -v mystocks-mongodb_data:/data \
  -v $BACKUP_DIR:/backup \
  alpine tar czf - -C /data . | \
  gpg --symmetric --cipher-algo AES256 --compress-algo 1 \
  --output $BACKUP_DIR/mongodb-$(date +%Y%m%d).tar.gz.gpg
```

## 🚀 安全启动脚本

```bash
#!/bin/bash
# 安全启动验证脚本

check_security_config() {
    echo "检查安全配置..."

    # 检查密码强度
    if [[ ${#GRAFANA_ADMIN_PASSWORD} -lt 12 ]]; then
        echo "ERROR: Grafana 密码长度不足 12 字符"
        exit 1
    fi

    # 检查环境变量文件权限
    if [[ "$(stat -c %a .env)" != "600" ]]; then
        echo "ERROR: .env 文件权限不安全"
        exit 1
    fi

    # 检查端口暴露
    if netstat -tuln | grep -q ":27018"; then
        echo "WARNING: MongoDB 端口暴露到网络"
    fi

    echo "安全配置检查通过"
}

check_security_config
```

## 📞 安全事件响应

### 检测到安全问题时

1. **立即行动**：
   - 停止受影响的服务
   - 更改所有密码
   - 检查访问日志

2. **调查**：
   - 确定影响范围
   - 收集证据
   - 分析攻击向量

3. **恢复**：
   - 从干净备份恢复
   - 修复安全漏洞
   - 加强监控

## 📚 相关资源

- [Docker 安全最佳实践](https://docs.docker.com/engine/security/)
- [Prometheus 安全配置](https://prometheus.io/docs/prometheus/latest/configuration/ssl/)
- [Grafana 安全指南](https://grafana.com/docs/grafana/latest/setup-grafana/configure-security/)
- [MongoDB 安全](https://docs.mongodb.com/manual/security/)

---

**重要提醒**：安全是一个持续的过程，请定期审查和更新安全配置。
