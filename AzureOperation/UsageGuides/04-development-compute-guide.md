# Development Environment - Compute & Networking Guide (Resources 31-40)

## Development Environment Foundation: 31-33

### 31. module.spoke_dev.data.azurerm_client_config.current
**Purpose:** Data source providing Azure subscription and tenant information for dev environment

**Information Provided:**
- Subscription ID: `a9530d40-75da-44a3-9581-b9faf889608c`
- Tenant ID: Used for Key Vault access policies
- Object ID: For IAM role assignments

**How to Use:**
```bash
# Verify current Azure context
az account show

# Ensure you're in the correct subscription
az account set --subscription a9530d40-75da-44a3-9581-b9faf889608c

# View tenant details
az account show --query "{SubscriptionId:id, TenantId:tenantId, Name:name}"
```

---

### 32. module.spoke_dev.azurerm_cosmosdb_account.dev
**Cosmos DB Account:** `cosmos-lms-dev-lms-dxdfyl`
**API:** SQL (Core)
**Location:** Southeast Asia

**Purpose:** NoSQL database for development environment (content, sessions, logs)

**How to Use:**

**Get Connection Information:**
```bash
# Get primary connection string
az cosmosdb keys list \
  --name cosmos-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --type connection-strings \
  --query "connectionStrings[0].connectionString" -o tsv

# Get primary key only
az cosmosdb keys list \
  --name cosmos-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --query primaryMasterKey -o tsv

# Get endpoint URL
az cosmosdb show \
  --name cosmos-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --query documentEndpoint -o tsv
```

**Connect from Application:**
```python
# Python example
from azure.cosmos import CosmosClient

endpoint = "https://cosmos-lms-dev-lms-dxdfyl.documents.azure.com:443/"
key = "your-primary-key"  # From Key Vault: cosmosdb-primary-key

client = CosmosClient(endpoint, key)
database = client.get_database_client("lms_content")
container = database.get_container_client("courses")

# Query documents
for item in container.query_items(
    query="SELECT * FROM c WHERE c.status = 'active'",
    enable_cross_partition_query=True
):
    print(item)
```

**Manage Databases:**
```bash
# List databases
az cosmosdb sql database list \
  --account-name cosmos-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  -o table

# List containers in a database
az cosmosdb sql container list \
  --account-name cosmos-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --database-name lms_content \
  -o table
```

**Monitor Performance:**
```bash
# Check RU consumption
az monitor metrics list \
  --resource /subscriptions/a9530d40-75da-44a3-9581-b9faf889608c/resourceGroups/lms-dev-rg-lms-dxdfyl/providers/Microsoft.DocumentDB/databaseAccounts/cosmos-lms-dev-lms-dxdfyl \
  --metric "TotalRequestUnits" \
  --aggregation Total

# View throttled requests
az monitor metrics list \
  --resource /subscriptions/a9530d40-75da-44a3-9581-b9faf889608c/resourceGroups/lms-dev-rg-lms-dxdfyl/providers/Microsoft.DocumentDB/databaseAccounts/cosmos-lms-dev-lms-dxdfyl \
  --metric "UserReplicationLag"
```

**Backup & Restore:**
```bash
# Cosmos DB uses automatic continuous backup (7 days retention)
# To restore, open Azure Portal > Cosmos DB > Restore

# Or via CLI (requires timestamp)
az cosmosdb sql database restore \
  --account-name cosmos-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --name lms_content \
  --restore-timestamp "2025-02-01T10:00:00Z"
```

---

### 33. module.spoke_dev.azurerm_cosmosdb_sql_database.dev
**Database Name:** `lms_content`

**Purpose:** SQL API database for storing application data

**How to Use:**

**View Database Details:**
```bash
# Show database information
az cosmosdb sql database show \
  --account-name cosmos-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --name lms_content

# Check throughput settings
az cosmosdb sql database throughput show \
  --account-name cosmos-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --name lms_content
```

**Create Containers:**
```bash
# Create container for courses
az cosmosdb sql container create \
  --account-name cosmos-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --database-name lms_content \
  --name courses \
  --partition-key-path "/courseId" \
  --throughput 400

# Create container for users
az cosmosdb sql container create \
  --account-name cosmos-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --database-name lms_content \
  --name users \
  --partition-key-path "/userId" \
  --throughput 400

# Create container with TTL enabled
az cosmosdb sql container create \
  --account-name cosmos-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --database-name lms_content \
  --name sessions \
  --partition-key-path "/sessionId" \
  --throughput 400 \
  --ttl 86400  # 24 hours
```

**Scale Throughput:**
```bash
# Update RU/s for database (shared across containers)
az cosmosdb sql database throughput update \
  --account-name cosmos-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --name lms_content \
  --throughput 1000

# Or use autoscale
az cosmosdb sql database throughput update \
  --account-name cosmos-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --name lms_content \
  --max-throughput 4000
```

---

## Key Vault & Secrets: 34-37

### 34. module.spoke_dev.azurerm_key_vault.dev
**Key Vault:** `kv-lms-dev-lms-dxdfyl`

**Purpose:** Stores secrets, keys, and certificates for dev environment

**How to Use:**

**Access Key Vault:**
```bash
# Set secret
az keyvault secret set \
  --vault-name kv-lms-dev-lms-dxdfyl \
  --name api-key \
  --value "your-secret-value"

# Get secret
az keyvault secret show \
  --vault-name kv-lms-dev-lms-dxdfyl \
  --name api-key \
  --query value -o tsv

# List all secrets
az keyvault secret list \
  --vault-name kv-lms-dev-lms-dxdfyl \
  -o table

# Delete secret
az keyvault secret delete \
  --vault-name kv-lms-dev-lms-dxdfyl \
  --name api-key
```

**Access Policies:**
```bash
# Grant access to a service principal
az keyvault set-policy \
  --name kv-lms-dev-lms-dxdfyl \
  --spn <service-principal-id> \
  --secret-permissions get list

# Grant access to a user
az keyvault set-policy \
  --name kv-lms-dev-lms-dxdfyl \
  --upn user@domain.com \
  --secret-permissions get list set delete

# Grant access to managed identity
az keyvault set-policy \
  --name kv-lms-dev-lms-dxdfyl \
  --object-id <managed-identity-object-id> \
  --secret-permissions get
```

**Use in Applications:**
```python
# Python example with managed identity
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()
client = SecretClient(vault_url="https://kv-lms-dev-lms-dxdfyl.vault.azure.net/", credential=credential)

# Get secret
db_password = client.get_secret("database-admin-password").value
cosmosdb_key = client.get_secret("cosmosdb-primary-key").value
```

**Monitor Access:**
```bash
# View audit logs
az monitor log-analytics query \
  --workspace log-lms-hub-lms-dxdfyl \
  --analytics-query "AzureDiagnostics | where ResourceType == 'VAULTS' and ResourceId contains 'kv-lms-dev' | take 100"

# Check who accessed secrets
az monitor log-analytics query \
  --workspace log-lms-hub-lms-dxdfyl \
  --analytics-query "AzureDiagnostics | where ResourceType == 'VAULTS' and OperationName == 'SecretGet' and TimeGenerated > ago(24h)"
```

---

### 35. module.spoke_dev.azurerm_key_vault_secret.cosmosdb_connection_string
**Secret Name:** `cosmosdb-connection-string`

**Purpose:** Stores Cosmos DB connection string for dev applications

**How to Use:**

**Retrieve Connection String:**
```bash
# Get connection string from Key Vault
az keyvault secret show \
  --vault-name kv-lms-dev-lms-dxdfyl \
  --name cosmosdb-connection-string \
  --query value -o tsv
```

**Use in Applications:**
```bash
# Set as environment variable
export COSMOS_CONNECTION_STRING=$(az keyvault secret show \
  --vault-name kv-lms-dev-lms-dxdfyl \
  --name cosmosdb-connection-string \
  --query value -o tsv)

# Use in Docker
docker run -e COSMOS_CONNECTION_STRING="$(az keyvault secret show --vault-name kv-lms-dev-lms-dxdfyl --name cosmosdb-connection-string --query value -o tsv)" your-app
```

**Node.js Example:**
```javascript
const { SecretClient } = require("@azure/keyvault-secrets");
const { DefaultAzureCredential } = require("@azure/identity");
const { CosmosClient } = require("@azure/cosmos");

const credential = new DefaultAzureCredential();
const secretClient = new SecretClient("https://kv-lms-dev-lms-dxdfyl.vault.azure.net/", credential);

async function getCosmosClient() {
  const secret = await secretClient.getSecret("cosmosdb-connection-string");
  return new CosmosClient(secret.value);
}
```

---

### 36. module.spoke_dev.azurerm_key_vault_secret.cosmosdb_key
**Secret Name:** `cosmosdb-primary-key`

**Purpose:** Stores Cosmos DB primary master key

**How to Use:**

**Retrieve Key:**
```bash
# Get primary key
az keyvault secret show \
  --vault-name kv-lms-dev-lms-dxdfyl \
  --name cosmosdb-primary-key \
  --query value -o tsv
```

**Rotate Keys:**
```bash
# 1. Regenerate secondary key first
az cosmosdb keys regenerate \
  --name cosmos-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --key-kind secondary

# 2. Update applications to use secondary key
# 3. After verification, regenerate primary key
az cosmosdb keys regenerate \
  --name cosmos-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --key-kind primary

# 4. Update Key Vault with new primary key
NEW_KEY=$(az cosmosdb keys list --name cosmos-lms-dev-lms-dxdfyl --resource-group lms-dev-rg-lms-dxdfyl --query primaryMasterKey -o tsv)
az keyvault secret set \
  --vault-name kv-lms-dev-lms-dxdfyl \
  --name cosmosdb-primary-key \
  --value "$NEW_KEY"
```

---

### 37. module.spoke_dev.azurerm_key_vault_secret.db_password
**Secret Name:** `database-admin-password`

**Purpose:** Stores PostgreSQL admin password for dev environment

**How to Use:**

**Retrieve Password:**
```bash
# Get database password
az keyvault secret show \
  --vault-name kv-lms-dev-lms-dxdfyl \
  --name database-admin-password \
  --query value -o tsv
```

**Connect to PostgreSQL:**
```bash
# Using psql
PGPASSWORD=$(az keyvault secret show --vault-name kv-lms-dev-lms-dxdfyl --name database-admin-password --query value -o tsv) \
psql "host=psql-lms-dev-lms-dxdfyl.postgres.database.azure.com \
     dbname=lms_auth \
     user=psqladmin \
     sslmode=require"

# Using connection string
psql "postgresql://psqladmin:$(az keyvault secret show --vault-name kv-lms-dev-lms-dxdfyl --name database-admin-password --query value -o tsv)@psql-lms-dev-lms-dxdfyl.postgres.database.azure.com:5432/lms_auth?sslmode=require"
```

**Application Connection String:**
```python
# Python (psycopg2)
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
import psycopg2

credential = DefaultAzureCredential()
secret_client = SecretClient("https://kv-lms-dev-lms-dxdfyl.vault.azure.net/", credential)
password = secret_client.get_secret("database-admin-password").value

conn = psycopg2.connect(
    host="psql-lms-dev-lms-dxdfyl.postgres.database.azure.com",
    database="lms_auth",
    user="psqladmin",
    password=password,
    sslmode="require"
)
```

---

## Load Balancer: 38-40

### 38. module.spoke_dev.azurerm_lb.dev
**Load Balancer:** `lb-lms-dev-lms-dxdfyl`
**SKU:** Standard
**Frontend IP:** Private (10.1.2.10)

**Purpose:** Distributes traffic to VM Scale Set instances

**How to Use:**

**View Load Balancer Configuration:**
```bash
# Show load balancer details
az network lb show \
  --name lb-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl

# List frontend IPs
az network lb frontend-ip list \
  --lb-name lb-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  -o table

# List backend pools
az network lb address-pool list \
  --lb-name lb-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  -o table
```

**Check Backend Health:**
```bash
# View backend pool members
az network lb address-pool address list \
  --lb-name lb-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --pool-name backend-pool

# Check health probe status
az network lb probe list \
  --lb-name lb-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  -o table
```

**Monitor Load Balancer:**
```bash
# Check data throughput
az monitor metrics list \
  --resource /subscriptions/a9530d40-75da-44a3-9581-b9faf889608c/resourceGroups/lms-dev-rg-lms-dxdfyl/providers/Microsoft.Network/loadBalancers/lb-lms-dev-lms-dxdfyl \
  --metric "ByteCount" \
  --aggregation Total

# Check SNAT port usage
az monitor metrics list \
  --resource /subscriptions/a9530d40-75da-44a3-9581-b9faf889608c/resourceGroups/lms-dev-rg-lms-dxdfyl/providers/Microsoft.Network/loadBalancers/lb-lms-dev-lms-dxdfyl \
  --metric "UsedSNATPorts"
```

**Test Connectivity:**
```bash
# From hub subnet or another VM in dev VNet
curl http://10.1.2.10

# Check which backend instance responded
curl -v http://10.1.2.10 2>&1 | grep -i server
```

---

### 39. module.spoke_dev.azurerm_lb_backend_address_pool.dev
**Backend Pool:** `backend-pool`

**Purpose:** Pool of VMSS instances receiving traffic from load balancer

**How to Use:**

**View Pool Members:**
```bash
# List backend pool addresses
az network lb address-pool show \
  --lb-name lb-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --name backend-pool

# Check VMSS attachment
az vmss show \
  --name lms-dev-vmss-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --query "virtualMachineProfile.networkProfile.networkInterfaceConfigurations[0].ipConfigurations[0].loadBalancerBackendAddressPools"
```

**Health Status:**
```bash
# All VMSS instances are automatically added to backend pool
# Check instance health
az vmss list-instances \
  --name lms-dev-vmss-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --query "[].{Name:name, ProvisioningState:provisioningState, HealthState:instanceView.statuses[?code=='HealthState/healthy']}" \
  -o table
```

---

### 40. module.spoke_dev.azurerm_lb_probe.dev
**Health Probe:** `http-probe` on port 80

**Purpose:** Monitors backend instance health and removes unhealthy instances from pool

**How to Use:**

**View Probe Configuration:**
```bash
# Show probe details
az network lb probe show \
  --lb-name lb-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --name http-probe

# Configuration:
# - Protocol: HTTP
# - Port: 80
# - Path: /
# - Interval: 15 seconds
# - Unhealthy threshold: 2 consecutive failures
```

**Test Health Probe:**
```bash
# Ensure your application responds on port 80
curl http://10.1.2.10/

# On VMSS instance, test locally
curl http://localhost/

# Install simple web server for testing
sudo apt update && sudo apt install nginx -y
sudo systemctl start nginx
```

**Troubleshooting Failed Probes:**
```bash
# 1. Check if service is running on VMSS instances
az vmss run-command invoke \
  --command-id RunShellScript \
  --name lms-dev-vmss-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --instance-id 0 \
  --scripts "systemctl status nginx"

# 2. Check firewall rules on VM
az vmss run-command invoke \
  --command-id RunShellScript \
  --name lms-dev-vmss-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --instance-id 0 \
  --scripts "sudo iptables -L -n"

# 3. View NSG rules affecting probe
az network nsg show \
  --name nsg-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --query "securityRules[?destinationPortRange=='80']"
```

**Custom Health Endpoint:**
```bash
# Update probe to use custom health check path
az network lb probe update \
  --lb-name lb-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --name http-probe \
  --path /health

# Your application should respond 200 OK at /health endpoint
```

---

## Quick Reference Commands

```bash
# Development environment health check
az vmss list-instances --name lms-dev-vmss-lms-dxdfyl --resource-group lms-dev-rg-lms-dxdfyl -o table
az network lb show --name lb-lms-dev-lms-dxdfyl --resource-group lms-dev-rg-lms-dxdfyl --query provisioningState
az postgres flexible-server show --name psql-lms-dev-lms-dxdfyl --resource-group lms-dev-rg-lms-dxdfyl --query state -o tsv
az cosmosdb show --name cosmos-lms-dev-lms-dxdfyl --resource-group lms-dev-rg-lms-dxdfyl --query provisioningState

# Get all connection strings
az keyvault secret show --vault-name kv-lms-dev-lms-dxdfyl --name database-admin-password --query value -o tsv
az keyvault secret show --vault-name kv-lms-dev-lms-dxdfyl --name cosmosdb-connection-string --query value -o tsv

# Access a dev VM via Bastion
az network bastion ssh --name bastion-lms-hub --resource-group rg-lms-hub-lms-dxdfyl --target-resource-id $(az vmss list-instances --name lms-dev-vmss-lms-dxdfyl --resource-group lms-dev-rg-lms-dxdfyl --query "[0].id" -o tsv) --auth-type password --username azureuser
```

---

**Previous:** [03-hub-security-monitoring-guide.md](./03-hub-security-monitoring-guide.md)
**Next:** [05-development-data-services-guide.md](./05-development-data-services-guide.md) - PostgreSQL, Storage, and Data Management
