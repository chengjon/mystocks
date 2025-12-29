# MyStocks 快速开始指南

欢迎使用 MyStocks - 专业的A股量化交易分析平台

## 前置要求

- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- （可选）TDengine 3+ (用于时序数据)

## 快速安装

### 1. 克隆仓库

```bash
git clone <repository-url>
cd mystocks_phase6_quality
```

### 2. 安装Python依赖

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

复制并编辑环境变量文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置数据库连接：

```bash
# PostgreSQL配置
POSTGRESQL_HOST=192.168.123.104
POSTGRESQL_PORT=5438
POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=your_password
POSTGRESQL_DATABASE=mystocks

# TDengine配置（可选）
TDENGINE_HOST=localhost
TDENGINE_PORT=6030
TDENGINE_USER=root
TDENGINE_PASSWORD=taosdata
```

### 4. 初始化数据库

```bash
# 运行数据库迁移
python scripts/init_database.py
```

### 5. 启动后端服务

```bash
cd web/backend
python -m app.main
```

后端服务将在 `http://localhost:8000` 启动

### 6. 启动前端服务

```bash
cd web/frontend
npm install
npm run dev
```

前端服务将在 `http://localhost:3000` 启动

## 验证安装

### 检查后端健康状态

```bash
curl http://localhost:8000/health
```

预期响应：

```json
{
  "success": true,
  "code": 0,
  "message": "系统健康检查完成",
  "data": {
    "service": "mystocks-web-api",
    "status": "healthy",
    "timestamp": 1735497600.0,
    "version": "1.0.0"
  }
}
```

### 访问API文档

打开浏览器访问：
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### 访问前端界面

打开浏览器访问：http://localhost:3000

## 核心功能概览

### 1. 市场数据
- 实时行情数据
- K线图表数据
- 技术指标计算

### 2. 技术分析
- 161个技术指标
- 自定义指标组合
- 技术形态识别

### 3. 智能选股
- 自然语言查询
- 多策略推荐
- 风险评估

### 4. 策略回测
- 策略回测引擎
- 性能分析报告
- 参数优化

### 5. 风险管理
- 风险评估指标
- 投资组合分析
- 告警通知

## 常用API示例

### 获取股票K线数据

```bash
curl "http://localhost:8000/api/data/kline/000001?interval=1d&limit=100"
```

### 计算技术指标

```bash
curl "http://localhost:8000/api/indicators/000001/MACD"
```

### 获取实时行情

```bash
curl "http://localhost:8000/api/data/realtime/000001"
```

### 执行选股策略

```bash
curl -X POST "http://localhost:8000/api/strategy/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_id": "value",
    "params": {
      "top_n": 20,
      "min_score": 60
    }
  }'
```

## 开发指南

### 运行测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=src --cov-report=html

# 运行特定测试文件
pytest tests/unit/test_example.py
```

### 代码质量检查

```bash
# 运行代码格式化
black src/ tests/

# 运行Ruff检查
ruff check --fix .

# 运行Pylint检查
pylint src/
```

### 安全审计

```bash
# Bandit安全扫描
bandit -r src/ -f json -o reports/bandit_report.json

# Safety依赖安全检查
safety check --json > reports/safety_report.json
```

## 性能测试

### Locust压力测试

```bash
# 启动Locust Web界面
locust -f tests/load/locustfile.py --host=http://localhost:8000

# 运行无头模式压测
locust -f tests/load/locustfile.py \
  --host=http://localhost:8000 \
  --users=100 \
  --spawn-rate=10 \
  --run-time=5m \
  --headless \
  --html=reports/locust_report.html
```

## 故障排查

### 后端启动失败

检查日志：
```bash
# 查看应用日志
tail -f logs/app.log

# 检查数据库连接
psql -h localhost -p 5438 -U postgres -d mystocks
```

### 前端启动失败

```bash
# 清除缓存
rm -rf node_modules package-lock.json
npm install

# 检查端口占用
lsof -i :3000
```

### 数据库连接问题

```bash
# 测试PostgreSQL连接
psql -h 192.168.123.104 -p 5438 -U postgres

# 检查防火墙设置
telnet 192.168.123.104 5438
```

## 下一步

- 阅读完整的 [部署指南](docs/DEPLOYMENT_GUIDE.md)
- 查看 [API文档](docs/api/README.md)
- 了解 [架构设计](docs/architecture/README.md)
- 探索 [测试指南](docs/testing/README.md)

## 获取帮助

- 提交Issue: [GitHub Issues](https://github.com/your-org/mystocks/issues)
- 文档: [完整文档](docs/)
- 社区讨论: [Discussions](https://github.com/your-org/mystocks/discussions)

---

祝您使用愉快！🎉
