#!/usr/bin/env bash
# =============================================================================
# VirusTotal Data Pipeline — AWS ECS Fargate Deployment Script
# =============================================================================
# Usage:
#   chmod +x aws/deploy.sh
#   ./aws/deploy.sh
#
# Prerequisites (run ONCE before this script):
#   1. Install AWS CLI: brew install awscli
#   2. Configure credentials: aws configure
#   3. Set variables in the CONFIG section below
# =============================================================================

set -euo pipefail

# ─── CONFIG ──────────────────────────────────────────────────────────────────
AWS_REGION="us-east-1"                  # Change to your preferred region
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
CLUSTER_NAME="virustotal-pipeline"
ECR_BACKEND="virustotal-pipeline/backend"
ECR_FRONTEND="virustotal-pipeline/frontend"
VT_SECRET_NAME="virustotal/api-key"     # Name in AWS Secrets Manager
EFS_MOUNT_TARGET_DIR="/app/data"
# ─────────────────────────────────────────────────────────────────────────────

ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
BACKEND_IMAGE="${ECR_REGISTRY}/${ECR_BACKEND}:latest"
FRONTEND_IMAGE="${ECR_REGISTRY}/${ECR_FRONTEND}:latest"

echo "=================================================="
echo " VirusTotal Pipeline — AWS Deployment"
echo " Account : ${AWS_ACCOUNT_ID}"
echo " Region  : ${AWS_REGION}"
echo "=================================================="

# ─── Step 1: Ensure ECR Repositories Exist ───────────────────────────────────
echo ""
echo "[1/8] Creating ECR repositories (if not exist)..."
aws ecr describe-repositories --repository-names "${ECR_BACKEND}" --region "${AWS_REGION}" 2>/dev/null || \
    aws ecr create-repository --repository-name "${ECR_BACKEND}" --region "${AWS_REGION}"
aws ecr describe-repositories --repository-names "${ECR_FRONTEND}" --region "${AWS_REGION}" 2>/dev/null || \
    aws ecr create-repository --repository-name "${ECR_FRONTEND}" --region "${AWS_REGION}"

# ─── Step 2: Authenticate Docker to ECR ──────────────────────────────────────
echo ""
echo "[2/8] Authenticating Docker to ECR..."
aws ecr get-login-password --region "${AWS_REGION}" | \
    docker login --username AWS --password-stdin "${ECR_REGISTRY}"

# ─── Step 3: Build & Push Backend Image ──────────────────────────────────────
echo ""
echo "[3/8] Building & pushing backend image..."
cd "$(dirname "$0")/.."
docker build --platform linux/amd64 -t "${BACKEND_IMAGE}" -f Dockerfile .
docker push "${BACKEND_IMAGE}"
echo "✅ Backend image pushed: ${BACKEND_IMAGE}"

# ─── Step 4: Build & Push Frontend Image ─────────────────────────────────────
echo ""
echo "[4/8] Building & pushing frontend image..."
docker build --platform linux/amd64 -t "${FRONTEND_IMAGE}" -f frontend/Dockerfile ./frontend
docker push "${FRONTEND_IMAGE}"
echo "✅ Frontend image pushed: ${FRONTEND_IMAGE}"

# ─── Step 5: Store VT_API_KEY in Secrets Manager (interactive) ───────────────
echo ""
echo "[5/8] Checking for VT_API_KEY in Secrets Manager..."
if ! aws secretsmanager describe-secret --secret-id "${VT_SECRET_NAME}" --region "${AWS_REGION}" 2>/dev/null; then
    echo "Secret not found. Creating it now..."
    read -rsp "Enter your VirusTotal API Key: " VT_KEY
    echo ""
    aws secretsmanager create-secret \
        --name "${VT_SECRET_NAME}" \
        --secret-string "{\"VT_API_KEY\":\"${VT_KEY}\"}" \
        --region "${AWS_REGION}"
    echo "✅ Secret stored: ${VT_SECRET_NAME}"
else
    echo "✅ Secret already exists: ${VT_SECRET_NAME}"
fi

# ─── Step 6: Create ECS Cluster ──────────────────────────────────────────────
echo ""
echo "[6/8] Creating ECS cluster (if not exist)..."
aws ecs describe-clusters --clusters "${CLUSTER_NAME}" --region "${AWS_REGION}" | \
    python3 -c "import sys,json; clusters=json.load(sys.stdin)['clusters']; exit(0 if clusters and clusters[0]['status']=='ACTIVE' else 1)" 2>/dev/null || \
    aws ecs create-cluster --cluster-name "${CLUSTER_NAME}" \
        --capacity-providers FARGATE \
        --region "${AWS_REGION}"
echo "✅ Cluster ready: ${CLUSTER_NAME}"

# ─── Step 7: Register Task Definitions ───────────────────────────────────────
echo ""
echo "[7/8] Registering ECS task definitions..."

# Substitute placeholders in task definitions
sed \
    -e "s/ACCOUNT_ID/${AWS_ACCOUNT_ID}/g" \
    -e "s/REGION/${AWS_REGION}/g" \
    aws/task-definition-backend.json > /tmp/td-backend-rendered.json

sed \
    -e "s/ACCOUNT_ID/${AWS_ACCOUNT_ID}/g" \
    -e "s/REGION/${AWS_REGION}/g" \
    aws/task-definition-frontend.json > /tmp/td-frontend-rendered.json

aws ecs register-task-definition \
    --cli-input-json file:///tmp/td-backend-rendered.json \
    --region "${AWS_REGION}" > /dev/null
echo "✅ Backend task definition registered"

aws ecs register-task-definition \
    --cli-input-json file:///tmp/td-frontend-rendered.json \
    --region "${AWS_REGION}" > /dev/null
echo "✅ Frontend task definition registered"

# ─── Step 8: Print Next Steps ────────────────────────────────────────────────
echo ""
echo "=================================================="
echo " ✅ Images pushed & task definitions registered!"
echo "=================================================="
echo ""
echo "NEXT MANUAL STEPS (do once in AWS Console or CLI):"
echo ""
echo "  1. Create an EFS file system for SQLite persistence:"
echo "     https://console.aws.amazon.com/efs"
echo "     → Note the File System ID and update task-definition-backend.json"
echo ""
echo "  2. Create an Application Load Balancer (ALB):"
echo "     https://console.aws.amazon.com/ec2#LoadBalancers"
echo "     → Create two Target Groups: backend (port 8000), frontend (port 80)"
echo "     → Add listener rules: /api/* → backend, /* → frontend"
echo ""
echo "  3. Create ECS Services:"
echo "     aws ecs create-service \\"
echo "       --cluster ${CLUSTER_NAME} \\"
echo "       --service-name backend \\"
echo "       --task-definition vt-pipeline-backend \\"
echo "       --desired-count 1 \\"
echo "       --launch-type FARGATE \\"
echo "       --network-configuration 'awsvpcConfiguration={subnets=[SUBNET_ID],securityGroups=[SG_ID],assignPublicIp=ENABLED}' \\"
echo "       --load-balancers 'targetGroupArn=TG_ARN,containerName=backend,containerPort=8000' \\"
echo "       --region ${AWS_REGION}"
echo ""
echo "  4. Create CloudWatch Log Groups:"
echo "     aws logs create-log-group --log-group-name /ecs/vt-pipeline-backend --region ${AWS_REGION}"
echo "     aws logs create-log-group --log-group-name /ecs/vt-pipeline-frontend --region ${AWS_REGION}"
echo ""
echo "  5. Test your deployment:"
echo "     curl http://<your-alb-dns>/health"
echo "     curl http://<your-alb-dns>/api/v1/domains/google.com"
echo ""
