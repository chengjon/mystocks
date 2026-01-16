#!/usr/bin/env python3
"""
Algorithm Tables Creation Script

创建算法模型相关的数据表结构 (Phase 1.4)
包括: algorithm_models, training_history, prediction_history 表
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from web.backend.app.core.config import settings, get_postgresql_connection_string

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def create_algorithm_tables():
    """
    创建算法相关的数据库表
    """
    try:
        # 获取数据库连接字符串
        connection_string = get_postgresql_connection_string()
        logger.info(f"Connecting to database: {settings.postgresql_database}")

        # 创建引擎
        engine = create_engine(connection_string, echo=settings.debug, pool_pre_ping=True)

        # 定义表创建SQL
        create_tables_sql = """

        -- =====================================
        -- 第5类：算法模型数据 - PostgreSQL
        -- =====================================

        -- 算法模型存储表
        CREATE TABLE IF NOT EXISTS algorithm_models (
            model_id VARCHAR(100) PRIMARY KEY,
            algorithm_type VARCHAR(50) NOT NULL,
            model_name VARCHAR(200) NOT NULL,
            model_version VARCHAR(20) DEFAULT '1.0.0',
            model_data JSONB,
            metadata JSONB,
            training_metrics JSONB,
            symbol VARCHAR(20),
            features JSONB,
            is_active BOOLEAN DEFAULT TRUE,
            gpu_trained BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- 训练历史记录表
        CREATE TABLE IF NOT EXISTS training_history (
            training_id VARCHAR(100) PRIMARY KEY,
            model_id VARCHAR(100) NOT NULL,
            algorithm_type VARCHAR(50) NOT NULL,
            training_start_time TIMESTAMP NOT NULL,
            training_end_time TIMESTAMP,
            training_duration_ms BIGINT,
            status VARCHAR(20) NOT NULL,
            symbol VARCHAR(20),
            features JSONB,
            training_config JSONB,
            training_metrics JSONB,
            validation_metrics JSONB,
            error_message TEXT,
            gpu_used BOOLEAN DEFAULT FALSE,
            data_sample_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- 预测历史记录表
        CREATE TABLE IF NOT EXISTS prediction_history (
            prediction_id VARCHAR(100) PRIMARY KEY,
            model_id VARCHAR(100) NOT NULL,
            algorithm_type VARCHAR(50) NOT NULL,
            prediction_time TIMESTAMP NOT NULL,
            processing_time_ms BIGINT,
            status VARCHAR(20) NOT NULL,
            input_data JSONB,
            prediction_result JSONB,
            confidence_score NUMERIC(5,4),
            error_message TEXT,
            gpu_used BOOLEAN DEFAULT FALSE,
            batch_size INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- 创建索引
        CREATE INDEX IF NOT EXISTS idx_algorithm_models_type ON algorithm_models(algorithm_type);
        CREATE INDEX IF NOT EXISTS idx_algorithm_models_symbol ON algorithm_models(symbol);
        CREATE INDEX IF NOT EXISTS idx_algorithm_models_active ON algorithm_models(is_active);
        CREATE INDEX IF NOT EXISTS idx_algorithm_models_created ON algorithm_models(created_at);

        CREATE INDEX IF NOT EXISTS idx_training_history_model ON training_history(model_id);
        CREATE INDEX IF NOT EXISTS idx_training_history_type ON training_history(algorithm_type);
        CREATE INDEX IF NOT EXISTS idx_training_history_status ON training_history(status);
        CREATE INDEX IF NOT EXISTS idx_training_history_symbol ON training_history(symbol);
        CREATE INDEX IF NOT EXISTS idx_training_history_time ON training_history(training_start_time);

        CREATE INDEX IF NOT EXISTS idx_prediction_history_model ON prediction_history(model_id);
        CREATE INDEX IF NOT EXISTS idx_prediction_history_type ON prediction_history(algorithm_type);
        CREATE INDEX IF NOT EXISTS idx_prediction_history_status ON prediction_history(status);
        CREATE INDEX IF NOT EXISTS idx_prediction_history_time ON prediction_history(prediction_time);

        -- 添加表注释
        COMMENT ON TABLE algorithm_models IS '算法模型存储表';
        COMMENT ON TABLE training_history IS '算法训练历史记录表';
        COMMENT ON TABLE prediction_history IS '算法预测历史记录表';

        -- 为TimescaleDB添加hypertable（如果支持）
        -- 注意：这些语句在普通PostgreSQL中会被忽略，不会报错
        SELECT create_hypertable('training_history', 'training_start_time', if_not_exists => TRUE);
        SELECT create_hypertable('prediction_history', 'prediction_time', if_not_exists => TRUE);

        """

        # 执行表创建
        with engine.connect() as connection:
            logger.info("Creating algorithm tables...")

            # 分割SQL语句并逐个执行
            statements = [stmt.strip() for stmt in create_tables_sql.split(";") if stmt.strip()]

            for i, statement in enumerate(statements, 1):
                if statement:
                    try:
                        logger.info(f"Executing statement {i}/{len(statements)}")
                        connection.execute(text(statement))
                        connection.commit()
                    except SQLAlchemyError as e:
                        # 对于TimescaleDB相关的语句，如果不支持则跳过
                        if "create_hypertable" in statement.lower():
                            logger.warning(
                                f"TimescaleDB hypertable creation failed (expected if TimescaleDB not installed): {e}"
                            )
                            connection.rollback()
                            continue
                        else:
                            logger.error(f"Failed to execute statement {i}: {e}")
                            raise

            logger.info("Algorithm tables created successfully!")

            # 验证表创建结果
            verify_tables(connection)

    except Exception as e:
        logger.error(f"Failed to create algorithm tables: {e}")
        raise


def verify_tables(connection):
    """
    验证表是否创建成功
    """
    try:
        logger.info("Verifying table creation...")

        # 检查表是否存在
        tables_to_check = ["algorithm_models", "training_history", "prediction_history"]

        for table_name in tables_to_check:
            result = connection.execute(
                text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = :table_name
                )
            """),
                {"table_name": table_name},
            )

            exists = result.fetchone()[0]
            if exists:
                logger.info(f"✓ Table '{table_name}' created successfully")
            else:
                logger.error(f"✗ Table '{table_name}' was not created")

        # 检查索引
        indexes_to_check = ["idx_algorithm_models_type", "idx_training_history_model", "idx_prediction_history_model"]

        for index_name in indexes_to_check:
            result = connection.execute(
                text("""
                SELECT EXISTS (
                    SELECT FROM pg_indexes
                    WHERE schemaname = 'public'
                    AND indexname = :index_name
                )
            """),
                {"index_name": index_name},
            )

            exists = result.fetchone()[0]
            if exists:
                logger.info(f"✓ Index '{index_name}' created successfully")
            else:
                logger.warning(f"⚠ Index '{index_name}' was not created")

        logger.info("Table verification completed!")

    except Exception as e:
        logger.error(f"Failed to verify tables: {e}")
        raise


def create_sample_data():
    """
    创建示例数据（可选）
    """
    try:
        connection_string = get_postgresql_connection_string()
        engine = create_engine(connection_string, echo=settings.debug)

        with engine.connect() as connection:
            logger.info("Creating sample algorithm data...")

            # 插入示例算法模型
            sample_data_sql = """
            INSERT INTO algorithm_models (model_id, algorithm_type, model_name, model_version, is_active, created_at)
            VALUES
                ('svm_sample_001', 'svm', 'SVM Sample Model', '1.0.0', true, CURRENT_TIMESTAMP),
                ('dt_sample_001', 'decision_tree', 'Decision Tree Sample Model', '1.0.0', true, CURRENT_TIMESTAMP)
            ON CONFLICT (model_id) DO NOTHING;
            """

            connection.execute(text(sample_data_sql))
            connection.commit()

            logger.info("Sample data created successfully!")

    except Exception as e:
        logger.warning(f"Failed to create sample data: {e}")


def main():
    """
    主函数
    """
    try:
        logger.info("Starting algorithm tables creation (Phase 1.4)...")
        logger.info(f"Database: {settings.postgresql_database}")
        logger.info(f"Host: {settings.postgresql_host}:{settings.postgresql_port}")

        # 创建表
        create_algorithm_tables()

        # 可选：创建示例数据
        if os.getenv("CREATE_SAMPLE_DATA", "false").lower() == "true":
            create_sample_data()

        logger.info("Algorithm tables creation completed successfully! ✅")

    except Exception as e:
        logger.error(f"Algorithm tables creation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
