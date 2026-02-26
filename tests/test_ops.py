from ecopilot.ops import build_setup_commands, validate_required_env


def _base_env() -> dict[str, str]:
    return {
        "GCP_PROJECT": "demo-proj",
        "WEBHOOK_SECRET": "secret-123",
        "GITLAB_TOKEN": "glpat-xxx",
        "REGION": "us-central1",
    }


def test_validate_required_env_reports_missing_values() -> None:
    ok, missing = validate_required_env({"GCP_PROJECT": "demo"})
    assert ok is False
    assert "WEBHOOK_SECRET" in missing
    assert "GITLAB_TOKEN" in missing


def test_build_setup_commands_includes_core_gcp_and_run_commands() -> None:
    commands = build_setup_commands(_base_env())
    joined = "\n".join(commands)
    assert "gcloud builds submit --tag gcr.io/demo-proj/ecopilot:latest" in joined
    assert "gcloud run deploy ecopilot" in joined
    assert "ECOPILOT_WEBHOOK_SECRET=secret-123" in joined
    assert "ECOPILOT_GITLAB_TOKEN=glpat-xxx" in joined
    assert "ECOPILOT_BIGQUERY_TABLE_ID=demo-proj.ecopilot.analysis_events" in joined


def test_build_setup_commands_adds_duo_update_when_configured() -> None:
    env = _base_env()
    env["DUO_ANTHROPIC_URL"] = "https://duo.example/anthropic"
    env["DUO_ANTHROPIC_TOKEN"] = "token-abc"
    commands = build_setup_commands(env)
    joined = "\n".join(commands)
    assert "gcloud run services update ecopilot" in joined
    assert "ECOPILOT_DUO_ANTHROPIC_URL=https://duo.example/anthropic" in joined
