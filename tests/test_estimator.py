from ecopilot.estimator import estimate_impact
from ecopilot.models import Finding


def test_estimator_outputs_baseline_and_projected_savings() -> None:
    findings = [
        Finding(
            rule_id="missing_cache",
            title="Missing cache",
            severity="high",
            evidence={"jobs": ["build_app"]},
            recommendation="Add cache paths",
            savings_ratio=0.15,
        ),
        Finding(
            rule_id="retry_timeout_inefficiency",
            title="Retry/timeout inefficiency",
            severity="medium",
            evidence={"jobs": ["e2e_tests"]},
            recommendation="Reduce retry/timeout",
            savings_ratio=0.05,
        ),
    ]

    summary = estimate_impact(
        pipelines=[{"duration": 1200}, {"duration": 1800}],
        findings=findings,
        runner_cost_per_min=0.008,
        carbon_kg_per_min=0.02,
    )

    assert summary.baseline_duration_min == 50.0
    assert summary.baseline_cost_usd == 0.4
    assert summary.baseline_carbon_kgco2e == 1.0
    assert summary.projected_savings_duration_min > 0
    assert summary.projected_savings_cost_usd > 0
    assert summary.projected_savings_carbon_kgco2e > 0
