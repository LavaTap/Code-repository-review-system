"""
AI 代码审查系统 - Flask 应用入口

基于 LangChain + DeepSeek V3 的 Git 代码审查服务
集成 GitHub Webhook，支持用户认证和强制规则拦截
"""
import logging
import sys
from flask import Flask, jsonify, cors

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(asctime)s: %(filename)s:%(lineno)d * %(thread)d %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# 导入配置（必须在 Flask 创建前）
from .config import config as app_config


def create_app() -> Flask:
    """应用工厂函数"""
    
    # 校验配置
    errors = app_config.validate()
    if errors:
        for err in errors:
            logger.error(f"Config error: {err}")
        logger.warning("Application starting with configuration errors!")

    # 创建 Flask 实例
    app = Flask(__name__)
    app.config["SECRET_KEY"] = app_config.secret_key
    app.config["DEBUG"] = app_config.debug
    
    # 启用 CORS
    cors.CORS(app)
    
    # 初始化数据库
    from .database import init_db
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)
    
    # 注册路由蓝图
    from .routes.auth import auth_bp
    from .routes.review import review_bp
    from .routes.webhook import webhook_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(webhook_bp)
    
    # === 基础路由 ===
    
    @app.route("/")
    def index():
        """API 信息端点"""
        return jsonify({
            "service": "AI Code Review System (LangChain + DeepSeek V3)",
            "version": "2.0.0",
            "description": "Git-integrated AI code review with merge gate enforcement",
            "endpoints": {
                "health": "/health",
                "auth_register": "POST /api/auth/register",
                "auth_login": "POST /api/auth/login",
                "review": "POST /api/review (stream support)",
                "review_list": "GET /api/review/list",
                "webhook_github": "POST /api/webhook/github"
            }
        })
    
    @app.route("/health")
    def health():
        """健康检查"""
        return jsonify({
            "status": "healthy",
            "service": "ai-code-review-system",
            "model": app_config.deepseek_model,
            "database": "connected"
        })
    
    # === 错误处理 ===
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Endpoint not found"}), 404
    
    @app.errorhandler(500)
    def server_error(e):
        logger.error(f"Server error: {e}")
        return jsonify({"error": "Internal server error"}), 500
    
    logger.info("Flask application created successfully")
    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    logger.info(
        f"Starting server on {app_config.host}:{app_config.port} "
        f"(debug={app_config.debug})"
    )
    app.run(
        host=app_config.host,
        port=app_config.port,
        debug=app_config.debug
    )
