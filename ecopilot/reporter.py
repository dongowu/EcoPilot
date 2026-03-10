from __future__ import annotations

from ecopilot.models import (
    CloudImpactSummary,
    Finding,
    ImpactSummary,
    MergeRequestContext,
)
from ecopilot.prompts import build_report_prompt


class Reporter:
    def __init__(self, llm_client: object | None = None):
        self._llm_client = llm_client

    @property
    def llm_client(self) -> object | None:
        return self._llm_client

    def render(
        self,
        context: MergeRequestContext,
        findings: list[Finding],
        impact: ImpactSummary,
        cloud_impact: CloudImpactSummary | None = None,
    ) -> tuple[str, str]:
        prompt = build_report_prompt(context, findings, impact, cloud_impact)
        if self._llm_client is None:
            return self._render_fallback(findings, impact, cloud_impact), "fallback"

        try:
            response = self._llm_client.generate(prompt)
            if not isinstance(response, str) or not response.strip():
                raise RuntimeError("empty llm response")
            return response.strip(), "anthropic"
        except Exception:
            return self._render_fallback(findings, impact, cloud_impact), "fallback"

    def _render_fallback(
        self,
        findings: list[Finding],
        impact: ImpactSummary,
        cloud_impact: CloudImpactSummary | None = None,
    ) -> str:
        annual_cost = round(impact.projected_savings_cost_usd * 520, 2)
        annual_carbon = round(impact.projected_savings_carbon_kgco2e * 520, 2)
        severity_counts: dict[str, int] = {}
        for finding in findings:
            severity_counts[finding.severity] = (
                severity_counts.get(finding.severity, 0) + 1
            )

        severity_summary = (
            ", ".join(
                f"{count} {severity}"
                for severity, count in sorted(severity_counts.items())
            )
            or "no findings"
        )

        lines = [
            "### EcoPilot CI Sustainability Report",
            "",
            "#### Summary",
            (
                f"- Baseline: {impact.baseline_duration_min} min, "
                f"${impact.baseline_cost_usd}, {impact.baseline_carbon_kgco2e} kgCO2e"
            ),
            (
                f"- Estimated savings: {impact.projected_savings_duration_min} min, "
                f"${impact.projected_savings_cost_usd}, {impact.projected_savings_carbon_kgco2e} kgCO2e"
            ),
            f"- Finding mix: {severity_summary}",
            "",
            "#### Annualized Impact",
            f"- Estimated annual savings: ${annual_cost}, {annual_carbon} kgCO2e",
            "",
            "#### Top Findings",
        ]
        for finding in findings:
            lines.append(
                f"- `{finding.rule_id}` ({finding.severity}): {finding.recommendation}"
            )
        if cloud_impact is not None:
            lines.extend(
                [
                    "",
                    "#### Google Cloud Impact",
                    (
                        f"- Estimated monthly GCP spend: ${cloud_impact.estimated_monthly_cost_usd}; "
                        f"monthly savings: ${cloud_impact.estimated_monthly_savings_usd}"
                    ),
                    (
                        f"- Estimated annual GCP savings: ${cloud_impact.estimated_annual_savings_usd}; "
                        f"monthly carbon reduction: {cloud_impact.estimated_monthly_carbon_kgco2e} kgCO2e"
                    ),
                    f"- Highest-cost services in scope: {', '.join(cloud_impact.top_services) or 'n/a'}",
                ]
            )
        lines.extend(
            [
                "",
                "#### Recommended Next Step",
                "- Open the EcoPilot remediation MR or apply the highest-impact cache and rules changes first.",
            ]
        )
        return "\n".join(lines)
