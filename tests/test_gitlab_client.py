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


def test_create_branch(monkeypatch) -> None:
    def fake_request(method, url, headers=None, params=None, json=None, timeout=None):  # noqa: ANN001
        _ = (method, url, headers, params, timeout)
        assert json == {"branch": "feature/new-feature", "ref": "main"}
        return FakeResponse({"name": "feature/new-feature", "protected": False})

    monkeypatch.setattr("httpx.request", fake_request)
    client = GitLabClient(base_url="https://gitlab.example/api/v4", token="t")
    result = client.create_branch(1, "feature/new-feature", "main")
    assert result["name"] == "feature/new-feature"


def test_commit_file(monkeypatch) -> None:
    def fake_request(method, url, headers=None, params=None, json=None, timeout=None):  # noqa: ANN001
        _ = (method, url, headers, params, timeout)
        assert json["branch"] == "main"
        assert json["commit_message"] == "Add new file"
        content = base64.b64decode(json["content"]).decode("utf-8")
        assert content == "Hello World"
        return FakeResponse({"file_path": "test.txt", "branch": "main"})

    monkeypatch.setattr("httpx.request", fake_request)
    client = GitLabClient(base_url="https://gitlab.example/api/v4", token="t")
    result = client.commit_file(1, "main", "test.txt", "Hello World", "Add new file")
    assert result["file_path"] == "test.txt"


def test_create_mr(monkeypatch) -> None:
    def fake_request(method, url, headers=None, params=None, json=None, timeout=None):  # noqa: ANN001
        _ = (method, url, headers, params, timeout)
        assert json == {
            "source_branch": "feature/new-feature",
            "target_branch": "main",
            "title": "Add new feature",
            "description": "This adds a new feature",
        }
        return FakeResponse({"iid": 1, "state": "opened"})

    monkeypatch.setattr("httpx.request", fake_request)
    client = GitLabClient(base_url="https://gitlab.example/api/v4", token="t")
    result = client.create_mr(
        1, "feature/new-feature", "main", "Add new feature", "This adds a new feature"
    )
    assert result["iid"] == 1
