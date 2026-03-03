# 🌿 EcoPilot - Green CI Optimization Agent

[![GitLab AI Hackathon 2026](https://img.shields.io/badge/GitLab-AI%20Hackathon%202026-blue)](https://gitlab.devpost.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## 🎯 Hackathon Entry: Green Agent Prize

EcoPilot is an AI agent that helps developers build **sustainable CI/CD pipelines**. It analyzes your GitLab CI configuration, calculates environmental impact, and automatically generates optimizations.

### Why EcoPilot Wins

| Category | How EcoPilot Fits |
|----------|-------------------|
| 🌿 **Green Agent** | Reduces CI carbon emissions by 50-80% |
| 💻 **Most Technically Impressive** | AI-powered analysis + auto-fix |
| 💰 **Most Impactful** | Saves money + carbon for every team |

---

## 🚀 What It Does

1. **Analyzes** `.gitlab-ci.yml` for anti-patterns
2. **Calculates** cost ($) and carbon (kgCO2e) impact
3. **Recommends** specific optimizations with quantified savings
4. **Auto-fixes** by generating optimized CI configs

### Example Output

```markdown
## 🌿 EcoPilot CI Analysis

### Pipeline Overview
- Jobs: 8
- Runtime: 25 minutes
- Cost: $0.20 per run
- Carbon: 0.5 kgCO2e

### 🌱 Potential Savings
- Time: 20 min (-80%)
- Cost: $0.16 (-80%)
- Carbon: 0.4 kgCO2e (-80%)
```

---

## 🛠️ Setup

### 1. Deploy EcoPilot Service

```bash
git clone https://github.com/dongowu/EcoPilot.git
cd EcoPilot

# Install dependencies
pip install -r requirements.txt

# Set environment
export ECOPILOT_GITLAB_TOKEN=your_gitlab_token
export ECOPILOT_WEBHOOK_SECRET=your_secret

# Run
uvicorn ecopilot.main:app --port 8080
```

### 2. Configure GitLab Webhook

1. Go to **Settings → Webhooks** in your GitLab project
2. Add URL: `https://your-server/webhook/gitlab/mr`
3. Select **Merge request events**

### 3. Configure GitLab Duo Agent

1. Go to **Automate → Agents**
2. Create agent: `ecopilot-optimizer`
3. Use config from `.gitlab/agents/ecopilot-optimizer/config.yaml`

---

## 📊 Environmental Impact

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
│   ├── gitlab_client.py # GitLab API
│   ├── rules.py        # CI analysis rules
│   ├── estimator.py    # Cost/carbon calculation
│   └── reporter.py    # Report generation
├── .gitlab/
│   ├── agents/         # GitLab Duo Agent config
│   └── flows/          # GitLab Duo Flow config
└── README.md
```

---

## 🌍 License

MIT License

---

**Built for sustainable software development** 🌿

*GitLab AI Hackathon 2026 - Green Agent Prize Entry*
