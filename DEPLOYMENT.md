# EcoPilot 部署指南

## 📋 目录

1. [本地开发](#本地开发)
2. [Docker 部署](#docker-部署)
3. [Google Cloud Run](#google-cloud-run)
4. [Kubernetes](#kubernetes)
5. [故障排除](#故障排除)

---

## 本地开发

### 快速启动

```bash
# 1. 克隆项目
git clone git@github.com:dongowu/EcoPilot.git
cd EcoPilot

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 GitLab token 和 webhook secret

# 5. 启动服务
uvicorn main:app --host 0.0.0.0 --port 8080 --reload

# 6. 测试
pytest -v
```

### 验证服务

```bash
# 检查健康状态
curl http://localhost:8080/health

# 应该返回：
# {"status":"ok"}
```

---

## Docker 部署

### 方式 1: Docker Compose（推荐）

```bash
# 1. 复制环境配置
cp .env.example .env

# 2. 编辑 .env，填入必要的环境变量
nano .env

# 3. 启动服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f ecopilot

# 5. 停止服务
docker-compose down
```

### 方式 2: 直接 Docker

```bash
# 1. 构建镜像
docker build -t ecopilot:latest .

# 2. 运行容器
docker run -d \
  --name ecopilot \
  -p 8080:8080 \
  -e ECOPILOT_WEBHOOK_SECRET=your-secret \
  -e ECOPILOT_GITLAB_TOKEN=your-token \
  ecopilot:latest

# 3. 查看日志
docker logs -f ecopilot

# 4. 停止容器
docker stop ecopilot
docker rm ecopilot
```

### Docker 镜像优化

```bash
# 查看镜像大小
docker images ecopilot

# 多阶段构建已优化，大小约 200-300MB
```

---

## Google Cloud Run

### 前置条件

```bash
# 1. 安装 gcloud CLI
# https://cloud.google.com/sdk/docs/install

# 2. 初始化 gcloud
gcloud init

# 3. 设置项目
gcloud config set project YOUR_PROJECT_ID
```

### 部署步骤

```bash
# 1. 设置环境变量
export GCP_PROJECT=your-project-id
export REGION=us-central1
export WEBHOOK_SECRET=your-webhook-secret
export GITLAB_TOKEN=your-gitlab-token

# 2. 构建并推送镜像到 Container Registry
gcloud builds submit --tag gcr.io/${GCP_PROJECT}/ecopilot:latest

# 3. 部署到 Cloud Run
gcloud run deploy ecopilot \
  --image gcr.io/${GCP_PROJECT}/ecopilot:latest \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --set-env-vars ECOPILOT_WEBHOOK_SECRET=${WEBHOOK_SECRET} \
  --set-env-vars ECOPILOT_GITLAB_TOKEN=${GITLAB_TOKEN} \
  --set-env-vars ECOPILOT_GITLAB_BASE_URL=https://gitlab.com/api/v4 \
  --set-env-vars ECOPILOT_RUNNER_COST_PER_MIN=0.008 \
  --set-env-vars ECOPILOT_CARBON_KG_PER_MIN=0.02 \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300

# 4. 获取服务 URL
gcloud run services describe ecopilot --region ${REGION} --format 'value(status.url)'
```

### 配置 GitLab Webhook

```bash
# 1. 获取 Cloud Run URL
SERVICE_URL=$(gcloud run services describe ecopilot --region ${REGION} --format 'value(status.url)')

# 2. 在 GitLab 项目中配置 webhook
# Settings → Webhooks
# URL: ${SERVICE_URL}/webhook/gitlab/mr
# Secret: ${WEBHOOK_SECRET}
# Trigger: Merge request events
```

### 可选：添加 BigQuery 集成

```bash
# 1. 创建 BigQuery 数据集
bq mk --dataset --location=US "${GCP_PROJECT}:ecopilot"

# 2. 创建表（使用 schema.sql）
bq query --use_legacy_sql=false < infra/bigquery/schema.sql

# 3. 更新 Cloud Run 环境变量
gcloud run services update ecopilot \
  --region ${REGION} \
  --set-env-vars ECOPILOT_BIGQUERY_TABLE_ID=${GCP_PROJECT}.ecopilot.analysis_events \
  --set-env-vars ECOPILOT_GCP_PROJECT_ID=${GCP_PROJECT}
```

---

## Kubernetes

### 前置条件

```bash
# 1. 安装 kubectl
# https://kubernetes.io/docs/tasks/tools/

# 2. 配置 kubeconfig
kubectl config use-context your-cluster
```

### 部署配置

创建 `k8s/deployment.yaml`：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ecopilot
  labels:
    app: ecopilot
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ecopilot
  template:
    metadata:
      labels:
        app: ecopilot
    spec:
      containers:
      - name: ecopilot
        image: gcr.io/YOUR_PROJECT/ecopilot:latest
        ports:
        - containerPort: 8080
        env:
        - name: ECOPILOT_WEBHOOK_SECRET
          valueFrom:
            secretKeyRef:
              name: ecopilot-secrets
              key: webhook-secret
        - name: ECOPILOT_GITLAB_TOKEN
          valueFrom:
            secretKeyRef:
              name: ecopilot-secrets
              key: gitlab-token
        - name: ECOPILOT_GITLAB_BASE_URL
          value: "https://gitlab.com/api/v4"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: ecopilot-service
spec:
  selector:
    app: ecopilot
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: LoadBalancer
```

### 部署步骤

```bash
# 1. 创建 secret
kubectl create secret generic ecopilot-secrets \
  --from-literal=webhook-secret=your-secret \
  --from-literal=gitlab-token=your-token

# 2. 部署应用
kubectl apply -f k8s/deployment.yaml

# 3. 查看部署状态
kubectl get deployments
kubectl get pods
kubectl get services

# 4. 查看日志
kubectl logs -f deployment/ecopilot

# 5. 获取外部 IP
kubectl get service ecopilot-service
```

---

## 故障排除

### 常见问题

#### 1. Webhook 验证失败

```bash
# 检查 secret 是否正确
echo $ECOPILOT_WEBHOOK_SECRET

# 查看日志
docker logs ecopilot | grep -i webhook
```

#### 2. GitLab API 错误

```bash
# 验证 token
curl -H "PRIVATE-TOKEN: ${ECOPILOT_GITLAB_TOKEN}" \
  https://gitlab.com/api/v4/user

# 检查 token 权限（需要 api 和 read_repository）
```

#### 3. 内存不足

```bash
# 增加内存限制
docker run -m 1g ecopilot:latest

# 或在 docker-compose.yml 中
services:
  ecopilot:
    mem_limit: 1g
```

#### 4. 端口被占用

```bash
# 查找占用 8080 的进程
lsof -i :8080

# 使用不同的端口
docker run -p 9000:8080 ecopilot:latest
```

### 调试模式

```bash
# 启用详细日志
docker run -e LOG_LEVEL=DEBUG ecopilot:latest

# 或在本地开发中
uvicorn main:app --log-level debug
```

---

## 性能优化

### 生产环境建议

```yaml
# docker-compose.yml
services:
  ecopilot:
    # 使用多个 worker
    command: uvicorn main:app --host 0.0.0.0 --port 8080 --workers 4

    # 增加资源限制
    mem_limit: 1g
    cpus: 1.0

    # 配置日志
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 监控

```bash
# 使用 Prometheus 导出指标
pip install prometheus-client

# 在 main.py 中添加
from prometheus_client import Counter, Histogram
```

---

## 更新和维护

### 更新镜像

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 重新构建镜像
docker build -t ecopilot:latest .

# 3. 重启容器
docker-compose down
docker-compose up -d
```

### 备份数据

```bash
# 备份 BigQuery 数据
bq extract ecopilot.analysis_events gs://your-bucket/backup/analysis_events_*.json

# 备份配置
docker exec ecopilot env > ecopilot-config-backup.env
```

---

## 支持

- 📖 [README](../README.md)
- 🐛 [GitHub Issues](https://github.com/dongowu/EcoPilot/issues)
- 💬 [GitLab Discussions](https://gitlab.com/gitlab-ai-hackathon/participants/4363635/-/discussions)
