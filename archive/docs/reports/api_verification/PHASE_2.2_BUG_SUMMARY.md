# Phase 2.2 K线API验证 - BUG摘要

> **历史总结说明**:
> 本文件是阶段性总结、报告、状态、修复记录、验证结果或交付回执，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现、验证结果及主线文档一并核对。
>
> 文内统计值、完成状态、结论、验证结果和修复结论如未重新复核，应视为历史快照，不得直接当作当前事实。


**验证日期**: 2026-01-02
**API范围**: `/api/v1/market/kline`, `/api/v1/tdx/kline`

---

## 发现的BUG (3个)

### 🔴 BUG-KLINE-001: 月K线返回422错误

**严重程度**: HIGH
**API**: `/api/v1/market/kline?period=monthly`
**影响**: 技术分析页面月线图功能完全不可用

**复现命令**:
```bash
curl -X GET "http://localhost:8000/api/v1/market/kline?stock_code=600519&period=monthly&adjust=qfq&limit=10" \
  -H "Authorization: Bearer dev-mock-token-for-development"
```

**错误响应**:
```json
{"success":false,"code":422,"message":"内部服务器错误","data":null}
```

**预期**: 返回月K线OHLCV数据
**实际**: 422错误

**修复位置**: `/opt/claude/mystocks_spec/web/backend/app/api/market.py:649`
**可能原因**:
- AKShare的`stock_zh_a_hist()`不支持月线周期
- 需要从日线数据聚合生成月线

---

### 🔴 BUG-KLINE-002: start_date/end_date参数返回422错误

**严重程度**: HIGH (P0)
**API**: `/api/v1/market/kline?start_date=XXX&end_date=XXX`
**影响**: 所有需要指定日期范围的功能不可用

**复现命令**:
```bash
curl -X GET "http://localhost:8000/api/v1/market/kline?stock_code=600519&period=daily&adjust=qfq&start_date=2025-01-01&end_date=2025-01-10&limit=10" \
  -H "Authorization: Bearer dev-mock-token-for-development"
```

**错误响应**:
```json
{"success":false,"code":422,"message":"内部服务器错误","data":null}
```

**预期**: 返回2025-01-01到2025-01-10的K线数据
**实际**: 422错误

**修复位置**: `/opt/claude/mystocks_spec/web/backend/app/api/market.py:684-689`

**问题代码**:
```python
# Line 684-689
validated_params = MarketDataQueryModel(
    symbol=stock_code,
    start_date=dt_convert.strptime(start_date, "%Y-%m-%d") if start_date else dt_convert.now(),
    end_date=dt_convert.strptime(end_date, "%Y-%m-%d") if end_date else dt_convert.now(),
    interval=period,
)
```

**可能原因**:
1. `MarketDataQueryModel`验证逻辑错误
2. 日期格式转换异常
3. `get_a_stock_kline()`未正确处理日期参数

---

### 🟡 BUG-KLINE-003: TDX K线API性能极差且返回空数据

**严重程度**: MEDIUM
**API**: `/api/v1/tdx/kline`
**影响**: 备用数据源不可用

**复现命令**:
```bash
curl -X GET "http://localhost:8000/api/v1/tdx/kline?symbol=600519&period=1d&start_date=2025-01-01&end_date=2025-01-15" \
  -H "Authorization: Bearer dev-mock-token-for-development"
```

**实际行为**:
- 响应时间: **18.102秒** (目标<0.5秒)
- 返回数据: `{"code":"600519","period":"1d","data":[],"count":0}`

**修复位置**: `/opt/claude/mystocks_spec/web/backend/app/api/tdx.py:91`

**建议**:
1. 添加5秒超时控制
2. 实现缓存机制
3. 或弃用此端点

---

## 正常工作的功能 ✅

1. **日K线查询** - 平均响应时间 0.199秒 ✅
2. **周K线查询** - 响应时间 0.131秒 ✅
3. **前复权(qfq)** - 数据正确 ✅
4. **后复权(hfq)** - 数据正确 ✅
5. **不复权** - 数据正确 ✅
6. **数据完整性** - OHLCV字段完整 ✅

---

## 修复优先级

| Bug ID | 优先级 | 工作量 | 建议时间 |
|--------|--------|--------|----------|
| BUG-KLINE-002 | **P0** | 2-4h | 立即修复 |
| BUG-KLINE-001 | P1 | 4-8h | 本周内 |
| BUG-KLINE-003 | P2 | 8-16h | 下迭代 |

---

## 快速修复建议

### BUG-KLINE-002 (最紧急)

**方案**: 绕过`MarketDataQueryModel`,直接传递日期字符串
```python
# 修改: 直接传递,让service层处理
result = service.get_a_stock_kline(
    symbol=stock_code,
    period=period,
    adjust=adjust,
    start_date=start_date,
    end_date=end_date,
)
```

### BUG-KLINE-001

**方案**: 从日线数据聚合月线,或明确返回不支持
```python
if period == "monthly":
    raise HTTPException(
        status_code=400,
        detail="月K线暂不支持,请使用日线或周线"
    )
```

---

**完整报告**: `docs/reports/api_verification/PHASE_2.2_KLINE_API_VERIFICATION_REPORT.md`
**报告时间**: 2026-01-02 10:15 UTC
