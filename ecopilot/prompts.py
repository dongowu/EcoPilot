from __future__ import annotations

from ecopilot.models import (
    CloudImpactSummary,
    Finding,
    ImpactSummary,
    MergeRequestContext,
)


def build_report_prompt(
    context: MergeRequestContext,
    findings: list[Finding],
    impact: ImpactSummary,
    cloud_impact: CloudImpactSummary | None = None,
) -> str:
    lines = [
        "You are EcoPilot. Write an MR comment for CI sustainability optimization.",
        f"Project: {context.project_id}, MR: !{context.mr_iid}",
        "Findings:",
    ]
    for finding in findings:
        lines.append(
            f"- {finding.rule_id}: {finding.title}; severity={finding.severity}; "
            f"recommendation={finding.recommendation}; evidence={finding.evidence}"
        )
    lines.extend(
        [
            "Impact summary:",
            f"- baseline_duration_min={impact.baseline_duration_min}",
            f"- baseline_cost_usd={impact.baseline_cost_usd}",
            f"- baseline_carbon_kgco2e={impact.baseline_carbon_kgco2e}",
            f"- projected_savings_duration_min={impact.projected_savings_duration_min}",
            f"- projected_savings_cost_usd={impact.projected_savings_cost_usd}",
            f"- projected_savings_carbon_kgco2e={impact.projected_savings_carbon_kgco2e}",
        ]
    )
    if cloud_impact is not None:
        lines.extend(
            [
                "Google Cloud impact:",
                f"- estimated_monthly_cost_usd={cloud_impact.estimated_monthly_cost_usd}",
                f"- estimated_monthly_savings_usd={cloud_impact.estimated_monthly_savings_usd}",
                f"- estimated_annual_savings_usd={cloud_impact.estimated_annual_savings_usd}",
                f"- estimated_monthly_carbon_kgco2e={cloud_impact.estimated_monthly_carbon_kgco2e}",
                f"- top_services={cloud_impact.top_services}",
            ]
        )
    lines.append(
        "Return concise markdown with sections: Summary, Top Findings, Suggested CI Changes."
    )
    return "\n".join(lines)
