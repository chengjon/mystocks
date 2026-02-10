"""
测试持续集成系统 (Test Continuous Integration System)

提供完整的持续集成能力，包括：
- 自动化测试管道
- 构建和部署流程
- 代码质量检查
- 测试报告生成
- 集成监控和告警
- 环境管理
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import aiohttp
from pydantic import BaseModel, Field

import docker

# 设置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class PipelineStatus(Enum):
    """流水线状态"""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class EnvironmentType(Enum):
    """环境类型"""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class TestType(Enum):
    """测试类型"""

    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    PERFORMANCE = "performance"
    SECURITY = "security"
    LOAD = "load"


class PipelineStep(BaseModel):
    """流水线步骤"""

    id: str = Field(..., description="步骤ID")
    name: str = Field(..., description="步骤名称")
    type: TestType = Field(..., description="测试类型")
    command: str = Field(..., description="执行命令")
    dependencies: List[str] = Field(default=[], description="依赖步骤")
    timeout: int = Field(default=300, description="超时时间(秒)")
    retry_count: int = Field(default=0, description="重试次数")
    environment: Dict[str, str] = Field(default_factory=dict, description="环境变量")
    working_directory: Optional[str] = Field(None, description="工作目录")

    status: PipelineStatus = Field(default=PipelineStatus.PENDING, description="步骤状态")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    output: str = Field("", description="输出内容")
    error: str = Field("", description="错误信息")

    def __str__(self):
        return f"{self.name} ({self.type.value}) - {self.status.value}"


class TestSuite(BaseModel):
    """测试套件"""

    id: str = Field(..., description="套件ID")
    name: str = Field(..., description="套件名称")
    description: str = Field("", description="描述")
    test_type: TestType = Field(..., description="测试类型")
    tests: List[str] = Field(default=[], description="测试文件列表")
    tags: List[str] = Field(default=[], description="标签")
    parallel: bool = Field(default=True, description="是否并行")
    max_workers: int = Field(default=4, description="最大工作进程数")
    timeout: int = Field(default=600, description="超时时间(秒)")
    retry_count: int = Field(default=0, description="重试次数")

    def __str__(self):
        return f"{self.name} ({self.test_type.value})"


class TestReport(BaseModel):
    """测试报告"""

    id: str = Field(..., description="报告ID")
    pipeline_id: str = Field(..., description="流水线ID")
    test_suite_id: str = Field(..., description="测试套件ID")
    test_type: TestType = Field(..., description="测试类型")
    total_tests: int = Field(0, description="总测试数")
    passed_tests: int = Field(0, description="通过测试数")
    failed_tests: int = Field(0, description="失败测试数")
    skipped_tests: int = Field(0, description="跳过测试数")
    error_tests: int = Field(0, description="错误测试数")
    duration: float = Field(0.0, description="持续时间(秒)")
    coverage: float = Field(0.0, description="代码覆盖率")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    status: PipelineStatus = Field(default=PipelineStatus.PENDING, description="状态")
    results: List[Dict[str, Any]] = Field(default_factory=list, description="详细结果")
    artifacts: List[str] = Field(default_factory=list, description="产物路径")

    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100

    @property
    def summary(self) -> str:
        """摘要信息"""
        return f"{self.test_type.value} - {self.status.value}: {self.passed_tests}/{self.total_tests} passed ({self.success_rate:.1f}%)"


class PipelineConfig(BaseModel):
    """流水线配置"""

    id: str = Field(..., description="配置ID")
    name: str = Field(..., description="流水线名称")
    description: str = Field("", description="描述")
    trigger_on: List[str] = Field(default=["push", "pull_request"], description="触发条件")
    branches: List[str] = Field(default=["main", "develop"], description="目标分支")
    steps: List[PipelineStep] = Field(default=[], description="步骤列表")
    test_suites: List[TestSuite] = Field(default=[], description="测试套件")
    environment: EnvironmentType = Field(default=EnvironmentType.DEVELOPMENT, description="环境类型")
    variables: Dict[str, str] = Field(default_factory=dict, description="变量")
    artifacts: List[str] = Field(default_factory=list, description="产物路径")
    notifications: Dict[str, Any] = Field(default_factory=dict, description="通知配置")
    parallel: bool = Field(default=True, description="是否并行")
    max_workers: int = Field(default=4, description="最大工作进程数")

    def __str__(self):
        return f"{self.name} ({self.environment.value})"


class ContinuousIntegrationManager:
    """持续集成管理器"""

    def __init__(self, config_file: str = "ci_config.json"):
        """初始化CI管理器"""
        self.config_file = config_file
        self.config: Optional[PipelineConfig] = None
        self.pipelines: Dict[str, Dict[str, Any]] = {}
        self.reports: Dict[str, TestReport] = {}
        self.docker_client: Optional[docker.DockerClient] = None
        self.session: Optional[aiohttp.ClientSession] = None

        # 初始化Docker客户端
        try:
            self.docker_client = docker.from_env()
        except Exception as e:
            logger.warning("Docker初始化失败: %(e)s")

        # 初始化HTTP会话
        self.session = aiohttp.ClientSession()

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.session.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        await self.session.__aexit__(exc_type, exc_val, exc_tb)

    async def setup_test_environment(self, env_type: EnvironmentType) -> bool:
        """启动测试环境"""
        if env_type == EnvironmentType.TESTING:
            compose_file = "docker-compose.test.yml"
            logger.info(f"正在启动测试环境: {compose_file}")

            # 启动容器
            result = await self._run_command(
                f"docker-compose -f {compose_file} up -d --wait"
            )

            if not result['success']:
                logger.error(f"测试环境启动失败: {result.get('error')}")
                # 尝试打印输出以便调试
                logger.error(f"命令输出: {result.get('output')}")
                return False

            # 简单的健康检查等待（--wait参数通常已经处理了大部分，但这里可以添加额外的应用层检查）
            # await self._wait_for_services_healthy()
            logger.info("测试环境启动成功")
            return True
        return True

    async def teardown_test_environment(self, env_type: EnvironmentType):
        """拆除测试环境"""
        if env_type == EnvironmentType.TESTING:
            logger.info("正在拆除测试环境")
            await self._run_command("docker-compose -f docker-compose.test.yml down -v")

    def load_config(self) -> PipelineConfig:
        """加载配置文件"""
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                config_data = json.load(f)
                self.config = PipelineConfig(**config_data)
                logger.info("加载配置成功: {self.config}")
                return self.config
        except FileNotFoundError:
            logger.warning("配置文件 {self.config_file} 不存在，使用默认配置")
            self.config = self._create_default_config()
            return self.config
        except Exception as e:
            logger.error("加载配置失败: %(e)s")
            raise

    def _create_default_config(self) -> PipelineConfig:
        """创建默认配置"""
        return PipelineConfig(
            id="default",
            name="MyStocks Default Pipeline",
            description="默认的MyStocks持续集成流水线",
            trigger_on=["push", "pull_request"],
            branches=["main", "develop"],
            environment=EnvironmentType.DEVELOPMENT,
            variables={
                "PYTHONPATH": ".:src",
                "NODE_ENV": "test",
                "TEST_DATABASE_URL": "postgresql://test:test@localhost:5432/test",
            },
        )

    async def run_pipeline(self, pipeline_id: str, config: PipelineConfig) -> Dict[str, Any]:
        """运行流水线"""
        pipeline_info = {
            "id": pipeline_id,
            "name": config.name,
            "config": config.dict(),
            "status": PipelineStatus.RUNNING.value,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "steps": [],
            "reports": [],
        }

        self.pipelines[pipeline_id] = pipeline_info

        logger.info(f"开始运行流水线: {pipeline_id}")

        try:
            # 1. 启动测试环境
            if not await self.setup_test_environment(config.environment):
                raise RuntimeError("测试环境启动失败")

            # 2. 执行流水线步骤
            if config.parallel:
                pipeline_info["steps"] = await self._run_pipeline_parallel(config)
            else:
                pipeline_info["steps"] = await self._run_pipeline_sequential(config)

            # 检查整体状态
            all_success = all(step["status"] == PipelineStatus.SUCCESS.value for step in pipeline_info["steps"])

            if all_success:
                pipeline_info["status"] = PipelineStatus.SUCCESS.value
            else:
                pipeline_info["status"] = PipelineStatus.FAILED.value

            # 生成报告
            pipeline_info["reports"] = await self._generate_pipeline_reports(pipeline_id, config)

        except Exception as e:
            logger.error(f"流水线执行失败: {e}")
            pipeline_info["status"] = PipelineStatus.FAILED.value
            pipeline_info["error"] = str(e)

        finally:
            # 3. 拆除测试环境
            await self.teardown_test_environment(config.environment)
            pipeline_info["end_time"] = datetime.now().isoformat()

        logger.info(f"流水线执行完成: {pipeline_id} - {pipeline_info['status']}")
        return pipeline_info

    async def _run_pipeline_parallel(self, config: PipelineConfig) -> List[Dict[str, Any]]:
        """并行执行流水线步骤"""
        steps = []

        # 执行无依赖的步骤
        independent_steps = [step for step in config.steps if not step.dependencies]

        # 执行依赖的步骤
        while config.steps:
            # 找出可以执行的步骤
            executable_steps = []
            for step in config.steps:
                if not step.dependencies or all(
                    dep_step.id in [s["id"] for s in steps] for dep_step in step.dependencies
                ):
                    executable_steps.append(step)

            if not executable_steps:
                logger.warning("没有可执行的步骤，可能存在循环依赖")
                break

            # 并行执行可执行的步骤
            tasks = []
            for step in executable_steps:
                task = asyncio.create_task(self._execute_step(step))
                tasks.append(task)

            step_results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, step_result in enumerate(step_results):
                if isinstance(step_result, Exception):
                    logger.error("步骤 {executable_steps[i].name} 执行失败: %(step_result)s")
                    steps.append(
                        {
                            "id": executable_steps[i].id,
                            "name": executable_steps[i].name,
                            "status": PipelineStatus.FAILED.value,
                            "error": str(step_result),
                            "output": "",
                            "start_time": datetime.now().isoformat(),
                            "end_time": datetime.now().isoformat(),
                        }
                    )
                else:
                    steps.append(step_result)

            # 从剩余步骤中移除已执行的步骤
            config.steps = [step for step in config.steps if step.id not in [s["id"] for s in steps]]

        return steps

    async def _run_pipeline_sequential(self, config: PipelineConfig) -> List[Dict[str, Any]]:
        """顺序执行流水线步骤"""
        steps = []

        for step in config.steps:
            step_result = await self._execute_step(step)
            steps.append(step_result)

        return steps

    async def _execute_step(self, step: PipelineStep) -> Dict[str, Any]:
        """执行单个步骤"""
        step_info = {
            "id": step.id,
            "name": step.name,
            "type": step.type.value,
            "status": PipelineStatus.RUNNING.value,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "output": "",
            "error": "",
        }

        logger.info("开始执行步骤: {step.name}")

        try:
            # 设置环境变量
            env = os.environ.copy()
            env.update(step.environment)

            # 设置工作目录
            cwd = step.working_directory or os.getcwd()

            # 执行命令
            process = await asyncio.create_subprocess_shell(
                step.command,
                cwd=cwd,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            # 等待进程完成或超时
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=step.timeout)

                if process.returncode == 0:
                    step_info["status"] = PipelineStatus.SUCCESS.value
                    step_info["output"] = stdout.decode("utf-8", errors="ignore")
                    logger.info("步骤执行成功: {step.name}")
                else:
                    step_info["status"] = PipelineStatus.FAILED.value
                    step_info["output"] = stdout.decode("utf-8", errors="ignore")
                    step_info["error"] = stderr.decode("utf-8", errors="ignore")
                    logger.error("步骤执行失败: {step.name} - {stderr.decode('utf-8', errors='ignore')}")

            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                step_info["status"] = PipelineStatus.FAILED.value
                step_info["error"] = f"步骤超时: {step.timeout}秒"
                logger.error("步骤执行超时: {step.name}")

        except Exception as e:
            step_info["status"] = PipelineStatus.FAILED.value
            step_info["error"] = str(e)
            logger.error("步骤执行异常: {step.name} - %(e)s")

        step_info["end_time"] = datetime.now().isoformat()
        return step_info

    async def _generate_pipeline_reports(self, pipeline_id: str, config: PipelineConfig) -> List[TestReport]:
        """生成流水线报告"""
        reports = []

        for test_suite in config.test_suites:
            # 生成测试报告
            report = TestReport(
                id=f"{pipeline_id}_{test_suite.id}",
                pipeline_id=pipeline_id,
                test_suite_id=test_suite.id,
                test_type=test_suite.test_type,
                total_tests=len(test_suite.tests),
                passed_tests=len(test_suite.tests) // 2,  # 模拟数据
                failed_tests=len(test_suite.tests) // 4,  # 模拟数据
                skipped_tests=0,
                error_tests=len(test_suite.tests) // 4,  # 模拟数据
                duration=30.0,  # 模拟数据
                coverage=80.0,  # 模拟数据
                status=PipelineStatus.SUCCESS.value,
                results=[],  # 模拟数据
                artifacts=[],
            )

            self.reports[report.id] = report
            reports.append(report)

        return reports

    async def run_test_suite(self, suite: TestSuite) -> TestReport:
        """运行测试套件"""
        logger.info("开始运行测试套件: {suite.name}")

        start_time = datetime.now()
        total_tests = len(suite.tests)
        passed_tests = 0
        failed_tests = 0
        skipped_tests = 0
        error_tests = 0

        # 并行执行测试
        tasks = []
        for test_file in suite.tests:
            task = asyncio.create_task(self._run_test_file(test_file, suite))
            tasks.append(task)

        # 并行执行测试
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                error_tests += 1
                logger.error("测试执行异常: %(result)s")
            elif result.get("status") == "passed":
                passed_tests += 1
            elif result.get("status") == "failed":
                failed_tests += 1
            elif result.get("status") == "skipped":
                skipped_tests += 1

        # 生成测试报告
        report = TestReport(
            id=f"{suite.id}_{int(time.time())}",
            pipeline_id="",
            test_suite_id=suite.id,
            test_type=suite.test_type,
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
            error_tests=error_tests,
            duration=(datetime.now() - start_time).total_seconds(),
            coverage=85.0,  # 模拟覆盖率
            status=PipelineStatus.SUCCESS.value if error_tests == 0 else PipelineStatus.FAILED.value,
            results=results,
            artifacts=[],
        )

        logger.info("测试套件执行完成: {suite.name} - {report.summary}")
        return report

    async def _run_test_file(self, test_file: str, suite: TestSuite) -> Dict[str, Any]:
        """运行单个测试文件"""
        try:
            # 构建测试命令
            if suite.test_type == TestType.UNIT:
                cmd = f"python -m pytest {test_file} -v"
            elif suite.test_type == TestType.INTEGRATION:
                cmd = f"python -m pytest {test_file} -m integration -v"
            elif suite.test_type == TestType.E2E:
                cmd = f"npx playwright test {test_file} --project=chromium"
            elif suite.test_type == TestType.PERFORMANCE:
                cmd = f"python -m pytest {test_file} -m performance -v"
            elif suite.test_type == TestType.SECURITY:
                cmd = f"python -m pytest {test_file} -m security -v"
            else:
                cmd = f"python -m pytest {test_file} -v"

            # 执行测试
            process = await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                return {
                    "test_file": test_file,
                    "status": "passed",
                    "output": stdout.decode("utf-8", errors="ignore"),
                }
            else:
                return {
                    "test_file": test_file,
                    "status": "failed",
                    "error": stderr.decode("utf-8", errors="ignore"),
                    "output": stdout.decode("utf-8", errors="ignore"),
                }

        except Exception as e:
            return {"test_file": test_file, "status": "error", "error": str(e)}

    async def run_quality_checks(self) -> Dict[str, Any]:
        """运行代码质量检查"""
        logger.info("开始运行代码质量检查")

        checks = {
            "linting": False,
            "formatting": False,
            "security_scan": False,
            "dependency_check": False,
        }

        # 运行代码检查
        try:
            # 检查Python代码
            result = await self._run_command("python -m pylint src/ -E")
            checks["linting"] = result.get("success", False)

            # 检查代码格式
            result = await self._run_command("python -m black --check src/")
            checks["formatting"] = result.get("success", False)

            # 运行安全扫描
            result = await self._run_command("python -m bandit -r src/")
            checks["security_scan"] = result.get("success", False)

            # 检查依赖安全
            result = await self._run_command("python -m safety check")
            checks["dependency_check"] = result.get("success", False)

        except Exception as e:
            logger.error("代码质量检查失败: %(e)s")

        return checks

    async def _run_command(self, cmd: str) -> Dict[str, Any]:
        """执行命令"""
        try:
            process = await asyncio.create_subprocess_shell(
                cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            return {
                "success": process.returncode == 0,
                "output": stdout.decode("utf-8", errors="ignore"),
                "error": stderr.decode("utf-8", errors="ignore"),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def build_and_deploy(self, environment: EnvironmentType) -> Dict[str, Any]:
        """构建和部署应用"""
        logger.info("开始构建和部署: {environment.value}")

        result = {
            "environment": environment.value,
            "build_success": False,
            "deploy_success": False,
            "artifacts": [],
            "error": "",
        }

        try:
            # 构建应用
            if environment == EnvironmentType.DEVELOPMENT:
                build_cmd = "python -m pytest tests/ --tb=short"
            elif environment == EnvironmentType.TESTING:
                build_cmd = "python -m pytest tests/ --cov=src --cov-report=html"
            elif environment == EnvironmentType.STAGING:
                build_cmd = "python -m pytest tests/ --cov=src --cov-report=xml"
            else:  # PRODUCTION
                build_cmd = "python -m pytest tests/ --cov=src --cov-report=xml"

            build_result = await self._run_command(build_cmd)
            result["build_success"] = build_result["success"]

            # 部署应用
            if result["build_success"]:
                deploy_result = await self._run_command("./scripts/automation/deploy.sh --check")
                result["deploy_success"] = deploy_result["success"]

                # 构建产物
                result["artifacts"] = ["coverage.xml", "htmlcov", "test-results"]

        except Exception as e:
            result["error"] = str(e)
            logger.error("构建和部署失败: %(e)s")

        return result

    async def monitor_pipeline(self, pipeline_id: str) -> Dict[str, Any]:
        """监控流水线状态"""
        pipeline = self.pipelines.get(pipeline_id, {})

        if not pipeline:
            return {"error": "Pipeline not found"}

        # 获取实时状态
        status_info = {
            "pipeline_id": pipeline_id,
            "status": pipeline.get("status"),
            "progress": 0,
            "current_step": "",
            "steps_completed": 0,
            "total_steps": len(pipeline.get("steps", [])),
            "elapsed_time": 0,
            "estimated_remaining_time": 0,
        }

        # 计算进度
        steps = pipeline.get("steps", [])
        completed_steps = [step for step in steps if step.get("status") != PipelineStatus.RUNNING.value]
        status_info["steps_completed"] = len(completed_steps)
        status_info["progress"] = (len(completed_steps) / len(steps)) * 100 if steps else 0

        # 获取当前步骤
        running_steps = [step for step in steps if step.get("status") == PipelineStatus.RUNNING.value]
        if running_steps:
            status_info["current_step"] = running_steps[0]["name"]

        # 计算时间
        start_time = datetime.fromisoformat(pipeline.get("start_time", datetime.now().isoformat()))
        status_info["elapsed_time"] = (datetime.now() - start_time).total_seconds()

        # 估算剩余时间
        if status_info["progress"] > 0:
            estimated_total = status_info["elapsed_time"] / status_info["progress"] * 100
            status_info["estimated_remaining_time"] = estimated_total - status_info["elapsed_time"]

        return status_info

    async def cancel_pipeline(self, pipeline_id: str) -> bool:
        """取消流水线"""
        pipeline = self.pipelines.get(pipeline_id, {})

        if not pipeline:
            return False

        if pipeline.get("status") == PipelineStatus.RUNNING.value:
            pipeline["status"] = PipelineStatus.CANCELLED.value

            # 取消正在运行的步骤
            for step in pipeline.get("steps", []):
                if step.get("status") == PipelineStatus.RUNNING.value:
                    step["status"] = PipelineStatus.CANCELLED.value

            logger.info("流水线已取消: %(pipeline_id)s")
            return True

        return False

    async def get_pipeline_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取流水线历史"""
        sorted_pipelines = sorted(self.pipelines.values(), key=lambda x: x.get("start_time", ""), reverse=True)

        return sorted_pipelines[:limit]

    async def generate_report(self, pipeline_id: str) -> Dict[str, Any]:
        """生成流水线报告"""
        pipeline = self.pipelines.get(pipeline_id, {})

        if not pipeline:
            return {"error": "Pipeline not found"}

        reports = self.reports.get(pipeline_id, [])

        # 生成综合报告
        report = {
            "pipeline_id": pipeline_id,
            "pipeline_name": pipeline.get("name"),
            "status": pipeline.get("status"),
            "start_time": pipeline.get("start_time"),
            "end_time": pipeline.get("end_time"),
            "duration": self._calculate_duration(pipeline.get("start_time"), pipeline.get("end_time")),
            "total_steps": len(pipeline.get("steps", [])),
            "successful_steps": len(
                [step for step in pipeline.get("steps", []) if step.get("status") == PipelineStatus.SUCCESS.value]
            ),
            "failed_steps": len(
                [step for step in pipeline.get("steps", []) if step.get("status") == PipelineStatus.FAILED.value]
            ),
            "test_reports": [],
            "artifacts": pipeline.get("artifacts", []),
            "quality_checks": {},  # 从实际检查中获取
            "recommendations": self._generate_recommendations(pipeline, reports),
        }

        # 添加测试报告详情
        for test_report in reports:
            report["test_reports"].append(
                {
                    "test_suite_id": test_report.test_suite_id,
                    "test_type": test_report.test_type.value,
                    "summary": test_report.summary,
                    "coverage": test_report.coverage,
                    "duration": test_report.duration,
                    "artifacts": test_report.artifacts,
                }
            )

        return report

    def _calculate_duration(self, start_time: Optional[str], end_time: Optional[str]) -> str:
        """计算持续时间"""
        if not start_time:
            return "0s"

        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time) if end_time else datetime.now()

        duration = end - start

        minutes = int(duration.total_seconds() // 60)
        seconds = int(duration.total_seconds() % 60)

        return f"{minutes}m {seconds}s"

    def _generate_recommendations(self, pipeline: Dict[str, Any], reports: List[TestReport]) -> List[str]:
        """生成改进建议"""
        recommendations = []

        # 分析步骤失败情况
        failed_steps = [step for step in pipeline.get("steps", []) if step.get("status") == PipelineStatus.FAILED.value]
        if failed_steps:
            recommendations.append(f"有 {len(failed_steps)} 个步骤失败，请检查错误详情")

        # 分析测试覆盖率
        for report in reports:
            if report.coverage < 80:
                recommendations.append(f"测试覆盖率较低 ({report.coverage:.1f}%)，建议增加测试用例")

        # 分析性能
        total_duration = sum(report.duration for report in reports)
        if total_duration > 300:  # 5分钟
            recommendations.append("测试执行时间较长，可以考虑并行执行优化")

        return recommendations

    async def close(self):
        """关闭资源"""
        if self.session:
            await self.session.close()
        if self.docker_client:
            self.docker_client.close()


# 示例使用
async def demo_ci_system():
    """演示CI系统功能"""
    async with ContinuousIntegrationManager() as ci:
        # 加载配置
        config = ci.load_config()

        # 创建默认测试步骤
        if not config.steps:
            config.steps = [
                PipelineStep(id="1", name="依赖检查", type=TestType.UNIT, command="pip list"),
                PipelineStep(
                    id="2",
                    name="代码检查",
                    type=TestType.UNIT,
                    command="python -m pylint src/ -E",
                ),
                PipelineStep(
                    id="3",
                    name="单元测试",
                    type=TestType.UNIT,
                    command="python -m pytest tests/unit tests/test_data_format.py --tb=short",
                ),
                PipelineStep(
                    id="4",
                    name="集成测试",
                    type=TestType.INTEGRATION,
                    command="python -m pytest tests/integration --tb=short",
                ),
                PipelineStep(
                    id="5",
                    name="E2E测试",
                    type=TestType.E2E,
                    command="python -m pytest tests/e2e --tb=short",
                ),
            ]

        # Apply global variables to all steps
        for step in config.steps:
            if not step.environment:
                step.environment = {}
            step.environment.update(config.variables)

        # 创建测试套件
        if not config.test_suites:
            config.test_suites = [
                TestSuite(
                    id="unit_tests",
                    name="单元测试套件",
                    description="运行所有单元测试",
                    test_type=TestType.UNIT,
                    tests=[
                        "tests/test_data_format.py",
                        "tests/unit/test_config_driven_table_manager.py",
                        "tests/unit/test_config_validation.py",
                    ],
                    parallel=True,
                ),
                TestSuite(
                    id="integration_tests",
                    name="集成测试套件",
                    description="运行所有集成测试",
                    test_type=TestType.INTEGRATION,
                    tests=[
                        "tests/integration/test_api_integration.py",
                        "tests/integration/test_datasource_switching.py",
                    ],
                    parallel=True,
                ),
                TestSuite(
                    id="e2e_tests",
                    name="端到端测试套件",
                    description="运行E2E测试",
                    test_type=TestType.E2E,
                    tests=[
                        "tests/e2e/test_web_e2e.py",
                        "tests/e2e/test_dashboard_page.py",
                    ],
                    parallel=True,
                ),
            ]

        # 运行流水线
        pipeline_result = await ci.run_pipeline("demo_pipeline", config)

        # 监控流水线
        monitor_info = await ci.monitor_pipeline("demo_pipeline")

        # 生成报告
        report = await ci.generate_report("demo_pipeline")

        print("=== CI系统演示完成 ===")
        print(f"流水线状态: {pipeline_result['status']}")
        print(f"监控信息: {monitor_info}")
        print(f"报告摘要: {report}")

        # 打印失败步骤的详细输出
        failed_steps = [s for s in pipeline_result.get("steps", []) if s.get("status") == "failed"]
        if failed_steps:
            print("\n=== 失败步骤详情 ===")
            for step in failed_steps:
                print(f"\n[{step['name']}] Output:")
                print(step.get("output", "No output"))
                if step.get("error"):
                    print(f"[{step['name']}] Error:")
                    print(step.get("error"))

        return pipeline_result


if __name__ == "__main__":
    # 运行演示
    asyncio.run(demo_ci_system())
