from __future__ import annotations

from fastapi import HTTPException

from ecopilot.models import MergeRequestContext

SUPPORTED_ACTIONS = {"open", "opened", "update", "reopen", "reopened"}


def validate_secret(expected_secret: str, provided_secret: str | None) -> None:
    if expected_secret and provided_secret != expected_secret:
        raise HTTPException(status_code=401, detail="invalid webhook token")


def parse_merge_request_context(headers: dict[str, str], payload: dict) -> MergeRequestContext:
    if payload.get("object_kind") != "merge_request":
        raise HTTPException(status_code=400, detail="unsupported event type")

    attrs = payload.get("object_attributes") or {}
    action = str(attrs.get("action", "")).lower()
    if action not in SUPPORTED_ACTIONS:
        raise HTTPException(status_code=400, detail="unsupported merge request action")

    project = payload.get("project") or {}
    commit = attrs.get("last_commit") or {}
    event_id = (
        headers.get("x-gitlab-event-uuid")
        or headers.get("x-request-id")
        or str(commit.get("id", ""))
    )
    if not event_id:
        raise HTTPException(status_code=400, detail="missing event id")

    return MergeRequestContext(
        project_id=int(project.get("id")),
        mr_iid=int(attrs.get("iid")),
        source_branch=str(attrs.get("source_branch", "")),
        target_branch=str(attrs.get("target_branch", "")),
        commit_sha=str(commit.get("id", "")),
        event_id=event_id,
    )
