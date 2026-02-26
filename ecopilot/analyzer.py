from __future__ import annotations

from ecopilot.estimator import estimate_impact
from ecopilot.models import Finding, ImpactSummary
from ecopilot.rules import analyze_ci


def run_analysis(
    ci_yaml: str,
    pipelines: list[dict],
    runner_cost_per_min: float,
    carbon_kg_per_min: float,
) -> tuple[list[Finding], ImpactSummary]:
    findings = analyze_ci(ci_yaml, pipelines)
    impact = estimate_impact(
        pipelines=pipelines,
        findings=findings,
        runner_cost_per_min=runner_cost_per_min,
        carbon_kg_per_min=carbon_kg_per_min,
    )
    return findings, impact

