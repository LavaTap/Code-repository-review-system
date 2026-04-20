#!/usr/bin/env python
"""
快速测试：调用代码审查 API 审核 bad_example.py
"""
import requests
import json

# 读取待审核代码
with open("bad_example.py", "r", encoding="utf-8") as f:
    code = f.read()

# 调用 API
response = requests.post(
    "http://localhost:5000/api/review",
    json={
        "code": code,
        "filename": "bad_example.py",
        "user_id": 1  # 可选
    }
)

# 输出结果
result = response.json()
print(json.dumps(result, indent=2, ensure_ascii=False))
