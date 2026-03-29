<template>
  <div class="card demo-card">
    <div class="card-header">
      <span class="card-title">📂 DATA FILES</span>
      <span class="badge badge-info">TONGDAXIN FORMAT</span>
    </div>

    <div class="data-section">
      <h3>PROJECT DATA FILES</h3>
      <table class="table table-block">
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

      <h3 class="binary-format-heading">TONGDAXIN BINARY FORMAT</h3>
      <div class="info-grid info-grid-offset">
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

      <div class="alert-card">
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

.data-section {
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

  .file-path {
    color: var(--artdeco-gold-primary);
    font-family: var(--artdeco-font-accent, var(--font-mono));
  }
}

.table-block {
  margin-top: var(--artdeco-spacing-4);
}

.binary-format-heading {
  margin-top: var(--artdeco-spacing-8);
}

.info-grid-offset {
  margin-top: var(--artdeco-spacing-4);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--artdeco-spacing-4);
}

.info-item {
  padding: var(--artdeco-spacing-4);
  background: color-mix(in srgb, var(--artdeco-gold-primary) 3%, var(--artdeco-bg-card));
  border: 1px solid color-mix(in srgb, var(--artdeco-gold-primary) 20%, transparent);
}

.info-label {
  margin-bottom: var(--artdeco-spacing-2);
  color: var(--artdeco-fg-muted);
  font-family: var(--artdeco-font-heading, var(--font-display));
  font-size: var(--artdeco-text-xs);
  letter-spacing: var(--artdeco-tracking-wider);
  text-transform: uppercase;
}

.info-value {
  color: var(--artdeco-fg-primary);
  font-family: var(--artdeco-font-body, var(--font-body));
  font-size: var(--artdeco-text-sm);

  &.code {
    color: var(--artdeco-gold-primary);
    font-family: var(--artdeco-font-accent, var(--font-mono));
  }
}

.alert-card {
  padding: var(--artdeco-spacing-4);
  border: 1px solid color-mix(in srgb, var(--artdeco-info) 40%, transparent);
  background: color-mix(in srgb, var(--artdeco-info) 10%, var(--artdeco-bg-card));

  .alert-title {
    margin-bottom: var(--artdeco-spacing-3);
    color: var(--artdeco-info);
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
      margin: var(--artdeco-spacing-3) 0;
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

code {
  display: inline;
  padding: calc(var(--artdeco-spacing-px) * 2) var(--artdeco-spacing-2);
  border-radius: var(--artdeco-radius-none);
  background: color-mix(in srgb, var(--artdeco-gold-primary) 10%, var(--artdeco-bg-card));
  color: var(--artdeco-gold-primary);
  font-family: var(--artdeco-font-accent, var(--font-mono));
}

@media (width <= 48rem) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--artdeco-spacing-2);
  }

  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>
