# EcoPilot Agent Team Plan (2 PM + 3 Developer Agents)

> Objective: Build and deliver EcoPilot MVP aligned to the PRD in `docs/prd/2026-02-26-ecopilot-prd.md` before the 2026-03-25 deadline.

## 1) Team Topology

Pattern: **Supervisor + Pipeline Hybrid**
- Supervisor: PM-1 orchestrates priorities, decisions, and rule compliance.
- Pipeline stages: PM discovery -> technical breakdown -> implementation -> QA/verification -> demo packaging.

## 2) Agent Roles and Responsibilities

### PM-1: Product Strategy and Compliance Lead
- Mission: Keep scope aligned with hackathon rules and award targets.
- Owns:
  - PRD scope and acceptance criteria
  - Award compliance checklist (GitLab + Anthropic + GCP + Green)
  - Final go/no-go for MVP scope cuts
- Skills:
  - `requirements-analyst`
  - `doc-coauthoring`
  - `project-estimator`

### PM-2: Delivery and UX Narrative Lead
- Mission: Ensure recommendations are clear, usable, and demo-ready.
- Owns:
  - MR comment format
  - demo story and evidence package
  - dashboard narrative and before/after framing
- Skills:
  - `tech-writer`
  - `sprint-manager`
  - `brainstorming`

### DEV-1: Integration Engineer
- Mission: Build event ingestion and GitLab interactions.
- Owns:
  - webhook endpoint
  - GitLab API collectors
  - MR comment publishing and idempotency
- Skills:
  - `api-designer`
  - `mcp-builder`
  - `test-generator`

### DEV-2: Analysis Engine Engineer
- Mission: Build deterministic rule engine and estimators.
- Owns:
  - YAML parsing
  - rule detection
  - cost and carbon proxy formulas
- Skills:
  - `code-quality`
  - `code-refactorer`
  - `test-driven-development`

### DEV-3: Data and Cloud Engineer
- Mission: Implement GCP data plane and observability.
- Owns:
  - Cloud Run deployment
  - BigQuery schema and write path
  - Looker Studio dashboard and logs/alerts
- Skills:
  - `cloud-deployer`
  - `monitoring-setup`
  - `cicd-pipeline`

## 3) Requirement Discussion (Simulated Team Workshop Output)

### Round 1: PM Requirement Proposal

PM-1 proposes mandatory MVP requirements:
1. MR-triggered automatic execution.
2. Deterministic waste detection with at least five rule categories.
3. Anthropic-generated recommendation comment with concrete fixes.
4. BigQuery persistence and Looker dashboard.
5. Fallback mode when LLM path fails.

PM-2 proposes usability and demo requirements:
1. Recommendation format must be short, actionable, and evidence-backed.
2. Per-finding estimated savings must include `USD`, `minutes`, `kgCO2e`.
3. Dashboard must show trend and before/after view in under 3 clicks.

### Round 2: Developer Feasibility Review

DEV-1 feedback:
- Webhook and MR actions are straightforward.
- Risk: duplicate events from retries -> requires event idempotency key.

DEV-2 feedback:
- Rule engine can ship 5 rules in MVP.
- Risk: confidence noise if evidence mapping is weak -> require rule-level evidence payload.

DEV-3 feedback:
- BigQuery + Looker fit timeline.
- Risk: dashboard delays if schema churns -> freeze schema by end of week 1.

### Round 3: Alignment Decisions

1. Keep deterministic engine as source of truth; LLM only formats recommendations.
2. Freeze MVP rule list to 5 categories (expand post-hackathon).
3. Implement fallback report path before adding optional issue creation.
4. Lock BigQuery schema by week 1 end.
5. Define demo dataset generation script for reproducible before/after evidence.

## 4) FR-to-Owner Alignment Matrix

| FR ID | Feature | DRI | Support | Target Window | Done Definition |
|---|---|---|---|---|---|
| FR-001 | MR webhook trigger | DEV-1 | PM-1 | 02-26 to 03-01 | event received and queued in <60s |
| FR-002 | context fetch | DEV-1 | DEV-2 | 02-27 to 03-02 | context object includes project/MR/SHA |
| FR-003 | CI config retrieval | DEV-1 | DEV-2 | 02-27 to 03-02 | `.gitlab-ci.yml` parsed without fatal errors |
| FR-004 | pipeline history | DEV-1 | DEV-3 | 02-28 to 03-03 | latest history metrics returned |
| FR-005 | rule engine | DEV-2 | PM-1 | 02-28 to 03-05 | 5 rule categories pass tests |
| FR-006 | cost estimator | DEV-2 | PM-1 | 03-01 to 03-05 | baseline + per-finding cost outputs |
| FR-007 | carbon proxy estimator | DEV-2 | PM-2 | 03-01 to 03-05 | projected savings in kgCO2e output |
| FR-008 | anthropic report | DEV-2 | PM-2 | 03-03 to 03-07 | recommendation template complete |
| FR-009 | MR comment publish | DEV-1 | PM-2 | 03-03 to 03-07 | comment posted with deterministic sections |
| FR-010 | idempotency | DEV-1 | DEV-3 | 03-04 to 03-08 | duplicate event does not duplicate comment |
| FR-011 | fallback mode | DEV-2 | DEV-1 | 03-05 to 03-09 | fallback comment works on forced LLM error |
| FR-012 | BigQuery write path | DEV-3 | DEV-1 | 03-06 to 03-10 | row insert succeeds with partition key |
| FR-013 | Looker dashboard | DEV-3 | PM-2 | 03-08 to 03-14 | required dashboard tiles available |

## 5) Decision Protocol

- Priority order:
  1. Mandatory hackathon compliance.
  2. MVP reliability.
  3. Demo quality.
  4. Optional automation.

- Tie-breaker:
  - PM-1 decides scope.
  - DEV lead for affected domain decides implementation approach.
  - PM-2 approves external-facing wording and demo framing.

- Escalation SLA:
  - blocking issue triage within 4 hours.
  - scope-cut decision within same day.

## 6) Communication Protocol

Use structured task messages:
- `task_id`
- `owner`
- `requirement_ref` (FR/NFR id)
- `status` (`todo`, `in_progress`, `blocked`, `done`)
- `blocker`
- `next_action`
- `evidence_link`

Daily 15-minute sync agenda:
1. What was completed against FRs.
2. What is blocked and by whom.
3. Scope changes and their impact on awards.

## 7) Delivery Cadence

- Daily:
  - PM-1: compliance and scope check.
  - PM-2: recommendation UX and narrative check.
  - Devs: implementation and test updates.

- Twice weekly:
  - cross-role review of sample MR outputs.
  - dashboard quality and metric sanity check.

- End of each week:
  - checkpoint demo with frozen evidence snapshots.

## 8) Quality Gates

Release gate for MVP demo:
1. End-to-end MR trigger to comment succeeds in staging.
2. At least one forced LLM failure still posts fallback comment.
3. BigQuery receives analysis events with expected schema.
4. Looker dashboard shows trend and before/after evidence.
5. No secret leakage in logs.

## 9) Immediate Backlog (Next 7 Days)

1. DEV-1: webhook + context + comment skeleton.
2. DEV-2: 5-rule engine + estimator modules with unit tests.
3. DEV-3: BigQuery dataset/table + minimal dashboard v0.
4. PM-2: final MR comment template and rubric.
5. PM-1: compliance checklist and acceptance test matrix.

## 10) Output Artifacts to Maintain

- PRD: `docs/prd/2026-02-26-ecopilot-prd.md`
- Team alignment: `docs/plans/2026-02-26-ecopilot-agent-team-alignment.md`
- (Next) implementation plan: `docs/plans/2026-02-26-ecopilot-implementation-plan.md`
- (Next) demo checklist: `docs/plans/2026-02-26-ecopilot-demo-checklist.md`
- Deployment runbook: `docs/plans/2026-02-26-ecopilot-deployment-runbook.md`
