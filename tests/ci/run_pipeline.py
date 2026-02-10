#!/usr/bin/env python3
import asyncio
import argparse
import sys
import logging
from typing import List

# Ensure src is in python path
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from tests.ci.test_continuous_integration import (
    ContinuousIntegrationManager, 
    PipelineConfig, 
    PipelineStep, 
    TestType, 
    TestSuite, 
    EnvironmentType
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("CIPipeline")

def get_ci_check_steps() -> List[PipelineStep]:
    """Get steps for basic CI check"""
    return [
        PipelineStep(id="lint", name="代码质量检查", type=TestType.UNIT, command="ruff check src/ web/backend/app/"),
        PipelineStep(id="format", name="格式检查", type=TestType.UNIT, command="ruff format --check src/ web/backend/app/"),
        PipelineStep(id="type", name="类型检查", type=TestType.UNIT, command="mypy src/ --ignore-missing-imports"),
        PipelineStep(id="unit_test", name="单元测试", type=TestType.UNIT, command="pytest tests/unit -v --tb=short"),
    ]

def get_full_pipeline_steps() -> List[PipelineStep]:
    """Get steps for full pipeline including E2E and Integration"""
    steps = get_ci_check_steps()
    steps.extend([
        PipelineStep(
            id="integration_test", 
            name="集成测试", 
            type=TestType.INTEGRATION, 
            command="pytest tests/integration -v --tb=short",
            dependencies=["unit_test"]
        ),
        # E2E test requires build and server start, handled via npm run preview in strict mode
        # But for simple pipeline step, we can call the test runner if environment is ready
        # Or we can rely on the python manager to setup environment.
        # Here we assume environment is setup by manager.
        PipelineStep(
            id="e2e_test", 
            name="E2E测试", 
            type=TestType.E2E, 
            command="cd web/frontend && npx playwright test --project=chromium",
            dependencies=["integration_test"],
            environment={"BASE_URL": "http://localhost:3020"} # Assuming preview runs on 3020
        ),
    ])
    return steps

async def main():
    parser = argparse.ArgumentParser(description="MyStocks CI Pipeline Runner")
    parser.add_argument('--pipeline', choices=['ci-check', 'full', 'e2e-only', 'perf-only'], default='ci-check', help='Pipeline type to run')
    parser.add_argument('--env', choices=['development', 'testing', 'staging'], default='testing', help='Environment to run tests in')
    args = parser.parse_args()

    env_map = {
        'development': EnvironmentType.DEVELOPMENT,
        'testing': EnvironmentType.TESTING,
        'staging': EnvironmentType.STAGING
    }

    selected_env = env_map[args.env]
    logger.info(f"Starting pipeline: {args.pipeline} in {args.env} environment")

    async with ContinuousIntegrationManager() as ci:
        # Load or create config
        config = ci._create_default_config()
        config.name = f"MyStocks {args.pipeline.upper()} Pipeline"
        config.environment = selected_env
        config.parallel = False # Sequential for now to ensure dependencies

        # Configure steps based on pipeline type
        if args.pipeline == 'ci-check':
            config.steps = get_ci_check_steps()
        elif args.pipeline == 'full':
            config.steps = get_full_pipeline_steps()
        elif args.pipeline == 'e2e-only':
             config.steps = [
                PipelineStep(
                    id="e2e_test", 
                    name="E2E测试", 
                    type=TestType.E2E, 
                    command="cd web/frontend && npx playwright test --project=chromium",
                    environment={"BASE_URL": "http://localhost:3020"}
                )
            ]
        elif args.pipeline == 'perf-only':
             config.steps = [
                PipelineStep(
                    id="perf_test", 
                    name="性能测试", 
                    type=TestType.PERFORMANCE, 
                    command="locust -f tests/performance/locustfile.py --headless -u 10 -r 2 -t 30s"
                )
            ]

        # Run pipeline
        result = await ci.run_pipeline(f"pipeline_{args.pipeline}", config)

        # Output summary
        logger.info("="*50)
        logger.info(f"Pipeline Status: {result['status']}")
        for step in result.get('steps', []):
            icon = "✅" if step['status'] == 'success' else "❌"
            logger.info(f"{icon} {step['name']}: {step['status']}")
            if step['status'] != 'success' and step.get('error'):
                logger.error(f"  Error: {step['error']}")
                logger.error(f"  Output: {step.get('output', '')[:200]}...") # Truncate output
        logger.info("="*50)

        return 0 if result['status'] == 'success' else 1

if __name__ == '__main__':
    try:
        sys.exit(asyncio.run(main()))
    except KeyboardInterrupt:
        logger.info("Pipeline cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.exception(f"Pipeline failed with unexpected error: {e}")
        sys.exit(1)
