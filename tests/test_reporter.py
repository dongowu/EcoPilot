from ecopilot.models import Finding, ImpactSummary, MergeRequestContext
from ecopilot.reporter import Reporter


class SuccessLLM:
    def generate(self, prompt: str) -> str:
        assert "missing_cache" in prompt
        return "AI summary"


class FailingLLM:
    def generate(self, prompt: str) -> str:
        _ = prompt
        raise RuntimeError("timeout")


def _sample_context() -> MergeRequestContext:
    return MergeRequestContext(
        project_id=123,
        mr_iid=9,
        source_branch="feature/x",
        target_branch="main",
        commit_sha="abc123",
        event_id="evt-1",
    )


def _sample_findings() -> list[Finding]:
    return [
        Finding(
            rule_id="missing_cache",
            title="Cache missing",
            severity="high",
            evidence={"jobs": ["build_app"]},
            recommendation="Add cache",
            savings_ratio=0.15,
        )
    ]


def _sample_impact() -> ImpactSummary:
    return ImpactSummary(
        baseline_duration_min=50.0,
        baseline_cost_usd=0.4,
        baseline_carbon_kgco2e=1.0,
        projected_savings_duration_min=7.5,
        projected_savings_cost_usd=0.06,
        projected_savings_carbon_kgco2e=0.15,
    )


def test_reporter_uses_llm_output_when_available() -> None:
    reporter = Reporter(llm_client=SuccessLLM())
    body, mode = reporter.render(_sample_context(), _sample_findings(), _sample_impact())
    assert mode == "anthropic"
    assert body == "AI summary"


def test_reporter_falls_back_when_llm_fails() -> None:
    reporter = Reporter(llm_client=FailingLLM())
    body, mode = reporter.render(_sample_context(), _sample_findings(), _sample_impact())
    assert mode == "fallback"
    assert "missing_cache" in body
    assert "estimated savings" in body.lower()
