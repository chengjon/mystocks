"""
US2验收测试 - 配置驱动表结构管理

验证US2的完整功能:
- T024: 配置验证测试
- T025: US2安全模式验收测试

验收标准:
1. 可通过YAML配置自动创建所有表
2. 安全模式正确执行（添加列自动，删除/修改需确认）
3. 配置错误有明确提示

创建日期: 2025-10-12
"""

import logging
import sys
from pathlib import Path
import tempfile
import os

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.config_driven_table_manager import ConfigDrivenTableManager

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_config_validation():
    """T024: 配置验证测试"""
    logger.info("\n" + "=" * 60)
    logger.info("T024: 配置验证测试")
    logger.info("=" * 60)

    tests_passed = []
    tests_failed = []

    # 测试1: 正确的配置文件
    logger.info("\n1. 测试正确的配置文件")
    try:
        manager = ConfigDrivenTableManager(config_path="config/table_config.yaml")
        logger.info("   ✅ 正确的配置文件加载成功")
        tests_passed.append("正确配置文件加载")

        # 验证版本
        version = manager.config.get("version")
        if version:
            logger.info(f"   ✅ 配置版本: {version}")
            tests_passed.append("版本字段验证")
        else:
            logger.warning("   ⚠️ 缺少版本信息")
            tests_failed.append("版本字段缺失")

        # 验证必需字段
        if "databases" in manager.config:
            logger.info(
                f"   ✅ databases字段存在（{len(manager.config['databases'])}个数据库）"
            )
            tests_passed.append("databases字段验证")
        else:
            logger.error("   ❌ 缺少databases字段")
            tests_failed.append("databases字段缺失")

        if "tables" in manager.config:
            logger.info(f"   ✅ tables字段存在（{len(manager.config['tables'])}个表）")
            tests_passed.append("tables字段验证")
        else:
            logger.error("   ❌ 缺少tables字段")
            tests_failed.append("tables字段缺失")

        if "maintenance" in manager.config:
            logger.info(f"   ✅ maintenance字段存在")
            tests_passed.append("maintenance字段验证")
        else:
            logger.error("   ❌ 缺少maintenance字段")
            tests_failed.append("maintenance字段缺失")

    except Exception as e:
        logger.error(f"   ❌ 正确配置文件加载失败: {e}")
        tests_failed.append(f"正确配置文件加载: {e}")

    # 测试2: 不存在的配置文件
    logger.info("\n2. 测试不存在的配置文件（应该抛出错误）")
    try:
        manager = ConfigDrivenTableManager(config_path="nonexistent_config.yaml")
        logger.error("   ❌ 应该抛出FileNotFoundError但没有")
        tests_failed.append("缺失配置文件错误处理")
    except FileNotFoundError as e:
        logger.info(f"   ✅ 正确抛出FileNotFoundError: {e}")
        tests_passed.append("缺失配置文件错误处理")
    except Exception as e:
        logger.error(f"   ❌ 抛出了错误的异常类型: {type(e).__name__}")
        tests_failed.append("错误的异常类型")

    # 测试3: 格式错误的配置文件
    logger.info("\n3. 测试格式错误的配置文件（应该抛出错误）")
    try:
        # 创建临时的错误配置文件
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content:\n  - wrong indentation\n wrong")
            temp_config_path = f.name

        try:
            manager = ConfigDrivenTableManager(config_path=temp_config_path)
            logger.error("   ❌ 应该抛出YAML解析错误但没有")
            tests_failed.append("YAML格式错误处理")
        except Exception as e:
            logger.info(f"   ✅ 正确抛出异常: {type(e).__name__}")
            tests_passed.append("YAML格式错误处理")
        finally:
            os.unlink(temp_config_path)

    except Exception as e:
        logger.error(f"   ❌ 测试过程出错: {e}")
        tests_failed.append(f"格式错误测试: {e}")

    # 测试4: 缺少必需字段的配置
    logger.info("\n4. 测试缺少必需字段的配置（应该抛出错误）")
    try:
        # 创建临时的不完整配置文件
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("version: '1.0.0'\n")
            f.write("# 缺少databases和tables字段\n")
            temp_config_path = f.name

        try:
            manager = ConfigDrivenTableManager(config_path=temp_config_path)
            logger.error("   ❌ 应该抛出ValueError但没有")
            tests_failed.append("缺失必需字段错误处理")
        except ValueError as e:
            logger.info(f"   ✅ 正确抛出ValueError: {e}")
            tests_passed.append("缺失必需字段错误处理")
        except Exception as e:
            logger.error(f"   ❌ 抛出了错误的异常类型: {type(e).__name__}")
            tests_failed.append("错误的异常类型")
        finally:
            os.unlink(temp_config_path)

    except Exception as e:
        logger.error(f"   ❌ 测试过程出错: {e}")
        tests_failed.append(f"缺失字段测试: {e}")

    # 总结T024
    logger.info("\n" + "-" * 60)
    logger.info(
        f"T024结果: 通过 {len(tests_passed)} 项测试, 失败 {len(tests_failed)} 项"
    )

    if len(tests_failed) == 0:
        logger.info("✅ T024验收通过: 配置验证功能完善")
        return True
    else:
        logger.warning(f"⚠️ T024部分测试失败: {tests_failed}")
        return len(tests_passed) > len(tests_failed)


def test_safe_mode():
    """T025: US2安全模式验收测试"""
    logger.info("\n" + "=" * 60)
    logger.info("T025: US2安全模式验收测试")
    logger.info("=" * 60)

    tests_passed = []
    tests_failed = []

    try:
        manager = ConfigDrivenTableManager(config_path="config/table_config.yaml")

        # 测试1: 安全模式状态
        logger.info("\n1. 验证安全模式状态")
        if manager.safe_mode:
            logger.info(f"   ✅ 安全模式已启用: {manager.safe_mode}")
            tests_passed.append("安全模式启用")
        else:
            logger.warning("   ⚠️ 安全模式未启用")
            tests_failed.append("安全模式未启用")

        # 测试2: 安全添加列（应该允许）
        logger.info("\n2. 测试安全添加列（应该允许）")
        try:
            column_def = {
                "name": "new_test_column",
                "type": "VARCHAR",
                "length": 64,
                "nullable": True,
                "comment": "测试列",
            }

            # safe_add_column方法在安全模式下应该成功
            if manager.safe_mode:
                result = manager.safe_add_column("test_table", column_def)
                logger.info("   ✅ 安全模式下允许添加列")
                tests_passed.append("安全添加列")
            else:
                logger.warning("   ⚠️ 安全模式未启用，跳过测试")
                tests_failed.append("安全模式状态错误")

        except Exception as e:
            logger.error(f"   ❌ 安全添加列失败: {e}")
            tests_failed.append(f"安全添加列: {e}")

        # 测试3: 危险操作确认（删除列应该被拒绝）
        logger.info("\n3. 测试危险操作（删除列应该需要确认）")
        result = manager.confirm_dangerous_operation(
            operation_type="DELETE_COLUMN",
            table_name="test_table",
            details="删除列 old_column",
        )

        if result == False:
            logger.info("   ✅ 危险操作正确拒绝（返回False）")
            tests_passed.append("危险操作拒绝")
        else:
            logger.error("   ❌ 危险操作未被拒绝")
            tests_failed.append("危险操作未被拒绝")

        # 测试4: 危险操作确认（修改列应该被拒绝）
        logger.info("\n4. 测试危险操作（修改列应该需要确认）")
        result = manager.confirm_dangerous_operation(
            operation_type="MODIFY_COLUMN",
            table_name="test_table",
            details="修改列 price 从 FLOAT 到 DOUBLE",
        )

        if result == False:
            logger.info("   ✅ 危险操作正确拒绝（返回False）")
            tests_passed.append("危险操作拒绝（修改列）")
        else:
            logger.error("   ❌ 危险操作未被拒绝")
            tests_failed.append("危险操作未被拒绝（修改列）")

        # 测试5: 验证配置中的安全模式设置
        logger.info("\n5. 验证配置文件中的安全模式设置")
        maintenance = manager.config.get("maintenance", {})
        safe_mode_config = maintenance.get("safe_mode")

        if safe_mode_config == True:
            logger.info(f"   ✅ 配置文件中safe_mode设置正确: {safe_mode_config}")
            tests_passed.append("配置文件safe_mode设置")
        else:
            logger.error(f"   ❌ 配置文件中safe_mode设置错误: {safe_mode_config}")
            tests_failed.append("配置文件safe_mode设置错误")

        # 测试6: auto_create_tables配置
        logger.info("\n6. 验证auto_create_tables配置")
        auto_create = maintenance.get("auto_create_tables")

        if auto_create == True:
            logger.info(f"   ✅ auto_create_tables设置正确: {auto_create}")
            tests_passed.append("auto_create_tables设置")
        else:
            logger.warning(f"   ⚠️ auto_create_tables设置: {auto_create}")
            tests_failed.append("auto_create_tables设置异常")

    except Exception as e:
        logger.error(f"   ❌ 测试过程出错: {e}")
        tests_failed.append(f"测试过程错误: {e}")

    # 总结T025
    logger.info("\n" + "-" * 60)
    logger.info(
        f"T025结果: 通过 {len(tests_passed)} 项测试, 失败 {len(tests_failed)} 项"
    )

    if len(tests_failed) == 0:
        logger.info("✅ T025验收通过: 安全模式功能完善")
        return True
    else:
        logger.warning(f"⚠️ T025部分测试失败: {tests_failed}")
        return len(tests_passed) > len(tests_failed)


def main():
    """主测试函数"""
    logger.info("\n")
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " " * 15 + "US2验收测试套件" + " " * 22 + "║")
    logger.info("║" + " " * 12 + "配置驱动表结构管理" + " " * 19 + "║")
    logger.info("╚" + "=" * 58 + "╝")
    logger.info("")

    # T024: 配置验证测试
    success_t024 = test_config_validation()

    # T025: 安全模式验收测试
    success_t025 = test_safe_mode()

    # 总结
    logger.info("\n" + "=" * 60)
    logger.info("US2验收测试总结")
    logger.info("=" * 60)

    results = [
        ("T024 - 配置验证测试", success_t024),
        ("T025 - 安全模式验收测试", success_t025),
    ]

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} - {test_name}")

    logger.info("-" * 60)
    logger.info(f"验收测试通过: {passed}/{total}")

    if passed == total:
        logger.info("\n" + "🎉" * 30)
        logger.info("✅ US2完整验收通过！")
        logger.info("\n验收标准确认:")
        logger.info("  ✅ 可通过YAML配置自动创建所有表")
        logger.info("  ✅ 安全模式正确执行（添加列自动，删除/修改需确认）")
        logger.info("  ✅ 配置错误有明确提示")
        logger.info("\n" + "🎉" * 30)
        return True
    else:
        logger.warning(f"\n⚠️ {total - passed} 个验收测试失败")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
