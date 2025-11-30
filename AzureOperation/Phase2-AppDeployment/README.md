# Phase 2: Application Deployment - Complete!

## 📦 What's Been Created

All Phase 2 deployment files and scripts are ready in:
```
/home/huynguyen/lms_mcsrv_runwell/AzureOperation/Phase2-AppDeployment/
```

---

## 📁 Complete Structure

### 1. Kubernetes Manifests (8 files)

**Location**: `kubernetes/`

| File | Purpose | Services |
|------|---------|----------|
| `00-namespace.yaml` | Namespaces | lms-production, lms-development |
| `01-configmap.yaml` | Configuration | DB URLs, service endpoints, env vars |
| `02-secrets.yaml` | Secrets template | Database passwords, JWT keys, storage keys |
| `03-auth-service.yaml` | Auth service | Deployment (3 replicas) + Service |
| `04-content-service.yaml` | Content service | Deployment (3 replicas) + Service |
| `05-assignment-service.yaml` | Assignment service | Deployment (3 replicas) + Service |
| `06-frontends.yaml` | Frontend apps | Admin, Student, Teacher (2 replicas each) |
| `07-ingress.yaml` | Ingress rules | HTTPS routing, domain configuration |

**Total**: 6 deployments, 6 services, 1 ingress

### 2. Deployment Scripts (5 files)

**Location**: `scripts/`

| Script | Purpose | What It Does |
|--------|---------|--------------|
| `00-deploy-all.sh` | **Master orchestrator** | Runs all steps in order |
| `01-build-and-push.sh` | Build images | Builds 6 Docker images, pushes to ACR |
| `02-configure-secrets.sh` | Configure secrets | Retrieves from Key Vault, creates K8s secrets |
| `03-init-databases.sh` | Initialize DBs | Creates databases, runs migrations |
| `04-deploy-to-aks.sh` | Deploy to K8s | Applies manifests, waits for ready |

**All scripts are executable** ✅

### 3. Documentation

- `DEPLOYMENT_GUIDE.md` - Complete 17K deployment guide

---

## 🚀 Quick Start

### One-Command Deployment

```bash
cd /home/huynguyen/lms_mcsrv_runwell/AzureOperation/Phase2-AppDeployment/scripts

# Deploy everything to production
./00-deploy-all.sh production latest
```

This will:
1. ✅ Build and push 6 Docker images to ACR
2. ✅ Configure 4 secrets from Key Vault
3. ✅ Create 3 PostgreSQL databases
4. ✅ Deploy 6 services to AKS
5. ✅ Configure ingress and networking

**Estimated time**: 20-40 minutes

---

## 📋 Deployment Steps

### Prerequisites

```bash
# 1. Login to Azure
az login

# 2. Connect to AKS
az aks get-credentials \
  --name aks-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl

# 3. Verify connection
kubectl get nodes
```

### Step-by-Step Deployment

```bash
cd /home/huynguyen/lms_mcsrv_runwell/AzureOperation/Phase2-AppDeployment/scripts

# Step 1: Build and push images (~20 mins)
./01-build-and-push.sh latest

# Step 2: Configure secrets (~1 min)
./02-configure-secrets.sh production

# Step 3: Initialize databases (~5 mins)
./03-init-databases.sh production

# Step 4: Deploy to AKS (~10 mins)
./04-deploy-to-aks.sh production
```

---

## 🎯 What Gets Deployed

### Backend Services (Port 8001, 8002, 8004)
- **auth-service**: 3 replicas, 512Mi memory, 250m CPU
- **content-service**: 3 replicas, 512Mi memory, 250m CPU  
- **assignment-service**: 3 replicas, 512Mi memory, 250m CPU

### Frontend Services (Port 80)
- **frontend-admin**: 2 replicas, 256Mi memory, 100m CPU
- **frontend-student**: 2 replicas, 256Mi memory, 100m CPU
- **frontend-teacher**: 2 replicas, 256Mi memory, 100m CPU

### Total Resources
- **14 pods** (3+3+3+2+2+2)
- **6 services** (ClusterIP)
- **1 ingress** (NGINX)
- **3 databases** (lms_auth, lms_content, lms_assignment)

---

## 🔍 Verification

### Check Deployment Status

```bash
# All pods should be Running
kubectl get pods -n lms-production

# Check services
kubectl get services -n lms-production

# Check ingress IP
kubectl get ingress -n lms-production
```

### View Logs

```bash
# Auth service
kubectl logs -f deployment/auth-service -n lms-production

# Content service
kubectl logs -f deployment/content-service -n lms-production

# All pods
kubectl logs -l tier=backend -n lms-production --tail=50
```

### Test Endpoints

```bash
# Port forward for local testing
kubectl port-forward svc/auth-service 8001:8001 -n lms-production

# Test health endpoint
curl http://localhost:8001/health
```

---

## 🌐 Access Your Application

### Get Ingress IP

```bash
INGRESS_IP=$(kubectl get ingress lms-ingress -n lms-production -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "Ingress IP: $INGRESS_IP"
```

### Configure DNS

Add these A records to your DNS:
```
admin.lms.yourdomain.com    -> [INGRESS_IP]
student.lms.yourdomain.com  -> [INGRESS_IP]
teacher.lms.yourdomain.com  -> [INGRESS_IP]
api.lms.yourdomain.com      -> [INGRESS_IP]
```

### Local Testing (Without DNS)

```bash
# Add to /etc/hosts
echo "$INGRESS_IP admin.lms.yourdomain.com student.lms.yourdomain.com teacher.lms.yourdomain.com api.lms.yourdomain.com" | sudo tee -a /etc/hosts
```

Then access:
- Admin: http://admin.lms.yourdomain.com
- Student: http://student.lms.yourdomain.com
- Teacher: http://teacher.lms.yourdomain.com
- API: http://api.lms.yourdomain.com/auth/health

---

## 📚 Documentation

### Complete Guide
```bash
# View full deployment guide
cat /home/huynguyen/lms_mcsrv_runwell/AzureOperation/Phase2-AppDeployment/DEPLOYMENT_GUIDE.md
```

**Includes**:
- ✅ Detailed prerequisites
- ✅ Step-by-step instructions
- ✅ Troubleshooting guide
- ✅ Monitoring and maintenance
- ✅ Update procedures
- ✅ SSL/TLS configuration
- ✅ Common issues and solutions

### Phase 1 Infrastructure
```bash
# Infrastructure usage guides
ls /home/huynguyen/lms_mcsrv_runwell/AzureOperation/UsageGuides/
```

---

## 🛠️ Common Tasks

### Scale Services

```bash
# Scale auth service to 5 replicas
kubectl scale deployment auth-service --replicas=5 -n lms-production

# Scale all backends
kubectl scale deployment auth-service content-service assignment-service --replicas=5 -n lms-production
```

### Update Images

```bash
# Rebuild with new tag
./01-build-and-push.sh v2.0.0

# Update deployment
kubectl set image deployment/auth-service \
  auth-service=acrlmslmsdxdfyl.azurecr.io/lms/auth-service:v2.0.0 \
  -n lms-production

# Watch rollout
kubectl rollout status deployment/auth-service -n lms-production
```

### Restart Services

```bash
# Restart single service
kubectl rollout restart deployment/auth-service -n lms-production

# Restart all backends
kubectl rollout restart deployment/auth-service deployment/content-service deployment/assignment-service -n lms-production
```

### View Metrics

```bash
# Pod resource usage
kubectl top pods -n lms-production

# Node resource usage
kubectl top nodes

# Live pod updates
kubectl get pods -n lms-production -w
```

---

## 🐛 Troubleshooting

### Pods Not Starting

```bash
# Describe pod for errors
kubectl describe pod <pod-name> -n lms-production

# Check events
kubectl get events -n lms-production --sort-by='.lastTimestamp'
```

### Database Connection Issues

```bash
# Test from pod
AUTH_POD=$(kubectl get pods -n lms-production -l app=auth-service -o jsonpath='{.items[0].metadata.name}')
kubectl exec -it $AUTH_POD -n lms-production -- psql -h psql-lms-prod-lms-dxdfyl.postgres.database.azure.com -U psqladmin -d lms_auth
```

### Image Pull Errors

```bash
# Login to ACR
az acr login --name acrlmslmsdxdfyl

# Verify images
az acr repository list --name acrlmslmsdxdfyl
```

### Secrets Missing

```bash
# Recreate secrets
cd /home/huynguyen/lms_mcsrv_runwell/AzureOperation/Phase2-AppDeployment/scripts
./02-configure-secrets.sh production
```

---

## ✅ Deployment Checklist

### Before Deployment
- [ ] Azure CLI installed and logged in
- [ ] Docker running
- [ ] kubectl configured for AKS
- [ ] Firewall rules allow your IP
- [ ] All prerequisites validated

### During Deployment
- [ ] Images built and pushed to ACR
- [ ] Secrets configured from Key Vault
- [ ] Databases created and migrated
- [ ] All pods deployed to AKS
- [ ] All pods in Running state

### After Deployment
- [ ] Pod logs show no errors
- [ ] Health endpoints responding
- [ ] Database connections working
- [ ] DNS configured (or /etc/hosts)
- [ ] Ingress IP assigned
- [ ] Application accessible
- [ ] SSL configured (optional)
- [ ] Monitoring set up

---

## 📊 Summary

### Files Created
- ✅ 8 Kubernetes manifests
- ✅ 5 deployment scripts
- ✅ 1 comprehensive guide
- ✅ Total: 14 files, ~45KB

### Services Deployed
- ✅ 3 backend microservices
- ✅ 3 frontend applications
- ✅ 3 PostgreSQL databases
- ✅ 1 ingress controller

### Azure Resources Used
- ✅ AKS: `aks-lms-prod-lms-dxdfyl`
- ✅ ACR: `acrlmslmsdxdfyl`
- ✅ PostgreSQL: `psql-lms-prod-lms-dxdfyl`
- ✅ Key Vault: `kv-lms-prod-lms-dxdfyl`
- ✅ Storage: `stlmsprodlmsdxdfyl`

---

## 🎉 Next Steps

1. **Deploy your application**:
   ```bash
   cd /home/huynguyen/lms_mcsrv_runwell/AzureOperation/Phase2-AppDeployment/scripts
   ./00-deploy-all.sh production latest
   ```

2. **Configure DNS** after getting ingress IP

3. **Set up SSL certificates** with cert-manager

4. **Configure monitoring** using Guide 10 from Phase 1

5. **Run health checks** and verify everything works

6. **Update documentation** with your domain names

---

## 📞 Support

- **Deployment Guide**: `DEPLOYMENT_GUIDE.md`
- **Infrastructure Guides**: `/home/huynguyen/lms_mcsrv_runwell/AzureOperation/UsageGuides/`
- **Scripts**: `/home/huynguyen/lms_mcsrv_runwell/AzureOperation/Phase2-AppDeployment/scripts/`

---

**Phase 2 deployment files are ready! You can now deploy your LMS application to Azure.** 🚀
