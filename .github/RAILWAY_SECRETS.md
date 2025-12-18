# Railway GitHub Secrets Configuration

This document explains the required GitHub Secrets for the Railway deployment workflow.

## Required Secrets

To enable automatic deployment to Railway via GitHub Actions, you need to configure the following secrets in your GitHub repository settings (Settings → Secrets and variables → Actions):

### 1. RAILWAY_TOKEN
- **Description**: Your Railway project token for authentication
- **How to get it**:
  1. Go to your Railway project dashboard
  2. Navigate to Settings → Tokens
  3. Click "Create Token"
  4. Copy the generated token
- **Example**: `8f6d3a48-3760-4b06-9c61-f6fe51f63367`

### 2. RAILWAY_SERVICE_BACKEND
- **Description**: The service ID for the backend service
- **How to get it**:
  1. Go to your Railway project dashboard
  2. Click on your backend service
  3. The service ID is in the URL: `railway.app/project/{PROJECT_ID}/service/{SERVICE_ID}`
  4. Copy the SERVICE_ID part
- **Example**: `bc8cb3dc-e9c5-4fdb-b720-5049446d5a06`

### 3. RAILWAY_SERVICE_FRONTEND
- **Description**: The service ID for the frontend service
- **How to get it**:
  1. Go to your Railway project dashboard
  2. Click on your frontend service
  3. The service ID is in the URL: `railway.app/project/{PROJECT_ID}/service/{SERVICE_ID}`
  4. Copy the SERVICE_ID part
- **Example**: Similar format to backend service ID

## How to Add Secrets

1. Go to your GitHub repository
2. Click on **Settings** tab
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Add each secret with the name and value as specified above

## Verification

After adding the secrets, the next push to the `main` branch will automatically trigger the deployment workflow. You can monitor the deployment progress in the **Actions** tab of your GitHub repository.

## Troubleshooting

- If deployment fails with "Deploy failed", verify that:
  - All three secrets are correctly configured
  - The RAILWAY_TOKEN is valid and has not expired
  - The service IDs match your Railway project services
  - The Railway project is properly configured with the correct root directories (`/backend` and `/frontend`)

## Security Notes

- Never commit tokens or service IDs directly in the repository
- Rotate the RAILWAY_TOKEN periodically for security
- Use GitHub's secret management to keep credentials secure
