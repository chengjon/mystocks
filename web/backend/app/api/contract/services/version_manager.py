"""
契约版本管理服务
负责契约的创建、查询、更新和同步
"""

import logging
import subprocess
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.api.contract.models import ContractDiff, ContractValidation, ContractVersion
from app.api.contract.schemas import (
    ContractMetadata,
    ContractVersionCreate,
    ContractVersionResponse,
    ContractVersionUpdate,
    SyncResult,
)

from .openapi_generator import OpenAPIGenerator

logger = logging.getLogger(__name__)


class VersionManager:
    """契约版本管理器"""

    @staticmethod
    def create_version(db: Session, version_data: ContractVersionCreate) -> ContractVersionResponse:
        """
        创建新的契约版本

        Args:
            db: 数据库会话
            version_data: 契约版本创建请求

        Returns:
            契约版本响应
        """
        # 如果是同名契约的第一个版本，自动激活
        existing_count = db.query(ContractVersion).filter(ContractVersion.name == version_data.name).count()

        is_active = existing_count == 0

        db_version = ContractVersion(
            name=version_data.name,
            version=version_data.version,
            spec=version_data.spec,
            commit_hash=version_data.commit_hash,
            author=version_data.author,
            description=version_data.description,
            tags=version_data.tags,
            is_active=is_active,
        )

        db.add(db_version)
        db.commit()
        db.refresh(db_version)

        return VersionManager._to_response(db_version)

    @staticmethod
    def get_version(db: Session, version_id: int) -> Optional[ContractVersionResponse]:
        """
        获取指定版本

        Args:
            db: 数据库会话
            version_id: 版本ID

        Returns:
            契约版本响应
        """
        db_version = db.query(ContractVersion).filter(ContractVersion.id == version_id).first()

        if not db_version:
            return None

        return VersionManager._to_response(db_version)

    @staticmethod
    def get_active_version(db: Session, name: str) -> Optional[ContractVersionResponse]:
        """
        获取契约的当前激活版本

        Args:
            db: 数据库会话
            name: 契约名称

        Returns:
            契约版本响应
        """
        db_version = db.query(ContractVersion).filter(ContractVersion.name == name, ContractVersion.is_active).first()

        if not db_version:
            return None

        return VersionManager._to_response(db_version)

    @staticmethod
    def list_versions(
        db: Session, name: Optional[str] = None, limit: int = 50, offset: int = 0
    ) -> List[ContractVersionResponse]:
        """
        列出版本

        Args:
            db: 数据库会话
            name: 契约名称 (可选)
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            契约版本响应列表
        """
        query = db.query(ContractVersion)

        if name:
            query = query.filter(ContractVersion.name == name)

        db_versions = query.order_by(ContractVersion.created_at.desc()).limit(limit).offset(offset).all()

        return [VersionManager._to_response(v) for v in db_versions]

    @staticmethod
    def update_version(
        db: Session, version_id: int, update_data: ContractVersionUpdate
    ) -> Optional[ContractVersionResponse]:
        """
        更新契约版本

        Args:
            db: 数据库会话
            version_id: 版本ID
            update_data: 更新数据

        Returns:
            更新后的契约版本响应
        """
        db_version = db.query(ContractVersion).filter(ContractVersion.id == version_id).first()

        if not db_version:
            return None

        if update_data.description is not None:
            db_version.description = update_data.description

        if update_data.tags is not None:
            db_version.tags = update_data.tags

        db.commit()
        db.refresh(db_version)

        return VersionManager._to_response(db_version)

    @staticmethod
    def activate_version(db: Session, version_id: int) -> bool:
        """
        激活指定版本（会停用同名的其他版本）

        Args:
            db: 数据库会话
            version_id: 版本ID

        Returns:
            是否成功
        """
        db_version = db.query(ContractVersion).filter(ContractVersion.id == version_id).first()

        if not db_version:
            return False

        # 停用同名的所有版本
        db.query(ContractVersion).filter(ContractVersion.name == db_version.name).update({"is_active": False})

        # 激活指定版本
        db_version.is_active = True
        db.commit()

        return True

    @staticmethod
    def delete_version(db: Session, version_id: int) -> bool:
        """
        删除契约版本

        Args:
            db: 数据库会话
            version_id: 版本ID

        Returns:
            是否成功
        """
        db_version = db.query(ContractVersion).filter(ContractVersion.id == version_id).first()

        if not db_version:
            return False

        db.delete(db_version)
        db.commit()

        return True

    @staticmethod
    def list_contracts(db: Session) -> List[ContractMetadata]:
        """
        列出所有契约及其元数据

        Args:
            db: 数据库会话

        Returns:
            契约元数据列表
        """
        # 获取每个契约的最新版本
        from sqlalchemy import func

        latest_versions = (
            db.query(ContractVersion.name, func.max(ContractVersion.created_at).label("last_updated"))
            .group_by(ContractVersion.name)
            .all()
        )

        contracts = []
        for name, last_updated in latest_versions:
            # 获取最新版本号
            latest = (
                db.query(ContractVersion)
                .filter(ContractVersion.name == name)
                .order_by(ContractVersion.created_at.desc())
                .first()
            )

            # 获取版本总数
            total = db.query(ContractVersion).filter(ContractVersion.name == name).count()

            contracts.append(
                ContractMetadata(
                    name=name,
                    latest_version=latest.version if latest else "0.0.0",
                    total_versions=total,
                    last_updated=last_updated,
                    description=latest.description if latest else None,
                    tags=latest.tags if latest else [],
                )
            )

        return contracts

    @staticmethod
    def _to_response(db_version: ContractVersion) -> ContractVersionResponse:
        """数据库模型转换为响应模型"""
        return ContractVersionResponse(
            id=db_version.id,
            name=db_version.name,
            version=db_version.version,
            spec=db_version.spec,
            commit_hash=db_version.commit_hash,
            author=db_version.author,
            description=db_version.description,
            tags=db_version.tags or [],
            created_at=db_version.created_at,
            is_active=db_version.is_active,
        )

    @staticmethod
    def sync(
        db: Session,
        contract_name: str,
        direction: str = "code_to_db",
        commit_hash: Optional[str] = None,
        author: Optional[str] = None,
        description: Optional[str] = None,
    ) -> SyncResult:
        """
        同步契约规格（Code-to-DB 或 DB-to-Code）

        Args:
            db: 数据库会话
            contract_name: 契约名称
            direction: 同步方向 ("code_to_db" 或 "db_to_code")
            commit_hash: Git commit hash
            author: 作者
            description: 版本描述

        Returns:
            SyncResult 同步结果

        Raises:
            ValueError: 无效的同步方向
        """
        if direction == "code_to_db":
            return VersionManager._sync_code_to_db(db, contract_name, commit_hash, author, description)
        elif direction == "db_to_code":
            return VersionManager._sync_db_to_code(db, contract_name)
        else:
            raise ValueError(f"Invalid sync direction: {direction}")

    @staticmethod
    def _sync_code_to_db(
        db: Session,
        contract_name: str,
        commit_hash: Optional[str] = None,
        author: Optional[str] = None,
        description: Optional[str] = None,
    ) -> SyncResult:
        """
        Code-to-DB: 从 FastAPI 路由生成 OpenAPI Spec 并保存到数据库

        Args:
            db: 数据库会话
            contract_name: 契约名称
            commit_hash: Git commit hash
            author: 作者
            description: 版本描述

        Returns:
            SyncResult 同步结果
        """
        from app.main import app as fastapi_app

        logger.info("Starting Code-to-DB sync for contract: %(contract_name)s")

        try:
            # 从 FastAPI 应用生成 OpenAPI Spec
            generator = OpenAPIGenerator(title="MyStocks API", version="1.0.0")
            generator.scan_app(fastapi_app)
            spec = generator.generate_spec()

            # 生成版本号
            timestamp = datetime.utcnow().strftime("%Y.%m.%d.%H%M")
            version = f"{timestamp}"

            # 获取 Git commit hash
            if not commit_hash:
                try:
                    commit_hash = (
                        subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
                        .decode("utf-8")
                        .strip()[:8]
                    )
                except subprocess.CalledProcessError:
                    commit_hash = "unknown"

            # 准备版本数据
            version_data = ContractVersionCreate(
                name=contract_name,
                version=version,
                spec=spec,
                commit_hash=commit_hash,
                author=author or "system",
                description=description or f"Auto-generated from code at {datetime.utcnow().isoformat()}",
                tags=["auto-generated", "code-to-db"],
            )

            # 创建新版本
            db_version = VersionManager.create_version(db, version_data)

            # 生成同步报告
            sync_report = generator.get_sync_report()
            changes = {
                "endpoints_added": sync_report["total_endpoints"],
                "sync_direction": "code_to_db",
                "generated_from": "FastAPI routes",
            }

            logger.info("Code-to-DB sync completed: {sync_report['total_endpoints']} endpoints")

            return SyncResult(
                success=True,
                version_id=db_version.id,
                version=version,
                direction="code_to_db",
                changes=changes,
                message=f"Successfully synced {sync_report['total_endpoints']} endpoints from code to database",
            )

        except Exception as e:
            logger.error("Code-to-DB sync failed: %(e)s")
            return SyncResult(success=False, direction="code_to_db", changes={}, message=f"Sync failed: {str(e)}")

    @staticmethod
    def _sync_db_to_code(db: Session, contract_name: str) -> SyncResult:
        """
        DB-to-Code: 从数据库生成 OpenAPI Spec 文件

        Args:
            db: 数据库会话
            contract_name: 契约名称

        Returns:
            SyncResult 同步结果
        """
        import yaml

        logger.info("Starting DB-to-Code sync for contract: %(contract_name)s")

        try:
            # 获取最新激活版本
            active_version = VersionManager.get_active_version(db, contract_name)

            if not active_version:
                return SyncResult(
                    success=False,
                    direction="db_to_code",
                    changes={},
                    message=f"No active version found for contract: {contract_name}",
                )

            # 获取 Spec 数据
            spec_data = active_version.spec

            # 确定输出路径
            output_paths = ["docs/api/openapi_generated.yaml", f"docs/api/openapi_{contract_name}.yaml"]

            saved_path = None
            for output_path in output_paths:
                try:
                    with open(output_path, "w", encoding="utf-8") as f:
                        yaml.dump(spec_data, f, allow_unicode=True, sort_keys=False)
                    saved_path = output_path
                    break
                except IOError:
                    continue

            if saved_path:
                # 统计变更
                paths_count = len(spec_data.get("paths", {}))
                schemas_count = len(spec_data.get("components", {}).get("schemas", {}))

                changes = {
                    "endpoints_exported": paths_count,
                    "schemas_exported": schemas_count,
                    "output_file": saved_path,
                    "version": active_version.version,
                }

                logger.info("DB-to-Code sync completed: exported to %(saved_path)s")

                return SyncResult(
                    success=True,
                    version_id=active_version.id,
                    version=active_version.version,
                    direction="db_to_code",
                    changes=changes,
                    message=f"Successfully exported {paths_count} endpoints to {saved_path}",
                )
            else:
                return SyncResult(
                    success=False, direction="db_to_code", changes={}, message="Failed to write output file"
                )

        except Exception as e:
            logger.error("DB-to-Code sync failed: %(e)s")
            return SyncResult(success=False, direction="db_to_code", changes={}, message=f"Sync failed: {str(e)}")

    @staticmethod
    def validate_version(db: Session, version_id: int) -> Dict[str, Any]:
        """
        验证契约版本的合规性

        Args:
            db: 数据库会话
            version_id: 版本ID

        Returns:
            验证结果字典
        """
        from .contract_validator import create_validator_from_dict

        version = VersionManager.get_version(db, version_id)
        if not version:
            return {"valid": False, "error": "Version not found"}

        try:
            validator = create_validator_from_dict(version.spec)

            # 获取所有端点
            endpoints = validator.get_endpoint_schema_paths()
            errors = []
            warnings = []

            for endpoint in endpoints:
                for status_code, schema in endpoint.get("responses", {}).items():
                    if status_code == "default":
                        continue

            # 记录验证结果
            validation = ContractValidation(
                version_id=version_id,
                valid=True,
                error_count=len(errors),
                warning_count=len(warnings),
                results={"endpoints_checked": len(endpoints), "errors": errors, "warnings": warnings},
            )
            db.add(validation)
            db.commit()

            return {
                "valid": len(errors) == 0,
                "endpoints_checked": len(endpoints),
                "error_count": len(errors),
                "warning_count": len(warnings),
                "errors": errors,
                "warnings": warnings,
            }

        except Exception as e:
            logger.error("Validation failed: %(e)s")
            return {"valid": False, "error": str(e)}

    @staticmethod
    def compare_versions(db: Session, version_id_1: int, version_id_2: int) -> Dict[str, Any]:
        """
        比较两个契约版本的差异

        Args:
            db: 数据库会话
            version_id_1: 第一个版本ID
            version_id_2: 第二个版本ID

        Returns:
            差异比较结果
        """
        from .diff_engine import ContractDiffEngine

        version_1 = VersionManager.get_version(db, version_id_1)
        version_2 = VersionManager.get_version(db, version_id_2)

        if not version_1 or not version_2:
            return {"error": "One or both versions not found"}

        diff_engine = ContractDiffEngine()
        diff_result = diff_engine.compare(version_1.spec, version_2.spec)

        # 保存差异记录
        diff_record = ContractDiff(
            contract_name=version_1.name,
            from_version_id=version_id_1,
            to_version_id=version_id_2,
            total_changes=diff_result.total_changes,
            breaking_changes=diff_result.breaking_changes,
            non_breaking_changes=diff_result.non_breaking_changes,
            diffs=diff_result.to_dict()["diffs"],
            summary=diff_result.summary,
        )
        db.add(diff_record)
        db.commit()

        return diff_result.to_dict()
