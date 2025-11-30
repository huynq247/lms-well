# Hub Network Infrastructure Usage Guide (Resources 11-20)

## VPN Gateway & Connectivity: 11-13

### 11. module.hub.azurerm_local_network_gateway.onprem[0]
**Purpose:** Represents your on-premises network endpoint for VPN connection

**Configuration:**
- Gateway IP: `203.0.113.10`
- On-premises Network: `192.168.0.0/16`

**How to Use:**

**Update On-Premises Configuration:**
```bash
# If your on-premises gateway IP changes
az network local-gateway update \
  --name lng-lms-hub-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --gateway-ip-address <new-public-ip>

# Update address space
az network local-gateway update \
  --name lng-lms-hub-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --local-address-prefixes 192.168.0.0/16 172.16.0.0/12
```

**View Configuration:**
```bash
# Show local network gateway details
az network local-gateway show \
  --name lng-lms-hub-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl
```

**Troubleshooting:**
- Ensure on-premises firewall allows UDP 500, 4500, ESP (IP Protocol 50)
- Verify the gateway public IP is correct
- Check that address spaces don't overlap with Azure VNets

---

### 12. module.hub.azurerm_monitor_diagnostic_setting.hub_vnet
**Purpose:** Monitors hub virtual network activities and sends logs to Log Analytics

**How to Use:**

**Query VNet Logs:**
```bash
# View all VNet diagnostic logs
az monitor log-analytics query \
  --workspace log-lms-hub-lms-dxdfyl \
  --analytics-query "AzureDiagnostics | where ResourceType == 'VIRTUALNETWORKS' | take 100"

# Check for failed connections
az monitor log-analytics query \
  --workspace log-lms-hub-lms-dxdfyl \
  --analytics-query "AzureDiagnostics | where Category == 'NetworkSecurityGroupEvent' and msg_s contains 'blocked'"
```

**Monitored Events:**
- NSG rule matches
- Network flow changes
- Peering status changes
- Route table updates

**Set Up Alerts:**
```bash
# Create alert for VNet configuration changes
az monitor metrics alert create \
  --name "vnet-config-change" \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --scopes /subscriptions/a9530d40-75da-44a3-9581-b9faf889608c/resourceGroups/rg-lms-hub-lms-dxdfyl/providers/Microsoft.Network/virtualNetworks/vnet-lms-hub-lms-dxdfyl \
  --condition "count > 0" \
  --description "Alert when VNet configuration changes"
```

---

### 13. module.hub.azurerm_monitor_diagnostic_setting.vpn_gateway[0]
**Purpose:** Monitors VPN Gateway activities, connection status, and performance

**How to Use:**

**Check VPN Connection Status:**
```bash
# View VPN gateway logs
az monitor log-analytics query \
  --workspace log-lms-hub-lms-dxdfyl \
  --analytics-query "AzureDiagnostics | where ResourceType == 'VIRTUALNETWORKGATEWAYS' | take 100"

# Check tunnel status
az monitor log-analytics query \
  --workspace log-lms-hub-lms-dxdfyl \
  --analytics-query "AzureDiagnostics | where Category == 'TunnelDiagnosticLog' | order by TimeGenerated desc"

# Monitor bandwidth usage
az monitor log-analytics query \
  --workspace log-lms-hub-lms-dxdfyl \
  --analytics-query "AzureDiagnostics | where Category == 'GatewayDiagnosticLog' and operationName_s == 'VpnGatewayPacketDropTSMismatch'"
```

**Performance Monitoring:**
```bash
# Check gateway CPU and bandwidth
az network vnet-gateway show \
  --name vgw-lms-hub-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl

# View connection metrics
az monitor metrics list \
  --resource /subscriptions/a9530d40-75da-44a3-9581-b9faf889608c/resourceGroups/rg-lms-hub-lms-dxdfyl/providers/Microsoft.Network/virtualNetworkGateways/vgw-lms-hub-lms-dxdfyl \
  --metric "AverageBandwidth"
```

---

## Network Security: 14-17

### 14. module.hub.azurerm_network_security_group.hub
**NSG Name:** `nsg-lms-hub-lms-dxdfyl`

**Purpose:** Controls inbound and outbound traffic for hub subnets

**How to Use:**

**View Current Rules:**
```bash
# List all NSG rules
az network nsg show \
  --name nsg-lms-hub-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl

# List security rules in table format
az network nsg rule list \
  --nsg-name nsg-lms-hub-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl \
  -o table
```

**Add Custom Rules:**
```bash
# Allow SSH from specific IP range
az network nsg rule create \
  --name Allow-SSH-From-Office \
  --nsg-name nsg-lms-hub-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --priority 1000 \
  --source-address-prefixes 203.0.113.0/24 \
  --destination-port-ranges 22 \
  --protocol Tcp \
  --access Allow \
  --direction Inbound

# Block outbound traffic to specific IP
az network nsg rule create \
  --name Deny-Outbound-To-BadIP \
  --nsg-name nsg-lms-hub-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --priority 4000 \
  --destination-address-prefixes 198.51.100.0/24 \
  --access Deny \
  --direction Outbound
```

**View Traffic Analytics:**
```bash
# Enable NSG flow logs (if not enabled)
az network watcher flow-log create \
  --name nsg-hub-flow-log \
  --nsg nsg-lms-hub-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --storage-account <storage-account-id> \
  --enabled true
```

**Best Practices:**
- Use service tags (e.g., `AzureLoadBalancer`, `VirtualNetwork`)
- Keep priorities organized (1000-2000: Allow rules, 3000-4000: Deny rules)
- Document rules with descriptive names
- Review rules quarterly

---

### 15. module.hub.azurerm_public_ip.bastion[0]
**Public IP:** Bastion Host access endpoint

**How to Use:**

**View Public IP:**
```bash
# Get Bastion public IP details
az network public-ip show \
  --name pip-bastion-lms-hub-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl

# Get IP address only
az network public-ip show \
  --name pip-bastion-lms-hub-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --query ipAddress -o tsv
```

**Configuration:**
- SKU: Standard (Static allocation)
- Allocation: Static (IP never changes)
- Zone: Zone-redundant
- Used exclusively by Azure Bastion

**DNS Configuration:**
```bash
# View DNS settings
az network public-ip show \
  --name pip-bastion-lms-hub-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --query dnsSettings

# Update DNS label (creates FQDN)
az network public-ip update \
  --name pip-bastion-lms-hub-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --dns-name bastion-lms
```

**Important:** This IP is managed by Azure Bastion. Don't manually assign or remove it.

---

### 16. module.hub.azurerm_public_ip.firewall[0]
**Public IP:** `20.6.121.168`

**Purpose:** Static public IP for Azure Firewall

**How to Use:**

**View IP Details:**
```bash
# Show public IP configuration
az network public-ip show \
  --name pip-azfw-lms-hub-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl

# Monitor IP usage
az monitor metrics list \
  --resource /subscriptions/a9530d40-75da-44a3-9581-b9faf889608c/resourceGroups/rg-lms-hub-lms-dxdfyl/providers/Microsoft.Network/publicIPAddresses/pip-azfw-lms-hub-lms-dxdfyl \
  --metric "ByteCount"
```

**NAT Configuration:**
All outbound traffic from spoke networks uses this IP as source:
```
Dev VMs (10.1.x.x) → Firewall → 20.6.121.168 → Internet
Prod AKS (10.2.x.x) → Firewall → 20.6.121.168 → Internet
```

**Whitelist This IP:**
```bash
# Use this IP for:
# - External API whitelisting
# - Partner network ACLs
# - Cloud service access control

# Example: Whitelist in GitHub Enterprise
# Settings > Security > IP Allow List > Add: 20.6.121.168/32
```

**DDoS Protection:**
- Basic DDoS protection enabled by default
- Consider Azure DDoS Protection Standard for production

---

### 17. module.hub.azurerm_public_ip.vpn_gateway[0]
**Public IP:** VPN Gateway endpoint

**How to Use:**

**Get VPN Gateway Public IP:**
```bash
# Show VPN gateway public IP
az network public-ip show \
  --name pip-vgw-lms-hub-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --query ipAddress -o tsv

# Example output: 20.247.45.123
```

**Configure On-Premises VPN Device:**
```bash
# Use this IP as the remote gateway endpoint
# Example for pfSense:
# 1. Navigate to VPN > IPsec > Tunnels
# 2. Remote Gateway: <vpn-gateway-public-ip>
# 3. Pre-Shared Key: (from Key Vault secret: vpn-shared-key)
# 4. Phase 1: IKEv2, AES256, SHA256, DH Group 2
# 5. Phase 2: AES256, SHA256, PFS Group 2
```

**Monitor Connection:**
```bash
# Check VPN connection status
az network vpn-connection show \
  --name vpn-lms-hub-to-onprem-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --query connectionStatus

# View connection statistics
az network vpn-connection show \
  --name vpn-lms-hub-to-onprem-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --query "{Status:connectionStatus, IngressBytes:ingressBytesTransferred, EgressBytes:egressBytesTransferred}"
```

**Troubleshooting VPN Issues:**
```bash
# 1. Verify gateway is running
az network vnet-gateway show \
  --name vgw-lms-hub-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --query provisioningState

# 2. Check shared key matches
az network vpn-connection shared-key show \
  --connection-name vpn-lms-hub-to-onprem-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl

# 3. Reset connection
az network vpn-connection reset \
  --name vpn-lms-hub-to-onprem-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl
```

---

## Core Networking: 18-20

### 18. module.hub.azurerm_resource_group.hub
**Resource Group:** `rg-lms-hub-lms-dxdfyl`

**Purpose:** Contains all hub networking and security resources

**How to Use:**

**View All Hub Resources:**
```bash
# List all resources
az resource list \
  --resource-group rg-lms-hub-lms-dxdfyl \
  -o table

# Count resources by type
az resource list \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --query "[].type" -o tsv | sort | uniq -c

# View resource group details
az group show --name rg-lms-hub-lms-dxdfyl
```

**Cost Management:**
```bash
# View costs for this resource group
az consumption usage list \
  --start-date 2025-02-01 \
  --end-date 2025-02-28 \
  --query "[?contains(instanceName, 'rg-lms-hub')]"

# Export cost data
az consumption usage list \
  --start-date 2025-02-01 \
  --end-date 2025-02-28 \
  --output json > hub-costs.json
```

**Resource Inventory:**
- VPN Gateway (VpnGw1 SKU) → ~$150/month
- Azure Firewall (Standard) → ~$1,250/month
- Bastion (Standard) → ~$140/month
- Public IPs (3x Standard) → ~$11/month
- VNet Peerings → Data transfer costs
- Log Analytics → Ingestion + Retention costs

**Tags:**
```bash
# Add cost center tag
az group update \
  --name rg-lms-hub-lms-dxdfyl \
  --tags CostCenter=IT-Security Environment=hub Project=lms-infrastructure
```

---

### 19. module.hub.azurerm_route_table.hub
**Route Table:** `rt-lms-hub-lms-dxdfyl`

**Purpose:** Forces all traffic through Azure Firewall for inspection

**How to Use:**

**View Routes:**
```bash
# List all routes
az network route-table route list \
  --route-table-name rt-lms-hub-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl \
  -o table

# Show route table details
az network route-table show \
  --name rt-lms-hub-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl
```

**Current Routes:**
```
Name               Address Prefix    Next Hop Type    Next Hop IP Address
-----------------  ----------------  ---------------  --------------------
to-firewall        0.0.0.0/0         VirtualAppliance 10.0.1.4
to-dev-spoke       10.1.0.0/16       VirtualAppliance 10.0.1.4
to-prod-spoke      10.2.0.0/16       VirtualAppliance 10.0.1.4
```

**Add Custom Route:**
```bash
# Route specific traffic to firewall
az network route-table route create \
  --route-table-name rt-lms-hub-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --name to-partner-network \
  --address-prefix 172.16.0.0/12 \
  --next-hop-type VirtualAppliance \
  --next-hop-ip-address 10.0.1.4

# Route to on-premises network
az network route-table route create \
  --route-table-name rt-lms-hub-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --name to-onprem \
  --address-prefix 192.168.0.0/16 \
  --next-hop-type VirtualNetworkGateway
```

**Important:** Changes to routes take effect immediately and may impact connectivity.

---

### 20. module.hub.azurerm_subnet.AzureBastionSubnet[0]
**Subnet:** `AzureBastionSubnet`
**Address Range:** `10.0.2.0/26` (64 IPs, 59 usable)

**Purpose:** Dedicated subnet for Azure Bastion (required naming convention)

**How to Use:**

**View Subnet Configuration:**
```bash
# Show subnet details
az network vnet subnet show \
  --vnet-name vnet-lms-hub-lms-dxdfyl \
  --name AzureBastionSubnet \
  --resource-group rg-lms-hub-lms-dxdfyl

# Check IP usage
az network vnet subnet show \
  --vnet-name vnet-lms-hub-lms-dxdfyl \
  --name AzureBastionSubnet \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --query "ipConfigurations"
```

**Requirements:**
- Name MUST be "AzureBastionSubnet"
- Minimum size: /26 (64 IPs)
- Cannot have NSG attached (managed by Bastion service)
- Cannot have route table attached
- Cannot be used for any other purpose

**Scaling Bastion:**
```bash
# Upgrade to larger SKU for more concurrent sessions
az network bastion update \
  --name bastion-lms-hub \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --scale-units 5  # 2-50 scale units, each supports 8 concurrent connections
```

**Troubleshooting:**
```bash
# Check Bastion connectivity
nslookup bst-bb4333be-8e0d-41f0-b967-a149eaf54f28.bastion.azure.com

# Verify subnet has enough free IPs
az network vnet subnet show \
  --vnet-name vnet-lms-hub-lms-dxdfyl \
  --name AzureBastionSubnet \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --query "addressPrefix"
```

---

## Quick Reference Commands

```bash
# Check VPN connection status
az network vpn-connection show \
  --name vpn-lms-hub-to-onprem-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --query connectionStatus -o tsv

# Get all public IPs
az network public-ip list \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --query "[].{Name:name, IP:ipAddress}" -o table

# View hub VNet peerings
az network vnet peering list \
  --vnet-name vnet-lms-hub-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl \
  -o table

# Check firewall traffic logs (last hour)
az monitor log-analytics query \
  --workspace log-lms-hub-lms-dxdfyl \
  --analytics-query "AzureDiagnostics | where ResourceType == 'AZUREFIREWALLS' and TimeGenerated > ago(1h)"
```

---

**Previous:** [01-core-infrastructure-guide.md](./01-core-infrastructure-guide.md)
**Next:** [03-hub-security-monitoring-guide.md](./03-hub-security-monitoring-guide.md) - Key Vault, Log Analytics, and Monitoring
