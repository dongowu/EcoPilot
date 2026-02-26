from ecopilot.collector import collect_ci_context
from ecopilot.models import MergeRequestContext


class FakeGitLabClient:
    def get_ci_config(self, project_id: int, ref: str) -> str:
        assert project_id == 123
        assert ref == "feature/x"
        return "build:\n  script: echo hi\n"

    def list_pipelines(self, project_id: int, ref: str, limit: int) -> list[dict]:
        assert project_id == 123
        assert ref == "feature/x"
        assert limit == 10
        return [{"id": 1, "duration": 120, "status": "success"}]

    def list_jobs(self, project_id: int, pipeline_id: int) -> list[dict]:
        assert project_id == 123
        assert pipeline_id == 1
        return [{"id": 11, "name": "build", "stage": "build", "duration": 120}]


def test_collect_returns_ci_and_history() -> None:
    ctx = MergeRequestContext(
        project_id=123,
        mr_iid=9,
        source_branch="feature/x",
        target_branch="main",
        commit_sha="abc123",
        event_id="evt-1",
    )
    result = collect_ci_context(FakeGitLabClient(), ctx, limit=10)
    assert "build:" in result.ci_yaml
    assert len(result.pipelines) == 1
    assert result.pipelines[0]["jobs"][0]["name"] == "build"
