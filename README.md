# 🌿 EcoPilot - Green CI Optimization Agent

[![GitLab AI Hackathon 2026](https://img.shields.io/badge/GitLab-AI%20Hackathon%202026-blue)](https://gitlab.devpost.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)

## 🎯 What is EcoPilot?

EcoPilot is an **AI agent** that helps developers build **sustainable CI/CD pipelines**. It analyzes your GitLab CI configuration, calculates environmental impact, and automatically generates optimizations.

### Key Features

- 🔍 **Automatic CI Analysis** - Detects anti-patterns in `.gitlab-ci.yml`
- 💰 **Cost Tracking** - Calculates CI costs in USD
- 🌱 **Carbon Estimation** - Estimates CO2e emissions
- ⚡ **Auto-Optimization** - Generates optimized CI configurations
- 🤖 **GitLab Duo Agent** - Native integration with GitLab Duo Platform

---

## 🏆 Hackathon Entry

This project is submitted to **GitLab AI Hackathon 2026** for the **Green Agent Prize**.

### Why EcoPilot Wins

| Category | How EcoPilot Fits |
|----------|-------------------|
| 🌿 **Green Agent** | Reduces CI carbon emissions by 50-80% |
| 💻 **Most Technically Impressive** | AI-powered analysis + auto-fix |
| 📈 **Most Impactful** | Saves money + carbon for every team |

---

## 🚀 Quick Start

### Prerequisites

- GitLab account
- Python 3.10+
- GitLab API token

### Installation

```bash
# Clone the repository
git clone https://github.com/dongowu/EcoPilot.git
cd EcoPilot

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ECOPILOT_GITLAB_TOKEN=your_gitlab_token
export ECOPILOT_WEBHOOK_SECRET=your_secret
```

### Run

```bash
uvicorn ecopilot.main:app --port 8080
```

### Configure GitLab Webhook

1. Go to **Settings → Webhooks** in your GitLab project
2. Add URL: `https://your-server/webhook/gitlab/mr`
3. Select **Merge request events**
4. Add secret token

---

## 📊 Example Output

```markdown
## 🌿 EcoPilot CI Analysis

### Pipeline Overview
- Jobs: 8
- Runtime: 25 minutes
- Cost: $0.20 per run
- Carbon: 0.5 kgCO2e

### Findings
| Issue | Severity | Impact |
|-------|----------|--------|
| No cache configured | 🔴 Critical | +12 min, $0.10 |
| Sequential jobs | 🟡 Medium | +8 min, $0.06 |

### 🌱 Potential Savings
- ⏱️ Time: 20 min (-80%)
- 💰 Cost: $0.16 (-80%)
- 🌿 Carbon: 0.4 kgCO2e (-80%)
```

---

## 🛠️ Configuration

| Environment Variable | Description | Default |
|----------------------|-------------|---------|
| `ECOPILOT_GITLAB_TOKEN` | GitLab API token | required |
| `ECOPILOT_WEBHOOK_SECRET` | Webhook security | optional |
| `ECOPILOT_RUNNER_COST_PER_MIN` | Cost per minute | $0.008 |
| `ECOPILOT_CARBON_KG_PER_MIN` | Carbon per minute | 0.02 kg |

---

## 🔧 GitLab Duo Agent Setup

### Enable the Agent

1. Go to **Automate → Agents** in your GitLab project
2. Create agent: `ecopilot-optimizer`
3. Use config from `.gitlab/agents/ecopilot-optimizer/config.yaml`

### Enable the Flow

1. Go to **Automate → Flows**
2. Import `.gitlab/flows/ecopilot-ci-optimization.yaml`
3. Configure trigger: Merge request opened/reopened/updated

---

## 📈 Environmental Impact

Using EcoPilot, teams can achieve:

- **50-80% reduction** in CI costs
- **50-80% reduction** in carbon emissions
- **Faster pipelines** through optimization

| Metric | Before | After | Savings |
|--------|--------|-------|---------|
| Runtime | 25 min | 5 min | 80% |
| Cost | $0.20 | $0.04 | 80% |
| Carbon | 0.5 kg | 0.1 kg | 80% |

---

## 📁 Project Structure

```
EcoPilot/
├── ecopilot/           # Main application
│   ├── main.py         # FastAPI app
│   ├── webhook.py      # Webhook handler
│   ├── gitlab_client.py # GitLab API client
│   ├── rules.py        # CI analysis rules
│   ├── estimator.py    # Cost/carbon calculation
│   └── reporter.py     # Report generation
├── .gitlab/
│   ├── agents/         # GitLab Duo Agent config
│   └── flows/          # GitLab Duo Flow config
├── tests/              # Test suite
└── README.md
```

---

## 🌍 License

MIT License - See [LICENSE](LICENSE)

---

**Built for sustainable software development** 🌿

*Submitting to GitLab AI Hackathon 2026 - Green Agent Prize*
