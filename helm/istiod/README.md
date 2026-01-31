# Istiod Control Plane Umbrella Chart

Umbrella chart для установки Istio Control Plane (istiod) в Kubernetes кластер.

## Описание

Этот Helm chart предоставляет удобный способ установки Istio Control Plane (istiod), который управляет конфигурацией и координирует работу service mesh.

## Предварительные требования

- Kubernetes 1.24+
- Helm 3.0+
- Установленные Istio Base CRDs (istio-base chart)

## Установка

### Обновление зависимостей

```bash
cd /Users/dserbeniuk/projects/mcp-incident-analyst/helm/istiod
helm dependency update
```

### Установка chart

```bash
# Сначала убедитесь что установлен istio-base
helm install istio-base ../istio-base -n istio-system --create-namespace

# Затем установите istiod
helm install istiod . -n istio-system
```

### Установка с кастомными значениями

```bash
helm install istiod . -n istio-system -f custom-values.yaml
```

## Удаление

```bash
helm uninstall istiod -n istio-system
```

## Конфигурация

### Основные параметры

| Параметр | Описание | Значение по умолчанию |
|----------|----------|----------------------|
| `istiod.enabled` | Включить/выключить istiod chart | `true` |
| `istiod.global.istioNamespace` | Namespace для Istio | `istio-system` |
| `istiod.pilot.replicaCount` | Количество реплик istiod | `1` |
| `istiod.pilot.autoscaleEnabled` | Включить автомасштабирование | `true` |
| `istiod.pilot.autoscaleMin` | Минимум реплик при автомасштабировании | `1` |
| `istiod.pilot.autoscaleMax` | Максимум реплик при автомасштабировании | `5` |

### Пример кастомизации

```yaml
istiod:
  enabled: true
  global:
    istioNamespace: istio-system
  pilot:
    replicaCount: 2
    resources:
      requests:
        cpu: 1000m
        memory: 4096Mi
    autoscaleEnabled: true
    autoscaleMin: 2
    autoscaleMax: 10
```

## Проверка установки

```bash
# Проверить статус istiod pods
kubectl get pods -n istio-system

# Проверить статус release
helm status istiod -n istio-system

# Проверить логи istiod
kubectl logs -n istio-system -l app=istiod

# Проверить работу control plane
istioctl verify-install
```

## Мониторинг

После установки istiod предоставляет метрики для Prometheus:

```bash
# Port-forward для доступа к метрикам
kubectl port-forward -n istio-system svc/istiod 15014:15014

# Метрики доступны на http://localhost:15014/metrics
```

## Обновление

```bash
helm dependency update
helm upgrade istiod . -n istio-system
```

## Дополнительная информация

Больше информации об Istio можно найти в [официальной документации](https://istio.io/).
