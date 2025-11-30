#!/bin/bash
# ============================================================
# LMS GitHub Actions CI/CD Setup Script
# ============================================================
# This script creates the Service Principal and configures
# GitHub Actions for automated deployment to Azure AKS
#
# Usage: ./setup-github-actions.sh
# ============================================================

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Azure Configuration
SUBSCRIPTION_ID="b0eb3b11-2c08-45b8-a88a-ad3ba129957f"
RESOURCE_GROUP_PROD="rg-lms-prod-lms-rbmfy1"
ACR_NAME="acrlmsprodlmsrbmfy1"
AKS_CLUSTER="aks-lms-prod"
KEY_VAULT_NAME="kv-lms-prod-lms-rbmfy1"
SP_NAME="github-actions-lms-deploy"

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}    LMS GitHub Actions CI/CD Setup${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# Check Azure login
echo -e "${YELLOW}Checking Azure login...${NC}"
if ! az account show &>/dev/null; then
    echo -e "${RED}Not logged into Azure. Please run 'az login' first.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Logged into Azure${NC}"

echo ""
echo -e "${BLUE}Step 1: Creating Service Principal for GitHub Actions${NC}"
echo "------------------------------------------------------------"

# Create Service Principal with contributor role
echo -e "${YELLOW}Creating Service Principal '$SP_NAME'...${NC}"

SP_OUTPUT=$(az ad sp create-for-rbac \
    --name "$SP_NAME" \
    --role contributor \
    --scopes /subscriptions/$SUBSCRIPTION_ID \
    --sdk-auth 2>/dev/null)

if [ -z "$SP_OUTPUT" ]; then
    echo -e "${YELLOW}Service Principal may already exist. Getting credentials...${NC}"
    SP_APP_ID=$(az ad sp list --display-name "$SP_NAME" --query "[0].appId" -o tsv)
else
    echo -e "${GREEN}✓ Service Principal created${NC}"
    SP_APP_ID=$(echo $SP_OUTPUT | jq -r '.clientId')
fi

echo ""
echo -e "${BLUE}Step 2: Assigning ACR Push Role${NC}"
echo "------------------------------------------------------------"

ACR_ID=$(az acr show --name $ACR_NAME --query id -o tsv 2>/dev/null)
if [ -n "$ACR_ID" ]; then
    az role assignment create \
        --assignee $SP_APP_ID \
        --role "AcrPush" \
        --scope $ACR_ID \
        --output none 2>/dev/null || echo -e "${YELLOW}⚠ ACR role may already be assigned${NC}"
    echo -e "${GREEN}✓ ACR Push role assigned${NC}"
else
    echo -e "${YELLOW}⚠ ACR not found, skipping role assignment${NC}"
fi

echo ""
echo -e "${BLUE}Step 3: Assigning AKS Cluster User Role${NC}"
echo "------------------------------------------------------------"

AKS_ID=$(az aks show --resource-group $RESOURCE_GROUP_PROD --name $AKS_CLUSTER --query id -o tsv 2>/dev/null)
if [ -n "$AKS_ID" ]; then
    az role assignment create \
        --assignee $SP_APP_ID \
        --role "Azure Kubernetes Service Cluster User Role" \
        --scope $AKS_ID \
        --output none 2>/dev/null || echo -e "${YELLOW}⚠ AKS role may already be assigned${NC}"
    echo -e "${GREEN}✓ AKS Cluster User role assigned${NC}"
else
    echo -e "${YELLOW}⚠ AKS cluster not found, skipping role assignment${NC}"
fi

echo ""
echo -e "${BLUE}Step 4: Assigning Key Vault Secrets User Role${NC}"
echo "------------------------------------------------------------"

KV_ID=$(az keyvault show --name $KEY_VAULT_NAME --query id -o tsv 2>/dev/null)
if [ -n "$KV_ID" ]; then
    az role assignment create \
        --assignee $SP_APP_ID \
        --role "Key Vault Secrets User" \
        --scope $KV_ID \
        --output none 2>/dev/null || echo -e "${YELLOW}⚠ Key Vault role may already be assigned${NC}"
    echo -e "${GREEN}✓ Key Vault Secrets User role assigned${NC}"
else
    echo -e "${YELLOW}⚠ Key Vault not found, skipping role assignment${NC}"
fi

echo ""
echo -e "${BLUE}============================================================${NC}"
echo -e "${GREEN}    ✓ GitHub Actions Setup Complete!${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""
echo -e "${YELLOW}GitHub Secrets to Add:${NC}"
echo "------------------------------------------------------------"
echo -e "Go to: ${GREEN}https://github.com/huynq247/lms-well/settings/secrets/actions${NC}"
echo ""
echo -e "${YELLOW}Add these secrets:${NC}"
echo ""
echo "1. AZURE_CREDENTIALS:"
echo "   Copy the entire JSON output below:"
echo "------------------------------------------------------------"
if [ -n "$SP_OUTPUT" ]; then
    echo "$SP_OUTPUT"
else
    echo -e "${YELLOW}Run this command to get credentials:${NC}"
    echo "az ad sp create-for-rbac --name $SP_NAME --role contributor --scopes /subscriptions/$SUBSCRIPTION_ID --sdk-auth"
fi
echo "------------------------------------------------------------"
echo ""
echo "2. AZURE_SUBSCRIPTION_ID:"
echo "   $SUBSCRIPTION_ID"
echo ""
echo "3. ACR_LOGIN_SERVER:"
echo "   ${ACR_NAME}.azurecr.io"
echo ""
echo "4. AKS_RESOURCE_GROUP:"
echo "   $RESOURCE_GROUP_PROD"
echo ""
echo "5. AKS_CLUSTER_NAME:"
echo "   $AKS_CLUSTER"
echo ""
echo "6. KEY_VAULT_NAME:"
echo "   $KEY_VAULT_NAME"
echo ""
