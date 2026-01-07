<template>
  <div class="card demo-card">
    <div class="card-header">
      <span class="card-title">🌐 FLASK API SERVICE</span>
      <span class="badge badge-warning">MINIMAL</span>
    </div>

    <div class="api-section">
        <div class="alert-title">API STATUS</div>
        <div class="alert-content">
          Current <code>server.py</code> only implements welcome page, no ML prediction endpoints exposed.
          Model prediction logic only exists in <code>model.py</code> as standalone script.
        </div>
      </div>

      <h3 style="margin-top: 20px">EXISTING ENDPOINTS</h3>
      <div class="info-grid" style="margin-top: 15px">
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

      <h3 style="margin-top: 30px">SUGGESTED API ENDPOINTS</h3>
      <table class="table" style="margin-top: 15px">
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

.api-section {
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

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-4);

  .full-width {
    grid-column: span 2;
  }
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

  .method-badge {
    font-family: var(--font-mono);
    color: var(--accent-gold);
    background: rgba(212, 175, 55, 0.1);
    text-align: center;
  }

  .endpoint {
    font-family: var(--font-mono);
    color: var(--fg-primary);
  }
}

  padding: var(--spacing-4);
  border: 1px solid;

  .alert-title {
    font-family: var(--font-display);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: var(--tracking-wider);
    margin-bottom: var(--spacing-2);
  }

  .alert-content {
    font-family: var(--font-body);
    font-size: var(--font-size-small);
    line-height: 1.6;

    ol {
      margin: var(--spacing-2) 0;
      padding-left: var(--spacing-5);
    }

    li {
      margin: var(--spacing-2) 0;
    }
  }
}

  background: rgba(230, 126, 34, 0.1);
  border-color: rgba(230, 126, 34, 0.4);

  .alert-title {
    color: #E67E22;
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

.badge-warning {
  background: rgba(230, 126, 34, 0.15);
  color: #E67E22;
  border: 1px solid #E67E22;
}

.badge-danger {
  background: rgba(231, 76, 60, 0.15);
  color: #E74C3C;
  border: 1px solid #E74C3C;
}

.badge-info {
  background: rgba(74, 144, 226, 0.15);
  color: #4A90E2;
  border: 1px solid #4A90E2;
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
