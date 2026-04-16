"""
Prompt 模板管理模块
从 agent.md 加载代码审查规范作为 System Prompt
"""
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# agent.md 文件路径（项目根目录的 .codebuddy/agents/ 下）
AGENT_MD_PATH = (
    Path(__file__).parent.parent.parent
    / ".codebuddy"
    / "agents"
    / "code-review-agent"
    / "agent.md"
)

_cached_prompt: str | None = None


def load_system_prompt() -> str:
    """
    加载 System Prompt（从 agent.md 缓存）
    
    Returns:
        str: 完整的审查规范文本作为 System Prompt
    """
    global _cached_prompt
    
    if _cached_prompt is not None:
        return _cached_prompt
    
    if not AGENT_MD_PATH.exists():
        logger.warning(f"Agent prompt file not found: {AGENT_MD_PATH}")
        _cached_prompt = _get_fallback_prompt()
        return _cached_prompt
    
    try:
        content = AGENT_MD_PATH.read_text(encoding="utf-8")
        _cached_prompt = content.strip()
        logger.info(f"Loaded system prompt from {AGENT_MD_PATH} ({len(_cached_prompt)} chars)")
        return _cached_prompt
    except Exception as e:
        logger.error(f"Failed to load agent.md: {e}")
        _cached_prompt = _get_fallback_prompt()
        return _cached_prompt


def reload_prompt() -> str:
    """强制重新加载 Prompt（清除缓存）"""
    global _cached_prompt
    _cached_prompt = None
    return load_system_prompt()


def _get_fallback_prompt() -> str:
    """当 agent.md 不存在时的备用 Prompt"""
    return """你是一位资深的 Python 代码审查专家。请审查提交的 Python 代码，发现潜在问题并提供改进建议。

审查维度：
1. 语言规范（Import、异常处理、变量使用等）
2. 风格规范（缩进、行长度、命名等）
3. 编程实践（资源管理、安全性等）

输出格式：
对于每个问题，请按以下格式输出：
### 问题 [级别]: 简短描述
- **位置**: 第 X 行
- **规则**: 违反的具体规范
- **当前代码**: 问题代码片段
- **建议修改**: 修改后的代码
- **说明**: 为什么这是一个问题

级别说明：
- **[强制]**: 必须修复的问题
- **[建议]**: 建议改进的问题
"""
