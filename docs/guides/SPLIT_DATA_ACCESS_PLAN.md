# Data Access文件拆分计划

**目标**: 将1549行的`src/data_access.py`拆分为多个小模块
**当前问题**: 循环依赖、文件过大、难以维护

## 文件结构分析

### 当前src/data_access.py包含:
1. **接口定义** (第1-115行)
   - IDataAccessLayer抽象基类
   - 导入和配置

2. **TDengine访问类** (第116-759行)
   - TDengineDataAccess类
   - 时序数据访问实现

3. **PostgreSQL访问类** (第760-1549行)
   - PostgreSQLDataAccess类
   - 关系数据访问实现

## 拆分方案

### 1. 创建模块结构
```
src/data_access/
├── __init__.py              # 统一导出
├── interfaces.py            # 接口定义
├── tdengine_access.py       # TDengine访问实现
├── postgresql_access.py     # PostgreSQL访问实现
└── factory.py              # 工厂模式
```

### 2. 循环依赖解决

**当前依赖链**:
```
src/core/data_manager.py → src/data_access.py → src/storage/database/connection_manager.py
                      ↑                                              ↓
                      ←────────────────────────────────────────────────
```

**解决方案**:
1. 将connection_manager移到独立的utils模块
2. 使用依赖注入避免直接导入
3. 在data_manager中使用懒加载

### 3. 拆分步骤

#### Step 1: 创建新的目录结构
```bash
mkdir -p src/data_access
```

#### Step 2: 提取接口定义 (interfaces.py)
- 第1-115行内容
- IDataAccessLayer抽象基类

#### Step 3: 提取TDengine实现 (tdengine_access.py)
- 第116-759行内容
- TDengineDataAccess类

#### Step 4: 提取PostgreSQL实现 (postgresql_access.py)
- 第760-1549行内容
- PostgreSQLDataAccess类

#### Step 5: 创建工厂模块 (factory.py)
- 工厂方法创建不同访问器实例

#### Step 6: 更新__init__.py
- 统一导出接口
- 保持向后兼容

#### Step 7: 修复导入引用
- 更新所有引用data_access.py的文件
- 解决循环依赖

## 预期收益

1. **代码可维护性**: 每个文件 < 500行
2. **循环依赖解决**: 模块间依赖清晰
3. **测试友好**: 可以单独测试每个模块
4. **扩展性**: 易于添加新的数据源类型

## 风险控制

1. **备份原文件**: 保留原始文件作为备份
2. **渐进式迁移**: 一次迁移一个模块
3. **测试验证**: 每次拆分后运行完整测试
4. **回滚计划**: 如果问题立即回滚到原文件

## 开始执行

```bash
# 1. 备份原文件
cp src/data_access.py src/data_access.py.backup

# 2. 创建新目录
mkdir -p src/data_access

# 3. 开始拆分...
```