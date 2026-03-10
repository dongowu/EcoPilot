from __future__ import annotations

from datetime import datetime, timezone

from ecopilot.models import (
    CloudImpactSummary,
    Finding,
    ImpactSummary,
    MergeRequestContext,
)


class BigQuerySink:
    def __init__(self, client: object, table_id: str):
        self._client = client
        self._table_id = table_id

    def write(
        self,
        context: MergeRequestContext,
        findings: list[Finding],
        impact: ImpactSummary,
        llm_mode: str,
        cloud_impact: CloudImpactSummary | None = None,
        pipeline_count: int = 0,
    ) -> None:
        row = {
            "event_id": context.event_id,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "project_id": str(context.project_id),
            "mr_iid": str(context.mr_iid),
            "pipeline_count": int(pipeline_count),
            "baseline_duration_min": impact.baseline_duration_min,
            "baseline_cost_usd": impact.baseline_cost_usd,
            "baseline_carbon_kgco2e": impact.baseline_carbon_kgco2e,
            "projected_savings_duration_min": impact.projected_savings_duration_min,
            "projected_savings_cost_usd": impact.projected_savings_cost_usd,
            "projected_savings_carbon_kgco2e": impact.projected_savings_carbon_kgco2e,
            "top_rule_ids": [f.rule_id for f in findings],
            "llm_mode": llm_mode,
            "cloud_provider": cloud_impact.provider if cloud_impact else "",
            "estimated_monthly_gcp_cost_usd": cloud_impact.estimated_monthly_cost_usd
            if cloud_impact
            else 0.0,
            "estimated_monthly_gcp_savings_usd": cloud_impact.estimated_monthly_savings_usd
            if cloud_impact
            else 0.0,
            "estimated_annual_gcp_savings_usd": cloud_impact.estimated_annual_savings_usd
            if cloud_impact
            else 0.0,
        }
        errors = self._client.insert_rows_json(self._table_id, [row])
        if errors:
            raise RuntimeError(f"failed to insert rows into BigQuery: {errors}")
