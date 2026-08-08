# 运维手册

> **版本**: 1.0 | **更新日期**: 2026-07-12
> **维护者**: 运维
> **文档类型**: 手册主页
> **上游入口**: [CORE.md](../CORE.md) → 运维角色

---

## 本手册范围

覆盖部署、监控、备份恢复、排障、运行手册。

---

## 快速入口

| 场景 | 文档 | 简介 |
|------|------|------|
| 部署 | [deployment.md](deployment.md) | deploy.yml、PM2 一等公民、部署清单 |
| 监控 | [monitoring.md](monitoring.md) | Prometheus/Grafana 监控栈、告警 |
| 备份恢复 | [operations/BACKUP_GUIDE.md](../operations/BACKUP_GUIDE.md) | 数据库备份、恢复流程 |
| 排障 | [troubleshooting.md](troubleshooting.md) | 故障排除、phase6 恢复预案、Lnav |
| 运维总览 | [operations/OPS_MANUAL.md](../operations/OPS_MANUAL.md) | 运维标准流程、应急预案 |
| 运维快参 | [operations/STOCKS_SPEC_COMMAND_GUIDE.md](../operations/STOCKS_SPEC_COMMAND_GUIDE.md) | 常用命令一页纸 |
| 生产信息 | [operations/PRODUCTION_INFO.md](../operations/PRODUCTION_INFO.md) | 端口、数据目录、关键配置 |
| 基础设施清单 | [operations/INFRASTRUCTURE_CHECKLIST.md](../operations/INFRASTRUCTURE_CHECKLIST.md) | 服务器/网络/存储检查项 |
| CI/CD 管道 | [operations/ci-cd/ARCHITECTURE.md](../operations/ci-cd/ARCHITECTURE.md) | 36 workflow、三层管道 |

---

## 部署流水线

```
develop push → staging（自动）
main push    → production（手动审批 + confirm_deployment）
```

部署验证：
```bash
# 健康检查
curl -s http://localhost:8020/health
curl -s http://localhost:3020

# PM2 状态
pm2 status
pm2 logs
```

---

## 监控栈概览

| 组件 | 端口 | 用途 |
|------|------|------|
| Prometheus | 9090 | 指标采集 |
| Grafana | 3000 | 视觉面板 |
| Alertmanager | 9093 | 告警通知 |
| Pushgateway | 9091 | 批处理指标 |

监控接入：[monitoring.md](monitoring.md) · [operations/monitoring/](../operations/monitoring/)

---

## 排障速查

| 症状 | 排查路径 |
|------|---------|
| API 502 | `pm2 logs nginx` → backend 健康 → 端口占用 |
| 前端白屏 | `cd web/frontend && npm run build` → 控制台错误 |
| DB 慢查询 | TDengine log + `SHOW QUERIES` |
| CI 失败 | `python3 scripts/ci/run_local_ci.py` 本地复现 |
| 监控断点 | `curl localhost:9090/-/healthy` |

详细排障：[troubleshooting.md](troubleshooting.md) · [operations/TROUBLESHOOTING.md](../operations/TROUBLESHOOTING.md)

---

> 跨手册链接：开发入口 [dev/](../dev/index.md) · 测试入口 [test/](../test/index.md)
