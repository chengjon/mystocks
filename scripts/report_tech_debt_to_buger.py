#!/usr/bin/env python3
"""
上报技术债务BUG到BUGer系统

将MyStocks项目的技术债务问题批量上报到BUGer知识库
"""

import os
import requests
import json
from datetime import datetime, timezone
from typing import Dict, List

# BUGer配置
BUGER_API_URL = "http://localhost:3030/api"
BUGER_API_KEY = "sk_mystocks_2025"  # 需要从BUGer管理员获取
PROJECT_ID = "mystocks"
PROJECT_NAME = "MyStocks"
PROJECT_ROOT = "/opt/claude/mystocks_spec"


def report_bug(bug_data: Dict) -> Dict:
    """上报单个BUG到BUGer"""
    payload = {
        "errorCode": bug_data['errorCode'],
        "title": bug_data['title'],
        "message": bug_data['message'],
        "severity": bug_data.get('severity', 'medium'),
        "context": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "project": PROJECT_ID,
            "project_name": PROJECT_NAME,
            "project_root": PROJECT_ROOT,
            "component": bug_data.get('component', 'backend'),
            "module": bug_data.get('module', ''),
            "file": bug_data.get('file', ''),
            "fix": bug_data.get('fix', ''),
            "status": bug_data.get('status', 'OPEN')
        }
    }

    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': BUGER_API_KEY
    }

    try:
        response = requests.post(
            f'{BUGER_API_URL}/bugs',
            json=payload,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
        print(f"✓ BUG已上报: {result.get('data', {}).get('bugId', 'unknown')}")
        return result
    except requests.exceptions.RequestException as e:
        print(f"✗ BUG上报失败: {e}")
        return {"success": False, "error": str(e)}


def report_bugs_batch(bugs: List[Dict]) -> Dict:
    """批量上报BUG"""
    formatted_bugs = []
    for bug in bugs:
        formatted_bugs.append({
            "errorCode": bug['errorCode'],
            "title": bug['title'],
            "message": bug['message'],
            "severity": bug.get('severity', 'medium'),
            "context": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "project": PROJECT_ID,
                "project_name": PROJECT_NAME,
                "project_root": PROJECT_ROOT,
                "component": bug.get('component', 'backend'),
                "module": bug.get('module', ''),
                "file": bug.get('file', ''),
                "fix": bug.get('fix', ''),
                "status": bug.get('status', 'OPEN')
            }
        })

    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': BUGER_API_KEY
    }

    try:
        response = requests.post(
            f'{BUGER_API_URL}/bugs/batch',
            json={'bugs': formatted_bugs},
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        print(f"✓ 批量上报成功: {result.get('data', {}).get('summary', {})}")
        return result
    except requests.exceptions.RequestException as e:
        print(f"✗ 批量上报失败: {e}")
        return {"success": False, "error": str(e)}


def main():
    """上报技术债务BUG"""
    print("=" * 60)
    print("MyStocks 技术债务BUG上报到BUGer系统")
    print("=" * 60)
    print(f"BUGer API: {BUGER_API_URL}")
    print(f"项目: {PROJECT_NAME} ({PROJECT_ID})")
    print("=" * 60)

    # 定义技术债务BUG列表
    tech_debt_bugs = [
        # 类型注解问题
        {
            "errorCode": "TYPE_001",
            "title": "unified_manager.py类型注解错误",
            "message": "unified_manager.py存在7个MyPy类型错误：\n1. 监控组件(monitoring_db, performance_monitor等)未正确处理Optional类型\n2. 调用Optional对象方法前未进行None检查\n3. 包括track_operation、get_performance_summary、check_completeness等方法调用",
            "severity": "medium",
            "component": "backend",
            "module": "core",
            "file": "src/core/unified_manager.py",
            "fix": "需要在调用Optional组件方法前添加None检查，或使用类型守卫",
            "status": "OPEN"
        },
        {
            "errorCode": "TYPE_002",
            "title": "DataClassification枚举值不匹配",
            "message": "unified_manager.py中引用了不存在的DataClassification枚举值，已修复为正确的值：\n- REALTIME_DATA -> ORDER_BOOK_DEPTH\n- WEEKLY_KLINE -> FUNDAMENTAL_METRICS\n- INDEX_COMPONENTS -> INDEX_CONSTITUENTS等",
            "severity": "medium",
            "component": "backend",
            "module": "core",
            "file": "src/core/unified_manager.py",
            "fix": "已修复枚举值引用，与data_classification.py中的定义保持一致",
            "status": "FIXED"
        },
        # 代码规范问题
        {
            "errorCode": "CODE_001",
            "title": "bare except语句需要改进",
            "message": "代码库中存在约10个bare except语句，应改为except Exception:\n主要分布在:\n- src/gpu/api_system/utils/gpu_utils.py\n- src/utils/check_api_health_v2.py\n- src/utils/data_format_converter.py等",
            "severity": "low",
            "component": "backend",
            "module": "utils",
            "file": "src/",
            "fix": "将bare except:改为except Exception:以避免捕获SystemExit等系统异常",
            "status": "IN_PROGRESS"
        },
        # 已修复的问题记录
        {
            "errorCode": "TYPE_003",
            "title": "exceptions.py类型注解缺失",
            "message": "src/core/exceptions.py缺少完整类型注解：\n- 未导入Optional, List, Dict, Any\n- 默认参数使用None但类型未声明Optional\n- 返回值类型未标注",
            "severity": "medium",
            "component": "backend",
            "module": "core",
            "file": "src/core/exceptions.py",
            "fix": "已添加from typing import Any, Dict, List, Optional，所有参数和返回值类型已正确标注",
            "status": "FIXED"
        },
        {
            "errorCode": "TYPE_004",
            "title": "batch_failure_strategy.py Optional类型问题",
            "message": "BatchOperationResult dataclass中failed_indices和error_messages字段类型问题：\n- 类型声明为List[int]和Dict[int, str]\n- 但默认值为None",
            "severity": "medium",
            "component": "backend",
            "module": "core",
            "file": "src/core/batch_failure_strategy.py",
            "fix": "已修改为Optional[List[int]]和Optional[Dict[int, str]]，并在to_dict()方法中添加None检查",
            "status": "FIXED"
        },
        {
            "errorCode": "TYPE_005",
            "title": "classification_root.py类型注解问题 (文件已删除)",
            "message": "原classification_root.py已被删除，DeduplicationStrategy枚举已整合到data_classification.py",
            "severity": "medium",
            "component": "backend",
            "module": "core",
            "file": "src/core/data_classification.py",
            "fix": "文件已删除，功能整合到data_classification.py中",
            "status": "RESOLVED"
        },
        {
            "errorCode": "TYPE_006",
            "title": "config_driven_table_manager.py类型和变量错误",
            "message": "存在9个类型错误:\n1. load_config返回Any而非Dict[str, Any]\n2. result字典缺少类型注解\n3. _table_exists返回Any而非bool\n4. 第429行引用未定义变量e",
            "severity": "medium",
            "component": "backend",
            "module": "core",
            "file": "src/core/config_driven_table_manager.py",
            "fix": "已修复所有问题：添加dict()转换、显式类型注解、bool()转换、移除错误变量引用",
            "status": "FIXED"
        },
        # 测试覆盖率问题
        {
            "errorCode": "TEST_001",
            "title": "测试覆盖率不足",
            "message": "当前测试覆盖率仅15-20%，目标80%。主要缺失:\n- src/core/ 核心模块单元测试\n- src/adapters/ 适配器集成测试\n- API端点测试",
            "severity": "high",
            "component": "backend",
            "module": "tests",
            "file": "tests/",
            "fix": "需要编写pytest测试用例，优先覆盖核心业务逻辑",
            "status": "OPEN"
        },
        # TODO注释问题
        {
            "errorCode": "CODE_002",
            "title": "TODO注释需要清理",
            "message": "代码库中存在92个TODO注释，需要评估和处理:\n- 部分为过时的待办事项\n- 部分需要创建正式任务跟踪",
            "severity": "low",
            "component": "backend",
            "module": "general",
            "file": "src/",
            "fix": "需要逐一评估TODO注释，完成或移除过时项，重要项创建任务",
            "status": "OPEN"
        }
    ]

    print(f"\n准备上报 {len(tech_debt_bugs)} 个技术债务BUG...")

    # 批量上报
    result = report_bugs_batch(tech_debt_bugs)

    if result.get('success'):
        summary = result.get('data', {}).get('summary', {})
        print(f"\n✅ 上报完成!")
        print(f"   - 总数: {summary.get('total', len(tech_debt_bugs))}")
        print(f"   - 成功: {summary.get('successful', 0)}")
        print(f"   - 失败: {summary.get('failed', 0)}")
    else:
        print(f"\n❌ 上报失败: {result.get('error', 'Unknown error')}")
        print("\n尝试逐个上报...")
        success_count = 0
        for bug in tech_debt_bugs:
            result = report_bug(bug)
            if result.get('success'):
                success_count += 1
        print(f"\n逐个上报完成: {success_count}/{len(tech_debt_bugs)} 成功")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
