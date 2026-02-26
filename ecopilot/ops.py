from __future__ import annotations

import argparse
import os
import sys
from typing import Sequence

REQUIRED_ENV_KEYS = ("GCP_PROJECT", "WEBHOOK_SECRET", "GITLAB_TOKEN")


def validate_required_env(env: dict[str, str]) -> tuple[bool, list[str]]:
    missing = [key for key in REQUIRED_ENV_KEYS if not str(env.get(key, "")).strip()]
    return len(missing) == 0, missing


def build_setup_commands(env: dict[str, str]) -> list[str]:
    project = env["GCP_PROJECT"]
    region = env.get("REGION", "us-central1")
    webhook_secret = env["WEBHOOK_SECRET"]
    gitlab_token = env["GITLAB_TOKEN"]
    duo_url = env.get("DUO_ANTHROPIC_URL", "").strip()
    duo_token = env.get("DUO_ANTHROPIC_TOKEN", "").strip()

    commands = [
        f"gcloud config set project {project}",
        f"gcloud builds submit --tag gcr.io/{project}/ecopilot:latest",
        f"bq mk --dataset --location=US \"{project}:ecopilot\"",
        "bq query --use_legacy_sql=false < infra/bigquery/schema.sql",
        "bq query --use_legacy_sql=false < infra/bigquery/views.sql",
        (
            "gcloud run deploy ecopilot "
            f"--image gcr.io/{project}/ecopilot:latest "
            "--platform managed "
            f"--region {region} "
            "--allow-unauthenticated "
            f"--set-env-vars ECOPILOT_WEBHOOK_SECRET={webhook_secret} "
            "--set-env-vars ECOPILOT_GITLAB_BASE_URL=https://gitlab.com/api/v4 "
            f"--set-env-vars ECOPILOT_GITLAB_TOKEN={gitlab_token} "
            "--set-env-vars ECOPILOT_RUNNER_COST_PER_MIN=0.008 "
            "--set-env-vars ECOPILOT_CARBON_KG_PER_MIN=0.02 "
            "--set-env-vars ECOPILOT_ENABLE_AUTO_LABEL=true "
            "--set-env-vars ECOPILOT_ENABLE_AUTO_ISSUE=true "
            f"--set-env-vars ECOPILOT_BIGQUERY_TABLE_ID={project}.ecopilot.analysis_events"
        ),
        "Configure GitLab webhook URL: https://<cloud-run-url>/webhook/gitlab/mr",
        f"Configure GitLab webhook secret: {webhook_secret}",
    ]

    if duo_url and duo_token:
        commands.append(
            "gcloud run services update ecopilot "
            f"--region {region} "
            f"--set-env-vars ECOPILOT_DUO_ANTHROPIC_URL={duo_url} "
            f"--set-env-vars ECOPILOT_DUO_ANTHROPIC_TOKEN={duo_token} "
            "--set-env-vars ECOPILOT_DUO_ANTHROPIC_MODEL=claude-sonnet-4-20250514"
        )

    return commands


def _parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="EcoPilot deployment helper")
    parser.add_argument("--validate-env", action="store_true", help="Validate required env vars")
    parser.add_argument("--print-commands", action="store_true", help="Print setup commands")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    env = dict(os.environ)
    should_print = args.print_commands or not args.validate_env

    ok, missing = validate_required_env(env)
    if not ok:
        print(f"Missing required env vars: {', '.join(missing)}", file=sys.stderr)
        return 1

    if args.validate_env:
        print("Environment validation passed.")

    if should_print:
        for cmd in build_setup_commands(env):
            print(cmd)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
