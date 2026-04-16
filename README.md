# AI Code Review System (v2.0)

基于 **LangChain + DeepSeek V3** 的 Git 代码审查系统，集成 GitHub Webhook 自动触发评审。

## 核心功能

| 功能 | 说明 |
|------|------|
| **AI 代码审查** | 基于 LangChain + DeepSeek V3 智能审查 Python 代码 |
| **GitHub Webhook** | PR/Push 事件自动触发审查 |
| **用户认证** | 用户名+密码验证 Git 提交者身份 |
| **强制规则拦截** | 发现 `[强制]` 级别问题 → 阻止合并 |
| **流式响应** | 支持 SSE 逐 token 输出审查结果 |

## 架构流程

```
GitHub PR/Push
    ↓ Webhook
验证提交者身份 (users 表)
    ↓ 未注册 → 拒绝
AI Agent 审查 (DeepSeek V3)
    ↓ 解析结果
有 [强制] 问题?
    ├── YES → status=failed → 阻止合并 ✗
    └── NO  → status=passed → 允许合并 ✓
```

## 项目结构

```
Code-repository-review/
├── server/
│   ├── app.py                    # Flask 入口
│   ├── config.py                 # 配置管理 (.env 加载)
│   ├── models.py                 # SQLAlchemy 数据模型
│   ├── database.py               # 数据库初始化
│   ├── .env.example              # 环境变量模板
│   ├── requirements.txt          # Python 依赖
│   ├── agent/
│   │   ├── code_review_agent.py  # 核心: LangChain + DeepSeek V3 Agent
│   │   └── prompts.py            # System Prompt (加载 agent.md)
│   ├── routes/
│   │   ├── auth.py               # 认证路由 (注册/登录)
│   │   ├── review.py             # 审查路由 (手动/查询/历史)
│   │   └── webhook.py            # GitHub Webhook 路由
│   └── venv/                     # 虚拟环境
├── .codebuddy/
│   └── agents/code-review-agent/
│       └── agent.md              # Python 审查规范 (System Prompt 源)
├── bad_example.py                # 测试用例
└── README.md                     # 本文件
```

## 技术栈

| 层 | 技术 |
|---|---|
| Web 框架 | Flask + flask-cors |
| LLM | DeepSeek V3 (deepseek-chat) |
| Agent 框架 | LangChain (langchain-openai) |
| 数据库 | SQLite (SQLAlchemy, 可迁移 PostgreSQL/MySQL) |
| 配置 | python-dotenv (.env) |
| Git 集成 | GitHub Webhook |

## 快速开始

### 1. 环境准备

```bash
cd server

# 创建虚拟环境
python -m venv venv

# Windows PowerShell 激活
.\venv\Scripts\Activate.ps1

# Linux/Mac 激活
source venv/bin/activate
```

### 2. 配置环境变量

```bash
# 复制模板
cp .env.example .env

# 编辑 .env 填入你的配置
# 必填项:
#   - DEEPSEEK_API_KEY: 你的 DeepSeek API Key
#   - GITHUB_WEBHOOK_SECRET: Webhook 密钥 (openssl rand -hex 20 生成)
```

```env
# DeepSeek API
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

# GitHub Webhook
GITHUB_WEBHOOK_SECRET=your-webhook-secret-here

# Flask
SECRET_KEY=your-secret-key-here
DEBUG=true
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 启动服务

```bash
python -m app
```

服务启动在 `http://0.0.0.0:5000`

## API 接口

### 认证

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 用户注册 (`{username, password}`) |
| POST | `/api/auth/login` | 用户登录 (`{username, password}`) → 返回 token |

### 代码审查

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/review` | 手动提交审查 (`{code, filename, stream?}`) |
| GET | `/api/review/<id>` | 查询审查结果 |
| GET | `/api/review/list` | 查询审查历史 (`?user_id=&status=`) |

### GitHub Webhook

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/webhook/github` | 接收 PR/Push 事件自动触发审查 |

### 其他

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | API 信息 |
| GET | `/health` | 健康检查 |

## 使用示例

### 手动审查代码

```bash
curl -X POST http://localhost:5000/api/review \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def foo():\n    data=[]\n    return data",
    "filename": "test.py"
  }'
```

### 流式审查

```bash
curl -X POST http://localhost:5000/api/review \
  -H "Content-Type: application/json" \
  -d '{"code": "...", "filename": "test.py", "stream": true}'
```

### 注册用户

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "my-git-name", "password": "mypassword"}'
```

## GitHub Webhook 设置

1. 进入目标仓库 Settings → Webhooks → Add webhook
2. Payload URL: `https://your-domain.com/api/webhook/github`
3. Content type: `application/json`
4. Secret: 与 `.env` 中 `GITHUB_WEBHOOK_SECRET` 一致
5. 触发事件: 选择 `Pull requests` 和 `Push`
6. Active: ✅

## 数据库设计

### users 表
- `id`, `username`(唯一), `password_hash`, `github_id`, `email`, `created_at`, `is_active`

### reviews 表  
- `id`, `user_id`(FK), `commit_hash`, `branch`, `filename`, `code_content`, `result_json`, `has_mandatory_issues`, `status`, `created_at`

## 合并门禁逻辑

当 GitHub Webhook 收到 PR/Push 时：

1. 验证签名（HMAC-SHA256）
2. 提取提交者 GitHub 用户名
3. 查询 `users` 表确认已注册
4. 提取变更代码 → 调用 DeepSeek V3 审查
5. **关键判断**：
   - 有 `[强制]` 问题 → `status=failed` → `merge_allowed=false` → **阻止合并**
   - 无强制问题 → `status=passed` → `merge_allowed=true` → **允许合并**

## License

MIT License
