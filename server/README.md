# Flask项目

## 目录结构
```
server/
├── app.py              # Flask应用入口
├── requirements.txt    # Python依赖
├── venv/               # 虚拟环境
└── .gitignore
```

## 快速开始

### 1. 创建虚拟环境
```bash
cd server
python -m venv venv
```

### 2. 激活虚拟环境

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```
如果遇到执行策略错误，运行：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 运行应用
```bash
python app.py
```

访问 http://localhost:5000 查看应用。
