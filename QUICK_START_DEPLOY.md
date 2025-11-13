# Quick Start: Deploy to GCP

## Prerequisites Checklist

- [ ] Google Cloud account with billing enabled
- [ ] `gcloud` CLI installed: https://cloud.google.com/sdk/docs/install
- [ ] GitHub repository created
- [ ] Authenticated with GCP: `gcloud auth login`

## Step-by-Step Deployment

### 1. Initial Setup (One-time)

```bash
# Set your GCP project ID
export GCP_PROJECT_ID=your-project-id

# Run the setup script
chmod +x scripts/setup-gcp.sh
./scripts/setup-gcp.sh
```

**What this does:**
- Creates Cloud SQL database
- Creates Artifact Registry for Docker images
- Creates secrets in Secret Manager
- Creates service account for GitHub Actions
- Automatically enables service account key creation (if needed)
- Generates `gcp-service-account-key.json`

**Important:** The script will output:
- Database password (save it!)
- Service account key file location

### 2. Configure GitHub Secrets

1. Go to: `https://github.com/YOUR_USERNAME/llm-aggregator/settings/secrets/actions`
2. Click **"New repository secret"**
3. Add these two secrets:

   **Secret 1:**
   - Name: `GCP_PROJECT_ID`
   - Value: `your-project-id` (same as above)

   **Secret 2:**
   - Name: `GCP_SA_KEY`
   - Value: Copy the entire content of `gcp-service-account-key.json`
     ```bash
     cat gcp-service-account-key.json
     # Copy everything including { and }
     ```

### 3. Deploy!

```bash
# Commit and push to main branch
git add .
git commit -m "Setup GCP deployment"
git push origin main
```

**GitHub Actions will automatically:**
- Build Docker images
- Push to Artifact Registry
- Deploy to Cloud Run

**Monitor deployment:**
- Go to: `https://github.com/YOUR_USERNAME/llm-aggregator/actions`
- Watch the workflow run (takes ~5-10 minutes)

### 4. Get Your URLs

After deployment completes:

```bash
# Get frontend URL
gcloud run services describe llm-aggregator-frontend \
  --region=us-central1 --format='value(status.url)'

# Get backend URL
gcloud run services describe llm-aggregator-backend \
  --region=us-central1 --format='value(status.url)'
```

### 5. Update CORS (Important!)

After first deployment, update backend CORS to allow your frontend:

```bash
# Get frontend URL
FRONTEND_URL=$(gcloud run services describe llm-aggregator-frontend \
  --region=us-central1 --format='value(status.url)')

# Update backend CORS
gcloud run services update llm-aggregator-backend \
  --region=us-central1 \
  --update-env-vars="CORS_ORIGINS=$FRONTEND_URL"
```

### 6. Test Your Deployment

1. Open your frontend URL in a browser
2. Register a new account
3. Check email for verification (if SMTP configured)
4. Login and test!

## Troubleshooting

### Deployment Failed?

1. Check GitHub Actions logs
2. Verify secrets are set correctly
3. Check service account permissions

### Can't Connect to Database?

```bash
# Test database connection
gcloud sql connect llm-aggregator-db --user=llm_user
```

### Frontend Shows Errors?

1. Check browser console
2. Verify backend URL is correct
3. Check CORS is configured

## Next Steps

- Configure email (SMTP) for verification emails
- Set up custom domain (optional)
- Monitor costs in GCP Console
- Set up alerts for errors

## Cost

- **Free tier:** 2M Cloud Run requests/month
- **Database:** ~$7/month (db-f1-micro)
- **Total:** ~$7/month for low traffic

## Need Help?

See `DEPLOYMENT.md` for detailed documentation.


