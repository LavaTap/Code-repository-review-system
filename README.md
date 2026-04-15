# Code Repository Review System

一个完整的代码仓库审查系统，包含前端客户端和后端服务器。

## 项目结构

```
├── client/                 # 前端客户端 (Vue.js)
├── server/                # 后端服务器 (Python Flask)
├── .gitignore            # Git 忽略文件
├── README.md            # 项目说明文档
├── Python-项目规范.md    # Python 项目规范
└── 百度-Python-编码规范.md # 百度 Python 编码规范
```

## 功能特点

### 前端客户端 (client/)
- 基于 Vue.js + Vite 构建
- 现代化的用户界面
- 响应式设计

### 后端服务器 (server/)
- 基于 Python Flask 框架
- 提供 RESTful API
- 支持代码审查和分析功能

## 技术栈

### 前端
- Vue.js 3
- Vite
- JavaScript/TypeScript

### 后端
- Python 3
- Flask
- LangChain (用于代码分析)
- ChromaDB (向量数据库)

## 快速开始

### 后端服务器
```bash
cd server
pip install -r requirements.txt
python main.py
```

### 前端客户端
```bash
cd client
npm install
npm run dev
```

## 项目规范

项目包含以下规范文档：
1. `Python-项目规范.md` - Python 项目开发规范
2. `百度-Python-编码规范.md` - 百度 Python 编码规范

## 许可证

MIT License
