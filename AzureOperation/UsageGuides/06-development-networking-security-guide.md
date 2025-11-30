# Development Environment - Networking & Security Guide (Resources 51-60)

## Storage Containers: 51-53

### 51. module.spoke_dev.azurerm_storage_container.backups
**Container Name:** `backups`
**Access Level:** Private

**Purpose:** Store database backups and application state snapshots

**How to Use:**

**Upload Backups:**
```bash
# Upload database backup
az storage blob upload \
  --account-name stlmsdevlmsdxdfyl \
  --container-name backups \
  --name "lms_auth_$(date +%Y%m%d_%H%M%S).sql" \
  --file ./lms_auth_backup.sql

# Upload with metadata
az storage blob upload \
  --account-name stlmsdevlmsdxdfyl \
  --container-name backups \
  --name backup.tar.gz \
  --file ./backup.tar.gz \
  --metadata "date=$(date +%Y-%m-%d)" "type=full" "source=postgres"

# Upload directory
az storage blob upload-batch \
  --account-name stlmsdevlmsdxdfyl \
  --destination backups \
  --source ./backup-folder/ \
  --pattern "*.sql"
```

**Download Backups:**
```bash
# List backups
az storage blob list \
  --account-name stlmsdevlmsdxdfyl \
  --container-name backups \
  --query "[].{Name:name, Size:properties.contentLength, Modified:properties.lastModified}" \
  -o table

# Download specific backup
az storage blob download \
  --account-name stlmsdevlmsdxdfyl \
  --container-name backups \
  --name lms_auth_20250202_120000.sql \
  --file ./restore.sql

# Download latest backup
LATEST=$(az storage blob list --account-name stlmsdevlmsdxdfyl --container-name backups --query "sort_by(@, &properties.lastModified)[-1].name" -o tsv)
az storage blob download --account-name stlmsdevlmsdxdfyl --container-name backups --name "$LATEST" --file ./latest-backup.sql
```

**Lifecycle Management:**
```bash
# Set up automatic deletion of old backups (30 days)
az storage account management-policy create \
  --account-name stlmsdevlmsdxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --policy '{
    "rules": [{
      "enabled": true,
      "name": "delete-old-backups",
      "type": "Lifecycle",
      "definition": {
        "filters": {
          "blobTypes": ["blockBlob"],
          "prefixMatch": ["backups/"]
        },
        "actions": {
          "baseBlob": {
            "delete": {"daysAfterModificationGreaterThan": 30}
          }
        }
      }
    }]
  }'
```

**Automated Backup Script:**
```bash
#!/bin/bash
# backup-postgres.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="lms_auth_${DATE}.sql"

# Get password from Key Vault
PASSWORD=$(az keyvault secret show --vault-name kv-lms-dev-lms-dxdfyl --name database-admin-password --query value -o tsv)

# Dump database
PGPASSWORD=$PASSWORD pg_dump \
  -h psql-lms-dev-lms-dxdfyl.postgres.database.azure.com \
  -U psqladmin \
  -d lms_auth \
  -F c \
  -f "$BACKUP_FILE"

# Upload to blob storage
az storage blob upload \
  --account-name stlmsdevlmsdxdfyl \
  --container-name backups \
  --name "$BACKUP_FILE" \
  --file "$BACKUP_FILE"

# Clean up local file
rm "$BACKUP_FILE"
echo "Backup completed: $BACKUP_FILE"
```

---

### 52. module.spoke_dev.azurerm_storage_container.logs
**Container Name:** `logs`
**Access Level:** Private

**Purpose:** Application logs and diagnostic data

**How to Use:**

**Upload Logs:**
```bash
# Upload application logs
az storage blob upload \
  --account-name stlmsdevlmsdxdfyl \
  --container-name logs \
  --name "app-$(date +%Y%m%d).log" \
  --file /var/log/app.log

# Upload with automatic compression
gzip -c /var/log/app.log | az storage blob upload \
  --account-name stlmsdevlmsdxdfyl \
  --container-name logs \
  --name "app-$(date +%Y%m%d).log.gz" \
  --file -
```

**Query Logs:**
```bash
# List today's logs
az storage blob list \
  --account-name stlmsdevlmsdxdfyl \
  --container-name logs \
  --prefix "app-$(date +%Y%m%d)" \
  -o table

# Download and view logs
az storage blob download \
  --account-name stlmsdevlmsdxdfyl \
  --container-name logs \
  --name app-20250202.log \
  --file - | tail -100

# Search logs for errors
az storage blob download \
  --account-name stlmsdevlmsdxdfyl \
  --container-name logs \
  --name app-20250202.log \
  --file - | grep ERROR
```

**Log Aggregation Script:**
```python
# aggregate-logs.py
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
import datetime

credential = DefaultAzureCredential()
blob_service_client = BlobServiceClient(
    account_url="https://stlmsdevlmsdxdfyl.blob.core.windows.net",
    credential=credential
)

container_client = blob_service_client.get_container_client("logs")

# List logs from last 7 days
start_date = datetime.datetime.now() - datetime.timedelta(days=7)
for blob in container_client.list_blobs():
    if blob.last_modified >= start_date:
        print(f"{blob.name}: {blob.size} bytes, Modified: {blob.last_modified}")
```

---

### 53. module.spoke_dev.azurerm_storage_container.uploads
**Container Name:** `uploads`
**Access Level:** Private

**Purpose:** User-uploaded content (documents, images, videos)

**How to Use:**

**Upload Files:**
```bash
# Upload image
az storage blob upload \
  --account-name stlmsdevlmsdxdfyl \
  --container-name uploads \
  --name images/profile.jpg \
  --file ./profile.jpg \
  --content-type image/jpeg

# Upload with public read access (use SAS token instead)
az storage blob upload \
  --account-name stlmsdevlmsdxdfyl \
  --container-name uploads \
  --name public/banner.png \
  --file ./banner.png
```

**Generate SAS Tokens:**
```bash
# Generate SAS token for temporary access (1 hour)
az storage blob generate-sas \
  --account-name stlmsdevlmsdxdfyl \
  --container-name uploads \
  --name images/profile.jpg \
  --permissions r \
  --expiry $(date -u -d "1 hour" '+%Y-%m-%dT%H:%MZ') \
  --https-only

# Use SAS token
# https://stlmsdevlmsdxdfyl.blob.core.windows.net/uploads/images/profile.jpg?<SAS-token>

# Container-level SAS (for multiple files)
az storage container generate-sas \
  --account-name stlmsdevlmsdxdfyl \
  --name uploads \
  --permissions rl \
  --expiry $(date -u -d "24 hours" '+%Y-%m-%dT%H:%MZ')
```

**Use in Web Application:**
```javascript
// Node.js example
const { BlobServiceClient } = require('@azure/storage-blob');
const { DefaultAzureCredential } = require('@azure/identity');

const credential = new DefaultAzureCredential();
const blobServiceClient = new BlobServiceClient(
  'https://stlmsdevlmsdxdfyl.blob.core.windows.net',
  credential
);

// Upload file from Express.js
app.post('/upload', upload.single('file'), async (req, res) => {
  const containerClient = blobServiceClient.getContainerClient('uploads');
  const blobName = `${Date.now()}-${req.file.originalname}`;
  const blockBlobClient = containerClient.getBlockBlobClient(blobName);
  
  await blockBlobClient.uploadFile(req.file.path);
  res.json({ url: blockBlobClient.url });
});
```

**Content CDN Integration:**
```bash
# Create CDN endpoint (optional, for better performance)
az cdn endpoint create \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --profile-name lms-dev-cdn \
  --name lms-dev-uploads \
  --origin stlmsdevlmsdxdfyl.blob.core.windows.net \
  --origin-host-header stlmsdevlmsdxdfyl.blob.core.windows.net

# Access via CDN: https://lms-dev-uploads.azureedge.net/uploads/images/profile.jpg
```

---

## Key Vault Secrets: 54-55

### 54. module.spoke_dev.azurerm_key_vault_secret.sa_key
**Secret Name:** `storage-account-key`

**Purpose:** Primary access key for storage account

**How to Use:**

**Retrieve Key:**
```bash
# Get storage account key from Key Vault
az keyvault secret show \
  --vault-name kv-lms-dev-lms-dxdfyl \
  --name storage-account-key \
  --query value -o tsv
```

**Use in Applications:**
```python
# Python example
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

credential = DefaultAzureCredential()
secret_client = SecretClient("https://kv-lms-dev-lms-dxdfyl.vault.azure.net/", credential)

# Get storage key
storage_key = secret_client.get_secret("storage-account-key").value

# Use with connection string
connection_string = f"DefaultEndpointsProtocol=https;AccountName=stlmsdevlmsdxdfyl;AccountKey={storage_key};EndpointSuffix=core.windows.net"
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
```

**Rotate Keys:**
```bash
# 1. Regenerate key2 (secondary)
az storage account keys renew \
  --account-name stlmsdevlmsdxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --key secondary

# 2. Update applications to use key2
# 3. Regenerate key1 (primary)
az storage account keys renew \
  --account-name stlmsdevlmsdxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --key primary

# 4. Update Key Vault with new key
NEW_KEY=$(az storage account keys list --account-name stlmsdevlmsdxdfyl --resource-group lms-dev-rg-lms-dxdfyl --query "[0].value" -o tsv)
az keyvault secret set \
  --vault-name kv-lms-dev-lms-dxdfyl \
  --name storage-account-key \
  --value "$NEW_KEY"
```

---

### 55. module.spoke_dev.azurerm_subnet.app
**Subnet:** `app-subnet`
**Address Range:** `10.1.2.0/24` (256 IPs, 251 usable)

**Purpose:** Hosts VMSS instances (application tier)

**How to Use:**

**View Subnet Details:**
```bash
# Show subnet configuration
az network vnet subnet show \
  --vnet-name vnet-lms-dev-lms-dxdfyl \
  --name app-subnet \
  --resource-group lms-dev-rg-lms-dxdfyl

# List resources in subnet
az network nic list \
  --query "[?ipConfigurations[0].subnet.id.contains(@, 'app-subnet')].{Name:name, PrivateIP:ipConfigurations[0].privateIPAddress}" \
  -o table
```

**Network Configuration:**
- NSG: `nsg-lms-dev-lms-dxdfyl`
- Route Table: `rt-lms-dev-lms-dxdfyl`
- Service Endpoints: None (add if needed)

**Add Service Endpoints:**
```bash
# Enable direct access to Azure Storage (bypass firewall)
az network vnet subnet update \
  --vnet-name vnet-lms-dev-lms-dxdfyl \
  --name app-subnet \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --service-endpoints Microsoft.Storage Microsoft.Sql Microsoft.KeyVault

# This allows resources in this subnet to access Azure services
# via Azure backbone network instead of internet
```

**Delegate Subnet (for specific services):**
```bash
# Example: Delegate to Azure Container Instances
az network vnet subnet update \
  --vnet-name vnet-lms-dev-lms-dxdfyl \
  --name app-subnet \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --delegations Microsoft.ContainerInstance/containerGroups
```

---

## Subnet Networking: 56-58

### 56. module.spoke_dev.azurerm_subnet.data
**Subnet:** `data-subnet`
**Address Range:** `10.1.1.0/24` (256 IPs, 251 usable)

**Purpose:** Hosts data services (PostgreSQL, Cosmos DB connections)

**How to Use:**

**View Subnet:**
```bash
# Show subnet details
az network vnet subnet show \
  --vnet-name vnet-lms-dev-lms-dxdfyl \
  --name data-subnet \
  --resource-group lms-dev-rg-lms-dxdfyl
```

**Network Security:**
```bash
# Verify NSG rules allow PostgreSQL
az network nsg rule list \
  --nsg-name nsg-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --query "[?destinationPortRange=='5432']" \
  -o table

# Add rule to allow PostgreSQL from app subnet
az network nsg rule create \
  --nsg-name nsg-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --name Allow-PostgreSQL-From-App \
  --priority 1100 \
  --source-address-prefixes 10.1.2.0/24 \
  --destination-address-prefixes 10.1.1.0/24 \
  --destination-port-ranges 5432 \
  --access Allow \
  --protocol Tcp
```

**Private Endpoint Configuration:**
```bash
# PostgreSQL uses private endpoint in this subnet
# Verify private endpoint
az network private-endpoint list \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --query "[?subnet.id.contains(@, 'data-subnet')]" \
  -o table
```

---

### 57. module.spoke_dev.azurerm_subnet_network_security_group_association.app
**Purpose:** Associates NSG with app-subnet

**How to Use:**

**Verify Association:**
```bash
# Check NSG association
az network vnet subnet show \
  --vnet-name vnet-lms-dev-lms-dxdfyl \
  --name app-subnet \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --query "networkSecurityGroup.id"
```

**Effective Security Rules:**
```bash
# View all effective rules for a NIC in app-subnet
az network nic list-effective-nsg \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --name <vmss-nic-name>

# Test connectivity
az network watcher test-ip-flow \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --vm <vm-name> \
  --direction Outbound \
  --protocol TCP \
  --local 10.1.2.5:443 \
  --remote 8.8.8.8:443
```

---

### 58. module.spoke_dev.azurerm_subnet_network_security_group_association.data
**Purpose:** Associates NSG with data-subnet

**How to Use:**

**Verify Association:**
```bash
# Check NSG on data subnet
az network vnet subnet show \
  --vnet-name vnet-lms-dev-lms-dxdfyl \
  --name data-subnet \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --query "networkSecurityGroup.id"
```

**Security Rules Impact:**
All traffic to/from data-subnet is filtered by `nsg-lms-dev-lms-dxdfyl` rules.

---

## Route Tables & VNets: 59-60

### 59. module.spoke_dev.azurerm_subnet_route_table_association.app
**Purpose:** Routes app-subnet traffic through Azure Firewall

**How to Use:**

**Verify Routing:**
```bash
# Check route table association
az network vnet subnet show \
  --vnet-name vnet-lms-dev-lms-dxdfyl \
  --name app-subnet \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --query "routeTable.id"

# View effective routes
az network nic show-effective-route-table \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --name <vmss-nic-name> \
  -o table
```

**Expected Routes:**
```
Source    State    Address Prefix    Next Hop Type       Next Hop IP
--------  -------  ----------------  ------------------  ------------
Default   Active   10.1.0.0/16       VnetLocal           -
User      Active   0.0.0.0/0         VirtualAppliance    10.0.1.4
User      Active   10.0.0.0/16       VirtualAppliance    10.0.1.4
User      Active   10.2.0.0/16       VirtualAppliance    10.0.1.4
```

**Trace Route:**
```bash
# From VMSS instance, trace to internet
az vmss run-command invoke \
  --command-id RunShellScript \
  --name lms-dev-vmss-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --instance-id 0 \
  --scripts "traceroute 8.8.8.8"

# Expected: 10.1.2.x → 10.0.1.4 (Firewall) → Internet
```

---

### 60. module.spoke_dev.azurerm_subnet_route_table_association.data
**Purpose:** Routes data-subnet traffic through Azure Firewall

**How to Use:**

**Verify Routing:**
```bash
# Check route table on data subnet
az network vnet subnet show \
  --vnet-name vnet-lms-dev-lms-dxdfyl \
  --name data-subnet \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --query "routeTable.id"
```

**Traffic Flow:**
```
PostgreSQL/Cosmos DB
  ↓ (in data-subnet)
Route Table
  ↓
For internet-bound: → 10.0.1.4 (Firewall) → Internet
For intra-VNet: → VNet routing
```

---

## Quick Reference Commands

```bash
# Storage operations
az storage blob list --account-name stlmsdevlmsdxdfyl --container-name backups -o table
az storage blob list --account-name stlmsdevlmsdxdfyl --container-name logs -o table
az storage blob list --account-name stlmsdevlmsdxdfyl --container-name uploads -o table

# Network diagnostics
az network vnet subnet list --vnet-name vnet-lms-dev-lms-dxdfyl --resource-group lms-dev-rg-lms-dxdfyl -o table
az network nsg rule list --nsg-name nsg-lms-dev-lms-dxdfyl --resource-group lms-dev-rg-lms-dxdfyl -o table
az network route-table route list --route-table-name rt-lms-dev-lms-dxdfyl --resource-group lms-dev-rg-lms-dxdfyl -o table

# Get storage key
az keyvault secret show --vault-name kv-lms-dev-lms-dxdfyl --name storage-account-key --query value -o tsv

# Backup database
PGPASSWORD=$(az keyvault secret show --vault-name kv-lms-dev-lms-dxdfyl --name database-admin-password --query value -o tsv) \
pg_dump -h psql-lms-dev-lms-dxdfyl.postgres.database.azure.com -U psqladmin -d lms_auth -F c | \
az storage blob upload --account-name stlmsdevlmsdxdfyl --container-name backups --name "backup-$(date +%Y%m%d_%H%M%S).dump" --file -
```

---

**Previous:** [05-development-data-services-guide.md](./05-development-data-services-guide.md)
**Next:** [07-production-kubernetes-guide.md](./07-production-kubernetes-guide.md) - AKS Cluster Management
