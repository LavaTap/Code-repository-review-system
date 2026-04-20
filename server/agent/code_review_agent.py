"""
LangChain + DeepSeek V3 代码审查 Agent 核心
负责调用 LLM 执行代码审查，支持非流式和流式两种模式
"""
import json
import logging
import re
from typing import Generator

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from config import config as app_config
from .prompts import load_system_prompt

logger = logging.getLogger(__name__)


class CodeReviewAgent:
    """
    基于 LangChain + DeepSeek V3 的代码审查 Agent
    
    功能：
    - 非流式审查：review() → 返回完整结构化结果
    - 流式审查：review_stream() → 逐 token 生成
    """

    def __init__(self):
        self.llm = ChatOpenAI(
            model=app_config.deepseek_model,
            api_key=app_config.deepseek_api_key,
            base_url=app_config.deepseek_base_url,
            temperature=app_config.temperature,
            max_tokens=app_config.max_tokens,
        )
        self.system_prompt = load_system_prompt()
        logger.info(
            f"CodeReviewAgent initialized: model={app_config.deepseek_model}, "
            f"base_url={app_config.deepseek_base_url}"
        )

    def _build_messages(self, code: str, filename: str) -> list:
        """构建发送给 LLM 的消息列表"""
        user_content = (
            f"请审查以下 Python 文件:\n\n"
            f"文件名: {filename}\n\n"
            f"```python\n{code}\n```\n\n"
            f"请按照规范输出格式给出完整的审查报告，包括所有发现的问题。"
        )
        return [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_content)
        ]

    def review(self, code: str, filename: str = "unknown.py") -> dict:
        """
        执行非流式代码审查
        
        Args:
            code: Python 源代码
            filename: 文件名（用于上下文）
            
        Returns:
            dict: 结构化审查结果 {
                "filename": str,
                "issues_summary": str,  # 原始 LLM 输出
                "has_mandatory_issues": bool,
                "status": "passed" | "failed",
                "raw_response": str
            }
        """
        logger.info(f"Starting review for file: {filename} ({len(code)} chars)")
        
        messages = self._build_messages(code, filename)
        
        try:
            response = self.llm.invoke(messages)
            raw_result = response.content
            
            # 解析是否包含强制问题
            has_mandatory = self._check_mandatory_issues(raw_result)
            
            result = {
                "filename": filename,
                "issues_summary": raw_result,
                "has_mandatory_issues": has_mandatory,
                "status": "failed" if has_mandatory else "passed",
                "raw_response": raw_result
            }
            
            logger.info(
                f"Review completed: {filename}, "
                f"status={result['status']}, mandatory={has_mandatory}"
            )
            return result
            
        except Exception as e:
            logger.error(f"Review failed for {filename}: {e}")
            raise RuntimeError(f"AI review failed: {str(e)}") from e

    def review_stream(self, code: str, filename: str = "unknown.py") -> Generator[str, None, None]:
        """
        流式代码审查，逐 token yield
        
        Args:
            code: Python 源代码
            filename: 文件名
            
        Yields:
            str: 每个 chunk 的文本内容
        """
        logger.info(f"Starting stream review for file: {filename}")
        
        messages = self._build_messages(code, filename)
        
        try:
            for chunk in self.llm.stream(messages):
                if chunk.content:
                    yield chunk.content
            logger.info(f"Stream review completed: {filename}")
        except Exception as e:
            logger.error(f"Stream review failed for {filename}: {e}")
            raise RuntimeError(f"AI stream review failed: {str(e)}") from e

    @staticmethod
    def _check_mandatory_issues(text: str) -> bool:
        """
        检查审查结果中是否包含强制级别的问题
        
        匹配模式：
        - [强制] 标记
        - **[强制]** 加粗标记
        - 级别：强制
        
        Args:
            text: LLM 返回的审查结果
            
        Returns:
            bool: 是否存在强制级别问题
        """
        patterns = [
            r'\[\s*强制\s*\]',           # [强制]
            r'\*\*\[\s*强制\s*\]\*\*',   # **[强制]**
            r'级别.*?[：:]\s*强制',       # 级别：强制
            r'级别.*?强制',               # 级别强制
        ]
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        return False


# 全局 Agent 实例（延迟初始化）
_agent_instance: CodeReviewAgent | None = None


def get_agent() -> CodeReviewAgent:
    """获取全局 Agent 实例（单例）"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = CodeReviewAgent()
    return _agent_instance
