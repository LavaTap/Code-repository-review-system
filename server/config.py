"""
应用配置管理模块
从 .env 文件加载配置，提供类型安全的配置访问
"""
import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件（从 server/ 目录）
ENV_PATH = Path(__file__).parent / ".env"
load_dotenv(ENV_PATH)


@dataclass
class AppConfig:
    """应用全局配置"""

    # === DeepSeek API ===
    deepseek_api_key: str = field(default_factory=lambda: os.getenv("DEEPSEEK_API_KEY", ""))
    deepseek_base_url: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    deepseek_model: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    # === Flask ===
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    # === Database ===
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///reviews.db")

    # === GitHub Webhook ===
    webhook_secret: str = os.getenv("GITHUB_WEBHOOK_SECRET", "")

    # === Server ===
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "5000"))

    # === LLM Parameters ===
    temperature: float = 0.1
    max_tokens: int = 8192

    def validate(self) -> list[str]:
        """校验必填配置，返回错误列表"""
        errors = []
        if not self.deepseek_api_key:
            errors.append("DEEPSEEK_API_KEY is required in .env file")
        if not self.webhook_secret:
            errors.append(
                "GITHUB_WEBHOOK_SECRET is required in .env file. "
                "Generate one with: openssl rand -hex 20"
            )
        return errors

    @property
    def db_path(self) -> Path:
        """获取数据库文件绝对路径（仅 SQLite）"""
        if self.database_url.startswith("sqlite:///"):
            db_name = self.database_url.replace("sqlite:///", "")
            # 相对于 server/ 目录
            return Path(__file__).parent / db_name
        return None


# 全局配置实例
config = AppConfig()
