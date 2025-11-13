# GCP Cloud Run Deployment Guide

This guide will help you deploy the LLM Aggregator to Google Cloud Platform using Cloud Run.

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **gcloud CLI** installed and authenticated
   ```bash
   # Install gcloud CLI: https://cloud.google.com/sdk/docs/install
   gcloud auth login
   gcloud auth application-default login
   ```
3. **GitHub Account** (for CI/CD)
4. **Docker** (optional, for local testing)

## Quick Start

### Step 1: Initial GCP Setup

1. **Set your project ID:**
   ```bash
   export GCP_PROJECT_ID=your-project-id
   export GCP_REGION=us-central1  # Optional, defaults to us-central1
   ```

2. **Run the setup script:**
   ```bash
   chmod +x scripts/setup-gcp.sh
   ./scripts/setup-gcp.sh
   ```

   This script will:
   - Enable required GCP APIs
   - Create Artifact Registry for Docker images
   - Create Cloud SQL PostgreSQL instance
   - Create database and user
   - Create secrets in Secret Manager
   - Create service account for GitHub Actions
   - Automatically enable service account key creation (if needed)
   - Generate and download service account key

3. **Save the generated credentials:**
   - The script creates `gcp-service-account-key.json`
   - **IMPORTANT:** Add this file to `.gitignore` and never commit it!

### Step 2: Configure GitHub Secrets

1. Go to your GitHub repository
2. Navigate to: **Settings** → **Secrets and variables** → **Actions**
3. Add the following secrets:

   - **GCP_PROJECT_ID**: Your GCP project ID
   - **GCP_SA_KEY**: Content of `gcp-service-account-key.json` (copy entire JSON)

   To add a secret:
   - Click "New repository secret"
   - Name: `GCP_PROJECT_ID`
   - Value: `your-project-id`
   - Click "Add secret"
   - Repeat for `GCP_SA_KEY` (paste the entire JSON content)

### Step 3: Update CORS Configuration

After the first deployment, you'll need to update the backend CORS settings:

1. Get your frontend URL from Cloud Run console
2. Update the backend service:
   ```bash
   gcloud run services update llm-aggregator-backend \
     --region=us-central1 \
     --update-env-vars="CORS_ORIGINS=https://your-frontend-url.run.app"
   ```

### Step 4: Deploy

#### Option A: Automatic Deployment (Recommended)

1. **Push to main branch:**
   ```bash
   git add .
   git commit -m "Setup GCP deployment"
   git push origin main
   ```

2. **GitHub Actions will automatically:**
   - Build Docker images
   - Push to Artifact Registry
   - Deploy to Cloud Run

3. **Monitor deployment:**
   - Go to: https://github.com/YOUR_USERNAME/llm-aggregator/actions
   - Watch the workflow run

#### Option B: Manual Deployment

If you prefer to deploy manually:

```bash
chmod +x scripts/manual-deploy.sh
export GCP_PROJECT_ID=your-project-id
./scripts/manual-deploy.sh
```

## Post-Deployment Steps

### 1. Update Backend CORS

After deployment, update CORS to allow your frontend:

```bash
# Get frontend URL
FRONTEND_URL=$(gcloud run services describe llm-aggregator-frontend \
  --region=us-central1 --format='value(status.url)')

# Update backend CORS
gcloud run services update llm-aggregator-backend \
  --region=us-central1 \
  --update-env-vars="CORS_ORIGINS=$FRONTEND_URL"
```

### 2. Configure Email (Optional)

If you want email verification to work:

```bash
# Store SMTP password in Secret Manager
echo "your-smtp-password" | gcloud secrets create smtp-password --data-file=-

# Update backend to use SMTP secret
gcloud run services update llm-aggregator-backend \
  --region=us-central1 \
  --update-secrets=SMTP_PASSWORD=smtp-password:latest \
  --update-env-vars="SMTP_HOST=smtp.gmail.com,SMTP_PORT=587,SMTP_USER=your-email@gmail.com,SMTP_FROM_EMAIL=your-email@gmail.com,FRONTEND_URL=$FRONTEND_URL"
```

### 3. Run Database Migrations

The application will automatically create tables on first startup. If you need to run migrations manually:

```bash
# Connect to Cloud SQL
gcloud sql connect llm-aggregator-db --user=llm_user --database=llm_aggregator

# Or use Cloud SQL Proxy for local development
```

## Architecture

```
┌─────────────────┐
│   GitHub Repo   │
│  (Source Code)  │
└────────┬────────┘
         │
         │ Push to main
         ▼
┌─────────────────┐
│ GitHub Actions  │
│   (CI/CD)       │
└────────┬────────┘
         │
         ├─► Build Backend Image ──┐
         │                          │
         └─► Build Frontend Image ──┤
                                    ▼
                          ┌──────────────────┐
                          │ Artifact Registry│
                          │  (Docker Images) │
                          └────────┬─────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    ▼                             ▼
          ┌─────────────────┐         ┌─────────────────┐
          │  Cloud Run      │         │  Cloud Run       │
          │  (Backend)      │         │  (Frontend)     │
          └────────┬────────┘         └─────────────────┘
                   │
                   │ Connects via
                   │ Unix Socket
                   ▼
          ┌─────────────────┐
          │   Cloud SQL     │
          │  (PostgreSQL)   │
          └─────────────────┘
```

## Security

### Secrets Management

All sensitive data is stored in GCP Secret Manager:
- `encryption-key`: For encrypting API keys
- `jwt-secret`: For JWT token signing
- `db-password`: Database password
- `db-connection-string`: Full database connection string
- `smtp-password`: Email SMTP password (optional)

### Service Account Permissions

The GitHub Actions service account has minimal required permissions:
- `roles/run.admin`: Deploy to Cloud Run
- `roles/secretmanager.secretAccessor`: Read secrets
- `roles/cloudsql.client`: Connect to Cloud SQL
- `roles/artifactregistry.writer`: Push Docker images
- `roles/cloudbuild.builds.editor`: Build images

### Network Security

- Cloud SQL uses private IP (no public access)
- Cloud Run services use HTTPS automatically
- CORS is configured to only allow your frontend domain

## Monitoring

### View Logs

```bash
# Backend logs
gcloud run services logs read llm-aggregator-backend --region=us-central1

# Frontend logs
gcloud run services logs read llm-aggregator-frontend --region=us-central1
```

### View Metrics

1. Go to Cloud Run console: https://console.cloud.google.com/run
2. Click on your service
3. View metrics, logs, and revisions

## Cost Estimation

**Free Tier:**
- Cloud Run: 2 million requests/month free
- Cloud SQL: No free tier, but db-f1-micro is ~$7/month
- Secret Manager: 6 secrets free

**Typical Monthly Cost (low traffic):**
- Cloud Run: $0 (within free tier)
- Cloud SQL (db-f1-micro): ~$7
- Secret Manager: $0 (within free tier)
- **Total: ~$7/month**

**Scaling:**
- Cloud Run scales to zero when not in use
- Pay only for actual usage
- Can scale up to handle traffic spikes automatically

## Troubleshooting

### Deployment Fails

1. **Check GitHub Actions logs:**
   - Go to Actions tab in GitHub
   - Click on failed workflow
   - Review error messages

2. **Common issues:**
   - Missing secrets: Ensure GCP_PROJECT_ID and GCP_SA_KEY are set
   - Permission errors: Verify service account has required roles
   - Build errors: Check Dockerfile syntax

### Backend Can't Connect to Database

1. **Verify Cloud SQL connection:**
   ```bash
   gcloud sql instances describe llm-aggregator-db
   ```

2. **Check Cloud SQL connection name:**
   - Should be: `PROJECT_ID:REGION:llm-aggregator-db`
   - Verify in backend environment variables

3. **Test connection:**
   ```bash
   gcloud sql connect llm-aggregator-db --user=llm_user
   ```

### Frontend Can't Connect to Backend

1. **Check CORS configuration:**
   - Verify CORS_ORIGINS includes frontend URL
   - Check browser console for CORS errors

2. **Verify backend URL:**
   - Check VITE_API_URL in frontend build
   - Ensure backend is deployed and accessible

### Secrets Not Found

1. **List secrets:**
   ```bash
   gcloud secrets list
   ```

2. **Verify secret versions:**
   ```bash
   gcloud secrets versions list encryption-key
   ```

3. **Recreate if needed:**
   ```bash
   echo "your-value" | gcloud secrets create secret-name --data-file=-
   ```

## Updating the Application

### Automatic Updates

Just push to the `main` branch - GitHub Actions will handle the rest!

### Manual Updates

1. **Update code:**
   ```bash
   git add .
   git commit -m "Update application"
   git push origin main
   ```

2. **Or rebuild manually:**
   ```bash
   ./scripts/manual-deploy.sh
   ```

## Cleanup

To remove all resources:

```bash
# Delete Cloud Run services
gcloud run services delete llm-aggregator-backend --region=us-central1
gcloud run services delete llm-aggregator-frontend --region=us-central1

# Delete Cloud SQL instance (WARNING: This deletes all data!)
gcloud sql instances delete llm-aggregator-db

# Delete secrets
gcloud secrets delete encryption-key
gcloud secrets delete jwt-secret
gcloud secrets delete db-password
gcloud secrets delete db-connection-string

# Delete Artifact Registry repository
gcloud artifacts repositories delete llm-aggregator --location=us-central1

# Delete service account
gcloud iam service-accounts delete github-actions@$PROJECT_ID.iam.gserviceaccount.com
```

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Cloud Run logs
3. Check GitHub Actions workflow logs
4. Verify all secrets and environment variables are set correctly


