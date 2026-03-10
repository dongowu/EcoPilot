# EcoPilot Prize Upgrade Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Upgrade EcoPilot from a solid webhook analyzer into a stronger hackathon submission with deterministic auto-remediation, richer quantified reporting, and a more compelling GitLab Duo story for Green Agent and GitLab + Google judging.

**Architecture:** Keep the existing FastAPI webhook service and deterministic analyzer, then add a deterministic remediation engine that can rewrite `.gitlab-ci.yml` without depending on an LLM. Improve the merge request report to show clearer baseline, projected savings, and annualized impact, then update the public agent and flow definitions so the project reads like an orchestrated GitLab-native sustainability workflow.

**Tech Stack:** Python, FastAPI, pytest, PyYAML, GitLab webhook integration, GitLab Duo agent YAML, GitLab Duo flow YAML

---

### Task 1: Deterministic remediation tests

**Files:**
- Modify: `tests/test_repair.py`
- Test: `tests/test_repair.py`

**Step 1: Write the failing test**

Add a test that passes a wasteful `.gitlab-ci.yml` and asserts `AIRepairService.generate_fix()` returns YAML even when no LLM client exists.

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_repair.py -v`
Expected: FAIL because the current implementation returns `None` without an LLM.

**Step 3: Write minimal implementation**

Add a deterministic fallback repair path for key rules such as missing cache, broad test scope, and retry/timeout inefficiency.

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_repair.py -v`
Expected: PASS.

### Task 2: Prize-oriented reporting tests

**Files:**
- Modify: `tests/test_reporter.py`
- Test: `tests/test_reporter.py`

**Step 1: Write the failing test**

Add a test asserting the fallback MR report includes quantified savings, annualized impact, and a clear recommended next action.

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_reporter.py -v`
Expected: FAIL because the current fallback report is too sparse.

**Step 3: Write minimal implementation**

Improve fallback rendering to highlight baseline metrics, projected savings, annualized impact, severity summary, and remediation guidance.

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_reporter.py -v`
Expected: PASS.

### Task 3: Flow and documentation upgrade

**Files:**
- Modify: `agents/ecopilot-agent.yml`
- Modify: `flows/ecopilot-flow.yml`
- Modify: `README.md`

**Step 1: Update agent and flow narrative**

Make the public assets describe trigger, analysis, remediation, and Google Cloud/green story more clearly.

**Step 2: Update README**

Document the winning story, why deterministic remediation matters, and how to demo the project in 3 minutes.

**Step 3: Verify repository behavior**

Run: `python -m pytest -v`
Expected: PASS.
