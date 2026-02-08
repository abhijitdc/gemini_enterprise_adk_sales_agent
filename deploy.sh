#!/bin/bash
set -e

# Cleanup artifacts
echo "Cleaning up __pycache__ and .venv..."
rm -rf .venv
find . -type d -name "__pycache__" -exec rm -rf {} +

# Load configuration from .env
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# Check for required variables
if [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
  echo "Error: GOOGLE_CLOUD_PROJECT is not set in .env or environment."
  exit 1
fi

if [ -z "$GOOGLE_CLOUD_LOCATION" ]; then
  echo "Error: GOOGLE_CLOUD_LOCATION is not set in .env or environment."
  exit 1
fi

echo "Deploying to Project: $GOOGLE_CLOUD_PROJECT, Location: $GOOGLE_CLOUD_LOCATION"

# 1. Set Project
echo "Setting gcloud project..."
gcloud config set project "$GOOGLE_CLOUD_PROJECT"

# 2. Enable Required APIs
echo "Enabling required APIs..."
gcloud services enable \
  discoveryengine.googleapis.com \
  dialogflow.googleapis.com \
  aiplatform.googleapis.com \
  cloudaicompanion.googleapis.com \
  telemetry.googleapis.com

# 3. Create Agent Engine Instance (if needed) & Deploy
# Note: adk deploy agent_engine handles app creation if it doesn't exist, 
# provided the necessary permissions and APIs are active.
echo "Deploying Agent..."

# Install dependencies if needed (ensure adk is available)
# Assumes running in uv environment or adk is installed
DEPLOY_CMD="uv run adk deploy agent_engine sales_agent --env_file .env"

if [ -n "$AGENT_ENGINE_ID" ]; then
  echo "Updating existing Agent Engine: $AGENT_ENGINE_ID"
  DEPLOY_CMD="$DEPLOY_CMD --agent_engine_id $AGENT_ENGINE_ID"
fi

echo "Executing deployment..."
$DEPLOY_CMD

echo "Deployment complete!"
