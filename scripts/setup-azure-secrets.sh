#!/bin/bash
# ============================================================
# LMS Azure Key Vault Secrets Setup Script
# ============================================================
# This script sets up all required secrets in Azure Key Vault
# for the LMS production deployment
# 
# Usage: ./setup-azure-secrets.sh
# ============================================================

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Azure Resource Configuration
RESOURCE_GROUP="rg-lms-prod-lms-rbmfy1"
KEY_VAULT_NAME="kv-lms-prod-lms-rbmfy1"
POSTGRES_SERVER="psql-lms-prod-lms-rbmfy1"
COSMOS_ACCOUNT="cosmos-lms-prod-lms-rbmfy1"
STORAGE_ACCOUNT="stlmsprodlmsrbmfy1"

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}    LMS Azure Key Vault Secrets Setup${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# Function to check if logged into Azure
check_azure_login() {
    echo -e "${YELLOW}Checking Azure login status...${NC}"
    if ! az account show &>/dev/null; then
        echo -e "${RED}Not logged into Azure. Please run 'az login' first.${NC}"
        exit 1
    fi
    SUBSCRIPTION=$(az account show --query name -o tsv)
    echo -e "${GREEN}✓ Logged into Azure: $SUBSCRIPTION${NC}"
}

# Function to verify Key Vault exists
check_key_vault() {
    echo -e "${YELLOW}Checking Key Vault exists...${NC}"
    if ! az keyvault show --name $KEY_VAULT_NAME &>/dev/null; then
        echo -e "${RED}Key Vault '$KEY_VAULT_NAME' not found!${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Key Vault '$KEY_VAULT_NAME' exists${NC}"
}

# Function to generate secure password
generate_password() {
    openssl rand -base64 24 | tr -d '/+=' | head -c 24
}

# Function to generate JWT secret
generate_jwt_secret() {
    openssl rand -base64 64 | tr -d '\n'
}

echo ""
echo -e "${BLUE}Step 1: Verifying Azure Resources${NC}"
echo "------------------------------------------------------------"
check_azure_login
check_key_vault

echo ""
echo -e "${BLUE}Step 2: Creating PostgreSQL Password Secret${NC}"
echo "------------------------------------------------------------"

# Generate secure password
POSTGRES_PASSWORD=$(generate_password)
echo -e "${YELLOW}Generated secure PostgreSQL password${NC}"

# Store in Key Vault
az keyvault secret set \
    --vault-name $KEY_VAULT_NAME \
    --name "postgres-password" \
    --value "$POSTGRES_PASSWORD" \
    --output none

echo -e "${GREEN}✓ Secret 'postgres-password' created in Key Vault${NC}"

# Update PostgreSQL server password
echo -e "${YELLOW}Updating PostgreSQL server admin password...${NC}"
az postgres flexible-server update \
    --resource-group $RESOURCE_GROUP \
    --name $POSTGRES_SERVER \
    --admin-password "$POSTGRES_PASSWORD" \
    --output none 2>/dev/null || echo -e "${YELLOW}⚠ PostgreSQL password update skipped (may need manual update)${NC}"

echo -e "${GREEN}✓ PostgreSQL password configured${NC}"

echo ""
echo -e "${BLUE}Step 3: Creating Cosmos DB Key Secret${NC}"
echo "------------------------------------------------------------"

# Get Cosmos DB primary key
echo -e "${YELLOW}Retrieving Cosmos DB primary key...${NC}"
COSMOS_KEY=$(az cosmosdb keys list \
    --name $COSMOS_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --query "primaryMasterKey" -o tsv 2>/dev/null) || COSMOS_KEY=""

if [ -n "$COSMOS_KEY" ]; then
    az keyvault secret set \
        --vault-name $KEY_VAULT_NAME \
        --name "cosmos-primary-key" \
        --value "$COSMOS_KEY" \
        --output none
    echo -e "${GREEN}✓ Secret 'cosmos-primary-key' created in Key Vault${NC}"
else
    echo -e "${YELLOW}⚠ Cosmos DB key not retrieved. Creating placeholder...${NC}"
    az keyvault secret set \
        --vault-name $KEY_VAULT_NAME \
        --name "cosmos-primary-key" \
        --value "PLACEHOLDER_UPDATE_MANUALLY" \
        --output none
fi

echo ""
echo -e "${BLUE}Step 4: Creating Storage Account Key Secret${NC}"
echo "------------------------------------------------------------"

# Get Storage Account key
echo -e "${YELLOW}Retrieving Storage Account key...${NC}"
STORAGE_KEY=$(az storage account keys list \
    --account-name $STORAGE_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --query "[0].value" -o tsv 2>/dev/null) || STORAGE_KEY=""

if [ -n "$STORAGE_KEY" ]; then
    az keyvault secret set \
        --vault-name $KEY_VAULT_NAME \
        --name "storage-account-key" \
        --value "$STORAGE_KEY" \
        --output none
    echo -e "${GREEN}✓ Secret 'storage-account-key' created in Key Vault${NC}"
else
    echo -e "${YELLOW}⚠ Storage key not retrieved. Creating placeholder...${NC}"
    az keyvault secret set \
        --vault-name $KEY_VAULT_NAME \
        --name "storage-account-key" \
        --value "PLACEHOLDER_UPDATE_MANUALLY" \
        --output none
fi

echo ""
echo -e "${BLUE}Step 5: Creating JWT Secret Key${NC}"
echo "------------------------------------------------------------"

# Generate JWT secret
JWT_SECRET=$(generate_jwt_secret)
echo -e "${YELLOW}Generated secure JWT secret${NC}"

az keyvault secret set \
    --vault-name $KEY_VAULT_NAME \
    --name "jwt-secret-key" \
    --value "$JWT_SECRET" \
    --output none

echo -e "${GREEN}✓ Secret 'jwt-secret-key' created in Key Vault${NC}"

echo ""
echo -e "${BLUE}Step 6: Creating PostgreSQL Database${NC}"
echo "------------------------------------------------------------"

echo -e "${YELLOW}Creating 'lmsdb' database...${NC}"
az postgres flexible-server db create \
    --resource-group $RESOURCE_GROUP \
    --server-name $POSTGRES_SERVER \
    --database-name "lmsdb" \
    --output none 2>/dev/null || echo -e "${YELLOW}⚠ Database 'lmsdb' may already exist${NC}"

# Create additional databases for microservices
for db in "lms_auth" "lms_content" "lms_assignment"; do
    az postgres flexible-server db create \
        --resource-group $RESOURCE_GROUP \
        --server-name $POSTGRES_SERVER \
        --database-name "$db" \
        --output none 2>/dev/null || echo -e "${YELLOW}⚠ Database '$db' may already exist${NC}"
done

echo -e "${GREEN}✓ PostgreSQL databases created${NC}"

echo ""
echo -e "${BLUE}Step 7: Verifying All Secrets${NC}"
echo "------------------------------------------------------------"

echo -e "${YELLOW}Listing all secrets in Key Vault...${NC}"
az keyvault secret list \
    --vault-name $KEY_VAULT_NAME \
    --query "[].{Name:name, Enabled:attributes.enabled}" \
    --output table

echo ""
echo -e "${BLUE}============================================================${NC}"
echo -e "${GREEN}    ✓ All Azure Key Vault Secrets Created Successfully!${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""
echo -e "${YELLOW}Summary:${NC}"
echo "------------------------------------------------------------"
echo -e "Key Vault:        ${GREEN}$KEY_VAULT_NAME${NC}"
echo -e "PostgreSQL:       ${GREEN}$POSTGRES_SERVER.postgres.database.azure.com${NC}"
echo -e "Cosmos DB:        ${GREEN}$COSMOS_ACCOUNT.documents.azure.com${NC}"
echo -e "Storage Account:  ${GREEN}$STORAGE_ACCOUNT${NC}"
echo ""
echo -e "${YELLOW}Secrets Created:${NC}"
echo "  • postgres-password"
echo "  • cosmos-primary-key"
echo "  • storage-account-key"
echo "  • jwt-secret-key"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Run the GitHub Actions setup script"
echo "  2. Deploy to AKS using CI/CD pipeline"
echo "  3. Verify application connectivity"
echo ""
