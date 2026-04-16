#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2024 CodeBuddy. All Rights Reserved

This module provides a RESTful API service for Python code review based on Baidu coding standards.

Authors: CodeBuddy Team

Date: 2024/01/01
"""

import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(asctime)s: %(filename)s:%(lineno)d * %(thread)d %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


class CodeReviewService:
    """Service class for Python code review."""

    def __init__(self):
        """Initialize the code review service."""
        self.rules = self._load_rules()

    def _load_rules(self):
        """Load code review rules based on Baidu Python coding standards."""
        return {
            'import': {
                'from_import_class': {
                    'level': 'suggestion',
                    'pattern': r'from\s+\S+\s+import\s+\S+',
                    'message': '建议禁止使用 from xxx import yyy 语法直接导入类或函数',
                    'fix': '使用 import module 然后通过 module.func 调用'
                },
                'star_import': {
                    'level': 'suggestion',
                    'pattern': r'from\s+\S+\s+import\s+\*',
                    'message': '建议禁止使用 from xxx import *',
                    'fix': '明确导入需要的模块或函数'
                }
            },
            'exception': {
                'bare_except': {
                    'level': 'mandatory',
                    'pattern': r'except\s*:',
                    'message': '禁止捕获所有异常（bare except）',
                    'fix': '明确指定要捕获的异常类型，如 except ValueError:'
                },
                'old_raise_syntax': {
                    'level': 'mandatory',
                    'pattern': r'raise\s+\w+\s*,',
                    'message': '禁止使用双参数形式抛出异常',
                    'fix': '使用 raise Exception("message") 语法'
                },
                'comma_except': {
                    'level': 'mandatory',
                    'pattern': r'except\s+\w+\s*,',
                    'message': '捕捉异常时应当使用 as 语法',
                    'fix': '使用 except Exception as e: 语法'
                }
            },
            'style': {
                'line_too_long': {
                    'level': 'mandatory',
                    'max_length': 120,
                    'message': '每行不得超过 120 个字符',
                    'fix': '将长行拆分为多行'
                },
                'function_too_long': {
                    'level': 'mandatory',
                    'max_lines': 120,
                    'message': '函数长度不得超过 120 行',
                    'fix': '将长函数拆分为多个小函数'
                },
                'tab_indentation': {
                    'level': 'mandatory',
                    'pattern': r'\t',
                    'message': '禁止使用 tab 缩进',
                    'fix': '使用 4 个空格缩进'
                }
            },
            'naming': {
                'class_naming': {
                    'level': 'mandatory',
                    'pattern': r'^class\s+([a-z_][a-z0-9_]*)',
                    'message': '类名必须使用首字母大写驼峰式命名',
                    'fix': '使用 ClassName 格式'
                },
                'constant_naming': {
                    'level': 'mandatory',
                    'pattern': r'^([a-z][a-z0-9_]*)\s*=',
                    'message': '模块级常量应使用全大写字母',
                    'fix': '使用 CONSTANT_NAME 格式'
                }
            },
            'best_practices': {
                'mutable_default': {
                    'level': 'suggestion',
                    'pattern': r'def\s+\w+\s*\([^)]*=\s*(\[\s*\]|\{\s*\})',
                    'message': '禁止使用可变对象作为默认参数',
                    'fix': '使用 None 作为默认值，在函数内部初始化'
                },
                'has_key': {
                    'level': 'mandatory',
                    'pattern': r'\.has_key\s*\(',
                    'message': '禁止使用 has_key 判断键是否存在',
                    'fix': '使用 key in dict 语法'
                },
                'none_comparison': {
                    'level': 'mandatory',
                    'pattern': r'==\s*None|!=\s*None',
                    'message': '禁止使用 == 或 != 判断 None',
                    'fix': '使用 is None 或 is not None'
                }
            }
        }

    def review_code(self, code, filename='unknown.py'):
        """
        Review Python code and return issues found.

        Args:
            code: Python source code string to review
            filename: Name of the file being reviewed

        Returns:
            dict: Review results containing issues and summary
        """
        import re

        issues = []
        lines = code.split('\n')

        # Check for file encoding
        if len(lines) >= 2:
            if 'coding' not in lines[0] and 'coding' not in lines[1]:
                if any(ord(c) > 127 for c in code):
                    issues.append({
                        'line': 1,
                        'level': 'mandatory',
                        'category': '编码',
                        'message': '文件包含非 ASCII 字符，必须在文件前两行标明字符编码',
                        'fix': '添加 # -*- coding: utf-8 -*-',
                        'code': lines[0] if lines else ''
                    })

        # Check for shebang
        if not code.startswith('#!'):
            issues.append({
                'line': 1,
                'level': 'suggestion',
                'category': '文件头',
                'message': '建议模块以 #!/usr/bin/env python 开头',
                'fix': '添加 #!/usr/bin/env python',
                'code': lines[0] if lines else ''
            })

        # Check each line
        in_function = False
        function_start_line = 0
        function_lines = 0
        indent_level = 0

        for i, line in enumerate(lines, 1):
            # Check line length
            if len(line) > 120:
                issues.append({
                    'line': i,
                    'level': 'mandatory',
                    'category': '风格',
                    'message': f'行长度 {len(line)} 超过 120 字符限制',
                    'fix': '将长行拆分为多行',
                    'code': line[:100] + '...' if len(line) > 100 else line
                })

            # Check for tabs
            if '\t' in line:
                issues.append({
                    'line': i,
                    'level': 'mandatory',
                    'category': '缩进',
                    'message': '禁止使用 tab 缩进',
                    'fix': '使用 4 个空格替换 tab',
                    'code': line.replace('\t', '→')
                })

            # Check for bare except
            if re.search(r'except\s*:', line) and 'except Exception' not in line:
                issues.append({
                    'line': i,
                    'level': 'mandatory',
                    'category': '异常',
                    'message': '禁止捕获所有异常（bare except）',
                    'fix': '明确指定异常类型，如 except ValueError:',
                    'code': line.strip()
                })

            # Check for old raise syntax
            if re.search(r'raise\s+\w+\s*,', line):
                issues.append({
                    'line': i,
                    'level': 'mandatory',
                    'category': '异常',
                    'message': '禁止使用双参数形式抛出异常',
                    'fix': '使用 raise Exception("message") 语法',
                    'code': line.strip()
                })

            # Check for comma in except
            if re.search(r'except\s+\w+\s*,\s*\w+', line):
                issues.append({
                    'line': i,
                    'level': 'mandatory',
                    'category': '异常',
                    'message': '捕捉异常时应当使用 as 语法',
                    'fix': '使用 except Exception as e: 语法',
                    'code': line.strip()
                })

            # Check for has_key
            if '.has_key(' in line:
                issues.append({
                    'line': i,
                    'level': 'mandatory',
                    'category': '最佳实践',
                    'message': '禁止使用 has_key 判断键是否存在',
                    'fix': '使用 key in dict 语法',
                    'code': line.strip()
                })

            # Check for None comparison with ==
            if re.search(r'==\s*None|!=\s*None', line):
                issues.append({
                    'line': i,
                    'level': 'mandatory',
                    'category': '最佳实践',
                    'message': '禁止使用 == 或 != 判断 None',
                    'fix': '使用 is None 或 is not None',
                    'code': line.strip()
                })

            # Check for mutable default arguments
            if re.search(r'def\s+\w+\s*\([^)]*=\s*(\[\s*\]|\{\s*\})', line):
                issues.append({
                    'line': i,
                    'level': 'suggestion',
                    'category': '最佳实践',
                    'message': '禁止使用可变对象（列表/字典）作为默认参数',
                    'fix': '使用 None 作为默认值，在函数内部初始化',
                    'code': line.strip()
                })

            # Check for semicolon
            if re.search(r';\s*$', line.strip()):
                issues.append({
                    'line': i,
                    'level': 'suggestion',
                    'category': '风格',
                    'message': '禁止以分号结束语句',
                    'fix': '移除行尾分号',
                    'code': line.strip()
                })

            # Check for multiple statements on one line
            if ';' in line and not line.strip().startswith('#'):
                statements = [s.strip() for s in line.split(';') if s.strip()]
                if len(statements) > 1:
                    issues.append({
                        'line': i,
                        'level': 'suggestion',
                        'category': '风格',
                        'message': '一行只能写一条语句',
                        'fix': '将多条语句拆分到多行',
                        'code': line.strip()
                    })

            # Track function length
            if re.search(r'^\s*def\s+\w+', line):
                if in_function and function_lines > 120:
                    issues.append({
                        'line': function_start_line,
                        'level': 'mandatory',
                        'category': '风格',
                        'message': f'函数长度 {function_lines} 超过 120 行限制',
                        'fix': '将长函数拆分为多个小函数',
                        'code': f'Function starting at line {function_start_line}'
                    })
                in_function = True
                function_start_line = i
                function_lines = 0
                indent_level = len(line) - len(line.lstrip())
            elif in_function:
                current_indent = len(line) - len(line.lstrip())
                if line.strip() and current_indent <= indent_level and not line.strip().startswith('#'):
                    if function_lines > 120:
                        issues.append({
                            'line': function_start_line,
                            'level': 'mandatory',
                            'category': '风格',
                            'message': f'函数长度 {function_lines} 超过 120 行限制',
                            'fix': '将长函数拆分为多个小函数',
                            'code': f'Function starting at line {function_start_line}'
                        })
                    in_function = False
                    function_lines = 0
                else:
                    function_lines += 1

        # Check function length for last function
        if in_function and function_lines > 120:
            issues.append({
                'line': function_start_line,
                'level': 'mandatory',
                'category': '风格',
                'message': f'函数长度 {function_lines} 超过 120 行限制',
                'fix': '将长函数拆分为多个小函数',
                'code': f'Function starting at line {function_start_line}'
            })

        # Generate summary
        mandatory_count = sum(1 for issue in issues if issue['level'] == 'mandatory')
        suggestion_count = sum(1 for issue in issues if issue['level'] == 'suggestion')

        return {
            'filename': filename,
            'total_lines': len(lines),
            'issues': issues,
            'summary': {
                'total_issues': len(issues),
                'mandatory': mandatory_count,
                'suggestion': suggestion_count
            },
            'status': 'passed' if len(issues) == 0 else 'failed'
        }


# Initialize service
review_service = CodeReviewService()


@app.route('/', methods=['GET'])
def index():
    """Root endpoint - API info."""
    return jsonify({
        'service': 'Python Code Review API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health',
            'review': '/api/review (POST)',
            'rules': '/api/rules',
            'batch_review': '/api/batch-review (POST)'
        }
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'python-code-review-api'
    })


@app.route('/api/review', methods=['POST'])
def review_code():
    """
    Review Python code endpoint.

    Request body:
        {
            "code": "Python source code string",
            "filename": "optional filename"
        }

    Returns:
        Review results with issues found
    """
    try:
        data = request.get_json()

        if not data or 'code' not in data:
            return jsonify({
                'error': 'Missing required field: code',
                'status': 'error'
            }), 400

        code = data['code']
        filename = data.get('filename', 'unknown.py')

        if not code.strip():
            return jsonify({
                'error': 'Code cannot be empty',
                'status': 'error'
            }), 400

        logger.info(f'Reviewing code from file: {filename}')
        result = review_service.review_code(code, filename)

        return jsonify(result)

    except Exception as e:
        logger.error(f'Error reviewing code: {str(e)}')
        return jsonify({
            'error': f'Internal error: {str(e)}',
            'status': 'error'
        }), 500


@app.route('/api/rules', methods=['GET'])
def get_rules():
    """Get all review rules."""
    return jsonify(review_service.rules)


@app.route('/api/batch-review', methods=['POST'])
def batch_review():
    """
    Review multiple files.

    Request body:
        {
            "files": [
                {"filename": "test.py", "code": "..."},
                ...
            ]
        }
    """
    try:
        data = request.get_json()

        if not data or 'files' not in data:
            return jsonify({
                'error': 'Missing required field: files',
                'status': 'error'
            }), 400

        files = data['files']
        results = []

        for file_info in files:
            filename = file_info.get('filename', 'unknown.py')
            code = file_info.get('code', '')

            if code.strip():
                result = review_service.review_code(code, filename)
                results.append(result)

        total_issues = sum(r['summary']['total_issues'] for r in results)
        total_mandatory = sum(r['summary']['mandatory'] for r in results)

        return jsonify({
            'results': results,
            'summary': {
                'files_reviewed': len(results),
                'total_issues': total_issues,
                'total_mandatory': total_mandatory
            }
        })

    except Exception as e:
        logger.error(f'Error in batch review: {str(e)}')
        return jsonify({
            'error': f'Internal error: {str(e)}',
            'status': 'error'
        }), 500


if __name__ == '__main__':
    logger.info('Starting Python Code Review API Server...')
    app.run(host='0.0.0.0', port=5000, debug=True)
