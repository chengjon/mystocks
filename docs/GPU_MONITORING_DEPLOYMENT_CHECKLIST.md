# GPU监控仪表板 - 部署检查清单

## 前置条件

### 系统要求
- [ ] 操作系统: Linux (Ubuntu 20.04+, CentOS 7+) 或 Windows (WSL2)
- [ ] Python: 3.8+
- [ ] Node.js: 16+
- [ ] PostgreSQL: 12+
- [ ] 内存: 至少 4GB
- [ ] 磁盘: 至少 10GB 可用空间

### 可选要求
- [ ] NVIDIA GPU (无GPU时使用模拟数据)
- [ ] NVIDIA Driver: 470+ (如使用GPU)
- [ ] CUDA Toolkit: 11.0+ (如使用GPU)

## 后端部署检查

### 1. 依赖安装
- [ ] Python 3.8+ 已安装: `python3 --version`
- [ ] pip 已安装: `pip --version`
- [ ] virtualenv 已安装 (推荐): `pip show virtualenv`

### 2. Python包依赖
- [ ] fastapi: `pip show fastapi`
- [ ] uvicorn: `pip show uvicorn`
- [ ] pynvml: `pip show nvidia-ml-py`
- [ ] psutil: `pip show psutil`
- [ ] sqlalchemy: `pip show sqlalchemy`
- [ ] pydantic: `pip show pydantic`
- [ ] cupy: `pip show cupy` (可选，GPU需要)
- [ ] numpy: `pip show numpy`

### 3. 数据库配置
- [ ] PostgreSQL 服务运行中: `systemctl status postgresql`
- [ ] 数据库已创建: `psql -l | grep mystocks`
- [ ] 用户权限已配置: `psql -U postgres -c "\du"`
- [ ] 环境变量已设置:
  - [ ] POSTGRESQL_HOST
  - [ ] POSTGRESQL_PORT
  - [ ] POSTGRESQL_USER
  - [ ] POSTGRESQL_PASSWORD
  - [ ] POSTGRESQL_DATABASE

### 4. 代码文件检查
- [ ] 后端代码存在: `src/gpu_monitoring/`
- [ ] API路由存在: `src/api/gpu_monitoring_routes.py`
- [ ] 测试文件存在: `tests/test_gpu_monitoring*.py`

### 5. 数据库表创建
- [ ] gpu_monitoring_history 表已创建
- [ ] gpu_performance_events 表已创建
- [ ] 索引已创建:
  - [ ] idx_gpu_monitoring_device_time
  - [ ] idx_gpu_monitoring_timestamp

### 6. 测试验证
- [ ] 单元测试通过: `pytest tests/test_gpu_monitoring.py -v`
- [ ] API测试通过: `pytest tests/test_gpu_monitoring_api.py -v`
- [ ] 测试覆盖率 > 80%

### 7. 后端服务启动
- [ ] 手动启动成功: `uvicorn src.api.gpu_monitoring_routes:app`
- [ ] 健康检查通过: `curl http://localhost:8000/health`
- [ ] API文档可访问: `http://localhost:8000/docs`

## 前端部署检查

### 1. 依赖安装
- [ ] Node.js 16+ 已安装: `node --version`
- [ ] npm 已安装: `npm --version`

### 2. npm包依赖
- [ ] vue: `npm list vue`
- [ ] element-plus: `npm list element-plus`
- [ ] echarts: `npm list echarts`
- [ ] axios: `npm list axios`

### 3. 代码文件检查
- [ ] 前端代码存在: `web/frontend/src/components/GPUMonitoring/`
- [ ] 组件文件:
  - [ ] GPUStatusCard.vue
  - [ ] PerformanceChart.vue
  - [ ] OptimizationPanel.vue
  - [ ] PerformanceStatsCard.vue
- [ ] Composable文件: `useGPUStream.ts`
- [ ] 页面文件: `GPUMonitoring.vue`

### 4. 路由配置
- [ ] 路由已添加: `web/frontend/src/router/index.js`
- [ ] 路由路径: `/gpu-monitoring`
- [ ] 组件导入正确

### 5. 构建验证
- [ ] 开发模式启动: `npm run dev`
- [ ] 前端可访问: `http://localhost:5173/gpu-monitoring`
- [ ] 无控制台错误

## 集成部署检查

### 1. 服务启动脚本
- [ ] 启动脚本存在: `scripts/start_gpu_monitoring.sh`
- [ ] 停止脚本存在: `scripts/stop_gpu_monitoring.sh`
- [ ] 脚本有执行权限: `ls -l scripts/*.sh`

### 2. 日志配置
- [ ] 日志目录存在: `logs/`
- [ ] 后端日志文件: `logs/gpu-api.log`
- [ ] 前端日志文件: `logs/gpu-frontend.log`

### 3. 端口配置
- [ ] 后端端口 8000 未被占用: `netstat -tuln | grep 8000`
- [ ] 前端端口 5173 未被占用: `netstat -tuln | grep 5173`
- [ ] 防火墙规则已配置 (如需要)

### 4. 完整启动测试
- [ ] 使用启动脚本启动: `./scripts/start_gpu_monitoring.sh`
- [ ] 后端服务运行中: `ps aux | grep uvicorn`
- [ ] 前端服务运行中: `ps aux | grep "npm run dev"`
- [ ] 健康检查通过: `curl http://localhost:8000/health`

### 5. API端点测试
- [ ] GPU指标: `curl http://localhost:8000/api/gpu/metrics/0`
- [ ] 性能指标: `curl http://localhost:8000/api/gpu/performance`
- [ ] 历史数据: `curl http://localhost:8000/api/gpu/history/0?hours=1`
- [ ] 聚合统计: `curl http://localhost:8000/api/gpu/stats/0?hours=24`
- [ ] 优化建议: `curl http://localhost:8000/api/gpu/recommendations`

### 6. 前端功能测试
- [ ] GPU状态卡片正常显示
- [ ] 性能图表正常渲染
- [ ] 优化建议正常显示
- [ ] 实时数据更新 (2秒刷新)
- [ ] 时间范围切换正常

## 生产环境部署检查

### 1. 进程管理 (PM2)
- [ ] PM2 已安装: `pm2 --version`
- [ ] 后端服务已配置: `pm2 list | grep gpu-api`
- [ ] 前端服务已配置: `pm2 list | grep gpu-frontend`
- [ ] 服务自动重启已配置

### 2. 反向代理 (Nginx)
- [ ] Nginx 已安装: `nginx -v`
- [ ] 配置文件存在: `/etc/nginx/sites-available/gpu-monitoring`
- [ ] SSL证书已配置 (如需要)
- [ ] 静态文件路径正确
- [ ] API代理配置正确
- [ ] SSE支持已配置 (proxy_buffering off)

### 3. 数据库优化
- [ ] 连接池已配置
- [ ] 索引已优化
- [ ] 定期清理任务已配置
- [ ] 备份策略已制定

### 4. 监控和日志
- [ ] 系统监控已配置 (Prometheus/Grafana)
- [ ] 日志收集已配置 (ELK/Loki)
- [ ] 告警通知已配置 (邮件/Slack)
- [ ] 性能监控已配置

### 5. 安全加固
- [ ] CORS 已配置
- [ ] 认证已启用 (如需要)
- [ ] HTTPS 已启用
- [ ] 防火墙规则已配置
- [ ] 数据库密码已加密

## 文档检查

- [ ] 完成报告: `docs/GPU_MONITORING_COMPLETION_REPORT.md`
- [ ] 快速开始: `docs/GPU_MONITORING_QUICK_START.md`
- [ ] 项目总结: `docs/GPU_MONITORING_SUMMARY.md`
- [ ] 部署检查清单: 本文件

## 最终验收

### 功能测试
- [ ] GPU硬件监控正常工作
- [ ] 性能指标采集正常工作
- [ ] 历史数据查询正常工作
- [ ] 优化建议生成正常工作
- [ ] SSE实时推送正常工作
- [ ] 告警系统正常工作

### 性能测试
- [ ] 指标采集延迟 < 100ms
- [ ] SSE推送延迟 < 2秒
- [ ] 历史查询速度 < 500ms
- [ ] 前端图表渲染 < 1秒

### 稳定性测试
- [ ] 7x24小时稳定运行
- [ ] 内存无泄漏
- [ ] CPU使用正常
- [ ] 数据库连接正常

### 用户体验
- [ ] 页面加载速度快
- [ ] 响应式布局正常
- [ ] 移动端适配正常
- [ ] 错误提示清晰

---

**部署状态**: [ ] 待部署 / [ ] 部署中 / [ ] 已完成

**部署人员**: _______________

**部署日期**: _______________

**备注**: _______________
