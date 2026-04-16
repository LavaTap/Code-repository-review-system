"""
SQLAlchemy 数据模型定义
- User: 用户表（Git 提交者认证）
- Review: 代码审查记录表
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean,
    DateTime, ForeignKey, create_engine
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()


class User(Base):
    """用户表 - 存储 Git 提交者信息"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    github_id = Column(String(100), unique=True, nullable=True)
    email = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # 关联关系
    reviews = relationship("Review", back_populates="user", lazy="dynamic")

    def to_dict(self) -> dict:
        """转换为字典（不含密码）"""
        return {
            "id": self.id,
            "username": self.username,
            "github_id": self.github_id,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_active": self.is_active
        }


class Review(Base):
    """代码审查记录表"""
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    commit_hash = Column(String(64), nullable=False, index=True)
    branch = Column(String(200), nullable=True)
    filename = Column(Text, nullable=False)
    code_content = Column(Text, nullable=True)
    result_json = Column(Text, nullable=True)
    has_mandatory_issues = Column(Boolean, default=False)
    status = Column(String(20), default="pending")  # pending / passed / failed
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关联关系
    user = relationship("User", back_populates="reviews")

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "commit_hash": self.commit_hash,
            "branch": self.branch,
            "filename": self.filename,
            "result_json": self.result_json,
            "has_mandatory_issues": self.has_mandatory_issues,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
