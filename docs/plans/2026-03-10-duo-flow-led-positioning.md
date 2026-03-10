# EcoPilot Flow-Led Duo Positioning Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Reposition EcoPilot so the GitLab Duo flow is clearly the primary product surface, while the EcoPilot service is presented as the execution engine behind that flow.

**Architecture:** Keep the existing Python service unchanged as the automation backend, but rewrite the public agents, public flow, and repository documentation so the user journey starts with GitLab Duo orchestration. Add an architecture document that maps each Duo stage to the underlying service actions and data sources.

**Tech Stack:** GitLab Duo public agent YAML, GitLab Duo public flow YAML, Markdown documentation, Python test verification

---

### Task 1: Reframe the public flow and agent descriptions

**Files:**
- Modify: `flows/ecopilot-flow.yml`
- Modify: `agents/ecopilot-agent.yml`
- Modify: `agents/ecopilot-triage-agent.yml`
- Modify: `agents/ecopilot-impact-agent.yml`
- Modify: `agents/ecopilot-remediation-agent.yml`
- Modify: `agents/ecopilot-guardrail-agent.yml`

**Step 1: Update descriptions**

Make the flow the primary artifact and position each agent as a stage in the Duo workflow.

**Step 2: Clarify orchestration intent**

Emphasize that the flow coordinates analysis, impact, remediation, and safety guidance.

### Task 2: Add a Duo-native architecture document

**Files:**
- Create: `docs/duo-flow-architecture.md`

**Step 1: Document stage mapping**

Show how `triage`, `impact`, `remediation`, and `guardrail` map to EcoPilot service capabilities.

**Step 2: Document action mapping**

Explain which parts happen in Duo and which parts happen in the service backend.

### Task 3: Rewrite README around the flow-led story

**Files:**
- Modify: `README.md`

**Step 1: Move flow to the top**

Introduce EcoPilot first as a GitLab Duo flow.

**Step 2: Reframe the service**

Describe the Python service as the backend execution layer for the flow.

**Step 3: Verify**

Run: `python -m pytest -v`
Expected: PASS.
