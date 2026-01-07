<template>
  <div class="card demo-card">
    <div class="card-header">
      <span class="card-title">📂 DATA FILES</span>
      <span class="badge badge-info">TONGDAXIN FORMAT</span>
    </div>

    <div class="data-section">
      <h3>PROJECT DATA FILES</h3>
      <table class="table" style="margin-top: 15px">
        <thead>
          <tr>
            <th>FILE PATH</th>
            <th>FORMAT</th>
            <th>DESCRIPTION</th>
            <th>PURPOSE</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="file in dataFiles" :key="file.file">
            <td class="file-path">{{ file.file }}</td>
            <td><span class="badge badge-warning">{{ file.format }}</span></td>
            <td>{{ file.description }}</td>
            <td>{{ file.size }}</td>
          </tr>
        </tbody>
      </table>

      <h3 style="margin-top: 30px">TONGDAXIN BINARY FORMAT</h3>
      <div class="info-grid" style="margin-top: 15px">
        <div class="info-item">
          <div class="info-label">FILE FORMAT</div>
          <div class="info-value">32-byte fixed structure (struct)</div>
        </div>
        <div class="info-item">
          <div class="info-label">PARSING METHOD</div>
          <div class="info-value code">struct.unpack('IIIIIfII', ...)</div>
        </div>
        <div class="info-item">
          <div class="info-label">PRICE FIELDS</div>
          <div class="info-value">open/high/low/close stored as integers, divide by 100</div>
        </div>
        <div class="info-item">
          <div class="info-label">OUTPUT COLUMNS</div>
          <div class="info-value code">['code', 'tradeDate', 'open', 'high', 'low', 'close', 'amount', 'vol']</div>
        </div>
      </div>

        <div class="alert-title">DATA PROCESSING FLOW</div>
        <div class="alert-content">
          <strong>Conversion steps:</strong>
          <ol>
            <li><code>utils.read_tdx_day_file()</code> - Read .day binary files</li>
            <li>Parse to OHLCV DataFrame (sh000001.csv)</li>
            <li><code>utils.gen_model_datum(step=10)</code> - Generate rolling window features</li>
            <li>Export feature file (sh000001_10.csv) for model training</li>
          </ol>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { DATA_FILES } from '../config'

const dataFiles = DATA_FILES
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

.data-section {
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

  .file-path {
    font-family: var(--font-mono);
    color: var(--accent-gold);
  }
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-4);
}

.info-item {
  padding: var(--spacing-4);
  background: rgba(212, 175, 55, 0.03);
  border: 1px solid rgba(212, 175, 55, 0.2);
}

.info-label {
  font-family: var(--font-display);
  font-size: var(--font-size-xs);
  color: var(--fg-muted);
  text-transform: uppercase;
  letter-spacing: var(--tracking-wider);
  margin-bottom: var(--spacing-2);
}

.info-value {
  font-family: var(--font-body);
  color: var(--fg-primary);
  font-size: var(--font-size-small);

  &.code {
    font-family: var(--font-mono);
    color: var(--accent-gold);
  }
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
      margin: var(--spacing-3) 0;
      padding-left: var(--spacing-5);
    }

    li {
      margin: var(--spacing-2) 0;
    }
  }
}

  background: rgba(74, 144, 226, 0.1);
  border-color: rgba(74, 144, 226, 0.4);

  .alert-title {
    color: #4A90E2;
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

code {
  background: rgba(212, 175, 55, 0.1);
  padding: 2px 6px;
  border-radius: 0;
  font-family: var(--font-mono);
  color: var(--accent-gold);
  display: inline;
}
</style>
