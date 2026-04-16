"""
代码审查路由
- POST /api/review - 手动提交代码审查（非流式/流式）
- GET /api/review/<id> - 查询审查结果
- GET /api/reviews - 查询审查历史
"""
import json
import logging
from flask import Blueprint, request, jsonify, Response, stream_with_context

from ..agent.code_review_agent import get_agent
from ..database import get_session
from ..models import Review

logger = logging.getLogger(__name__)
review_bp = Blueprint("review", __name__, url_prefix="/api/review")


@review_bp.route("", methods=["POST"])
def review_code():
    """
    手动提交代码进行 AI 审查
    
    Request Body (非流式):
        {
            "code": "Python source code...",
            "filename": "example.py",
            "user_id": 1,
            "commit_hash": "abc123",
            "branch": "main"
        }
    
    Request Body (流式，添加 stream=true):
        {
            "code": "...",
            "filename": "example.py",
            "stream": true
        }
    """
    try:
        data = request.get_json(silent=True)
        
        if not data or "code" not in data:
            return jsonify({"error": "Missing required field: code"}), 400
        
        code = data["code"]
        filename = data.get("filename", "unknown.py")
        is_stream = data.get("stream", False)
        
        if not code.strip():
            return jsonify({"error": "Code cannot be empty"}), 400
        
        # 流式模式
        if is_stream:
            agent = get_agent()

            def generate():
                try:
                    for chunk in agent.review_stream(code, filename):
                        yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"
                    yield "data: [DONE]\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"

            return Response(
                stream_with_context(generate()),
                mimetype="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "X-Accel-Buffering": "no"
                }
            )
        
        # 非流式模式
        agent = get_agent()
        result = agent.review(code, filename)
        
        # 可选：保存到数据库
        user_id = data.get("user_id")
        if user_id:
            session = get_session()
            review_record = Review(
                user_id=user_id,
                commit_hash=data.get("commit_hash", ""),
                branch=data.get("branch", ""),
                filename=filename,
                code_content=code,
                result_json=json.dumps(result, ensure_ascii=False),
                has_mandatory_issues=result["has_mandatory_issues"],
                status=result["status"],
            )
            session.add(review_record)
            session.commit()
            result["review_id"] = review_record.id
        
        return jsonify(result)
        
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 502  # LLM 调用失败
    except Exception as e:
        logger.error(f"Review error: {e}")
        return jsonify({"error": f"Internal error: {str(e)}"}), 500


@review_bp.route("/<int:review_id>", methods=["GET"])
def get_review(review_id):
    """查询单条审查记录"""
    try:
        session = get_session()
        review = session.query(Review).filter(Review.id == review_id).first()
        
        if not review:
            return jsonify({"error": "Review not found"}), 404
        
        result = review.to_dict()
        # 解析 JSON 结果
        if review.result_json:
            try:
                result["details"] = json.loads(review.result_json)
            except json.JSONDecodeError:
                pass
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Get review error: {e}")
        return jsonify({"error": str(e)}), 500


@review_bp.route("/list", methods=["GET"])
def list_reviews():
    """
    查询审查历史
    
    Query Params:
        user_id: 可选，按用户过滤
        status: 可选，按状态过滤 (passed/failed/pending)
        limit: 可选，返回数量限制 (默认 20)
        offset: 可选，偏移量
    """
    try:
        session = get_session()
        query = session.query(Review).order_by(Review.created_at.desc())
        
        user_id = request.args.get("user_id", type=int)
        status = request.args.get("status")
        limit = request.args.get("limit", 20, type=int)
        offset = request.args.get("offset", 0, type=int)
        
        if user_id:
            query = query.filter(Review.user_id == user_id)
        if status:
            query = query.filter(Review.status == status)
        
        total = query.count()
        reviews = query.offset(offset).limit(limit).all()
        
        return jsonify({
            "reviews": [r.to_dict() for r in reviews],
            "total": total,
            "limit": limit,
            "offset": offset
        })
        
    except Exception as e:
        logger.error(f"List reviews error: {e}")
        return jsonify({"error": str(e)}), 500
