# EcoPilot

EcoPilot is a `GitLab Duo Agent Platform` project for sustainable CI/CD, led by a public Duo flow that acts like a green CI teammate. The flow triages CI waste, quantifies runtime/cost/carbon impact, proposes remediation, and adds merge guardrails before a developer merges the optimization.

## Why this project can win

- It is built around a `GitLab Duo flow` and public agents, not just an external AI webhook.
- It reacts to merge request events instead of acting like a chat-only assistant.
- It takes action by publishing MR feedback and generating a deterministic fix even when an LLM is unavailable.
- It tells a strong story for `Green Agent`, `GitLab + Google`, and `GitLab + Anthropic` categories.

## What the service does

EcoPilot has two layers:

1. `GitLab Duo flow and agents` are the primary product surface.
2. `EcoPilot service` is the backend execution engine that powers real actions.

The backend service does the following:

1. Receives a GitLab merge request webhook.
2. Reads CI config and recent pipeline history from GitLab.
3. Detects CI waste patterns such as missing cache, redundant steps, broad test scope, wasteful retry or timeout settings, and over-serialized pipelines.
4. Calculates baseline runtime, estimated savings, runner cost reduction, and carbon reduction.
5. Posts a sustainability report back to the merge request with annualized savings.
6. Generates a deterministic `.gitlab-ci.yml` fix for common waste patterns, with optional AI refinement when Anthropic is configured.
7. Opens a remediation merge request so the developer can merge the optimization instead of rewriting CI by hand.

## Why deterministic remediation matters

Hackathon demos break when they depend on a single model call. EcoPilot now keeps the workflow alive even without Anthropic by auto-fixing common CI waste patterns itself:

- missing cache for dependency-heavy jobs
- overly broad test execution
- wasteful retry counts and timeouts

That makes the project easier to demo, easier to trust, and more aligned with the idea of an autonomous teammate.

## Winning demo arc

1. Show a merge request with an intentionally wasteful `.gitlab-ci.yml`.
2. Trigger EcoPilot through the MR webhook.
3. Show the MR comment with baseline metrics, projected savings, and annualized impact.
4. Show the remediation MR that EcoPilot created automatically.
5. Close with the before/after story: less runner waste, lower cloud spend, lower carbon.

## Project layout

```text
ecopilot/      Python service code
tests/         Automated test suite
fixtures/      Webhook payload fixtures
agents/        Public GitLab Duo agent definition
flows/         Public GitLab Duo flow definition
main.py        ASGI entry point
```

## Local setup

```bash
python -m pip install -r requirements.txt
uvicorn ecopilot.main:app --host 0.0.0.0 --port 8080
```

Optional environment variables:

- `ECOPILOT_GITLAB_BASE_URL`
- `ECOPILOT_GITLAB_TOKEN`
- `ECOPILOT_WEBHOOK_SECRET`
- `ECOPILOT_DUO_ANTHROPIC_URL`
- `ECOPILOT_DUO_ANTHROPIC_TOKEN`
- `ECOPILOT_DUO_ANTHROPIC_MODEL`
- `ECOPILOT_BIGQUERY_TABLE_ID`
- `ECOPILOT_GCP_BILLING_TABLE_ID`
- `ECOPILOT_GCP_PROJECT_ID`
- `ECOPILOT_ENABLE_AUTO_LABEL`
- `ECOPILOT_ENABLE_AUTO_ISSUE`

## Verify

```bash
python -m pytest -v
```

## GitLab Duo Agent Platform assets

- Flow-first entry point: `flows/ecopilot-flow.yml`
- Orchestrator: `agents/ecopilot-agent.yml`
- Triage agent: `agents/ecopilot-triage-agent.yml`
- Impact agent: `agents/ecopilot-impact-agent.yml`
- Remediation agent: `agents/ecopilot-remediation-agent.yml`
- Guardrail agent: `agents/ecopilot-guardrail-agent.yml`

The public flow is the main product entry and is structured as a four-stage Duo workflow:

1. `triage_agent` finds the largest CI waste patterns
2. `impact_agent` quantifies runtime, cost, carbon, and Google Cloud impact
3. `remediation_agent` proposes merge-ready GitLab CI changes
4. `guardrail_agent` adds merge confidence and rollback guidance

## Platform architecture

- `GitLab Duo flow` is the primary user experience
- `Public Duo agents` are the reusable stages within that flow
- `EcoPilot service` is the execution engine that powers webhook handling, analysis, remediation, and persistence
- `Anthropic through GitLab` strengthens the guardrail and remediation reasoning path
- `Google Cloud` strengthens the cost and sustainability evidence path

More detail: `docs/duo-flow-architecture.md`

## License

MIT
