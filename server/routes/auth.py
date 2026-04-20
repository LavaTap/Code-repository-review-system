"""
用户认证路由
- POST /api/auth/register - 用户注册
- POST /api/auth/login - 用户登录
"""
import logging
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_session
from models import User

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    用户注册
    
    Request Body:
        {
            "username": "git_username",
            "password": "password",
            "email": "optional@email.com",
            "github_id": "optional_github_id"
        }
    
    Response:
        {"user": {...}, "message": "Registration successful"}
        {"error": "..."} 400
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        username = data.get("username", "").strip()
        password = data.get("password", "")
        email = data.get("email", "").strip() or None
        github_id = data.get("github_id", "").strip() or None
        
        # 验证必填字段
        if not username:
            return jsonify({"error": "Username is required"}), 400
        if not password:
            return jsonify({"error": "Password is required"}), 400
        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400
        
        session = get_session()
        
        # 检查用户是否已存在
        existing_user = session.query(User).filter(
            (User.username == username) | (User.github_id == github_id)
        ).first()
        
        if existing_user:
            field = "username" if existing_user.username == username else "github_id"
            return jsonify({"error": f"User with this {field} already exists"}), 409
        
        # 创建用户
        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            github_id=github_id,
            email=email,
            is_active=True
        )
        
        session.add(user)
        session.commit()
        
        logger.info(f"User registered: {username}")
        
        return jsonify({
            "user": user.to_dict(),
            "message": "Registration successful"
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({"error": f"Internal error: {str(e)}"}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    用户登录
    
    Request Body:
        {
            "username": "git_username",
            "password": "password"
        }
    
    Response:
        {"user": {...}, "token": "..."}
        {"error": "..."} 401
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        username = data.get("username", "").strip()
        password = data.get("password", "")
        
        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400
        
        session = get_session()
        
        user = session.query(User).filter(
            User.username == username,
            User.is_active == True
        ).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({"error": "Invalid credentials"}), 401
        
        logger.info(f"User logged in: {username}")
        
        # 简单 token（生产环境应使用 JWT）
        token = f"{user.id}_{user.username}"
        
        return jsonify({
            "user": user.to_dict(),
            "token": token
        })
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({"error": f"Internal error: {str(e)}"}), 500
