"""
File-Level API Test Runner

This module provides the main entry point for running file-level API tests.
It orchestrates the testing of multiple API files in parallel and generates
comprehensive reports.

Usage:
    python -m pytest tests/file_level/test_runner.py -v
    python tests/file_level/run_file_tests.py --api-dir web/backend/app/api

Author: MyStocks Testing Team
Date: 2026-01-10
"""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.file_level.core import FileLevelTestRunner, FileTestSuiteResult


async def run_file_tests(
    api_dir: str = "web/backend/app/api",
    output_format: str = "json",
    max_workers: int = 4,
    base_url: str = "http://localhost:8000",
    verbose: bool = False
) -> FileTestSuiteResult:
    """
    Run file-level tests for all API files.

    Args:
        api_dir: Directory containing API files
        output_format: Report output format (json, html, yaml)
        max_workers: Maximum number of parallel workers
        base_url: Base URL of the API to test
        verbose: Enable verbose output

    Returns:
        Complete test suite results
    """
    print("🚀 Starting File-Level API Testing"    print(f"📁 API Directory: {api_dir}")
    print(f"🌐 Base URL: {base_url}")
    print(f"⚡ Max Workers: {max_workers}")
    print(f"📊 Output Format: {output_format}")
    print("-" * 60)

    async with FileLevelTestRunner(
        base_url=base_url,
        max_workers=max_workers
    ) as runner:
        # Run tests
        result = await runner.run_file_tests()

        # Print summary
        print("
📊 Test Results Summary"        print(f"📁 Files Tested: {result.files_tested}")
        print(f"✅ Files Passed: {result.files_passed}")
        print(f"❌ Files Failed: {result.files_failed}")
        print(f"📊 Total Endpoints: {result.total_endpoints}")
        print(f"📈 Success Rate: {result.overall_success_rate:.1f}%")
        print(f"⏱️  Execution Time: {result.total_execution_time:.2f}s")

        if verbose and result.file_results:
            print("
📋 Detailed Results:"            for file_result in result.file_results:
                status_icon = "✅" if file_result.status == "passed" else "❌"
                print(f"  {status_icon} {file_result.file_name}: "
                      f"{file_result.endpoints_passed}/{file_result.endpoints_tested} endpoints "
                      f"({file_result.execution_time:.2f}s)")

        # Save report
        report_path = runner.save_results(result, format=output_format)
        print(f"\n💾 Report saved to: {report_path}")

        return result


def main():
    """Main entry point for file-level testing"""
    parser = argparse.ArgumentParser(
        description="Run file-level API tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --api-dir web/backend/app/api --verbose
  %(prog)s --base-url http://localhost:8001 --format html
  %(prog)s --max-workers 8 --api-dir custom/api/dir
        """
    )

    parser.add_argument(
        "--api-dir",
        default="web/backend/app/api",
        help="Directory containing API files to test"
    )

    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL of the API to test"
    )

    parser.add_argument(
        "--format", "--output-format",
        choices=["json", "html", "yaml"],
        default="json",
        help="Report output format"
    )

    parser.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="Maximum number of parallel test workers"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "--config",
        help="Path to test configuration file"
    )

    args = parser.parse_args()

    # Validate API directory exists
    if not Path(args.api_dir).exists():
        print(f"❌ Error: API directory not found: {args.api_dir}")
        sys.exit(1)

    try:
        # Run tests
        result = asyncio.run(run_file_tests(
            api_dir=args.api_dir,
            output_format=args.format,
            max_workers=args.max_workers,
            base_url=args.base_url,
            verbose=args.verbose
        ))

        # Exit with appropriate code
        if result.files_failed > 0:
            print(f"\n❌ Tests completed with {result.files_failed} failed files")
            sys.exit(1)
        else:
            print("\n✅ All tests passed!"
            sys.exit(0)

    except KeyboardInterrupt:
        print("\n⚠️  Testing interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()</content>
<parameter name="filePath">tests/file_level/test_runner.py