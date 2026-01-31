# Create Required Secrets for Respondua

## 1. AWS ECR Credentials

Create secret for pulling images from AWS ECR:

```bash
export KUBECONFIG=~/.kube/respondua

# Get ECR login token
aws ecr get-login-password --region eu-central-1 | kubectl create secret docker-registry ecr-credentials \
  --docker-server=420779746987.dkr.ecr.eu-central-1.amazonaws.com \
  --docker-username=AWS \
  --docker-password="$(cat -)" \
  -n respondua
```

**Note:** ECR tokens expire after 12 hours. Consider using ECR credential helper or refresh token periodically.

## 2. Application Secrets

Create secret with Django and AWS credentials:

```bash
export KUBECONFIG=~/.kube/respondua

kubectl create secret generic respondua-secrets \
  --from-literal=SECRET_KEY="$(openssl rand -base64 50)" \
  --from-literal=POSTGRES_PASSWORD="your-postgres-password" \
  --from-literal=AWS_ACCESS_KEY_ID="your-aws-access-key" \
  --from-literal=AWS_SECRET_ACCESS_KEY="your-aws-secret-key" \
  -n web
```

## 3. Get PostgreSQL Password

If you need the PostgreSQL password from existing secret:

```bash
export KUBECONFIG=~/.kube/respondua

kubectl get secret postgresql-secrets -n postgresql \
  -o jsonpath='{.data.POSTGRES_ADMIN_PASSWORD}' | base64 -d
```

## Update values.yaml

Make sure to update these values in `values.yaml`:

```yaml
env:
  - name: AWS_STORAGE_BUCKET_NAME
    value: "your-actual-bucket-name"  # Change this!
  - name: AWS_S3_REGION_NAME
    value: "eu-central-1"
```

## Verify Secrets

```bash
export KUBECONFIG=~/.kube/respondua

# Check ECR credentials
kubectl get secret ecr-credentials -n web

# Check application secrets
kubectl get secret respondua-secrets -n web
```
