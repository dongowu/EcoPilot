from ecopilot.action import ActionPublisher
from ecopilot.models import MergeRequestContext
from ecopilot.reporter import Reporter
from ecopilot.service import EcoPilotService


class FakeGitLabClient:
    def __init__(self) -> None:
        self.notes: list[dict] = [
            {
                "project_id": 123,
                "mr_iid": 9,
                "body": "existing\n<!-- ecopilot:event_id=evt-known -->",
            }
        ]

    def list_mr_notes(self, project_id: int, mr_iid: int) -> list[dict]:
        return [note for note in self.notes if note["project_id"] == project_id and note["mr_iid"] == mr_iid]

    def create_mr_note(self, project_id: int, mr_iid: int, body: str) -> None:
        self.notes.append({"project_id": project_id, "mr_iid": mr_iid, "body": body})

    def add_mr_label(self, project_id: int, mr_iid: int, labels: list[str]) -> None:
        _ = (project_id, mr_iid, labels)

    def create_issue(self, project_id: int, title: str, description: str) -> dict:
        _ = (project_id, title, description)
        return {"iid": 1}


class CountingCollector:
    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, gitlab_client: object, context: MergeRequestContext, limit: int = 10):  # noqa: ANN001
        self.calls += 1
        _ = (gitlab_client, context, limit)
        raise AssertionError("collector should not run for known duplicate event")


def test_service_short_circuits_known_duplicate_event() -> None:
    gitlab_client = FakeGitLabClient()
    collector = CountingCollector()
    service = EcoPilotService(
        gitlab_client=gitlab_client,
        collector=collector,
        reporter=Reporter(),
        publisher=ActionPublisher(gitlab_client),
    )
    context = MergeRequestContext(
        project_id=123,
        mr_iid=9,
        source_branch="feature/x",
        target_branch="main",
        commit_sha="abc",
        event_id="evt-known",
    )
    result = service.process_event(context, payload={})
    assert result["status"] == "duplicate"
    assert result["comment_posted"] is False
    assert result["finding_count"] == 0
    assert collector.calls == 0
