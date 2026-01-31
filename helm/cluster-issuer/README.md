# ClusterIssuer Chart

This chart creates a cert-manager ClusterIssuer for Let's Encrypt with Cloudflare DNS-01 validation.

## Prerequisites

- cert-manager installed
- Cloudflare API token with DNS edit permissions

## Installation

1. Create Cloudflare API token secret:

```bash
kubectl create secret generic cloudflare-api-token \
  --from-literal=api-token=YOUR_CLOUDFLARE_API_TOKEN \
  -n cert-manager
```

2. Install the chart:

```bash
helm install cluster-issuer . -n cert-manager
```

## Configuration

Key values:

- `clusterIssuer.name`: Name of the ClusterIssuer (default: letsencrypt-prod)
- `clusterIssuer.certEmail`: Email for Let's Encrypt notifications
- `clusterIssuer.staging.enabled`: Use Let's Encrypt staging (default: false)
- `cloudflare.apiTokenSecretRef.name`: Name of Cloudflare API token secret
- `cloudflare.apiTokenSecretRef.key`: Key in the secret containing the token

## Usage

Create a Certificate for wildcard domain:

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: wildcard-dmytroserbeniuk-com
  namespace: gateway
spec:
  secretName: wildcard-dmytroserbeniuk-com-tls
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
  - "*.dmytroserbeniuk.com"
  - "dmytroserbeniuk.com"
```
