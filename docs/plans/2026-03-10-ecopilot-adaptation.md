# EcoPilot Adaptation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Adapt the existing EcoPilot service into this GitLab AI Hackathon repository so it can analyze GitLab CI pipelines, estimate cost and carbon waste, and provide an agent/flow configuration that supports automated remediation.

**Architecture:** Port the proven Python FastAPI service from the existing `EcoPilot` project into this repository, keeping the deterministic analyzer, webhook handling, report generation, and optional AI repair path. Add public GitLab Duo agent and flow definitions that explain and orchestrate the sustainability optimization workflow around the service.

**Tech Stack:** Python, FastAPI, pytest, PyYAML, GitLab webhook integration, GitLab Duo agent YAML, GitLab Duo flow YAML

---

### Task 1: Scaffold the Python service package

**Files:**
- Create: `ecopilot/__init__.py`
- Create: `ecopilot/config.py`
- Create: `ecopilot/models.py`
- Create: `requirements.txt`
- Create: `main.py`
- Test: `tests/test_health.py`

**Step 1: Write the failing test**

Create `tests/test_health.py` with a health endpoint expectation.

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_health.py -v`
Expected: FAIL because the app module does not exist yet.

**Step 3: Write minimal implementation**

Add the FastAPI app entry point, minimal settings/model scaffolding, and `/health` endpoint.

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_health.py -v`
Expected: PASS.

### Task 2: Add CI analysis and cost/carbon estimation

**Files:**
- Create: `ecopilot/rules.py`
- Create: `ecopilot/estimator.py`
- Create: `ecopilot/analyzer.py`
- Test: `tests/test_rules.py`
- Test: `tests/test_estimator.py`

**Step 1: Write the failing tests**

Add tests for missing cache detection, redundant steps, broad test scope, and impact summary calculations.

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_rules.py tests/test_estimator.py -v`
Expected: FAIL because modules and functions are missing.

**Step 3: Write minimal implementation**

Implement deterministic CI rule checks and impact estimation based on runner-minute cost and carbon coefficients.

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_rules.py tests/test_estimator.py -v`
Expected: PASS.

### Task 3: Add reporting, webhook parsing, and service orchestration

**Files:**
- Create: `ecopilot/prompts.py`
- Create: `ecopilot/reporter.py`
- Create: `ecopilot/webhook.py`
- Create: `ecopilot/collector.py`
- Create: `ecopilot/action.py`
- Create: `ecopilot/service.py`
- Create: `ecopilot/gitlab_client.py`
- Test: `tests/test_reporter.py`
- Test: `tests/test_webhook_validation.py`
- Test: `tests/test_service_duplicates.py`

**Step 1: Write the failing tests**

Add tests for fallback report formatting, webhook secret validation, merge request context parsing, and duplicate-event handling.

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_reporter.py tests/test_webhook_validation.py tests/test_service_duplicates.py -v`
Expected: FAIL because orchestration modules do not exist yet.

**Step 3: Write minimal implementation**

Implement comment rendering, webhook validation, lightweight GitLab API abstraction, context collection, and service coordination.

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_reporter.py tests/test_webhook_validation.py tests/test_service_duplicates.py -v`
Expected: PASS.

### Task 4: Add AI-assisted repair flow and end-to-end webhook behavior

**Files:**
- Create: `ecopilot/repair.py`
- Create: `ecopilot/anthropic_client.py`
- Update: `ecopilot/main.py`
- Test: `tests/test_repair.py`
- Test: `tests/test_e2e_webhook_to_comment.py`

**Step 1: Write the failing tests**

Add tests for repair prompt generation, MR creation flow, and webhook-to-comment execution using a fake GitLab client/service.

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_repair.py tests/test_e2e_webhook_to_comment.py -v`
Expected: FAIL because repair and integration pieces are incomplete.

**Step 3: Write minimal implementation**

Implement optional LLM-based repair generation, fix-MR creation helpers, and webhook route wiring.

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_repair.py tests/test_e2e_webhook_to_comment.py -v`
Expected: PASS.

### Task 5: Publish GitLab Duo agent, flow, and documentation

**Files:**
- Create: `agents/ecopilot-agent.yml`
- Create: `flows/ecopilot-flow.yml`
- Update: `README.md`

**Step 1: Write documentation expectations**

Define the public-facing story: trigger, analysis, quantified impact, and automated remediation.

**Step 2: Implement agent/flow definitions**

Create a public agent prompt focused on CI sustainability analysis and a public flow that sequences analysis and remediation guidance.

**Step 3: Update repository README**

Document setup, architecture, demo narrative, and prize alignment.

**Step 4: Verify repository completeness**

Run: `pytest -v`
Expected: PASS for the test suite that covers the service logic.
