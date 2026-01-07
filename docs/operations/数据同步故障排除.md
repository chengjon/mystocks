# 数据同步故障排除指南

## 1. 分时线数据同步 (data-sync-minute-kline)

### 常见问题
1. **无数据同步**
   - 现象: 日志显示"未能获取到分时线数据"
   - 原因: TDX数据源连接失败或股票代码格式不正确
   - 解决方案:
     - 检查TDX服务器配置是否正确
     - 验证股票代码是否为6位数字格式
     - 确保网络连接正常

2. **数据不完整**
   - 现象: 日志显示"部分股票分时线数据获取失败"
   - 原因: 网络不稳定或TDX服务器响应超时
   - 解决方案:
     - 增加重试次数和延迟时间
     - 检查网络连接稳定性
     - 调整同步时间避开高峰期

### 日志查看
```bash
# 查看分时线同步日志
tail -f logs/data_sync/minute_kline_sync.log

# 查看错误日志
grep "ERROR" logs/data_sync/minute_kline_sync.log
```

### 手动测试
```bash
# 测试单只股票的分时线数据获取
cd /opt/claude/mystocks_spec
python scripts/data_sync/sync_minute_kline.py --limit 1 --periods 5m

# 测试指定股票
python scripts/data_sync/sync_minute_kline.py --limit 1 --periods 1m 5m 15m
```

## 2. 行业分类数据同步 (data-sync-industry-classify)

### 常见问题
1. **行业数据为空**
   - 现象: 日志显示"未能获取到行业分类数据"
   - 原因: AkShare数据源连接失败或接口变更
   - 解决方案:
     - 检查AkShare版本是否最新
     - 验证网络连接是否正常
     - 查看AkShare官方文档确认接口变更

2. **数据格式错误**
   - 现象: 日志显示"数据格式不匹配"
   - 原因: AkShare返回数据结构变更
   - 解决方案:
     - 更新适配器中的数据处理逻辑
     - 检查列名映射是否正确

### 日志查看
```bash
# 查看行业分类同步日志
tail -f logs/data_sync/industry_classify_sync.log

# 查看错误日志
grep "ERROR" logs/data_sync/industry_classify_sync.log
```

### 手动测试
```bash
# 测试行业分类数据获取
cd /opt/claude/mystocks_spec
python scripts/data_sync/sync_industry_classify.py
```

## 3. 概念分类数据同步 (data-sync-concept-classify)

### 常见问题
1. **概念数据获取失败**
   - 现象: 日志显示"获取概念分类数据失败"
   - 原因: AkShare接口调用异常
   - 解决方案:
     - 检查AkShare依赖库是否完整
     - 验证API调用参数是否正确

2. **数据更新不及时**
   - 现象: 概念数据与实际市场不符
   - 原因: 数据源更新延迟
   - 解决方案:
     - 调整同步时间
     - 增加同步频率

### 日志查看
```bash
# 查看概念分类同步日志
tail -f logs/data_sync/concept_classify_sync.log

# 查看错误日志
grep "ERROR" logs/data_sync/concept_classify_sync.log
```

### 手动测试
```bash
# 测试概念分类数据获取
cd /opt/claude/mystocks_spec
python scripts/data_sync/sync_concept_classify.py
```

## 4. 个股行业概念关联数据同步 (data-sync-stock-industry-concept)

### 常见问题
1. **个股关联信息缺失**
   - 现象: 日志显示"股票XXX没有行业概念信息"
   - 原因: 个股代码不存在或数据源无该股票信息
   - 解决方案:
     - 验证股票代码是否正确
     - 检查数据源是否支持该股票

2. **同步时间过长**
   - 现象: 同步过程耗时过长
   - 原因: 股票数量过多或网络延迟
   - 解决方案:
     - 增加并发处理
     - 优化数据获取逻辑
     - 调整同步时间窗口

### 日志查看
```bash
# 查看个股关联数据同步日志
tail -f logs/data_sync/stock_industry_concept_sync.log

# 查看错误日志
grep "ERROR" logs/data_sync/stock_industry_concept_sync.log
```

### 手动测试
```bash
# 测试个股行业概念关联数据获取（限制5只股票）
cd /opt/claude/mystocks_spec
python scripts/data_sync/sync_stock_industry_concept.py --limit 5
```

## 通用故障排除步骤

### 1. 检查PM2服务状态
```bash
# 查看所有数据同步服务状态
pm2 list | grep data-sync

# 重启特定服务
pm2 restart data-sync-minute-kline
```

### 2. 检查数据库连接
```bash
# 检查PostgreSQL连接
pg_isready -h localhost -p 5432

# 检查TDengine连接（如果需要）
taos -h localhost -P 6030
```

### 3. 检查环境变量
```bash
# 查看关键环境变量
echo $USE_MOCK_DATA
echo $TDX_SERVER_HOST
echo $TDX_SERVER_PORT
```

### 4. 检查依赖库版本
```bash
# 检查关键依赖库版本
pip show akshare
pip show pytdx
```

## 数据库相关问题

### 1. 表不存在错误
如果出现"relation XXX does not exist"错误，需要重新初始化数据库表：
```bash
cd /opt/claude/mystocks_spec
python -c "from src.core.config_driven_table_manager import ConfigDrivenTableManager; manager = ConfigDrivenTableManager(); manager.initialize_tables()"
```

### 2. 数据写入失败
如果出现数据写入失败，检查数据库连接配置和权限：
```bash
# 检查PostgreSQL连接配置
cat config/.env | grep POSTGRESQL

# 检查用户权限
psql -h localhost -U your_user -d quant_research -c "SELECT current_user;"
```
