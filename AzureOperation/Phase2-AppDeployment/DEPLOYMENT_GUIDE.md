# Phase 2: Application Deployment Guide

Complete guide for deploying LMS microservices application from RedHat to Azure infrastructure.

---

## 📋 Overview

This guide walks you through deploying your LMS application to the Azure infrastructure deployed in Phase 1.

**What will be deployed:**
- ✅ 3 Backend microservices (auth, content, assignment)
- ✅ 3 Frontend applications (admin, student, teacher)
- ✅ Database schemas and migrations
- ✅ Secrets and configuration
- ✅ Kubernetes resources (Production)

**Deployment Target:**
- **Production**: Azure Kubernetes Service (AKS)
- **Development**: Virtual Machine Scale Set (VMSS)

---

## 📁 Files Structure

```
AzureOperation/Phase2-AppDeployment/
├── kubernetes/                      # Kubernetes manifests
│   ├── 00-namespace.yaml           # Namespaces (prod/dev)
│   ├── 01-configmap.yaml           # Configuration
│   ├── 02-secrets.yaml             # Secrets template
│   ├── 03-auth-service.yaml        # Auth service deployment
│   ├── 04-content-service.yaml     # Content service deployment
│   ├── 05-assignment-service.yaml  # Assignment service deployment
│   ├── 06-frontends.yaml           # Frontend deployments
│   └── 07-ingress.yaml             # Ingress rules
├── scripts/                         # Deployment scripts
│   ├── 00-deploy-all.sh            # Master orchestration script
│   ├── 01-build-and-push.sh        # Build & push Docker images
│   ├── 02-configure-secrets.sh     # Configure K8s secrets
│   ├── 03-init-databases.sh        # Initialize databases
│   └── 04-deploy-to-aks.sh         # Deploy to Kubernetes
├── database/                        # Database migration scripts
└── DEPLOYMENT_GUIDE.md             # This file
```

---

## ⚙️ Prerequisites

### Required Tools

```bash
# Check Azure CLI
az --version
# If not installed: https://docs.microsoft.com/cli/azure/install-azure-cli

# Check Docker
docker --version
# If not installed: https://docs.docker.com/get-docker/

# Check kubectl
kubectl version --client
# If not installed: https://kubernetes.io/docs/tasks/tools/

# Check PostgreSQL client (psql)
psql --version
# If not installed on RedHat: sudo dnf install postgresql
```

### Azure Login

```bash
# Login to Azure
az login

# Set subscription (if you have multiple)
az account set --subscription "your-subscription-id"

# Verify login
az account show
```

### AKS Access

```bash
# Get AKS credentials
az aks get-credentials \
  --name aks-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --overwrite-existing

# Verify kubectl access
kubectl get nodes
```

### Firewall Configuration

Ensure your RedHat system IP is allowed in Azure PostgreSQL firewall:

```bash
# Get your public IP
curl ifconfig.me

# Add firewall rule
az postgres flexible-server firewall-rule create \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --name psql-lms-prod-lms-dxdfyl \
  --rule-name allow-redhat-system \
  --start-ip-address YOUR_IP \
  --end-ip-address YOUR_IP
```

---

## 🚀 Quick Start (Automated Deployment)

### Option 1: Complete Automated Deployment

Deploy everything with a single command:

```bash
cd /home/huynguyen/lms_mcsrv_runwell/AzureOperation/Phase2-AppDeployment/scripts

# Make scripts executable
chmod +x *.sh

# Run complete deployment (Production)
./00-deploy-all.sh production latest

# Or for Development
./00-deploy-all.sh development latest
```

**What this does:**
1. ✅ Builds all Docker images
2. ✅ Pushes images to Azure Container Registry
3. ✅ Configures secrets from Key Vault
4. ✅ Initializes databases and runs migrations
5. ✅ Deploys to AKS (Production) or VMSS (Development)

### Option 2: Skip Image Build (If already built)

```bash
# If images are already in ACR, skip build step
./00-deploy-all.sh production latest yes
```

---

## 📝 Step-by-Step Deployment (Manual)

If you prefer to run each step manually or need to troubleshoot:

### Step 1: Build and Push Docker Images

Build all microservices and push to Azure Container Registry:

```bash
cd /home/huynguyen/lms_mcsrv_runwell/AzureOperation/Phase2-AppDeployment/scripts

# Run build script
./01-build-and-push.sh latest
```

**What happens:**
- Builds 6 Docker images (3 backends + 3 frontends)
- Tags with specified version (default: latest)
- Pushes to ACR: `acrlmslmsdxdfyl.azurecr.io`
- Verifies images in registry

**Estimated time:** 15-30 minutes (depending on network)

**Verify images:**
```bash
az acr repository list --name acrlmslmsdxdfyl --output table
```

### Step 2: Configure Secrets

Retrieve secrets from Azure Key Vault and create Kubernetes secrets:

```bash
# For Production
./02-configure-secrets.sh production

# For Development
./02-configure-secrets.sh development
```

**What happens:**
- Retrieves 4 secrets from Key Vault:
  - `database-admin-password`
  - `jwt-secret-key`
  - `storage-account-key`
  - `cosmos-primary-key`
- Creates Kubernetes secret: `lms-secrets`
- Stores in namespace: `lms-production` or `lms-development`

**Verify secrets:**
```bash
kubectl get secret lms-secrets -n lms-production
kubectl describe secret lms-secrets -n lms-production
```

### Step 3: Initialize Databases

Create databases and run migrations:

```bash
# For Production
./03-init-databases.sh production

# For Development
./03-init-databases.sh development
```

**What happens:**
- Creates 3 PostgreSQL databases:
  - `lms_auth` (Authentication service)
  - `lms_content` (Content service)
  - `lms_assignment` (Assignment service)
- Runs Alembic migrations for each service
- Verifies table creation

**Estimated time:** 2-5 minutes

**Manual verification:**
```bash
# Get password from Key Vault
PGPASSWORD=$(az keyvault secret show \
  --vault-name kv-lms-prod-lms-dxdfyl \
  --name database-admin-password \
  --query value -o tsv)

# Connect to database
psql -h psql-lms-prod-lms-dxdfyl.postgres.database.azure.com \
     -U psqladmin \
     -d lms_auth

# List tables
\dt
```

### Step 4: Deploy to Kubernetes (Production)

Deploy application to AKS:

```bash
./04-deploy-to-aks.sh production
```

**What happens:**
- Creates namespace: `lms-production`
- Applies ConfigMaps
- Deploys 3 backend services (3 replicas each)
- Deploys 3 frontend services (2 replicas each)
- Creates ClusterIP services
- Configures Ingress
- Waits for all pods to be ready

**Estimated time:** 5-10 minutes

**Monitor deployment:**
```bash
# Watch pods starting
kubectl get pods -n lms-production -w

# Check deployment status
kubectl get deployments -n lms-production

# Check services
kubectl get services -n lms-production

# Check ingress
kubectl get ingress -n lms-production
```

---

## 🔍 Verification and Testing

### 1. Check Pod Status

```bash
# All pods should be Running
kubectl get pods -n lms-production

# Expected output:
# NAME                                  READY   STATUS    RESTARTS   AGE
# auth-service-xxx                      1/1     Running   0          5m
# content-service-xxx                   1/1     Running   0          5m
# assignment-service-xxx                1/1     Running   0          5m
# frontend-admin-xxx                    1/1     Running   0          4m
# frontend-student-xxx                  1/1     Running   0          4m
# frontend-teacher-xxx                  1/1     Running   0          4m
```

### 2. Check Pod Logs

```bash
# View logs for specific service
kubectl logs -f deployment/auth-service -n lms-production
kubectl logs -f deployment/content-service -n lms-production
kubectl logs -f deployment/assignment-service -n lms-production

# Check last 50 lines
kubectl logs --tail=50 deployment/auth-service -n lms-production
```

### 3. Test Service Connectivity

```bash
# Port forward to test locally
kubectl port-forward svc/auth-service 8001:8001 -n lms-production

# In another terminal, test API
curl http://localhost:8001/health

# Should return: {"status": "healthy"}
```

### 4. Test Database Connectivity

```bash
# Get auth service pod name
AUTH_POD=$(kubectl get pods -n lms-production -l app=auth-service -o jsonpath='{.items[0].metadata.name}')

# Exec into pod
kubectl exec -it $AUTH_POD -n lms-production -- bash

# Inside pod, test database
python -c "
from app.core.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT 1'))
    print('Database connection successful!')
"
```

### 5. Check Ingress

```bash
# Get ingress details
kubectl describe ingress lms-ingress -n lms-production

# Get LoadBalancer IP
INGRESS_IP=$(kubectl get ingress lms-ingress -n lms-production -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "Ingress IP: $INGRESS_IP"
```

---

## 🌐 DNS Configuration

### Get Ingress IP Address

```bash
kubectl get ingress lms-ingress -n lms-production
```

### Configure DNS Records

Add these A records to your DNS provider:

```
admin.lms.yourdomain.com    -> [INGRESS_IP]
student.lms.yourdomain.com  -> [INGRESS_IP]
teacher.lms.yourdomain.com  -> [INGRESS_IP]
api.lms.yourdomain.com      -> [INGRESS_IP]
```

### Test Without DNS (Local Testing)

Add to `/etc/hosts` on your local machine:

```bash
# Replace [INGRESS_IP] with actual IP
[INGRESS_IP] admin.lms.yourdomain.com student.lms.yourdomain.com teacher.lms.yourdomain.com api.lms.yourdomain.com
```

Then access:
- Admin: http://admin.lms.yourdomain.com
- Student: http://student.lms.yourdomain.com
- Teacher: http://teacher.lms.yourdomain.com
- API: http://api.lms.yourdomain.com

---

## 🔐 SSL/TLS Certificates

### Install cert-manager (If not already installed)

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Wait for cert-manager to be ready
kubectl wait --for=condition=Available --timeout=300s deployment/cert-manager -n cert-manager
```

### Create ClusterIssuer

```bash
cat <<EOF | kubectl apply -f -
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
          class: nginx
EOF
```

### Update Ingress for SSL

The ingress manifest (`07-ingress.yaml`) is already configured for cert-manager. After DNS is configured and cert-manager is installed, certificates will be automatically issued.

**Verify certificates:**
```bash
kubectl get certificate -n lms-production
kubectl describe certificate lms-tls-cert -n lms-production
```

---

## 📊 Monitoring and Maintenance

### View Real-time Metrics

```bash
# Pod resource usage
kubectl top pods -n lms-production

# Node resource usage
kubectl top nodes

# Watch pod status
kubectl get pods -n lms-production -w
```

### Scale Deployments

```bash
# Scale auth service to 5 replicas
kubectl scale deployment auth-service --replicas=5 -n lms-production

# Scale frontend-admin to 3 replicas
kubectl scale deployment frontend-admin --replicas=3 -n lms-production

# View scaling status
kubectl get deployment -n lms-production
```

### Rolling Updates

When you push new images:

```bash
# Trigger rolling update
kubectl rollout restart deployment/auth-service -n lms-production

# Watch rollout status
kubectl rollout status deployment/auth-service -n lms-production

# Rollback if needed
kubectl rollout undo deployment/auth-service -n lms-production
```

### Health Checks

```bash
# Check all pod health
kubectl get pods -n lms-production -o wide

# Describe pod for detailed info
kubectl describe pod <pod-name> -n lms-production

# Check events
kubectl get events -n lms-production --sort-by='.lastTimestamp'
```

---

## 🐛 Troubleshooting

### Pods Not Starting

```bash
# Check pod events
kubectl describe pod <pod-name> -n lms-production

# Common issues:
# - Image pull errors: Check ACR credentials
# - CrashLoopBackOff: Check logs
# - Pending: Check resource limits
```

### Database Connection Errors

```bash
# Check database firewall rules
az postgres flexible-server firewall-rule list \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --name psql-lms-prod-lms-dxdfyl

# Test connection from pod
kubectl exec -it <pod-name> -n lms-production -- psql -h psql-lms-prod-lms-dxdfyl.postgres.database.azure.com -U psqladmin -d lms_auth
```

### Secrets Not Found

```bash
# Check if secret exists
kubectl get secret lms-secrets -n lms-production

# If missing, recreate
cd /home/huynguyen/lms_mcsrv_runwell/AzureOperation/Phase2-AppDeployment/scripts
./02-configure-secrets.sh production
```

### Image Pull Errors

```bash
# Check ACR login
az acr login --name acrlmslmsdxdfyl

# Create image pull secret (if needed)
kubectl create secret docker-registry acr-secret \
  --docker-server=acrlmslmsdxdfyl.azurecr.io \
  --docker-username=acrlmslmsdxdfyl \
  --docker-password=$(az acr credential show --name acrlmslmsdxdfyl --query passwords[0].value -o tsv) \
  -n lms-production
```

### Service Unavailable

```bash
# Check service endpoints
kubectl get endpoints -n lms-production

# Check service logs
kubectl logs -f deployment/<service-name> -n lms-production

# Restart deployment
kubectl rollout restart deployment/<service-name> -n lms-production
```

---

## 🔄 Update and Redeploy

### Update Application Code

When you have new code changes:

```bash
# 1. Rebuild and push images with new tag
cd /home/huynguyen/lms_mcsrv_runwell/AzureOperation/Phase2-AppDeployment/scripts
./01-build-and-push.sh v2.0.0

# 2. Update Kubernetes deployments
kubectl set image deployment/auth-service \
  auth-service=acrlmslmsdxdfyl.azurecr.io/lms/auth-service:v2.0.0 \
  -n lms-production

# 3. Watch rollout
kubectl rollout status deployment/auth-service -n lms-production
```

### Update Configuration

```bash
# 1. Edit configmap
kubectl edit configmap lms-config -n lms-production

# 2. Restart pods to pick up changes
kubectl rollout restart deployment/auth-service -n lms-production
kubectl rollout restart deployment/content-service -n lms-production
kubectl rollout restart deployment/assignment-service -n lms-production
```

### Database Migrations

```bash
# Run migrations from your local machine
cd /home/huynguyen/lms_mcsrv_runwell/lms_micro_services/auth-service

# Set environment variables
export POSTGRES_HOST=psql-lms-prod-lms-dxdfyl.postgres.database.azure.com
export POSTGRES_PASSWORD=$(az keyvault secret show --vault-name kv-lms-prod-lms-dxdfyl --name database-admin-password --query value -o tsv)

# Run migrations
alembic upgrade head
```

---

## 📋 Deployment Checklist

Use this checklist for each deployment:

### Pre-Deployment
- [ ] Azure CLI installed and logged in
- [ ] Docker installed and running
- [ ] kubectl configured for AKS
- [ ] Firewall rules configured
- [ ] All scripts have execute permissions
- [ ] Reviewed recent code changes

### Deployment
- [ ] Built and pushed Docker images
- [ ] Configured secrets from Key Vault
- [ ] Initialized/updated databases
- [ ] Deployed to Kubernetes
- [ ] All pods running successfully

### Post-Deployment
- [ ] Verified pod status (all Running)
- [ ] Checked application logs
- [ ] Tested API endpoints
- [ ] Verified database connectivity
- [ ] Configured DNS records
- [ ] SSL certificates issued
- [ ] Smoke tests passed
- [ ] Monitoring configured
- [ ] Documentation updated
- [ ] Team notified

---

## 📞 Support and Resources

### Documentation

- **Phase 1 Infrastructure**: `/home/huynguyen/lms_mcsrv_runwell/AzureOperation/UsageGuides/`
- **Kubernetes Manifests**: `/home/huynguyen/lms_mcsrv_runwell/AzureOperation/Phase2-AppDeployment/kubernetes/`
- **Deployment Scripts**: `/home/huynguyen/lms_mcsrv_runwell/AzureOperation/Phase2-AppDeployment/scripts/`

### Useful Commands Reference

```bash
# View all resources
kubectl get all -n lms-production

# Get detailed pod info
kubectl describe pod <pod-name> -n lms-production

# Execute command in pod
kubectl exec -it <pod-name> -n lms-production -- bash

# View logs with timestamps
kubectl logs -f --timestamps deployment/auth-service -n lms-production

# Copy files from pod
kubectl cp lms-production/<pod-name>:/path/to/file ./local/path

# View resource usage
kubectl top pods -n lms-production

# Delete and recreate pod
kubectl delete pod <pod-name> -n lms-production
```

### Azure Resources

- **AKS Cluster**: `aks-lms-prod-lms-dxdfyl`
- **ACR**: `acrlmslmsdxdfyl.azurecr.io`
- **PostgreSQL**: `psql-lms-prod-lms-dxdfyl.postgres.database.azure.com`
- **Key Vault**: `kv-lms-prod-lms-dxdfyl`
- **Resource Group**: `lms-prod-rg-lms-dxdfyl`

---

## ✅ Success Criteria

Your deployment is successful when:

1. ✅ All 6 deployments show READY (auth, content, assignment, 3 frontends)
2. ✅ All pods in Running state
3. ✅ Health check endpoints return 200 OK
4. ✅ Database connections working
5. ✅ Ingress has external IP assigned
6. ✅ DNS records configured and resolving
7. ✅ SSL certificates issued (if configured)
8. ✅ Frontend applications accessible
9. ✅ API endpoints responding correctly
10. ✅ No errors in application logs

---

**Deployment Complete! Your LMS application is now running on Azure AKS.** 🎉

For operational guidance, refer to the Phase 1 Usage Guides in `/home/huynguyen/lms_mcsrv_runwell/AzureOperation/UsageGuides/`.
