# Production Environment - Networking & Storage Guide (Resources 81-90)

## Storage Containers: 81-83

### 81. module.spoke_prod.azurerm_storage_container.backups
**Container Name:** `backups`
**Access Level:** Private

**Purpose:** Production database backups and system state snapshots

**How to Use:**

**Upload Backups:**
```bash
# PostgreSQL backup
DATE=$(date +%Y%m%d_%H%M%S)
PGPASSWORD=$(az keyvault secret show --vault-name kv-lms-prod-lms-dxdfyl --name database-admin-password --query value -o tsv) \
pg_dump -h psql-lms-prod-lms-dxdfyl.postgres.database.azure.com -U psqladmin -d lms_auth -F c | \
gzip | az storage blob upload \
  --account-name stlmsprodlmsdxdfyl \
  --container-name backups \
  --name "postgres/lms_auth_${DATE}.dump.gz" \
  --file -

# Kubernetes cluster backup
kubectl get all --all-namespaces -o yaml > k8s-backup-${DATE}.yaml
gzip k8s-backup-${DATE}.yaml
az storage blob upload \
  --account-name stlmsprodlmsdxdfyl \
  --container-name backups \
  --name "kubernetes/cluster-${DATE}.yaml.gz" \
  --file k8s-backup-${DATE}.yaml.gz

# Cosmos DB backup metadata
az storage blob upload \
  --account-name stlmsprodlmsdxdfyl \
  --container-name backups \
  --name "cosmosdb/backup-info-${DATE}.json" \
  --file - <<EOF
{
  "timestamp": "$(date -Iseconds)",
  "account": "cosmos-lms-prod-lms-dxdfyl",
  "database": "lms_content",
  "backup_type": "continuous",
  "retention_days": 30
}
EOF
```

**List and Manage Backups:**
```bash
# List all backups
az storage blob list \
  --account-name stlmsprodlmsdxdfyl \
  --container-name backups \
  --query "[].{Name:name, Size:properties.contentLength, Modified:properties.lastModified}" \
  -o table

# List only PostgreSQL backups
az storage blob list \
  --account-name stlmsprodlmsdxdfyl \
  --container-name backups \
  --prefix "postgres/" \
  -o table

# Download latest backup
LATEST=$(az storage blob list \
  --account-name stlmsprodlmsdxdfyl \
  --container-name backups \
  --prefix "postgres/" \
  --query "sort_by(@, &properties.lastModified)[-1].name" -o tsv)

az storage blob download \
  --account-name stlmsprodlmsdxdfyl \
  --container-name backups \
  --name "$LATEST" \
  --file ./latest-backup.dump.gz

# Restore database from backup
gunzip -c latest-backup.dump.gz | PGPASSWORD=$(az keyvault secret show --vault-name kv-lms-prod-lms-dxdfyl --name database-admin-password --query value -o tsv) \
pg_restore -h psql-lms-prod-lms-dxdfyl.postgres.database.azure.com -U psqladmin -d lms_auth_restore
```

**Automated Backup Retention:**
```bash
# Set lifecycle policy (keep backups for 90 days)
az storage account management-policy create \
  --account-name stlmsprodlmsdxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --policy '{
    "rules": [
      {
        "enabled": true,
        "name": "backup-retention",
        "type": "Lifecycle",
        "definition": {
          "filters": {
            "blobTypes": ["blockBlob"],
            "prefixMatch": ["backups/"]
          },
          "actions": {
            "baseBlob": {
              "tierToCool": {"daysAfterModificationGreaterThan": 7},
              "tierToArchive": {"daysAfterModificationGreaterThan": 30},
              "delete": {"daysAfterModificationGreaterThan": 90}
            }
          }
        }
      }
    ]
  }'
```

**Backup Verification Script:**
```bash
#!/bin/bash
# verify-backups.sh
echo "Checking production backups..."

# Check PostgreSQL backups (should have daily backups)
PG_BACKUP_COUNT=$(az storage blob list \
  --account-name stlmsprodlmsdxdfyl \
  --container-name backups \
  --prefix "postgres/" \
  --query "length([?properties.lastModified >= '$(date -d '7 days ago' -Iseconds)'])" -o tsv)

echo "PostgreSQL backups (last 7 days): $PG_BACKUP_COUNT"

if [ "$PG_BACKUP_COUNT" -lt 7 ]; then
  echo "WARNING: Missing PostgreSQL backups!"
  exit 1
fi

# Check Kubernetes backups
K8S_BACKUP_COUNT=$(az storage blob list \
  --account-name stlmsprodlmsdxdfyl \
  --container-name backups \
  --prefix "kubernetes/" \
  --query "length([?properties.lastModified >= '$(date -d '7 days ago' -Iseconds)'])" -o tsv)

echo "Kubernetes backups (last 7 days): $K8S_BACKUP_COUNT"

echo "Backup verification completed successfully"
```

---

### 82. module.spoke_prod.azurerm_storage_container.logs
**Container Name:** `logs`
**Access Level:** Private

**Purpose:** Application logs, audit trails, and diagnostic data

**How to Use:**

**Upload Logs:**
```bash
# Application logs from Kubernetes
kubectl logs -l app=api-service --tail=10000 | \
  gzip | az storage blob upload \
  --account-name stlmsprodlmsdxdfyl \
  --container-name logs \
  --name "kubernetes/api-service-$(date +%Y%m%d_%H%M%S).log.gz" \
  --file -

# Nginx access logs
az storage blob upload \
  --account-name stlmsprodlmsdxdfyl \
  --container-name logs \
  --name "nginx/access-$(date +%Y%m%d).log" \
  --file /var/log/nginx/access.log

# Application error logs
az storage blob upload \
  --account-name stlmsprodlmsdxdfyl \
  --container-name logs \
  --name "application/errors-$(date +%Y%m%d).log.gz" \
  --file /app/logs/error.log.gz
```

**Query and Analyze Logs:**
```bash
# List today's logs
az storage blob list \
  --account-name stlmsprodlmsdxdfyl \
  --container-name logs \
  --prefix "application/errors-$(date +%Y%m%d)" \
  -o table

# Download and search for errors
az storage blob download \
  --account-name stlmsprodlmsdxdfyl \
  --container-name logs \
  --name "application/errors-$(date +%Y%m%d).log.gz" \
  --file - | gunzip | grep -i "ERROR\|CRITICAL"

# Count error occurrences
az storage blob download \
  --account-name stlmsprodlmsdxdfyl \
  --container-name logs \
  --name "application/errors-$(date +%Y%m%d).log.gz" \
  --file - | gunzip | grep -c "ERROR"

# Aggregate logs from last 7 days
for i in {0..6}; do
  DATE=$(date -d "$i days ago" +%Y%m%d)
  az storage blob download \
    --account-name stlmsprodlmsdxdfyl \
    --container-name logs \
    --name "application/errors-${DATE}.log.gz" \
    --file - 2>/dev/null | gunzip
done | grep "ERROR" > weekly-errors.log
```

**Log Aggregation with Python:**
```python
# aggregate_logs.py
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
import gzip
from datetime import datetime, timedelta

credential = DefaultAzureCredential()
blob_service_client = BlobServiceClient(
    account_url="https://stlmsprodlmsdxdfyl.blob.core.windows.net",
    credential=credential
)

container_client = blob_service_client.get_container_client("logs")

# Analyze logs from last 24 hours
cutoff_time = datetime.now() - timedelta(days=1)
error_count = 0

for blob in container_client.list_blobs(name_starts_with="application/"):
    if blob.last_modified >= cutoff_time:
        blob_client = container_client.get_blob_client(blob.name)
        content = blob_client.download_blob().readall()
        
        if blob.name.endswith('.gz'):
            content = gzip.decompress(content)
        
        error_count += content.decode('utf-8').count('ERROR')

print(f"Total errors in last 24 hours: {error_count}")
```

**Lifecycle Policy for Logs:**
```bash
# Keep logs for 30 days, then delete
az storage account management-policy create \
  --account-name stlmsprodlmsdxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --policy '{
    "rules": [
      {
        "enabled": true,
        "name": "log-retention",
        "type": "Lifecycle",
        "definition": {
          "filters": {
            "blobTypes": ["blockBlob"],
            "prefixMatch": ["logs/"]
          },
          "actions": {
            "baseBlob": {
              "tierToCool": {"daysAfterModificationGreaterThan": 3},
              "delete": {"daysAfterModificationGreaterThan": 30}
            }
          }
        }
      }
    ]
  }'
```

---

### 83. module.spoke_prod.azurerm_storage_container.uploads
**Container Name:** `uploads`
**Access Level:** Private

**Purpose:** User-uploaded content (documents, images, videos, assignments)

**How to Use:**

**Upload Files:**
```bash
# Upload user content with metadata
az storage blob upload \
  --account-name stlmsprodlmsdxdfyl \
  --container-name uploads \
  --name "users/123/profile.jpg" \
  --file ./profile.jpg \
  --content-type image/jpeg \
  --metadata "user_id=123" "uploaded_at=$(date -Iseconds)"

# Upload course materials
az storage blob upload \
  --account-name stlmsprodlmsdxdfyl \
  --container-name uploads \
  --name "courses/456/lecture1.pdf" \
  --file ./lecture1.pdf \
  --content-type application/pdf

# Batch upload
az storage blob upload-batch \
  --account-name stlmsprodlmsdxdfyl \
  --destination uploads \
  --source ./course-materials/ \
  --pattern "*.pdf"
```

**Generate Secure Access Links:**
```bash
# Generate SAS token for specific file (24 hours, read-only)
az storage blob generate-sas \
  --account-name stlmsprodlmsdxdfyl \
  --container-name uploads \
  --name "courses/456/lecture1.pdf" \
  --permissions r \
  --expiry $(date -u -d "24 hours" '+%Y-%m-%dT%H:%MZ') \
  --https-only \
  --full-uri

# Generate SAS for user folder (7 days, read-write)
az storage container generate-sas \
  --account-name stlmsprodlmsdxdfyl \
  --name uploads \
  --permissions rwdl \
  --expiry $(date -u -d "7 days" '+%Y-%m-%dT%H:%MZ') \
  --https-only

# Account-level SAS (for applications)
az storage account generate-sas \
  --account-name stlmsprodlmsdxdfyl \
  --services b \
  --resource-types sco \
  --permissions rwdl \
  --expiry $(date -u -d "30 days" '+%Y-%m-%dT%H:%MZ') \
  --https-only
```

**Use from Node.js Application:**
```javascript
// upload-handler.js
const { BlobServiceClient } = require('@azure/storage-blob');
const { DefaultAzureCredential } = require('@azure/identity');
const multer = require('multer');
const { v4: uuidv4 } = require('uuid');

const credential = new DefaultAzureCredential();
const blobServiceClient = new BlobServiceClient(
  'https://stlmsprodlmsdxdfyl.blob.core.windows.net',
  credential
);

const upload = multer({ dest: '/tmp/' });

app.post('/api/upload', upload.single('file'), async (req, res) => {
  try {
    const containerClient = blobServiceClient.getContainerClient('uploads');
    const userId = req.user.id;
    const fileExtension = req.file.originalname.split('.').pop();
    const blobName = `users/${userId}/${uuidv4()}.${fileExtension}`;
    
    const blockBlobClient = containerClient.getBlockBlobClient(blobName);
    
    await blockBlobClient.uploadFile(req.file.path, {
      blobHTTPHeaders: {
        blobContentType: req.file.mimetype
      },
      metadata: {
        user_id: userId.toString(),
        original_name: req.file.originalname,
        uploaded_at: new Date().toISOString()
      }
    });
    
    // Generate short-lived SAS URL
    const sasToken = await blockBlobClient.generateSasUrl({
      permissions: 'r',
      expiresOn: new Date(Date.now() + 3600 * 1000) // 1 hour
    });
    
    res.json({
      success: true,
      url: sasToken,
      blob_name: blobName
    });
  } catch (error) {
    console.error('Upload error:', error);
    res.status(500).json({ error: 'Upload failed' });
  }
});
```

**Content Moderation:**
```bash
# List files uploaded in last hour for review
az storage blob list \
  --account-name stlmsprodlmsdxdfyl \
  --container-name uploads \
  --query "[?properties.lastModified >= '$(date -d '1 hour ago' -Iseconds)'].{Name:name, Size:properties.contentLength, ContentType:properties.contentType}" \
  -o table

# Check file metadata
az storage blob metadata show \
  --account-name stlmsprodlmsdxdfyl \
  --container-name uploads \
  --name "users/123/profile.jpg"

# Update metadata (e.g., mark as reviewed)
az storage blob metadata update \
  --account-name stlmsprodlmsdxdfyl \
  --container-name uploads \
  --name "users/123/profile.jpg" \
  --metadata "reviewed=true" "reviewed_at=$(date -Iseconds)" "status=approved"
```

**Storage Metrics:**
```bash
# Check storage usage by prefix
az storage blob list \
  --account-name stlmsprodlmsdxdfyl \
  --container-name uploads \
  --prefix "users/" \
  --query "sum([].properties.contentLength)" -o tsv | \
  awk '{print $1/1024/1024/1024 " GB"}'

# Top 10 largest files
az storage blob list \
  --account-name stlmsprodlmsdxdfyl \
  --container-name uploads \
  --query "reverse(sort_by(@, &properties.contentLength))[0:10].{Name:name, SizeMB:properties.contentLength}" \
  -o table
```

---

## Subnets & Network Associations: 84-89

### 84. module.spoke_prod.azurerm_subnet.aks
**Subnet:** `aks-subnet`
**Address Range:** `10.2.0.0/20` (4,096 IPs, ~4,000 usable)

**Purpose:** Dedicated subnet for AKS cluster nodes and pods

**How to Use:**

**View Subnet Configuration:**
```bash
# Show subnet details
az network vnet subnet show \
  --vnet-name vnet-lms-prod-lms-dxdfyl \
  --name aks-subnet \
  --resource-group lms-prod-rg-lms-dxdfyl

# Check IP allocation
az network vnet subnet show \
  --vnet-name vnet-lms-prod-lms-dxdfyl \
  --name aks-subnet \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --query "{AddressPrefix:addressPrefix, AvailableIPs:availableIpAddressCount}"
```

**Subnet Configuration:**
- Network Plugin: Azure CNI
- Each pod gets an IP from this subnet
- Planning: 
  - System node pool: 2 nodes × 30 pods = 60 IPs
  - App node pool: 3 nodes × 30 pods = 90 IPs
  - Total: ~150 IPs used, 3,900 available for scaling

**Service Endpoints:**
```bash
# Add service endpoints for direct Azure service access
az network vnet subnet update \
  --vnet-name vnet-lms-prod-lms-dxdfyl \
  --name aks-subnet \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --service-endpoints Microsoft.Storage Microsoft.Sql Microsoft.KeyVault Microsoft.ContainerRegistry

# Verify service endpoints
az network vnet subnet show \
  --vnet-name vnet-lms-prod-lms-dxdfyl \
  --name aks-subnet \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --query "serviceEndpoints[].service"
```

**Monitor Subnet Usage:**
```bash
# Check available IPs
AVAILABLE_IPS=$(az network vnet subnet show \
  --vnet-name vnet-lms-prod-lms-dxdfyl \
  --name aks-subnet \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --query availableIpAddressCount -o tsv)

echo "Available IPs in AKS subnet: $AVAILABLE_IPS"

if [ "$AVAILABLE_IPS" -lt 100 ]; then
  echo "WARNING: Low IP availability! Consider expanding subnet."
fi
```

---

### 85. module.spoke_prod.azurerm_subnet.data
**Subnet:** `data-subnet`
**Address Range:** `10.2.16.0/24` (256 IPs, 251 usable)

**Purpose:** Data services subnet (PostgreSQL private endpoints, Cosmos DB)

**How to Use:**

**View Subnet:**
```bash
# Show subnet details
az network vnet subnet show \
  --vnet-name vnet-lms-prod-lms-dxdfyl \
  --name data-subnet \
  --resource-group lms-prod-rg-lms-dxdfyl
```

**Private Endpoints:**
```bash
# List private endpoints in data subnet
az network private-endpoint list \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --query "[?subnet.id.contains(@, 'data-subnet')]" \
  -o table

# Create private endpoint for PostgreSQL (if not exists)
az network private-endpoint create \
  --name pe-psql-prod \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --vnet-name vnet-lms-prod-lms-dxdfyl \
  --subnet data-subnet \
  --private-connection-resource-id /subscriptions/a9530d40-75da-44a3-9581-b9faf889608c/resourceGroups/lms-prod-rg-lms-dxdfyl/providers/Microsoft.DBforPostgreSQL/flexibleServers/psql-lms-prod-lms-dxdfyl \
  --group-id postgresqlServer \
  --connection-name psql-prod-connection

# Create private DNS zone
az network private-dns zone create \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --name privatelink.postgres.database.azure.com

# Link DNS zone to VNet
az network private-dns link vnet create \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --zone-name privatelink.postgres.database.azure.com \
  --name prod-dns-link \
  --virtual-network vnet-lms-prod-lms-dxdfyl \
  --registration-enabled false
```

---

### 86. module.spoke_prod.azurerm_subnet_network_security_group_association.aks
**Purpose:** Associates NSG with AKS subnet

**How to Use:**

**Verify Association:**
```bash
# Check NSG association
az network vnet subnet show \
  --vnet-name vnet-lms-prod-lms-dxdfyl \
  --name aks-subnet \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --query "networkSecurityGroup.id"
```

**View Effective Security Rules:**
```bash
# Get AKS node NIC
AKS_NIC=$(az network nic list \
  --resource-group MC_lms-prod-rg-lms-dxdfyl_aks-lms-prod-lms-dxdfyl_southeastasia \
  --query "[0].name" -o tsv)

# View effective NSG rules
az network nic list-effective-nsg \
  --resource-group MC_lms-prod-rg-lms-dxdfyl_aks-lms-prod-lms-dxdfyl_southeastasia \
  --name $AKS_NIC \
  -o table
```

---

### 87. module.spoke_prod.azurerm_subnet_network_security_group_association.data
**Purpose:** Associates NSG with data subnet

**How to Use:**

**Verify Association:**
```bash
# Check NSG on data subnet
az network vnet subnet show \
  --vnet-name vnet-lms-prod-lms-dxdfyl \
  --name data-subnet \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --query "networkSecurityGroup.id"
```

---

### 88. module.spoke_prod.azurerm_subnet_route_table_association.aks
**Purpose:** Routes AKS subnet traffic through Azure Firewall

**How to Use:**

**Verify Routing:**
```bash
# Check route table association
az network vnet subnet show \
  --vnet-name vnet-lms-prod-lms-dxdfyl \
  --name aks-subnet \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --query "routeTable.id"

# View effective routes for AKS node
AKS_NIC=$(az network nic list \
  --resource-group MC_lms-prod-rg-lms-dxdfyl_aks-lms-prod-lms-dxdfyl_southeastasia \
  --query "[0].name" -o tsv)

az network nic show-effective-route-table \
  --resource-group MC_lms-prod-rg-lms-dxdfyl_aks-lms-prod-lms-dxdfyl_southeastasia \
  --name $AKS_NIC \
  -o table
```

**Test Routing from Pod:**
```bash
# Deploy test pod
kubectl run -it --rm nettest --image=nicolaka/netshoot --restart=Never -- bash

# Inside pod:
# 1. Check route to internet
traceroute 8.8.8.8
# Expected: 10.2.x.x → 10.0.1.4 (Firewall) → Internet

# 2. Test DNS resolution
nslookup psql-lms-prod-lms-dxdfyl.postgres.database.azure.com

# 3. Check connectivity to hub
ping 10.0.0.5

# 4. Test outbound HTTPS
curl -v https://www.google.com
```

---

### 89. module.spoke_prod.azurerm_subnet_route_table_association.data
**Purpose:** Routes data subnet traffic through Azure Firewall

**How to Use:**

**Verify Routing:**
```bash
# Check route table on data subnet
az network vnet subnet show \
  --vnet-name vnet-lms-prod-lms-dxdfyl \
  --name data-subnet \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --query "routeTable.id"
```

---

### 90. module.hub.azurerm_log_analytics_workspace.hub[0]
**Workspace:** `log-lms-hub-lms-dxdfyl`
**SKU:** PerGB2018
**Retention:** 30 days

**Purpose:** Centralized logging and monitoring for all environments

**How to Use:**

**Query Logs:**
```bash
# View all logs
az monitor log-analytics query \
  --workspace log-lms-hub-lms-dxdfyl \
  --analytics-query "AzureDiagnostics | take 100"

# AKS container logs
az monitor log-analytics query \
  --workspace log-lms-hub-lms-dxdfyl \
  --analytics-query "ContainerLog | where ClusterName_s == 'aks-lms-prod-lms-dxdfyl' | take 100"

# Network traffic logs
az monitor log-analytics query \
  --workspace log-lms-hub-lms-dxdfyl \
  --analytics-query "AzureDiagnostics | where ResourceType == 'AZUREFIREWALLS' | take 100"

# Failed authentication attempts
az monitor log-analytics query \
  --workspace log-lms-hub-lms-dxdfyl \
  --analytics-query "AzureDiagnostics | where OperationName contains 'Authentication' and ResultType == 'Failed' | take 100"
```

**Advanced Queries:**
```kusto
// Top 10 error messages
AzureDiagnostics
| where Level == "Error"
| summarize count() by Message_s
| top 10 by count_ desc

// AKS pod restarts
ContainerInventory
| where TimeGenerated > ago(24h)
| where RestartCount > 0
| summarize max(RestartCount) by ContainerName_s, PodNamespace_s
| order by max_RestartCount desc

// Firewall blocked connections
AzureDiagnostics
| where Category == "AzureFirewallNetworkRule"
| where msg_s contains "Deny"
| summarize count() by src_ip_s, dest_ip_s, dest_port_s
| order by count_ desc

// Database performance
AzureDiagnostics
| where ResourceType == "POSTGRESQLFLEXIBLESERVERS"
| where MetricName == "cpu_percent"
| summarize avg(Average) by bin(TimeGenerated, 5m)
| render timechart
```

**Export Logs:**
```bash
# Export to JSON
az monitor log-analytics query \
  --workspace log-lms-hub-lms-dxdfyl \
  --analytics-query "AzureDiagnostics | where TimeGenerated > ago(24h)" \
  --output json > logs-$(date +%Y%m%d).json

# Export to CSV
az monitor log-analytics query \
  --workspace log-lms-hub-lms-dxdfyl \
  --analytics-query "AzureDiagnostics | where TimeGenerated > ago(24h) | project TimeGenerated, Level, Message_s" \
  --output tsv > logs-$(date +%Y%m%d).csv
```

---

## Quick Reference Commands

```bash
# Storage operations
az storage container list --account-name stlmsprodlmsdxdfyl -o table
az storage blob list --account-name stlmsprodlmsdxdfyl --container-name backups --query "[].{Name:name, Size:properties.contentLength}" -o table

# Network configuration
az network vnet subnet list --vnet-name vnet-lms-prod-lms-dxdfyl --resource-group lms-prod-rg-lms-dxdfyl -o table
az network nsg rule list --nsg-name nsg-lms-prod-lms-dxdfyl --resource-group lms-prod-rg-lms-dxdfyl -o table

# Log Analytics
az monitor log-analytics query --workspace log-lms-hub-lms-dxdfyl --analytics-query "ContainerLog | where TimeGenerated > ago(1h) | take 100"

# Health checks
kubectl get pods --all-namespaces
az postgres flexible-server show --name psql-lms-prod-lms-dxdfyl --resource-group lms-prod-rg-lms-dxdfyl --query state -o tsv
```

---

**Previous:** [08-production-data-services-guide.md](./08-production-data-services-guide.md)
**Next:** [10-monitoring-operations-guide.md](./10-monitoring-operations-guide.md) - Monitoring, Alerts, and Operational Tasks
