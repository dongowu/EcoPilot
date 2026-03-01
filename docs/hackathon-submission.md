# EcoPilot - GitLab AI Hackathon 2026 Submission

## Project Information

- **Project Name**: EcoPilot AI
- **Team**: 1 developer
- **Category**: Green Agents / CI Optimization
- **Video**: [To be uploaded]
- **Repository**: https://github.com/dongowu/EcoPilot

---

## Problem Statement

Development teams face constantly rising CI/CD costs. Despite optimization opportunities, manual optimization is time-consuming and often overlooked. EcoPilot AI automates CI optimization by detecting anti-patterns and generating AI-powered fixes directly within the merge request workflow.

## Solution

EcoPilot is an event-driven GitLab MR assistant that:
1. Receives merge request webhook events
2. Analyzes `.gitlab-ci.yml` for 5 common anti-patterns
3. Calculates cost and carbon impact
4. Uses AI (Claude) to generate optimized configurations
5. Automatically creates fix merge requests

## Key Features

| Feature | Description |
|---------|-------------|
| **Anti-Pattern Detection** | 5 detection rules for common CI inefficiencies |
| **Cost Estimation** | $0.008/min runner cost calculation |
| **Carbon Tracking** | 0.02 kgCO2e/min carbon proxy |
| **AI Auto-Fix** | Claude-powered CI configuration generation |
| **Auto-Repair MR** | Automatic fix MR creation |
| **GitLab Duo Agent** | Custom agent for CI optimization |
| **Flow Integration** | Orchestrated multi-agent workflow |

## Technical Stack

- **Language**: Python 3.10+
- **API**: GitLab REST API v4
- **AI**: Anthropic Claude API
- **Deployment**: FastAPI (uvicorn)
- **Testing**: pytest (31 tests passing)

## Innovation

1. **Event-Driven Automation**: React to MR events automatically
2. **Hybrid Approach**: Deterministic detection + AI generation
3. **Quantified Impact**: Time, cost, and carbon savings
4. **Auto-Repair**: Not just detection—actual fixes generated
5. **Full Integration**: Webhook → Analysis → Fix → MR

## Submission Checklist

- [x] Public repository with MIT license
- [x] Custom agent configuration (`.gitlab/agents/`)
- [x] Flow configuration (`.gitlab/flows/`)
- [x] Chat rules (`.gitlab/duo/chat-rules.md`)
- [x] Agent guidelines (`AGENTS.md`)
- [x] Demo script prepared
- [ ] Video recording
- [ ] GitLab AI Hackathon group registration

## Next Steps

1. Register for GitLab AI Hackathon group
2. Create demo video (3 minutes)
3. Set up live demo environment
4. Test with real GitLab MRs

---

## Contact

- GitHub: https://github.com/dongowu/EcoPilot
- Demo: https://github.com/dongowu/EcoPilot/blob/main/docs/demo-script.md
