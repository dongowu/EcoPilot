from pathlib import Path

import pytest

from ecopilot.replay import build_curl_command, build_headers, load_payload, main


def test_build_headers_contains_secret_and_event_id() -> None:
    headers = build_headers(secret="abc", event_id="evt-1")
    assert headers["x-gitlab-token"] == "abc"
    assert headers["x-gitlab-event-uuid"] == "evt-1"
    assert headers["content-type"] == "application/json"


def test_load_payload_rejects_non_mr_event(tmp_path: Path) -> None:
    payload_file = tmp_path / "payload.json"
    payload_file.write_text('{"object_kind":"push"}', encoding="utf-8")
    with pytest.raises(ValueError):
        load_payload(str(payload_file))


def test_build_curl_command_contains_required_flags() -> None:
    command = build_curl_command(
        url="http://127.0.0.1:8080/webhook/gitlab/mr",
        secret="abc",
        event_id="evt-1",
        payload_path="fixtures/mr_event.json",
    )
    assert "curl -sS -X POST" in command
    assert "x-gitlab-token: abc" in command
    assert "x-gitlab-event-uuid: evt-1" in command
    assert "--data-binary @fixtures/mr_event.json" in command


def test_main_returns_error_when_secret_missing(tmp_path: Path) -> None:
    payload_file = tmp_path / "payload.json"
    payload_file.write_text('{"object_kind":"merge_request"}', encoding="utf-8")
    rc = main(["--payload", str(payload_file), "--print-only"])
    assert rc == 1


def test_main_print_only_outputs_command(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    payload_file = tmp_path / "payload.json"
    payload_file.write_text('{"object_kind":"merge_request"}', encoding="utf-8")
    rc = main(
        [
            "--payload",
            str(payload_file),
            "--secret",
            "abc",
            "--event-id",
            "evt-9",
            "--print-only",
        ]
    )
    out = capsys.readouterr().out
    assert rc == 0
    assert "evt-9" in out
