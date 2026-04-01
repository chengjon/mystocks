<template>
  <div class="card demo-card">
    <div class="card-header">
      <span class="card-title">⚡ PYTHON PROFILING TOOLS</span>
      <span class="badge badge-info">TOOLKIT</span>
    </div>

    <div class="profiling-section">
      <h3>PERFORMANCE TOOLS COMPARISON</h3>
      <table class="table profiling-table-offset">
        <thead>
          <tr>
            <th>TOOL</th>
            <th>GRANULARITY</th>
            <th>USAGE</th>
            <th>OUTPUT</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="tool in profilingTools" :key="tool.tool">
            <td class="tool-name">{{ tool.tool }}</td>
            <td><span class="badge" :class="getLevelBadgeClass(tool.level)">{{ tool.level }}</span></td>
            <td class="usage-text">{{ tool.usage }}</td>
            <td>{{ tool.output }}</td>
          </tr>
        </tbody>
      </table>

      <h3 class="profiling-section-heading">EXAMPLE COMMANDS</h3>
      <div class="command-examples">
        <div class="card command-card" v-for="cmd in profilingCommands" :key="cmd.tool">
          <h4>{{ cmd.tool }}</h4>
          <div class="command-box">
            <div class="command-label">COMMAND</div>
            <pre class="command-code">{{ cmd.command }}</pre>
          </div>
          <p class="command-desc">{{ cmd.description }}</p>
        </div>
      </div>

      <div class="alert-card">
        <div class="alert-title">OPTIMIZATION WORKFLOW</div>
        <div class="alert-content">
          <ol>
            <li>Use <code>cProfile</code> to quickly identify performance bottlenecks</li>
            <li>Use <code>line_profiler</code> for line-by-line analysis</li>
            <li>Use <code>memory_profiler</code> to check memory usage</li>
            <li>Use <code>timeit</code> to compare before/after optimization</li>
          </ol>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { PROFILING_TOOLS, PROFILING_COMMANDS } from '../config'

const profilingTools = PROFILING_TOOLS
const profilingCommands = PROFILING_COMMANDS

const getLevelBadgeClass = (level: string) => {
  const classes: Record<string, string> = {
    '粗粒度': 'badge-info',
    '语句级': 'badge-warning',
    '函数级': 'badge-success',
    '行级': 'badge-danger'
  }
  return classes[level] || 'badge-info'
}
</script>

<style scoped lang="scss">
@use '../../../../styles/artdeco-tokens.scss' as *;

.demo-card {
  padding: var(--artdeco-spacing-5);
  margin-bottom: var(--artdeco-spacing-4);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-5);
  padding-bottom: var(--artdeco-spacing-4);
  border-bottom: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 30%, transparent);
}

.card-title {
  color: var(--artdeco-fg-primary);
  font-family: var(--artdeco-font-heading, var(--font-display));
  font-size: var(--artdeco-text-lg);
  font-weight: var(--artdeco-font-semibold);
  letter-spacing: var(--artdeco-tracking-wider);
  text-transform: uppercase;
}

.profiling-section {
  padding: var(--artdeco-spacing-2) 0;

  h3 {
    margin-bottom: var(--artdeco-spacing-4);
    color: var(--artdeco-gold-primary);
    font-family: var(--artdeco-font-heading, var(--font-display));
    font-size: var(--artdeco-text-base);
    letter-spacing: var(--artdeco-tracking-wider);
    text-transform: uppercase;
  }
}

.table {
  width: 100%;
  border-collapse: collapse;

  th {
    padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
    border-bottom: calc(var(--artdeco-spacing-px) * 2) solid var(--artdeco-gold-primary);
    background: color-mix(in srgb, var(--artdeco-gold-primary) 10%, var(--artdeco-bg-card));
    color: var(--artdeco-gold-primary);
    font-family: var(--artdeco-font-heading, var(--font-display));
    font-weight: var(--artdeco-font-semibold);
    letter-spacing: var(--artdeco-tracking-wider);
    text-align: left;
    text-transform: uppercase;
  }

  td {
    padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
    border-bottom: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
    color: var(--artdeco-fg-muted);
    font-size: var(--artdeco-text-sm);
  }

  tr:hover td {
    background: color-mix(in srgb, var(--artdeco-gold-primary) 3%, transparent);
  }

  .tool-name {
    color: var(--artdeco-gold-primary);
    font-family: var(--artdeco-font-heading, var(--font-display));
    font-weight: var(--artdeco-font-semibold);
  }

  .usage-text {
    font-family: var(--artdeco-font-accent, var(--font-mono));
    font-size: var(--artdeco-text-xs);
  }
}

.profiling-table-offset {
  margin-top: calc(var(--artdeco-spacing-5) - var(--artdeco-spacing-px) * 5);
}

.profiling-section-heading {
  margin-top: calc(var(--artdeco-spacing-6) + var(--artdeco-spacing-3) / 2);
}

.command-examples {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--artdeco-spacing-4);
  margin-top: var(--artdeco-spacing-4);
}

.command-card {
  padding: var(--artdeco-spacing-4);
  background: color-mix(in srgb, var(--artdeco-gold-primary) 3%, var(--artdeco-bg-card));
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);

  h4 {
    margin: 0 0 var(--artdeco-spacing-3) 0;
    color: var(--artdeco-gold-primary);
    font-family: var(--artdeco-font-heading, var(--font-display));
    letter-spacing: var(--artdeco-tracking-wider);
    text-transform: uppercase;
  }
}

.command-box {
  margin-top: var(--artdeco-spacing-3);
}

.command-label {
  margin-bottom: var(--artdeco-spacing-2);
  color: var(--artdeco-fg-muted);
  font-family: var(--artdeco-font-heading, var(--font-display));
  font-size: var(--artdeco-text-xs);
  letter-spacing: var(--artdeco-tracking-wider);
  text-transform: uppercase;
}

.command-code {
  margin: 0;
  padding: var(--artdeco-spacing-3);
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
  border-radius: var(--artdeco-radius-none);
  background: color-mix(in srgb, var(--artdeco-bg-global) 85%, transparent);
  color: var(--artdeco-fg-primary);
  font-family: var(--artdeco-font-accent, var(--font-mono));
  font-size: var(--artdeco-text-sm);
  line-height: 1.6;
  white-space: pre-wrap;
}

.command-desc {
  margin-top: var(--artdeco-spacing-3);
  color: var(--artdeco-fg-muted);
  font-family: var(--artdeco-font-body, var(--font-body));
  font-size: var(--artdeco-text-sm);
  line-height: 1.5;
}

.alert-card {
  padding: var(--artdeco-spacing-4);
  border: 1px solid color-mix(in srgb, var(--artdeco-success) 40%, transparent);
  background: color-mix(in srgb, var(--artdeco-success) 10%, var(--artdeco-bg-card));

  .alert-title {
    margin-bottom: var(--artdeco-spacing-3);
    color: var(--artdeco-success);
    font-family: var(--artdeco-font-heading, var(--font-display));
    font-weight: var(--artdeco-font-semibold);
    letter-spacing: var(--artdeco-tracking-wider);
    text-transform: uppercase;
  }

  .alert-content {
    font-family: var(--artdeco-font-body, var(--font-body));
    font-size: var(--artdeco-text-sm);
    line-height: 1.8;

    ol {
      margin: var(--artdeco-spacing-2) 0;
      padding-left: var(--artdeco-spacing-5);
    }

    li {
      margin: var(--artdeco-spacing-2) 0;
    }
  }
}

.badge {
  display: inline-block;
  padding: var(--artdeco-spacing-1) var(--artdeco-spacing-3);
  border-radius: var(--artdeco-radius-none);
  font-family: var(--artdeco-font-heading, var(--font-display));
  font-size: var(--artdeco-text-xs);
  font-weight: var(--artdeco-font-semibold);
  letter-spacing: var(--artdeco-tracking-wider);
  text-transform: uppercase;
}

.badge-info {
  border: 1px solid color-mix(in srgb, var(--artdeco-info) 40%, transparent);
  background: color-mix(in srgb, var(--artdeco-info) 15%, var(--artdeco-bg-card));
  color: var(--artdeco-info);
}

.badge-warning {
  border: 1px solid color-mix(in srgb, var(--artdeco-warning) 40%, transparent);
  background: color-mix(in srgb, var(--artdeco-warning) 15%, var(--artdeco-bg-card));
  color: var(--artdeco-warning);
}

.badge-success {
  border: 1px solid color-mix(in srgb, var(--artdeco-success) 40%, transparent);
  background: color-mix(in srgb, var(--artdeco-success) 15%, var(--artdeco-bg-card));
  color: var(--artdeco-success);
}

.badge-danger {
  border: 1px solid color-mix(in srgb, var(--artdeco-down) 40%, transparent);
  background: color-mix(in srgb, var(--artdeco-down) 15%, var(--artdeco-bg-card));
  color: var(--artdeco-down);
}

code {
  display: inline;
  padding: calc(var(--artdeco-spacing-px) * 2) var(--artdeco-spacing-2);
  border-radius: var(--artdeco-radius-none);
  background: color-mix(in srgb, var(--artdeco-gold-primary) 10%, var(--artdeco-bg-card));
  color: var(--artdeco-gold-primary);
  font-family: var(--artdeco-font-accent, var(--font-mono));
}
</style>
