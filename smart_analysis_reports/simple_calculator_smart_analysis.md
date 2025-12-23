# simple_calculator 智能分析报告

## 📊 分析概览

- **函数数量**: 18
- **高风险函数**: 0
- **发现Bug**: 4
- **生成测试**: 4
- **平均复杂度**: 1.6

## 🔍 函数分析

### 高风险函数

## 🐛 Bug预测

### 发现的问题

- **sql_injection** (行 42)
  - 严重程度: high
  - 描述: 存在SQL注入风险

- **sql_injection** (行 59)
  - 严重程度: high
  - 描述: 存在SQL注入风险

- **sql_injection** (行 76)
  - 严重程度: high
  - 描述: 存在SQL注入风险

- **sql_injection** (行 253)
  - 严重程度: high
  - 描述: 存在SQL注入风险

## 🧪 智能测试

### 测试分布
- **安全测试**: 3 个
- **单元测试**: 1 个

### 高优先级测试

- **test_simple_calculator_bug_prevention_sql_injection**
  - 描述: Bug防护测试: 存在SQL注入风险
  - 优先级: 14.0

- **test_simple_calculator_bug_prevention_sql_injection**
  - 描述: Bug防护测试: 存在SQL注入风险
  - 优先级: 14.0

- **test_simple_calculator_bug_prevention_sql_injection**
  - 描述: Bug防护测试: 存在SQL注入风险
  - 优先级: 14.0

- **test_simple_calculator_basic_functionality**
  - 描述: 基本功能测试
  - 优先级: 5.0
