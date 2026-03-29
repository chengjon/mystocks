<template>
  <div class="card demo-card">
    <div class="card-header">
      <span class="card-title">🌐 FLASK API SERVICE</span>
      <span class="badge badge-warning">MINIMAL</span>
    </div>

    <div class="api-section">
      <div class="alert-card status-card">
        <div class="alert-title">API STATUS</div>
        <div class="alert-content">
          Current <code>server.py</code> only implements welcome page, no ML prediction endpoints exposed.
          Model prediction logic only exists in <code>model.py</code> as standalone script.
        </div>
      </div>

      <h3 class="section-heading">EXISTING ENDPOINTS</h3>
      <div class="info-grid info-grid-offset">
        <div class="info-item">
          <div class="info-label">SERVICE ADDRESS</div>
          <div class="info-value">http://localhost:5000</div>
        </div>
        <div class="info-item">
          <div class="info-label">ENDPOINT</div>
          <div class="info-value code">GET /</div>
        </div>
        <div class="info-item full-width">
          <div class="info-label">RESPONSE</div>
          <div class="info-value">"Welcome to Tongdaxin Data Analysis"</div>
        </div>
      </div>

      <h3 class="section-heading section-heading-spaced">SUGGESTED API ENDPOINTS</h3>
      <table class="table table-block">
        <thead>
          <tr>
            <th>METHOD</th>
            <th>ENDPOINT</th>
            <th>DESCRIPTION</th>
            <th>PRIORITY</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="api in suggestedAPIs" :key="api.endpoint">
            <td class="method-badge">{{ api.method }}</td>
            <td class="endpoint">{{ api.endpoint }}</td>
            <td>{{ api.description }}</td>
            <td>
              <span class="badge" :class="api.priority === '高' ? 'badge-danger' : 'badge-info'">
                {{ api.priority }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>

      <div class="alert-card">
        <div class="alert-title">INTEGRATION RECOMMENDATIONS</div>
        <div class="alert-content">
          <strong>Recommended PyProfiling Integration:</strong>
          <ol>
            <li>Create <code>/api/ml/predict</code> endpoint in backend API</li>
            <li>Integrate LightGBM model training and prediction logic</li>
            <li>Support Tongdaxin data auto-parsing and feature engineering</li>
            <li>Provide performance analysis API for model optimization monitoring</li>
          </ol>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { SUGGESTED_APIS } from '../config'

const suggestedAPIs = SUGGESTED_APIS
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

.api-section {
  padding: var(--artdeco-spacing-2) 0;
}

.section-heading {
  margin-bottom: var(--artdeco-spacing-4);
  color: var(--artdeco-gold-primary);
  font-family: var(--artdeco-font-heading, var(--font-display));
  font-size: var(--artdeco-text-base);
  letter-spacing: var(--artdeco-tracking-wider);
  text-transform: uppercase;
}

.section-heading-spaced {
  margin-top: var(--artdeco-spacing-8);
}

.info-grid-offset {
  margin-top: var(--artdeco-spacing-4);
}

.table-block {
  margin-top: var(--artdeco-spacing-4);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--artdeco-spacing-4);

  .full-width {
    grid-column: span 2;
  }
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

  .method-badge {
    background: color-mix(in srgb, var(--artdeco-gold-primary) 10%, var(--artdeco-bg-card));
    color: var(--artdeco-gold-primary);
    font-family: var(--artdeco-font-accent, var(--font-mono));
    text-align: center;
  }

  .endpoint {
    color: var(--artdeco-fg-primary);
    font-family: var(--artdeco-font-accent, var(--font-mono));
  }
}

.alert-card {
  padding: var(--artdeco-spacing-4);
  border: 1px solid color-mix(in srgb, var(--artdeco-warning) 40%, transparent);
  background: color-mix(in srgb, var(--artdeco-warning) 10%, var(--artdeco-bg-card));

  .alert-title {
    margin-bottom: var(--artdeco-spacing-2);
    color: var(--artdeco-warning);
    font-family: var(--artdeco-font-heading, var(--font-display));
    font-weight: var(--artdeco-font-semibold);
    letter-spacing: var(--artdeco-tracking-wider);
    text-transform: uppercase;
  }

  .alert-content {
    font-family: var(--artdeco-font-body, var(--font-body));
    font-size: var(--artdeco-text-sm);
    line-height: 1.6;

    ol {
      margin: var(--artdeco-spacing-2) 0;
      padding-left: var(--artdeco-spacing-5);
    }

    li {
      margin: var(--artdeco-spacing-2) 0;
    }
  }
}

.status-card {
  border-color: color-mix(in srgb, var(--artdeco-info) 40%, transparent);
  background: color-mix(in srgb, var(--artdeco-info) 10%, var(--artdeco-bg-card));

  .alert-title {
    color: var(--artdeco-info);
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

.badge-warning {
  border: 1px solid color-mix(in srgb, var(--artdeco-warning) 40%, transparent);
  background: color-mix(in srgb, var(--artdeco-warning) 15%, var(--artdeco-bg-card));
  color: var(--artdeco-warning);
}

.badge-danger {
  border: 1px solid color-mix(in srgb, var(--artdeco-down) 40%, transparent);
  background: color-mix(in srgb, var(--artdeco-down) 15%, var(--artdeco-bg-card));
  color: var(--artdeco-down);
}

.badge-info {
  border: 1px solid color-mix(in srgb, var(--artdeco-info) 40%, transparent);
  background: color-mix(in srgb, var(--artdeco-info) 15%, var(--artdeco-bg-card));
  color: var(--artdeco-info);
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

    .full-width {
      grid-column: span 1;
    }
  }
}
</style>
