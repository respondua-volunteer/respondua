# Istio Gateway Umbrella Chart

Umbrella chart для установки Istio Gateway (ingress/egress) в Kubernetes кластер.

## Описание

Этот Helm chart предоставляет удобный способ установки Istio Gateway, который обрабатывает входящий и исходящий трафик для service mesh.

## Предварительные требования

- Kubernetes 1.24+
- Helm 3.0+
- Установленные Istio Base CRDs (istio-base chart)
- Установленный Istio Control Plane (istiod chart)
- Namespace с label `istio.io/rev=default` для injection

## Установка

### Создание namespace и добавление label

```bash
kubectl create namespace gateway
kubectl label namespace gateway istio.io/rev=default
```

### Обновление зависимостей

```bash
cd /Users/dserbeniuk/projects/mcp-incident-analyst/helm/istio-gateway
helm dependency update
```

### Установка chart

```bash
helm install istio-ingressgateway . -n gateway
```

### Установка с кастомными значениями

```bash
helm install istio-ingressgateway . -n gateway -f custom-values.yaml
```

## Удаление

```bash
helm uninstall istio-ingressgateway -n gateway
```

## Конфигурация

### Основные параметры

| Параметр | Описание | Значение по умолчанию |
|----------|----------|----------------------|
| `gateway.enabled` | Включить/выключить gateway | `true` |
| `gateway.name` | Имя gateway | `istio-ingressgateway` |
| `gateway.revision` | Revision tag для gateway | `1-28-0` |
| `gateway.replicaCount` | Количество реплик | `1` |
| `gateway.autoscaling.enabled` | Включить автомасштабирование | `true` |
| `gateway.service.type` | Тип сервиса (LoadBalancer/ClusterIP/NodePort) | `LoadBalancer` |

### Пример кастомизации для production

```yaml
gateway:
  enabled: true
  replicaCount: 2
  
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70
  
  resources:
    requests:
      cpu: 500m
      memory: 512Mi
    limits:
      cpu: 2000m
      memory: 2Gi
  
  service:
    type: LoadBalancer
    annotations:
      service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
```

## Проверка установки

```bash
# Проверить статус gateway pods
kubectl get pods -n gateway

# Проверить сервис gateway
kubectl get svc -n gateway

# Проверить статус release
helm status istio-ingressgateway -n gateway

# Получить External IP (для LoadBalancer)
kubectl get svc istio-ingressgateway -n gateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

## Настройка Gateway и VirtualService

После установки создайте Gateway и VirtualService для маршрутизации трафика:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: my-gateway
  namespace: gateway
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "example.com"
---
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: my-service
  namespace: gateway
spec:
  hosts:
  - "example.com"
  gateways:
  - my-gateway
  http:
  - route:
    - destination:
        host: my-service.default.svc.cluster.local
        port:
          number: 8080
```

## Мониторинг

Gateway предоставляет метрики для Prometheus на порту 15020:

```bash
# Port-forward для доступа к метрикам
kubectl port-forward -n gateway svc/istio-ingressgateway 15020:15020

# Метрики доступны на http://localhost:15020/stats/prometheus
```

## Обновление

```bash
helm dependency update
helm upgrade istio-ingressgateway . -n gateway
```

## Troubleshooting

### Gateway pods не запускаются

Проверьте что namespace имеет label для injection:

```bash
kubectl get namespace gateway --show-labels
```

Должен быть label `istio.io/rev=default`.

### Нет External IP

Если используете LoadBalancer и External IP остается в состоянии Pending, проверьте поддержку LoadBalancer в вашем кластере или используйте NodePort:

```bash
helm upgrade istio-ingressgateway . -n gateway --set gateway.service.type=NodePort
```

## Дополнительная информация

Больше информации об Istio Gateway можно найти в [официальной документации](https://istio.io/latest/docs/tasks/traffic-management/ingress/).
