# CLI-2 紧急问题解决方案: price_predictor.py IndentationError

**发布时间**: 2025-12-28 T+4.5h
**优先级**: 🔴 紧急阻塞
**文件**: `src/ml_strategy/price_predictor.py:430`

---

## 🔴 问题诊断

### 错误信息
```
IndentationError: unexpected indent (price_predictor.py, line 430)
```

### 根本原因

**缩进不一致问题**:
- 第428行: `axes[1].grid(True)` - **8个空格**
- 第430行: `plt.tight_layout()` - **9个空格** ❌
- 第432行: `if save_path:` - **9个空格** ❌
- 第434行: `else:` - **9个空格** ❌

**原始版本** (commit cd5c02f) 有8个空格，当前版本被Black格式化成9个空格，但Python解析器要求同一代码块缩进必须一致。

---

## ✅ 解决方案

### 方案A: Git恢复到稳定版本 (推荐⭐)

**这是最安全、最快速的解决方案**

```bash
cd /opt/claude/mystocks_phase6_e2e

# 步骤1: 查看文件历史
git log --oneline --all -- src/ml_strategy/price_predictor.py | head -5

# 步骤2: 恢复到最后稳定版本 (cd5c02f)
git show cd5c02f:src/ml_strategy/price_predictor.py > src/ml_strategy/price_predictor.py

# 步骤3: 验证修复
python3 -m py_compile src/ml_strategy/price_predictor.py
echo "✅ price_predictor.py 语法检查通过"

# 步骤4: 查看恢复的内容确认
sed -n '428,436p' src/ml_strategy/price_predictor.py
```

**预期输出**:
```python
        axes[1].grid(True)              # 8个空格 ✅
        plt.tight_layout()             # 8个空格 ✅
        if save_path:                   # 8个空格 ✅
            plt.savefig(save_path, dpi=150, bbox_inches="tight")
            self.logger.info(f"预测图表已保存: {save_path}")  # 原始版本有这行
        else:
            plt.show()
```

---

### 方案B: 手动修正缩进 (如果不想恢复)

```bash
cd /opt/claude/mystocks_phase6_e2e

# 步骤1: 使用sed统一缩进为8个空格
sed -i '430s/^        /        /' src/ml_strategy/price_predictor.py
sed -i '432s/^         /        /' src/ml_strategy/price_predictor.py
sed -i '434s/^         /        /' src/ml_strategy/price_predictor.py

# 步骤2: 验证修复
python3 -m py_compile src/ml_strategy/price_predictor.py
```

---

### 方案C: 使用Python AST自动修复 (高级方案)

```python
#!/usr/bin/env python3
"""修复Python文件的缩进问题"""
import ast
import tokenize
import io

def fix_indentation(file_path):
    """使用AST修复缩进"""
    with open(file_path, 'r') as f:
        source = f.read()

    try:
        # 尝试解析
        tree = ast.parse(source)
        # 如果成功，重新生成带正确缩进的代码
        fixed_source = ast.unparse(tree)

        with open(file_path, 'w') as f:
            f.write(fixed_source)

        print(f"✅ {file_path} 缩进已自动修复")
        return True
    except IndentationError as e:
        print(f"❌ 自动修复失败: {e}")
        return False

if __name__ == "__main__":
    fix_indentation("src/ml_strategy/price_predictor.py")
```

---

## 🎯 推荐执行步骤

### 步骤1: 立即恢复稳定版本 (2分钟)

```bash
cd /opt/claude/mystocks_phase6_e2e

# 恢复文件
git show cd5c02f:src/ml_strategy/price_predictor.py > src/ml_strategy/price_predictor.py

# 验证
python3 -m py_compile src/ml_strategy/price_predictor.py && echo "✅ 修复成功"
```

### 步骤2: 继续修复其他4个问题 (8分钟)

```bash
# 1. 修复 backtest_schemas.py (ModuleNotFoundError)
vim web/backend/app/schemas/backtest_schemas.py
# 第15行: from web.backend.app.mock → from app.mock

# 2. 修复 tdengine_manager.py (IndentationError)
vim web/backend/app/core/tdengine_manager.py
# 第21-26行: 统一try-except缩进为模块级

# 3. 修复 data_manager.py (SyntaxError)
vim src/core/data_manager.py
# 添加except块到try语句

# 4. 修复 API响应格式
vim web/backend/app/api/system.py
# 修改database/health端点返回databases数组
```

### 步骤3: 验证所有修复并启动后端 (5分钟)

```bash
# 1. 验证所有文件语法
python3 -m py_compile \
    web/backend/app/schemas/backtest_schemas.py \
    web/backend/app/core/tdengine_manager.py \
    src/core/data_manager.py \
    src/ml_strategy/price_predictor.py

# 2. 重启后端服务
cd web/backend
pkill -f "uvicorn.*app.main"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/backend_new.log 2>&1 &

# 3. 等待服务启动
sleep 10

# 4. 验证服务运行
curl -s http://localhost:8000/health | jq

# 5. 测试API响应格式
curl -s http://localhost:8000/api/system/database/health | jq '.databases'
```

---

## 📊 修复后预期结果

| 文件 | 问题 | 状态 | 验证命令 |
|------|------|------|---------|
| backtest_schemas.py | ModuleNotFoundError | ✅ | `python3 -c "from app.schemas.backtest_schemas import BacktestRequest"` |
| tdengine_manager.py | IndentationError | ✅ | `python3 -m py_compile web/backend/app/core/tdengine_manager.py` |
| data_manager.py | SyntaxError | ✅ | `python3 -m py_compile src/core/data_manager.py` |
| price_predictor.py | IndentationError | ✅ | `python3 -m py_compile src/ml_strategy/price_predictor.py` |
| system.py | API响应格式 | ✅ | `curl /api/system/database/health \| jq '.databases'` |

---

## ⏱️ 时间估算

- **方案A (Git恢复)**: 2分钟修复 + 5分钟验证 = **7分钟** ⭐ 推荐
- **方案B (手动修正)**: 5分钟修复 + 5分钟验证 = **10分钟**
- **方案C (AST自动)**: 不确定，可能需要调试

---

## 💡 为什么推荐Git恢复

1. ✅ **最安全**: 恢复到已知工作版本
2. ✅ **最快速**: 2分钟完成
3. ✅ **无风险**: 不引入新的错误
4. ✅ **保留功能**: 原始版本包含`self.logger.info`调用

---

## ⚠️ 不建议的做法

❌ **继续手动调整缩进**
- 时间消耗大（可能需要多次尝试）
- 容易引入新的缩进错误
- 不确定原始代码的正确结构

❌ **跳过这个文件**
- price_predictor.py被其他模块导入
- 语法错误会导致整个应用无法启动
- E2E测试无法运行

---

## 📞 需要帮助？

如果Git恢复后仍有问题，请运行以下诊断命令：

```bash
# 检查文件具体行
sed -n '428,436p' src/ml_strategy/price_predictor.py | cat -A

# 检查Python解析错误详情
python3 -c "
import ast
with open('src/ml_strategy/price_predictor.py', 'r') as f:
    try:
        ast.parse(f.read())
    except SyntaxError as e:
        print(f'Line {e.lineno}: {e.msg}')
        print(f'Text: {e.text}')
"
```

---

**请立即执行方案A (Git恢复)，然后继续修复其他4个问题。**

**预计总时间**: 15分钟内完成所有5个问题修复，后端服务可以启动。

---

*文档生成: 2025-12-28 T+4.5h*
*预计完成: 2025-12-28 T+5h (15分钟后)*
