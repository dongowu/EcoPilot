from ecopilot.bq_sink import BigQuerySink
from ecopilot.models import Finding, ImpactSummary, MergeRequestContext


class FakeBigQueryClient:
    def __init__(self) -> None:
        self.writes: list[tuple[str, list[dict]]] = []

    def insert_rows_json(self, table: str, rows: list[dict]) -> list:
        self.writes.append((table, rows))
        return []


def test_bq_sink_writes_expected_shape() -> None:
    client = FakeBigQueryClient()
    sink = BigQuerySink(client, table_id="demo.dataset.analysis_events")
    context = MergeRequestContext(
        project_id=123,
        mr_iid=9,
        source_branch="feature/x",
        target_branch="main",
        commit_sha="abc123",
        event_id="evt-1",
    )
    findings = [
        Finding(
            rule_id="missing_cache",
            title="Cache missing",
            severity="high",
            evidence={"jobs": ["build_app"]},
            recommendation="Add cache",
            savings_ratio=0.15,
        )
    ]
    impact = ImpactSummary(
        baseline_duration_min=50.0,
        baseline_cost_usd=0.4,
        baseline_carbon_kgco2e=1.0,
        projected_savings_duration_min=7.5,
        projected_savings_cost_usd=0.06,
        projected_savings_carbon_kgco2e=0.15,
    )

    sink.write(
        context=context,
        findings=findings,
        impact=impact,
        llm_mode="fallback",
        pipeline_count=7,
    )

    assert len(client.writes) == 1
    table, rows = client.writes[0]
    assert table == "demo.dataset.analysis_events"
    assert rows[0]["event_id"] == "evt-1"
    assert rows[0]["top_rule_ids"] == ["missing_cache"]
    assert rows[0]["pipeline_count"] == 7
