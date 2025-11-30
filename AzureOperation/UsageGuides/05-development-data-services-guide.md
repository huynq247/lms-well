# Development Environment - Data Services & Storage Guide (Resources 41-50)

## Load Balancing Rules: 41-42

### 41. module.spoke_dev.azurerm_lb_rule.dev
**Rule Name:** `http-rule`

**Purpose:** Load balancer rule directing HTTP traffic (port 80) to backend pool

**Configuration:**
- Frontend Port: 80
- Backend Port: 80
- Protocol: TCP
- Session Affinity: None (round-robin)
- Idle Timeout: 4 minutes

**How to Use:**

**View Rule Details:**
```bash
# Show load balancing rule
az network lb rule show \
  --lb-name lb-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --name http-rule

# List all rules
az network lb rule list \
  --lb-name lb-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  -o table
```

**Add Additional Rules:**
```bash
# Add HTTPS rule
az network lb rule create \
  --lb-name lb-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --name https-rule \
  --protocol Tcp \
  --frontend-port 443 \
  --backend-port 443 \
  --frontend-ip-name frontend-ip \
  --backend-pool-name backend-pool \
  --probe-name http-probe

# Add custom application port
az network lb rule create \
  --lb-name lb-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --name app-rule \
  --protocol Tcp \
  --frontend-port 8080 \
  --backend-port 8080 \
  --frontend-ip-name frontend-ip \
  --backend-pool-name backend-pool \
  --probe-name http-probe
```

**Enable Session Affinity:**
```bash
# Update rule to enable client IP affinity (sticky sessions)
az network lb rule update \
  --lb-name lb-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --name http-rule \
  --load-distribution SourceIP

# Options:
# - Default: 5-tuple hash (Source IP, Source Port, Destination IP, Destination Port, Protocol)
# - SourceIP: 2-tuple hash (Source IP, Destination IP) - sticky sessions
# - SourceIPProtocol: 3-tuple hash (Source IP, Destination IP, Protocol)
```

**Adjust Idle Timeout:**
```bash
# Increase idle timeout for long-running connections
az network lb rule update \
  --lb-name lb-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --name http-rule \
  --idle-timeout 15  # Minutes (4-30)
```

---

### 42. module.spoke_dev.azurerm_linux_virtual_machine_scale_set.dev
**VMSS Name:** `lms-dev-vmss-lms-dxdfyl`
**Size:** Standard_D2s_v3 (2 vCPU, 8 GB RAM)
**OS:** Ubuntu 22.04 LTS
**Instances:** 2 (configurable)

**Purpose:** Scalable compute resources for development applications

**How to Use:**

**Manage Instances:**
```bash
# List instances
az vmss list-instances \
  --name lms-dev-vmss-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  -o table

# Get instance details
az vmss get-instance-view \
  --name lms-dev-vmss-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl

# Restart all instances
az vmss restart \
  --name lms-dev-vmss-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl

# Restart specific instance
az vmss restart \
  --name lms-dev-vmss-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --instance-ids 0
```

**Scale Operations:**
```bash
# Manual scaling
az vmss scale \
  --name lms-dev-vmss-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --new-capacity 3

# Set up autoscale (CPU-based)
az monitor autoscale create \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --resource lms-dev-vmss-lms-dxdfyl \
  --resource-type Microsoft.Compute/virtualMachineScaleSets \
  --name autoscale-dev \
  --min-count 2 \
  --max-count 10 \
  --count 2

# Add scale-out rule (CPU > 70%)
az monitor autoscale rule create \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --autoscale-name autoscale-dev \
  --condition "Percentage CPU > 70 avg 5m" \
  --scale out 1

# Add scale-in rule (CPU < 30%)
az monitor autoscale rule create \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --autoscale-name autoscale-dev \
  --condition "Percentage CPU < 30 avg 5m" \
  --scale in 1
```

**Run Commands on Instances:**
```bash
# Run command on all instances
az vmss run-command invoke \
  --command-id RunShellScript \
  --name lms-dev-vmss-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --scripts "sudo apt update && sudo apt upgrade -y"

# Run on specific instance
az vmss run-command invoke \
  --command-id RunShellScript \
  --name lms-dev-vmss-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --instance-id 0 \
  --scripts "docker ps"

# Deploy application
az vmss run-command invoke \
  --command-id RunShellScript \
  --name lms-dev-vmss-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --scripts "cd /app && git pull && docker-compose up -d"
```

**Connect via Bastion:**
```bash
# SSH to instance 0
az network bastion ssh \
  --name bastion-lms-hub \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --target-resource-id /subscriptions/a9530d40-75da-44a3-9581-b9faf889608c/resourceGroups/lms-dev-rg-lms-dxdfyl/providers/Microsoft.Compute/virtualMachineScaleSets/lms-dev-vmss-lms-dxdfyl/virtualMachines/0 \
  --auth-type ssh-key \
  --username azureuser \
  --ssh-key ~/.ssh/id_rsa
```

**Update VMSS Image:**
```bash
# Update to latest Ubuntu image
az vmss update \
  --name lms-dev-vmss-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --set virtualMachineProfile.storageProfile.imageReference.version=latest

# Upgrade instances to new image (rolling upgrade)
az vmss update-instances \
  --name lms-dev-vmss-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --instance-ids "*"
```

**Monitor Performance:**
```bash
# CPU usage
az monitor metrics list \
  --resource /subscriptions/a9530d40-75da-44a3-9581-b9faf889608c/resourceGroups/lms-dev-rg-lms-dxdfyl/providers/Microsoft.Compute/virtualMachineScaleSets/lms-dev-vmss-lms-dxdfyl \
  --metric "Percentage CPU" \
  --aggregation Average

# Memory usage
az monitor metrics list \
  --resource /subscriptions/a9530d40-75da-44a3-9581-b9faf889608c/resourceGroups/lms-dev-rg-lms-dxdfyl/providers/Microsoft.Compute/virtualMachineScaleSets/lms-dev-vmss-lms-dxdfyl \
  --metric "Available Memory Bytes"
```

---

## Log Analytics Integration: 43

### 43. module.spoke_dev.azurerm_monitor_diagnostic_setting.dev_vnet
**Purpose:** Sends VNet diagnostic logs to Log Analytics workspace

**How to Use:**

**Query VNet Logs:**
```bash
# View all VNet logs
az monitor log-analytics query \
  --workspace log-lms-hub-lms-dxdfyl \
  --analytics-query "AzureDiagnostics | where ResourceId contains 'vnet-lms-dev' | take 100"

# Check NSG flow logs
az monitor log-analytics query \
  --workspace log-lms-hub-lms-dxdfyl \
  --analytics-query "AzureDiagnostics | where Category == 'NetworkSecurityGroupFlowEvent' and ResourceId contains 'lms-dev'"

# Monitor blocked traffic
az monitor log-analytics query \
  --workspace log-lms-hub-lms-dxdfyl \
  --analytics-query "AzureDiagnostics | where Category == 'NetworkSecurityGroupEvent' and ResourceId contains 'lms-dev' and msg_s contains 'Deny'"
```

**Analyze Traffic Patterns:**
```bash
# Top source IPs
az monitor log-analytics query \
  --workspace log-lms-hub-lms-dxdfyl \
  --analytics-query "AzureDiagnostics | where ResourceId contains 'vnet-lms-dev' | summarize count() by sourceIP_s | top 10 by count_"

# Traffic by destination port
az monitor log-analytics query \
  --workspace log-lms-hub-lms-dxdfyl \
  --analytics-query "AzureDiagnostics | where ResourceId contains 'vnet-lms-dev' | summarize count() by destinationPort_s | order by count_ desc"
```

**Create Alerts:**
```bash
# Alert on high denied traffic
az monitor scheduled-query create \
  --name "dev-high-denied-traffic" \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --scopes /subscriptions/a9530d40-75da-44a3-9581-b9faf889608c/resourceGroups/rg-lms-hub-lms-dxdfyl/providers/Microsoft.OperationalInsights/workspaces/log-lms-hub-lms-dxdfyl \
  --condition "count 'Denied' > 100" \
  --condition-query "AzureDiagnostics | where ResourceId contains 'vnet-lms-dev' and msg_s contains 'Deny' | summarize count()" \
  --description "Alert when denied traffic exceeds threshold"
```

---

## Networking & Security: 44-46

### 44. module.spoke_dev.azurerm_network_security_group.dev
**NSG Name:** `nsg-lms-dev-lms-dxdfyl`

**Purpose:** Controls traffic to/from development subnet

**How to Use:**

**View Security Rules:**
```bash
# List all rules
az network nsg rule list \
  --nsg-name nsg-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  -o table

# Show specific rule
az network nsg rule show \
  --nsg-name nsg-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --name AllowHTTP
```

**Add Custom Rules:**
```bash
# Allow SSH from hub subnet
az network nsg rule create \
  --nsg-name nsg-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --name Allow-SSH-From-Hub \
  --priority 1000 \
  --source-address-prefixes 10.0.0.0/24 \
  --destination-port-ranges 22 \
  --access Allow \
  --protocol Tcp \
  --direction Inbound

# Allow PostgreSQL from app subnet
az network nsg rule create \
  --nsg-name nsg-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --name Allow-PostgreSQL \
  --priority 1100 \
  --source-address-prefixes 10.1.2.0/24 \
  --destination-port-ranges 5432 \
  --access Allow \
  --protocol Tcp \
  --direction Inbound

# Block outbound to specific IP
az network nsg rule create \
  --nsg-name nsg-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --name Deny-Malicious-IP \
  --priority 4000 \
  --destination-address-prefixes 198.51.100.0/24 \
  --access Deny \
  --direction Outbound
```

**Analyze NSG Flow Logs:**
```bash
# Enable flow logs (if not enabled)
az network watcher flow-log create \
  --name nsg-dev-flow-log \
  --nsg nsg-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --storage-account <storage-account-id> \
  --enabled true \
  --retention 30

# Query flow logs via Log Analytics
az monitor log-analytics query \
  --workspace log-lms-hub-lms-dxdfyl \
  --analytics-query "AzureNetworkAnalytics_CL | where SubType_s == 'FlowLog' and ResourceId contains 'nsg-lms-dev'"
```

---

### 45. module.spoke_dev.azurerm_postgresql_flexible_server.dev
**Server Name:** `psql-lms-dev-lms-dxdfyl`
**Version:** PostgreSQL 16
**SKU:** Burstable B1ms (1 vCore, 2 GB RAM)
**Storage:** 32 GB

**Purpose:** PostgreSQL database for development applications

**How to Use:**

**Connect to Database:**
```bash
# Get connection information
az postgres flexible-server show \
  --name psql-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --query "{FQDN:fullyQualifiedDomainName, State:state}" -o table

# Connect using psql
PGPASSWORD=$(az keyvault secret show --vault-name kv-lms-dev-lms-dxdfyl --name database-admin-password --query value -o tsv) \
psql "host=psql-lms-dev-lms-dxdfyl.postgres.database.azure.com \
     port=5432 \
     dbname=lms_auth \
     user=psqladmin \
     sslmode=require"

# Connection string format
postgresql://psqladmin:<password>@psql-lms-dev-lms-dxdfyl.postgres.database.azure.com:5432/lms_auth?sslmode=require
```

**Database Management:**
```bash
# List databases
az postgres flexible-server db list \
  --server-name psql-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  -o table

# Create new database
az postgres flexible-server db create \
  --server-name psql-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --database-name lms_content

# Delete database
az postgres flexible-server db delete \
  --server-name psql-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --database-name old_database \
  --yes
```

**Backup & Restore:**
```bash
# Backups are automatic (7-day retention by default)
# List available backups
az postgres flexible-server backup list \
  --server-name psql-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl

# Restore to a point in time
az postgres flexible-server restore \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --name psql-lms-dev-restored \
  --source-server psql-lms-dev-lms-dxdfyl \
  --restore-time "2025-02-02T10:00:00Z"

# Export database
pg_dump "postgresql://psqladmin:<password>@psql-lms-dev-lms-dxdfyl.postgres.database.azure.com/lms_auth?sslmode=require" > backup.sql

# Import database
psql "postgresql://psqladmin:<password>@psql-lms-dev-lms-dxdfyl.postgres.database.azure.com/lms_auth?sslmode=require" < backup.sql
```

**Scale Server:**
```bash
# Scale up to General Purpose
az postgres flexible-server update \
  --name psql-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --sku-name Standard_D2s_v3 \
  --tier GeneralPurpose

# Increase storage
az postgres flexible-server update \
  --name psql-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --storage-size 64
```

**Monitor Performance:**
```bash
# Check connections
az postgres flexible-server show \
  --name psql-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --query "highAvailability.state"

# View metrics
az monitor metrics list \
  --resource /subscriptions/a9530d40-75da-44a3-9581-b9faf889608c/resourceGroups/lms-dev-rg-lms-dxdfyl/providers/Microsoft.DBforPostgreSQL/flexibleServers/psql-lms-dev-lms-dxdfyl \
  --metric "cpu_percent" \
  --aggregation Average

# Check storage usage
az monitor metrics list \
  --resource /subscriptions/a9530d40-75da-44a3-9581-b9faf889608c/resourceGroups/lms-dev-rg-lms-dxdfyl/providers/Microsoft.DBforPostgreSQL/flexibleServers/psql-lms-dev-lms-dxdfyl \
  --metric "storage_percent"
```

**Firewall Rules:**
```bash
# Allow Azure services
az postgres flexible-server firewall-rule create \
  --server-name psql-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --name AllowAzure \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0

# Allow specific IP range
az postgres flexible-server firewall-rule create \
  --server-name psql-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --name AllowOffice \
  --start-ip-address 203.0.113.0 \
  --end-ip-address 203.0.113.255
```

---

### 46. module.spoke_dev.azurerm_postgresql_flexible_server_database.dev
**Database Name:** `lms_auth`

**Purpose:** Authentication and user management database

**How to Use:**

**Connect to Database:**
```bash
# Direct connection
PGPASSWORD=$(az keyvault secret show --vault-name kv-lms-dev-lms-dxdfyl --name database-admin-password --query value -o tsv) \
psql -h psql-lms-dev-lms-dxdfyl.postgres.database.azure.com \
     -U psqladmin \
     -d lms_auth \
     -c "SELECT version();"
```

**Database Operations:**
```sql
-- Connect and check tables
\c lms_auth
\dt

-- Create tables
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Create indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

-- Grant permissions
GRANT SELECT, INSERT, UPDATE ON users TO app_user;
```

**Application Integration:**
```python
# Python (SQLAlchemy)
from sqlalchemy import create_engine
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
secret_client = SecretClient("https://kv-lms-dev-lms-dxdfyl.vault.azure.net/", credential)
password = secret_client.get_secret("database-admin-password").value

engine = create_engine(
    f"postgresql://psqladmin:{password}@psql-lms-dev-lms-dxdfyl.postgres.database.azure.com:5432/lms_auth?sslmode=require"
)

# Execute query
with engine.connect() as conn:
    result = conn.execute("SELECT * FROM users LIMIT 10")
    for row in result:
        print(row)
```

---

## Resource Group & Networking: 47-50

### 47. module.spoke_dev.azurerm_resource_group.dev
**Resource Group:** `lms-dev-rg-lms-dxdfyl`

**Purpose:** Contains all development environment resources

**How to Use:**

**View Resources:**
```bash
# List all resources
az resource list \
  --resource-group lms-dev-rg-lms-dxdfyl \
  -o table

# Count by type
az resource list \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --query "type" -o tsv | sort | uniq -c

# View with details
az resource list \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --query "[].{Name:name, Type:type, Location:location}" \
  -o table
```

**Cost Management:**
```bash
# View costs
az consumption usage list \
  --start-date 2025-02-01 \
  --end-date 2025-02-28 \
  --query "[?contains(instanceId, 'lms-dev-rg')]" \
  -o table

# Export cost data
az consumption usage list \
  --start-date 2025-02-01 \
  --end-date 2025-02-28 \
  --query "[?contains(instanceId, 'lms-dev-rg')]" > dev-costs.json
```

**Resource Locks:**
```bash
# Add delete lock to prevent accidental deletion
az lock create \
  --name dev-delete-lock \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --lock-type CanNotDelete \
  --notes "Prevent accidental deletion"

# Remove lock
az lock delete \
  --name dev-delete-lock \
  --resource-group lms-dev-rg-lms-dxdfyl
```

---

### 48. module.spoke_dev.azurerm_route_table.dev
**Route Table:** `rt-lms-dev-lms-dxdfyl`

**Purpose:** Routes all traffic through Azure Firewall in hub

**How to Use:**

**View Routes:**
```bash
# List routes
az network route-table route list \
  --route-table-name rt-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  -o table
```

**Routes Configuration:**
```
Name              Address Prefix    Next Hop Type       Next Hop IP
----------------  ----------------  ------------------  ------------
to-internet       0.0.0.0/0         VirtualAppliance    10.0.1.4
to-hub            10.0.0.0/16       VirtualAppliance    10.0.1.4
to-prod           10.2.0.0/16       VirtualAppliance    10.0.1.4
```

**Add Custom Route:**
```bash
# Route to on-premises
az network route-table route create \
  --route-table-name rt-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --name to-onprem \
  --address-prefix 192.168.0.0/16 \
  --next-hop-type VirtualAppliance \
  --next-hop-ip-address 10.0.1.4
```

---

### 49. module.spoke_dev.azurerm_storage_account.dev
**Storage Account:** `stlmsdevlmsdxdfyl`

**Purpose:** Blob storage for development files, logs, backups

**How to Use:**

**Access Storage:**
```bash
# Get connection string
az storage account show-connection-string \
  --name stlmsdevlmsdxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --query connectionString -o tsv

# Get account key
az storage account keys list \
  --account-name stlmsdevlmsdxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --query "[0].value" -o tsv
```

**Upload/Download Files:**
```bash
# Upload file
az storage blob upload \
  --account-name stlmsdevlmsdxdfyl \
  --container-name uploads \
  --name myfile.txt \
  --file ./local-file.txt

# Download file
az storage blob download \
  --account-name stlmsdevlmsdxdfyl \
  --container-name uploads \
  --name myfile.txt \
  --file ./downloaded-file.txt

# List blobs
az storage blob list \
  --account-name stlmsdevlmsdxdfyl \
  --container-name uploads \
  -o table
```

**Use with Python:**
```python
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
blob_service_client = BlobServiceClient(
    account_url="https://stlmsdevlmsdxdfyl.blob.core.windows.net",
    credential=credential
)

# Upload blob
blob_client = blob_service_client.get_blob_client(container="uploads", blob="test.txt")
with open("./test.txt", "rb") as data:
    blob_client.upload_blob(data, overwrite=True)
```

---

### 50. module.spoke_dev.azurerm_storage_account_network_rules.dev
**Purpose:** Restricts storage account access to specific networks

**Configuration:**
- Default Action: Deny
- Allowed VNets: Dev VNet (10.1.0.0/16)
- Bypass: AzureServices

**How to Use:**

**View Network Rules:**
```bash
# Show network rules
az storage account show \
  --name stlmsdevlmsdxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --query "networkRuleSet"
```

**Add IP Range:**
```bash
# Allow specific public IP
az storage account network-rule add \
  --account-name stlmsdevlmsdxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --ip-address 203.0.113.50

# Allow IP range
az storage account network-rule add \
  --account-name stlmsdevlmsdxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --ip-address 203.0.113.0/24
```

---

## Quick Reference Commands

```bash
# Development health check
az vmss list-instances --name lms-dev-vmss-lms-dxdfyl --resource-group lms-dev-rg-lms-dxdfyl -o table
az postgres flexible-server show --name psql-lms-dev-lms-dxdfyl --resource-group lms-dev-rg-lms-dxdfyl --query state -o tsv
az cosmosdb show --name cosmos-lms-dev-lms-dxdfyl --resource-group lms-dev-rg-lms-dxdfyl --query provisioningState -o tsv

# Get all credentials
az keyvault secret show --vault-name kv-lms-dev-lms-dxdfyl --name database-admin-password --query value -o tsv
az keyvault secret show --vault-name kv-lms-dev-lms-dxdfyl --name cosmosdb-primary-key --query value -o tsv
az keyvault secret show --vault-name kv-lms-dev-lms-dxdfyl --name storage-account-key --query value -o tsv
```

---

**Previous:** [04-development-compute-guide.md](./04-development-compute-guide.md)
**Next:** [06-development-networking-security-guide.md](./06-development-networking-security-guide.md) - Dev Subnets and Network Configuration
