# MyStocks Phase 6.2 服务器恢复后测试流程
# 执行时间: 服务器恢复后立即执行

## 紧急恢复流程 (5分钟)

### 1. 数据库连接验证
```bash
# 立即验证所有数据库连接
./scripts/tools/verify-database-connections.sh
```

**成功标准**: 所有数据库显示"✅ 连接成功"

### 2. 服务启动测试
```bash
# 启动前端和后端服务
cd web/backend && python run_server.py &
cd web/frontend && npm run dev -- --port 3001 &
```

**成功标准**:
- 后端: http://localhost:8000/api/health 返回200
- 前端: http://localhost:3001 可访问

### 3. PM2服务部署
```bash
# 使用PM2部署完整服务栈
pm2 start ecosystem.config.js
pm2 save
```

**成功标准**: `pm2 list` 显示所有服务为"online"

## 完整验证流程 (15分钟)

### 4. 端到端测试链路验证
```bash
# 执行Phase 6.1测试链路验证
python scripts/test-runner/run-orchestration.sh --all
```

**成功标准**: 所有测试阶段显示"✅ PASSED"

### 5. CI/CD工作流测试
```bash
# 验证GitHub Actions配置
./scripts/tools/test-github-actions-syntax.sh
```

**成功标准**: "✅ CI/CD workflow syntax is valid"

### 6. 持续优化数据收集测试
```bash
# 模拟CI/CD环境测试优化数据收集
./scripts/tools/test-optimization-data-collection.sh
```

**成功标准**: 生成优化报告和建议

## 生产部署验证 (10分钟)

### 7. 生产环境配置验证
```bash
# 验证生产环境配置
./scripts/tools/verify-production-config.sh
```

**成功标准**: 所有生产配置正确

### 8. 监控和告警验证
```bash
# 启动监控栈
cd monitoring-stack && docker-compose up -d
```

**成功标准**:
- Grafana: http://localhost:3000 可访问
- Prometheus: http://localhost:9090 可访问

## 性能和稳定性测试 (20分钟)

### 9. 性能基准测试
```bash
# 运行性能测试套件
./performance-tests/locustfile.py --host=http://localhost:8000
```

**成功标准**: 响应时间<500ms，错误率<1%

### 10. 稳定性测试
```bash
# 运行持续负载测试 (1小时)
./scripts/tools/run-stability-test.sh --duration=3600
```

**成功标准**: 无服务崩溃，内存使用稳定

## 最终验证和报告

### 11. Phase 6.2完成验证
```bash
# 生成最终完成报告
./scripts/tools/generate-phase6-completion-report.sh
```

**输出**: `docs/reports/PHASE6_COMPLETION_REPORT.md`

### 12. 部署就绪检查
- ✅ 数据库连接正常
- ✅ 服务自动启动
- ✅ CI/CD流水线完整
- ✅ 监控告警就绪
- ✅ 性能达标
- ✅ 文档完整

## 应急处理

### 如果数据库连接失败
```bash
# 检查数据库服务状态
ssh user@192.168.123.104 "systemctl status postgresql tdengine mysql redis"
```

### 如果服务启动失败
```bash
# 查看详细错误日志
pm2 logs --lines=50
tail -f web/backend/logs/*.log
```

### 如果测试失败
```bash
# 运行诊断脚本
./scripts/tools/diagnose-test-failures.sh
```

## 时间估算

- **紧急恢复**: 5分钟
- **完整验证**: 15分钟
- **生产部署**: 10分钟
- **性能测试**: 20分钟
- **总计**: ~50分钟

## 成功标准

✅ **所有数据库连接正常**
✅ **前后端服务自动启动**
✅ **PM2进程管理正常**
✅ **测试链路100%通过**
✅ **CI/CD配置正确**
✅ **监控告警就绪**
✅ **性能指标达标**
✅ **文档和报告完整**

---

*Phase 6.2 服务器恢复测试流程 - 自动生成*