# Python 代码审查工具使用指南

## 项目概述

本项目基于**百度 Python 编码规范**和**Python 项目规范**，提供了一个完整的代码审查解决方案，包括：

1. **智能体配置** - CodeBuddy 智能体定义
2. **后端 API** - Python Flask 提供的代码审查服务
3. **前端界面** - Vue 3 + Element Plus 的交互式审查界面

---

## 目录结构

```
Code-repository&review/
├── .codebuddy/
│   └── agents/
│       └── code-review-agent/
│           └── agent.md          # 代码审查智能体配置
├── server/
│   └── code_review_api.py        # Python 代码审查 API 服务
├── client/
│   └── src/
│       ├── views/
│       │   └── CodeReview.vue    # 代码审查页面
│       └── router/
│           └── index.ts          # 路由配置
├── 百度-Python-编码规范.md        # 百度 Python 编码规范文档
└── Python-项目规范.md             # Python 项目规范文档
```

---

## 快速开始

### 1. 启动后端服务

进入 server 目录，安装依赖并启动服务：

```bash
cd server

# 创建虚拟环境（推荐）
python -m venv venv

# Windows 激活虚拟环境
venv\Scripts\activate

# Linux/Mac 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install flask flask-cors

# 启动服务
python code_review_api.py
```

服务将在 `http://localhost:5000` 启动。

### 2. 启动前端项目

进入 client 目录，安装依赖并启动：

```bash
cd client

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 `http://localhost:5173`（或其他可用端口）启动。

### 3. 访问代码审查工具

打开浏览器访问前端地址，即可使用代码审查工具。

---

## 网页调用方式

### 方式一：通过前端界面使用

1. 打开浏览器访问前端页面
2. 在左侧输入框粘贴 Python 代码
3. 点击"开始审查"按钮
4. 在右侧查看审查结果

### 方式二：直接调用 API

#### 单文件审查

```bash
curl -X POST http://localhost:5000/api/review \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def test():\n    pass",
    "filename": "test.py"
  }'
```

**响应示例：**

```json
{
  "filename": "test.py",
  "total_lines": 2,
  "issues": [
    {
      "line": 1,
      "level": "suggestion",
      "category": "文件头",
      "message": "建议模块以 #!/usr/bin/env python 开头",
      "fix": "添加 #!/usr/bin/env python",
      "code": "def test():"
    }
  ],
  "summary": {
    "total_issues": 1,
    "mandatory": 0,
    "suggestion": 1
  },
  "status": "failed"
}
```

#### 批量审查

```bash
curl -X POST http://localhost:5000/api/batch-review \
  -H "Content-Type: application/json" \
  -d '{
    "files": [
      {"filename": "file1.py", "code": "..."},
      {"filename": "file2.py", "code": "..."}
    ]
  }'
```

#### 获取审查规则

```bash
curl http://localhost:5000/api/rules
```

#### 健康检查

```bash
curl http://localhost:5000/api/health
```

---

## 审查规则说明

### 强制规则（Mandatory）

必须修复的问题：

| 规则 | 说明 | 示例 |
|------|------|------|
| 行长度 | 每行不得超过 120 字符 | 自动检测 |
| 函数长度 | 函数不得超过 120 行 | 自动检测 |
| Tab 缩进 | 禁止使用 Tab 缩进 | 自动检测 |
| 异常捕获 | 禁止 bare except | `except:` → `except ValueError:` |
| 抛出异常 | 禁止旧语法 | `raise E, 'msg'` → `raise E('msg')` |
| None 判断 | 使用 is | `== None` → `is None` |
| has_key | 使用 in | `dict.has_key(k)` → `k in dict` |

### 建议规则（Suggestion）

建议改进的问题：

| 规则 | 说明 | 示例 |
|------|------|------|
| 可变默认参数 | 避免使用列表/字典 | `def f(a=[])` → `def f(a=None)` |
| 文件编码 | 非 ASCII 文件需声明 | 添加 `# -*- coding: utf-8 -*-` |
| Shebang | 建议添加解释器声明 | 添加 `#!/usr/bin/env python` |
| 分号 | 禁止行尾分号 | 移除 `;` |
| 多语句 | 一行一条语句 | 拆分多语句 |

---

## 在 CodeBuddy 中使用智能体

### 方式一：直接调用智能体

在 CodeBuddy 聊天中，可以直接引用智能体进行代码审查：

```
请使用 code-review-agent 审查以下代码：

[粘贴代码]
```

### 方式二：通过技能调用

如果需要更复杂的审查流程，可以将智能体封装为技能。

---

## API 接口文档

### 接口列表

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/rules` | GET | 获取所有审查规则 |
| `/api/review` | POST | 单文件代码审查 |
| `/api/batch-review` | POST | 批量代码审查 |

### 请求/响应详情

#### POST /api/review

**请求体：**

```json
{
  "code": "Python 源代码字符串",
  "filename": "文件名.py"  // 可选，默认为 unknown.py
}
```

**响应体：**

```json
{
  "filename": "文件名",
  "total_lines": 总行数,
  "issues": [
    {
      "line": 行号,
      "level": "mandatory|suggestion",
      "category": "问题分类",
      "message": "问题描述",
      "fix": "修复建议",
      "code": "问题代码片段"
    }
  ],
  "summary": {
    "total_issues": 问题总数,
    "mandatory": 强制问题数,
    "suggestion": 建议问题数
  },
  "status": "passed|failed"
}
```

---

## 扩展开发

### 添加新的审查规则

编辑 `server/code_review_api.py` 中的 `CodeReviewService` 类：

```python
def review_code(self, code, filename='unknown.py'):
    # 在适当位置添加新的检查逻辑
    if '某种模式' in line:
        issues.append({
            'line': i,
            'level': 'mandatory',  # 或 'suggestion'
            'category': '分类',
            'message': '问题描述',
            'fix': '修复建议',
            'code': line.strip()
        })
```

### 自定义前端样式

编辑 `client/src/views/CodeReview.vue` 修改样式。

---

## 常见问题

### Q: 后端服务启动失败？

A: 检查：
1. Python 版本 >= 3.7
2. 依赖是否安装：`pip install flask flask-cors`
3. 端口 5000 是否被占用

### Q: 前端无法连接后端？

A: 检查：
1. 后端服务是否已启动
2. `API_BASE_URL` 配置是否正确
3. 浏览器控制台是否有 CORS 错误

### Q: 如何修改审查规则的严格程度？

A: 编辑 `server/code_review_api.py`，修改 `level` 字段：
- `'mandatory'` - 强制规则
- `'suggestion'` - 建议规则

---

## 参考文档

- [百度 Python 编码规范](./百度-Python-编码规范.md)
- [Python 项目规范](./Python-项目规范.md)
