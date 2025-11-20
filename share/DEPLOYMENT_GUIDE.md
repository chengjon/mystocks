# MyStocks AI生产环境部署指南

## 📋 概述

本文档详细说明MyStocks AI系统在生产环境的部署、运维和扩展方法，为mystocks_nice分支提供完整的部署参考。

**目标读者**: DevOps工程师、运维团队、系统架构师、生产环境管理员  
**实施难度**: 高级  
**前置要求**: Docker、Kubernetes、CI/CD、监控运维经验

---

## 🏗️ 生产架构概览

### 系统架构图

```yaml
# docker-compose.prod.yml - 生产环境架构
version: '3.8'

services:
  # AI核心服务
  ai-strategy-engine:
    image: mystocks/ai-strategy:latest
    environment:
      - ENV=production
      - GPU_ENABLED=true
      - REDIS_URL=redis://redis:6379
    deploy:
      replicas: 3
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ['0']
              capabilities: [gpu]
    depends_on:
      - redis
      - postgresql
      - tdengine
    networks:
      - ai-network

  # GPU加速服务
  gpu-acceleration-service:
    image: mystocks/gpu-service:latest
    environment:
      - CUDA_VISIBLE_DEVICES=0
      - RAPIDS_ENABLED=true
    deploy:
      replicas: 2
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ['0']
              capabilities: [gpu]
    networks:
      - ai-network

  # Web前端服务 (mystocks_nice分支)
  web-frontend:
    image: mystocks/web-frontend:latest
    ports:
      - "80:80"
      - "443:443"
    environment:
      - API_BASE_URL=http://api-gateway:8080
    depends_on:
      - api-gateway
    networks:
      - ai-network

  # API网关
  api-gateway:
    image: mystocks/api-gateway:latest
    ports:
      - "8080:8080"
    environment:
      - STRATEGY_SERVICE_URL=http://ai-strategy-engine:8000
      - GPU_SERVICE_URL=http://gpu-acceleration-service:8001
    networks:
      - ai-network

  # 数据服务
  postgresql:
    image: postgres:15
    environment:
      - POSTGRES_DB=mystocks
      - POSTGRES_USER=admin
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - ai-network

  tdengine:
    image: tdengine/tdengine:latest
    environment:
      - TAOS_FIRST_EP=tdengine
    volumes:
      - tdengine_data:/var/lib/taos
    networks:
      - ai-network

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - ai-network

  # 监控服务
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    networks:
      - ai-network

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - ai-network

volumes:
  postgres_data:
  tdengine_data:
  redis_data:
  grafana_data:

networks:
  ai-network:
    driver: bridge
```

---

## 🚀 CI/CD 流水线

### GitHub Actions 工作流

```yaml
# .github/workflows/deploy-production.yml
name: Deploy to Production

on:
  push:
    branches: [main, production]
    tags: ['v*']

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: mystocks

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      
      - name: Run tests
        run: |
          pytest tests/ --cov=src/ --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push'
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}
      image-digest: ${{ steps.build.outputs.digest }}
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
      
      - name: Build and push
        id: build
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  security-scan:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ needs.build.outputs.image-tag }}
          format: 'sarif'
          output: 'trivy-results.sarif'
      
      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

  deploy-staging:
    needs: [build, security-scan]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: staging
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to staging
        run: |
          echo "Deploying to staging environment..."
          # kubectl apply -f k8s/staging/
      
      - name: Run integration tests
        run: |
          echo "Running integration tests..."
          pytest tests/integration/ -v

  deploy-production:
    needs: [build, security-scan]
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/v')
    environment: production
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy to production
        run: |
          echo "Deploying to production environment..."
          # kubectl apply -f k8s/production/
      
      - name: Verify deployment
        run: |
          echo "Verifying production deployment..."
          # kubectl rollout status deployment/ai-strategy-engine
      
      - name: Notify deployment
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          channel: '#deployments'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}

  rollback:
    needs: deploy-production
    runs-on: ubuntu-latest
    if: failure()
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Rollback deployment
        run: |
          echo "Rolling back deployment..."
          # kubectl rollout undo deployment/ai-strategy-engine
```

---

## 🔧 Kubernetes 部署

### 生产环境配置

```yaml
# k8s/production/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: mystocks-prod
  labels:
    name: mystocks-prod
    environment: production

---
# k8s/production/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mystocks-config
  namespace: mystocks-prod
data:
  ENV: "production"
  LOG_LEVEL: "INFO"
  REDIS_URL: "redis://redis-service:6379"
  POSTGRES_URL: "postgresql://admin:password@postgres-service:5432/mystocks"
  TDENGINE_URL: "tdengine-service:6030"
  GPU_ENABLED: "true"
  MONITORING_ENABLED: "true"

---
# k8s/production/ai-strategy-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-strategy-engine
  namespace: mystocks-prod
  labels:
    app: ai-strategy-engine
    version: v1
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  selector:
    matchLabels:
      app: ai-strategy-engine
  template:
    metadata:
      labels:
        app: ai-strategy-engine
        version: v1
    spec:
      serviceAccountName: mystocks-sa
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
      - name: ai-strategy-engine
        image: ghcr.io/mystocks/ai-strategy:latest
        ports:
        - containerPort: 8000
          name: http
        - containerPort: 9090
          name: metrics
        env:
        - name: ENV
          valueFrom:
            configMapKeyRef:
              name: mystocks-config
              key: ENV
        - name: GPU_ENABLED
          valueFrom:
            configMapKeyRef:
              name: mystocks-config
              key: GPU_ENABLED
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
            nvidia.com/gpu: 1
          limits:
            memory: "4Gi"
            cpu: "2000m"
            nvidia.com/gpu: 1
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        volumeMounts:
        - name: config-volume
          mountPath: /app/config
      volumes:
      - name: config-volume
        configMap:
          name: mystocks-config
      nodeSelector:
        accelerator: nvidia-tesla-k80
      tolerations:
      - key: nvidia.com/gpu
        operator: Exists
        effect: NoSchedule

---
# k8s/production/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: ai-strategy-service
  namespace: mystocks-prod
  labels:
    app: ai-strategy-engine
spec:
  selector:
    app: ai-strategy-engine
  ports:
  - name: http
    port: 80
    targetPort: 8000
  - name: metrics
    port: 9090
    targetPort: 9090
  type: ClusterIP

---
# k8s/production/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ai-strategy-hpa
  namespace: mystocks-prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-strategy-engine
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60

---
# k8s/production/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mystocks-ingress
  namespace: mystocks-prod
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  tls:
  - hosts:
    - mystocks.yourcompany.com
    secretName: mystocks-tls
  rules:
  - host: mystocks.yourcompany.com
    http:
      paths:
      - path: /api/strategy
        pathType: Prefix
        backend:
          service:
            name: ai-strategy-service
            port:
              number: 80
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-frontend-service
            port:
              number: 80
```

---

## 📊 监控和告警配置

### Prometheus 配置

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'ai-strategy-engine'
    static_configs:
      - targets: ['ai-strategy-service:9090']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'gpu-acceleration-service'
    static_configs:
      - targets: ['gpu-service:9091']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-service:9121']

  - job_name: 'postgresql'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
```

### AlertManager 配置

```yaml
# monitoring/alertmanager.yml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@mystocks.com'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'
  routes:
  - match:
      severity: critical
    receiver: 'critical-alerts'
  - match:
      severity: warning
    receiver: 'warning-alerts'

receivers:
- name: 'web.hook'
  webhook_configs:
  - url: 'http://webhook-service:5000/alerts'

- name: 'critical-alerts'
  email_configs:
  - to: 'ops-team@mystocks.com'
    subject: '【严重】MyStocks AI系统告警'
    body: |
      {{ range .Alerts }}
      告警: {{ .Annotations.summary }}
      详情: {{ .Annotations.description }}
      时间: {{ .StartsAt }}
      {{ end }}
  slack_configs:
  - api_url: 'YOUR_SLACK_WEBHOOK_URL'
    channel: '#critical-alerts'
    title: 'MyStocks AI系统严重告警'
    text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'

- name: 'warning-alerts'
  email_configs:
  - to: 'dev-team@mystocks.com'
    subject: '【警告】MyStocks AI系统告警'
```

### 自定义告警规则

```yaml
# monitoring/alert_rules.yml
groups:
- name: mystocks-ai-rules
  rules:
  - alert: AIStrategyEngineDown
    expr: up{job="ai-strategy-engine"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "AI策略引擎服务不可用"
      description: "AI策略引擎服务已经宕机超过1分钟"

  - alert: GPUUtilizationHigh
    expr: nvidia_gpu_utilization > 90
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "GPU使用率过高"
      description: "GPU使用率已达到 {{ $value }}%，超过90%阈值"

  - alert: StrategyPerformanceDegraded
    expr: strategy_win_rate < 0.3
    for: 10m
    labels:
      severity: critical
    annotations:
      summary: "AI策略表现异常"
      description: "策略胜率已降至 {{ $value }}，持续超过10分钟"

  - alert: HighMemoryUsage
    expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "系统内存使用率过高"
      description: "系统内存使用率已达 {{ $value }}%，超过85%阈值"

  - alert: PostgreSQLDown
    expr: up{job="postgresql"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "PostgreSQL数据库不可用"
      description: "PostgreSQL数据库连接已中断超过1分钟"

  - alert: RedisDown
    expr: up{job="redis"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Redis缓存服务不可用"
      description: "Redis缓存服务连接已中断超过1分钟"
```

---

## 🛡️ 安全配置

### RBAC 配置

```yaml
# k8s/production/rbac.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: mystocks-sa
  namespace: mystocks-prod

---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: mystocks-prod
  name: mystocks-role
rules:
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  verbs: ["get", "list"]
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: mystocks-rolebinding
  namespace: mystocks-prod
subjects:
- kind: ServiceAccount
  name: mystocks-sa
  namespace: mystocks-prod
roleRef:
  kind: Role
  name: mystocks-role
  apiGroup: rbac.authorization.k8s.io
```

### 网络策略

```yaml
# k8s/production/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: mystocks-prod
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress

---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: ai-strategy-policy
  namespace: mystocks-prod
spec:
  podSelector:
    matchLabels:
      app: ai-strategy-engine
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: api-gateway
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
  - to:
    - podSelector:
        matchLabels:
          app: postgresql
    ports:
    - protocol: TCP
      port: 5432
```

### 密钥管理

```yaml
# k8s/production/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: mystocks-secrets
  namespace: mystocks-prod
type: Opaque
data:
  # 实际使用时应使用 kubectl create secret 动态生成
  postgres-password: cGFzc3dvcmQxMjM= # base64编码
  redis-password: cmVkaXNwYXNzd29yZA== # base64编码
  jwt-secret: eW91cl9zdXBlcl9zZWNyZXQ= # base64编码
  openai-api-key: eW91cl9vcGVuYWlfa2V5 # base64编码

---
# 使用External Secrets Operator或Vault集成
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: mystocks-secrets
  namespace: mystocks-prod
spec:
  provider:
    vault:
      server: "https://vault.yourcompany.com"
      path: "secret"
      version: "v2"
      auth:
        kubernetes:
          mountPath: "kubernetes"
          role: "mystocks-role"

---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: mystocks-external-secrets
  namespace: mystocks-prod
spec:
  refreshInterval: 15s
  secretStoreRef:
    name: mystocks-secrets
    kind: SecretStore
  target:
    creationPolicy: Owner
  data:
  - secretKey: postgres-password
    remoteRef:
      key: database
      property: password
  - secretKey: redis-password
    remoteRef:
      key: cache
      property: password
  - secretKey: jwt-secret
    remoteRef:
      key: auth
      property: jwt-secret
```

---

## 🔄 灾难恢复计划

### 数据备份策略

```bash
#!/bin/bash
# backup/backup-script.sh

set -e

BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/mystocks/${BACKUP_DATE}"

echo "开始备份 MyStocks 数据 - ${BACKUP_DATE}"

# 创建备份目录
mkdir -p "${BACKUP_DIR}"

# 1. 备份 PostgreSQL
echo "备份 PostgreSQL 数据库..."
kubectl exec -n mystocks-prod deployment/postgres -- pg_dump -U admin mystocks > "${BACKUP_DIR}/postgresql.sql"

# 2. 备份 TDengine
echo "备份 TDengine 数据..."
kubectl exec -n mystocks-prod statefulset/tdengine -- taosdump -u root -p password -o /var/lib/taos/backup_${BACKUP_DATE}

# 3. 备份 Redis
echo "备份 Redis 数据..."
kubectl exec -n mystocks-prod deployment/redis -- redis-cli --rdb /data/dump.rdb
kubectl cp mystocks-prod/$(kubectl get pods -n mystocks-prod -l app=redis -o jsonpath='{.items[0].metadata.name}'):/data/dump.rdb "${BACKUP_DIR}/redis.rdb"

# 4. 备份配置和密钥
echo "备份配置..."
kubectl get configmaps -n mystocks-prod -o yaml > "${BACKUP_DIR}/configmaps.yaml"
kubectl get secrets -n mystocks-prod -o yaml > "${BACKUP_DIR}/secrets.yaml"

# 5. 备份持久化卷
echo "备份持久化卷..."
for pvc in $(kubectl get pvc -n mystocks-prod -o jsonpath='{.items[*].metadata.name}'); do
    kubectl exec -n mystocks-prod deployment/backup-tool -- tar czf "/backup/${pvc}.tar.gz" -C /mnt/pvc "${pvc}"
    kubectl cp mystocks-prod/backup-pod:/backup/${pvc}.tar.gz "${BACKUP_DIR}/${pvc}.tar.gz"
done

# 6. 压缩并上传到对象存储
echo "上传到对象存储..."
tar czf "${BACKUP_DIR}.tar.gz" -C /backup/mystocks "${BACKUP_DATE}"
aws s3 cp "${BACKUP_DIR}.tar.gz" s3://mystocks-backups/database/

# 7. 清理本地备份
echo "清理本地备份..."
rm -rf "${BACKUP_DIR}"
rm -f "${BACKUP_DIR}.tar.gz"

# 8. 验证备份
echo "验证备份完整性..."
BACKUP_SIZE=$(aws s3 ls s3://mystocks-backups/database/ --human-readable | tail -n 1 | awk '{print $3}')
echo "备份大小: ${BACKUP_SIZE}"

echo "备份完成 - ${BACKUP_DATE}"
```

### 恢复程序

```bash
#!/bin/bash
# disaster-recovery/restore-script.sh

BACKUP_FILE=$1
if [ -z "$BACKUP_FILE" ]; then
    echo "使用方法: $0 <backup_file>"
    exit 1
fi

echo "开始恢复 MyStocks 系统 - ${BACKUP_FILE}"

# 1. 下载备份文件
echo "下载备份文件..."
aws s3 cp s3://mystocks-backups/database/${BACKUP_FILE} ./

# 2. 解压备份文件
echo "解压备份文件..."
tar xzf ${BACKUP_FILE}

# 3. 停止应用服务
echo "停止应用服务..."
kubectl scale deployment ai-strategy-engine --replicas=0 -n mystocks-prod
kubectl scale deployment gpu-acceleration-service --replicas=0 -n mystocks-prod

# 4. 恢复 PostgreSQL
echo "恢复 PostgreSQL 数据库..."
BACKUP_DIR=$(basename ${BACKUP_FILE} .tar.gz)
kubectl exec -i -n mystocks-prod deployment/postgres -- psql -U admin mystocks < "${BACKUP_DIR}/postgresql.sql"

# 5. 恢复 TDengine
echo "恢复 TDengine 数据..."
kubectl exec -n mystocks-prod statefulset/tdengine -- rm -rf /var/lib/taos/data/*
kubectl exec -n mystocks-prod statefulset/tdengine -- taosdump -u root -p password -i /var/lib/taos/backup_*

# 6. 恢复 Redis
echo "恢复 Redis 数据..."
kubectl cp "${BACKUP_DIR}/redis.rdb" mystocks-prod/$(kubectl get pods -n mystocks-prod -l app=redis -o jsonpath='{.items[0].metadata.name}'):/data/dump.rdb
kubectl exec -n mystocks-prod deployment/redis -- redis-cli --rdb /data/dump.rdb

# 7. 恢复应用服务
echo "恢复应用服务..."
kubectl scale deployment ai-strategy-engine --replicas=3 -n mystocks-prod
kubectl scale deployment gpu-acceleration-service --replicas=2 -n mystocks-prod

# 8. 验证恢复
echo "验证恢复状态..."
sleep 30
kubectl get pods -n mystocks-prod
kubectl rollout status deployment/ai-strategy-engine -n mystocks-prod

echo "恢复完成"
```

---

## 📈 性能调优

### GPU 优化配置

```python
# src/gpu/optimization/gpu_config.py
import cupy as cp
import cudf
from numba import cuda
import rmm

class GPUOptimizationManager:
    """GPU性能优化管理器"""
    
    def __init__(self):
        self.gpu_id = 0
        self.setup_memory_pool()
        self.setup_kernel_cache()
    
    def setup_memory_pool(self):
        """设置GPU内存池"""
        # 初始化RMM内存池
        rmm.reinitialize(
            pool_allocator=True,
            managed_memory=True,
            initial_pool_size=1e9,  # 1GB初始池大小
            max_pool_size=8e9,      # 8GB最大池大小
            devices=[0]
        )
        
        # 配置CuPy内存池
        cp.cuda.runtime.setDevice(self.gpu_id)
        mempool = cp.get_default_memory_pool()
        mempool.set_limit(fraction=0.8)  # 使用80% GPU内存
    
    def setup_kernel_cache(self):
        """设置内核缓存"""
        # 预编译常用内核
        @cp.fuse
        def fast_ma(data, window):
            """快速移动平均"""
            cumsum = cp.cumsum(data, dtype=cp.float32)
            cumsum[window:] = cumsum[window:] - cumsum[:-window]
            return cumsum[window - 1:] / window
        
        # 编译并缓存
        self.ma_kernel = fast_ma
        print("✅ GPU内核缓存预编译完成")
    
    def optimize_strategies(self, strategy_data):
        """优化策略计算"""
        # 使用CuDF进行GPU加速数据处理
        gpu_df = cudf.from_pandas(strategy_data)
        
        # GPU加速技术指标计算
        gpu_df['ma_20'] = gpu_df['close'].rolling(20).mean()
        gpu_df['ma_50'] = gpu_df['close'].rolling(50).mean()
        gpu_df['rsi'] = self.calculate_gpu_rsi(gpu_df['close'])
        
        return gpu_df.to_pandas()
    
    def calculate_gpu_rsi(self, prices, period=14):
        """GPU加速RSI计算"""
        prices_gpu = cp.asarray(prices.values)
        deltas = cp.diff(prices_gpu)
        
        gains = cp.where(deltas > 0, deltas, 0)
        losses = cp.where(deltas < 0, -deltas, 0)
        
        avg_gains = cp.convolve(gains, cp.ones(period), 'valid') / period
        avg_losses = cp.convolve(losses, cp.ones(period), 'valid') / period
        
        rs = avg_gains / (avg_losses + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        
        return cp.asnumpy(rsi)
```

### 数据库连接池优化

```python
# src/database/connection_pool.py
import asyncpg
import asyncio
from sqlalchemy import create_engine, pool
from sqlalchemy.pool import QueuePool
import redis.asyncio as redis
from contextlib import asynccontextmanager

class DatabaseConnectionPool:
    """数据库连接池管理器"""
    
    def __init__(self):
        self.postgres_pool = None
        self.redis_pool = None
        self.tdengine_pool = None
    
    async def initialize_pools(self):
        """初始化连接池"""
        # PostgreSQL连接池
        self.postgres_pool = await asyncpg.create_pool(
            host='postgres-service',
            port=5432,
            user='admin',
            password='password',
            database='mystocks',
            min_size=5,
            max_size=20,
            command_timeout=60
        )
        
        # Redis连接池
        self.redis_pool = redis.ConnectionPool.from_url(
            'redis://redis-service:6379',
            max_connections=20,
            retry_on_timeout=True
        )
        
        print("✅ 数据库连接池初始化完成")
    
    @asynccontextmanager
    async def get_postgres_connection(self):
        """获取PostgreSQL连接"""
        async with self.postgres_pool.acquire() as connection:
            try:
                yield connection
            except Exception as e:
                print(f"PostgreSQL连接错误: {e}")
                raise
    
    @asynccontextmanager
    async def get_redis_connection(self):
        """获取Redis连接"""
        async with redis.Redis(connection_pool=self.redis_pool) as redis_client:
            try:
                yield redis_client
            except Exception as e:
                print(f"Redis连接错误: {e}")
                raise

# 使用示例
async def example_usage():
    db_pool = DatabaseConnectionPool()
    await db_pool.initialize_pools()
    
    # 使用PostgreSQL
    async with db_pool.get_postgres_connection() as conn:
        result = await conn.fetch("SELECT * FROM ai_strategies WHERE active = true")
        print(f"策略数量: {len(result)}")
    
    # 使用Redis缓存
    async with db_pool.get_redis_connection() as redis_client:
        await redis_client.set("key", "value", ex=3600)
        value = await redis_client.get("key")
        print(f"缓存值: {value}")
```

---

## 🚀 自动化运维脚本

### 日常运维脚本

```bash
#!/bin/bash
# scripts/daily-maintenance.sh

set -e

LOG_FILE="/var/log/mystocks-maintenance.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

log() {
    echo "[$DATE] $1" | tee -a "$LOG_FILE"
}

log "开始日常维护任务"

# 1. 检查系统健康状态
log "检查Pod状态..."
kubectl get pods -n mystocks-prod -o wide

log "检查Node状态..."
kubectl get nodes -o wide

log "检查PVC状态..."
kubectl get pvc -n mystocks-prod

# 2. 检查资源使用情况
log "检查资源使用..."
kubectl top nodes
kubectl top pods -n mystocks-prod

# 3. 检查GPU状态
log "检查GPU状态..."
kubectl exec -n mystocks-prod deployment/ai-strategy-engine -- nvidia-smi

# 4. 清理过期日志
log "清理过期日志..."
find /var/log -name "*.log" -mtime +7 -delete

# 5. 备份重要配置
log "备份配置..."
kubectl get all -n mystocks-prod -o yaml > /backup/config/$(date +%Y%m%d)_mystocks-config.yaml

# 6. 更新监控指标
log "更新监控指标..."
curl -X POST http://prometheus:9090/-/reload

# 7. 检查告警状态
log "检查告警状态..."
curl -s http://alertmanager:9093/api/v1/alerts | jq '.data[].status'

# 8. 性能基准测试
log "运行性能基准测试..."
python /opt/mystocks/performance_benchmark.py

log "日常维护任务完成"
```

### 自动扩缩容脚本

```python
#!/usr/bin/env python3
# scripts/auto_scaling.py

import asyncio
import kubernetes_asyncio as k8s
import requests
import logging
from datetime import datetime

class AutoScalingManager:
    """自动扩缩容管理器"""
    
    def __init__(self):
        self.namespace = "mystocks-prod"
        self.deployment_name = "ai-strategy-engine"
        self.min_replicas = 3
        self.max_replicas = 15
        
    async def initialize(self):
        """初始化Kubernetes客户端"""
        k8s.config.load_incluster_config()
        self.api = k8s.client.AppsV1Api()
        
    async def get_current_metrics(self):
        """获取当前系统指标"""
        try:
            # 从Prometheus获取CPU使用率
            cpu_query = 'avg(rate(container_cpu_usage_seconds_total{namespace="mystocks-prod"}[5m])) * 100'
            cpu_response = requests.get(
                'http://prometheus:9090/api/v1/query',
                params={'query': cpu_query}
            )
            cpu_usage = float(cpu_response.json()['data']['result'][0]['value'][1])
            
            # 获取GPU使用率
            gpu_query = 'avg(nvidia_gpu_utilization)'
            gpu_response = requests.get(
                'http://prometheus:9090/api/v1/query',
                params={'query': gpu_query}
            )
            gpu_usage = float(gpu_response.json()['data']['result'][0]['value'][1])
            
            # 获取内存使用率
            memory_query = 'avg(container_memory_working_set_bytes{namespace="mystocks-prod"}) / avg(container_spec_memory_limit_bytes{namespace="mystocks-prod"}) * 100'
            memory_response = requests.get(
                'http://prometheus:9090/api/v1/query',
                params={'query': memory_query}
            )
            memory_usage = float(memory_response.json()['data']['result'][0]['value'][1])
            
            return {
                'cpu_usage': cpu_usage,
                'gpu_usage': gpu_usage,
                'memory_usage': memory_usage
            }
        except Exception as e:
            logging.error(f"获取指标失败: {e}")
            return None
    
    async def calculate_target_replicas(self, metrics):
        """计算目标副本数"""
        if not metrics:
            return None
        
        cpu_usage = metrics['cpu_usage']
        gpu_usage = metrics['gpu_usage']
        memory_usage = metrics['memory_usage']
        
        # 基于资源使用率的扩缩容策略
        if cpu_usage > 80 or gpu_usage > 90 or memory_usage > 85:
            # 高负载 - 增加副本
            target_replicas = min(self.max_replicas, int((cpu_usage + gpu_usage + memory_usage) / 30))
        elif cpu_usage < 30 and gpu_usage < 30 and memory_usage < 30:
            # 低负载 - 减少副本
            target_replicas = max(self.min_replicas, int((cpu_usage + gpu_usage + memory_usage) / 90))
        else:
            # 中等负载 - 保持现状
            return None
        
        return max(self.min_replicas, min(self.max_replicas, target_replicas))
    
    async def scale_deployment(self, replicas):
        """执行扩缩容"""
        try:
            # 获取当前部署
            deployment = await self.api.read_namespaced_deployment(
                name=self.deployment_name,
                namespace=self.namespace
            )
            
            current_replicas = deployment.spec.replicas
            
            if current_replicas == replicas:
                logging.info(f"副本数无需调整，当前: {current_replicas}, 目标: {replicas}")
                return False
            
            # 更新副本数
            deployment.spec.replicas = replicas
            
            await self.api.patch_namespaced_deployment(
                name=self.deployment_name,
                namespace=self.namespace,
                body=deployment
            )
            
            logging.info(f"扩缩容完成: {current_replicas} -> {replicas}")
            return True
            
        except Exception as e:
            logging.error(f"扩缩容失败: {e}")
            return False
    
    async def run_scaling_loop(self):
        """运行扩缩容循环"""
        await self.initialize()
        
        while True:
            try:
                # 获取当前指标
                metrics = await self.get_current_metrics()
                
                if metrics:
                    # 计算目标副本数
                    target_replicas = await self.calculate_target_replicas(metrics)
                    
                    if target_replicas:
                        # 执行扩缩容
                        await self.scale_deployment(target_replicas)
                
                # 等待60秒后重新检查
                await asyncio.sleep(60)
                
            except Exception as e:
                logging.error(f"扩缩容循环异常: {e}")
                await asyncio.sleep(60)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    manager = AutoScalingManager()
    asyncio.run(manager.run_scaling_loop())
```

---

## 📞 故障排查指南

### 常见问题诊断

```bash
#!/bin/bash
# scripts/troubleshoot.sh

echo "=== MyStocks AI系统故障排查 ==="

# 1. 检查核心服务状态
echo "1. 检查Pod状态..."
kubectl get pods -n mystocks-prod -o wide

# 2. 检查事件日志
echo "2. 检查事件日志..."
kubectl get events -n mystocks-prod --sort-by='.lastTimestamp'

# 3. 检查资源使用
echo "3. 检查资源使用..."
kubectl top nodes
kubectl top pods -n mystocks-prod

# 4. 检查GPU状态
echo "4. 检查GPU状态..."
kubectl exec -n mystocks-prod deployment/ai-strategy-engine -- nvidia-smi

# 5. 检查网络连接
echo "5. 检查服务连通性..."
kubectl exec -n mystocks-prod deployment/ai-strategy-engine -- curl -f http://redis-service:6379/ping
kubectl exec -n mystocks-prod deployment/ai-strategy-engine -- nc -zv postgres-service 5432

# 6. 检查日志
echo "6. 检查最近的错误日志..."
kubectl logs -n mystocks-prod deployment/ai-strategy-engine --tail=50 | grep ERROR

# 7. 检查存储
echo "7. 检查存储状态..."
kubectl get pv,pvc -n mystocks-prod

# 8. 检查网络策略
echo "8. 检查网络策略..."
kubectl get networkpolicies -n mystocks-prod

# 9. 检查Prometheus指标
echo "9. 检查Prometheus指标..."
curl -s "http://prometheus:9090/api/v1/query?query=up" | jq '.data.result'

# 10. 检查告警状态
echo "10. 检查告警状态..."
curl -s "http://alertmanager:9093/api/v1/alerts" | jq '.data[].status'

echo "=== 故障排查完成 ==="
```

---

## 📚 最佳实践总结

### 部署检查清单

- [ ] **环境准备**
  - [ ] Kubernetes集群运行正常
  - [ ] NVIDIA GPU节点配置完成
  - [ ] 存储类配置正确
  - [ ] 网络策略设置完成

- [ ] **安全配置**
  - [ ] RBAC权限配置正确
  - [ ] 密钥管理配置完成
  - [ ] 网络策略启用
  - [ ] 镜像签名验证

- [ ] **监控告警**
  - [ ] Prometheus配置正确
  - [ ] Grafana仪表板部署
  - [ ] AlertManager规则配置
  - [ ] 通知渠道测试

- [ ] **备份恢复**
  - [ ] 自动备份脚本配置
  - [ ] 恢复流程测试
  - [ ] 灾难恢复计划文档

- [ ] **性能优化**
  - [ ] GPU内存池配置
  - [ ] 数据库连接池优化
  - [ ] 缓存策略配置
  - [ ] 自动扩缩容测试

---

**文档版本**: v1.0  
**更新时间**: 2025-11-16  
**维护者**: MyStocks开发团队