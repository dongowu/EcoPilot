from __future__ import annotations

from urllib.parse import quote_plus

import httpx


class GitLabClient:
    def __init__(self, base_url: str, token: str, timeout: float = 15.0):
        self._base_url = base_url.rstrip("/")
        self._headers = {"PRIVATE-TOKEN": token} if token else {}
        self._timeout = timeout

    def _request(self, method: str, path: str, params: dict | None = None, json: dict | None = None) -> dict | list:
        url = f"{self._base_url}{path}"
        response = httpx.request(
            method=method,
            url=url,
            headers=self._headers,
            params=params,
            json=json,
            timeout=self._timeout,
        )
        response.raise_for_status()
        return response.json()

    def get_ci_config(self, project_id: int, ref: str) -> str:
        path = f"/projects/{project_id}/repository/files/{quote_plus('.gitlab-ci.yml')}"
        data = self._request("GET", path, params={"ref": ref})
        # GitLab file API returns base64 content by default; many self-managed instances can return raw.
        content = data.get("content", "")
        if not isinstance(content, str):
            raise RuntimeError("invalid CI content")
        try:
            import base64

            return base64.b64decode(content).decode("utf-8")
        except Exception:
            return content

    def list_pipelines(self, project_id: int, ref: str, limit: int) -> list[dict]:
        path = f"/projects/{project_id}/pipelines"
        data = self._request("GET", path, params={"ref": ref, "per_page": limit})
        return list(data) if isinstance(data, list) else []

    def list_jobs(self, project_id: int, pipeline_id: int) -> list[dict]:
        path = f"/projects/{project_id}/pipelines/{pipeline_id}/jobs"
        data = self._request("GET", path, params={"per_page": 100})
        return list(data) if isinstance(data, list) else []

    def create_mr_note(self, project_id: int, mr_iid: int, body: str) -> None:
        path = f"/projects/{project_id}/merge_requests/{mr_iid}/notes"
        self._request("POST", path, json={"body": body})

    def list_mr_notes(self, project_id: int, mr_iid: int) -> list[dict]:
        path = f"/projects/{project_id}/merge_requests/{mr_iid}/notes"
        data = self._request("GET", path, params={"per_page": 100})
        return list(data) if isinstance(data, list) else []

    def add_mr_label(self, project_id: int, mr_iid: int, labels: list[str]) -> None:
        path = f"/projects/{project_id}/merge_requests/{mr_iid}"
        self._request("PUT", path, json={"labels": ",".join(labels)})

    def create_issue(self, project_id: int, title: str, description: str) -> dict:
        path = f"/projects/{project_id}/issues"
        data = self._request("POST", path, json={"title": title, "description": description})
        return dict(data) if isinstance(data, dict) else {}
