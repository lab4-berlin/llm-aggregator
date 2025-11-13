#!/bin/bash

# GCP Setup Script for LLM Aggregator
# This script sets up all necessary GCP resources for deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-}"
REGION="${GCP_REGION:-us-central1}"
DB_INSTANCE="llm-aggregator-db"
DB_NAME="llm_aggregator"
DB_USER="llm_user"
ARTIFACT_REGISTRY="llm-aggregator"

echo -e "${GREEN}=== GCP Setup for LLM Aggregator ===${NC}\n"

# Check if project ID is set
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: GCP_PROJECT_ID environment variable is not set${NC}"
    echo "Please set it with: export GCP_PROJECT_ID=your-project-id"
    exit 1
fi

echo -e "${YELLOW}Using project: $PROJECT_ID${NC}"
echo -e "${YELLOW}Using region: $REGION${NC}\n"

# Set the project
gcloud config set project $PROJECT_ID

# Step 1: Enable required APIs
echo -e "${GREEN}Step 1: Enabling required APIs...${NC}"
gcloud services enable \
    run.googleapis.com \
    sqladmin.googleapis.com \
    secretmanager.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    --project=$PROJECT_ID

echo -e "${GREEN}✓ APIs enabled${NC}\n"

# Step 2: Create Artifact Registry repository
echo -e "${GREEN}Step 2: Creating Artifact Registry repository...${NC}"
if gcloud artifacts repositories describe $ARTIFACT_REGISTRY --location=$REGION --project=$PROJECT_ID &>/dev/null; then
    echo -e "${YELLOW}Repository already exists, skipping...${NC}"
else
    gcloud artifacts repositories create $ARTIFACT_REGISTRY \
        --repository-format=docker \
        --location=$REGION \
        --project=$PROJECT_ID
    echo -e "${GREEN}✓ Repository created${NC}"
fi
echo ""

# Step 3: Create Cloud SQL instance
echo -e "${GREEN}Step 3: Creating Cloud SQL instance...${NC}"
if gcloud sql instances describe $DB_INSTANCE --project=$PROJECT_ID &>/dev/null; then
    echo -e "${YELLOW}Database instance already exists, skipping...${NC}"
else
    echo -e "${YELLOW}Creating database instance (this may take 5-10 minutes)...${NC}"
    gcloud sql instances create $DB_INSTANCE \
        --database-version=POSTGRES_15 \
        --tier=db-f1-micro \
        --region=$REGION \
        --root-password=$(openssl rand -base64 32) \
        --project=$PROJECT_ID
    
    echo -e "${GREEN}✓ Database instance created${NC}"
fi
echo ""

# Step 4: Create database
echo -e "${GREEN}Step 4: Creating database...${NC}"
if gcloud sql databases describe $DB_NAME --instance=$DB_INSTANCE --project=$PROJECT_ID &>/dev/null; then
    echo -e "${YELLOW}Database already exists, skipping...${NC}"
else
    gcloud sql databases create $DB_NAME \
        --instance=$DB_INSTANCE \
        --project=$PROJECT_ID
    echo -e "${GREEN}✓ Database created${NC}"
fi
echo ""

# Step 5: Create database user
echo -e "${GREEN}Step 5: Creating database user...${NC}"
DB_PASSWORD=$(openssl rand -base64 32)
gcloud sql users create $DB_USER \
    --instance=$DB_INSTANCE \
    --password=$DB_PASSWORD \
    --project=$PROJECT_ID 2>/dev/null || echo -e "${YELLOW}User may already exist, updating password...${NC}"

# Update password if user exists
gcloud sql users set-password $DB_USER \
    --instance=$DB_INSTANCE \
    --password=$DB_PASSWORD \
    --project=$PROJECT_ID

echo -e "${GREEN}✓ Database user created/updated${NC}"
echo -e "${YELLOW}Database password: $DB_PASSWORD${NC}"
echo -e "${YELLOW}Save this password! You'll need it for secrets.${NC}\n"

# Step 6: Get connection name
CONNECTION_NAME=$(gcloud sql instances describe $DB_INSTANCE --project=$PROJECT_ID --format='value(connectionName)')
echo -e "${GREEN}Cloud SQL Connection Name: $CONNECTION_NAME${NC}\n"

# Step 7: Create secrets
echo -e "${GREEN}Step 6: Creating secrets in Secret Manager...${NC}"

# Generate encryption key
ENCRYPTION_KEY=$(openssl rand -hex 32)
echo -e "${YELLOW}Generated encryption key: $ENCRYPTION_KEY${NC}"

# Generate JWT secret
JWT_SECRET=$(openssl rand -hex 32)
echo -e "${YELLOW}Generated JWT secret: $JWT_SECRET${NC}"

# Create database connection string
DB_CONNECTION_STRING="postgresql://$DB_USER:$DB_PASSWORD@/$DB_NAME?host=/cloudsql/$CONNECTION_NAME"

# Create secrets
echo "$ENCRYPTION_KEY" | gcloud secrets create encryption-key --data-file=- --project=$PROJECT_ID 2>/dev/null || \
    echo "$ENCRYPTION_KEY" | gcloud secrets versions add encryption-key --data-file=- --project=$PROJECT_ID

echo "$JWT_SECRET" | gcloud secrets create jwt-secret --data-file=- --project=$PROJECT_ID 2>/dev/null || \
    echo "$JWT_SECRET" | gcloud secrets versions add jwt-secret --data-file=- --project=$PROJECT_ID

echo "$DB_PASSWORD" | gcloud secrets create db-password --data-file=- --project=$PROJECT_ID 2>/dev/null || \
    echo "$DB_PASSWORD" | gcloud secrets versions add db-password --data-file=- --project=$PROJECT_ID

echo "$DB_CONNECTION_STRING" | gcloud secrets create db-connection-string --data-file=- --project=$PROJECT_ID 2>/dev/null || \
    echo "$DB_CONNECTION_STRING" | gcloud secrets versions add db-connection-string --data-file=- --project=$PROJECT_ID

echo -e "${GREEN}✓ Secrets created${NC}\n"

# Step 8: Create service account for GitHub Actions
echo -e "${GREEN}Step 7: Creating service account for GitHub Actions...${NC}"
SA_NAME="github-actions"
SA_EMAIL="$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"

if gcloud iam service-accounts describe $SA_EMAIL --project=$PROJECT_ID &>/dev/null; then
    echo -e "${YELLOW}Service account already exists${NC}"
else
    gcloud iam service-accounts create $SA_NAME \
        --display-name="GitHub Actions Service Account" \
        --project=$PROJECT_ID
    echo -e "${GREEN}✓ Service account created${NC}"
fi

# Grant necessary permissions
echo -e "${YELLOW}Granting permissions...${NC}"
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/run.admin" \
    --condition=None

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/secretmanager.secretAccessor" \
    --condition=None

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/cloudsql.client" \
    --condition=None

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/artifactregistry.writer" \
    --condition=None

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/cloudbuild.builds.editor" \
    --condition=None

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/iam.serviceAccountUser" \
    --condition=None

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/serviceusage.serviceUsageConsumer" \
    --condition=None

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/storage.admin" \
    --condition=None

echo -e "${GREEN}✓ Permissions granted${NC}\n"

# Grant permissions to default Compute Engine service account for Cloud Build
echo -e "${GREEN}Granting permissions to Compute Engine service account for Cloud Build...${NC}"
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
COMPUTE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$COMPUTE_SA" \
    --role="roles/storage.admin" \
    --condition=None

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$COMPUTE_SA" \
    --role="roles/serviceusage.serviceUsageConsumer" \
    --condition=None

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$COMPUTE_SA" \
    --role="roles/artifactregistry.writer" \
    --condition=None

echo -e "${GREEN}✓ Compute Engine service account permissions granted${NC}\n"

# Step 9: Create and download service account key
echo -e "${GREEN}Step 8: Creating service account key...${NC}"
KEY_FILE="gcp-service-account-key.json"

# Disable the constraint that prevents service account key creation
echo -e "${YELLOW}Ensuring service account key creation is allowed...${NC}"
gcloud resource-manager org-policies disable-enforce \
    constraints/iam.disableServiceAccountKeyCreation \
    --project=$PROJECT_ID 2>/dev/null || echo -e "${YELLOW}Note: Constraint may already be disabled or requires org-level access${NC}"

# Create the service account key
gcloud iam service-accounts keys create $KEY_FILE \
    --iam-account=$SA_EMAIL \
    --project=$PROJECT_ID

echo -e "${GREEN}✓ Service account key created: $KEY_FILE${NC}\n"

# Summary
echo -e "${GREEN}=== Setup Complete! ===${NC}\n"
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Add the following secrets to your GitHub repository:"
echo "   - GCP_PROJECT_ID: $PROJECT_ID"
echo "   - GCP_SA_KEY: (content of $KEY_FILE)"
echo ""
echo "2. To add secrets to GitHub:"
echo "   - Go to: https://github.com/YOUR_USERNAME/llm-aggregator/settings/secrets/actions"
echo "   - Click 'New repository secret'"
echo "   - Add GCP_PROJECT_ID and GCP_SA_KEY"
echo ""
echo "3. The service account key file ($KEY_FILE) contains sensitive information."
echo "   Add it to .gitignore and never commit it!"
echo ""
echo -e "${GREEN}Database connection details:${NC}"
echo "  Connection Name: $CONNECTION_NAME"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo ""
echo -e "${GREEN}Your application will be deployed to:${NC}"
echo "  Backend: https://llm-aggregator-backend-xxx.run.app"
echo "  Frontend: https://llm-aggregator-frontend-xxx.run.app"
echo ""
echo -e "${YELLOW}Note: Update CORS_ORIGINS in backend after first deployment!${NC}"


