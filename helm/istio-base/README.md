# Istio Base CRDs Umbrella Chart

Umbrella chart для установки Istio Base CRDs в Kubernetes кластер.

## Описание

Этот Helm chart предоставляет удобный способ установки Istio Base CRDs (Custom Resource Definitions), которые являются основой для работы Istio service mesh.

## Компоненты

- **base**: Официальный Istio base chart с CRDs

## Предварительные требования

- Kubernetes 1.24+
- Helm 3.0+

## Установка

### Обновление зависимостей

```bash
cd /Users/dserbeniuk/projects/mcp-incident-analyst/helm/istio-base
helm dependency update
```

### Установка chart

```bash
helm install istio-base . -n istio-system --create-namespace
```

### Установка с кастомными значениями

```bash
helm install istio-base . -n istio-system --create-namespace -f custom-values.yaml
```

## Удаление

```bash
helm uninstall istio-base -n istio-system
```

## Конфигурация

### Основные параметры

| Параметр | Описание | Значение по умолчанию |
|----------|----------|----------------------|
| `base.enabled` | Включить/выключить base chart | `true` |
| `base._internal_defaults_do_not_set.global.istioNamespace` | Namespace для Istio | `istio-system` |
| `base._internal_defaults_do_not_set.base.enableCRDTemplates` | Включить управление CRDs через Helm | `true` |
| `base._internal_defaults_do_not_set.base.enableIstioConfigCRDs` | Включить Istio config CRDs | `true` |

### Пример кастомизации

```yaml
base:
  enabled: true
  _internal_defaults_do_not_set:
    global:
      istioNamespace: custom-istio-system
      imagePullSecrets:
        - name: my-registry-secret
    base:
      excludedCRDs:
        - "envoyfilters.networking.istio.io"
```

## Проверка установки

```bash
# Проверить установленные CRDs
kubectl get crds | grep istio

# Проверить статус release
helm status istio-base -n istio-system

# Проверить все ресурсы
kubectl get all -n istio-system
```

## Обновление

```bash
helm dependency update
helm upgrade istio-base . -n istio-system
```

## Дополнительная информация

Больше информации об Istio можно найти в [официальной документации](https://istio.io/).
