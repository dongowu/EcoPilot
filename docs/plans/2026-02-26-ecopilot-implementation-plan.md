# EcoPilot MVP Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build an MVP that analyzes MR-triggered CI waste, posts actionable recommendations, and stores metrics for sustainability dashboards.

**Architecture:** FastAPI webhook service on Cloud Run receives MR events, collects GitLab CI config/history, runs deterministic rule analysis and estimators, optionally formats output with Anthropic, posts MR comments, and persists metrics to BigQuery.

**Tech Stack:** Python 3.12, FastAPI, httpx, pydantic, pytest, Google Cloud Run, BigQuery, GitLab APIs.

---

### Task 1: Bootstrap Service Skeleton (DEV-1)

**Files:**
- Create: `ecopilot/main.py`
- Create: `ecopilot/config.py`
- Create: `ecopilot/models.py`
- Create: `tests/test_health.py`

**Step 1: Write the failing test**

```python
from fastapi.testclient import TestClient
from ecopilot.main import app

def test_healthcheck():
    client = TestClient(app)
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_health.py -v`
Expected: FAIL because app route not defined yet.

**Step 3: Write minimal implementation**

Implement a FastAPI app with `GET /health` returning `{\"status\": \"ok\"}`.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_health.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add ecopilot/main.py ecopilot/config.py ecopilot/models.py tests/test_health.py
git commit -m "feat: bootstrap EcoPilot FastAPI service with health endpoint"
```

### Task 2: MR Webhook Intake and Validation (DEV-1)

**Files:**
- Modify: `ecopilot/main.py`
- Create: `ecopilot/webhook.py`
- Create: `tests/test_webhook_validation.py`

**Step 1: Write the failing test**

```python
def test_webhook_rejects_missing_secret(client):
    payload = {"object_kind": "merge_request"}
    res = client.post("/webhook/gitlab/mr", json=payload)
    assert res.status_code == 401
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_webhook_validation.py -v`
Expected: FAIL because endpoint or auth check is missing.

**Step 3: Write minimal implementation**

Add endpoint `POST /webhook/gitlab/mr` and verify secret header before processing.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_webhook_validation.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add ecopilot/main.py ecopilot/webhook.py tests/test_webhook_validation.py
git commit -m "feat: add MR webhook endpoint with secret validation"
```

### Task 3: GitLab Collector for CI Config and Pipeline History (DEV-1 + DEV-2)

**Files:**
- Create: `ecopilot/gitlab_client.py`
- Create: `ecopilot/collector.py`
- Create: `tests/test_collector.py`

**Step 1: Write the failing test**

```python
def test_collect_returns_ci_and_history(mock_gitlab):
    result = collect_ci_context(project_id="1", mr_iid="2")
    assert ".gitlab-ci.yml" in result
    assert len(result["pipelines"]) >= 1
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_collector.py -v`
Expected: FAIL because collector is not implemented.

**Step 3: Write minimal implementation**

Implement GitLab API wrappers for:
- fetching CI YAML at MR target ref
- fetching last N pipelines and basic job metrics

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_collector.py -v`
Expected: PASS with mocked HTTP responses.

**Step 5: Commit**

```bash
git add ecopilot/gitlab_client.py ecopilot/collector.py tests/test_collector.py
git commit -m "feat: implement GitLab collector for CI config and pipeline history"
```

### Task 4: Rule Engine and Estimators (DEV-2)

**Files:**
- Create: `ecopilot/rules.py`
- Create: `ecopilot/estimator.py`
- Create: `tests/test_rules.py`
- Create: `tests/test_estimator.py`

**Step 1: Write the failing tests**

Create tests for 5 rule categories and cost/carbon estimator outputs.

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_rules.py tests/test_estimator.py -v`
Expected: FAIL because logic is missing.

**Step 3: Write minimal implementation**

Implement deterministic findings with rule IDs and evidence payloads.

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_rules.py tests/test_estimator.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add ecopilot/rules.py ecopilot/estimator.py tests/test_rules.py tests/test_estimator.py
git commit -m "feat: add deterministic CI waste rule engine and sustainability estimators"
```

### Task 5: Recommendation Generator with Anthropic and Fallback (DEV-2)

**Files:**
- Create: `ecopilot/reporter.py`
- Create: `ecopilot/prompts.py`
- Create: `tests/test_reporter.py`

**Step 1: Write the failing tests**

Tests:
- reporter returns structured text when LLM succeeds
- fallback report returned when LLM throws error

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_reporter.py -v`
Expected: FAIL because reporter is missing.

**Step 3: Write minimal implementation**

Add Anthropic request wrapper and deterministic fallback formatter.

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_reporter.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add ecopilot/reporter.py ecopilot/prompts.py tests/test_reporter.py
git commit -m "feat: implement recommendation generator with fallback path"
```

### Task 6: MR Comment Publisher with Idempotency (DEV-1)

**Files:**
- Create: `ecopilot/action.py`
- Modify: `ecopilot/main.py`
- Create: `tests/test_action.py`

**Step 1: Write the failing tests**

Test:
- publishes one comment per unique event_id
- duplicate event_id does not repost comment

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_action.py -v`
Expected: FAIL because publisher is missing.

**Step 3: Write minimal implementation**

Implement GitLab note posting + event_id de-dup store.

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_action.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add ecopilot/action.py ecopilot/main.py tests/test_action.py
git commit -m "feat: add MR comment publishing with idempotency"
```

### Task 7: BigQuery Sink and Dashboard Dataset View (DEV-3)

**Files:**
- Create: `ecopilot/bq_sink.py`
- Create: `tests/test_bq_sink.py`
- Create: `infra/bigquery/schema.sql`
- Create: `infra/bigquery/views.sql`

**Step 1: Write the failing tests**

Test that analysis payload maps to expected row schema.

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_bq_sink.py -v`
Expected: FAIL because sink is missing.

**Step 3: Write minimal implementation**

Implement BigQuery insert client and SQL schema/view scripts.

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_bq_sink.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add ecopilot/bq_sink.py tests/test_bq_sink.py infra/bigquery/schema.sql infra/bigquery/views.sql
git commit -m "feat: add BigQuery sink and analytics schema"
```

### Task 8: End-to-End Integration and Demo Artifacts (PM-2 + DEV-3)

**Files:**
- Create: `docs/demo/README.md`
- Create: `docs/demo/evidence-checklist.md`
- Create: `tests/test_e2e_webhook_to_comment.py`

**Step 1: Write the failing test**

Define one mocked E2E scenario:
- webhook payload in
- comment and BQ row out

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_e2e_webhook_to_comment.py -v`
Expected: FAIL due incomplete pipeline path.

**Step 3: Write minimal implementation**

Wire modules in `main.py` to execute collector -> analyzer -> reporter -> action -> sink.

**Step 4: Run tests to verify it passes**

Run: `pytest -v`
Expected: PASS for all test suites.

**Step 5: Commit**

```bash
git add docs/demo/README.md docs/demo/evidence-checklist.md tests/test_e2e_webhook_to_comment.py ecopilot/main.py
git commit -m "feat: complete MVP flow and demo evidence package"
```

## Implementation Governance

- PM-1 reviews each task for PRD compliance before merge.
- PM-2 reviews user-facing output quality (comment readability and dashboard story).
- DEV-3 validates deployment and observability before demo freeze.

## Verification Before Completion

Run:
- `pytest -v`
- smoke request to `/health`
- sample webhook replay
- verify one BigQuery insert
- screenshot Looker tiles for evidence pack
