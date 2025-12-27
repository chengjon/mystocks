# MyStocks Operations Manual

## Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Load Balancer                        │
└────────────────────────┬────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
   ┌─────────┐     ┌─────────┐     ┌─────────┐
   │API Pod 1│     │API Pod 2│     │API Pod N│
   └─────────┘     └─────────┘     └─────────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
     ┌──────────┬───────┴───────┬──────────┐
     ▼          ▼               ▼          ▼
  ┌──────┐  ┌──────┐       ┌──────┐   ┌──────┐
  │Redis │  │ PG   │       │TDeng │   │Monitor│
  └──────┘  └──────┘       └──────┘   └──────┘
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| mystocks-api | 8000 | Main API server |
| redis | 6379 | Cache server |
| prometheus | 9090 | Metrics |

## Daily Operations

### Morning Checklist

```bash
# Check pod status
kubectl get pods -n mystocks

# Check resource usage
kubectl top pods -n mystocks

# Check application health
curl -f http://api.mystocks.example.com/health
```

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Database health
curl http://localhost:8000/api/health/database

# Cache health
redis-cli ping
```

## Incident Response

### Severity Levels

| Level | Description | Response Time |
|-------|-------------|---------------|
| P1 Critical | Complete outage | 15 min |
| P2 High | Major feature broken | 1 hour |
| P3 Medium | Minor issue | 4 hours |
| P4 Low | Cosmetic | 24 hours |

### Rollback Procedure

```bash
# Rollback to previous version
kubectl rollout undo deployment/mystocks-api -n mystocks

# Monitor rollout
kubectl rollout status deployment/mystocks-api -n mystocks
```

## Maintenance Procedures

### Deployment

```bash
# Deploy new version
kubectl set image deployment/mystocks-api \
  mystocks-api=mystocks/api:v1.0.1 -n mystocks

# Verify health
curl -f http://api.mystocks.example.com/health
```

### Database Maintenance

```sql
-- Check table sizes
SELECT relname, pg_size_pretty(pg_relation_size(relid))
FROM pg_stat_user_tables
ORDER BY pg_relation_size(relid) DESC;

-- Analyze tables
VACUUM ANALYZE;
```

## Troubleshooting

### High Latency

```bash
# Check API latency
curl -w "\nTotal: %{time_total}s\n" http://api.mystocks.example.com/health

# Check cache hit rate
curl http://api.mystocks.example.com/metrics | grep cache_hit

# Check resource usage
kubectl top pods -n mystocks
```

### High Error Rate

```bash
# Check recent errors
kubectl logs -n mystocks -l app=mystocks-api --tail=500 | grep -i error

# Check 5xx responses
kubectl logs -n mystocks -l app=mystocks-api --tail=500 | grep "500\|502\|503"
```

## Runbooks

### Runbook: High CPU Usage

1. Check resource usage
   ```bash
   kubectl top pods -n mystocks
   ```

2. Scale up if needed
   ```bash
   kubectl scale deployment/mystocks-api -n mystocks --replicas=10
   ```

### Runbook: Database Connection Pool Exhausted

1. Check pool metrics
   ```bash
   curl http://api.mystocks.example.com/metrics | grep db_pool
   ```

2. Fixes
   - Increase pool size
   - Optimize slow queries
   - Add database index

## Contact

| Role | Contact |
|------|---------|
| On-Call | PagerDuty: +1-555-0100 |
| Platform | platform@mystocks.example.com |

## Quick Reference

```bash
# View all pods
kubectl get pods -n mystocks

# View logs
kubectl logs -f deployment/mystocks-api -n mystocks

# Restart service
kubectl rollout restart deployment/mystocks-api -n mystocks

# Scale service
kubectl scale deployment/mystocks-api -n mystocks --replicas=5
```
