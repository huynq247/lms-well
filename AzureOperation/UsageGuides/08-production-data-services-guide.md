# Production Environment - Data Services & Storage Guide (Resources 71-80)

## Key Vault Secrets: 71-74

### 71. module.spoke_prod.azurerm_key_vault_secret.db_password
**Secret Name:** `database-admin-password`

**Purpose:** PostgreSQL admin password for production environment

**How to Use:**

**Retrieve Password:**
```bash
# Get password from Key Vault
az keyvault secret show \
  --vault-name kv-lms-prod-lms-dxdfyl \
  --name database-admin-password \
  --query value -o tsv
```

**Connect to PostgreSQL:**
```bash
# Using psql
PGPASSWORD=$(az keyvault secret show --vault-name kv-lms-prod-lms-dxdfyl --name database-admin-password --query value -o tsv) \
psql "host=psql-lms-prod-lms-dxdfyl.postgres.database.azure.com \
     port=5432 \
     dbname=lms_auth \
     user=psqladmin \
     sslmode=require"
```

**Use from Kubernetes:**
```yaml
# Create Kubernetes secret from Key Vault
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
  namespace: default
type: Opaque
stringData:
  password: "" # Populated via CSI driver

---
# Use CSI driver (recommended)
apiVersion: secrets-store.csi.x-k8s.io/v1
kind: SecretProviderClass
metadata:
  name: postgres-secrets
spec:
  provider: azure
  secretObjects:
  - secretName: postgres-secret
    type: Opaque
    data:
    - objectName: database-admin-password
      key: password
  parameters:
    keyvaultName: "kv-lms-prod-lms-dxdfyl"
    objects: |
      array:
        - |
          objectName: database-admin-password
          objectType: secret

---
# Deployment using secret
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
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        - name: DB_HOST
          value: "psql-lms-prod-lms-dxdfyl.postgres.database.azure.com"
        - name: DB_USER
          value: "psqladmin"
        - name: DB_NAME
          value: "lms_auth"
      volumes:
      - name: secrets-store
        csi:
          driver: secrets-store.csi.k8s.io
          readOnly: true
          volumeAttributes:
            secretProviderClass: "postgres-secrets"
```

---

### 72. module.spoke_prod.azurerm_key_vault_secret.sa_key
**Secret Name:** `storage-account-key`

**Purpose:** Primary access key for production storage account

**How to Use:**

**Retrieve Key:**
```bash
# Get storage account key
az keyvault secret show \
  --vault-name kv-lms-prod-lms-dxdfyl \
  --name storage-account-key \
  --query value -o tsv
```

**Use with Azure CLI:**
```bash
# Set as environment variable
export AZURE_STORAGE_KEY=$(az keyvault secret show --vault-name kv-lms-prod-lms-dxdfyl --name storage-account-key --query value -o tsv)
export AZURE_STORAGE_ACCOUNT=stlmsprodlmsdxdfyl

# List blobs
az storage blob list --container-name uploads -o table

# Upload file
az storage blob upload \
  --container-name uploads \
  --name myfile.txt \
  --file ./local-file.txt
```

**Use from Kubernetes:**
```yaml
# Create secret for storage account
apiVersion: v1
kind: Secret
metadata:
  name: storage-secret
type: Opaque
stringData:
  account-name: stlmsprodlmsdxdfyl
  account-key: "" # From Key Vault via CSI driver

---
# Use in pod
apiVersion: v1
kind: Pod
metadata:
  name: file-processor
spec:
  containers:
  - name: processor
    image: acrlmslmsdxdfyl.azurecr.io/processor:latest
    env:
    - name: AZURE_STORAGE_ACCOUNT
      valueFrom:
        secretKeyRef:
          name: storage-secret
          key: account-name
    - name: AZURE_STORAGE_KEY
      valueFrom:
        secretKeyRef:
          name: storage-secret
          key: account-key
```

**Rotate Keys:**
```bash
# 1. Regenerate secondary key
az storage account keys renew \
  --account-name stlmsprodlmsdxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --key secondary

# 2. Test with secondary key
# 3. Update applications to use secondary key
# 4. Regenerate primary key
az storage account keys renew \
  --account-name stlmsprodlmsdxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --key primary

# 5. Update Key Vault
NEW_KEY=$(az storage account keys list --account-name stlmsprodlmsdxdfyl --resource-group lms-prod-rg-lms-dxdfyl --query "[0].value" -o tsv)
az keyvault secret set \
  --vault-name kv-lms-prod-lms-dxdfyl \
  --name storage-account-key \
  --value "$NEW_KEY"
```

---

### 73. module.spoke_prod.azurerm_monitor_diagnostic_setting.prod_vnet
**Purpose:** Sends production VNet diagnostic logs to Log Analytics

**How to Use:**

**Query Network Logs:**
```bash
# View all VNet events
az monitor log-analytics query \
  --workspace log-lms-hub-lms-dxdfyl \
  --analytics-query "AzureDiagnostics | where ResourceId contains 'vnet-lms-prod' | take 100"

# Check NSG flow logs
az monitor log-analytics query \
  --workspace log-lms-hub-lms-dxdfyl \
  --analytics-query "AzureDiagnostics | where Category == 'NetworkSecurityGroupFlowEvent' and ResourceId contains 'lms-prod' | take 100"

# Monitor blocked traffic
az monitor log-analytics query \
  --workspace log-lms-hub-lms-dxdfyl \
  --analytics-query "AzureDiagnostics | where Category == 'NetworkSecurityGroupEvent' and ResourceId contains 'lms-prod' and msg_s contains 'Deny' | summarize count() by sourceIP_s | order by count_ desc"
```

**Network Traffic Analysis:**
```bash
# Top talkers (by traffic volume)
az monitor log-analytics query \
  --workspace log-lms-hub-lms-dxdfyl \
  --analytics-query "AzureDiagnostics | where ResourceId contains 'vnet-lms-prod' | summarize TotalBytes=sum(BytesSent_d + BytesReceived_d) by sourceIP_s | top 20 by TotalBytes"

# Connection attempts by destination port
az monitor log-analytics query \
  --workspace log-lms-hub-lms-dxdfyl \
  --analytics-query "AzureDiagnostics | where ResourceId contains 'vnet-lms-prod' | summarize count() by destinationPort_s | order by count_ desc | take 10"
```

**Set Up Alerts:**
```bash
# Alert on high blocked traffic rate
az monitor scheduled-query create \
  --name "prod-high-blocked-traffic" \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --scopes /subscriptions/a9530d40-75da-44a3-9581-b9faf889608c/resourceGroups/rg-lms-hub-lms-dxdfyl/providers/Microsoft.OperationalInsights/workspaces/log-lms-hub-lms-dxdfyl \
  --condition "count 'DeniedFlows' > 500" \
  --condition-query "AzureDiagnostics | where ResourceId contains 'vnet-lms-prod' and msg_s contains 'Deny' | summarize count()" \
  --description "Alert when denied traffic in production exceeds threshold"

# Alert on suspicious source IPs
az monitor scheduled-query create \
  --name "prod-suspicious-ip" \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --scopes /subscriptions/a9530d40-75da-44a3-9581-b9faf889608c/resourceGroups/rg-lms-hub-lms-dxdfyl/providers/Microsoft.OperationalInsights/workspaces/log-lms-hub-lms-dxdfyl \
  --condition "count 'SuspiciousIPs' > 10" \
  --condition-query "AzureDiagnostics | where ResourceId contains 'vnet-lms-prod' and sourceIP_s in ('198.51.100.0', '203.0.113.0') | summarize count()"
```

---

### 74. module.spoke_prod.azurerm_network_security_group.prod
**NSG Name:** `nsg-lms-prod-lms-dxdfyl`

**Purpose:** Controls network access to production resources

**How to Use:**

**View Security Rules:**
```bash
# List all rules
az network nsg rule list \
  --nsg-name nsg-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  -o table

# Show effective security rules for AKS nodes
az network nic list-effective-nsg \
  --resource-group MC_lms-prod-rg-lms-dxdfyl_aks-lms-prod-lms-dxdfyl_southeastasia \
  --name <aks-node-nic>
```

**Add Production Security Rules:**
```bash
# Allow HTTPS from specific IP ranges (e.g., CDN, API Gateway)
az network nsg rule create \
  --nsg-name nsg-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --name Allow-HTTPS-From-CDN \
  --priority 1000 \
  --source-address-prefixes 13.107.0.0/16 \
  --destination-port-ranges 443 \
  --access Allow \
  --protocol Tcp \
  --direction Inbound

# Allow PostgreSQL only from AKS subnet
az network nsg rule create \
  --nsg-name nsg-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --name Allow-PostgreSQL-From-AKS \
  --priority 1100 \
  --source-address-prefixes 10.2.0.0/20 \
  --destination-address-prefixes 10.2.16.0/24 \
  --destination-port-ranges 5432 \
  --access Allow \
  --protocol Tcp

# Deny all other database access
az network nsg rule create \
  --nsg-name nsg-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --name Deny-PostgreSQL-All \
  --priority 4000 \
  --destination-port-ranges 5432 \
  --access Deny \
  --protocol Tcp
```

**Enable NSG Flow Logs:**
```bash
# Create storage account for flow logs (if not exists)
az storage account create \
  --name stflowlogsprodlms \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --sku Standard_LRS

# Enable flow logs
az network watcher flow-log create \
  --name nsg-prod-flow-log \
  --nsg nsg-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --storage-account stflowlogsprodlms \
  --enabled true \
  --retention 90 \
  --traffic-analytics true \
  --workspace log-lms-hub-lms-dxdfyl
```

**Audit Security Rules:**
```bash
# Export rules for compliance audit
az network nsg rule list \
  --nsg-name nsg-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --query "[].{Name:name, Priority:priority, Direction:direction, Access:access, Protocol:protocol, SourceAddressPrefix:sourceAddressPrefix, SourcePortRange:sourcePortRange, DestinationAddressPrefix:destinationAddressPrefix, DestinationPortRange:destinationPortRange}" \
  -o json > prod-nsg-rules-$(date +%Y%m%d).json
```

---

## PostgreSQL Database: 75-76

### 75. module.spoke_prod.azurerm_postgresql_flexible_server.prod
**Server Name:** `psql-lms-prod-lms-dxdfyl`
**Version:** PostgreSQL 16
**SKU:** General Purpose D4s_v3 (4 vCPU, 16 GB RAM)
**Storage:** 128 GB with auto-grow enabled

**Purpose:** Production PostgreSQL database for authentication and transactional data

**How to Use:**

**Connect to Database:**
```bash
# Get connection info
az postgres flexible-server show \
  --name psql-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --query "{FQDN:fullyQualifiedDomainName, State:state, StorageSize:storage.storageSizeGB}"

# Connect with psql
PGPASSWORD=$(az keyvault secret show --vault-name kv-lms-prod-lms-dxdfyl --name database-admin-password --query value -o tsv) \
psql "host=psql-lms-prod-lms-dxdfyl.postgres.database.azure.com \
     port=5432 \
     dbname=lms_auth \
     user=psqladmin \
     sslmode=require"
```

**High Availability:**
```bash
# Enable zone-redundant HA (if not enabled)
az postgres flexible-server update \
  --name psql-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --high-availability ZoneRedundant \
  --standby-availability-zone 2

# Check HA status
az postgres flexible-server show \
  --name psql-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --query "highAvailability"
```

**Backup & Restore:**
```bash
# View backup retention
az postgres flexible-server show \
  --name psql-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --query "backup.backupRetentionDays"

# List available backups
az postgres flexible-server backup list \
  --server-name psql-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl

# Point-in-time restore
az postgres flexible-server restore \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --name psql-lms-prod-restored-$(date +%Y%m%d) \
  --source-server psql-lms-prod-lms-dxdfyl \
  --restore-time "2025-02-02T14:30:00Z"

# Restore to different server
az postgres flexible-server geo-restore \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --name psql-lms-prod-dr \
  --source-server psql-lms-prod-lms-dxdfyl \
  --location eastasia
```

**Performance Tuning:**
```bash
# View server parameters
az postgres flexible-server parameter list \
  --server-name psql-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  -o table

# Update parameters
az postgres flexible-server parameter set \
  --server-name psql-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --name max_connections \
  --value 500

az postgres flexible-server parameter set \
  --server-name psql-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --name shared_buffers \
  --value 2097152  # 2GB in 8KB pages

# Enable query performance insights
az postgres flexible-server parameter set \
  --server-name psql-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --name pg_stat_statements.track \
  --value ALL
```

**Monitor Performance:**
```bash
# Check CPU and memory usage
az monitor metrics list \
  --resource /subscriptions/a9530d40-75da-44a3-9581-b9faf889608c/resourceGroups/lms-prod-rg-lms-dxdfyl/providers/Microsoft.DBforPostgreSQL/flexibleServers/psql-lms-prod-lms-dxdfyl \
  --metric "cpu_percent" \
  --aggregation Average

# Check connections
az monitor metrics list \
  --resource /subscriptions/a9530d40-75da-44a3-9581-b9faf889608c/resourceGroups/lms-prod-rg-lms-dxdfyl/providers/Microsoft.DBforPostgreSQL/flexibleServers/psql-lms-prod-lms-dxdfyl \
  --metric "active_connections"

# Check storage usage
az monitor metrics list \
  --resource /subscriptions/a9530d40-75da-44a3-9581-b9faf889608c/resourceGroups/lms-prod-rg-lms-dxdfyl/providers/Microsoft.DBforPostgreSQL/flexibleServers/psql-lms-prod-lms-dxdfyl \
  --metric "storage_percent"
```

**Scale Operations:**
```bash
# Scale up compute
az postgres flexible-server update \
  --name psql-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --sku-name Standard_D8s_v3 \
  --tier GeneralPurpose

# Increase storage (cannot decrease)
az postgres flexible-server update \
  --name psql-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --storage-size 256
```

**Maintenance Window:**
```bash
# Set maintenance window (Sunday 2 AM - 6 AM)
az postgres flexible-server update \
  --name psql-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --maintenance-window day=0 hour=2 minute=0
```

---

### 76. module.spoke_prod.azurerm_postgresql_flexible_server_database.prod
**Database Name:** `lms_auth`

**Purpose:** Production authentication and user management database

**How to Use:**

**Database Operations:**
```sql
-- Connect to database
\c lms_auth

-- View tables
\dt

-- Create production tables
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'student',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER,
    action VARCHAR(100) NOT NULL,
    resource VARCHAR(100),
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_sessions_token ON sessions(token);
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);
CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at);

-- Create database user for application
CREATE ROLE lms_app WITH LOGIN PASSWORD 'secure-app-password';
GRANT CONNECT ON DATABASE lms_auth TO lms_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO lms_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO lms_app;

-- Enable row-level security (optional)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
CREATE POLICY user_isolation ON users
    USING (id = current_setting('app.user_id')::integer);
```

**Maintenance Tasks:**
```sql
-- Analyze query performance
SELECT query, calls, total_time, mean_time, max_time
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;

-- Check table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Vacuum and analyze
VACUUM ANALYZE users;
VACUUM ANALYZE sessions;
VACUUM ANALYZE audit_log;

-- Check index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
ORDER BY idx_scan;
```

**Automated Backup Script:**
```bash
#!/bin/bash
# backup-prod-postgres.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="lms_auth_prod_${DATE}.dump"

# Get password from Key Vault
PASSWORD=$(az keyvault secret show --vault-name kv-lms-prod-lms-dxdfyl --name database-admin-password --query value -o tsv)

# Create backup
PGPASSWORD=$PASSWORD pg_dump \
  -h psql-lms-prod-lms-dxdfyl.postgres.database.azure.com \
  -U psqladmin \
  -d lms_auth \
  -F c \
  -f "$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_FILE"

# Upload to blob storage
az storage blob upload \
  --account-name stlmsprodlmsdxdfyl \
  --container-name backups \
  --name "postgres/$BACKUP_FILE.gz" \
  --file "$BACKUP_FILE.gz"

# Clean up
rm "$BACKUP_FILE.gz"

echo "Production backup completed: $BACKUP_FILE.gz"
```

---

## Resource Management: 77-80

### 77. module.spoke_prod.azurerm_resource_group.prod
**Resource Group:** `lms-prod-rg-lms-dxdfyl`

**Purpose:** Contains all production environment resources

**How to Use:**

**View Resources:**
```bash
# List all production resources
az resource list \
  --resource-group lms-prod-rg-lms-dxdfyl \
  -o table

# Count by resource type
az resource list \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --query "type" -o tsv | sort | uniq -c

# Export resource list with details
az resource list \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --query "[].{Name:name, Type:type, Location:location, ProvisioningState:provisioningState}" \
  -o json > prod-resources-$(date +%Y%m%d).json
```

**Cost Analysis:**
```bash
# View costs for production
az consumption usage list \
  --start-date 2025-02-01 \
  --end-date 2025-02-28 \
  --query "[?contains(instanceId, 'lms-prod-rg')].[instanceName, usageStart, quantity, pretaxCost, currency]" \
  -o table

# Summary by resource type
az consumption usage list \
  --start-date 2025-02-01 \
  --end-date 2025-02-28 \
  --query "[?contains(instanceId, 'lms-prod-rg')] | group_by(@, &meterCategory).{Category:key, TotalCost:sum(values[*].pretaxCost)}"
```

**Apply Resource Locks:**
```bash
# Add delete lock (prevent accidental deletion)
az lock create \
  --name prod-delete-lock \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --lock-type CanNotDelete \
  --notes "Production environment - delete protection"

# Add read-only lock (for critical resources)
az lock create \
  --name prod-readonly-lock \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --lock-type ReadOnly \
  --notes "Production environment - change protection"

# List locks
az lock list --resource-group lms-prod-rg-lms-dxdfyl -o table

# Remove lock (when needed)
az lock delete --name prod-delete-lock --resource-group lms-prod-rg-lms-dxdfyl
```

**Tags for Management:**
```bash
# Add cost center and project tags
az group update \
  --name lms-prod-rg-lms-dxdfyl \
  --tags Environment=Production CostCenter=IT-Education Project=LMS Owner=Platform-Team Criticality=High

# Query resources by tags
az resource list \
  --tag Environment=Production \
  -o table
```

---

### 78. module.spoke_prod.azurerm_route_table.prod
**Route Table:** `rt-lms-prod-lms-dxdfyl`

**Purpose:** Routes production traffic through Azure Firewall

**How to Use:**

**View Routes:**
```bash
# List all routes
az network route-table route list \
  --route-table-name rt-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  -o table
```

**Expected Routes:**
```
Name          Address Prefix    Next Hop Type      Next Hop IP
------------  ----------------  -----------------  ------------
to-internet   0.0.0.0/0         VirtualAppliance   10.0.1.4
to-hub        10.0.0.0/16       VirtualAppliance   10.0.1.4
to-dev        10.1.0.0/16       VirtualAppliance   10.0.1.4
```

**Add Custom Routes:**
```bash
# Route to partner network via VPN
az network route-table route create \
  --route-table-name rt-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --name to-partner-network \
  --address-prefix 172.16.0.0/12 \
  --next-hop-type VirtualAppliance \
  --next-hop-ip-address 10.0.1.4

# Bypass firewall for specific Azure service (if needed)
az network route-table route create \
  --route-table-name rt-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --name to-azure-sql \
  --address-prefix 13.76.0.0/16 \
  --next-hop-type Internet
```

**Verify Effective Routes:**
```bash
# Get AKS node NIC name
AKS_NODE_NIC=$(az vm nic list --resource-group MC_lms-prod-rg-lms-dxdfyl_aks-lms-prod-lms-dxdfyl_southeastasia --query "[0].id" -o tsv)

# View effective routes
az network nic show-effective-route-table \
  --ids $AKS_NODE_NIC \
  -o table
```

---

### 79. module.spoke_prod.azurerm_storage_account.prod
**Storage Account:** `stlmsprodlmsdxdfyl`
**Replication:** ZRS (Zone-Redundant Storage)
**Performance Tier:** Standard

**Purpose:** Production storage for uploads, backups, and static content

**How to Use:**

**Access Storage:**
```bash
# Get connection string (use Key Vault in production)
az storage account show-connection-string \
  --name stlmsprodlmsdxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --query connectionString -o tsv

# Get account key
az keyvault secret show \
  --vault-name kv-lms-prod-lms-dxdfyl \
  --name storage-account-key \
  --query value -o tsv
```

**Blob Operations:**
```bash
# List containers
az storage container list \
  --account-name stlmsprodlmsdxdfyl \
  -o table

# Upload file
az storage blob upload \
  --account-name stlmsprodlmsdxdfyl \
  --container-name uploads \
  --name documents/report.pdf \
  --file ./report.pdf \
  --content-type application/pdf

# Download file
az storage blob download \
  --account-name stlmsprodlmsdxdfyl \
  --container-name backups \
  --name postgres/latest.dump.gz \
  --file ./latest-backup.dump.gz

# Generate SAS token (read-only, 1 hour)
az storage blob generate-sas \
  --account-name stlmsprodlmsdxdfyl \
  --container-name uploads \
  --name documents/report.pdf \
  --permissions r \
  --expiry $(date -u -d "1 hour" '+%Y-%m-%dT%H:%MZ') \
  --https-only
```

**Use from AKS:**
```yaml
# Mount blob storage in Kubernetes using CSI driver
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-blob
spec:
  capacity:
    storage: 100Gi
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  csi:
    driver: blob.csi.azure.com
    volumeHandle: stlmsprodlmsdxdfyl-uploads
    volumeAttributes:
      containerName: uploads
      storageAccount: stlmsprodlmsdxdfyl
    nodeStageSecretRef:
      name: storage-secret
      namespace: default

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-blob
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 100Gi
  volumeName: pv-blob

---
# Use in pod
apiVersion: v1
kind: Pod
metadata:
  name: file-processor
spec:
  containers:
  - name: processor
    image: acrlmslmsdxdfyl.azurecr.io/processor:latest
    volumeMounts:
    - name: blob-storage
      mountPath: /mnt/uploads
  volumes:
  - name: blob-storage
    persistentVolumeClaim:
      claimName: pvc-blob
```

**Lifecycle Management:**
```bash
# Move old files to cool tier after 30 days
az storage account management-policy create \
  --account-name stlmsprodlmsdxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --policy '{
    "rules": [
      {
        "enabled": true,
        "name": "move-to-cool",
        "type": "Lifecycle",
        "definition": {
          "filters": {
            "blobTypes": ["blockBlob"],
            "prefixMatch": ["uploads/"]
          },
          "actions": {
            "baseBlob": {
              "tierToCool": {"daysAfterModificationGreaterThan": 30},
              "tierToArchive": {"daysAfterModificationGreaterThan": 90},
              "delete": {"daysAfterModificationGreaterThan": 365}
            }
          }
        }
      }
    ]
  }'
```

---

### 80. module.spoke_prod.azurerm_storage_account_network_rules.prod
**Purpose:** Network isolation for production storage account

**Configuration:**
- Default Action: Deny
- Allowed VNets: Production VNet (10.2.0.0/16)
- Bypass: AzureServices, Metrics, Logging

**How to Use:**

**View Network Rules:**
```bash
# Show network rules
az storage account show \
  --name stlmsprodlmsdxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --query "networkRuleSet"
```

**Add IP Exceptions:**
```bash
# Allow specific public IP (for admin access)
az storage account network-rule add \
  --account-name stlmsprodlmsdxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --ip-address 203.0.113.50

# Allow IP range
az storage account network-rule add \
  --account-name stlmsprodlmsdxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --ip-address 203.0.113.0/24

# List IP rules
az storage account network-rule list \
  --account-name stlmsprodlmsdxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --query "ipRules"
```

**Add VNet Rules:**
```bash
# Allow access from additional subnet
az storage account network-rule add \
  --account-name stlmsprodlmsdxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --vnet-name vnet-lms-prod-lms-dxdfyl \
  --subnet private-endpoints-subnet
```

**Temporary Admin Access:**
```bash
# Temporarily allow all access (for emergency maintenance)
az storage account update \
  --name stlmsprodlmsdxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --default-action Allow

# Re-enable restrictions after maintenance
az storage account update \
  --name stlmsprodlmsdxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl \
  --default-action Deny
```

---

## Quick Reference Commands

```bash
# Production health check
kubectl get nodes
kubectl get pods --all-namespaces
az postgres flexible-server show --name psql-lms-prod-lms-dxdfyl --resource-group lms-prod-rg-lms-dxdfyl --query state -o tsv
az cosmosdb show --name cosmos-lms-prod-lms-dxdfyl --resource-group lms-prod-rg-lms-dxdfyl --query provisioningState -o tsv

# Get credentials
az keyvault secret show --vault-name kv-lms-prod-lms-dxdfyl --name database-admin-password --query value -o tsv
az keyvault secret show --vault-name kv-lms-prod-lms-dxdfyl --name cosmosdb-primary-key --query value -o tsv
az keyvault secret show --vault-name kv-lms-prod-lms-dxdfyl --name storage-account-key --query value -o tsv

# Backup production database
./backup-prod-postgres.sh

# List storage containers
az storage container list --account-name stlmsprodlmsdxdfyl -o table
```

---

**Previous:** [07-production-kubernetes-guide.md](./07-production-kubernetes-guide.md)
**Next:** [09-production-networking-storage-guide.md](./09-production-networking-storage-guide.md) - Production Subnets and Network Configuration
