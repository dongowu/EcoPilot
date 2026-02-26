from __future__ import annotations

from ecopilot.models import Finding, ImpactSummary, MergeRequestContext
from ecopilot.prompts import build_report_prompt


class Reporter:
    def __init__(self, llm_client: object | None = None):
        self._llm_client = llm_client

    def render(
        self,
        context: MergeRequestContext,
        findings: list[Finding],
        impact: ImpactSummary,
    ) -> tuple[str, str]:
        prompt = build_report_prompt(context, findings, impact)
        if self._llm_client is None:
            return self._render_fallback(findings, impact), "fallback"

        try:
            response = self._llm_client.generate(prompt)
            if not isinstance(response, str) or not response.strip():
                raise RuntimeError("empty llm response")
            return response.strip(), "anthropic"
        except Exception:
            return self._render_fallback(findings, impact), "fallback"

    def _render_fallback(self, findings: list[Finding], impact: ImpactSummary) -> str:
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
            "",
            "#### Top Findings",
        ]
        for finding in findings:
            lines.append(f"- `{finding.rule_id}` ({finding.severity}): {finding.recommendation}")
        return "\n".join(lines)

