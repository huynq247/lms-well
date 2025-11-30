# Hub Security & Monitoring Usage Guide (Resources 21-30)

## Azure Firewall Subnets: 21-22

### 21. module.hub.azurerm_subnet.AzureFirewallSubnet[0]
**Subnet:** `AzureFirewallSubnet`
**Address Range:** `10.0.1.0/26` (64 IPs, 59 usable)

**Purpose:** Dedicated subnet for Azure Firewall (required naming convention)

**How to Use:**

**View Subnet Configuration:**
```bash
# Show subnet details
az network vnet subnet show \
  --vnet-name vnet-lms-hub-lms-dxdfyl \
  --name AzureFirewallSubnet \
  --resource-group rg-lms-hub-lms-dxdfyl

# Check which resources are using this subnet
az network vnet subnet show \
  --vnet-name vnet-lms-hub-lms-dxdfyl \
  --name AzureFirewallSubnet \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --query "ipConfigurations[].id"
```

**Requirements:**
- Name MUST be "AzureFirewallSubnet"
- Minimum size: /26 (64 IPs)
- First usable IP (10.0.1.4) is assigned to firewall
- Cannot have NSG or UDR attached
- Only Azure Firewall can use this subnet

**Firewall IP Allocation:**
```
10.0.1.0/26 → AzureFirewallSubnet
├── 10.0.1.0    → Network address
├── 10.0.1.1    → Reserved (Azure)
├── 10.0.1.2    → Reserved (Azure)
├── 10.0.1.3    → Reserved (Azure)
├── 10.0.1.4    → Azure Firewall (Primary IP)
├── 10.0.1.5-62 → Available for firewall scale
└── 10.0.1.63   → Broadcast address
```

**Monitoring:**
```bash
# Check subnet health
az network vnet subnet show \
  --vnet-name vnet-lms-hub-lms-dxdfyl \
  --name AzureFirewallSubnet \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --query "provisioningState"
```

---

### 22. module.hub.azurerm_subnet.GatewaySubnet[0]
**Subnet:** `GatewaySubnet`
**Address Range:** `10.0.3.0/27` (32 IPs, 27 usable)

**Purpose:** Dedicated subnet for VPN Gateway (required naming convention)

**How to Use:**

**View Subnet Details:**
```bash
# Show gateway subnet configuration
az network vnet subnet show \
  --vnet-name vnet-lms-hub-lms-dxdfyl \
  --name GatewaySubnet \
  --resource-group rg-lms-hub-lms-dxdfyl

# Check IP allocation
az network vnet subnet show \
  --vnet-name vnet-lms-hub-lms-dxdfyl \
  --name GatewaySubnet \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --query "{AddressPrefix:addressPrefix, ProvisioningState:provisioningState}"
```

**Requirements:**
- Name MUST be "GatewaySubnet"
- Recommended minimum size: /27 (32 IPs)
- Used exclusively by Virtual Network Gateways
- Can have route table (UDR) attached
- Should NOT have NSG attached

**Gateway IP Allocation:**
```
10.0.3.0/27 → GatewaySubnet
├── 10.0.3.0-3   → Reserved (Azure)
├── 10.0.3.4     → VPN Gateway primary IP
├── 10.0.3.5     → VPN Gateway instance 2 (High Availability)
└── 10.0.3.6-30  → Available for additional gateways/ExpressRoute
```

**Best Practices:**
- Use /27 for VPN Gateway only
- Use /26 if planning to add ExpressRoute Gateway
- Never deploy VMs or other resources here
- Monitor available IPs before gateway upgrades

---

## Hub Network Subnets: 23-24

### 23. module.hub.azurerm_subnet.hub
**Subnet:** `hub-subnet`
**Address Range:** `10.0.0.0/24` (256 IPs, 251 usable)

**Purpose:** General-purpose subnet in hub VNet for management resources

**How to Use:**

**View Subnet Configuration:**
```bash
# Show subnet details
az network vnet subnet show \
  --vnet-name vnet-lms-hub-lms-dxdfyl \
  --name hub-subnet \
  --resource-group rg-lms-hub-lms-dxdfyl

# List resources in this subnet
az network nic list \
  --query "[?ipConfigurations[0].subnet.id.contains(@, 'hub-subnet')].{Name:name, PrivateIP:ipConfigurations[0].privateIPAddress}" \
  -o table
```

**Use Cases:**
- Jump box VMs for management
- Monitoring tools and agents
- Network appliances (if needed)
- Active Directory Domain Controllers (if implementing)

**Deploy Management VM:**
```bash
# Example: Deploy a Linux jump box
az vm create \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --name vm-jumpbox \
  --image Ubuntu2204 \
  --size Standard_B2s \
  --vnet-name vnet-lms-hub-lms-dxdfyl \
  --subnet hub-subnet \
  --nsg nsg-lms-hub-lms-dxdfyl \
  --public-ip-address "" \
  --authentication-type ssh \
  --admin-username azureuser \
  --ssh-key-values @~/.ssh/id_rsa.pub
```

**Security:**
- NSG attached: `nsg-lms-hub-lms-dxdfyl`
- Route table attached: `rt-lms-hub-lms-dxdfyl`
- Service endpoints: None (add if needed)

**Add Service Endpoint:**
```bash
# Enable access to Azure Storage without going through firewall
az network vnet subnet update \
  --vnet-name vnet-lms-hub-lms-dxdfyl \
  --name hub-subnet \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --service-endpoints Microsoft.Storage Microsoft.KeyVault
```

---

### 24. module.hub.azurerm_subnet_network_security_group_association.hub
**Purpose:** Associates NSG with hub-subnet for traffic filtering

**How to Use:**

**Verify Association:**
```bash
# Check NSG association
az network vnet subnet show \
  --vnet-name vnet-lms-hub-lms-dxdfyl \
  --name hub-subnet \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --query "networkSecurityGroup.id"

# Should return: .../networkSecurityGroups/nsg-lms-hub-lms-dxdfyl
```

**Impact:**
- All traffic to/from hub-subnet is filtered by NSG rules
- Rules apply to all resources in the subnet
- Changes to NSG affect all subnet resources immediately

**Manage NSG Rules:**
```bash
# View effective security rules for a NIC in this subnet
az network nic list-effective-nsg \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --name <nic-name>

# Test if traffic would be allowed
az network watcher test-flow-filters \
  --vm <vm-name> \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --direction Outbound \
  --protocol TCP \
  --remote 8.8.8.8 \
  --remote-port 443
```

**Remove Association (if needed):**
```bash
# WARNING: Removes all NSG protection from subnet
az network vnet subnet update \
  --vnet-name vnet-lms-hub-lms-dxdfyl \
  --name hub-subnet \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --network-security-group null
```

---

## Route Table Associations: 25-26

### 25. module.hub.azurerm_subnet_route_table_association.hub
**Purpose:** Associates route table with hub-subnet to force traffic through firewall

**How to Use:**

**Verify Association:**
```bash
# Check route table association
az network vnet subnet show \
  --vnet-name vnet-lms-hub-lms-dxdfyl \
  --name hub-subnet \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --query "routeTable.id"

# View effective routes for subnet
az network nic show-effective-route-table \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --name <nic-name-in-subnet> \
  -o table
```

**Traffic Flow:**
```
VM in hub-subnet (10.0.0.x)
  ↓
Route Table (rt-lms-hub-lms-dxdfyl)
  ↓
Azure Firewall (10.0.1.4)
  ↓
Destination (Internet, Spoke, or On-Prem)
```

**Troubleshooting Routing:**
```bash
# Test connectivity from VM in hub-subnet
az network watcher next-hop \
  --dest-ip 8.8.8.8 \
  --source-ip 10.0.0.5 \
  --vm <vm-name> \
  --nic <nic-name> \
  --resource-group rg-lms-hub-lms-dxdfyl

# Expected output:
# NextHopType: VirtualAppliance
# NextHopIpAddress: 10.0.1.4
```

**Bypass Firewall (Emergency Only):**
```bash
# Remove route table association temporarily
az network vnet subnet update \
  --vnet-name vnet-lms-hub-lms-dxdfyl \
  --name hub-subnet \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --route-table null

# Traffic will now go directly without firewall inspection
# Re-associate after troubleshooting!
```

---

### 26. module.hub.azurerm_virtual_network.hub
**VNet Name:** `vnet-lms-hub-lms-dxdfyl`
**Address Space:** `10.0.0.0/16` (65,536 IPs)

**Purpose:** Central hub VNet for all network connectivity and security services

**How to Use:**

**View VNet Configuration:**
```bash
# Show VNet details
az network vnet show \
  --name vnet-lms-hub-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl

# List all subnets
az network vnet subnet list \
  --vnet-name vnet-lms-hub-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --query "[].{Name:name, AddressPrefix:addressPrefix}" \
  -o table
```

**VNet Architecture:**
```
vnet-lms-hub-lms-dxdfyl (10.0.0.0/16)
├── hub-subnet (10.0.0.0/24)              → Management resources
├── AzureFirewallSubnet (10.0.1.0/26)     → Azure Firewall
├── AzureBastionSubnet (10.0.2.0/26)      → Azure Bastion
└── GatewaySubnet (10.0.3.0/27)           → VPN Gateway
```

**VNet Peerings:**
```bash
# List all peerings
az network vnet peering list \
  --vnet-name vnet-lms-hub-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl \
  -o table

# Expected peerings:
# - hub-to-dev (10.1.0.0/16)
# - hub-to-prod (10.2.0.0/16)
```

**Add New Subnet:**
```bash
# Example: Add subnet for shared services
az network vnet subnet create \
  --vnet-name vnet-lms-hub-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --name shared-services-subnet \
  --address-prefix 10.0.4.0/24 \
  --network-security-group nsg-lms-hub-lms-dxdfyl \
  --route-table rt-lms-hub-lms-dxdfyl
```

**Monitor VNet:**
```bash
# Check VNet health
az network vnet show \
  --name vnet-lms-hub-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --query "provisioningState"

# View VNet metrics
az monitor metrics list \
  --resource /subscriptions/a9530d40-75da-44a3-9581-b9faf889608c/resourceGroups/rg-lms-hub-lms-dxdfyl/providers/Microsoft.Network/virtualNetworks/vnet-lms-hub-lms-dxdfyl \
  --metric "BytesDroppedDDoS"
```

---

## VPN Gateway: 27-29

### 27. module.hub.azurerm_virtual_network_gateway.hub[0]
**Gateway Name:** `vgw-lms-hub-lms-dxdfyl`
**SKU:** `VpnGw1` (up to 650 Mbps, 30 tunnels)

**Purpose:** Site-to-Site VPN connection to on-premises network

**How to Use:**

**View Gateway Status:**
```bash
# Check gateway status
az network vnet-gateway show \
  --name vgw-lms-hub-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --query "{Name:name, State:provisioningState, SKU:sku.name, ActiveActive:activeActive}"

# Get gateway public IP
az network vnet-gateway show \
  --name vgw-lms-hub-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --query "ipConfigurations[0].publicIPAddress.id" -o tsv | xargs az network public-ip show --ids --query ipAddress -o tsv
```

**Monitor VPN Performance:**
```bash
# Check bandwidth usage
az monitor metrics list \
  --resource /subscriptions/a9530d40-75da-44a3-9581-b9faf889608c/resourceGroups/rg-lms-hub-lms-dxdfyl/providers/Microsoft.Network/virtualNetworkGateways/vgw-lms-hub-lms-dxdfyl \
  --metric "AverageBandwidth" \
  --start-time 2025-02-02T00:00:00Z \
  --end-time 2025-02-02T23:59:59Z

# Check tunnel health
az monitor metrics list \
  --resource /subscriptions/a9530d40-75da-44a3-9581-b9faf889608c/resourceGroups/rg-lms-hub-lms-dxdfyl/providers/Microsoft.Network/virtualNetworkGateways/vgw-lms-hub-lms-dxdfyl \
  --metric "TunnelIngressPacketDropCount"
```

**Reset Gateway (If Needed):**
```bash
# Reset gateway (causes brief downtime)
az network vnet-gateway reset \
  --name vgw-lms-hub-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl

# This takes 5-10 minutes
```

**Upgrade SKU:**
```bash
# Upgrade to VpnGw2 (1 Gbps, 30 tunnels) - No downtime
az network vnet-gateway update \
  --name vgw-lms-hub-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --sku VpnGw2

# Upgrade to VpnGw3 (1.25 Gbps, 30 tunnels)
az network vnet-gateway update \
  --name vgw-lms-hub-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --sku VpnGw3
```

**Enable BGP (Advanced):**
```bash
# Enable BGP for dynamic routing
az network vnet-gateway update \
  --name vgw-lms-hub-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --asn 65515
```

---

### 28. module.hub.azurerm_virtual_network_peering.hub_to_dev
**Peering:** Hub ↔ Development Spoke

**Configuration:**
- Remote VNet: `vnet-lms-dev-lms-dxdfyl` (10.1.0.0/16)
- Allow Gateway Transit: Enabled (Dev uses Hub's VPN Gateway)
- Allow Forwarded Traffic: Enabled (Traffic through Firewall)

**How to Use:**

**Check Peering Status:**
```bash
# View peering status
az network vnet peering show \
  --name hub-to-dev \
  --vnet-name vnet-lms-hub-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --query "{Name:name, State:peeringState, RemoteVNet:remoteVirtualNetwork.id}"

# Verify bidirectional peering
az network vnet peering show \
  --name dev-to-hub \
  --vnet-name vnet-lms-dev-lms-dxdfyl \
  --resource-group lms-dev-rg-lms-dxdfyl \
  --query peeringState
```

**Peering States:**
- `Initiated` → Peering created but not connected
- `Connected` → Both sides configured, traffic flowing ✅
- `Disconnected` → Peering broken

**Troubleshoot Connectivity:**
```bash
# Test connectivity from hub to dev
az network watcher test-ip-flow \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --vm <hub-vm-name> \
  --direction Outbound \
  --protocol TCP \
  --local 10.0.0.5:443 \
  --remote 10.1.0.5:443

# Check if traffic is allowed
# Expected: Access Allowed via Firewall rule
```

**Refresh Peering (If Stuck):**
```bash
# Sync peering state
az network vnet peering sync \
  --name hub-to-dev \
  --vnet-name vnet-lms-hub-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl
```

---

### 29. module.hub.azurerm_virtual_network_peering.hub_to_prod
**Peering:** Hub ↔ Production Spoke

**Configuration:**
- Remote VNet: `vnet-lms-prod-lms-dxdfyl` (10.2.0.0/16)
- Allow Gateway Transit: Enabled (Prod uses Hub's VPN Gateway)
- Allow Forwarded Traffic: Enabled (Traffic through Firewall)

**How to Use:**

**Check Peering Status:**
```bash
# View peering status
az network vnet peering show \
  --name hub-to-prod \
  --vnet-name vnet-lms-hub-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl

# Verify bidirectional peering
az network vnet peering show \
  --name prod-to-hub \
  --vnet-name vnet-lms-prod-lms-dxdfyl \
  --resource-group lms-prod-rg-lms-dxdfyl
```

**Test Connectivity:**
```bash
# Ping from AKS pod to hub
kubectl run -it --rm debug --image=busybox --restart=Never -- ping 10.0.0.5

# Test DNS resolution
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup kv-lms-hub-lms-dxdfyl.vault.azure.net

# Verify firewall routing
kubectl run -it --rm debug --image=nicolaka/netshoot --restart=Never -- traceroute 8.8.8.8
# Expected: 10.2.x.x → 10.0.1.4 (Firewall) → Internet
```

**Monitor Peering Traffic:**
```bash
# View bytes transferred over peering
az monitor metrics list \
  --resource /subscriptions/a9530d40-75da-44a3-9581-b9faf889608c/resourceGroups/rg-lms-hub-lms-dxdfyl/providers/Microsoft.Network/virtualNetworks/vnet-lms-hub-lms-dxdfyl/virtualNetworkPeerings/hub-to-prod \
  --metric "BytesTransmittedRate"
```

---

## Key Vault & Monitoring: 30

### 30. module.hub.azurerm_vpn_connection.onprem[0]
**Connection Name:** `vpn-lms-hub-to-onprem-lms-dxdfyl`

**Purpose:** Active Site-to-Site VPN tunnel to on-premises network (192.168.0.0/16)

**How to Use:**

**Check Connection Status:**
```bash
# View connection status
az network vpn-connection show \
  --name vpn-lms-hub-to-onprem-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --query "{Status:connectionStatus, Type:connectionType, EgressBytes:egressBytesTransferred, IngressBytes:ingressBytesTransferred}"

# Expected output:
# Status: Connected
# Type: IPsec
```

**Get Shared Key:**
```bash
# Retrieve VPN shared key (for on-premises device configuration)
az network vpn-connection shared-key show \
  --connection-name vpn-lms-hub-to-onprem-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl

# Or from Key Vault
az keyvault secret show \
  --vault-name kv-lms-hub-lms-dxdfyl \
  --name vpn-shared-key \
  --query value -o tsv
```

**Update Shared Key:**
```bash
# Change VPN shared key (requires coordination with on-prem team)
az network vpn-connection shared-key set \
  --connection-name vpn-lms-hub-to-onprem-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --value "NewSecureKey123!@#"

# Update Key Vault
az keyvault secret set \
  --vault-name kv-lms-hub-lms-dxdfyl \
  --name vpn-shared-key \
  --value "NewSecureKey123!@#"
```

**Troubleshoot Connection:**
```bash
# 1. Check connection logs
az monitor log-analytics query \
  --workspace log-lms-hub-lms-dxdfyl \
  --analytics-query "AzureDiagnostics | where ResourceType == 'CONNECTIONS' and TimeGenerated > ago(1h)"

# 2. Verify IKE policy matches on-prem
az network vpn-connection show \
  --name vpn-lms-hub-to-onprem-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --query "ipsecPolicies"

# 3. Reset connection
az network vpn-connection reset \
  --name vpn-lms-hub-to-onprem-lms-dxdfyl \
  --resource-group rg-lms-hub-lms-dxdfyl
```

**Monitor Bandwidth:**
```bash
# Check connection throughput
az monitor metrics list \
  --resource /subscriptions/a9530d40-75da-44a3-9581-b9faf889608c/resourceGroups/rg-lms-hub-lms-dxdfyl/providers/Microsoft.Network/connections/vpn-lms-hub-to-onprem-lms-dxdfyl \
  --metric "AverageBandwidth" \
  --aggregation Average

# Check packet drops
az monitor metrics list \
  --resource /subscriptions/a9530d40-75da-44a3-9581-b9faf889608c/resourceGroups/rg-lms-hub-lms-dxdfyl/providers/Microsoft.Network/connections/vpn-lms-hub-to-onprem-lms-dxdfyl \
  --metric "TunnelEgressPacketDropTSMismatch"
```

**Set Up Alerts:**
```bash
# Alert when connection goes down
az monitor metrics alert create \
  --name "vpn-connection-down" \
  --resource-group rg-lms-hub-lms-dxdfyl \
  --scopes /subscriptions/a9530d40-75da-44a3-9581-b9faf889608c/resourceGroups/rg-lms-hub-lms-dxdfyl/providers/Microsoft.Network/connections/vpn-lms-hub-to-onprem-lms-dxdfyl \
  --condition "avg ConnectionStatus < 1" \
  --description "VPN connection to on-premises is down" \
  --evaluation-frequency 1m \
  --window-size 5m
```

---

## Quick Reference Commands

```bash
# Hub infrastructure health check
az network vnet show --name vnet-lms-hub-lms-dxdfyl --resource-group rg-lms-hub-lms-dxdfyl --query provisioningState
az network vnet-gateway show --name vgw-lms-hub-lms-dxdfyl --resource-group rg-lms-hub-lms-dxdfyl --query provisioningState
az network firewall show --name azfw-lms-hub --resource-group rg-lms-hub-lms-dxdfyl --query provisioningState

# Check all peerings
az network vnet peering list --vnet-name vnet-lms-hub-lms-dxdfyl --resource-group rg-lms-hub-lms-dxdfyl -o table

# VPN connection status
az network vpn-connection show --name vpn-lms-hub-to-onprem-lms-dxdfyl --resource-group rg-lms-hub-lms-dxdfyl --query connectionStatus -o tsv

# Monitor firewall traffic (last 5 minutes)
az monitor log-analytics query \
  --workspace log-lms-hub-lms-dxdfyl \
  --analytics-query "AzureDiagnostics | where ResourceType == 'AZUREFIREWALLS' and TimeGenerated > ago(5m) | summarize count() by msg_s"
```

---

**Previous:** [02-hub-networking-guide.md](./02-hub-networking-guide.md)
**Next:** [04-development-compute-guide.md](./04-development-compute-guide.md) - Development Environment Resources
