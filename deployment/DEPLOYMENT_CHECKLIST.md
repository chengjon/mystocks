# MyStocks 生产环境部署清单

**版本**: 1.0.0
**更新日期**: 2025-10-25
**架构**: 双数据库 (TDengine + PostgreSQL)

---

## 📋 部署前检查清单

在开始部署之前，请确保完成以下所有检查项：

### 1. 环境准备 ✓

#### 硬件要求

- [ ] **服务器配置**
  - [ ] CPU: 4核心或以上
  - [ ] 内存: 8GB或以上（推荐16GB）
  - [ ] 磁盘: 100GB以上可用空间
  - [ ] 网络: 100Mbps或以上

- [ ] **操作系统**
  - [ ] Linux (Ubuntu 20.04+, CentOS 8+, Debian 10+)
  - [ ] 或 macOS 12+
  - [ ] 或 Windows Server 2019+（不推荐）

#### 软件依赖

- [ ] **Python环境**
  - [ ] Python 3.11+ 已安装
  - [ ] pip 已安装并更新到最新版本
  - [ ] venv 或 virtualenv 已安装

- [ ] **数据库**
  - [ ] PostgreSQL 14+ 已安装并运行
  - [ ] TDengine 3.0+ 已安装并运行
  - [ ] 数据库管理工具已安装（psql, taos）

- [ ] **系统工具**
  - [ ] Git 已安装
  - [ ] curl/wget 已安装
  - [ ] systemd 已配置（Linux）
  - [ ] 防火墙已配置

### 2. 网络和端口 ✓

- [ ] **防火墙规则**
  - [ ] 8000端口开放（API服务）
  - [ ] 5432端口开放（PostgreSQL，内网）
  - [ ] 6030端口开放（TDengine，内网）

- [ ] **域名和DNS**
  - [ ] 域名已注册（可选）
  - [ ] DNS A记录已配置
  - [ ] SSL证书已准备（生产必需）

- [ ] **负载均衡**
  - [ ] Nginx/HAProxy已配置（可选）
  - [ ] SSL终止已配置
  - [ ] 健康检查已配置

### 3. 数据库准备 ✓

#### PostgreSQL

- [ ] **数据库创建**
  - [ ] mystocks数据库已创建
  - [ ] 用户权限已配置
  - [ ] 连接池已配置

- [ ] **扩展安装**
  - [ ] TimescaleDB扩展已安装（可选）
  - [ ] pg_stat_statements已启用

- [ ] **备份配置**
  - [ ] 自动备份已配置
  - [ ] 备份策略已确定
  - [ ] 恢复测试已完成

#### TDengine

- [ ] **数据库创建**
  - [ ] market_data数据库已创建
  - [ ] 用户权限已配置
  - [ ] 超表已创建

- [ ] **配置优化**
  - [ ] 内存配置已优化
  - [ ] 缓存配置已调整
  - [ ] 日志级别已设置

- [ ] **监控配置**
  - [ ] 监控数据库已创建
  - [ ] 监控表已初始化
  - [ ] Grafana数据源已配置

### 4. 应用配置 ✓

- [ ] **环境变量**
  - [ ] .env文件已创建
  - [ ] 所有必需变量已配置
  - [ ] 敏感信息已加密存储
  - [ ] 环境变量已验证

- [ ] **依赖安装**
  - [ ] requirements.txt所有包已安装
  - [ ] 版本冲突已解决
  - [ ] 虚拟环境已激活

- [ ] **配置文件**
  - [ ] config.yaml已配置
  - [ ] 日志级别已设置为INFO或WARNING
  - [ ] 缓存配置已优化
  - [ ] CORS设置已确认

### 5. 安全配置 ✓

- [ ] **认证和授权**
  - [ ] JWT密钥已生成（强密码）
  - [ ] Token过期时间已配置
  - [ ] 默认管理员密码已修改

- [ ] **网络安全**
  - [ ] 仅必要端口开放
  - [ ] 数据库不暴露到公网
  - [ ] SSH密钥认证已启用
  - [ ] fail2ban已配置（可选）

- [ ] **数据安全**
  - [ ] 数据库连接使用SSL（推荐）
  - [ ] 敏感数据已加密
  - [ ] 备份数据已加密
  - [ ] 访问日志已启用

### 6. 监控和日志 ✓

- [ ] **日志配置**
  - [ ] 日志目录已创建
  - [ ] 日志轮转已配置
  - [ ] 日志级别已设置
  - [ ] 错误日志告警已配置

- [ ] **监控系统**
  - [ ] Grafana已安装并配置
  - [ ] Prometheus已安装（可选）
  - [ ] 监控数据库已初始化
  - [ ] 告警规则已配置

- [ ] **健康检查**
  - [ ] /health端点已验证
  - [ ] /api/system/health已验证
  - [ ] 数据库健康检查已验证
  - [ ] 适配器健康检查已验证

### 7. 测试和验证 ✓

- [ ] **单元测试**
  - [ ] pytest测试套件已通过
  - [ ] 覆盖率达到80%以上

- [ ] **集成测试**
  - [ ] API端点测试已通过
  - [ ] 数据库连接测试已通过
  - [ ] 缓存功能测试已通过

- [ ] **性能测试**
  - [ ] 负载测试已完成
  - [ ] 响应时间符合要求
  - [ ] 并发能力验证通过

- [ ] **安全测试**
  - [ ] SQL注入测试已通过
  - [ ] XSS测试已通过
  - [ ] 认证测试已通过

### 8. 文档准备 ✓

- [ ] **部署文档**
  - [ ] 部署步骤文档已准备
  - [ ] 配置说明已完整
  - [ ] 故障排查指南已准备

- [ ] **运维文档**
  - [ ] 备份恢复流程已文档化
  - [ ] 扩容方案已准备
  - [ ] 应急预案已制定

- [ ] **API文档**
  - [ ] API文档已更新
  - [ ] OpenAPI规范已生成
  - [ ] 示例代码已验证

---

## 🚀 部署步骤

### 步骤1: 环境准备

```bash
# 1.1 创建部署用户
sudo useradd -m -s /bin/bash mystocks
sudo usermod -aG sudo mystocks

# 1.2 创建应用目录
sudo mkdir -p /opt/mystocks
sudo chown mystocks:mystocks /opt/mystocks

# 1.3 切换到部署用户
sudo su - mystocks
```

### 步骤2: 代码部署

```bash
# 2.1 克隆代码（或上传压缩包）
cd /opt/mystocks
git clone https://github.com/your-org/mystocks.git .

# 2.2 切换到生产分支
git checkout main

# 2.3 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 2.4 安装依赖
pip install --upgrade pip
pip install -r requirements.txt
```

### 步骤3: 配置文件

```bash
# 3.1 复制环境变量模板
cp deployment/production.env.template .env

# 3.2 编辑环境变量
nano .env

# 3.3 验证配置
python deployment/verify_config.py
```

### 步骤4: 数据库初始化

```bash
# 4.1 初始化PostgreSQL
export $(cat .env | xargs)
python deployment/init_postgresql.py

# 4.2 初始化TDengine
python deployment/init_tdengine.py

# 4.3 初始化监控数据库
psql -h $POSTGRESQL_HOST -U $POSTGRESQL_USER -d mystocks -f monitoring/init_us3_monitoring.sql

# 4.4 验证数据库
python deployment/verify_database.py
```

### 步骤5: 应用启动

```bash
# 5.1 测试启动（前台）
cd /opt/mystocks
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 5.2 验证服务
curl http://localhost:8000/health

# 5.3 停止测试进程
# Ctrl+C

# 5.4 配置systemd服务
sudo cp deployment/mystocks-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mystocks-api
sudo systemctl start mystocks-api

# 5.5 检查服务状态
sudo systemctl status mystocks-api
```

### 步骤6: 反向代理配置（Nginx）

```bash
# 6.1 安装Nginx
sudo apt install nginx

# 6.2 配置站点
sudo cp deployment/nginx-mystocks.conf /etc/nginx/sites-available/mystocks
sudo ln -s /etc/nginx/sites-available/mystocks /etc/nginx/sites-enabled/

# 6.3 测试配置
sudo nginx -t

# 6.4 重启Nginx
sudo systemctl restart nginx
```

### 步骤7: SSL证书配置（Let's Encrypt）

```bash
# 7.1 安装certbot
sudo apt install certbot python3-certbot-nginx

# 7.2 获取证书
sudo certbot --nginx -d yourdomain.com

# 7.3 自动续期
sudo certbot renew --dry-run
```

### 步骤8: 监控配置

```bash
# 8.1 部署Grafana监控
cd /opt/mystocks
./monitoring/deploy_us3_monitoring.sh

# 8.2 配置数据源
# 访问 http://yourdomain.com:3000
# 配置PostgreSQL数据源

# 8.3 导入仪表板
# 导入 monitoring/grafana_dashboards/*.json
```

### 步骤9: 验证部署

```bash
# 9.1 运行健康检查
python deployment/health_check.py

# 9.2 运行API测试
python examples/test_api_endpoints.py --base-url http://yourdomain.com

# 9.3 验证监控
curl http://yourdomain.com/api/system/health
curl http://yourdomain.com/api/system/database/health
```

### 步骤10: 备份配置

```bash
# 10.1 配置自动备份
sudo cp deployment/backup-cron /etc/cron.d/mystocks-backup

# 10.2 测试备份脚本
sudo /opt/mystocks/deployment/backup.sh

# 10.3 验证备份
ls -lh /opt/mystocks/backups/
```

---

## ✅ 部署后验证清单

### 基础功能验证

- [ ] **服务运行**
  - [ ] API服务正常运行
  - [ ] systemd服务状态为active
  - [ ] 日志无错误信息

- [ ] **健康检查**
  - [ ] /health返回200
  - [ ] /api/system/health显示healthy
  - [ ] /api/system/database/health显示所有数据库healthy

- [ ] **数据库连接**
  - [ ] PostgreSQL连接正常
  - [ ] TDengine连接正常
  - [ ] 查询测试通过

### API功能验证

- [ ] **认证**
  - [ ] 登录功能正常
  - [ ] Token刷新正常
  - [ ] 权限控制正常

- [ ] **核心API**
  - [ ] 股票查询正常
  - [ ] K线数据正常
  - [ ] 技术指标计算正常
  - [ ] 市场数据查询正常

- [ ] **缓存**
  - [ ] 缓存功能启用
  - [ ] 缓存命中率正常
  - [ ] 缓存失效正常

### 性能验证

- [ ] **响应时间**
  - [ ] 平均响应时间 < 200ms
  - [ ] 99分位响应时间 < 1s
  - [ ] 无超时错误

- [ ] **并发能力**
  - [ ] 支持100并发请求
  - [ ] 无连接池耗尽
  - [ ] 无数据库锁超时

- [ ] **资源使用**
  - [ ] CPU使用率 < 70%
  - [ ] 内存使用率 < 80%
  - [ ] 磁盘I/O正常

### 监控验证

- [ ] **Grafana**
  - [ ] 仪表板正常显示
  - [ ] 数据实时更新
  - [ ] 告警规则生效

- [ ] **日志**
  - [ ] 日志正常写入
  - [ ] 日志轮转正常
  - [ ] 错误日志告警正常

- [ ] **备份**
  - [ ] 自动备份正常执行
  - [ ] 备份文件完整
  - [ ] 恢复测试通过

---

## 🔧 常见问题排查

### 问题1: 服务无法启动

**症状**: systemctl status显示failed

**排查步骤**:
```bash
# 查看详细日志
sudo journalctl -u mystocks-api -n 50

# 检查端口占用
sudo netstat -tulpn | grep 8000

# 检查环境变量
cat /opt/mystocks/.env

# 手动启动测试
cd /opt/mystocks
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 问题2: 数据库连接失败

**症状**: Database connection error

**排查步骤**:
```bash
# 测试PostgreSQL连接
PGPASSWORD=your_password psql -h localhost -U postgres -d mystocks -c "SELECT version();"

# 测试TDengine连接
taos -h localhost -P 6030 -u root -p taosdata -s "SELECT server_version();"

# 检查防火墙
sudo ufw status
sudo firewall-cmd --list-all

# 检查数据库服务
sudo systemctl status postgresql
sudo systemctl status taosd
```

### 问题3: API响应慢

**症状**: 请求超时或响应时间过长

**排查步骤**:
```bash
# 检查数据库性能
python deployment/check_db_performance.py

# 检查缓存状态
curl http://localhost:8000/api/system/health | jq '.cache'

# 查看慢查询日志
sudo tail -f /opt/mystocks/logs/slow_queries.log

# 检查系统资源
top
free -h
df -h
```

### 问题4: SSL证书问题

**症状**: HTTPS访问失败

**排查步骤**:
```bash
# 检查证书状态
sudo certbot certificates

# 测试Nginx配置
sudo nginx -t

# 查看Nginx错误日志
sudo tail -f /var/log/nginx/error.log

# 手动续期证书
sudo certbot renew
```

---

## 📊 性能基准

### 预期性能指标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| **平均响应时间** | < 200ms | 所有API平均值 |
| **99分位响应时间** | < 1s | 99%请求的响应时间 |
| **并发请求** | 100+ | 同时处理的请求数 |
| **数据库查询** | < 100ms | 单次查询平均时间 |
| **缓存命中率** | > 70% | 缓存有效性 |
| **CPU使用率** | < 70% | 正常负载下 |
| **内存使用率** | < 80% | 正常负载下 |
| **可用性** | > 99.9% | 年停机时间 < 8.76小时 |

---

## 🔄 升级和回滚

### 升级流程

```bash
# 1. 备份当前版本
cd /opt/mystocks
./deployment/backup.sh

# 2. 拉取新代码
git fetch origin
git checkout v2.1.0  # 替换为新版本号

# 3. 更新依赖
source venv/bin/activate
pip install -r requirements.txt

# 4. 数据库迁移
python deployment/migrate_database.py

# 5. 重启服务
sudo systemctl restart mystocks-api

# 6. 验证升级
python deployment/health_check.py
```

### 回滚流程

```bash
# 1. 停止服务
sudo systemctl stop mystocks-api

# 2. 回滚代码
cd /opt/mystocks
git checkout v2.0.0  # 替换为旧版本号

# 3. 恢复数据库（如需要）
./deployment/restore_backup.sh /opt/mystocks/backups/backup-20251025.tar.gz

# 4. 重启服务
sudo systemctl start mystocks-api

# 5. 验证回滚
python deployment/health_check.py
```

---

## 📞 支持和联系

**部署支持**: deployment@mystocks.com
**技术支持**: support@mystocks.com
**文档**: https://docs.mystocks.com

**紧急联系**: +86-xxx-xxxx-xxxx (7x24小时)

---

**版本**: 1.0.0
**最后更新**: 2025-10-25
**维护者**: MyStocks DevOps Team
