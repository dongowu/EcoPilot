from fastapi.testclient import TestClient

from ecopilot.action import ActionPublisher
from ecopilot.bq_sink import BigQuerySink
from ecopilot.collector import collect_ci_context
from ecopilot.main import create_app
from ecopilot.reporter import Reporter
from ecopilot.service import EcoPilotService


class FakeGitLabClient:
    def __init__(self) -> None:
        self.notes: list[dict] = []
        self.labels: list[dict] = []
        self.issues: list[dict] = []

    def get_ci_config(self, project_id: int, ref: str) -> str:
        _ = (project_id, ref)
        return """
stages: [build, test]
build_app:
  stage: build
  script: [npm ci, npm run build]
test_app:
  stage: test
  script: [npm ci, npm test]
"""

    def list_pipelines(self, project_id: int, ref: str, limit: int) -> list[dict]:
        _ = (project_id, ref, limit)
        return [{"id": 1, "duration": 600, "status": "success"}]

    def list_jobs(self, project_id: int, pipeline_id: int) -> list[dict]:
        _ = (project_id, pipeline_id)
        return [
            {"name": "build_app", "stage": "build", "duration": 300},
            {"name": "test_app", "stage": "test", "duration": 300},
        ]

    def create_mr_note(self, project_id: int, mr_iid: int, body: str) -> None:
        self.notes.append({"project_id": project_id, "mr_iid": mr_iid, "body": body})

    def add_mr_label(self, project_id: int, mr_iid: int, labels: list[str]) -> None:
        self.labels.append({"project_id": project_id, "mr_iid": mr_iid, "labels": labels})

    def create_issue(self, project_id: int, title: str, description: str) -> dict:
        issue = {"project_id": project_id, "title": title, "description": description, "iid": 1}
        self.issues.append(issue)
        return issue

    def list_mr_notes(self, project_id: int, mr_iid: int) -> list[dict]:
        return [note for note in self.notes if note["project_id"] == project_id and note["mr_iid"] == mr_iid]


class FakeBigQueryClient:
    def __init__(self) -> None:
        self.rows: list[dict] = []

    def insert_rows_json(self, table: str, rows: list[dict]) -> list:
        _ = table
        self.rows.extend(rows)
        return []


class SuccessLLM:
    def generate(self, prompt: str) -> str:
        _ = prompt
        return "AI summary"


def test_webhook_to_comment_and_bq() -> None:
    gitlab_client = FakeGitLabClient()
    bq_client = FakeBigQueryClient()
    service = EcoPilotService(
        gitlab_client=gitlab_client,
        collector=collect_ci_context,
        reporter=Reporter(llm_client=SuccessLLM()),
        publisher=ActionPublisher(gitlab_client),
        sink=BigQuerySink(client=bq_client, table_id="demo.dataset.analysis_events"),
        runner_cost_per_min=0.008,
        carbon_kg_per_min=0.02,
        enable_auto_label=True,
        enable_auto_issue=True,
    )
    app = create_app(webhook_secret="secret", service=service)
    client = TestClient(app)

    payload = {
        "object_kind": "merge_request",
        "project": {"id": 123},
        "object_attributes": {
            "iid": 9,
            "action": "update",
            "source_branch": "feature/x",
            "target_branch": "main",
            "last_commit": {"id": "abc123"},
        },
    }
    response = client.post(
        "/webhook/gitlab/mr",
        headers={"x-gitlab-token": "secret", "x-gitlab-event-uuid": "evt-1"},
        json=payload,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "processed"
    assert len(gitlab_client.notes) == 1
    assert gitlab_client.notes[0]["body"].startswith("AI summary")
    assert "<!-- ecopilot:event_id=evt-1 -->" in gitlab_client.notes[0]["body"]
    assert len(gitlab_client.labels) == 1
    assert len(gitlab_client.issues) == 1
    assert len(bq_client.rows) == 1
    assert bq_client.rows[0]["event_id"] == "evt-1"
    assert bq_client.rows[0]["pipeline_count"] == 1


def test_duplicate_webhook_event_is_skipped() -> None:
    gitlab_client = FakeGitLabClient()
    bq_client = FakeBigQueryClient()
    service = EcoPilotService(
        gitlab_client=gitlab_client,
        collector=collect_ci_context,
        reporter=Reporter(llm_client=SuccessLLM()),
        publisher=ActionPublisher(gitlab_client),
        sink=BigQuerySink(client=bq_client, table_id="demo.dataset.analysis_events"),
        runner_cost_per_min=0.008,
        carbon_kg_per_min=0.02,
        enable_auto_label=True,
        enable_auto_issue=True,
    )
    app = create_app(webhook_secret="secret", service=service)
    client = TestClient(app)
    payload = {
        "object_kind": "merge_request",
        "project": {"id": 123},
        "object_attributes": {
            "iid": 9,
            "action": "update",
            "source_branch": "feature/x",
            "target_branch": "main",
            "last_commit": {"id": "abc123"},
        },
    }
    headers = {"x-gitlab-token": "secret", "x-gitlab-event-uuid": "evt-dup"}
    first = client.post("/webhook/gitlab/mr", headers=headers, json=payload)
    second = client.post("/webhook/gitlab/mr", headers=headers, json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["result"]["status"] == "processed"
    assert second.json()["result"]["status"] == "duplicate"
    assert len(gitlab_client.notes) == 1
    assert len(gitlab_client.labels) == 1
    assert len(gitlab_client.issues) == 1
    assert len(bq_client.rows) == 1
