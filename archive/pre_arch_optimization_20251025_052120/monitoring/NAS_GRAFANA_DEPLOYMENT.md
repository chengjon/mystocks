# Grafana在NAS中的部署指南

**目标NAS**: 群晖/威联通/其他NAS系统
**部署方式**: Docker容器
**部署时间**: 约15分钟
**创建日期**: 2025-10-12

---

## 📋 前置条件

- ✅ NAS支持Docker (Container Station / Docker套件)
- ✅ NAS可访问互联网 (下载镜像)
- ✅ PostgreSQL监控数据库已部署 (192.168.123.104:5438)
- ✅ 至少500MB可用空间

---

## 🚀 快速部署步骤

### 步骤1: 在NAS上创建目录结构

```bash
# SSH登录NAS
ssh admin@192.168.123.104

# 创建Grafana目录
mkdir -p /volume1/docker/mystocks-grafana/{data,config}
cd /volume1/docker/mystocks-grafana

# 创建配置目录
mkdir -p config/provisioning/{datasources,dashboards}
```

### 步骤2: 上传配置文件到NAS

将以下文件从开发机上传到NAS:

```bash
# 在开发机上执行 (从项目根目录)
cd /mnt/wd_mycode/mystocks_spec/monitoring

# 上传配置文件到NAS
scp grafana-datasource.yml admin@192.168.123.104:/volume1/docker/mystocks-grafana/config/provisioning/datasources/
scp grafana-dashboard-provider.yml admin@192.168.123.104:/volume1/docker/mystocks-grafana/config/provisioning/dashboards/
scp grafana_dashboard.json admin@192.168.123.104:/volume1/docker/mystocks-grafana/config/provisioning/dashboards/
scp docker-compose-grafana.yml admin@192.168.123.104:/volume1/docker/mystocks-grafana/docker-compose.yml
```

**或者使用NAS文件管理器**: 手动上传这4个文件

### 步骤3: 启动Grafana容器

#### 方法A: 使用Docker Compose (推荐)

```bash
# SSH到NAS
cd /volume1/docker/mystocks-grafana

# 启动容器
docker-compose up -d

# 查看日志
docker-compose logs -f grafana
```

#### 方法B: 使用Docker命令

```bash
docker run -d \
  --name mystocks-grafana \
  --restart unless-stopped \
  -p 3000:3000 \
  -v /volume1/docker/mystocks-grafana/data:/var/lib/grafana \
  -v /volume1/docker/mystocks-grafana/config/provisioning:/etc/grafana/provisioning \
  -e GF_SECURITY_ADMIN_USER=admin \
  -e GF_SECURITY_ADMIN_PASSWORD=mystocks2025 \
  -e GF_SERVER_ROOT_URL=http://192.168.123.104:3000 \
  -e GF_USERS_ALLOW_SIGN_UP=false \
  -e TZ=Asia/Shanghai \
  grafana/grafana:latest
```

#### 方法C: 使用NAS GUI (群晖/威联通)

**群晖 Container Manager**:
1. 打开 Container Manager
2. 点击"注册表" → 搜索"grafana"
3. 下载 grafana/grafana:latest
4. 创建容器:
   - 容器名称: mystocks-grafana
   - 端口设置: 本地端口 3000 → 容器端口 3000
   - 卷挂载:
     - `/volume1/docker/mystocks-grafana/data` → `/var/lib/grafana`
     - `/volume1/docker/mystocks-grafana/config/provisioning` → `/etc/grafana/provisioning`
   - 环境变量:
     ```
     GF_SECURITY_ADMIN_USER=admin
     GF_SECURITY_ADMIN_PASSWORD=mystocks2025
     GF_SERVER_ROOT_URL=http://192.168.123.104:3000
     GF_USERS_ALLOW_SIGN_UP=false
     TZ=Asia/Shanghai
     ```
5. 点击"应用"启动容器

**威联通 Container Station**:
1. 打开 Container Station
2. 点击"创建" → "创建容器"
3. 搜索镜像: grafana/grafana
4. 配置容器 (参数同上)
5. 启动容器

---

### 步骤4: 验证部署

```bash
# 检查容器状态
docker ps | grep grafana

# 输出示例:
# a1b2c3d4e5f6   grafana/grafana:latest   "/run.sh"   2 minutes ago   Up 2 minutes   0.0.0.0:3000->3000/tcp   mystocks-grafana

# 检查健康状态
docker exec mystocks-grafana wget -qO- http://localhost:3000/api/health

# 输出示例:
# {"commit":"...","database":"ok","version":"..."}
```

---

### 步骤5: 访问Grafana

**访问地址**: http://192.168.123.104:3000

**登录信息**:
- 用户名: `admin`
- 密码: `mystocks2025`

**首次登录后**:
1. 系统会自动加载数据源 (MyStocks-Monitoring)
2. 自动导入监控面板
3. 验证数据源连接: Configuration → Data Sources → MyStocks-Monitoring → Test

---

## 📊 监控面板说明

部署完成后,您将看到以下面板:

### 1. 系统概览 (第一行)
- 今日操作总数
- 慢查询数量
- 未解决告警
- 平均查询时间

### 2. 性能监控
- 查询时间趋势图 (5分钟聚合)
- 数据库性能对比
- 慢查询Top 10列表

### 3. 数据质量
- 质量检查状态分布 (饼图)
- 质量检查趋势 (按检查类型)

### 4. 告警监控
- 告警级别分布
- 未解决告警列表

### 5. 操作统计
- 操作类型分布
- 操作成功率

---

## 🔧 配置优化

### 1. 设置反向代理 (可选)

如果您的NAS有Web Station或Nginx:

```nginx
# Nginx配置示例
server {
    listen 80;
    server_name grafana.yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. 配置HTTPS (推荐)

```bash
# 使用Let's Encrypt证书
docker run -d \
  --name mystocks-grafana \
  --restart unless-stopped \
  -p 3000:3000 \
  -v /volume1/docker/mystocks-grafana/data:/var/lib/grafana \
  -v /volume1/docker/mystocks-grafana/config/provisioning:/etc/grafana/provisioning \
  -v /volume1/docker/ssl:/etc/grafana/ssl:ro \
  -e GF_SERVER_PROTOCOL=https \
  -e GF_SERVER_CERT_FILE=/etc/grafana/ssl/cert.pem \
  -e GF_SERVER_CERT_KEY=/etc/grafana/ssl/key.pem \
  grafana/grafana:latest
```

### 3. 配置邮件告警

编辑 `/volume1/docker/mystocks-grafana/config/grafana.ini`:

```ini
[smtp]
enabled = true
host = smtp.gmail.com:587
user = your-email@gmail.com
password = your-app-password
from_address = grafana@yourdomain.com
from_name = MyStocks Monitoring

[emails]
welcome_email_on_sign_up = false
```

重启容器使配置生效:
```bash
docker restart mystocks-grafana
```

---

## 🔐 安全配置

### 1. 修改管理员密码

首次登录后立即修改密码:
1. 点击左下角头像
2. Preferences → Change Password
3. 输入新密码并保存

### 2. 创建只读用户

```bash
# 使用Grafana API创建只读用户
curl -X POST http://admin:mystocks2025@192.168.123.104:3000/api/admin/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Viewer",
    "email": "viewer@example.com",
    "login": "viewer",
    "password": "viewer123",
    "role": "Viewer"
  }'
```

### 3. 配置访问控制

编辑 `/volume1/docker/mystocks-grafana/config/grafana.ini`:

```ini
[auth]
disable_login_form = false

[auth.anonymous]
enabled = false

[security]
admin_user = admin
admin_password = $__file{/run/secrets/admin_password}
```

---

## 📱 移动访问

### 方法1: 浏览器访问
- 在手机浏览器输入: http://192.168.123.104:3000
- 登录后可查看所有面板

### 方法2: Grafana官方App
- iOS: https://apps.apple.com/app/grafana/id1475826620
- Android: https://play.google.com/store/apps/details?id=com.grafana.mobile

配置连接:
- Server URL: http://192.168.123.104:3000
- Username: admin
- Password: mystocks2025

---

## 🔄 维护管理

### 备份配置

```bash
# 备份Grafana数据
cd /volume1/docker/mystocks-grafana
tar -czf grafana-backup-$(date +%Y%m%d).tar.gz data/ config/

# 恢复数据
tar -xzf grafana-backup-20251012.tar.gz
docker restart mystocks-grafana
```

### 更新Grafana

```bash
# 停止容器
docker stop mystocks-grafana

# 拉取最新镜像
docker pull grafana/grafana:latest

# 删除旧容器
docker rm mystocks-grafana

# 重新创建容器 (使用原命令)
docker run -d ...

# 或使用docker-compose
docker-compose pull
docker-compose up -d
```

### 查看日志

```bash
# 实时日志
docker logs -f mystocks-grafana

# 最近100行日志
docker logs --tail 100 mystocks-grafana

# 导出日志到文件
docker logs mystocks-grafana > grafana.log 2>&1
```

---

## 🐛 故障排查

### 问题1: 容器启动失败

```bash
# 查看详细错误
docker logs mystocks-grafana

# 常见原因:
# - 端口3000已被占用: 修改为其他端口 -p 3001:3000
# - 权限问题: chmod 777 /volume1/docker/mystocks-grafana/data
# - 配置文件错误: 检查YAML语法
```

### 问题2: 无法连接数据源

```bash
# 测试PostgreSQL连接
docker exec mystocks-grafana nc -zv 192.168.123.104 5438

# 检查防火墙
# 群晖: 控制面板 → 安全性 → 防火墙 → 添加端口5438
# 威联通: 控制面板 → 系统 → 安全 → 防火墙
```

### 问题3: 面板显示"No Data"

```bash
# 检查监控数据库是否有数据
docker exec -it mystocks-grafana psql \
  -h 192.168.123.104 -p 5438 \
  -U postgres -d mystocks_monitoring \
  -c "SELECT COUNT(*) FROM operation_logs;"

# 如果无数据,运行一些操作生成监控数据
cd /mnt/wd_mycode/mystocks_spec
python test_monitoring_with_redis.py
```

### 问题4: 性能慢

```bash
# 增加资源限制
docker update \
  --memory 512m \
  --cpus 1 \
  mystocks-grafana

# 或在docker-compose.yml中配置:
# deploy:
#   resources:
#     limits:
#       memory: 512M
#       cpus: '1'
```

---

## 📊 监控数据生成

为了让监控面板有数据显示,请运行测试程序:

```bash
# 在开发机上运行
cd /mnt/wd_mycode/mystocks_spec

# 生成监控数据
python test_monitoring_with_redis.py

# 或运行完整的系统测试
python -c "
from unified_manager import MyStocksUnifiedManager
from core.data_classification import DataClassification
import pandas as pd

manager = MyStocksUnifiedManager(enable_monitoring=True)

# 模拟多次操作生成监控数据
for i in range(20):
    data = pd.DataFrame({
        'symbol': [f'60000{i}.SH'],
        'position': [1000 + i * 100],
        'cost': [10.0 + i * 0.5]
    })
    manager.save_data_by_classification(
        DataClassification.REALTIME_POSITIONS,
        data,
        table_name=f'test_monitor_{i}'
    )
print('✅ 监控数据生成完成')
"
```

---

## ✅ 部署检查清单

部署完成后,请检查以下项目:

- [ ] Grafana容器运行正常 (`docker ps`)
- [ ] 可以访问 http://192.168.123.104:3000
- [ ] 可以用admin/mystocks2025登录
- [ ] 数据源"MyStocks-Monitoring"连接正常 (绿色勾选)
- [ ] 监控面板已自动导入 (Dashboards → MyStocks)
- [ ] 面板显示数据 (至少有部分数据)
- [ ] 配置文件已备份
- [ ] 已修改默认管理员密码
- [ ] 已创建只读用户 (可选)
- [ ] 邮件告警已配置 (可选)

---

## 📞 技术支持

**遇到问题?**

1. 查看本文档的故障排查部分
2. 检查容器日志: `docker logs mystocks-grafana`
3. 检查PostgreSQL连接
4. 参考Grafana官方文档: https://grafana.com/docs/

---

**部署文档版本**: 1.0.0
**最后更新**: 2025-10-12
**预计部署时间**: 15-30分钟

🎉 **祝部署顺利!**
