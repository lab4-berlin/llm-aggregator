#!/bin/bash

# Manual Deployment Script for GCP Cloud Run
# Use this if you want to deploy manually without GitHub Actions

set -e

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-}"
REGION="${GCP_REGION:-us-central1}"
BACKEND_SERVICE="llm-aggregator-backend"
FRONTEND_SERVICE="llm-aggregator-frontend"
DB_INSTANCE="llm-aggregator-db"

if [ -z "$PROJECT_ID" ]; then
    echo "Error: GCP_PROJECT_ID environment variable is not set"
    exit 1
fi

gcloud config set project $PROJECT_ID

echo "Building and deploying backend..."
cd backend
gcloud builds submit --tag $REGION-docker.pkg.dev/$PROJECT_ID/llm-aggregator/$BACKEND_SERVICE:latest

gcloud run deploy $BACKEND_SERVICE \
    --image $REGION-docker.pkg.dev/$PROJECT_ID/llm-aggregator/$BACKEND_SERVICE:latest \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-secrets=DATABASE_URL=db-connection-string:latest,ENCRYPTION_KEY=encryption-key:latest,JWT_SECRET_KEY=jwt-secret:latest,DB_PASSWORD=db-password:latest \
    --set-env-vars="JWT_ALGORITHM=HS256,JWT_EXPIRATION_HOURS=24,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID:$REGION:$DB_INSTANCE" \
    --add-cloudsql-instances=$PROJECT_ID:$REGION:$DB_INSTANCE \
    --memory=512Mi \
    --cpu=1 \
    --min-instances=0 \
    --max-instances=10 \
    --timeout=300

BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE --region=$REGION --format='value(status.url)')
echo "Backend deployed at: $BACKEND_URL"

cd ../frontend
echo "VITE_API_URL=$BACKEND_URL" > .env.production
npm install
npm run build

echo "Building and deploying frontend..."
gcloud builds submit --tag $REGION-docker.pkg.dev/$PROJECT_ID/llm-aggregator/$FRONTEND_SERVICE:latest

gcloud run deploy $FRONTEND_SERVICE \
    --image $REGION-docker.pkg.dev/$PROJECT_ID/llm-aggregator/$FRONTEND_SERVICE:latest \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory=256Mi \
    --cpu=1 \
    --min-instances=0 \
    --max-instances=10 \
    --port=80

FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE --region=$REGION --format='value(status.url)')
echo "Frontend deployed at: $FRONTEND_URL"

echo ""
echo "Deployment complete!"
echo "Backend: $BACKEND_URL"
echo "Frontend: $FRONTEND_URL"
echo ""
echo "Update CORS_ORIGINS in backend to include: $FRONTEND_URL"


