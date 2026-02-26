# EcoPilot Product Requirements Document (PRD)

- Version: v1.0 (Hackathon Submission)
- Date: 2026-02-26
- Product: EcoPilot CI Sustainability Flow
- Primary Goal: Win Green Agent Prize and be competitive for GitLab + Google Cloud impact awards.

## 1) Problem Statement

Engineering teams spend CI minutes without clear visibility into cost and environmental impact. Most merge requests (MRs) are reviewed for code quality, not CI efficiency. Waste patterns such as missing cache, over-serialized jobs, redundant installs, and broad test scopes increase spend and energy usage.

EcoPilot addresses this by running on MR events, measuring CI cost and carbon proxy metrics, identifying inefficiencies, and posting actionable optimization recommendations directly in MR discussions.

## 2) Product Vision

EcoPilot is an event-driven AI flow that acts as a CI sustainability copilot:
1. Measure CI spend and carbon proxy impact at MR time.
2. Explain why waste happens, with evidence.
3. Recommend concrete YAML-level changes with estimated savings.
4. Track trend improvements in Google Cloud dashboards.

## 3) Business and Hackathon Alignment

### 3.1 Mandatory Compliance

- Use GitLab Duo Agent Platform (custom public flow).
- Use Anthropic models through GitLab-managed runtime defaults.
- Use Google Cloud capabilities (Cloud Run, BigQuery, Looker Studio).
- Build an agent or flow that takes action from triggers (not chat-only).

### 3.2 Award Target Fit

- Green Agent Prize: Directly optimizes software development sustainability.
- GitLab + Google Cloud Impact: Uses GCP data pipeline and dashboarding.
- Technical Impressive: Multi-agent orchestration with deterministic rule engine + LLM narrative generation.

## 4) Users and Personas

### Persona P1: MR Author (Developer)
- Goal: Ship code quickly without CI waste.
- Pain: CI bills and pipeline slowness are opaque.
- Need: Clear, practical suggestions in MR comments.

### Persona P2: Engineering Manager
- Goal: Reduce CI costs while maintaining delivery speed.
- Pain: No aggregated trend reporting on CI efficiency.
- Need: Weekly trend dashboard and top waste patterns.

### Persona P3: Platform Engineer / DevOps
- Goal: Improve CI templates and runner efficiency.
- Pain: Difficult root-cause analysis across projects.
- Need: Evidence-backed rule violations and history.

## 5) Goals and Non-Goals

### Goals (MVP)
- Trigger on MR events and automatically analyze CI efficiency.
- Produce per-MR report with cost, duration, carbon proxy, and recommendations.
- Persist analysis results in BigQuery and visualize in Looker Studio.
- Provide robust fallback mode if LLM output is unavailable.

### Non-Goals (MVP)
- Auto-commit CI YAML changes.
- Cross-group global optimization policy engine.
- Real-time carbon grid integration per runner region (use proxy model in v1).

## 6) Scope (MoSCoW)

### Must Have
- MR event webhook ingestion.
- `.gitlab-ci.yml` parser + pipeline history collector.
- Deterministic rule engine for waste detection.
- Cost and carbon proxy estimation.
- Anthropic-based recommendation rendering.
- MR comment posting and idempotency.
- BigQuery write path and Looker dashboard.
- LLM fallback comment path.

### Should Have
- Auto-label MR (for example: `ci-optimized`, `ci-waste-detected`).
- Auto-create optimization issue when severity is high.
- Rule confidence score and recommendation rank.

### Could Have
- Suggested patch snippet generator by stage.
- Team-level weekly digest comments.

### Won't Have (Hackathon Cut)
- Autonomous pipeline rewrite and direct merge action.
- Organization-wide policy enforcement with approvals.

## 7) User Stories

1. As an MR author, I want EcoPilot to comment on CI inefficiencies so I can fix them before merge.
2. As an engineering manager, I want trend dashboards so I can track cost and carbon improvements over time.
3. As a platform engineer, I want evidence-linked rule violations so I can update CI templates at the source.

## 8) Functional Requirements (FR)

### FR-001 Webhook Trigger
- Priority: Must
- Description: Trigger on MR opened, reopened, and updated events.
- Acceptance Criteria:
  - Given an MR update event, when webhook payload is valid, then analysis job starts within 60 seconds.

### FR-002 Project and MR Context Fetch
- Priority: Must
- Description: Resolve project, MR, branch, and commit SHA context from webhook.
- Acceptance Criteria:
  - Given event payload with project and MR references, then context object is built and logged with request_id.

### FR-003 CI Config Retrieval
- Priority: Must
- Description: Fetch `.gitlab-ci.yml` from target branch.
- Acceptance Criteria:
  - Given project and ref, then CI config fetch succeeds or returns actionable error in fallback comment.

### FR-004 Pipeline History Retrieval
- Priority: Must
- Description: Fetch latest 10 to 30 pipelines and relevant job-level metrics.
- Acceptance Criteria:
  - Given valid project token, then collector returns history list with duration/status/stage metadata.

### FR-005 Rule Engine Detection
- Priority: Must
- Description: Detect at least 5 waste patterns:
  - missing cache
  - serializable jobs left serial
  - redundant job steps
  - broad test scope without change-based filtering
  - retry/timeout inefficiency
- Acceptance Criteria:
  - Given known CI anti-pattern inputs, then engine emits deterministic findings with rule IDs.

### FR-006 Cost Estimation
- Priority: Must
- Description: Estimate CI spend with configurable runner unit cost.
- Acceptance Criteria:
  - Given total duration and runner cost input, then output includes total and per-finding cost impact.

### FR-007 Carbon Proxy Estimation
- Priority: Must
- Description: Estimate carbon proxy (`kgCO2e`) from duration and configured intensity coefficients.
- Acceptance Criteria:
  - Given duration and coefficient set, then output includes baseline and projected savings.

### FR-008 Recommendation Generation (Anthropic)
- Priority: Must
- Description: Generate human-readable recommendations via Duo Anthropic model.
- Acceptance Criteria:
  - Given findings payload, then generated report includes: issue, evidence, fix, expected savings.

### FR-009 MR Comment Publishing
- Priority: Must
- Description: Post structured report comment to MR.
- Acceptance Criteria:
  - Given report body, then MR receives a new comment with deterministic section format.

### FR-010 Idempotency and De-duplication
- Priority: Must
- Description: Prevent repeated comments on duplicate webhook deliveries.
- Acceptance Criteria:
  - Given same event_id, then at most one report comment is posted.

### FR-011 Fallback Mode
- Priority: Must
- Description: If LLM call fails, post rule-based plain-text report.
- Acceptance Criteria:
  - Given LLM timeout/error, then fallback report is posted and failure reason is logged.

### FR-012 BigQuery Persistence
- Priority: Must
- Description: Store analysis outputs for dashboarding.
- Acceptance Criteria:
  - Given completed analysis, then row insert succeeds with partitionable event timestamp.

### FR-013 Looker Studio Dashboard
- Priority: Must
- Description: Provide dashboard with trend and savings views.
- Acceptance Criteria:
  - Dashboard includes at least: total CI spend trend, total carbon proxy trend, top rules, before/after comparison.

### FR-014 Optional Labeling
- Priority: Should
- Description: Add MR label when inefficiency severity passes threshold.

### FR-015 Optional Issue Creation
- Priority: Should
- Description: Create optimization issue for high-impact findings with recommended actions.

## 9) Non-Functional Requirements (NFR)

### NFR-001 Performance
- End-to-end analysis p95 < 60 seconds for typical MR payload.

### NFR-002 Reliability
- Event handling success > 99% in demo environment.
- Retry strategy for external API transient failures.

### NFR-003 Security
- Secrets in Google Secret Manager.
- No plain-text tokens in logs.
- Signed webhook validation where possible.

### NFR-004 Observability
- Structured logs with request_id, project_id, mr_iid.
- Error rate metrics and alert thresholds.

### NFR-005 Explainability
- Every recommendation references source evidence and rule id.

### NFR-006 Maintainability
- Rule definitions are config-driven and extensible.

## 10) Data Model (MVP)

### 10.1 Core Entities
- `analysis_event`: one row per MR analysis execution.
- `finding`: one row per detected waste issue.
- `recommendation`: one row per recommendation.

### 10.2 Suggested BigQuery Schema
- `event_id` STRING
- `timestamp` TIMESTAMP
- `project_id` STRING
- `mr_iid` STRING
- `pipeline_count` INT64
- `baseline_duration_min` FLOAT64
- `baseline_cost_usd` FLOAT64
- `baseline_carbon_kgco2e` FLOAT64
- `projected_savings_cost_usd` FLOAT64
- `projected_savings_duration_min` FLOAT64
- `projected_savings_carbon_kgco2e` FLOAT64
- `top_rule_ids` ARRAY<STRING>
- `llm_mode` STRING (`anthropic` or `fallback`)

## 11) System Architecture

1. GitLab MR webhook calls FastAPI endpoint on Cloud Run.
2. Collector module calls GitLab APIs for CI config and history.
3. Analyzer module runs deterministic rules and estimators.
4. Reporter module calls Anthropic via GitLab Duo environment.
5. Action module posts MR comment and optional labels/issues.
6. Persistence module writes event results to BigQuery.
7. Looker Studio reads BigQuery views for demo dashboard.

## 12) API and Interface Requirements

### Input
- Webhook endpoint: `POST /webhook/gitlab/mr`
- Auth: shared secret header validation.

### Output
- MR comment template:
  - Summary (cost/duration/carbon proxy)
  - Top findings with evidence
  - YAML-oriented optimization suggestions
  - Estimated savings

## 13) Recommendation Template (Required)

Each finding must include:
- Rule ID and title.
- Evidence (job names/stages/history stats).
- Proposed fix (specific CI config changes).
- Estimated savings (`USD`, `min`, `kgCO2e`).
- Confidence (low/medium/high).

## 14) Error Handling and Fallback

- GitLab API errors: retry with backoff, then fallback comment if needed.
- Anthropic errors: use deterministic report generator.
- BigQuery write errors: queue to retry, do not block MR comment path.
- Invalid payload: reject with 4xx and log reason.

## 15) Delivery Plan and Milestones

- 2026-02-26 to 2026-03-05: MVP core flow and comment output.
- 2026-03-06 to 2026-03-14: BigQuery + Looker + fallback + hardening.
- 2026-03-15 to 2026-03-22: Benchmark data generation and before/after demo.
- 2026-03-23 to 2026-03-24: Video, submission copy, evidence pack.
- 2026-03-25: Final submission.

## 16) Success Metrics

### Product KPIs
- MR coverage: % of target MRs analyzed.
- Suggestion adoption: % of recommendations acted on.
- CI savings: baseline vs. post-change cost and duration delta.
- Carbon proxy reduction: baseline vs. post-change delta.

### Demo KPIs
- At least one repository with measurable before/after improvements.
- At least 3 reproducible MR examples with EcoPilot comments.

## 17) Risks and Mitigations

- Risk: Noisy recommendations reduce trust.
  - Mitigation: rule confidence thresholds + evidence citations.
- Risk: Inaccurate cost/carbon assumptions.
  - Mitigation: configurable coefficients and transparent formula section.
- Risk: External API instability during demo.
  - Mitigation: fallback report + cached sample payload replay.
- Risk: Timeline slip.
  - Mitigation: strict MVP cut; defer autonomous patching to v2.

## 18) Out-of-Scope for v1.0

- Automatic MR patch generation and direct merge suggestions.
- Multi-repo portfolio optimization engine.
- Per-region real-time carbon intensity feed integration.

## 19) Traceability Matrix (MVP)

| Requirement | Validation Method |
|---|---|
| FR-001 to FR-004 | Integration test with sample webhook payloads |
| FR-005 to FR-007 | Unit tests for rule engine and estimators |
| FR-008 to FR-011 | Fault-injection test for LLM fallback |
| FR-012 to FR-013 | BigQuery insert test and dashboard screenshot evidence |
| NFR-001 to NFR-004 | Load sample + structured logs + error replay |

## 20) Demo Evidence Checklist

- Public flow link and architecture diagram.
- MR trigger-to-comment video.
- 3 MR screenshots with actionable recommendations.
- Before/after trend charts from Looker.
- One-page methodology for cost and carbon proxy formulas.
