# MyStocks 部署指南

## 端口配置

### 固定端口说明
- **后端服务**: 8020
- **后端备用端口**: 8021
- **前端服务**: 3020
- **前端备用端口**: 3021

当前端口规则以 `web/PORTS.md` 与 `.env` 为准，不再使用“自动范围选择端口”口径。

## 快速部署

### 1. 环境准备
```bash
# 安装依赖
pip install -r requirements.txt

# 启动数据库
docker-compose up -d

# 初始化GPU环境
python src/gpu/api_system/wsl2_gpu_init.py
```

### 2. 自动化部署
```bash
# 运行部署脚本
./scripts/automation/deploy.sh

# 检查部署状态
./scripts/automation/health_check.sh
```

### 3. 验证部署
- 访问后端API文档：http://localhost:8020/api/docs
- 访问前端页面：http://localhost:3020
- 检查监控系统
- 验证AI功能
