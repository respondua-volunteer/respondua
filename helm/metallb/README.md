# MetalLB Load Balancer Umbrella Chart

Umbrella chart для установки MetalLB - load balancer implementation для bare metal Kubernetes кластеров.

## Описание

MetalLB предоставляет network load-balancer для Kubernetes кластеров, которые не работают в облачных провайдерах с поддержкой LoadBalancer сервисов.

## Предварительные требования

- Kubernetes 1.24+
- Helm 3.0+
- Доступный диапазон IP адресов в вашей сети

## Установка

### Настройка IP адресов

Перед установкой убедитесь что IP адреса в `values.yaml` доступны в вашей сети:

```bash
# Проверьте что IP свободны
ping -c 2 194.163.181.240
ping -c 2 194.163.181.241
```

### Обновление зависимостей

```bash
cd /Users/dserbeniuk/projects/mcp-incident-analyst/helm/metallb
helm dependency update
```

### Установка chart

```bash
helm install metallb . -n metallb-system --create-namespace
```

### Установка с кастомными IP адресами

```bash
helm install metallb . -n metallb-system --create-namespace \
  --set metallb.configInline.address-pools[0].addresses[0]="192.168.1.240-192.168.1.250"
```

## Удаление

```bash
helm uninstall metallb -n metallb-system
```

## Конфигурация

### Основные параметры

| Параметр | Описание | Значение по умолчанию |
|----------|----------|----------------------|
| `metallb.enabled` | Включить/выключить MetalLB | `true` |
| `metallb.configInline.address-pools[].addresses` | Диапазон IP адресов для LoadBalancer | `["194.163.181.240-194.163.181.250"]` |
| `metallb.configInline.address-pools[].protocol` | Протокол (layer2 или bgp) | `layer2` |

### Пример кастомизации

```yaml
metallb:
  enabled: true
  
  configInline:
    address-pools:
    - name: default
      protocol: layer2
      addresses:
      - 192.168.1.240-192.168.1.250
    - name: production
      protocol: layer2
      addresses:
      - 192.168.2.100-192.168.2.110
```

## Проверка установки

```bash
# Проверить pods MetalLB
kubectl get pods -n metallb-system

# Проверить ConfigMap с IP пулами
kubectl get configmap -n metallb-system

# Проверить что LoadBalancer сервисы получают External IP
kubectl get svc --all-namespaces | grep LoadBalancer
```

## Использование

После установки MetalLB, все сервисы типа LoadBalancer автоматически получат External IP из настроенного пула:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8080
  selector:
    app: my-app
```

Проверить назначенный IP:

```bash
kubectl get svc my-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

## Layer2 vs BGP

**Layer2 (по умолчанию):**
- Проще в настройке
- Не требует настройки роутера
- Работает в большинстве сетей
- Один node отвечает за IP (failover при падении node)

**BGP:**
- Требует настройки BGP на роутере
- Лучший failover
- Распределение нагрузки между nodes
- Подходит для production с поддержкой BGP

## Troubleshooting

### LoadBalancer остается в Pending

Проверьте что speaker pods запущены:

```bash
kubectl get pods -n metallb-system -l component=speaker
```

Проверьте логи:

```bash
kubectl logs -n metallb-system -l component=speaker
```

### IP не доступен извне

Убедитесь что:
1. IP находится в той же подсети что и узлы кластера
2. Нет конфликта IP с другими устройствами
3. Firewall не блокирует трафик

## Дополнительная информация

- [Официальная документация MetalLB](https://metallb.universe.tf/)
- [Конфигурация Layer2](https://metallb.universe.tf/configuration/#layer-2-configuration)
- [Конфигурация BGP](https://metallb.universe.tf/configuration/#bgp-configuration)
