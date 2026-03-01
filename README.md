# EcoPilot CI Sustainability Flow

![GitLab AI Hackathon 2026](https://img.shields.io/badge/GitLab-AI%20Hackathon%202026-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-green)
![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)

EcoPilot is an event-driven GitLab MR assistant that detects CI waste, estimates cost/carbon proxy impact, and automatically generates AI-powered optimization fixes.

## What It Does

- Receives merge request webhook events.
- Pulls `.gitlab-ci.yml` and recent pipeline/job history.
- Detects CI anti-patterns using deterministic rules.
- Estimates baseline and potential savings in:
  - pipeline duration (minutes)
  - CI cost (USD)
  - carbon proxy (`kgCO2e`)
- **AI-Powered Auto-Fix**: Generates optimized CI configuration using LLM and creates automatic fix MRs
- Generates MR report (Anthropic mode when integrated, deterministic fallback otherwise).
- Optionally applies follow-up actions: add MR labels and open optimization issues for high-severity findings.
- Stores analysis records for dashboarding (BigQuery sink interface).

## Key Features

### 1. CI Anti-Pattern Detection
- Missing cache configuration
- Sequential jobs that could run in parallel
- Redundant builds and tests
- Inefficient Docker layer caching
- Over-provisioned runner resources

### 2. Cost & Carbon Estimation
- Runner cost: $0.008/min (GitLab shared runners)
- Carbon proxy: 0.02 kgCO2e/min
- Quantified savings in USD and kgCO2e

### 3. AI Auto-Repair
- Generates optimized .gitlab-ci.yml using Claude
- Automatically creates fix merge requests
- Links fix MR in original MR comments

### 4. GitLab Duo Agent Integration
- Custom agent: `ecopilot-optimizer`
- Flow: `ecopilot-ci-optimization`
- Chat rules for CI optimization guidance

## Project Layout

```text
ecopilot/
  main.py
  webhook.py
  gitlab_client.py
  collector.py
  rules.py
  estimator.py
  reporter.py
  action.py
  bq_sink.py
  service.py
```

## Quick Start

```bash
python3 -m pip install -r requirements.txt
python3 -m pytest tests -q
uvicorn ecopilot.main:app --reload --port 8080
```

Health check:

```bash
curl -s http://127.0.0.1:8080/health
```

Generate deployment commands (requires env vars set):

```bash
./scripts/print_setup_commands.sh
```

Replay a local MR webhook event (service must already be running):

```bash
ECOPILOT_WEBHOOK_SECRET=your_secret ./scripts/replay_webhook.sh --print-only
ECOPILOT_WEBHOOK_SECRET=your_secret ./scripts/replay_webhook.sh
```

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `ECOPILOT_WEBHOOK_SECRET` | GitLab webhook token | empty |
| `ECOPILOT_GITLAB_BASE_URL` | GitLab API base URL | `https://gitlab.com/api/v4` |
| `ECOPILOT_GITLAB_TOKEN` | Personal/project token for GitLab API | empty |
| `ECOPILOT_RUNNER_COST_PER_MIN` | Cost estimator coefficient | `0.008` |
| `ECOPILOT_CARBON_KG_PER_MIN` | Carbon proxy coefficient | `0.02` |
| `ECOPILOT_ENABLE_AUTO_LABEL` | Auto add MR label when findings exist | `false` |
| `ECOPILOT_ENABLE_AUTO_ISSUE` | Auto open issue for high-severity findings | `false` |
| `ECOPILOT_BIGQUERY_TABLE_ID` | BigQuery target table | empty |
| `ECOPILOT_DUO_ANTHROPIC_URL` | GitLab Duo/Anthropic endpoint URL | empty |
| `ECOPILOT_DUO_ANTHROPIC_TOKEN` | Token for Duo/Anthropic endpoint | empty |
| `ECOPILOT_DUO_ANTHROPIC_MODEL` | Anthropic model id | `claude-sonnet-4-20250514` |

## Webhook Endpoint

- `POST /webhook/gitlab/mr`
- validates `x-gitlab-token` when secret is configured
- accepts merge request actions: `opened`, `reopened`, `update`
- appends event marker comments (`<!-- ecopilot:event_id=... -->`) for durable idempotency
- duplicate webhook deliveries with same event id are short-circuited (status `duplicate`)

## Notes

- Current BigQuery integration is pluggable through `BigQuerySink`; wire a real client in production.
- LLM generation is abstracted in `Reporter`; inject Duo/Anthropic client in deployment runtime.

## GitLab Duo Agent Configuration

### Enable the Agent
1. Create a GitLab project and push this code
2. Go to **Automate → Agents**
3. Create new agent with name `ecopilot-optimizer`
4. Configure as specified in `.gitlab/agents/ecopilot-optimizer/config.yaml`

### Enable the Flow
1. Go to **Automate → Flows**
2. Import `.gitlab/flows/ecopilot-ci-optimization.yaml`
3. Configure triggers for merge request events

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ GitLab MR   │────▶│  EcoPilot    │────▶│  Claude API │
│  Webhook    │     │  分析引擎    │     │  生成修复   │
└─────────────┘     └──────────────┘     └─────────────┘
       │                   │                    │
       ▼                   ▼                    ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ MR Comment  │◀────│  修复 MR     │     │  成本/碳排  │
│ 优化建议    │     │  (自动创建)  │     │   估算      │
└─────────────┘     └──────────────┘     └─────────────┘
```
