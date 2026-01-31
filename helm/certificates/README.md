# Certificates Chart

This chart creates TLS Certificates using cert-manager.

## Prerequisites

- cert-manager installed
- ClusterIssuer configured (letsencrypt-prod)

## Installation

```bash
helm install certificates . -n gateway --create-namespace
```

## Configuration

Key values:

- `domain`: Base domain (default: dmytroserbeniuk.com)
- `namespace`: Namespace for certificates (default: gateway)
- `clusterIssuer`: ClusterIssuer name (default: letsencrypt-prod)
- `certificates`: List of certificates to create

## Certificates Created

- `wildcard-dmytroserbeniuk-com`: Wildcard certificate for *.dmytroserbeniuk.com

## Usage with Istio Gateway

Reference the certificate in your Gateway:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: default-gateway
  namespace: gateway
spec:
  selector:
    istio: gateway
  servers:
  - port:
      number: 443
      name: https
      protocol: HTTPS
    tls:
      mode: SIMPLE
      credentialName: wildcard-dmytroserbeniuk-com-tls
    hosts:
    - "*.dmytroserbeniuk.com"
```
