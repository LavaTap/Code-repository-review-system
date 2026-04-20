---
name: langchain-deepseek-agent
overview: 基于 LangChain + DeepSeek V3 搭建 AI Agent 后端服务，包含 Agent 核心逻辑、API 接口和对话功能。
todos:
  - id: cleanup-frontend
    content: 删除 client/ 目录及根目录 package.json、package-lock.json 前端文件
    status: completed
  - id: cleanup-old-server
    content: 删除旧版 server/code_review_api.py 和 server/main.py，清理遗留代码
    status: completed
    dependencies:
      - cleanup-frontend
  - id: create-config-prompt
    content: 创建 server/config.py 配置管理和 server/agent/prompts.py Prompt 模板加载模块
    status: completed
    dependencies:
      - cleanup-old-server
  - id: create-agent-core
    content: 创建 server/agent/code_review_agent.py 核心类，实现 LangChain + DeepSeek V3 的代码审查 Agent（含流式/非流式）
    status: completed
    dependencies:
      - create-config-prompt
  - id: create-api-routes
    content: 创建 server/routes/review.py 和 server/routes/chat.py RESTful API 路由，更新 server/app.py 注册路由
    status: completed
    dependencies:
      - create-agent-core
  - id: update-deps-docs
    content: 重写 server/requirements.txt，更新 README.md 文档，验证整体架构完整性
    status: completed
    dependencies:
      - create-api-routes
---

# LangChain + DeepSeek V3 Git 代码审查系统 - 实施方案

## 产品概述

将现有项目重构为 **AI 驱动的 Git 代码审查系统**，集成 GitHub Webhook 自动触发评审。删除全部前端代码，构建纯后端 API 服务。

**核心流程**：

```
GitHub PR/Push → Webhook → 用户验证 → 触发 AI 审查 → [强制]问题? → 阻止合并 : 通过
```

---

## 核心功能

| # | 功能 | 说明 |
| --- | --- | --- |
| 1 | **删除前端** | 移除 `client/`、`package.json`、`package-lock.json` |
| 2 | **DeepSeek V3 Agent** | 基于 LangChain + DeepSeek V3 的 AI 代码审查 |
| 3 | **GitHub Webhook** | 接收 PR/Push 事件自动触发审查 |
| 4 | **用户认证 + 数据库** | 用户名+密码验证 Git 提交者，SQLite 存储用户和评审记录 |
| 5 | **强制规则拦截** | 发现 `[强制]` 级别问题 → 返回失败 → 阻止合并 |
| 6 | **RESTful API** | 审查接口（流式+非流式）、Webhook 接口、健康检查 |
| 7 | **.env 配置** | 通过 `.env` 文件管理 API Key 等敏感配置 |


---

## 技术栈

| 层 | 技术 | 用途 |
| --- | --- | --- |
| Web 框架 | Flask + flask-cors | HTTP 服务 |
| LLM | DeepSeek V3 (deepseek-chat) | OpenAI 兼容 API |
| LangChain | langchain-openai, langchain-core | ChatOpenAI 对接 |
| 数据库 | SQLite + SQLAlchemy | 用户表 + 评审记录表 |
| 配置 | python-dotenv | .env 文件管理 |
| Git 集成 | GitHub Webhook | push/pull_request 事件 |


---

## 目录结构

```
d:\code\private\Code-repository-review\
├── server/
│   ├── .env.example                    # [NEW] 环境变量模板
│   ├── app.py                          # [MODIFY] Flask 入口，注册所有路由/蓝图
│   ├── config.py                       # [NEW] 配置加载（.env → AppConfig）
│   ├── models.py                       # [NEW] SQLAlchemy 数据模型（User, Review）
│   ├── database.py                     # [NEW] 数据库初始化与管理
│   ├── agent/
│   │   ├── __init__.py                 # [NEW]
│   │   ├── code_review_agent.py        # [NEW] 核心：LangChain + DeepSeek V3 Agent
│   │   └── prompts.py                  # [NEW] 加载 agent.md 作为 System Prompt
│   ├── routes/
│   │   ├── __init__.py                 # [NEW]
│   │   ├── review.py                   # [NEW] /api/review - 手动审查 API
│   │   ├── webhook.py                  # [NEW] /api/webhook/github - GitHub Webhook
│   │   └── auth.py                     # [NEW] /api/auth - 用户注册/登录
│   ├── requirements.txt                # [MODIFY] 重写依赖
│   ├── README.md                       # [MODIFY] 更新文档
│   ├── venv/                           # [KEEP] 虚拟环境
│   ├── main.py                         # [DELETE] PyCharm 示例文件
│   └── code_review_api.py              # [DELETE] 旧版规则引擎
├── client/                             # [DELETE] 整个前端目录
├── package.json                        # [DELETE]
├── package-lock.json                   # [DELETE]
├── .codebuddy/agents/code-review-agent/
│   └── agent.md                        # [KEEP] System Prompt 数据源
├── bad_example.py                      # [KEEP] 测试用例
└── README.md                           # [MODIFY] 根 README
```

---

## 数据库设计

### users 表

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | INTEGER PK | 自增主键 |
| username | TEXT UNIQUE | Git 用户名（GitHub ID） |
| password_hash | TEXT | 密码哈希 |
| github_id | TEXT | GitHub 用户 ID |
| email | TEXT | 邮箱 |
| created_at | DATETIME | 注册时间 |
| is_active | BOOLEAN | 是否活跃 |


### reviews 表

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | INTEGER PK | 自增主键 |
| user_id | INTEGER FK | 关联用户 |
| commit_hash | TEXT | Git 提交 hash |
| branch | TEXT | 分支名 |
| filename | TEXT | 文件名 |
| code_content | TEXT | 代码内容 |
| result_json | TEXT | AI 审查结果 JSON |
| has_mandatory_issues | BOOLEAN | 是否有强制级别问题 |
| status | TEXT | passed / failed / pending |
| created_at | DATETIME | 审查时间 |


---

## API 接口设计

### 认证相关

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/auth/register` | 用户注册（username + password） |
| POST | `/api/auth/login` | 用户登录，返回 token |


### 审查相关

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/review` | 手动提交代码审查（支持 stream=true 参数） |
| GET | `/api/review/{id}` | 查询审查结果 |
| GET | `/api/reviews?user_id=` | 查询用户的审查历史 |


### GitHub Webhook

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/webhook/github` | 接收 GitHub PR/Push 事件 |


**Webhook 处理流程**：

1. 验证签名（`X-Hub-Signature-256`）
2. 提取 commit 信息、作者、变更文件列表
3. **验证用户**：查询 users 表确认提交者已注册
4. 未注册 → 返回错误，拒绝处理
5. 已注册 → 提取代码 → 调用 CodeReviewAgent 审查
6. **判断结果**：有 `[强制]` 问题 → `status=failed` → GitHub Status Check 失败 → 阻止合并
7. 无强制问题或仅有建议 → `status=passed` → 允许合并
8. 写入 reviews 表

### 其他

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/` | API 信息 |
| GET | `/health` | 健康检查 |


---

## 核心模块设计

### config.py - 配置管理

```python
from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()

@dataclass
class AppConfig:
    # DeepSeek
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY")
    deepseek_base_url: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    deepseek_model: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    
    # Flask
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///reviews.db")
    
    # GitHub Webhook
    webhook_secret: str = os.getenv("GITHUB_WEBHOOK_SECRET", "")
    
    # LLM 参数
    temperature: float = 0.1
    max_tokens: int = 8192
    
    def validate(self):
        """启动时校验必填配置"""
        if not self.deepseek_api_key:
            raise ValueError("DEEPSEEK_API_KEY is required in .env")
```

### code_review_agent.py - Agent 核心

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

class CodeReviewAgent:
    """基于 LangChain + DeepSeek V3 的代码审查 Agent"""
    
    def __init__(self, config: AppConfig):
        self.llm = ChatOpenAI(
            model=config.deepseek_model,
            api_key=config.deepseek_api_key,
            base_url=config.deepseek_base_url,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            streaming=True
        )
        self.system_prompt = load_system_prompt()  # from prompts.py
    
    def review(self, code: str, filename: str) -> dict:
        """
        执行代码审查，返回结构化结果:
        {
            "issues": [...],
            "has_mandatory": bool,
            "summary": {...},
            "status": "passed" | "failed"
        }
        """
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"请审查以下 Python 文件:\n\n文件名: {filename}\n\n```python\n{code}\n```")
        ]
        response = self.llm.invoke(messages)
        return self._parse_result(response.content)
    
    def review_stream(self, code: str, filename: str):
        """流式审查，逐 token yield"""
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"请审查以下 Python 文件:\n\n文件名: {filename}\n\n```python\n{code}\n```")
        ]
        for chunk in self.llm.stream(messages):
            yield chunk.content
```

### webhook.py - GitHub Webhook 处理

```python
@app.route('/api/webhook/github', methods=['POST'])
def github_webhook():
    # 1. 验证签名
    # 2. 解析 payload (PR / Push)
    # 3. 提取 author, commits, changed files
    # 4. 查验 user 是否存在
    # 5. 调用 CodeReviewAgent.review()
    # 6. 判断 has_mandatory → 决定 merge gate
    # 7. 写库 + 返回结果
```

### .env 文件

```
# DeepSeek API
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

# Flask
SECRET_KEY=your-secret-key-here
DEBUG=true

# Database
DATABASE_URL=sqlite:///reviews.db

# GitHub Webhook
GITHUB_WEBHOOK_SECRET=your-webhook-secret
```

---

## 实施步骤（按顺序执行）

1. **清理旧文件**：删除 client/, package.json, server/main.py, server/code_review_api.py
2. **创建基础架构**：config.py, .env.example, database.py, models.py
3. **创建 Agent 模块**：agent/prompts.py, agent/code_review_agent.py
4. **创建 API 路由**：routes/auth.py, routes/review.py, routes/webhook.py
5. **组装入口**：重写 app.py，注册蓝图和初始化组件
6. **重写依赖和文档**：requirements.txt, README.md