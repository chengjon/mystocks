<template>
  <div class="card demo-card">
    <div class="card-header">
      <span class="card-title">⚡ PYTHON PROFILING TOOLS</span>
      <span class="badge badge-info">TOOLKIT</span>
    </div>

    <div class="profiling-section">
      <h3>PERFORMANCE TOOLS COMPARISON</h3>
      <table class="table" style="margin-top: 15px">
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

      <h3 style="margin-top: 30px">EXAMPLE COMMANDS</h3>
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

.demo-card {
  padding: var(--spacing-5);
  margin-bottom: var(--spacing-4);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-5);
  padding-bottom: var(--spacing-4);
  border-bottom: 1px solid rgba(212, 175, 55, 0.3);
}

.card-title {
  font-family: var(--font-display);
  font-size: var(--font-size-h5);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  color: var(--fg-primary);
}

.profiling-section {
  padding: var(--spacing-2) 0;

  h3 {
    font-family: var(--font-display);
    font-size: var(--font-size-body);
    color: var(--accent-gold);
    text-transform: uppercase;
    letter-spacing: var(--tracking-wider);
    margin-bottom: var(--spacing-4);
  }
}

.table {
  width: 100%;
  border-collapse: collapse;

  th {
    background: rgba(212, 175, 55, 0.1);
    color: var(--accent-gold);
    font-family: var(--font-display);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: var(--tracking-wider);
    padding: var(--spacing-3) var(--spacing-4);
    border-bottom: 2px solid var(--accent-gold);
    text-align: left;
  }

  td {
    padding: var(--spacing-3) var(--spacing-4);
    border-bottom: 1px solid rgba(212, 175, 55, 0.2);
    color: var(--fg-secondary);
    font-size: var(--font-size-small);
  }

  tr:hover td {
    background: rgba(212, 175, 55, 0.03);
  }

  .tool-name {
    font-family: var(--font-display);
    color: var(--accent-gold);
    font-weight: 600;
  }

  .usage-text {
    font-family: var(--font-mono);
    font-size: var(--font-size-xs);
  }
}

.command-examples {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--spacing-4);
  margin-top: var(--spacing-4);
}

.command-card {
  padding: var(--spacing-4);
  background: rgba(212, 175, 55, 0.03);
  border: 1px solid rgba(212, 175, 55, 0.2);

  h4 {
    font-family: var(--font-display);
    color: var(--accent-gold);
    text-transform: uppercase;
    letter-spacing: var(--tracking-wider);
    margin: 0 0 var(--spacing-3) 0;
  }
}

.command-box {
  margin-top: var(--spacing-3);
}

.command-label {
  font-family: var(--font-display);
  font-size: var(--font-size-xs);
  color: var(--fg-muted);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  margin-bottom: var(--spacing-2);
}

.command-code {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(212, 175, 55, 0.2);
  border-radius: 0;
  padding: var(--spacing-3);
  font-family: var(--font-mono);
  font-size: var(--font-size-small);
  line-height: 1.6;
  color: var(--fg-primary);
  white-space: pre-wrap;
  margin: 0;
}

.command-desc {
  margin-top: var(--spacing-3);
  font-family: var(--font-body);
  font-size: var(--font-size-small);
  color: var(--fg-muted);
  line-height: 1.5;
}

  padding: var(--spacing-4);
  border: 1px solid;

  .alert-title {
    font-family: var(--font-display);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: var(--tracking-wider);
    margin-bottom: var(--spacing-3);
  }

  .alert-content {
    font-family: var(--font-body);
    font-size: var(--font-size-small);
    line-height: 1.8;

    ol {
      margin: var(--spacing-2) 0;
      padding-left: var(--spacing-5);
    }

    li {
      margin: var(--spacing-2) 0;
    }
  }
}

  background: rgba(39, 174, 96, 0.1);
  border-color: rgba(39, 174, 96, 0.4);

  .alert-title {
    color: #27AE60;
  }
}

.badge {
  display: inline-block;
  padding: 4px 10px;
  font-family: var(--font-display);
  font-size: var(--font-size-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  border-radius: 0;
}

.badge-info {
  background: rgba(74, 144, 226, 0.15);
  color: #4A90E2;
  border: 1px solid #4A90E2;
}

.badge-warning {
  background: rgba(230, 126, 34, 0.15);
  color: #E67E22;
  border: 1px solid #E67E22;
}

.badge-success {
  background: rgba(39, 174, 96, 0.15);
  color: #27AE60;
  border: 1px solid #27AE60;
}

.badge-danger {
  background: rgba(231, 76, 60, 0.15);
  color: #E74C3C;
  border: 1px solid #E74C3C;
}

code {
  background: rgba(212, 175, 55, 0.1);
  padding: 2px 6px;
  border-radius: 0;
  font-family: var(--font-mono);
  color: var(--accent-gold);
  display: inline;
}
</style>
