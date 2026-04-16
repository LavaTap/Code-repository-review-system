<template>
  <div class="code-review-container">
    <div class="header">
      <h1>Python 代码审查工具</h1>
      <p class="subtitle">基于百度 Python 编码规范自动审查</p>
    </div>

    <div class="main-content">
      <!-- 左侧：代码输入区 -->
      <div class="input-section">
        <div class="section-header">
          <h3>输入 Python 代码</h3>
          <div class="actions">
            <el-button @click="loadExample" size="small">加载示例</el-button>
            <el-button @click="clearCode" size="small">清空</el-button>
          </div>
        </div>
        <el-input
          v-model="code"
          type="textarea"
          :rows="25"
          placeholder="在此粘贴 Python 代码..."
          class="code-input"
          @input="onCodeChange"
        />
        <div class="input-footer">
          <el-button type="primary" @click="reviewCode" :loading="loading" size="large">
            开始审查
          </el-button>
          <span class="line-count">{{ lineCount }} 行</span>
        </div>
      </div>

      <!-- 右侧：审查结果区 -->
      <div class="result-section">
        <div class="section-header">
          <h3>审查结果</h3>
          <div v-if="result" class="summary-tags">
            <el-tag :type="result.status === 'passed' ? 'success' : 'danger'" effect="dark">
              {{ result.status === 'passed' ? '通过' : '未通过' }}
            </el-tag>
            <el-tag type="warning" v-if="result.summary?.mandatory > 0">
              强制: {{ result.summary?.mandatory }}
            </el-tag>
            <el-tag type="info" v-if="result.summary?.suggestion > 0">
              建议: {{ result.summary?.suggestion }}
            </el-tag>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-if="!result && !loading" class="empty-state">
          <p>请输入代码并点击"开始审查"</p>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-state">
          <el-skeleton :rows="10" animated />
        </div>

        <!-- 审查结果 -->
        <div v-if="result && !loading" class="result-content">
          <!-- 概览卡片 -->
          <div class="overview-cards">
            <div class="stat-card total">
              <div class="stat-number">{{ result.summary?.total_issues || 0 }}</div>
              <div class="stat-label">问题总数</div>
            </div>
            <div class="stat-card mandatory">
              <div class="stat-number">{{ result.summary?.mandatory || 0 }}</div>
              <div class="stat-label">强制修复</div>
            </div>
            <div class="stat-card suggestion">
              <div class="stat-number">{{ result.summary?.suggestion || 0 }}</div>
              <div class="stat-label">改进建议</div>
            </div>
          </div>

          <!-- 问题列表 -->
          <div v-if="result.issues && result.issues.length > 0" class="issues-list">
            <div
              v-for="(issue, index) in result.issues"
              :key="index"
              class="issue-item"
              :class="issue.level"
            >
              <div class="issue-header">
                <div class="issue-badges">
                  <span class="badge level" :class="issue.level">
                    {{ issue.level === 'mandatory' ? '强制' : '建议' }}
                  </span>
                  <span class="badge category">{{ issue.category }}</span>
                  <span class="badge line">第 {{ issue.line }} 行</span>
                </div>
              </div>
              <div class="issue-body">
                <p class="message">{{ issue.message }}</p>
                <div class="code-block">
                  <pre><code>{{ issue.code }}</code></pre>
                </div>
                <div class="fix-suggestion" v-if="issue.fix">
                  <span>修复建议: {{ issue.fix }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 通过状态 -->
          <div v-else class="passed-state">
            <h3>代码审查通过！</h3>
            <p>未发现违反规范的问题</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部：规范参考 -->
    <div class="reference-section">
      <el-collapse>
        <el-collapse-item title="审查规范参考" name="1">
          <div class="rules-reference">
            <el-row :gutter="20">
              <el-col :span="8">
                <h4>语言规范</h4>
                <ul>
                  <li>Import 规范 - 避免 from xxx import *</li>
                  <li>异常处理 - 明确捕获异常类型</li>
                  <li>函数返回值 - 最多 3 个返回值</li>
                  <li>默认参数 - 避免使用可变对象</li>
                </ul>
              </el-col>
              <el-col :span="8">
                <h4>风格规范</h4>
                <ul>
                  <li>行长度 - 不超过 120 字符</li>
                  <li>函数长度 - 不超过 120 行</li>
                  <li>缩进 - 使用 4 个空格</li>
                  <li>命名 - 类使用驼峰式</li>
                </ul>
              </el-col>
              <el-col :span="8">
                <h4>最佳实践</h4>
                <ul>
                  <li>使用 is None 判断空值</li>
                  <li>使用 key in dict 替代 has_key</li>
                  <li>使用 with 语句管理资源</li>
                  <li>添加文件编码声明</li>
                </ul>
              </el-col>
            </el-row>
          </div>
        </el-collapse-item>
      </el-collapse>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
// 使用 Element Plus 内置图标

const code = ref('')
const loading = ref(false)
const result = ref<any>(null)
const API_BASE_URL = 'http://localhost:5000'

const lineCount = computed(() => {
  return code.value ? code.value.split('\n').length : 0
})

const exampleCode = `#!/usr/bin/env python
# -*- coding: utf-8 -*-

def bad_function(a, b=[]):
    # 问题1: 使用可变对象作为默认参数
    data = []
    for i in range(1000):
        data.append(i * 2)
    return data

def long_line_example():
    # 问题2: 行长度超过120字符
    very_long_variable_name = "这是一段非常长的字符串，用来演示当代码行长度超过120个字符时会被检测出来的情况"
    return very_long_variable_name

def exception_example():
    try:
        result = 1 / 0
    except:  # 问题3: 捕获所有异常
        pass

def none_check(value):
    # 问题4: 使用 == 判断 None
    if value == None:
        return True
    return False
`

const loadExample = () => {
  code.value = exampleCode
  ElMessage.success('已加载示例代码')
}

const clearCode = () => {
  code.value = ''
  result.value = null
}

const onCodeChange = () => {
  // 可以在这里添加实时检查逻辑
}

const reviewCode = async () => {
  if (!code.value.trim()) {
    ElMessage.warning('请输入 Python 代码')
    return
  }

  loading.value = true
  result.value = null

  try {
    const response = await fetch(`${API_BASE_URL}/api/review`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        code: code.value,
        filename: 'review.py'
      })
    })

    if (!response.ok) {
      throw new Error('审查请求失败')
    }

    result.value = await response.json()

    if (result.value.status === 'passed') {
      ElMessage.success('代码审查通过！')
    } else {
      ElMessage.warning(`发现 ${result.value.summary?.total_issues || 0} 个问题`)
    }
  } catch (error) {
    console.error('Review error:', error)
    ElMessage.error('审查服务连接失败，请确保后端服务已启动')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.code-review-container {
  max-width: 1600px;
  margin: 0 auto;
  padding: 20px;

  .header {
    text-align: center;
    margin-bottom: 30px;

    h1 {
      font-size: 28px;
      color: #303133;
      margin-bottom: 8px;
    }

    .subtitle {
      color: #909399;
      font-size: 14px;
    }
  }

  .main-content {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 20px;

    @media (max-width: 1200px) {
      grid-template-columns: 1fr;
    }
  }

  .input-section,
  .result-section {
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    padding: 20px;
  }

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;

    h3 {
      font-size: 16px;
      color: #303133;
      margin: 0;
    }

    .actions {
      display: flex;
      gap: 8px;
    }

    .summary-tags {
      display: flex;
      gap: 8px;
    }
  }

  .code-input {
    :deep(.el-textarea__inner) {
      font-family: 'Consolas', 'Monaco', monospace;
      font-size: 13px;
      line-height: 1.6;
    }
  }

  .input-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 15px;

    .line-count {
      color: #909399;
      font-size: 13px;
    }
  }

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60px 20px;
    color: #909399;

    .empty-icon {
      font-size: 48px;
      margin-bottom: 16px;
    }
  }

  .loading-state {
    padding: 20px;
  }

  .result-content {
    .overview-cards {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 15px;
      margin-bottom: 20px;

      .stat-card {
        text-align: center;
        padding: 15px;
        border-radius: 6px;
        background: #f5f7fa;

        &.total {
          background: #ecf5ff;
          .stat-number { color: #409eff; }
        }

        &.mandatory {
          background: #fef0f0;
          .stat-number { color: #f56c6c; }
        }

        &.suggestion {
          background: #f4f4f5;
          .stat-number { color: #909399; }
        }

        .stat-number {
          font-size: 28px;
          font-weight: bold;
          margin-bottom: 5px;
        }

        .stat-label {
          font-size: 12px;
          color: #606266;
        }
      }
    }

    .issues-list {
      max-height: 500px;
      overflow-y: auto;

      .issue-item {
        border: 1px solid #ebeef5;
        border-radius: 6px;
        margin-bottom: 12px;
        overflow: hidden;

        &.mandatory {
          border-left: 4px solid #f56c6c;
        }

        &.suggestion {
          border-left: 4px solid #e6a23c;
        }

        .issue-header {
          background: #f5f7fa;
          padding: 10px 15px;

          .issue-badges {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;

            .badge {
              display: inline-block;
              padding: 2px 8px;
              border-radius: 4px;
              font-size: 12px;

              &.level {
                &.mandatory {
                  background: #fef0f0;
                  color: #f56c6c;
                }

                &.suggestion {
                  background: #fdf6ec;
                  color: #e6a23c;
                }
              }

              &.category {
                background: #ecf5ff;
                color: #409eff;
              }

              &.line {
                background: #f4f4f5;
                color: #909399;
              }
            }
          }
        }

        .issue-body {
          padding: 15px;

          .message {
            margin: 0 0 10px 0;
            color: #303133;
            font-size: 14px;
          }

          .code-block {
            background: #f5f7fa;
            border-radius: 4px;
            padding: 10px;
            margin-bottom: 10px;

            pre {
              margin: 0;
              font-family: 'Consolas', 'Monaco', monospace;
              font-size: 12px;
              color: #606266;
              white-space: pre-wrap;
              word-break: break-all;
            }
          }

          .fix-suggestion {
            display: flex;
            align-items: center;
            gap: 6px;
            color: #67c23a;
            font-size: 13px;

            .el-icon {
              font-size: 14px;
            }
          }
        }
      }
    }

    .passed-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 60px 20px;

      .success-icon {
        font-size: 64px;
        color: #67c23a;
        margin-bottom: 16px;
      }

      h3 {
        color: #67c23a;
        margin-bottom: 8px;
      }

      p {
        color: #909399;
      }
    }
  }

  .reference-section {
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    padding: 0 20px;

    .rules-reference {
      padding: 10px 0;

      h4 {
        color: #303133;
        margin-bottom: 10px;
      }

      ul {
        margin: 0;
        padding-left: 20px;

        li {
          color: #606266;
          font-size: 13px;
          margin-bottom: 6px;
        }
      }
    }
  }
}
</style>
