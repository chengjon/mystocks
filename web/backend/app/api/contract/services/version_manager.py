"""
契约版本管理服务
负责契约的创建、查询、更新和激活
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from web.backend.app.api.contract.models import ContractVersion
from web.backend.app.api.contract.schemas import (
    ContractVersionCreate,
    ContractVersionUpdate,
    ContractVersionResponse,
    ContractMetadata,
)


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
