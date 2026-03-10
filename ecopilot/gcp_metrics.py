from __future__ import annotations

from types import SimpleNamespace

from ecopilot.models import CloudImpactSummary, ImpactSummary


class GCPMetricsCollector:
    def __init__(
        self, client: object, billing_table: str, carbon_kg_per_usd: float = 0.12
    ):
        self._client = client
        self._billing_table = billing_table
        self._carbon_kg_per_usd = carbon_kg_per_usd

    def collect(
        self, project_id: str, impact: ImpactSummary
    ) -> CloudImpactSummary | None:
        if impact.baseline_cost_usd <= 0:
            return None

        monthly_cost_usd, top_services = self._read_monthly_cost(project_id)
        savings_ratio = min(
            max(impact.projected_savings_cost_usd / impact.baseline_cost_usd, 0.0), 1.0
        )
        monthly_savings = round(monthly_cost_usd * savings_ratio, 2)
        annual_savings = round(monthly_savings * 12, 2)
        monthly_carbon = round(monthly_savings * self._carbon_kg_per_usd, 2)
        return CloudImpactSummary(
            provider="gcp",
            estimated_monthly_cost_usd=monthly_cost_usd,
            estimated_monthly_savings_usd=monthly_savings,
            estimated_annual_savings_usd=annual_savings,
            estimated_monthly_carbon_kgco2e=monthly_carbon,
            top_services=top_services,
        )

    def _read_monthly_cost(self, project_id: str) -> tuple[float, list[str]]:
        if not hasattr(self._client, "query"):
            return 0.0, []

        query = (
            "SELECT ROUND(SUM(cost), 2) AS monthly_cost_usd, "
            "ARRAY_AGG(service.description ORDER BY cost DESC LIMIT 3) AS top_services "
            f"FROM `{self._billing_table}` "
            "WHERE project.id = @project_id"
        )
        try:
            job_config = SimpleNamespace(
                query_parameters=[
                    {
                        "name": "project_id",
                        "parameterType": "STRING",
                        "parameterValue": project_id,
                    }
                ]
            )
            rows = list(self._client.query(query, job_config=job_config).result())
        except Exception:
            return 0.0, []
        if not rows:
            return 0.0, []
        row = rows[0]
        return float(row.get("monthly_cost_usd", 0.0) or 0.0), [
            str(item) for item in (row.get("top_services", []) or [])
        ]
