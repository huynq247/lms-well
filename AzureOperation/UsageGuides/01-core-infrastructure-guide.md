# Core Infrastructure Usage Guide (Resources 1-10)

## Resource Group: 1-3

### 1. random_password.db_password
**Purpose:** Generates secure random passwords for database authentication

**How to Use:**
```bash
# View the generated password (stored in Terraform state)
cd /home/huynguyen/lms_mcsrv_runwell/Azure_withCode/terraform
terraform output -raw database_admin_username

# The password is automatically used by PostgreSQL servers
# Never commit this to source control
```

**Best Practices:**
- Password is automatically rotated when Terraform recreates the resource
- Stored securely in Terraform state (encrypted backend recommended)
- Used by both dev and prod PostgreSQL servers

---

### 2. random_string.suffix
**Purpose:** Generates unique suffix "dxdfyl" for globally unique resource names

**How to Use:**
```bash
# View the suffix
terraform output

# This suffix is appended to resource names like:
# - acrlmslmsdxdfyl (Container Registry)
# - kv-lms-hub-lms-dxdfyl (Key Vault)
```

**Why It's Important:**
- Ensures globally unique names for Azure resources
- Consistent across all deployments
- Makes resource identification easier

---

### 3. azurerm_key_vault_secret.db_password
**Purpose:** Stores the database admin password in Key Vault

**How to Use:**
```bash
# Retrieve the password from Key Vault
az keyvault secret show \
  --vault-name kv-lms-hub-lms-dxdfyl \
  --name database-admin-password \
  --query value -o tsv

# Use in connection strings
psql "host=psql-lms-prod-lms-dxdfyl.postgres.database.azure.com \
      dbname=lms_auth user=psqladmin \
      password=$(az keyvault secret show --vault-name kv-lms-hub-lms-dxdfyl --name database-admin-password --query value -o tsv)"
```

**Access Control:**
- Terraform has Set/Get/Delete permissions
- Applications use managed identity for Get permission
- Audit logs track all access

---

## Container Registry: 4-6

### 4. module.container_registry.azurerm_container_registry.acr
**Purpose:** Premium container registry for storing Docker images

**How to Use:**
```bash
# Login to ACR
az acr login --name acrlmslmsdxdfyl

# Tag and push images
docker tag your-app:latest acrlmslmsdxdfyl.azurecr.io/your-app:latest
docker push acrlmslmsdxdfyl.azurecr.io/your-app:latest

# List repositories
az acr repository list --name acrlmslmsdxdfyl -o table

# List tags for a repository
az acr repository show-tags --name acrlmslmsdxdfyl --repository your-app -o table

# Pull image
docker pull acrlmslmsdxdfyl.azurecr.io/your-app:latest
```

**Premium Features:**
- Geo-replication support
- Webhook notifications
- Content trust
- Private link support

**Security:**
```bash
# Enable admin user (if needed for CI/CD)
az acr update --name acrlmslmsdxdfyl --admin-enabled true

# Get admin credentials
az acr credential show --name acrlmslmsdxdfyl

# Use service principal for production (recommended)
az ad sp create-for-rbac \
  --name acr-sp \
  --role acrpull \
  --scopes /subscriptions/a9530d40-75da-44a3-9581-b9faf889608c/resourceGroups/rg-lms-acr-lms-dxdfyl/providers/Microsoft.ContainerRegistry/registries/acrlmslmsdxdfyl
```

---

### 5. module.container_registry.azurerm_monitor_diagnostic_setting.acr
**Purpose:** Monitors ACR activities and sends logs to Log Analytics

**How to Use:**
```bash
# View ACR logs in Log Analytics
az monitor log-analytics query \
  --workspace log-lms-hub-lms-dxdfyl \
  --analytics-query "ContainerRegistryRepositoryEvents | take 100"

# Check who pushed/pulled images
az monitor log-analytics query \
  --workspace log-lms-hub-lms-dxdfyl \
  --analytics-query "ContainerRegistryLoginEvents | where TimeGenerated > ago(24h)"
```

**Monitored Events:**
- Push/Pull operations
- Repository deletions
- Authentication attempts
- Administrative actions

---

### 6. module.container_registry.azurerm_resource_group.acr
**Resource Group:** `rg-lms-acr-lms-dxdfyl`

**How to Use:**
```bash
# List all resources in ACR resource group
az resource list --resource-group rg-lms-acr-lms-dxdfyl -o table

# View resource group details
az group show --name rg-lms-acr-lms-dxdfyl

# Check tags
az group show --name rg-lms-acr-lms-dxdfyl --query tags

# Update tags (if needed)
az group update --name rg-lms-acr-lms-dxdfyl \
  --tags CostCenter=IT Project=lms Environment=prod
```

**Management:**
- Contains only ACR and diagnostic settings
- Location: Southeast Asia
- Managed by: Terraform

---

## Hub Infrastructure Setup: 7-10

### 7. module.hub.data.azurerm_client_config.current
**Purpose:** Data source that retrieves current Azure subscription and tenant information

**Information Provided:**
- Subscription ID: `a9530d40-75da-44a3-9581-b9faf889608c`
- Tenant ID: Used for Key Vault access policies
- Client ID: Terraform service principal
- Object ID: Used for IAM assignments

**How to Use:**
```bash
# View current Azure context
az account show

# List all subscriptions
az account list -o table

# Switch subscription (if needed)
az account set --subscription a9530d40-75da-44a3-9581-b9faf889608c
```

---

### 8. module.hub.azurerm_bastion_host.hub[0]
**Purpose:** Secure RDP/SSH access to VMs without exposing them to the internet

**How to Use:**

**Via Azure Portal:**
1. Navigate to Azure Portal > Virtual Machines
2. Select your VM (in dev environment)
3. Click "Connect" > "Bastion"
4. Enter credentials
5. Connect securely

**Via Azure CLI:**
```bash
# Connect to a VM using Bastion
az network bastion ssh \
  --name bastion-lms-hub \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --target-resource-id /subscriptions/a9530d40-75da-44a3-9581-b9faf889608c/resourceGroups/lms-dev-rg-lms-dxdfyl/providers/Microsoft.Compute/virtualMachineScaleSets/lms-dev-vmss-lms-dxdfyl/virtualMachines/0 \
  --auth-type password \
  --username azureuser

# For RDP (Windows VMs)
az network bastion rdp \
  --name bastion-lms-hub \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --target-resource-id <vm-id>
```

**Benefits:**
- No public IPs needed on VMs
- No VPN required for management access
- All traffic encrypted
- Session recording available
- FQDN: `bst-bb4333be-8e0d-41f0-b967-a149eaf54f28.bastion.azure.com`

**Cost:** ~$140/month for Standard SKU

---

### 9. module.hub.azurerm_firewall.hub[0]
**Purpose:** Centralized network security and filtering for all spoke networks

**Public IP:** `20.6.121.168`

**How to Use:**

**View Firewall Logs:**
```bash
# Check firewall logs
az monitor log-analytics query \
  --workspace log-lms-hub-lms-dxdfyl \
  --analytics-query "AzureDiagnostics | where Category == 'AzureFirewallApplicationRule' | take 100"

# View blocked traffic
az monitor log-analytics query \
  --workspace log-lms-hub-lms-dxdfyl \
  --analytics-query "AzureDiagnostics | where Category == 'AzureFirewallNetworkRule' and msg_s contains 'Deny'"
```

**Add Firewall Rules:**
```bash
# Add application rule (via Azure Portal or Terraform)
# Navigate to: Azure Firewall > Firewall Policy > Application Rules

# Example: Allow HTTPS to specific domain
# - Source: 10.1.0.0/16, 10.2.0.0/16
# - Target FQDN: *.microsoft.com
# - Protocol: HTTPS:443
# - Action: Allow
```

**Current Configuration:**
- Threat Intelligence: Alert mode
- DNS Proxy: Enabled
- Integrated with Log Analytics
- Policy: `afwp-lms-hub`

**Important:** All outbound traffic from spokes routes through this firewall

---

### 10. module.hub.azurerm_firewall_policy.hub[0]
**Policy Name:** `afwp-lms-hub`

**Purpose:** Defines rules and policies for Azure Firewall

**How to Manage:**

**View Policy:**
```bash
# Show firewall policy details
az network firewall policy show \
  --name afwp-lms-hub \
  --resource-group rg-lms-hub-lms-dxdfyl

# List rule collection groups
az network firewall policy rule-collection-group list \
  --policy-name afwp-lms-hub \
  --resource-group rg-lms-hub-lms-dxdfyl -o table
```

**Rule Structure:**
```
Firewall Policy: afwp-lms-hub
├── Application Rules (HTTP/HTTPS filtering)
│   ├── Allow Microsoft services
│   ├── Allow Azure services
│   └── Allow specific FQDNs
└── Network Rules (Port-based filtering)
    ├── Allow DNS
    ├── Allow NTP
    └── Allow inter-spoke communication
```

**Update Rules (via Terraform):**
```hcl
# Edit: modules/hub/main.tf
# Add new application rule collection
resource "azurerm_firewall_policy_rule_collection_group" "application_rules" {
  # ... existing rules ...
  
  application_rule_collection {
    name     = "allow-custom-apps"
    priority = 200
    action   = "Allow"
    
    rule {
      name = "allow-github"
      source_addresses = ["10.1.0.0/16", "10.2.0.0/16"]
      destination_fqdns = ["*.github.com", "github.com"]
      protocols {
        type = "Https"
        port = 443
      }
    }
  }
}
```

**Best Practices:**
- Use FQDN filtering instead of IP addresses when possible
- Order rules by priority (lower number = higher priority)
- Use rule collection groups to organize related rules
- Enable diagnostic logging for compliance
- Test new rules in dev environment first

---

## Quick Reference Commands

```bash
# Get ACR login server
terraform output acr_login_server

# Get Bastion FQDN
terraform output bastion_fqdn

# Get Firewall public IP
terraform output azure_firewall_public_ip

# View all hub resources
az resource list --resource-group rg-lms-hub-lms-dxdfyl -o table
```

---

**Next Guide:** [02-hub-networking-guide.md](./02-hub-networking-guide.md) - VPN Gateway, Networking, and Log Analytics
