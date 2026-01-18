# CI/CD Pipeline Documentation

This document explains the continuous integration and deployment pipeline for the HealthCast application.

## Overview

The pipeline automatically builds, tests, and deploys the application to Google Cloud Platform (GCP) whenever code is pushed to the `main` branch.

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Push to   │────▶│  Run Tests  │────▶│ Build & Push│────▶│  Deploy to  │
│    main     │     │             │     │   Docker    │     │     GCE     │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

## Pipeline Stages

### 1. Test (`test` job)

Runs automated tests to verify code quality.

**Steps:**
1. Checkout code from repository
2. Set up Python 3.12
3. Install dependencies from `requirements.txt`
4. Install test dependencies (pytest, pytest-asyncio, httpx)
5. Run unit tests
6. Run integration tests

**Trigger:** Runs on every push to `main` or manual trigger.

### 2. Build and Push (`build-and-push` job)

Builds a production Docker image and pushes it to GCP Artifact Registry.

**Steps:**
1. Checkout code
2. Authenticate to Google Cloud using service account
3. Configure Docker for Artifact Registry
4. Build Docker image using `Dockerfile.prod`
5. Tag image with commit SHA and `latest`
6. Push both tags to Artifact Registry

**Image location:** `<REGION>-docker.pkg.dev/<PROJECT_ID>/<REPO>/healthcast`

**Depends on:** `test` job must pass first.

### 3. Deploy (`deploy` job)

Deploys the new image to the GCP Compute Engine VM.

**Steps:**
1. Authenticate to Google Cloud
2. SSH into the GCE instance
3. Pull the latest Docker image
4. Stop and remove the existing container
5. Start a new container with the updated image
6. Clean up old images
7. Verify deployment via health check

**Depends on:** `build-and-push` job must complete first.

## Required GitHub Secrets

Configure these in your repository: **Settings → Secrets and variables → Actions**

| Secret | Description | Example |
|--------|-------------|---------|
| `GCP_PROJECT_ID` | Your GCP project ID | `my-project-123` |
| `GCP_REGION` | GCP region for Artifact Registry | `us-central1` |
| `GCE_INSTANCE` | Compute Engine VM name | `healthcast-vm` |
| `GCE_INSTANCE_ZONE` | VM zone | `us-central1-a` |
| `GCP_ARTIFACT_REPO` | Artifact Registry repository name | `healthcast-repo` |
| `GCP_SA_KEY` | Service account JSON key (full contents) | `{"type": "service_account", ...}` |

## Triggering Deployments

### Automatic Deployment
Push to the `main` branch:
```bash
git push origin main
```

### Manual Deployment
1. Go to **Actions** tab in GitHub
2. Select "Build and Deploy to GCP"
3. Click "Run workflow"
4. Select the branch and click "Run workflow"

## GCP Infrastructure Requirements

### Compute Engine VM
- The VM must have Docker installed
- The VM must have the `gcloud` CLI configured
- The VM service account needs permission to pull from Artifact Registry

### Artifact Registry
- Create a Docker repository in your chosen region
- Grant the deployment service account `Artifact Registry Writer` role

### Service Account Permissions
The deployment service account needs:
- `roles/artifactregistry.writer` - Push images to registry
- `roles/compute.instanceAdmin.v1` - SSH into VM
- `roles/compute.osLogin` - OS Login access
- `roles/iap.tunnelResourceAccessor` - IAP tunnel access (if using IAP)

## Container Configuration

The deployed container runs with:
- **Port mapping:** `80:5050` (external:internal)
- **Restart policy:** `unless-stopped`
- **Environment:** `APP_ENV=production`

## Monitoring Deployments

### Check GitHub Actions
View pipeline status at: `https://github.com/<owner>/<repo>/actions`

### Check Container Status
```bash
gcloud compute ssh <INSTANCE_NAME> --zone=<ZONE> --command="docker ps"
```

### View Container Logs
```bash
gcloud compute ssh <INSTANCE_NAME> --zone=<ZONE> --command="docker logs healthcast"
```

### Health Check
```bash
curl http://<INSTANCE_IP>/health
```

## Rollback

To rollback to a previous version:

1. Find the commit SHA of the working version
2. Pull and run that specific image:

```bash
gcloud compute ssh <INSTANCE_NAME> --zone=<ZONE> --command="
  docker stop healthcast
  docker rm healthcast
  docker run -d \
    --name healthcast \
    --restart unless-stopped \
    -p 80:5050 \
    -e APP_ENV=production \
    <REGISTRY>/<PROJECT>/<REPO>/healthcast:<COMMIT_SHA>
"
```

## Troubleshooting

### Pipeline fails at test stage
- Check test output in GitHub Actions logs
- Run tests locally: `./scripts/test.sh`

### Pipeline fails at build stage
- Verify GCP credentials are correct
- Check Artifact Registry permissions
- Ensure Dockerfile.prod builds locally

### Pipeline fails at deploy stage
- Verify VM is running
- Check VM has Docker installed
- Verify service account can SSH to VM
- Check firewall rules allow SSH (port 22)

### Health check fails after deployment
- Wait longer for the app to start (ML models take time to load)
- Check container logs for errors
- Verify port 80 is open in GCP firewall
