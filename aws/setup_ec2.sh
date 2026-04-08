#!/bin/bash
# =============================================================================
# VirusTotal Data Pipeline — EC2 Setup Script
# =============================================================================
# This script prepares an Amazon Linux 2023 instance for the pipeline.
# =============================================================================

set -e

echo "🚀 Starting EC2 Setup..."

# 1. Update system
echo "📦 Updating system packages..."
sudo dnf update -y

# 2. Install Docker
echo "🐳 Installing Docker..."
sudo dnf install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# 3. Install Docker Compose
echo "🐙 Installing Docker Compose..."
DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
mkdir -p $DOCKER_CONFIG/cli-plugins
curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose
chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose

# 4. Install Git
echo "📂 Installing Git..."
sudo dnf install -y git

# 5. Create App Directory
echo "📁 Creating app directory..."
mkdir -p ~/virustotal-pipeline
sudo chown $USER:$USER ~/virustotal-pipeline

echo "=================================================="
echo " ✅ EC2 Setup Complete!"
echo " Please LOG OUT and LOG BACK IN for Docker permissions to take effect."
echo "=================================================="
