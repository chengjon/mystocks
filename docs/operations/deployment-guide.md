# MyStocks 部署指南

> **使用说明**:
> 本文件属于历史部署说明，不是当前运行架构、当前端口基线或仓库共享规则的唯一事实来源。
> 若涉及环境一致性、PM2/Docker 优先级、服务地址或运行门禁，请优先遵循 `architecture/STANDARDS.md`；若涉及运维执行流程或协作约束，再结合根目录 `AGENTS.md` 与 `docs/operations/README.md`。
>
> 文内端口范围、部署脚本与访问地址如未重新核实，应视为历史部署快照。

## 端口配置

### 历史端口范围说明
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
- 访问后端API文档：http://localhost:8020/api/docs (端口可能为8000-8010)
- 访问前端页面：http://localhost:3000 (端口可能为3000-3010)
- 检查监控系统
- 验证AI功能
