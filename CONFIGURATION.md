# EcoPilot 配置指南

完整的环境变量配置和数据获取方法。

---

## 📋 配置项总览

| 配置项 | 必需 | 说明 | 获取难度 |
|--------|------|------|--------|
| `ECOPILOT_WEBHOOK_SECRET` | ✅ | Webhook 验证密钥 | ⭐ 简单 |
| `ECOPILOT_GITLAB_TOKEN` | ✅ | GitLab API 访问令牌 | ⭐ 简单 |
| `ECOPILOT_GITLAB_BASE_URL` | ❌ | GitLab API 地址 | ⭐ 简单 |
| `ECOPILOT_RUNNER_COST_PER_MIN` | ❌ | 每分钟 runner 成本 | ⭐⭐ 中等 |
| `ECOPILOT_CARBON_KG_PER_MIN` | ❌ | 每分钟碳排放量 | ⭐⭐ 中等 |
| `ECOPILOT_DUO_ANTHROPIC_URL` | ❌ | Anthropic API 端点 | ⭐⭐⭐ 复杂 |
| `ECOPILOT_DUO_ANTHROPIC_TOKEN` | ❌ | Anthropic API 密钥 | ⭐⭐⭐ 复杂 |
| `ECOPILOT_DUO_ANTHROPIC_MODEL` | ❌ | Anthropic 模型名称 | ⭐ 简单 |
| `ECOPILOT_GCP_PROJECT_ID` | ❌ | GCP 项目 ID | ⭐⭐ 中等 |
| `ECOPILOT_BIGQUERY_TABLE_ID` | ❌ | BigQuery 表 ID | ⭐⭐⭐ 复杂 |
| `ECOPILOT_GCP_BILLING_TABLE_ID` | ❌ | GCP 账单表 ID | ⭐⭐⭐ 复杂 |
| `ECOPILOT_ENABLE_AUTO_LABEL` | ❌ | 自动打标签 | ⭐ 简单 |
| `ECOPILOT_ENABLE_AUTO_ISSUE` | ❌ | 自动创建 issue | ⭐ 简单 |

---

## 🔴 必需配置

### 1. ECOPILOT_WEBHOOK_SECRET

**用途**: 验证来自 GitLab 的 webhook 请求

**获取方法**:

```bash
# 方法 1: 生成随机密钥（推荐）
openssl rand -hex 32

# 输出示例:
# a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2

# 方法 2: 使用 Python
python -c "import secrets; print(secrets.token_hex(32))"

# 方法 3: 使用 UUID
python -c "import uuid; print(str(uuid.uuid4()).replace('-', ''))"
```

**配置步骤**:

```bash
# 1. 生成密钥
WEBHOOK_SECRET=$(openssl rand -hex 32)
echo $WEBHOOK_SECRET

# 2. 保存到 .env
echo "ECOPILOT_WEBHOOK_SECRET=$WEBHOOK_SECRET" >> .env

# 3. 在 GitLab 中配置
# 项目 → Settings → Webhooks
# Secret token: 粘贴上面的密钥
```

**验证**:

```bash
# 测试 webhook 签名
curl -X POST http://localhost:8080/webhook/gitlab/mr \
  -H "X-Gitlab-Token: $WEBHOOK_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"object_kind":"merge_request"}'
```

---

### 2. ECOPILOT_GITLAB_TOKEN

**用途**: 访问 GitLab API，读取 CI 配置和 pipeline 数据

**获取方法**:

#### 步骤 1: 登录 GitLab

访问 https://gitlab.com (或你的 GitLab 实例)

#### 步骤 2: 创建个人访问令牌

```
GitLab 右上角 → 头像 → Preferences → Access Tokens
```

或直接访问: https://gitlab.com/-/user_settings/personal_access_tokens

#### 步骤 3: 配置令牌

| 字段 | 值 |
|------|-----|
| Token name | `ecopilot-service` |
| Expiration date | 选择 90 天或更长 |
| Scopes | ✅ `api` ✅ `read_repository` |

**截图示例**:
```
┌─────────────────────────────────────┐
│ Create Personal Access Token        │
├─────────────────────────────────────┤
│ Token name: ecopilot-service        │
│ Expiration date: 2026-06-19         │
│ Scopes:                             │
│  ☑ api                              │
│  ☑ read_repository                  │
│  ☐ read_user                        │
│  ☐ write_repository                 │
│                                     │
│ [Create personal access token]      │
└─────────────────────────────────────┘
```

#### 步骤 4: 复制令牌

```bash
# 复制生成的令牌（只显示一次！）
# 示例: glpat-aBcDeFgHiJkLmNoPqRsT

# 保存到 .env
echo "ECOPILOT_GITLAB_TOKEN=glpat-aBcDeFgHiJkLmNoPqRsT" >> .env
```

**验证**:

```bash
# 测试 token 是否有效
curl -H "PRIVATE-TOKEN: $ECOPILOT_GITLAB_TOKEN" \
  https://gitlab.com/api/v4/user

# 应该返回你的用户信息
# {
#   "id": 12345,
#   "username": "your-username",
#   "name": "Your Name",
#   ...
# }
```

**权限检查**:

```bash
# 验证 token 有 api 权限
curl -H "PRIVATE-TOKEN: $ECOPILOT_GITLAB_TOKEN" \
  https://gitlab.com/api/v4/projects/YOUR_PROJECT_ID

# 验证 token 有 read_repository 权限
curl -H "PRIVATE-TOKEN: $ECOPILOT_GITLAB_TOKEN" \
  https://gitlab.com/api/v4/projects/YOUR_PROJECT_ID/repository/files/.gitlab-ci.yml?ref=main
```

---

## 🟡 可选但推荐配置

### 3. ECOPILOT_GITLAB_BASE_URL

**用途**: 指定 GitLab 实例地址

**默认值**: `https://gitlab.com/api/v4`

**配置**:

```bash
# GitLab.com（默认）
ECOPILOT_GITLAB_BASE_URL=https://gitlab.com/api/v4

# 自托管 GitLab
ECOPILOT_GITLAB_BASE_URL=https://gitlab.your-company.com/api/v4

# 本地开发
ECOPILOT_GITLAB_BASE_URL=http://localhost:8000/api/v4
```

**验证**:

```bash
# 测试连接
curl -H "PRIVATE-TOKEN: $ECOPILOT_GITLAB_TOKEN" \
  ${ECOPILOT_GITLAB_BASE_URL}/user
```

---

### 4. ECOPILOT_RUNNER_COST_PER_MIN

**用途**: 计算 CI runner 成本

**默认值**: `0.008` (每分钟 $0.008)

**如何获取**:

#### 方法 1: 使用 GitLab 官方定价

```bash
# GitLab.com 共享 runner 成本
# 参考: https://about.gitlab.com/pricing/

# Linux runner: $0.008/分钟
# Windows runner: $0.016/分钟
# macOS runner: $0.03/分钟

ECOPILOT_RUNNER_COST_PER_MIN=0.008
```

#### 方法 2: 计算自托管 runner 成本

```bash
# 假设：
# - 服务器成本: $500/月
# - 月工作时间: 160 小时 = 9,600 分钟
# - 成本/分钟 = $500 / 9,600 = $0.052/分钟

ECOPILOT_RUNNER_COST_PER_MIN=0.052
```

#### 方法 3: 从 GCP 账单反推

```bash
# 如果使用 GCP Compute Engine 作为 runner
# 1. 查看 GCP 账单
# 2. 计算月成本
# 3. 除以月工作分钟数

# 示例: $100/月 ÷ 9,600 分钟 = $0.0104/分钟
ECOPILOT_RUNNER_COST_PER_MIN=0.0104
```

**验证**:

```bash
# 测试成本计算
# 假设 pipeline 运行 10 分钟
# 成本 = 10 * 0.008 = $0.08

python -c "
cost_per_min = 0.008
duration_min = 10
total_cost = cost_per_min * duration_min
print(f'10 分钟 pipeline 成本: \${total_cost:.4f}')
"
```

---

### 5. ECOPILOT_CARBON_KG_PER_MIN

**用途**: 计算 CI 碳排放量

**默认值**: `0.02` (每分钟 0.02 kg CO2e)

**如何获取**:

#### 方法 1: 使用行业平均值

```bash
# 数据中心平均碳排放: 0.2-0.4 kg CO2e/kWh
# 假设 runner 功耗: 100W = 0.1 kW
# 碳排放 = 0.1 kW * 0.3 kg CO2e/kWh / 60 分钟
#        = 0.0005 kg CO2e/分钟

# 但考虑到冷却、网络等开销，通常乘以 2-4 倍
# 最终: 0.002-0.002 kg CO2e/分钟

ECOPILOT_CARBON_KG_PER_MIN=0.02
```

#### 方法 2: 从云提供商数据

```bash
# Google Cloud 碳排放数据
# 参考: https://cloud.google.com/sustainability/region-carbon-footprints

# 美国中部: 0.15 kg CO2e/kWh
# 欧洲: 0.08 kg CO2e/kWh
# 假设 runner 100W，美国中部:
# 碳排放 = 0.1 kW * 0.15 kg CO2e/kWh / 60 分钟 * 2 (开销)
#        = 0.0005 kg CO2e/分钟

ECOPILOT_CARBON_KG_PER_MIN=0.0005
```

#### 方法 3: 使用 Scope 3 排放因子

```bash
# 参考 GHG Protocol
# 云计算排放因子: 0.0001-0.0005 kg CO2e/分钟

ECOPILOT_CARBON_KG_PER_MIN=0.0003
```

**验证**:

```bash
# 测试碳排放计算
python -c "
carbon_per_min = 0.02
duration_min = 10
total_carbon = carbon_per_min * duration_min
print(f'10 分钟 pipeline 碳排放: {total_carbon} kg CO2e')
print(f'相当于: {total_carbon * 1000:.1f} g CO2e')
"
```

---

## 🔵 高级配置（可选）

### 6. ECOPILOT_DUO_ANTHROPIC_URL

**用途**: 连接 GitLab Duo 的 Anthropic API

**获取方法**:

#### 前置条件

- 已注册 GitLab Duo 账户
- 已获得 Anthropic 集成权限

#### 步骤 1: 访问 GitLab Duo 控制面板

```
https://gitlab.com/admin/ai/anthropic
```

或在 GitLab 项目中:
```
Settings → Integrations → Anthropic
```

#### 步骤 2: 获取端点 URL

```bash
# GitLab 提供的 Anthropic 代理端点
# 格式: https://api.gitlab.com/ai/anthropic/v1/messages

ECOPILOT_DUO_ANTHROPIC_URL=https://api.gitlab.com/ai/anthropic/v1/messages
```

#### 步骤 3: 验证连接

```bash
# 测试 Anthropic 连接
curl -X POST $ECOPILOT_DUO_ANTHROPIC_URL \
  -H "Authorization: Bearer $ECOPILOT_DUO_ANTHROPIC_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 100,
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

---

### 7. ECOPILOT_DUO_ANTHROPIC_TOKEN

**用途**: Anthropic API 认证

**获取方法**:

#### 步骤 1: 登录 Anthropic 控制台

访问 https://console.anthropic.com

#### 步骤 2: 创建 API 密钥

```
Account → API Keys → Create Key
```

#### 步骤 3: 复制密钥

```bash
# 示例: sk-ant-v0-abc123def456...

ECOPILOT_DUO_ANTHROPIC_TOKEN=sk-ant-v0-abc123def456...
```

**验证**:

```bash
# 测试 API 密钥
curl -X POST https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ECOPILOT_DUO_ANTHROPIC_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 100,
    "messages": [{"role": "user", "content": "test"}]
  }'
```

---

### 8. ECOPILOT_DUO_ANTHROPIC_MODEL

**用途**: 指定使用的 Claude 模型

**可用模型**:

```bash
# 推荐（最新）
ECOPILOT_DUO_ANTHROPIC_MODEL=claude-sonnet-4-20250514

# 其他选项
ECOPILOT_DUO_ANTHROPIC_MODEL=claude-opus-4-20250514
ECOPILOT_DUO_ANTHROPIC_MODEL=claude-haiku-4-5-20251001
```

**选择建议**:

| 模型 | 速度 | 成本 | 推荐场景 |
|------|------|------|--------|
| Haiku | ⚡⚡⚡ | 💰 | 快速响应 |
| Sonnet | ⚡⚡ | 💰💰 | **平衡（推荐）** |
| Opus | ⚡ | 💰💰💰 | 复杂分析 |

---

### 9. ECOPILOT_GCP_PROJECT_ID

**用途**: 访问 GCP 资源（BigQuery、账单数据）

**获取方法**:

#### 步骤 1: 登录 Google Cloud Console

访问 https://console.cloud.google.com

#### 步骤 2: 查看项目 ID

```
顶部导航栏 → 项目选择器 → 复制项目 ID
```

或使用 gcloud CLI:

```bash
gcloud config get-value project
# 输出: my-project-id-12345
```

#### 步骤 3: 配置

```bash
ECOPILOT_GCP_PROJECT_ID=my-project-id-12345
```

**验证**:

```bash
# 测试 GCP 连接
gcloud config set project $ECOPILOT_GCP_PROJECT_ID
gcloud auth list
```

---

### 10. ECOPILOT_BIGQUERY_TABLE_ID

**用途**: 存储 EcoPilot 分析结果

**获取方法**:

#### 步骤 1: 创建 BigQuery 数据集

```bash
bq mk --dataset \
  --location=US \
  --description="EcoPilot analysis results" \
  ${ECOPILOT_GCP_PROJECT_ID}:ecopilot
```

#### 步骤 2: 创建表

```bash
# 使用 schema.sql（如果存在）
bq mk --table \
  ${ECOPILOT_GCP_PROJECT_ID}:ecopilot.analysis_events \
  schema.json

# 或手动创建
bq mk --table \
  ${ECOPILOT_GCP_PROJECT_ID}:ecopilot.analysis_events \
  event_id:STRING,project_id:INTEGER,mr_iid:INTEGER,findings:JSON,impact:JSON,timestamp:TIMESTAMP
```

#### 步骤 3: 配置

```bash
ECOPILOT_BIGQUERY_TABLE_ID=${ECOPILOT_GCP_PROJECT_ID}.ecopilot.analysis_events
```

**验证**:

```bash
# 查询表
bq query --use_legacy_sql=false \
  "SELECT * FROM \`${ECOPILOT_BIGQUERY_TABLE_ID}\` LIMIT 10"
```

---

### 11. ECOPILOT_GCP_BILLING_TABLE_ID

**用途**: 读取 GCP 账单数据，计算云成本节省

**获取方法**:

#### 步骤 1: 启用 BigQuery 导出

```
GCP Console → Billing → Billing Export to BigQuery
```

#### 步骤 2: 配置导出

```
Dataset: billing
Table: gcp_billing_export_v1_XXXXXX
```

#### 步骤 3: 获取表 ID

```bash
# 查看已导出的表
bq ls ${ECOPILOT_GCP_PROJECT_ID}:billing

# 输出示例:
# gcp_billing_export_v1_012345_6789AB_CDEF01

ECOPILOT_GCP_BILLING_TABLE_ID=${ECOPILOT_GCP_PROJECT_ID}.billing.gcp_billing_export_v1_012345_6789AB_CDEF01
```

**验证**:

```bash
# 查询账单数据
bq query --use_legacy_sql=false \
  "SELECT SUM(cost) as total_cost FROM \`${ECOPILOT_GCP_BILLING_TABLE_ID}\` LIMIT 1"
```

---

## 🟢 功能开关

### 12. ECOPILOT_ENABLE_AUTO_LABEL

**用途**: 自动为检测到浪费的 MR 打标签

**配置**:

```bash
# 启用
ECOPILOT_ENABLE_AUTO_LABEL=true

# 禁用（默认）
ECOPILOT_ENABLE_AUTO_LABEL=false
```

**效果**:

```
启用时，MR 会自动添加标签: ci-waste-detected
```

---

### 13. ECOPILOT_ENABLE_AUTO_ISSUE

**用途**: 自动为高严重性发现创建 issue

**配置**:

```bash
# 启用
ECOPILOT_ENABLE_AUTO_ISSUE=true

# 禁用（默认）
ECOPILOT_ENABLE_AUTO_ISSUE=false
```

**效果**:

```
启用时，如果发现高严重性问题，会自动创建 issue
```

---

## 📝 完整配置示例

### 最小配置（仅必需）

```bash
# .env
ECOPILOT_WEBHOOK_SECRET=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
ECOPILOT_GITLAB_TOKEN=glpat-aBcDeFgHiJkLmNoPqRsT
```

### 推荐配置（生产环境）

```bash
# .env
# 必需
ECOPILOT_WEBHOOK_SECRET=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
ECOPILOT_GITLAB_TOKEN=glpat-aBcDeFgHiJkLmNoPqRsT

# GitLab
ECOPILOT_GITLAB_BASE_URL=https://gitlab.com/api/v4

# 成本和碳排放
ECOPILOT_RUNNER_COST_PER_MIN=0.008
ECOPILOT_CARBON_KG_PER_MIN=0.02

# Anthropic（可选但推荐）
ECOPILOT_DUO_ANTHROPIC_URL=https://api.gitlab.com/ai/anthropic/v1/messages
ECOPILOT_DUO_ANTHROPIC_TOKEN=sk-ant-v0-abc123def456...
ECOPILOT_DUO_ANTHROPIC_MODEL=claude-sonnet-4-20250514

# GCP（可选）
ECOPILOT_GCP_PROJECT_ID=my-project-id-12345
ECOPILOT_BIGQUERY_TABLE_ID=my-project-id-12345.ecopilot.analysis_events
ECOPILOT_GCP_BILLING_TABLE_ID=my-project-id-12345.billing.gcp_billing_export_v1_012345

# 功能开关
ECOPILOT_ENABLE_AUTO_LABEL=true
ECOPILOT_ENABLE_AUTO_ISSUE=true
```

### 完整配置（所有功能）

```bash
# .env
# 必需
ECOPILOT_WEBHOOK_SECRET=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
ECOPILOT_GITLAB_TOKEN=glpat-aBcDeFgHiJkLmNoPqRsT

# GitLab
ECOPILOT_GITLAB_BASE_URL=https://gitlab.com/api/v4

# 成本和碳排放
ECOPILOT_RUNNER_COST_PER_MIN=0.008
ECOPILOT_CARBON_KG_PER_MIN=0.02

# Anthropic
ECOPILOT_DUO_ANTHROPIC_URL=https://api.gitlab.com/ai/anthropic/v1/messages
ECOPILOT_DUO_ANTHROPIC_TOKEN=sk-ant-v0-abc123def456...
ECOPILOT_DUO_ANTHROPIC_MODEL=claude-sonnet-4-20250514

# GCP
ECOPILOT_GCP_PROJECT_ID=my-project-id-12345
ECOPILOT_BIGQUERY_TABLE_ID=my-project-id-12345.ecopilot.analysis_events
ECOPILOT_GCP_BILLING_TABLE_ID=my-project-id-12345.billing.gcp_billing_export_v1_012345

# 功能开关
ECOPILOT_ENABLE_AUTO_LABEL=true
ECOPILOT_ENABLE_AUTO_ISSUE=true
```

---

## ✅ 配置检查清单

```bash
#!/bin/bash

echo "=== EcoPilot 配置检查 ==="

# 检查必需配置
echo "✓ 检查必需配置..."
[ -z "$ECOPILOT_WEBHOOK_SECRET" ] && echo "❌ ECOPILOT_WEBHOOK_SECRET 未设置" || echo "✅ ECOPILOT_WEBHOOK_SECRET"
[ -z "$ECOPILOT_GITLAB_TOKEN" ] && echo "❌ ECOPILOT_GITLAB_TOKEN 未设置" || echo "✅ ECOPILOT_GITLAB_TOKEN"

# 检查 GitLab 连接
echo "✓ 检查 GitLab 连接..."
curl -s -H "PRIVATE-TOKEN: $ECOPILOT_GITLAB_TOKEN" \
  ${ECOPILOT_GITLAB_BASE_URL:-https://gitlab.com/api/v4}/user > /dev/null && \
  echo "✅ GitLab 连接正常" || echo "❌ GitLab 连接失败"

# 检查可选配置
echo "✓ 检查可选配置..."
[ -n "$ECOPILOT_DUO_ANTHROPIC_TOKEN" ] && echo "✅ Anthropic 已配置" || echo "⚠️  Anthropic 未配置"
[ -n "$ECOPILOT_GCP_PROJECT_ID" ] && echo "✅ GCP 已配置" || echo "⚠️  GCP 未配置"

echo "=== 检查完成 ==="
```

---

## 🔗 相关资源

- [GitLab API 文档](https://docs.gitlab.com/ee/api/)
- [GitLab 个人访问令牌](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html)
- [Anthropic API 文档](https://docs.anthropic.com/)
- [Google Cloud 定价](https://cloud.google.com/pricing)
- [BigQuery 文档](https://cloud.google.com/bigquery/docs)

---

## 💡 常见问题

### Q: 如果没有 Anthropic token 可以使用吗？

**A**: 可以。EcoPilot 有确定性修复引擎，即使没有 Anthropic 也能工作。但 LLM 增强的修复会被禁用。

### Q: 如何更新配置？

**A**: 修改 `.env` 文件后重启服务：
```bash
docker-compose down
docker-compose up -d
```

### Q: 成本和碳排放数据从哪里来？

**A**: 这些是估算值，基于行业平均数据。你可以根据实际情况调整。

### Q: 如何验证所有配置都正确？

**A**: 运行测试套件：
```bash
pytest -v
```

---

现在你已经有了完整的配置指南！🎉
