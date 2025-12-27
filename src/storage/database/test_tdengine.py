#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TDengine连接测试脚本
包含条件导入和错误处理机制
"""

import logging
import sys

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TDengineTest")


def test_tdengine_import():
    """测试TDengine导入和连接"""
    print(f"Python版本: {sys.version}")
    print(f"Python可执行文件: {sys.executable}")

    # 尝试多种连接方式，优先WebSocket
    connection_methods = [
        ("taosws", "WebSocket方式 (推荐)"),
        ("taosrest", "REST API方式"),
        ("taos", "原生C库方式"),
    ]

    for module_name, description in connection_methods:
        try:
            module = __import__(module_name)
            logger.info(f"✓ TDengine Python库导入成功 ({description})")
            logger.info(f"TDengine客户端版本: {getattr(module, '__version__', '未知版本')}")
            return module, module_name
        except ImportError:
            logger.debug(f"未找到{module_name}模块")
            continue
        except Exception as e:
            logger.error(f"✗ {module_name}客户端库加载失败: {e}")
            continue

    logger.error("✗ 所有TDengine Python库导入失败")
    logger.error("原因: 未安装任何TDengine Python库")
    return None, None


def test_tdengine_connection(taos_module, module_name):
    """测试TDengine数据库连接"""
    if taos_module is None:
        return False

    try:
        logger.info(f"正在连接TDengine数据库... ({module_name}方式)")

        # 从环境变量获取TDengine连接参数
        import os
        from dotenv import load_dotenv

        # 加载环境变量
        env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
        load_dotenv(env_path)

        tdengine_host = os.getenv("TDENGINE_HOST")
        tdengine_user = os.getenv("TDENGINE_USER", "root")
        tdengine_password = os.getenv("TDENGINE_PASSWORD", "taosdata")
        tdengine_port = int(os.getenv("TDENGINE_PORT", "6041"))

        if not tdengine_host:
            logger.error("TDengine连接参数不完整，请检查.env文件")
            return False

        # 根据不同模块使用不同连接方式
        if module_name == "taosws":
            # WebSocket连接方式
            dsn = f"ws://{tdengine_user}:{tdengine_password}@{tdengine_host}:{tdengine_port}"
            conn = taos_module.connect(dsn)
        elif module_name == "taosrest":
            # REST API连接方式
            conn = taos_module.connect(
                url=f"http://{tdengine_host}:{tdengine_port}",
                user=tdengine_user,
                password=tdengine_password,
            )
        else:
            # 原生连接方式 (使用默认端口6030)
            native_port = int(os.getenv("TDENGINE_PORT", "6030"))
            conn = taos_module.connect(
                host=tdengine_host,
                user=tdengine_user,
                password=tdengine_password,
                port=native_port,
            )

        logger.info("✓ TDengine数据库连接成功")

        cursor = conn.cursor()

        # 执行测试SQL
        test_operations = [
            ("删除数据库", "drop database if exists db"),
            ("创建数据库", "create database if not exists db"),
            (
                "创建表",
                "create table db.tb(ts timestamp, n int, bin binary(10), nc nchar(10))",
            ),
            ("插入数据1", "insert into db.tb values (1650000000000, 1, 'abc', '北京')"),
            ("插入数据2", "insert into db.tb values (1650000000001, null, null, null)"),
        ]

        for operation, sql in test_operations:
            logger.info(f"执行: {operation}")
            cursor.execute(sql)

        # 查询数据
        logger.info("查询数据:")
        sql = "select * from db.tb"
        cursor.execute(sql)

        # 不同模块的结果获取方式不同
        if module_name == "taosrest":
            # REST API方式需要使用fetchall()获取结果
            results = cursor.fetchall()
            for row in results:
                print(f"数据行: {row}")
        else:
            # WebSocket和原生方式支持直接迭代
            for row in cursor:
                print(f"数据行: {row}")

        conn.close()
        logger.info("✓ 所有测试操作完成，连接已关闭")
        return True

    except Exception as e:
        logger.error(f"✗ 数据库操作失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("TDengine连接测试")
    print("=" * 60)

    # 测试导入
    taos, module_name = test_tdengine_import()

    if taos is None:
        print("\n" + "=" * 60)
        print("诊断信息:")
        print(f"- 当前Python版本: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        print(f"- Python可执行文件: {sys.executable}")
        print("\n解决方案:")
        print("1. 下载并安装TDengine客户端:")
        print("   https://docs.taosdata.com/get-started/")
        print("2. 下载安装TDengine-client:")
        print("   https://www.taosdata.com/assets-download/3.0/TDengine-client-3.3.6.13-Windows-x64.exe")
        print("3. 在当前Python环境中安装Python库 (推荐WebSocket方式):")
        print(f'   "{sys.executable}" -m pip install taos-ws-py')
        print("   或者使用原生连接方式:")
        print(f'   "{sys.executable}" -m pip install taospy')
        print("4. 或者使用已安装TDengine的Python环境运行")
        print("5. 确保TDengine服务正在运行")
        print("=" * 60)
        sys.exit(1)

    # 测试连接
    success = test_tdengine_connection(taos, module_name)

    print("\n" + "=" * 60)
    if success:
        print("✓ TDengine测试完成！")
    else:
        print("✗ TDengine测试失败，请检查连接配置")
    print("=" * 60)


if __name__ == "__main__":
    main()
