from fastapi.testclient import TestClient

from ecopilot.main import create_app


def _sample_payload() -> dict:
    return {
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


def test_webhook_rejects_missing_secret() -> None:
    app = create_app(webhook_secret="secret")
    client = TestClient(app)
    response = client.post("/webhook/gitlab/mr", json=_sample_payload())
    assert response.status_code == 401


def test_webhook_rejects_non_mr_event() -> None:
    app = create_app(webhook_secret="secret")
    client = TestClient(app)
    payload = _sample_payload()
    payload["object_kind"] = "push"
    response = client.post(
        "/webhook/gitlab/mr",
        headers={"x-gitlab-token": "secret"},
        json=payload,
    )
    assert response.status_code == 400

