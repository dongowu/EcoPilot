import base64

from ecopilot.gitlab_client import GitLabClient


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self):
        return self._payload


def test_get_ci_config_decodes_base64(monkeypatch) -> None:
    encoded = base64.b64encode(b"build:\n  script: echo hi\n").decode("utf-8")

    def fake_request(method, url, headers=None, params=None, json=None, timeout=None):  # noqa: ANN001
        _ = (method, url, headers, params, json, timeout)
        return FakeResponse({"content": encoded})

    monkeypatch.setattr("httpx.request", fake_request)
    client = GitLabClient(base_url="https://gitlab.example/api/v4", token="t")
    content = client.get_ci_config(1, "main")
    assert "build:" in content


def test_list_pipelines_returns_list(monkeypatch) -> None:
    def fake_request(method, url, headers=None, params=None, json=None, timeout=None):  # noqa: ANN001
        _ = (method, url, headers, params, json, timeout)
        return FakeResponse([{"id": 1}, {"id": 2}])

    monkeypatch.setattr("httpx.request", fake_request)
    client = GitLabClient(base_url="https://gitlab.example/api/v4", token="t")
    pipelines = client.list_pipelines(1, "main", 10)
    assert [p["id"] for p in pipelines] == [1, 2]
