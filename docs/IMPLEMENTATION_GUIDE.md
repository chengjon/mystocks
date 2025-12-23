# MyStocks API 修复实施指南

## 📖 快速导航

### 核心文档
- **[API修复摘要](./docs/api/API_FIXES_SUMMARY.md)** - 详细的修复说明和使用指南
- **[实施完成报告](./docs/api/IMPLEMENTATION_COMPLETE_REPORT.md)** - 完整的项目总结

### 验证脚本
```bash
# 快速验证所有修复
bash scripts/quick_validation.sh

# 运行API测试
bash scripts/test_api_fixes.sh

# 数据一致性检查
python3 scripts/test_data_consistency.py
```

---

## 🔧 修改清单

### 核心修复
| 文件 | 修改行数 | 说明 |
|------|---------|------|
| `web/backend/app/api/data.py` | 66-69 | ✅ 修复limit参数硬编码 |
| `web/backend/app/api/data.py` | 148-167 | ✅ 添加数据验证和监控 |
| `web/backend/app/api/data.py` | 152-173 | ✅ 改进错误处理 |
| `web/backend/app/api/data.py` | 508-519 | ✅ 搜索API错误处理 |
| `web/backend/app/core/database.py` | 193-236 | ✅ 增强查询方法 |

### 新增模块
| 文件 | 行数 | 功能 |
|------|------|------|
| `app/core/data_validator.py` | 450 | 数据验证 |
| `app/core/api_monitoring.py` | 300 | API监控 |
| `app/api/monitoring.py` | 150 | 监控端点 |
| `app/middleware/monitoring_middleware.py` | 50 | 监控中间件 |

### 验证脚本
| 文件 | 行数 | 用途 |
|------|------|------|
| `scripts/test_api_fixes.sh` | 200 | API功能测试 |
| `scripts/test_data_consistency.py` | 350 | 数据一致性检查 |
| `scripts/quick_validation.sh` | 150 | 快速验证 |

---

## 🚀 部署步骤

### 1. 验证修复
```bash
cd /opt/claude/mystocks_spec
bash scripts/quick_validation.sh
```

期望输出: ✅ 15/15 检查通过

### 2. 启动后端服务
```bash
python web/backend/start_server.py
```

检查输出:
- `Application startup complete`
- `API Monitoring middleware enabled`
- 无错误信息

### 3. 运行API测试
```bash
bash scripts/test_api_fixes.sh
```

期望: 所有API返回200状态码

### 4. 数据一致性验证
```bash
python3 scripts/test_data_consistency.py
```

期望: 所有测试通过

### 5. 检查监控系统
```bash
# 系统健康检查
curl http://localhost:8000/api/monitoring/health

# 监控仪表板
curl http://localhost:8000/api/monitoring/dashboard

# 获取最近指标
curl http://localhost:8000/api/monitoring/metrics?limit=10
```

---

## 📊 API响应示例

### 成功响应
```json
{
  "success": true,
  "data": [
    {
      "symbol": "000001.SZ",
      "name": "平安银行",
      "industry": "银行",
      "market": "SZ"
    }
  ],
  "total": 100,
  "data_quality_score": 92.5,
  "timestamp": "2025-11-27T10:00:00Z"
}
```

### 错误响应
```json
{
  "success": false,
  "msg": "数据库连接失败，请稍后重试",
  "error_type": "database_error",
  "timestamp": "2025-11-27T10:00:00Z"
}
```

### 监控仪表板
```json
{
  "success": true,
  "data": {
    "total_requests": 10000,
    "success_rate": "98.5%",
    "avg_response_time_ms": 125.5,
    "endpoints": {
      "GET /api/data/stocks/basic": {
        "total_requests": 2500,
        "success_count": 2450,
        "error_rate": "2.0%",
        "avg_response_time_ms": 85.3,
        "avg_data_quality_score": 92.5
      }
    }
  }
}
```

---

## 🔍 监控端点详解

### 健康检查
```
GET /api/monitoring/health
```
检查系统整体健康状态
- 错误率 < 10% → 健康
- 错误率 10-20% → 警告
- 错误率 > 20% → 不健康

### 仪表板
```
GET /api/monitoring/dashboard
```
获取所有API的聚合统计
- 请求量和成功率
- 响应时间统计
- 错误率排名
- 数据质量评分

### 端点统计
```
GET /api/monitoring/endpoints/GET%20/api/data/stocks/basic
```
获取特定端点的详细统计
- 请求量分布
- 响应时间分布
- 错误消息
- 数据质量趋势

### 指标历史
```
GET /api/monitoring/metrics?endpoint=/api/data/stocks/basic&limit=100
```
获取最近的API调用记录
- 每个请求的性能指标
- 数据质量评分
- 错误信息

---

## ⚙️ 配置说明

### 数据验证配置
在 `app/core/data_validator.py` 中修改:
```python
# 股票价格合理范围
PRICE_RANGE = (0.01, 100000)

# 交易量合理范围
VOLUME_RANGE = (0, 10**12)
```

### 监控配置
在 `app/core/api_monitoring.py` 中修改:
```python
# 历史记录限制
history_limit = 10000  # 保存最近10000条

# 健康检查阈值
error_rate_threshold = 0.1  # 10%
response_time_threshold = 1000  # 1秒
quality_score_threshold = 70  # 70分
```

### 中间件配置
在应用启动时集成:
```python
from app.middleware.monitoring_middleware import setup_monitoring_middleware

app = FastAPI()
setup_monitoring_middleware(app)
```

---

## 🐛 故障排查

### 问题1: 监控API返回401
**症状**: 访问监控端点收到401未授权错误
**解决**: 提供有效的认证令牌
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/monitoring/health
```

### 问题2: 数据质量评分低 (<70)
**症状**: API返回的data_quality_score很低
**检查**:
1. 数据库连接是否正常
2. 是否有过多空值
3. 字段格式是否正确
```bash
# 查看错误日志
tail -f /var/log/mystocks/api.log
```

### 问题3: 响应时间突然变长
**症状**: API响应时间从85ms增加到500ms+
**检查**:
1. 数据库查询是否变慢
2. 是否有大量并发请求
3. 监控历史是否过大
```bash
# 清理旧数据
curl -X POST http://localhost:8000/api/monitoring/cleanup?older_than_hours=24
```

### 问题4: 验证脚本失败
**症状**: 运行test_api_fixes.sh或test_data_consistency.py失败
**解决**:
1. 确保后端服务已启动
2. 检查API_BASE_URL是否正确
3. 查看脚本的错误输出
```bash
API_BASE_URL=http://localhost:8000 bash scripts/test_api_fixes.sh
```

---

## 📈 性能优化建议

### 短期 (1-2周)
- 配置监控告警规则
- 添加数据库连接池监控
- 实现缓存命中率统计

### 中期 (2-4周)
- 时间序列数据存储 (TDengine)
- Web仪表板UI
- 性能基准测试框架

### 长期 (1-3个月)
- 机器学习异常检测
- 多区域性能监控
- 自动扩展建议系统

---

## 📚 相关文档

- [API修复摘要](./docs/api/API_FIXES_SUMMARY.md)
- [实施完成报告](./docs/api/IMPLEMENTATION_COMPLETE_REPORT.md)
- [FastAPI官方文档](https://fastapi.tiangolo.com/)
- [Pandas文档](https://pandas.pydata.org/)

---

## 📞 支持

如有问题，请查看:
1. 详细日志: `/var/log/mystocks/api.log`
2. 监控仪表板: `http://localhost:8000/api/monitoring/dashboard`
3. 项目文档: `docs/api/`

---

**最后更新**: 2025-11-27
**版本**: 1.0
**状态**: ✅ 生产就绪
