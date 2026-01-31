# Metrics Server Umbrella Chart

Umbrella Helm chart for Kubernetes Metrics Server - enables resource metrics API for HPA and `kubectl top`.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+

## Installation

### Update dependencies

```bash
cd helm/metrics-server
helm dependency update
```

### Install the chart

```bash
# Using ArgoCD
kubectl apply -f helm/argo-apps/metrics-server-app.yaml

# Or manually
helm install metrics-server . -n kube-system
```

## Verify Installation

```bash
# Check if metrics-server is running
kubectl get pods -n kube-system -l app.kubernetes.io/name=metrics-server

# Test metrics API
kubectl top nodes
kubectl top pods -A
```

## Configuration

### Key Values

| Parameter | Description | Default |
|-----------|-------------|---------|
| `metrics-server.resources.requests.cpu` | CPU request | `100m` |
| `metrics-server.resources.requests.memory` | Memory request | `200Mi` |
| `metrics-server.args` | Additional arguments | See values.yaml |
| `metrics-server.replicas` | Number of replicas | `1` |

### Important for K3s/K8s with self-signed certificates

The chart includes `--kubelet-insecure-tls` flag by default for K3s compatibility.

## Usage with HPA

Once metrics-server is running, you can create HorizontalPodAutoscaler:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 1
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Troubleshooting

### Metrics not available

```bash
# Check metrics-server logs
kubectl logs -n kube-system -l app.kubernetes.io/name=metrics-server

# Check API service
kubectl get apiservice v1beta1.metrics.k8s.io
```

### Common Issues

1. **TLS Certificate Error**: Add `--kubelet-insecure-tls` to args
2. **Unable to connect to kubelet**: Check network policies and firewall rules
3. **High memory usage**: Increase memory limits based on cluster size

## Uninstall

```bash
helm uninstall metrics-server -n kube-system
```

sleep 10 && kubectl get svc metrics-server -n kube-system && echo "---" && kubectl top nodes
NAME             TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
metrics-server   ClusterIP   10.110.37.154   <none>        443/TCP   43s
---
NAME   CPU(cores)   CPU(%)   MEMORY(bytes)   MEMORY(%)   
cp-1   783m         13%      4118Mi          34%         

~/Project/mcp-incident-analyst/helm/argo-apps main* 11s
❯  kubectl top pods -n kube-system --sort-by=memory | head -10
NAME                                      CPU(cores)   MEMORY(bytes)   
metrics-server-56fbb959d7-xzxn6           7m           17Mi            
coredns-6d668d687-7mgsp                   18m          16Mi            
local-path-provisioner-869c44bfbd-lr5bv   1m           8Mi        