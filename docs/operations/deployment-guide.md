# MyStocks 部署指南

## 端口配置

### 端口范围说明
- **后端服务**: 8000-8010 (自动选择可用端口)
- **前端服务**: 3000-3010 (自动选择可用端口)

系统会在指定范围内自动查找并使用可用端口，避免端口冲突问题。

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
- 访问后端API文档：http://localhost:8000/api/docs (端口可能为8000-8010)
- 访问前端页面：http://localhost:3000 (端口可能为3000-3010)
- 检查监控系统
- 验证AI功能
