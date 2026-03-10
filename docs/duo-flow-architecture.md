# EcoPilot Duo Flow Architecture

EcoPilot is presented as a `GitLab Duo Agent Platform` workflow first, with the Python service acting as the execution backend.

## Product surface

The user-facing entry point is `flows/ecopilot-flow.yml`.

That flow coordinates four public agents:

1. `triage_agent`
   - identifies wasteful CI patterns
   - mirrors the deterministic rule analysis in `ecopilot/rules.py`
2. `impact_agent`
   - quantifies runtime, cost, carbon, and Google Cloud savings
   - mirrors `ecopilot/estimator.py` and `ecopilot/gcp_metrics.py`
3. `remediation_agent`
   - turns findings into safe GitLab CI changes
   - mirrors `ecopilot/repair.py`
4. `guardrail_agent`
   - adds merge confidence, rollback notes, and post-merge checks
   - mirrors the guardrail assessment path in `ecopilot/repair.py`

## Backend execution engine

The EcoPilot service in `ecopilot/main.py` and `ecopilot/service.py` powers the real actions behind the Duo story:

- receives GitLab merge request webhooks
- reads `.gitlab-ci.yml` and recent pipeline history
- runs deterministic CI waste analysis
- computes impact summaries
- generates deterministic remediation when no LLM is available
- uses Anthropic through GitLab for guardrail reasoning when configured
- comments on merge requests and can open remediation merge requests
- writes analytics rows to BigQuery when configured

## Why this split matters

This architecture makes the submission read correctly for the hackathon:

- `GitLab Duo flow` is the primary developer experience
- `public agents` are reusable building blocks within that flow
- `EcoPilot service` is the automation backend that makes the flow actionable

In short: Duo is the interface and orchestration layer; EcoPilot is the execution and data layer.
