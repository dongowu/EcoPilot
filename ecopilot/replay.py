from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from typing import Sequence


def build_headers(secret: str, event_id: str) -> dict[str, str]:
    return {
        "x-gitlab-token": secret,
        "x-gitlab-event-uuid": event_id,
        "content-type": "application/json",
    }


def load_payload(payload_path: str) -> dict:
    with open(payload_path, "r", encoding="utf-8") as fh:
        payload = json.load(fh)
    if payload.get("object_kind") != "merge_request":
        raise ValueError("payload object_kind must be merge_request")
    return payload


def build_curl_command(url: str, secret: str, event_id: str, payload_path: str) -> str:
    headers = build_headers(secret=secret, event_id=event_id)
    return (
        "curl -sS -X POST "
        + " ".join(f"-H {shlex.quote(f'{k}: {v}')}" for k, v in headers.items())
        + f" --data-binary @{payload_path} {shlex.quote(url)}"
    )


def _parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Replay a GitLab MR webhook payload to EcoPilot")
    parser.add_argument("--url", default="http://127.0.0.1:8080/webhook/gitlab/mr")
    parser.add_argument("--payload", default="fixtures/mr_event.json")
    parser.add_argument("--event-id", default="evt-local-replay")
    parser.add_argument("--secret", default=os.getenv("ECOPILOT_WEBHOOK_SECRET", ""))
    parser.add_argument("--print-only", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    if not args.secret:
        print("Missing --secret or ECOPILOT_WEBHOOK_SECRET", file=sys.stderr)
        return 1
    try:
        load_payload(args.payload)
    except Exception as exc:
        print(f"Invalid payload: {exc}", file=sys.stderr)
        return 1

    command = build_curl_command(
        url=args.url,
        secret=args.secret,
        event_id=args.event_id,
        payload_path=args.payload,
    )
    if args.print_only:
        print(command)
        return 0

    completed = subprocess.run(command, shell=True, check=False, text=True, capture_output=True)  # noqa: S602
    if completed.stdout:
        print(completed.stdout.strip())
    if completed.returncode != 0:
        if completed.stderr:
            print(completed.stderr.strip(), file=sys.stderr)
        return completed.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
