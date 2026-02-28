"""CLI命令行入口"""

import sys
import os

# 确保项目根目录在Python路径中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

import argparse
from src.monitoring.code_inventory.config import ScanConfig
from src.monitoring.code_inventory.scanner import CodeInventoryScanner
from src.monitoring.code_inventory.env_checker import EnvConfigChecker


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description="代码清单扫描工具 - 扫描并登记代码行数超过阈值的文件和Mock使用情况"
    )
    
    parser.add_argument(
        "--scan-dirs", 
        nargs="+",
        default=["src", "scripts", "web/backend/app"],
        help="扫描目录列表"
    )
    parser.add_argument(
        "--extensions", 
        nargs="+",
        default=[".py", ".vue", ".ts", ".tsx", ".js", ".jsx"],
        help="扫描文件扩展名"
    )
    parser.add_argument(
        "--threshold", 
        type=int,
        default=1000,
        help="行数阈值（默认1000）"
    )
    parser.add_argument(
        "--output-dir",
        default="src/monitoring/code_inventory",
        help="输出目录"
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="项目根目录"
    )
    parser.add_argument(
        "--no-validation",
        action="store_true",
        help="跳过REAL模式验证"
    )
    parser.add_argument(
        "--check-mock-only",
        action="store_true",
        help="仅检查Mock使用情况"
    )
    parser.add_argument(
        "--check-env",
        action="store_true",
        help="仅检查环境配置"
    )
    
    args = parser.parse_args()
    
    # 创建配置
    config = ScanConfig(
        scan_dirs=args.scan_dirs,
        file_extensions=args.extensions,
        line_threshold=args.threshold,
        output_dir=args.output_dir,
        project_root=args.project_root
    )
    
    # 创建扫描器
    scanner = CodeInventoryScanner(config)
    
    # 检查环境配置
    if args.check_env:
        checker = EnvConfigChecker()
        env_info = checker.load_env_config(args.project_root)
        current_mode = checker.check_current_mode(args.project_root)
        
        print("=" * 60)
        print("环境配置检查")
        print("=" * 60)
        print(f"  USE_MOCK_DATA: {env_info.use_mock_data}")
        print(f"  DATA_SOURCE: {env_info.data_source}")
        print(f"  当前模式: {current_mode}")
        
        if env_info.issues:
            print("\n问题:")
            for issue in env_info.issues:
                print(f"  - {issue}")
        
        # 执行REAL模式验证
        validation = checker.validate_real_mode(args.project_root)
        print(f"\nREAL模式验证: {'通过' if validation.is_valid else '失败'}")
        
        if not validation.is_valid:
            for v in validation.violations:
                print(f"  [{v['severity']}] {v['message']}")
        
        return
    
    # 仅检查Mock使用
    if args.check_mock_only:
        print("正在检查Mock使用情况...")
        records = scanner.check_mock_usage()
        
        print("=" * 60)
        print(f"使用Mock的文件 (共 {len(records)} 个)")
        print("=" * 60)
        
        for record in records:
            print(f"\n{record.file_path}")
            print(f"  严重性: {record.mock_severity}")
            if record.mock_imports:
                print(f"  Import: {', '.join(record.mock_imports[:3])}")
            if record.mock_calls:
                print(f"  调用: {', '.join(record.mock_calls[:3])}")
        
        return
    
    # 执行完整扫描
    print("开始扫描...")
    print(f"  扫描目录: {', '.join(args.scan_dirs)}")
    print(f"  文件类型: {', '.join(args.extensions)}")
    print(f"  行数阈值: {args.threshold}")
    print()
    
    scanner.scan(validate_real=not args.no_validation)
    
    print(f"\n结果已保存到: {args.output_dir}")


if __name__ == "__main__":
    main()