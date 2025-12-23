# MyStocks项目改进执行计划

**立即开始执行** 🚀
**执行时间**: 2025-12-16开始
**第一阶段目标**: 2-3周内完成紧急修复

## 📋 立即执行清单

### 🔥 本周必须完成 (Week 1)

#### 1. 安全漏洞修复 (优先级: 🔥 紧急)
```bash
# 运行安全检查
bandit -r src/ -f json -o security_report.json
safety check --json --output safety_report.json

# 修复关键安全问题:
# - 命令注入风险
# - 不安全的哈希算法 (MD5)
# - 文件解压安全问题
```

#### 2. 循环依赖解决 (优先级: 🔥 紧急)
```bash
# 目标文件: src/data_access.py (1,549行 - 需要拆分)
# 问题: storage模块和core模块循环导入

# 执行步骤:
1. 分析 src/data_access.py 的依赖关系
2. 将大文件拆分为多个小模块
3. 使用依赖注入解决循环依赖
4. 重构导入结构
```

#### 3. 认证系统修复 (优先级: ⚠️ 高)
```bash
# 问题: JWT令牌过期，API认证失败
# 影响: 部分API无法正常访问

# 执行步骤:
1. 检查 JWT_SECRET_KEY 配置
2. 修复令牌生成和验证逻辑
3. 更新认证中间件
4. 测试所有受保护的API端点
```

### 🎯 下周执行计划 (Week 2)

#### 4. 数据源适配器优化
```bash
# 当前状态: Mock数据源工作正常，Real数据源有问题
# 目标: 统一适配器接口，完善Real数据源

# 执行步骤:
1. 标准化适配器接口
2. 修复Real数据源连接问题
3. 完善错误处理机制
4. 添加数据质量验证
```

#### 5. 实时数据功能修复
```bash
# 问题: WebSocket连接不稳定，SSE推送有问题
# 目标: 稳定的实时数据推送

# 执行步骤:
1. 修复WebSocket连接稳定性
2. 优化SSE推送性能
3. 添加连接重试机制
4. 实现实时数据API
```

## 🛠️ 执行工具和脚本

### 1. 使用已创建的切换工具
```bash
# 测试数据模式切换
python scripts/switch_data_mode.py --status
python scripts/switch_data_mode.py --mode mock --test
python scripts/switch_data_mode.py --mode real --test
```

### 2. 安全检查脚本
```bash
# 运行完整的安全检查
python scripts/security/basic_security_check.py
python scripts/security/security_scanner.py
```

### 3. 代码质量检查
```bash
# 运行代码质量检查
pylint src/ --output-format=json > pylint_report.json
mypy src/ --junit-xml reports/typecheck.xml
black --check src/
```

## 📊 进度跟踪

### 每日检查清单
- [ ] 前端服务状态 (http://localhost:3000)
- [ ] 后端服务状态 (http://localhost:8000)
- [ ] 数据库连接状态
- [ ] API健康检查
- [ ] 安全扫描结果
- [ ] 代码质量指标

### 每周里程碑
- **Week 1**: 安全漏洞清零，系统稳定性提升80%
- **Week 2**: 数据源适配器统一，实时数据功能稳定
- **Week 3**: API完整性达到95%，性能优化完成

## 🎯 成功指标

### 技术指标
- **安全漏洞**: 438 → 0 (目标)
- **系统启动时间**: 减少50%
- **API响应时间**: 平均 < 50ms
- **代码质量**: pylint问题减少80%

### 功能指标
- **API完整性**: 85% → 95%
- **认证系统**: 100%可用
- **数据源切换**: 100%成功
- **实时数据**: 稳定运行

## 🚨 风险控制

### 每日备份
```bash
# 每天开始工作前备份
git add -A
git commit -m "每日备份: $(date +%Y-%m-%d)"
git tag -a "backup-$(date +%Y-%m-%d)" -m "备份点"
```

### 回滚计划
```bash
# 如果出现问题，立即回滚到上一个稳定版本
git reset --hard HEAD~1
# 或使用标签回滚
git reset --hard backup-2025-12-15
```

### 测试验证
```bash
# 每次修改后必须运行的测试
python -m pytest tests/ -v
curl -f http://localhost:8000/health
curl -f http://localhost:3000
python scripts/switch_data_mode.py --status
```

## 📞 支持和帮助

### 问题排查
1. **服务启动失败**: 检查 `web/backend/backend.log`
2. **API错误**: 查看 FastAPI 日志和错误追踪
3. **数据库问题**: 检查连接字符串和权限
4. **前端问题**: 检查 Vite 配置和代理设置

### 日志位置
- 后端日志: `web/backend/backend.log`
- 前端日志: 浏览器开发者工具控制台
- 数据库日志: PostgreSQL/TDengine 日志文件
- 系统日志: `/var/log/` 相关日志文件

---

## 🎯 立即开始

**第一步**: 运行安全检查
```bash
cd /opt/claude/mystocks_spec
python scripts/security/basic_security_check.py
```

**第二步**: 检查当前服务状态
```bash
curl http://localhost:8000/health
curl http://localhost:3000
```

**第三步**: 开始修复第一个安全问题
```bash
# 查看 security_report.json 中的第一个高严重性问题
# 开始修复...
```

**记住**: 每天更新进度，每周回顾成果。我们将按照这个计划系统性地改进项目！