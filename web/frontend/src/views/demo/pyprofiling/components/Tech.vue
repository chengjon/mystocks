<template>
  <div class="card demo-card">
    <div class="card-header">
      <span class="card-title">🔧 技术栈与依赖</span>
      <span class="badge badge-info">INFO</span>
    </div>

    <div class="tech-section">
      <div class="section">
        <h3>核心依赖包</h3>
        <table class="table">
          <thead>
            <tr>
              <th width="200">包名</th>
              <th width="150">版本</th>
              <th>用途</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in dependencies" :key="index">
              <td><code>{{ item.package }}</code></td>
              <td><span class="badge badge-info">{{ item.version }}</span></td>
              <td>{{ item.purpose }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="section">
        <h3>安装说明</h3>
        <div class="install-card">
          <h4>环境要求</h4>
          <ul class="req-list">
            <li>Python 3.6+</li>
            <li>pip（建议升级到最新版本）</li>
          </ul>

          <h4>安装命令</h4>
          <div class="command-box">
            <span class="cmd-label">命令</span>
            <code class="cmd-value">pip install -r requirements.txt</code>
          </div>

          <p class="help-text">
            如遇到安装问题，可先执行：
            <code class="inline-cmd">python -m pip install --force-reinstall pip setuptools</code>
          </p>
        </div>
      </div>

      <div class="section">
        <h3>中文字体配置</h3>
          <div class="alert-content">
            <strong>Matplotlib 中文显示</strong>
            <p>项目使用 SimHei 字体显示中文标签。如遇到乱码：</p>
            <pre class="code-block"><code>plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False</code></pre>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { DEPENDENCIES } from '../config'

const dependencies = DEPENDENCIES
</script>

<style scoped lang="scss">

.tech-section {
  padding: 10px 0;
}

.section {
  margin-bottom: 24px;

  h3 {
    margin: 0 0 16px 0;
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
    border-left: 3px solid var(--primary);
    padding-left: 12px;
  }
}

.install-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  padding: 20px;

  h4 {
    margin: 0 0 12px 0;
    font-size: 14px;
    font-weight: 600;
    color: var(--primary);
  }

  .req-list {
    margin: 0;
    padding-left: 20px;
    line-height: 1.8;
    color: var(--text-secondary);

    li {
      margin-bottom: 4px;
    }
  }
}

.command-box {
  display: flex;
  align-items: center;
  background: var(--bg-dark);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  overflow: hidden;
  margin-top: 12px;

  .cmd-label {
    background: var(--primary);
    color: white;
    padding: 8px 14px;
    font-size: 12px;
    font-weight: 600;
  }

  .cmd-value {
    flex: 1;
    padding: 8px 14px;
    font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
    font-size: 13px;
    color: var(--text-primary);
    margin: 0;
  }
}

.help-text {
  margin: 12px 0 0 0;
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.6;

  .inline-cmd {
    display: inline-block;
    margin-top: 6px;
    padding: 4px 8px;
    background: var(--bg-dark);
    border-radius: var(--radius-sm);
    font-size: 12px;
  }
}

.alert-content {
  strong {
    display: block;
    margin-bottom: 8px;
    color: var(--text-primary);
  }

  p {
    margin: 0 0 10px 0;
    color: var(--text-secondary);
  }
}

.code-block {
  background: var(--bg-dark);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 12px 16px;
  margin: 10px 0 0 0;
  overflow-x: auto;

  code {
    font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
    font-size: 13px;
    color: var(--text-primary);
    line-height: 1.5;
  }
}
</style>
