import json
import logging
from pathlib import Path
from typing import Dict

import pandas as pd
import yaml

logger = logging.getLogger(__name__)


def _load_from_database(self) -> Dict:
    """从PostgreSQL数据库加载数据源注册表"""
    query = """
        SELECT
            endpoint_name,
            source_name,
            source_type,
            data_category,
            data_classification,
            classification_level,
            target_db,
            table_name,
            parameters,
            data_quality_score,
            priority,
            status,
            health_status,
            avg_response_time,
            success_rate,
            consecutive_failures,
            last_success_time,
            last_failure_time,
            total_calls,
            failed_calls,
            tags,
            version,
            description
        FROM data_source_registry
        WHERE status = 'active'
    """

    try:
        db_manager = self._get_db_manager()
        pool = db_manager.get_postgresql_connection()
        conn = pool.getconn()
        try:
            df = pd.read_sql(query, conn)
        finally:
            pool.putconn(conn)

        sources = {}
        for _, row in df.iterrows():
            endpoint_name = row["endpoint_name"]
            sources[endpoint_name] = {
                "endpoint_name": endpoint_name,
                "source_name": row["source_name"],
                "source_type": row["source_type"],
                "data_category": row["data_category"],
                "data_classification": row["data_classification"],
                "classification_level": row["classification_level"],
                "target_db": row["target_db"],
                "table_name": row["table_name"],
                "parameters": (
                    row["parameters"]
                    if isinstance(row["parameters"], dict)
                    else (json.loads(row["parameters"]) if row["parameters"] else {})
                ),
                "data_quality_score": row["data_quality_score"],
                "priority": row["priority"],
                "status": row["status"],
                "health_status": row["health_status"],
                "avg_response_time": row["avg_response_time"],
                "success_rate": row["success_rate"],
                "consecutive_failures": row["consecutive_failures"],
                "last_success_time": row["last_success_time"],
                "last_failure_time": row["last_failure_time"],
                "total_calls": row["total_calls"],
                "failed_calls": row["failed_calls"],
                "tags": list(row["tags"]) if row["tags"] else [],
                "version": row["version"],
                "description": row["description"],
                "_loaded_from": "database",
            }

        return sources
    except Exception:
        # logger.error("从数据库加载失败: %(e)s")
        return {}


def _load_from_yaml(self) -> Dict:
    """从YAML配置文件加载数据源"""
    try:
        yaml_path = Path(self.yaml_config_path)
        if not yaml_path.exists():
            return {}

        with open(yaml_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        sources = {}
        for endpoint_key, source_config in config.get("data_sources", {}).items():
            if "endpoint_name" not in source_config:
                source_config["endpoint_name"] = endpoint_key

            source_config["_loaded_from"] = "yaml"
            sources[endpoint_key] = source_config

        return sources
    except Exception:
        return {}


def _merge_sources(self, db_sources: Dict, yaml_sources: Dict) -> Dict:
    merged = db_sources.copy()

    for endpoint_name, yaml_config in yaml_sources.items():
        if endpoint_name not in merged:
            merged[endpoint_name] = yaml_config
        else:
            db_source = merged[endpoint_name]
            config_fields = [
                "parameters",
                "description",
                "test_parameters",
                "source_config",
                "quality_rules",
                "update_schedule",
                "business_scene",
                "tags",
                "version",
            ]
            for field in config_fields:
                if field in yaml_config:
                    db_source[field] = yaml_config[field]

    return merged
