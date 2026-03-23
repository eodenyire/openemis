# kubernetes — K8s Deployment Manifests (v3)

Kubernetes manifests for deploying openEMIS v3 (Odoo) to a Kubernetes cluster.

## Files

| File | Purpose |
|------|---------|
| `namespace.yaml` | Creates the `openemis` namespace |
| `postgres.yaml` | PostgreSQL StatefulSet + Service + PVC |
| `openemis.yaml` | Odoo Deployment + Service + Ingress |
| `kustomization.yaml` | Kustomize config |

## Deploy

```bash
# Build and load image
docker build -t openemis:latest .
kind load docker-image openemis:latest --name openemis-local

# Apply manifests
kubectl apply -k kubernetes/

# Check status
kubectl -n openemis get pods
kubectl -n openemis rollout status deployment/openemis --timeout=300s
```

## Notes
- Update `openemis.yaml` with your hostname and image registry before production deployment.
- Manage secrets (DB password, Odoo admin password) via Kubernetes Secrets.
