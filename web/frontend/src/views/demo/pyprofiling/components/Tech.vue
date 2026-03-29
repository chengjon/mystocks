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
        <div class="alert-card">
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
@use '../../../../styles/artdeco-tokens.scss' as *;

.tech-section {
  padding: var(--artdeco-spacing-3) 0;
}

.section {
  margin-bottom: var(--artdeco-spacing-6);

  h3 {
    margin: 0 0 var(--artdeco-spacing-4) 0;
    padding-left: var(--artdeco-spacing-3);
    border-left: calc(var(--artdeco-spacing-px) * 3) solid var(--artdeco-gold-primary);
    color: var(--artdeco-fg-primary);
    font-size: var(--artdeco-text-base);
    font-weight: var(--artdeco-font-semibold);
  }
}

.install-card {
  padding: var(--artdeco-spacing-5);
  background: color-mix(in srgb, var(--artdeco-gold-primary) 3%, var(--artdeco-bg-card));
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
  border-radius: var(--artdeco-radius-none);

  h4 {
    margin: 0 0 var(--artdeco-spacing-3) 0;
    color: var(--artdeco-gold-primary);
    font-size: var(--artdeco-text-sm);
    font-weight: var(--artdeco-font-semibold);
  }

  .req-list {
    margin: 0;
    padding-left: var(--artdeco-spacing-5);
    color: var(--artdeco-fg-muted);
    line-height: 1.8;

    li {
      margin-bottom: var(--artdeco-spacing-1);
    }
  }
}

.command-box {
  display: flex;
  align-items: center;
  overflow: hidden;
  margin-top: var(--artdeco-spacing-3);
  background: color-mix(in srgb, var(--artdeco-bg-global) 85%, transparent);
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
  border-radius: var(--artdeco-radius-none);

  .cmd-label {
    padding: var(--artdeco-spacing-2) calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px));
    background: var(--artdeco-gold-primary);
    color: var(--artdeco-bg-global);
    font-size: var(--artdeco-text-xs);
    font-weight: var(--artdeco-font-semibold);
  }

  .cmd-value {
    flex: 1;
    margin: 0;
    padding: var(--artdeco-spacing-2) calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px));
    color: var(--artdeco-fg-primary);
    font-family: var(--artdeco-font-accent, var(--font-mono));
    font-size: calc(var(--artdeco-text-sm) - var(--artdeco-spacing-px));
  }
}

.help-text {
  margin: var(--artdeco-spacing-3) 0 0 0;
  color: var(--artdeco-fg-muted);
  font-size: calc(var(--artdeco-text-sm) - var(--artdeco-spacing-px));
  line-height: 1.6;

  .inline-cmd {
    display: inline-block;
    margin-top: var(--artdeco-spacing-2);
    padding: var(--artdeco-spacing-1) var(--artdeco-spacing-2);
    background: color-mix(in srgb, var(--artdeco-bg-global) 85%, transparent);
    border-radius: var(--artdeco-radius-none);
    font-size: var(--artdeco-text-xs);
  }
}

.alert-content {
  strong {
    display: block;
    margin-bottom: var(--artdeco-spacing-2);
    color: var(--artdeco-fg-primary);
  }

  p {
    margin: 0 0 var(--artdeco-spacing-2) 0;
    color: var(--artdeco-fg-muted);
  }
}

.code-block {
  margin: var(--artdeco-spacing-2) 0 0 0;
  padding: var(--artdeco-spacing-3) calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px));
  overflow-x: auto;
  background: color-mix(in srgb, var(--artdeco-bg-global) 85%, transparent);
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
  border-radius: var(--artdeco-radius-none);

  code {
    color: var(--artdeco-fg-primary);
    font-family: var(--artdeco-font-accent, var(--font-mono));
    font-size: calc(var(--artdeco-text-sm) - var(--artdeco-spacing-px));
    line-height: 1.5;
  }
}
</style>
