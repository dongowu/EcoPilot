# EcoPilot Demo Script - GitLab AI Hackathon 2026

**Duration: 3 minutes**

---

## Scene 1: The Problem (30 seconds)

**[画面: 展示一个CI pipeline运行很慢的截图]**

> "Every day, teams around the world run CI pipelines that waste time and money. Long build times, missing caches, redundant jobs, inefficient Docker layers. The problem? Developers don't have time to optimize their CI configs, and manual optimization is tedious."

**[画面: 切换到痛点]**

> "According to GitLab's own data, the average team spends $2,000/month on CI runners. With proper optimization, they could save 30-50%."

---

## Scene 2: The Solution - EcoPilot (60 seconds)

**[画面: 展示EcoPilot架构图]**

> "Meet EcoPilot. An event-driven GitLab MR assistant that automatically detects CI waste, estimates cost and carbon impact, and generates AI-powered fixes."

**[画面: 展示demo]**

> "Here's how it works. When a developer opens a merge request..."

1. **Webhook Trigger** - EcoPilot receives the MR event via webhook
2. **CI Analysis** - Fetches `.gitlab-ci.yml` and analyzes for anti-patterns
3. **Impact Calculation** - Calculates potential savings in time, cost, and carbon
4. **AI Generation** - Uses Claude to generate optimized CI configuration
5. **Auto-Fix MR** - Creates a new MR with the fixed configuration

**[画面: 展示检测规则]**

> "EcoPilot detects 5 major anti-patterns: missing cache, sequential jobs that could be parallel, redundant builds, inefficient Docker layers, and over-provisioned runners."

---

## Scene 3: Live Demo (90 seconds)

**[画面: 准备一个示例.gitlab-ci.yml]**

> "Let me show you a real example."

### Demo Step 1: Submit MR with inefficient CI

```yaml
# Inefficient .gitlab-ci.yml
stages:
  - build
  - test
  - deploy

build:
  stage: build
  script:
    - npm install
    - npm run build
  cache:
    key: npm
    paths:
      - node_modules/

test:
  stage: test
  script:
    - npm install
    - npm test
  cache:
    key: npm
    paths:
      - node_modules/
```

> "This CI has two problems: npm install runs twice (no proper cache), and jobs run sequentially when they could be parallel."

### Demo Step 2: EcoPilot Analysis

**[画面: 展示EcoPilot的分析结果]**

> "EcoPilot analyzes the MR and finds:
- Missing cache key (cache key should include hash)
- Duplicate npm install (should be in separate job)
- Total potential savings: 3 minutes, $0.024, 0.06 kgCO2e per run"

### Demo Step 3: AI Fix Generated

**[画面: 展示生成的修复MR]**

> "But here's the magic. EcoPilot not only detects issues—it generates fixes. The AI creates an optimized configuration..."

### Demo Step 4: Fix MR Created

> "...and automatically creates a fix merge request that the developer can review and merge."

---

## Scene 4: Value Proposition (30 seconds)

**[画面: 总结]**

> "EcoPilot delivers value in three ways:

1. **Saves Time**: 30-50% reduction in pipeline duration
2. **Saves Money**: Direct cost savings on CI runners
3. **Saves Carbon**: Environmentally sustainable CI practices

This isn't just a tool—it's a digital teammate that helps teams build better software, faster."

**[画面: 结束画面]**

> "EcoPilot: CI Sustainability Powered by AI."

**Thank you!**

---

## Demo Assets Needed

1. Demo GitLab project with sample `.gitlab-ci.yml`
2. Screen recording of EcoPilot analyzing the MR
3. Screenshots of:
   - Analysis report
   - Cost/carbon savings
   - Auto-generated fix MR
4. Architecture diagram
5. Demo script narration

## Key Talking Points

- Event-driven automation (webhook-based)
- Deterministic + AI hybrid approach
- Quantified impact (time, cost, carbon)
- Auto-repair workflow
- GitLab Duo Agent integration
- Ready for production deployment
