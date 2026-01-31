# cert-manager Umbrella Chart

This is an umbrella chart for deploying cert-manager, which provides X.509 certificate management for Kubernetes.

## Prerequisites

- Kubernetes 1.22+
- Helm 3.0+

## Installation

```bash
# Update dependencies
helm dependency update

# Install the chart
helm install cert-manager . -n cert-manager --create-namespace
```

## Configuration

The chart wraps the official cert-manager Helm chart from Jetstack.

### Key Values

- `cert-manager.enabled`: Enable/disable cert-manager (default: true)
- `cert-manager.crds.enabled`: Install CRDs (default: true)
- `cert-manager.resources`: Resource requests and limits

## Creating ClusterIssuers

After installation, create ClusterIssuers for Let's Encrypt:

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: istio
```

## Usage with Istio Gateway

Configure Certificate for Istio Gateway:

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: argocd-cert
  namespace: gateway
spec:
  secretName: argocd-tls
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
  - argocd.dmytroserbeniuk.com
```

## References

- [cert-manager Documentation](https://cert-manager.io/docs/)
- [Jetstack Helm Charts](https://github.com/cert-manager/cert-manager)
