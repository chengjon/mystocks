#!/usr/bin/env python3
"""
TDengine Deployment Verification Script - Task 2.1

This script verifies the TDengine deployment and functionality:
1. Check Docker container status
2. Verify TDengine connectivity
3. Validate database and table creation
4. Test cache operations
5. Verify performance metrics

Run this after: docker-compose -f docker-compose.tdengine.yml up -d
"""

import os
import sys
import subprocess
import time
from datetime import datetime
from pathlib import Path

# Add project root directory to path (3 levels up: scripts/database/verify_tdengine_deployment.py)
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)

# Load .env file
env_file = Path(project_root) / ".env"
if env_file.exists():
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                os.environ.setdefault(key, value)

# Set default environment variables if not set by .env
os.environ.setdefault("TDENGINE_HOST", "127.0.0.1")
os.environ.setdefault("TDENGINE_PORT", "6030")
os.environ.setdefault("TDENGINE_USER", "root")
os.environ.setdefault("TDENGINE_PASSWORD", "taosdata")


class TDengineDeploymentVerifier:
    """Verify TDengine deployment and functionality"""

    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = 0

    def print_header(self, text):
        """Print section header"""
        print(f"\n{'=' * 70}")
        print(f"  {text}")
        print(f"{'=' * 70}")

    def print_check(self, status, message, detail=""):
        """Print check result"""
        symbols = {"✅": "✅", "❌": "❌", "⚠️": "⚠️"}
        status_symbol = symbols.get(status, status)
        print(f"{status_symbol} {message}")
        if detail:
            print(f"   → {detail}")

    def check_docker_installed(self):
        """Check if Docker is installed"""
        self.print_header("1. Checking Docker Installation")

        try:
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True
            )
            if result.returncode == 0:
                self.print_check("✅", "Docker installed", result.stdout.strip())
                self.checks_passed += 1
                return True
            else:
                self.print_check("❌", "Docker not found")
                self.checks_failed += 1
                return False
        except FileNotFoundError:
            self.print_check("❌", "Docker command not found")
            self.checks_failed += 1
            return False

    def check_docker_compose(self):
        """Check if Docker Compose is installed"""
        try:
            result = subprocess.run(
                ["docker-compose", "--version"], capture_output=True, text=True
            )
            if result.returncode == 0:
                self.print_check(
                    "✅", "Docker Compose installed", result.stdout.strip()
                )
                self.checks_passed += 1
                return True
            else:
                self.print_check("❌", "Docker Compose not found")
                self.checks_failed += 1
                return False
        except FileNotFoundError:
            self.print_check("❌", "Docker Compose command not found")
            self.checks_failed += 1
            return False

    def check_docker_running(self):
        """Check if Docker daemon is running"""
        try:
            result = subprocess.run(["docker", "info"], capture_output=True, text=True)
            if result.returncode == 0:
                self.print_check("✅", "Docker daemon is running")
                self.checks_passed += 1
                return True
            else:
                self.print_check("❌", "Docker daemon is not running")
                self.checks_failed += 1
                return False
        except Exception as e:
            self.print_check("❌", "Cannot communicate with Docker", str(e))
            self.checks_failed += 1
            return False

    def check_tdengine_container(self):
        """Check if TDengine container is running"""
        self.print_header("2. Checking TDengine Container")

        try:
            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "--filter",
                    "name=mystocks_tdengine",
                    "--format",
                    "{{.Status}}",
                ],
                capture_output=True,
                text=True,
            )

            if "Up" in result.stdout:
                self.print_check(
                    "✅", "TDengine container is running", result.stdout.strip()
                )
                self.checks_passed += 1
                return True
            else:
                self.print_check("❌", "TDengine container is not running")
                self.checks_failed += 1
                return False

        except Exception as e:
            self.print_check("❌", "Cannot check container status", str(e))
            self.checks_failed += 1
            return False

    def check_postgresql_container(self):
        """Check if PostgreSQL container is running"""
        try:
            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "--filter",
                    "name=mystocks_postgres",
                    "--format",
                    "{{.Status}}",
                ],
                capture_output=True,
                text=True,
            )

            if "Up" in result.stdout:
                self.print_check(
                    "✅", "PostgreSQL container is running", result.stdout.strip()
                )
                self.checks_passed += 1
                return True
            else:
                self.print_check(
                    "⚠️",
                    "PostgreSQL container is not running (may not be needed for this test)",
                )
                self.warnings += 1
                return False

        except Exception as e:
            self.print_check("⚠️", "Cannot check PostgreSQL status", str(e))
            self.warnings += 1
            return False

    def check_tdengine_connectivity(self):
        """Check TDengine connectivity"""
        self.print_header("3. Checking TDengine Connectivity")

        try:
            from taos import connect
            from taos.error import ProgrammingError

            try:
                conn = connect(
                    host=os.getenv("TDENGINE_HOST"),
                    port=int(os.getenv("TDENGINE_PORT")),
                    user=os.getenv("TDENGINE_USER"),
                    password=os.getenv("TDENGINE_PASSWORD"),
                )
                self.print_check("✅", "TDengine connection successful")
                conn.close()
                self.checks_passed += 1
                return True

            except ProgrammingError as e:
                self.print_check("❌", "TDengine authentication failed", str(e))
                self.checks_failed += 1
                return False

        except ImportError:
            self.print_check("❌", "taospy module not installed")
            self.print_check("⚠️", "Run: pip install taospy", "")
            self.checks_failed += 1
            return False

        except Exception as e:
            self.print_check("❌", "Cannot connect to TDengine", str(e))
            self.checks_failed += 1
            return False

    def check_tdengine_manager(self):
        """Check TDengineManager functionality"""
        self.print_header("4. Checking TDengineManager")

        try:
            from web.backend.app.core.tdengine_manager import TDengineManager

            manager = TDengineManager()

            # Check connection
            if not manager.connect():
                self.print_check("❌", "TDengineManager connection failed")
                self.checks_failed += 1
                return False

            self.print_check("✅", "TDengineManager connection successful")
            self.checks_passed += 1

            # Check health
            if manager.health_check():
                self.print_check("✅", "TDengineManager health check passed")
                self.checks_passed += 1
            else:
                self.print_check("❌", "TDengineManager health check failed")
                self.checks_failed += 1

            manager.close()
            return True

        except ImportError as e:
            self.print_check("❌", "Cannot import TDengineManager", str(e))
            self.checks_failed += 1
            return False

        except Exception as e:
            self.print_check("❌", "TDengineManager error", str(e))
            self.checks_failed += 1
            return False

    def check_database_initialization(self):
        """Check database and table initialization"""
        self.print_header("5. Checking Database Initialization")

        try:
            from web.backend.app.core.tdengine_manager import TDengineManager

            manager = TDengineManager()

            if not manager.initialize():
                self.print_check("❌", "Database initialization failed")
                self.checks_failed += 1
                return False

            self.print_check("✅", "Database initialization successful")
            self.checks_passed += 1

            # Check if tables exist
            tables = ["market_data_cache", "cache_stats", "hot_symbols"]
            for table in tables:
                try:
                    result = manager._execute_query(
                        f"SELECT COUNT(*) FROM {table} LIMIT 1"
                    )
                    self.print_check("✅", f"Table '{table}' exists and accessible")
                    self.checks_passed += 1
                except Exception as e:
                    self.print_check("❌", f"Table '{table}' not accessible", str(e))
                    self.checks_failed += 1

            manager.close()
            return True

        except Exception as e:
            self.print_check("❌", "Database initialization check failed", str(e))
            self.checks_failed += 1
            return False

    def check_cache_operations(self):
        """Test cache read/write operations"""
        self.print_header("6. Testing Cache Read/Write Operations")

        try:
            from web.backend.app.core.tdengine_manager import TDengineManager

            manager = TDengineManager()

            if not manager.initialize():
                self.print_check("❌", "Cannot initialize manager")
                self.checks_failed += 1
                return False

            # Test write
            test_data = {
                "main_net_inflow": 1000000,
                "main_percent": 2.5,
                "retail_net_inflow": 500000,
            }

            write_result = manager.write_cache(
                symbol="000001", data_type="fund_flow", timeframe="1d", data=test_data
            )

            if write_result:
                self.print_check("✅", "Cache write operation successful")
                self.checks_passed += 1
            else:
                self.print_check("❌", "Cache write operation failed")
                self.checks_failed += 1
                manager.close()
                return False

            # Test read
            read_result = manager.read_cache(symbol="000001", data_type="fund_flow")

            if read_result:
                self.print_check("✅", "Cache read operation successful")
                self.print_check("✅", "Cache data retrieved", str(read_result))
                self.checks_passed += 1
            else:
                self.print_check("❌", "Cache read operation failed")
                self.checks_failed += 1
                manager.close()
                return False

            # Test stats
            stats = manager.get_cache_stats()
            if stats:
                self.print_check(
                    "✅", "Cache statistics retrieval successful", str(stats)
                )
                self.checks_passed += 1
            else:
                self.print_check("⚠️", "Cache statistics unavailable (may be empty)")
                self.warnings += 1

            manager.close()
            return True

        except Exception as e:
            self.print_check("❌", "Cache operations test failed", str(e))
            import traceback

            traceback.print_exc()
            self.checks_failed += 1
            return False

    def run_all_checks(self):
        """Run all verification checks"""
        print("\n" + "=" * 70)
        print("  TDengine Deployment Verification - Task 2.1")
        print("=" * 70)
        print(f"  Start Time: {datetime.now().isoformat()}")
        print(f"  TDengine Host: {os.getenv('TDENGINE_HOST')}")
        print(f"  TDengine Port: {os.getenv('TDENGINE_PORT')}")

        # Docker checks
        self.check_docker_installed()
        self.check_docker_compose()
        self.check_docker_running()

        # Container checks
        self.check_tdengine_container()
        self.check_postgresql_container()

        # Functionality checks
        self.check_tdengine_connectivity()
        self.check_tdengine_manager()
        self.check_database_initialization()
        self.check_cache_operations()

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print verification summary"""
        self.print_header("Verification Summary")

        total = self.checks_passed + self.checks_failed
        print(f"\n  ✅ Passed:  {self.checks_passed}/{total}")
        print(f"  ❌ Failed:  {self.checks_failed}/{total}")
        print(f"  ⚠️  Warnings: {self.warnings}")

        if self.checks_failed == 0:
            print("\n  🎉 All checks passed! TDengine is ready for use.")
            print("\n  Next Steps:")
            print(
                "  1. Run integration tests: pytest web/backend/tests/test_tdengine_manager.py -v"
            )
            print("  2. Start the backend service: python -m web.backend.main")
            print("  3. Monitor cache statistics: python monitor_cache_stats.py")
        else:
            print(
                f"\n  ⚠️  {self.checks_failed} check(s) failed. Please review the issues above."
            )
            print("\n  Troubleshooting:")
            print("  1. Ensure TDengine container is running:")
            print("     docker-compose -f docker-compose.tdengine.yml up -d")
            print(
                "  2. Check Docker logs: docker-compose -f docker-compose.tdengine.yml logs tdengine"
            )
            print("  3. Verify credentials in .env file")

        print(f"\n  End Time: {datetime.now().isoformat()}\n")

        return self.checks_failed == 0


if __name__ == "__main__":
    verifier = TDengineDeploymentVerifier()
    success = verifier.run_all_checks()
    sys.exit(0 if success else 1)
