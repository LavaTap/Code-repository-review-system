"""
数据库初始化与管理模块
负责创建数据库连接、初始化表结构
"""
import logging
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
try:
    from .config import config
    from .models import Base
except ImportError:
    from config import config
    from models import Base

logger = logging.getLogger(__name__)

# 全局引擎和会话工厂
_engine = None
_SessionLocal = None


def get_database_url() -> str:
    """获取完整数据库 URL，SQLite 使用绝对路径"""
    db_url = config.database_url
    if db_url.startswith("sqlite:///"):
        # 转换为绝对路径
        db_path = config.db_path
        # 确保父目录存在
        db_path.parent.mkdir(parents=True, exist_ok=True)
        db_url = f"sqlite:///{db_path.absolute()}"
    return db_url


def init_db():
    """
    初始化数据库连接和表结构
    应在应用启动时调用一次
    """
    global _engine, _SessionLocal

    db_url = get_database_url()
    logger.info(f"Initializing database: {db_url}")

    _engine = create_engine(
        db_url,
        echo=config.debug,  # debug 模式下输出 SQL 日志
        connect_args={"check_same_thread": False} if "sqlite" in db_url else {}
    )
    _SessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False)

    # 创建所有表
    Base.metadata.create_all(_engine)
    logger.info("Database tables created/verified")


def get_session() -> Session:
    """获取数据库会话（每次请求使用）"""
    if _SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _SessionLocal()


def close_db():
    """关闭数据库连接"""
    global _engine
    if _engine:
        _engine.dispose()
        logger.info("Database connection closed")
