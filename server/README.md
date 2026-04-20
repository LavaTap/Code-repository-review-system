# Server - AI Code Review Backend

AI 代码审查系统后端服务 (LangChain + DeepSeek V3)

## 目录结构

```
server/
├── app.py                    # Flask 应用入口（注册蓝图、初始化数据库）
├── config.py                 # 配置管理（从 .env 加载）
├── models.py                 # SQLAlchemy 数据模型（User, Review）
├── database.py               # 数据库连接与初始化
├── .env.example              # 环境变量模板（复制为 .env 使用）
├── requirements.txt          # Python 依赖
├── agent/
│   ├── __init__.py
│   ├── code_review_agent.py  # 核心：LangChain + DeepSeek V3 Agent
│   └── prompts.py            # Prompt 模板（加载 agent.md）
├── routes/
│   ├── __init__.py
│   ├── auth.py               # /api/auth/* 认证路由
│   ├── review.py             # /api/review/* 审查路由
│   └── webhook.py            # /api/webhook/github GitHub Webhook
├── venv/                     # 虚拟环境（需自行创建）
└── README.md                 # 本文件
```

## 快速开始

### 1. 创建虚拟环境并激活

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

如果遇到 PowerShell 执行策略错误：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的配置
```

必填配置：
- `DEEPSEEK_API_KEY`: [获取地址](https://platform.deepseek.com/)
- `GITHUB_WEBHOOK_SECRET`: 生成命令 `openssl rand -hex 20`

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 运行

```bash
python -m app
```

访问 http://localhost:5000 查看服务状态，http://localhost:5000/health 进行健康检查。
