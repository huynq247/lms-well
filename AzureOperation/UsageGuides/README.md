# Azure Infrastructure Usage Guides

This directory contains comprehensive usage guides for all 100 deployed Azure resources in your LMS infrastructure.

## 📁 Guide Organization

The guides are organized into 10 files, each covering 10 resources with detailed usage instructions, examples, and best practices:

### [01-core-infrastructure-guide.md](./01-core-infrastructure-guide.md)
**Resources 1-10: Core Infrastructure & Container Registry**
- Random password/string generators
- Key Vault secrets
- Azure Container Registry (ACR)
- Bastion Host
- Azure Firewall & Policy
- Local Network Gateway

### [02-hub-networking-guide.md](./02-hub-networking-guide.md)
**Resources 11-20: Hub Network Infrastructure**
- Local Network Gateway
- VNet diagnostic settings
- VPN Gateway diagnostics
- Network Security Group (NSG)
- Public IPs (Bastion, Firewall, VPN)
- Hub Resource Group
- Route tables
- Hub subnets (Bastion, Gateway, Hub)

### [03-hub-security-monitoring-guide.md](./03-hub-security-monitoring-guide.md)
**Resources 21-30: Hub Security & Monitoring**
- Azure Firewall subnet
- Gateway subnet
- Hub subnet associations
- Virtual Network (Hub)
- VPN Gateway
- Virtual Network peerings (Hub ↔ Dev, Hub ↔ Prod)
- VPN connection to on-premises
- Log Analytics workspace (partial)

### [04-development-compute-guide.md](./04-development-compute-guide.md)
**Resources 31-40: Development Compute & Networking**
- Azure client config
- Cosmos DB account & database
- Key Vault & secrets (4 secrets)
- Load Balancer components
- VM Scale Set (VMSS)

### [05-development-data-services-guide.md](./05-development-data-services-guide.md)
**Resources 41-50: Development Data Services & Storage**
- Load balancer rules
- VMSS configuration
- VNet diagnostic settings
- NSG and PostgreSQL
- Resource Group
- Route tables
- Storage account & network rules

### [06-development-networking-security-guide.md](./06-development-networking-security-guide.md)
**Resources 51-60: Development Networking & Security**
- Storage containers (backups, logs, uploads)
- Key Vault secrets (storage, Cosmos DB)
- Subnets (app, data)
- Subnet associations (NSG, routes)
- Virtual Network (Dev)

### [07-production-kubernetes-guide.md](./07-production-kubernetes-guide.md)
**Resources 61-70: Production Kubernetes (AKS)**
- Virtual Network (Prod)
- VNet peering (Prod ↔ Hub)
- Azure client config
- AKS cluster & node pools
- Cosmos DB account & database
- Key Vault & secrets

### [08-production-data-services-guide.md](./08-production-data-services-guide.md)
**Resources 71-80: Production Data Services & Storage**
- Key Vault secrets (database, storage)
- VNet diagnostic settings
- NSG
- PostgreSQL flexible server & database
- Resource Group
- Route tables
- Storage account & network rules

### [09-production-networking-storage-guide.md](./09-production-networking-storage-guide.md)
**Resources 81-90: Production Networking & Storage**
- Storage containers (backups, logs, uploads)
- Subnets (AKS, data)
- Subnet associations (NSG, routes)
- Log Analytics workspace

### [10-monitoring-operations-guide.md](./10-monitoring-operations-guide.md)
**Resources 91-100: Monitoring & Operations**
- Log Analytics advanced monitoring
- Alerting strategies
- Workbooks and dashboards
- Secret management & rotation
- Disaster recovery procedures
- Comprehensive health checks
- Cost optimization
- Emergency procedures

## 🚀 Quick Start

### Access a Specific Guide
```bash
cd /home/huynguyen/lms_mcsrv_runwell/AzureOperation/UsageGuides/

# View guide in terminal
cat 07-production-kubernetes-guide.md | less

# Open in editor
code 07-production-kubernetes-guide.md
```

### Find Specific Resource Usage
```bash
# Search across all guides
grep -r "aks-lms-prod" *.md
grep -r "PostgreSQL" *.md
grep -r "Key Vault" *.md
```

### Common Tasks by Guide

**Deploy to AKS:** → Guide 07
**Manage databases:** → Guides 05, 08
**Configure networking:** → Guides 02, 06, 09
**Monitor infrastructure:** → Guide 10
**Manage storage:** → Guides 05, 06, 08, 09
**Security & secrets:** → Guides 03, 04, 08

## 📊 Resource Summary

### Total Resources: 100

**By Environment:**
- Hub Infrastructure: 26 resources
- Container Registry: 3 resources
- Development: 34 resources
- Production: 37 resources

**By Category:**
- Networking: 32 resources (VNets, subnets, NSGs, routes, peerings)
- Compute: 8 resources (VMSS, AKS, node pools)
- Data Services: 8 resources (PostgreSQL, Cosmos DB)
- Storage: 12 resources (3 accounts, 9 containers)
- Security: 15 resources (Key Vaults, 12 secrets, NSGs)
- Monitoring: 4 resources (Log Analytics, diagnostics)
- Connectivity: 8 resources (VPN, Firewall, Bastion)
- Other: 13 resources (resource groups, policies, etc.)

## 🛠️ Essential Commands

### Infrastructure Health Check
```bash
# Hub health
az network vnet-gateway show --name vgw-lms-hub-lms-dxdfyl --resource-group rg-lms-hub-lms-dxdfyl --query provisioningState
az network firewall show --name azfw-lms-hub --resource-group rg-lms-hub-lms-dxdfyl --query provisioningState

# Development health
az vmss show --name lms-dev-vmss-lms-dxdfyl --resource-group lms-dev-rg-lms-dxdfyl --query provisioningState
az postgres flexible-server show --name psql-lms-dev-lms-dxdfyl --resource-group lms-dev-rg-lms-dxdfyl --query state

# Production health
az aks show --name aks-lms-prod-lms-dxdfyl --resource-group lms-prod-rg-lms-dxdfyl --query powerState
kubectl get nodes
az postgres flexible-server show --name psql-lms-prod-lms-dxdfyl --resource-group lms-prod-rg-lms-dxdfyl --query state
```

### Access Resources
```bash
# Connect to AKS
az aks get-credentials --name aks-lms-prod-lms-dxdfyl --resource-group lms-prod-rg-lms-dxdfyl --overwrite-existing

# Connect to PostgreSQL (dev)
PGPASSWORD=$(az keyvault secret show --vault-name kv-lms-dev-lms-dxdfyl --name database-admin-password --query value -o tsv) \
psql -h psql-lms-dev-lms-dxdfyl.postgres.database.azure.com -U psqladmin -d lms_auth

# Connect to PostgreSQL (prod)
PGPASSWORD=$(az keyvault secret show --vault-name kv-lms-prod-lms-dxdfyl --name database-admin-password --query value -o tsv) \
psql -h psql-lms-prod-lms-dxdfyl.postgres.database.azure.com -U psqladmin -d lms_auth

# Access VM via Bastion
az network bastion ssh \
  --name bastion-lms-hub \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --target-resource-id <vm-resource-id> \
  --auth-type password \
  --username azureuser
```

### Monitoring & Logs
```bash
# Query Log Analytics
az monitor log-analytics query \
  --workspace log-lms-hub-lms-dxdfyl \
  --analytics-query "AzureDiagnostics | take 100"

# AKS logs
kubectl logs -l app=<app-name> --tail=100

# Firewall logs
az monitor log-analytics query \
  --workspace log-lms-hub-lms-dxdfyl \
  --analytics-query "AzureDiagnostics | where ResourceType == 'AZUREFIREWALLS' | take 100"
```

### Backup & Restore
```bash
# Backup PostgreSQL (production)
PGPASSWORD=$(az keyvault secret show --vault-name kv-lms-prod-lms-dxdfyl --name database-admin-password --query value -o tsv) \
pg_dump -h psql-lms-prod-lms-dxdfyl.postgres.database.azure.com -U psqladmin -d lms_auth -F c -f backup.dump

# Upload to storage
az storage blob upload \
  --account-name stlmsprodlmsdxdfyl \
  --container-name backups \
  --name "postgres/backup-$(date +%Y%m%d_%H%M%S).dump" \
  --file backup.dump

# Backup Kubernetes
kubectl get all --all-namespaces -o yaml > k8s-backup-$(date +%Y%m%d).yaml
```

## 📖 Guide Features

Each guide includes:

✅ **Resource Overview** - Purpose and configuration details
✅ **How to Use** - Step-by-step instructions with CLI commands
✅ **Best Practices** - Recommended configurations and security
✅ **Troubleshooting** - Common issues and solutions
✅ **Code Examples** - Python, Node.js, Bash scripts
✅ **Monitoring** - Metrics, logs, and alerts
✅ **Quick Reference** - Essential commands at the end

## 🔗 Related Documentation

- **Deployment Documentation:** `/home/huynguyen/lms_mcsrv_runwell/AzureOperation/Resources/deployment-summary.md`
- **Resource Specifications:** `/home/huynguyen/lms_mcsrv_runwell/AzureOperation/Resources/resource-specifications.yaml`
- **Terraform Outputs:** `/home/huynguyen/lms_mcsrv_runwell/AzureOperation/Resources/terraform-outputs.json`
- **Resource List:** `/home/huynguyen/lms_mcsrv_runwell/AzureOperation/Resources/all-resources.txt`

## 📞 Support

For questions or issues:

1. Check the relevant usage guide
2. Search Log Analytics for errors
3. Run health check scripts (Guide 10)
4. Review Terraform documentation in `/home/huynguyen/lms_mcsrv_runwell/Azure_withCode/terraform/`

## 🔄 Updates

Last Updated: February 2, 2025
Infrastructure Version: 1.0
Terraform Version: 1.6.5
AKS Version: 1.32.9
PostgreSQL Version: 16

---

**Navigation:**
- [← Back to AzureOperation](../)
- [View All Resources List](../Resources/all-resources.txt)
- [View Deployment Summary](../Resources/deployment-summary.md)
