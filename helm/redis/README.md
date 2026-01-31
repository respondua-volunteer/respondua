# Redis Helm Chart

Redis umbrella chart для MCP Incident Analyst проекта.

## Описание

Этот chart является оберткой (umbrella chart) над официальным Bitnami Redis chart. Предоставляет:

- **Master-Replica replication** для high availability
- **Redis Sentinel** для автоматического failover
- **Persistence** с AOF для надежности данных
- **Prometheus metrics** для мониторинга
- **Network policies** для безопасности
- **Pod Disruption Budgets** для стабильности при обновлениях
- **Horizontal autoscaling** для реплик

## Предварительные требования

- Kubernetes 1.23+
- Helm 3.8+
- PV provisioner support (для persistence)
- Prometheus Operator (опционально, для metrics)

## Установка

### Development (standalone)

```bash
# Создать namespace
kubectl create namespace redis

# Установить в standalone режиме для разработки
helm install redis . \
  --namespace redis \
  --values values-dev.yaml
```

### Production (replication + sentinel)

```bash
# Создать namespace
kubectl create namespace redis

# Создать secret с паролем
kubectl create secret generic redis-credentials \
  --from-literal=redis-password='your-strong-password' \
  --namespace redis

# Установить в production режиме
helm install redis . \
  --namespace redis \
  --values values-prod.yaml
```

## Обновление

```bash
# Обновить chart dependencies
helm dependency update

# Обновить установленный release
helm upgrade redis . \
  --namespace redis \
  --values values-prod.yaml
```

## Конфигурация

### Основные параметры

| Parameter | Description | Default |
|-----------|-------------|---------|
| `redis.enabled` | Enable Redis deployment | `true` |
| `redis.architecture` | Redis architecture (`standalone` or `replication`) | `replication` |
| `redis.auth.enabled` | Enable password authentication | `true` |
| `redis.auth.password` | Redis password | `""` |
| `redis.auth.existingSecret` | Existing secret with Redis password | `""` |

### Master configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `redis.master.count` | Number of master instances | `1` |
| `redis.master.resources.requests.cpu` | CPU request | `50m` (dev), `500m` (prod) |
| `redis.master.resources.requests.memory` | Memory request | `64Mi` (dev), `1Gi` (prod) |
| `redis.master.persistence.enabled` | Enable persistence | `true` |
| `redis.master.persistence.size` | Volume size | `1Gi` (dev), `20Gi` (prod) |

### Replica configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `redis.replica.replicaCount` | Number of replicas | `0` (dev), `3` (prod) |
| `redis.replica.resources.requests.cpu` | CPU request | `50m` (dev), `500m` (prod) |
| `redis.replica.resources.requests.memory` | Memory request | `64Mi` (dev), `1Gi` (prod) |
| `redis.replica.autoscaling.enabled` | Enable HPA | `false` (dev), `true` (prod) |
| `redis.replica.autoscaling.maxReplicas` | Max replicas for HPA | `10` |

### Sentinel configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `redis.sentinel.enabled` | Enable Sentinel | `false` (dev), `true` (prod) |
| `redis.sentinel.masterSet` | Master set name | `mcp-redis-master` |
| `redis.sentinel.quorum` | Sentinel quorum | `2` |
| `redis.sentinel.downAfterMilliseconds` | Down after milliseconds | `10000` |

### Metrics configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `redis.metrics.enabled` | Enable metrics exporter | `false` (dev), `true` (prod) |
| `redis.metrics.serviceMonitor.enabled` | Enable ServiceMonitor | `false` (dev), `true` (prod) |
| `redis.metrics.prometheusRule.enabled` | Enable PrometheusRule | `false` (dev), `true` (prod) |

## Примеры использования

### Подключение из приложения

**Python (с поддержкой Sentinel):**

```python
from redis.sentinel import Sentinel

sentinel = Sentinel([
    ('redis-node-0.redis-headless:26379',),
    ('redis-node-1.redis-headless:26379',),
    ('redis-node-2.redis-headless:26379',)
], socket_timeout=0.1)

# Получить master для записи
master = sentinel.master_for('mcp-redis-master', socket_timeout=0.1, password='your-password')
master.set('key', 'value')

# Получить replica для чтения
slave = sentinel.slave_for('mcp-redis-master', socket_timeout=0.1, password='your-password')
value = slave.get('key')
```

**Python (простое подключение):**

```python
import redis

# Development (standalone)
r = redis.Redis(
    host='redis-master',
    port=6379,
    password='your-password',
    decode_responses=True
)

# Production (через service)
r = redis.Redis(
    host='redis',
    port=6379,
    password='your-password',
    decode_responses=True
)
```

**Environment variables для authenticate service:**

```yaml
# Development
REDIS_ENABLED=true
REDIS_HOST=redis-master
REDIS_PORT=6379
REDIS_DB=0

# Production (с Sentinel)
REDIS_ENABLED=true
REDIS_SENTINELS=redis-node-0.redis-headless:26379,redis-node-1.redis-headless:26379,redis-node-2.redis-headless:26379
REDIS_MASTER_SET=mcp-redis-master
REDIS_DB=0
```

## Мониторинг

### Metrics endpoints

- Master: `http://redis-master:9121/metrics`
- Replicas: `http://redis-replicas:9121/metrics`

### Grafana Dashboard

Импортируйте dashboard ID: `763` (Redis Dashboard for Prometheus Redis Exporter)

### Основные метрики

- `redis_up` - Redis instance status
- `redis_connected_clients` - Number of connected clients
- `redis_memory_used_bytes` - Memory usage
- `redis_commands_processed_total` - Total commands processed
- `redis_connected_slaves` - Number of connected replicas
- `redis_evicted_keys_total` - Number of evicted keys

## Troubleshooting

### Проверка статуса

```bash
# Проверить pods
kubectl get pods -n redis

# Проверить services
kubectl get svc -n redis

# Проверить logs
kubectl logs -n redis redis-master-0
kubectl logs -n redis redis-replicas-0
```

### Подключение к Redis CLI

```bash
# Development
kubectl exec -it -n redis redis-master-0 -- redis-cli -a your-password

# Production (через sentinel)
kubectl exec -it -n redis redis-node-0 -- redis-cli -p 26379
```

### Проверка replication

```bash
# В Redis CLI
INFO replication

# Ожидаемый output:
# role:master
# connected_slaves:3
# slave0:ip=10.244.1.5,port=6379,state=online,offset=123456
```

## Backup и Recovery

### Backup

```bash
# AOF файлы автоматически сохраняются в PVC
# Для backup просто копируйте PVC

# Или используйте Redis SAVE command
kubectl exec -it -n redis redis-master-0 -- redis-cli -a password BGSAVE
```

### Recovery

```bash
# Восстановите PVC из backup
# Redis автоматически загрузит AOF при старте
```

## Безопасность

1. **Используйте сильные пароли** в production
2. **Включите TLS** для production
3. **Настройте Network Policies** для ограничения доступа
4. **Регулярно обновляйте** Redis image
5. **Мониторьте метрики безопасности**

## Дополнительная информация

- [Bitnami Redis Chart Documentation](https://github.com/bitnami/charts/tree/main/bitnami/redis)
- [Redis Documentation](https://redis.io/documentation)
- [Redis Sentinel Documentation](https://redis.io/docs/management/sentinel/)
