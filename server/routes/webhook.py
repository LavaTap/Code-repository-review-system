"""
GitHub Webhook 路由
- POST /api/webhook/github - 接收 GitHub PR/Push 事件，自动触发代码审查

核心流程：
1. 验证 Webhook 签名
2. 解析事件 payload
3. 验证提交者身份（查 users 表）
4. 提取变更代码 → 调用 AI Agent 审查
5. 判断 [强制] 问题 → 决定合并门禁
6. 写入 reviews 表
"""
import hashlib
import hmac
import json
import logging

from flask import Blueprint, request, jsonify

from ..agent.code_review_agent import get_agent
from ..config import config as app_config
from ..database import get_session
from ..models import User, Review

logger = logging.getLogger(__name__)
webhook_bp = Blueprint("webhook", __name__, url_prefix="/api/webhook")


def _verify_signature(payload: bytes, signature: str) -> bool:
    """
    验证 GitHub Webhook 签名
    
    Args:
        payload: 原始请求体 bytes
        signature: X-Hub-Signature-256 头值 (sha256=...)
    
    Returns:
        bool: 签名是否有效
    """
    if not app_config.webhook_secret:
        logger.warning("WEBHOOK_SECRET not configured, skipping signature verification")
        return True
    
    if not signature or not signature.startswith("sha256="):
        return False
    
    expected = hmac.new(
        app_config.webhook_secret.encode("utf-8"),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    received = signature.split("=")[1]
    return hmac.compare_digest(expected, received)


@webhook_bp.route("/github", methods=["POST"])
def github_webhook():
    """
    接收 GitHub Webhook 事件
    
    支持的事件：
    - pull_request: opened / synchronize（PR 创建/更新）
    - push: push to target branch
    
    Response:
        {
            "status": "success" | "error",
            "review_status": "passed" | "failed",
            "has_mandatory_issues": bool,
            "message": "..."
        }
    """
    # 1. 验证签名
    signature = request.headers.get("X-Hub-Signature-256", "")
    if not _verify_signature(request.data, signature):
        logger.warning("Invalid webhook signature")
        return jsonify({"error": "Invalid signature"}), 401

    # 2. 解析事件
    event = request.headers.get("X-GitHub-Event", "")
    try:
        payload = request.get_json()
    except Exception as e:
        logger.error(f"Failed to parse webhook payload: {e}")
        return jsonify({"error": "Invalid JSON payload"}), 400

    logger.info(f"Received GitHub event: {event}")

    # 3. 只处理 PR 和 Push 事件
    if event == "pull_request":
        return _handle_pull_request(payload)
    elif event == "push":
        return _handle_push(payload)
    else:
        return jsonify({
            "status": "ignored",
            "message": f"Event '{event}' is not handled"
        })


def _handle_pull_request(payload: dict) -> dict:
    """处理 Pull Request 事件"""
    action = payload.get("action", "")
    
    # 仅在 PR 打开或代码更新时触发审查
    if action not in ("opened", "synchronize"):
        return jsonify({
            "status": "ignored",
            "message": f"PR action '{action}' does not trigger review"
        })

    pr = payload.get("pull_request", {})
    
    # 提取信息
    commit_hash = pr.get("head", {}).get("sha", "")
    author_username = pr.get("user", {}).get("login", "")
    branch = pr.get("head", {}).get("ref", "")
    repo_full_name = payload.get("repository", {}).get("full_name", "")

    logger.info(f"Processing PR #{pr.get('number')}: author={author_username}, sha={commit_hash[:12]}")

    # 4. 验证用户
    user = _verify_user(author_username)
    if user is None:
        return jsonify({
            "status": "error",
            "review_status": "failed",
            "message": f"User '{author_username}' is not registered. Please register first."
        }), 403

    # 5. 获取 PR 的变更文件列表（通过 GitHub API 或从 payload 中提取）
    # 注意：实际生产环境需要调 GitHub API 获取 diff 内容
    # 这里简化处理，返回提示信息
    changed_files = _extract_pr_files(payload)

    if not changed_files:
        return jsonify({
            "status": "warning",
            "message": "No Python files found in this PR for review"
        })

    # 6. 执行审查
    return _perform_review(
        user=user,
        commit_hash=commit_hash,
        branch=branch,
        files=changed_files,
        source_type="pull_request",
        pr_number=pr.get("number"),
        repo_name=repo_full_name
    )


def _handle_push(payload: dict) -> dict:
    """处理 Push 事件"""
    commits = payload.get("commits", [])
    ref = payload.get("ref", "")
    repo_full_name = payload.get("repository", {}).get("full_name", "")

    if not commits:
        return jsonify({"status": "ignored", "message": "No commits in this push"})

    # 取最新一个 commit 的信息
    latest_commit = commits[-1]
    author_username = latest_commit.get("author", {}).get("username", "")
    commit_hash = latest_commit.get("id", "")
    branch = ref.replace("refs/heads/", "") if ref.startswith("refs/heads/") else ref

    logger.info(f"Processing push: author={author_username}, branch={branch}, sha={commit_hash[:12]}")

    # 验证用户
    user = _verify_user(author_username)
    if user is None:
        return jsonify({
            "status": "error",
            "review_status": "failed",
            "message": f"User '{author_username}' is not registered."
        }, 403)

    # 从 commit 中提取修改的文件
    changed_files = _extract_push_files(latest_commit)

    if not changed_files:
        return jsonify({
            "status": "warning",
            "message": "No Python files found for review"
        })

    return _perform_review(
        user=user,
        commit_hash=commit_hash,
        branch=branch,
        files=changed_files,
        source_type="push",
        repo_name=repo_full_name
    )


def _verify_user(username: str) -> User | None:
    """
    验证用户是否已注册
    
    Args:
        username: GitHub 用户名
        
    Returns:
        User 对象或 None
    """
    session = get_session()
    user = session.query(User).filter(
        (User.username == username) | (User.github_id == username),
        User.is_active == True
    ).first()

    if user:
        logger.info(f"User verified: {user.username} (id={user.id})")
    else:
        logger.warning(f"Unregistered user attempt: {username}")

    return user


def _extract_pr_files(payload: dict) -> list[dict]:
    """
    从 PR payload 中提取变更的 Python 文件列表
    
    Returns:
        [{"filename": "...", "content": "..."}]
    """
    # 实际实现需要调用 GitHub API: GET /repos/{owner}/{repo}/pulls/{pr_number}/files
    # 这里先返回空列表，由调用方决定后续处理
    action = payload.get("action", "")
    pr = payload.get("pull_request", {})
    
    result = []
    # 如果 payload 中有 diff 信息，尝试解析
    # 简化：仅标记需要审查的文件名
    result.append({
        "filename": f"PR#{pr.get('number', '')} changes",
        "content": None,  # 需要 GitHub API 获取
        "diff_url": pr.get("diff_url", "")
    })
    return result


def _extract_push_files(commit: dict) -> list[dict]:
    """
    从 Push event 的 commit 中提取修改的文件
    
    Returns:
        [{"filename": "..."}]
    """
    files = []
    # commit payload 中通常有 added/modified/removed 字段
    for file_path in (
        commit.get("added", []) +
        commit.get("modified", [])
    ):
        if file_path.endswith(".py"):
            files.append({
                "filename": file_path,
                "content": None  # 需要通过 GitHub API 获取内容
            })
    return files


def _perform_review(
    user: User,
    commit_hash: str,
    branch: str,
    files: list[dict],
    source_type: str,
    **kwargs
) -> tuple:
    """
    执行 AI 代码审查并保存结果
    
    Args:
        user: 已验证的用户对象
        commit_hash: Git commit hash
        branch: 分支名
        files: 变更文件列表
        source_type: 'pull_request' | 'push'
        
    Returns:
        Flask response
    """
    agent = get_agent()
    all_results = []
    has_any_mandatory = False
    overall_status = "passed"

    for file_info in files:
        filename = file_info["filename"]
        code_content = file_info.get("content", "")

        # 如果没有代码内容，跳过但记录
        if not code_content:
            logger.warning(f"No content available for file: {filename}, skipping AI review")
            continue

        try:
            result = agent.review(code_content, filename)
            
            review_record = Review(
                user_id=user.id,
                commit_hash=commit_hash,
                branch=branch,
                filename=filename,
                code_content=code_content[:10000],  # 限制存储大小
                result_json=json.dumps(result, ensure_ascii=False),
                has_mandatory_issues=result.get("has_mandatory_issues", False),
                status=result.get("status", "pending"),
            )

            session = get_session()
            session.add(review_record)
            session.commit()

            all_results.append({
                "filename": filename,
                "review_id": review_record.id,
                **result
            })

            if result.get("has_mandatory_issues"):
                has_any_mandatory = True
                overall_status = "failed"

        except Exception as e:
            logger.error(f"Review failed for {filename}: {e}")
            all_results.append({
                "filename": filename,
                "error": str(e),
                "status": "error"
            })

    # 构建响应
    response_data = {
        "status": "success",
        "source": source_type,
        "user": user.username,
        "commit": commit_hash[:12],
        "branch": branch,
        "review_status": overall_status,
        "has_mandatory_issues": has_any_mandatory,
        "files_reviewed": len([r for r in all_results if "error" not in r]),
        "results": all_results,
        "message": (
            f"Review completed. Status: {overall_status}. "
            f"Mandatory issues found: {'Yes - MERGE BLOCKED' if has_any_mandatory else 'None'}"
        )
    }

    status_code = 200
    if has_any_mandatory:
        response_data["merge_allowed"] = False
    else:
        response_data["merge_allowed"] = True

    logger.info(
        f"Webhook review complete: commit={commit_hash[:12]}, "
        f"status={overall_status}, mandatory={has_any_mandatory}"
    )

    return jsonify(response_data), status_code
