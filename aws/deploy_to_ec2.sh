#!/bin/bash
# =============================================================================
# VirusTotal Data Pipeline — EC2 Deployment Script
# =============================================================================
# Usage:
#   chmod +x aws/deploy_to_ec2.sh
#   ./aws/deploy_to_ec2.sh <path-to-your-key.pem>
# =============================================================================

set -e

KEY_FILE=$1
# Priority: 1. Command-line arg, 2. Env var, 3. Hardcoded default
EC2_IP=${2:-${EC2_IP:-"44.222.171.147"}}
EC2_USER="ec2-user"
REMOTE_PATH="~/virustotal-pipeline"

if [ -z "$KEY_FILE" ]; then
    echo "❌ Error: Please provide the path to your .pem key file."
    echo "Usage: $0 <key-file.pem>"
    exit 1
fi

echo "🚀 Starting Deployment to $EC2_IP..."

# 1. Sync files (excluding unnecessary ones)
echo "📂 Syncing files to EC2..."
rsync -avz -e "ssh -i $KEY_FILE" \
    --exclude '.git' \
    --exclude 'venv' \
    --exclude '__pycache__' \
    --exclude 'node_modules' \
    --exclude 'frontend/dist' \
    ./ $EC2_USER@$EC2_IP:$REMOTE_PATH

# 2. Run Docker Compose on the remote server
echo "🐳 Building and starting containers on EC2..."
ssh -i $KEY_FILE $EC2_USER@$EC2_IP << EOF
    cd $REMOTE_PATH
    docker compose up -d --build
EOF

echo "=================================================="
echo " ✅ Deployment Complete!"
echo " Access your pipeline at: http://$EC2_IP"
echo "=================================================="
