from __future__ import annotations

from ecopilot.models import Finding, ImpactSummary


def estimate_impact(
    pipelines: list[dict],
    findings: list[Finding],
    runner_cost_per_min: float,
    carbon_kg_per_min: float,
) -> ImpactSummary:
    total_seconds = sum(float(item.get("duration") or 0.0) for item in pipelines)
    baseline_duration_min = round(total_seconds / 60.0, 2)
    baseline_cost_usd = round(baseline_duration_min * runner_cost_per_min, 4)
    baseline_carbon_kgco2e = round(baseline_duration_min * carbon_kg_per_min, 4)

    total_ratio = sum(max(0.0, finding.savings_ratio) for finding in findings)
    if total_ratio > 0.75:
        total_ratio = 0.75

    savings_duration = round(baseline_duration_min * total_ratio, 2)
    savings_cost = round(baseline_cost_usd * total_ratio, 4)
    savings_carbon = round(baseline_carbon_kgco2e * total_ratio, 4)

    return ImpactSummary(
        baseline_duration_min=baseline_duration_min,
        baseline_cost_usd=baseline_cost_usd,
        baseline_carbon_kgco2e=baseline_carbon_kgco2e,
        projected_savings_duration_min=savings_duration,
        projected_savings_cost_usd=savings_cost,
        projected_savings_carbon_kgco2e=savings_carbon,
    )

