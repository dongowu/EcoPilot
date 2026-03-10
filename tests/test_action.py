from ecopilot.action import ActionPublisher
from ecopilot.models import Finding, MergeRequestContext


class FakeGitLabClient:
    def __init__(self) -> None:
        self.notes: list[dict] = []
        self.labels: list[dict] = []
        self.issues: list[dict] = []

    def create_mr_note(self, project_id: int, mr_iid: int, body: str) -> None:
        self.notes.append({"project_id": project_id, "mr_iid": mr_iid, "body": body})

    def list_mr_notes(self, project_id: int, mr_iid: int) -> list[dict]:
        return [note for note in self.notes if note["project_id"] == project_id and note["mr_iid"] == mr_iid]

    def add_mr_label(self, project_id: int, mr_iid: int, labels: list[str]) -> None:
        self.labels.append({"project_id": project_id, "mr_iid": mr_iid, "labels": labels})

    def create_issue(self, project_id: int, title: str, description: str) -> dict:
        issue = {"project_id": project_id, "title": title, "description": description, "iid": 1}
        self.issues.append(issue)
        return issue


def _context(event_id: str) -> MergeRequestContext:
    return MergeRequestContext(
        project_id=123,
        mr_iid=9,
        source_branch="feature/x",
        target_branch="main",
        commit_sha="abc123",
        event_id=event_id,
    )


def test_action_publishes_once_per_event_id() -> None:
    client = FakeGitLabClient()
    publisher = ActionPublisher(client)
    body = "report"

    created = publisher.publish_comment(_context("evt-1"), body)
    duplicate = publisher.publish_comment(_context("evt-1"), body)

    assert created is True
    assert duplicate is False
    assert len(client.notes) == 1
    assert "<!-- ecopilot:event_id=evt-1 -->" in client.notes[0]["body"]


def test_action_skips_if_marker_already_exists_in_mr_notes() -> None:
    client = FakeGitLabClient()
    client.notes.append(
        {
            "project_id": 123,
            "mr_iid": 9,
            "body": "old report\n<!-- ecopilot:event_id=evt-remote -->",
        }
    )
    publisher = ActionPublisher(client)

    created = publisher.publish_comment(_context("evt-remote"), "new report")

    assert created is False
    assert len(client.notes) == 1


def _finding(severity: str) -> Finding:
    return Finding(
        rule_id="missing_cache",
        title="Cache missing",
        severity=severity,
        evidence={"jobs": ["build_app"]},
        recommendation="Add cache",
        savings_ratio=0.1,
    )


def test_action_optional_label_and_issue_for_high_severity() -> None:
    client = FakeGitLabClient()
    publisher = ActionPublisher(client)
    result = publisher.apply_optional_actions(
        context=_context("evt-2"),
        findings=[_finding("high")],
        enable_auto_label=True,
        enable_auto_issue=True,
    )
    assert result["label_applied"] is True
    assert result["issue_created"] is True
    assert len(client.labels) == 1
    assert len(client.issues) == 1


def test_action_skips_issue_when_no_high_severity() -> None:
    client = FakeGitLabClient()
    publisher = ActionPublisher(client)
    result = publisher.apply_optional_actions(
        context=_context("evt-3"),
        findings=[_finding("medium")],
        enable_auto_label=True,
        enable_auto_issue=True,
    )
    assert result["label_applied"] is True
    assert result["issue_created"] is False
    assert len(client.labels) == 1
    assert len(client.issues) == 0
