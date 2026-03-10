from ecopilot.gcp_metrics import GCPMetricsCollector
from ecopilot.models import CloudImpactSummary, ImpactSummary


class FakeBillingQueryClient:
    def __init__(self) -> None:
        self.queries: list[tuple[str, list]] = []

    def query(self, query: str, job_config=None):  # noqa: ANN001
        self.queries.append((query, getattr(job_config, "query_parameters", [])))

        class Result:
            def result(self_nonlocal):  # noqa: ANN001
                return [
                    {
                        "monthly_cost_usd": 240.0,
                        "top_services": ["Cloud Build", "Cloud Run"],
                    }
                ]

        return Result()


def test_gcp_metrics_collector_estimates_monthly_google_cloud_savings() -> None:
    collector = GCPMetricsCollector(
        client=FakeBillingQueryClient(),
        billing_table="demo.billing.gcp_export",
    )
    impact = ImpactSummary(
        baseline_duration_min=50.0,
        baseline_cost_usd=0.4,
        baseline_carbon_kgco2e=1.0,
        projected_savings_duration_min=10.0,
        projected_savings_cost_usd=0.1,
        projected_savings_carbon_kgco2e=0.2,
    )

    summary = collector.collect(project_id="demo-proj", impact=impact)

    assert isinstance(summary, CloudImpactSummary)
    assert summary.provider == "gcp"
    assert summary.estimated_monthly_cost_usd == 240.0
    assert summary.estimated_monthly_savings_usd == 60.0
    assert summary.estimated_annual_savings_usd == 720.0
    assert summary.top_services == ["Cloud Build", "Cloud Run"]


def test_gcp_metrics_collector_passes_project_id_query_parameter() -> None:
    client = FakeBillingQueryClient()
    collector = GCPMetricsCollector(
        client=client,
        billing_table="demo.billing.gcp_export",
    )
    impact = ImpactSummary(
        baseline_duration_min=50.0,
        baseline_cost_usd=0.4,
        baseline_carbon_kgco2e=1.0,
        projected_savings_duration_min=10.0,
        projected_savings_cost_usd=0.1,
        projected_savings_carbon_kgco2e=0.2,
    )

    collector.collect(project_id="demo-proj", impact=impact)

    assert client.queries
    _, query_parameters = client.queries[0]
    assert query_parameters
