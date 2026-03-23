# kubernetes — K8s Deployment Manifests (v1)

Kubernetes manifests for deploying openEMIS v1 to a Kubernetes cluster using Kustomize.

## Files

| File | Purpose |
|------|---------|
| `namespace.yaml` | Creates the `openemis` namespace |
| `postgres.yaml` | PostgreSQL StatefulSet + Service + PersistentVolumeClaim |
| `openemis.yaml` | openEMIS API Deployment + Service + Ingress |
| `kustomization.yaml` | Kustomize config tying all manifests together |

## Deploy

```bash
# Build and load image (local kind cluster)
docker build -t openemis:latest .
kind load docker-image openemis:latest --name my-cluster

# Apply all manifests
kubectl apply -k kubernetes/

# Check rollout
kubectl -n openemis get pods
kubectl -n openemis rollout status deployment/openemis

# View logs
kubectl -n openemis logs -l app=openemis -f
```

## Notes

- Update `openemis.yaml` with your actual hostname and image registry before deploying to production.
- Secrets (DB password, SECRET_KEY) should be managed via Kubernetes Secrets or an external secrets manager — do not commit them to the repo.
- The PostgreSQL manifest uses a PersistentVolumeClaim for data persistence.
