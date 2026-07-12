#!/usr/bin/env python3
"""MyStocks AI自动化现状分析脚本
第一阶段：全面评估现有AI基础设施
"""

import json
import logging
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List

import psutil


# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class AIAutomationAnalyzer:
    """AI自动化现状分析器"""

    def __init__(self, project_root: str = "/opt/claude/mystocks_spec"):
        self.project_root = Path(project_root)
        self.analysis_results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "project_root": str(self.project_root),
            "system_status": {},
            "ai_infrastructure": {},
            "performance_metrics": {},
            "automation_capabilities": {},
            "recommendations": [],
        }

    def analyze_system_status(self) -> Dict[str, Any]:
        """分析系统状态"""
        logger.info("🔍 分析系统状态...")

        status = {
            "cpu_info": {
                "cores": psutil.cpu_count(),
                "usage_percent": psutil.cpu_percent(interval=1),
                "load_average": os.getloadavg() if hasattr(os, "getloadavg") else None,
            },
            "memory_info": {
                "total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
                "usage_percent": psutil.virtual_memory().percent,
            },
            "disk_info": {
                "total_gb": round(
                    psutil.disk_usage(self.project_root).total / (1024**3),
                    2,
                ),
                "free_gb": round(
                    psutil.disk_usage(self.project_root).free / (1024**3),
                    2,
                ),
                "usage_percent": round(
                    (psutil.disk_usage(self.project_root).used / psutil.disk_usage(self.project_root).total) * 100,
                    2,
                ),
            },
            "gpu_info": self._check_gpu_status(),
            "database_status": self._check_database_status(),
        }

        self.analysis_results["system_status"] = status
        return status

    def _check_gpu_status(self) -> Dict[str, Any]:
        """检查GPU状态"""
        try:
            import GPUtil

            gpus = GPUtil.getGPUs()
            gpu_info = []
            for gpu in gpus:
                gpu_info.append(
                    {
                        "name": gpu.name,
                        "memory_total": gpu.memoryTotal,
                        "memory_used": gpu.memoryUsed,
                        "memory_util": gpu.memoryUtil * 100,
                        "temperature": gpu.temperature,
                        "load": gpu.load * 100,
                    },
                )
            return {"available": True, "gpus": gpu_info}
        except ImportError:
            return {"available": False, "error": "GPUtil not installed"}
        except Exception as e:
            return {"available": False, "error": str(e)}

    def _check_database_status(self) -> Dict[str, Any]:
        """检查数据库连接状态"""
        db_status = {"postgresql": False, "tdengine": False}

        # 检查PostgreSQL
        try:
            result = subprocess.run(["which", "psql"], capture_output=True, text=True)
            if result.returncode == 0:
                db_status["postgresql"] = True
                db_status["postgresql_path"] = result.stdout.strip()
        except:
            pass

        # 检查TDengine
        try:
            result = subprocess.run(["which", "taos"], capture_output=True, text=True)
            if result.returncode == 0:
                db_status["tdengine"] = True
                db_status["tdengine_path"] = result.stdout.strip()
        except:
            pass

        return db_status

    def analyze_ai_infrastructure(self) -> Dict[str, Any]:
        """分析AI基础设施"""
        logger.info("🧠 分析AI基础设施...")

        ai_infra = {
            "gpu_api_system": self._check_gpu_api_system(),
            "ml_services": self._check_ml_services(),
            "data_sources": self._check_data_sources(),
            "api_endpoints": self._check_api_endpoints(),
            "monitoring_systems": self._check_monitoring_systems(),
        }

        self.analysis_results["ai_infrastructure"] = ai_infra
        return ai_infra

    def _check_gpu_api_system(self) -> Dict[str, Any]:
        """检查GPU API系统"""
        gpu_api_path = self.project_root / "src/gpu/api_system"

        if not gpu_api_path.exists():
            return {"exists": False, "path": str(gpu_api_path)}

        # 检查关键文件
        key_files = [
            "main_server.py",
            "services/gpu_api_server.py",
            "services/integrated_ml_service.py",
            "utils/gpu_utils.py",
            "PROJECT_SUMMARY.md",
        ]

        files_found = {}
        for file in key_files:
            file_path = gpu_api_path / file
            files_found[file] = file_path.exists()

        # 计算代码行数
        try:
            total_lines = 0
            python_files = list(gpu_api_path.rglob("*.py"))
            for py_file in python_files:
                with open(py_file, encoding="utf-8") as f:
                    total_lines += len(f.readlines())

            files_found["total_python_lines"] = total_lines
            files_found["python_file_count"] = len(python_files)
        except:
            files_found["line_count_error"] = "无法计算代码行数"

        return {
            "exists": True,
            "path": str(gpu_api_path),
            "files": files_found,
            "ready": all([files_found.get(f, False) for f in key_files[:4]]),
        }

    def _check_ml_services(self) -> Dict[str, Any]:
        """检查ML服务"""
        ml_path = self.project_root / "src/gpu/api_system/services"

        services = {
            "ml_service": False,
            "backtesting_service": False,
            "real_time_service": False,
        }

        if ml_path.exists():
            service_files = list(ml_path.glob("*_service.py"))
            for service_file in service_files:
                if "ml" in service_file.name.lower():
                    services["ml_service"] = True
                elif "backtest" in service_file.name.lower():
                    services["backtesting_service"] = True
                elif "real" in service_file.name.lower():
                    services["real_time_service"] = True

        return services

    def _check_data_sources(self) -> Dict[str, Any]:
        """检查数据源"""
        adapters_path = self.project_root / "src/adapters"

        data_sources = {
            "akshare": False,
            "tdx": False,
            "financial": False,
            "byapi": False,
            "baostock": False,
            "customer": False,
            "tushare": False,
        }

        if adapters_path.exists():
            adapter_files = list(adapters_path.glob("*_adapter.py"))
            for adapter_file in adapter_files:
                for source in data_sources:
                    if source in adapter_file.name.lower():
                        data_sources[source] = True

        return data_sources

    def _check_api_endpoints(self) -> Dict[str, Any]:
        """检查API端点"""
        api_path = self.project_root / "web/backend/app/api"

        endpoints = {
            "monitoring": False,
            "technical": False,
            "multi_source": False,
            "announcement": False,
        }

        if api_path.exists():
            endpoint_dirs = [d for d in api_path.iterdir() if d.is_dir()]
            for endpoint_dir in endpoint_dirs:
                endpoint_name = endpoint_dir.name
                if endpoint_name in endpoints:
                    endpoints[endpoint_name] = True

        return endpoints

    def _check_monitoring_systems(self) -> Dict[str, Any]:
        """检查监控系统"""
        monitoring_path = self.project_root / "src/monitoring"

        monitoring_components = {
            "performance_monitor": False,
            "data_quality_monitor": False,
            "alert_manager": False,
            "monitoring_database": False,
        }

        if monitoring_path.exists():
            monitor_files = list(monitoring_path.glob("*.py"))
            for monitor_file in monitor_files:
                for component in monitoring_components:
                    if component.replace("_", "") in monitor_file.name.replace("_", ""):
                        monitoring_components[component] = True

        return monitoring_components

    def analyze_performance_metrics(self) -> Dict[str, Any]:
        """分析性能指标"""
        logger.info("📊 分析性能指标...")

        metrics = {
            "code_complexity": self._analyze_code_complexity(),
            "test_coverage": self._analyze_test_coverage(),
            "documentation": self._analyze_documentation(),
        }

        self.analysis_results["performance_metrics"] = metrics
        return metrics

    def _analyze_code_complexity(self) -> Dict[str, Any]:
        """分析代码复杂度"""
        src_path = self.project_root / "src"

        if not src_path.exists():
            return {"error": "src目录不存在"}

        total_lines = 0
        file_count = 0
        language_stats = {}

        for file_path in src_path.rglob("*"):
            if file_path.is_file():
                ext = file_path.suffix
                try:
                    with open(file_path, encoding="utf-8") as f:
                        lines = len(f.readlines())
                        total_lines += lines
                        file_count += 1

                        if ext not in language_stats:
                            language_stats[ext] = {"files": 0, "lines": 0}
                        language_stats[ext]["files"] += 1
                        language_stats[ext]["lines"] += lines
                except:
                    continue

        return {
            "total_lines": total_lines,
            "total_files": file_count,
            "languages": language_stats,
        }

    def _analyze_test_coverage(self) -> Dict[str, Any]:
        """分析测试覆盖率"""
        tests_path = self.project_root / "tests"

        if not tests_path.exists():
            return {"tests_exist": False}

        test_files = list(tests_path.rglob("test_*.py"))

        return {
            "tests_exist": True,
            "test_file_count": len(test_files),
            "tests_path": str(tests_path),
        }

    def _analyze_documentation(self) -> Dict[str, Any]:
        """分析文档完整性"""
        docs_path = self.project_root / "docs"

        if not docs_path.exists():
            return {"docs_exist": False}

        doc_files = list(docs_path.rglob("*.md"))

        return {
            "docs_exist": True,
            "doc_file_count": len(doc_files),
            "docs_path": str(docs_path),
        }

    def generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        recommendations = []

        # 基于GPU系统状态
        gpu_status = self.analysis_results["system_status"].get("gpu_info", {})
        if gpu_status.get("available", False):
            recommendations.append("✅ GPU加速系统可用，建议激活GPU加速AI计算")
        else:
            recommendations.append("⚠️  GPU加速不可用，建议安装GPUtil库以启用GPU监控")

        # 基于AI基础设施
        ai_infra = self.analysis_results["ai_infrastructure"]
        if ai_infra.get("gpu_api_system", {}).get("ready", False):
            recommendations.append("✅ GPU API系统已就绪，可以开始AI自动化集成测试")
        else:
            recommendations.append("🔧 GPU API系统配置不完整，建议完善关键文件")

        # 基于数据库状态
        db_status = self.analysis_results["system_status"].get("database_status", {})
        if all(db_status.values()):
            recommendations.append("✅ 数据库环境完整，支持AI自动化数据处理")
        else:
            recommendations.append("🔧 数据库环境不完整，建议安装PostgreSQL和TDengine")

        # 基于代码复杂度
        perf_metrics = self.analysis_results["performance_metrics"]
        code_complexity = perf_metrics.get("code_complexity", {})
        if code_complexity.get("total_lines", 0) > 10000:
            recommendations.append("📚 代码库规模较大，建议建立完善的自动化测试体系")

        self.analysis_results["recommendations"] = recommendations
        return recommendations

    def run_full_analysis(self) -> Dict[str, Any]:
        """运行完整分析"""
        logger.info("🚀 开始MyStocks AI自动化现状分析...")

        try:
            # 系统状态分析
            self.analyze_system_status()

            # AI基础设施分析
            self.analyze_ai_infrastructure()

            # 性能指标分析
            self.analyze_performance_metrics()

            # 生成建议
            self.generate_recommendations()

            logger.info("✅ 分析完成！")
            return self.analysis_results

        except Exception as e:
            logger.error(f"❌ 分析过程中发生错误: {e}")
            self.analysis_results["analysis_error"] = str(e)
            return self.analysis_results

    def save_results(self, output_file: str = None) -> str:
        """保存分析结果"""
        if not output_file:
            output_file = self.project_root / f"ai_automation_analysis_{int(time.time())}.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.analysis_results, f, ensure_ascii=False, indent=2)

        return str(output_file)

    def print_summary(self):
        """打印分析摘要"""
        print("\n" + "=" * 60)
        print("🎯 MyStocks AI自动化现状分析摘要")
        print("=" * 60)

        # 系统状态
        system_status = self.analysis_results["system_status"]
        print("\n📊 系统状态:")
        print(f"  CPU核心数: {system_status['cpu_info']['cores']}")
        print(f"  CPU使用率: {system_status['cpu_info']['usage_percent']}%")
        print(f"  内存使用率: {system_status['memory_info']['usage_percent']}%")
        print(f"  磁盘使用率: {system_status['disk_info']['usage_percent']}%")

        gpu_info = system_status.get("gpu_info", {})
        if gpu_info.get("available"):
            print(f"  GPU状态: ✅ 可用 ({len(gpu_info.get('gpus', []))}个GPU)")
        else:
            print("  GPU状态: ❌ 不可用")

        # AI基础设施
        ai_infra = self.analysis_results["ai_infrastructure"]
        print("\n🧠 AI基础设施:")

        gpu_api = ai_infra.get("gpu_api_system", {})
        if gpu_api.get("ready"):
            print("  GPU API系统: ✅ 就绪")
        else:
            print("  GPU API系统: ❌ 未就绪")

        ml_services = ai_infra.get("ml_services", {})
        active_services = sum(1 for v in ml_services.values() if v)
        print(f"  ML服务: {active_services}/{len(ml_services)} 个活跃")

        data_sources = ai_infra.get("data_sources", {})
        active_sources = sum(1 for v in data_sources.values() if v)
        print(f"  数据源: {active_sources}/{len(data_sources)} 个可用")

        # 建议
        print("\n💡 改进建议:")
        for i, rec in enumerate(self.analysis_results["recommendations"], 1):
            print(f"  {i}. {rec}")

        print("\n📁 详细分析结果已保存")
        print("=" * 60)


def main():
    """主函数"""
    analyzer = AIAutomationAnalyzer()

    # 运行分析
    results = analyzer.run_full_analysis()

    # 保存结果
    output_file = analyzer.save_results()
    print(f"📄 分析结果已保存到: {output_file}")

    # 打印摘要
    analyzer.print_summary()

    return results


if __name__ == "__main__":
    main()
