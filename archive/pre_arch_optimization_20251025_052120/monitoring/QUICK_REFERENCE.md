# Grafana快速参考卡片

---

## 🔑 访问信息

| 项目 | 信息 |
|-----|------|
| **URL** | http://localhost:3000 |
| **用户名** | admin |
| **密码** | mystocks2025 |

---

## 📝 数据源配置 (5分钟)

```
导航: Configuration → Data Sources → Add data source → PostgreSQL

配置参数:
  Name: MyStocks-Monitoring
  Host: localhost:5438
  Database: mystocks_monitoring
  User: postgres
  Password: your-postgresql-password
  SSL Mode: disable
  Version: 15

点击: Save & test
```

---

## 📊 导入监控面板 (2分钟)

```
导航: Create → Import

上传文件: monitoring/grafana_dashboard.json
数据源: MyStocks-Monitoring

点击: Import
```

---

## 🔄 生成测试数据

```bash
cd /mnt/wd_mycode/mystocks_spec
python test_monitoring_with_redis.py
```

---

## 🐛 快速故障排查

### 面板显示"No Data"
```bash
# 生成监控数据
python test_monitoring_with_redis.py

# 刷新Grafana面板
```

### 数据源连接失败
```bash
# 测试PostgreSQL连接
psql -h localhost -p 5438 -U postgres -d mystocks_monitoring

# 如果失败，检查:
# 1. PostgreSQL是否运行
# 2. 密码是否正确
# 3. 防火墙端口5438是否开放
```

### Grafana无法访问
```bash
# 检查容器状态
docker ps | grep grafana

# 查看容器日志
docker logs mystocks-grafana

# 重启容器
docker restart mystocks-grafana
```

---

## 📚 完整文档

- **手动配置**: `monitoring/MANUAL_SETUP_GUIDE.md`
- **部署指南**: `monitoring/grafana_setup.md`
- **NAS部署**: `monitoring/NAS_GRAFANA_DEPLOYMENT.md`
- **项目总结**: `PHASE5_US3_COMPLETION_REPORT.md`

---

**预计配置时间**: 10-15分钟

🎉 **祝使用愉快!**
