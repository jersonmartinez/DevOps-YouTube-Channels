# Environment Setup for GitHub Actions

This document explains how to set up the required environment variables and secrets for the GitHub Actions workflows.

## Link Validation Environment

The link validation workflow requires a specific environment called `link-validation` to be set up with the following secrets:

### Required Secrets

1. `YOUTUBE_API_KEY`
   - Required for validating YouTube channel links
   - Get it from [Google Cloud Console](https://console.cloud.google.com/)
   - Enable the YouTube Data API v3
   - Create credentials > API Key

2. `LINKEDIN_TOKEN` (Optional)
   - Used for validating LinkedIn profile links
   - Get it from [LinkedIn Developer Portal](https://www.linkedin.com/developers/)
   - Create a new app
   - Request the `r_liteprofile` scope
   - Generate an access token

### Setting up the Environment

1. Go to your repository settings
2. Navigate to Environments
3. Click "New environment"
4. Name it `link-validation`
5. Add the required secrets
6. Configure environment protection rules if needed

### Environment Variables

No additional environment variables are required. All configuration is handled through secrets.

## Permissions

The workflows require the following permissions:
- `contents: read` - For reading repository content
- `issues: write` - For creating issues when invalid links are found

These permissions are automatically configured in the workflow files.
