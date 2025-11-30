# Production Environment - Kubernetes (AKS) Guide (Resources 61-70)

## Production Foundation: 61-63

### 61. module.spoke_prod.azurerm_virtual_network.prod
**VNet Name:** `vnet-lms-prod-lms-dxdfyl`
**Address Space:** `10.2.0.0/16` (65,536 IPs)

**Purpose:** Production spoke VNet hosting AKS cluster and data services

**How to Use:**

**View VNet Configuration:**
```bash
# Show VNet details
az network vnet show \
  --name vnet-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl

# List subnets
az network vnet subnet list \
  --vnet-name vnet-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --query "[].{Name:name, AddressPrefix:addressPrefix, NSG:networkSecurityGroup.id}" \
  -o table
```

**VNet Architecture:**
```
vnet-lms-prod-lms-dxdfyl (10.2.0.0/16)
├── aks-subnet (10.2.0.0/20)             → AKS nodes (4,096 IPs)
├── data-subnet (10.2.16.0/24)           → PostgreSQL, Cosmos DB (256 IPs)
└── (Future: ingress-subnet, services-subnet)
```

**VNet Peering:**
```bash
# Check peering to hub
az network vnet peering show \
  --name prod-to-hub \
  --vnet-name vnet-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --query "{Name:name, State:peeringState, RemoteVNet:remoteVirtualNetwork.id}"

# Peering configuration:
# - Allow Gateway Transit: No
# - Use Remote Gateway: Yes (uses hub VPN)
# - Allow Forwarded Traffic: Yes (firewall inspection)
```

**Add Additional Subnet:**
```bash
# Example: Add subnet for private endpoints
az network vnet subnet create \
  --vnet-name vnet-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --name private-endpoints-subnet \
  --address-prefix 10.2.17.0/24 \
  --network-security-group nsg-lms-prod-lms-dxdfyl
```

---

### 62. module.spoke_prod.azurerm_virtual_network_peering.prod_to_hub
**Peering:** Production ↔ Hub

**Purpose:** Connects production VNet to hub for centralized services

**How to Use:**

**Check Peering Status:**
```bash
# View peering state
az network vnet peering show \
  --name prod-to-hub \
  --vnet-name vnet-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --query "{State:peeringState, AllowForwardedTraffic:allowForwardedTraffic, UseRemoteGateways:useRemoteGateways}"

# Should show:
# State: Connected
# AllowForwardedTraffic: true
# UseRemoteGateways: true
```

**Test Connectivity:**
```bash
# From AKS pod, test connection to hub services
kubectl run -it --rm debug --image=nicolaka/netshoot --restart=Never -- bash

# Inside pod:
ping 10.0.0.5  # Hub subnet
curl http://10.0.1.4  # Firewall private IP
nslookup kv-lms-hub-lms-dxdfyl.vault.azure.net  # Key Vault
traceroute 8.8.8.8  # Should route through firewall
```

**Troubleshoot Peering:**
```bash
# If peering shows "Disconnected"
# 1. Sync peering
az network vnet peering sync \
  --name prod-to-hub \
  --vnet-name vnet-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl

# 2. Check hub side
az network vnet peering show \
  --name hub-to-prod \
  --vnet-name vnet-lms-hub-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl

# 3. Verify no overlapping address spaces
az network vnet show --name vnet-lms-prod-lms-dxdfyl --resource-group lms-prod-rg-lms-dxdfyl --query addressSpace
az network vnet show --name vnet-lms-hub-lms-dxdfyl --resource-group rg-lms-hub-lms-dxdfyl --query addressSpace
```

---

### 63. module.spoke_prod.data.azurerm_client_config.current
**Purpose:** Provides Azure subscription and tenant information for production

**Information:**
- Subscription ID: `a9530d40-75da-44a3-9581-b9faf889608c`
- Tenant ID: For Key Vault access and managed identities
- Object ID: For role assignments

**How to Use:**
```bash
# Verify Azure context
az account show --query "{SubscriptionId:id, TenantId:tenantId, Name:name}"

# Ensure correct subscription
az account set --subscription a9530d40-75da-44a3-9581-b9faf889608c
```

---

## Azure Kubernetes Service: 64-66

### 64. module.spoke_prod.azurerm_kubernetes_cluster.prod
**AKS Cluster:** `aks-lms-prod-lms-dxdfyl`
**Kubernetes Version:** 1.32.9
**Network Plugin:** Azure CNI
**Location:** Southeast Asia

**Purpose:** Production-grade managed Kubernetes cluster

**How to Use:**

**Connect to Cluster:**
```bash
# Get credentials
az aks get-credentials \
  --name aks-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --overwrite-existing

# Verify connection
kubectl cluster-info
kubectl get nodes
kubectl get namespaces
```

**Cluster Information:**
```bash
# View cluster details
az aks show \
  --name aks-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --query "{K8sVersion:kubernetesVersion, FQDN:fqdn, NodeResourceGroup:nodeResourceGroup}"

# Check cluster health
az aks show \
  --name aks-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --query "powerState"
```

**Manage Node Pools:**
```bash
# List node pools
az aks nodepool list \
  --cluster-name aks-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  -o table

# System pool (system): 2 nodes (Standard_D2s_v3)
# Application pool (app): 3 nodes (Standard_D4s_v3)
```

**Scale Node Pool:**
```bash
# Scale application node pool
az aks nodepool scale \
  --cluster-name aks-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --name app \
  --node-count 5

# Enable autoscaler
az aks nodepool update \
  --cluster-name aks-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --name app \
  --enable-cluster-autoscaler \
  --min-count 3 \
  --max-count 10
```

**Upgrade Cluster:**
```bash
# Check available upgrades
az aks get-upgrades \
  --name aks-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  -o table

# Upgrade cluster (control plane first)
az aks upgrade \
  --name aks-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --kubernetes-version 1.33.0 \
  --control-plane-only

# Upgrade node pools
az aks nodepool upgrade \
  --cluster-name aks-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --name app \
  --kubernetes-version 1.33.0
```

**Deploy Applications:**
```bash
# Deploy sample application
kubectl create deployment nginx --image=nginx:latest --replicas=3
kubectl expose deployment nginx --port=80 --type=LoadBalancer

# Deploy from YAML
kubectl apply -f deployment.yaml

# Check deployment status
kubectl get deployments
kubectl get pods -o wide
kubectl get services
```

**Access Logs:**
```bash
# View pod logs
kubectl logs <pod-name>

# Stream logs
kubectl logs -f <pod-name>

# Logs from all pods in deployment
kubectl logs -l app=nginx

# Container insights (if enabled)
az monitor log-analytics query \
  --workspace log-lms-hub-lms-dxdfyl \
  --analytics-query "ContainerLog | where ClusterName_s == 'aks-lms-prod-lms-dxdfyl' | take 100"
```

**Troubleshooting:**
```bash
# Check node status
kubectl describe node <node-name>

# Check pod issues
kubectl describe pod <pod-name>
kubectl get events --sort-by='.lastTimestamp'

# Execute commands in pod
kubectl exec -it <pod-name> -- /bin/bash

# Check cluster diagnostics
az aks check-acr \
  --name aks-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --acr acrlmslmsdxdfyl.azurecr.io
```

**Enable Add-ons:**
```bash
# Enable monitoring
az aks enable-addons \
  --name aks-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --addons monitoring \
  --workspace-resource-id /subscriptions/a9530d40-75da-44a3-9581-b9faf889608c/resourceGroups/rg-lms-hub-lms-dxdfyl/providers/Microsoft.OperationalInsights/workspaces/log-lms-hub-lms-dxdfyl

# Enable Azure Policy
az aks enable-addons \
  --name aks-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --addons azure-policy

# Enable KEDA (Kubernetes Event Driven Autoscaling)
az aks enable-addons \
  --name aks-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --addons keda
```

---

### 65. module.spoke_prod.azurerm_kubernetes_cluster_node_pool.app
**Node Pool:** `app`
**VM Size:** Standard_D4s_v3 (4 vCPU, 16 GB RAM)
**Initial Count:** 3 nodes
**OS:** Ubuntu 22.04

**Purpose:** Dedicated node pool for application workloads

**How to Use:**

**View Node Pool:**
```bash
# Show node pool details
az aks nodepool show \
  --cluster-name aks-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --name app

# List nodes in pool
kubectl get nodes -l agentpool=app
```

**Scale Node Pool:**
```bash
# Manual scaling
az aks nodepool scale \
  --cluster-name aks-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --name app \
  --node-count 5

# Enable autoscaling
az aks nodepool update \
  --cluster-name aks-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --name app \
  --enable-cluster-autoscaler \
  --min-count 3 \
  --max-count 20
```

**Deploy to Specific Node Pool:**
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      nodeSelector:
        agentpool: app  # Deploy only to 'app' node pool
      containers:
      - name: my-app
        image: acrlmslmsdxdfyl.azurecr.io/my-app:latest
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 1000m
            memory: 1Gi
```

**Upgrade Node Pool:**
```bash
# Upgrade node pool independently
az aks nodepool upgrade \
  --cluster-name aks-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --name app \
  --kubernetes-version 1.32.9 \
  --no-wait

# Check upgrade status
az aks nodepool show \
  --cluster-name aks-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --name app \
  --query "provisioningState"
```

**Node Pool Taints (for dedicated workloads):**
```bash
# Add taint to isolate workloads
az aks nodepool update \
  --cluster-name aks-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --name app \
  --node-taints "app=true:NoSchedule"

# Pods must have matching toleration:
# tolerations:
# - key: "app"
#   operator: "Equal"
#   value: "true"
#   effect: "NoSchedule"
```

---

### 66. module.spoke_prod.azurerm_cosmosdb_account.prod
**Cosmos DB:** `cosmos-lms-prod-lms-dxdfyl`
**API:** SQL (Core)
**Consistency:** Session

**Purpose:** Production NoSQL database for content, sessions, analytics

**How to Use:**

**Get Connection Information:**
```bash
# Get connection string
az cosmosdb keys list \
  --name cosmos-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --type connection-strings \
  --query "connectionStrings[0].connectionString" -o tsv

# Get endpoint and key
az cosmosdb show \
  --name cosmos-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --query documentEndpoint -o tsv

az cosmosdb keys list \
  --name cosmos-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --query primaryMasterKey -o tsv
```

**Use from Kubernetes:**
```yaml
# Create Kubernetes secret
apiVersion: v1
kind: Secret
metadata:
  name: cosmos-secret
type: Opaque
stringData:
  connection-string: "AccountEndpoint=https://cosmos-lms-prod-lms-dxdfyl.documents.azure.com:443/;AccountKey=<key>;"

---
# Use in deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-service
spec:
  template:
    spec:
      containers:
      - name: api
        image: acrlmslmsdxdfyl.azurecr.io/api:latest
        env:
        - name: COSMOS_CONNECTION_STRING
          valueFrom:
            secretKeyRef:
              name: cosmos-secret
              key: connection-string
```

**Managed Identity (Recommended):**
```bash
# Enable workload identity on AKS
az aks update \
  --name aks-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --enable-workload-identity \
  --enable-oidc-issuer

# Create managed identity
az identity create \
  --name cosmos-reader-identity \
  --resource-group lms-prod-rg-lms-dxdfyl

# Grant Cosmos DB access
az cosmosdb sql role assignment create \
  --account-name cosmos-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --role-definition-name "Cosmos DB Built-in Data Reader" \
  --principal-id <managed-identity-object-id> \
  --scope "/"
```

**Monitor Performance:**
```bash
# Check RU consumption
az monitor metrics list \
  --resource /subscriptions/a9530d40-75da-44a3-9581-b9faf889608c/resourceGroups/lms-prod-rg-lms-dxdfyl/providers/Microsoft.DocumentDB/databaseAccounts/cosmos-lms-prod-lms-dxdfyl \
  --metric "TotalRequestUnits" \
  --aggregation Total

# View throttling
az monitor metrics list \
  --resource /subscriptions/a9530d40-75da-44a3-9581-b9faf889608c/resourceGroups/lms-prod-rg-lms-dxdfyl/providers/Microsoft.DocumentDB/databaseAccounts/cosmos-lms-prod-lms-dxdfyl \
  --metric "TotalRequests" \
  --filter "StatusCode eq '429'"
```

**Scale Throughput:**
```bash
# Update database throughput
az cosmosdb sql database throughput update \
  --account-name cosmos-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --name lms_content \
  --throughput 2000

# Enable autoscale
az cosmosdb sql database throughput update \
  --account-name cosmos-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --name lms_content \
  --max-throughput 10000
```

---

## Data Services: 67-70

### 67. module.spoke_prod.azurerm_cosmosdb_sql_database.prod
**Database:** `lms_content`

**Purpose:** Production content database

**How to Use:**

**Create Containers:**
```bash
# Courses container
az cosmosdb sql container create \
  --account-name cosmos-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --database-name lms_content \
  --name courses \
  --partition-key-path "/courseId" \
  --throughput 1000

# Students container
az cosmosdb sql container create \
  --account-name cosmos-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --database-name lms_content \
  --name students \
  --partition-key-path "/studentId" \
  --throughput 1000

# Sessions container with TTL
az cosmosdb sql container create \
  --account-name cosmos-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --database-name lms_content \
  --name sessions \
  --partition-key-path "/sessionId" \
  --throughput 400 \
  --ttl 3600  # 1 hour
```

**Query Data:**
```bash
# Using Azure CLI (limited)
az cosmosdb sql container show \
  --account-name cosmos-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --database-name lms_content \
  --name courses

# Using Python SDK (recommended)
from azure.cosmos import CosmosClient

client = CosmosClient("https://cosmos-lms-prod-lms-dxdfyl.documents.azure.com:443/", "<key>")
database = client.get_database_client("lms_content")
container = database.get_container_client("courses")

# Query courses
for item in container.query_items(
    query="SELECT * FROM c WHERE c.status = @status",
    parameters=[{"name": "@status", "value": "published"}],
    enable_cross_partition_query=True
):
    print(item)
```

---

### 68. module.spoke_prod.azurerm_key_vault.prod
**Key Vault:** `kv-lms-prod-lms-dxdfyl`

**Purpose:** Production secrets, keys, and certificates

**How to Use:**

**Access Secrets:**
```bash
# Get secret
az keyvault secret show \
  --vault-name kv-lms-prod-lms-dxdfyl \
  --name database-admin-password \
  --query value -o tsv

# Set secret
az keyvault secret set \
  --vault-name kv-lms-prod-lms-dxdfyl \
  --name api-key \
  --value "prod-secret-value"

# List secrets
az keyvault secret list \
  --vault-name kv-lms-prod-lms-dxdfyl \
  -o table
```

**Use from AKS:**
```bash
# Option 1: Azure Key Vault Provider for Secrets Store CSI Driver
# Install CSI driver
az aks enable-addons \
  --name aks-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --addons azure-keyvault-secrets-provider

# Create SecretProviderClass
kubectl apply -f - <<EOF
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: azure-kv-prod
spec:
  provider: azure
  parameters:
    usePodIdentity: "false"
    useVMManagedIdentity: "true"
    userAssignedIdentityID: "<aks-kubelet-identity-client-id>"
    keyvaultName: "kv-lms-prod-lms-dxdfyl"
    objects: |
      array:
        - |
          objectName: database-admin-password
          objectType: secret
          objectVersion: ""
    tenantId: "<tenant-id>"
EOF

# Mount secrets in pod
kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  containers:
  - name: app
    image: acrlmslmsdxdfyl.azurecr.io/app:latest
    volumeMounts:
    - name: secrets
      mountPath: "/mnt/secrets"
      readOnly: true
  volumes:
  - name: secrets
    csi:
      driver: secrets-store.csi.k8s.io
      readOnly: true
      volumeAttributes:
        secretProviderClass: "azure-kv-prod"
EOF
```

---

### 69. module.spoke_prod.azurerm_key_vault_secret.cosmosdb_connection_string
**Secret:** `cosmosdb-connection-string`

**How to Use:**
```bash
# Retrieve from Key Vault
az keyvault secret show \
  --vault-name kv-lms-prod-lms-dxdfyl \
  --name cosmosdb-connection-string \
  --query value -o tsv

# Use in application (via CSI driver)
# Connection string available at: /mnt/secrets/cosmosdb-connection-string
```

---

### 70. module.spoke_prod.azurerm_key_vault_secret.cosmosdb_key
**Secret:** `cosmosdb-primary-key`

**How to Use:**
```bash
# Retrieve key
az keyvault secret show \
  --vault-name kv-lms-prod-lms-dxdfyl \
  --name cosmosdb-primary-key \
  --query value -o tsv

# Rotate keys (follow same process as dev environment)
```

---

## Quick Reference Commands

```bash
# AKS cluster access
az aks get-credentials --name aks-lms-prod-lms-dxdfyl --resource-group lms-prod-rg-lms-dxdfyl
kubectl get nodes
kubectl get pods --all-namespaces

# Scale application node pool
az aks nodepool scale --cluster-name aks-lms-prod-lms-dxdfyl --resource-group lms-prod-rg-lms-dxdfyl --name app --node-count 5

# Get Cosmos DB connection
az keyvault secret show --vault-name kv-lms-prod-lms-dxdfyl --name cosmosdb-connection-string --query value -o tsv

# Check VNet peering
az network vnet peering show --name prod-to-hub --vnet-name vnet-lms-prod-lms-dxdfyl --resource-group lms-prod-rg-lms-dxdfyl --query peeringState
```

---

**Previous:** [06-development-networking-security-guide.md](./06-development-networking-security-guide.md)
**Next:** [08-production-data-services-guide.md](./08-production-data-services-guide.md) - PostgreSQL, Storage, and Data Management
