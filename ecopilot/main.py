from __future__ import annotations

from fastapi import FastAPI, Request

from ecopilot.anthropic_client import DuoAnthropicClient
from ecopilot.bq_sink import BigQuerySink
from ecopilot.config import Settings
from ecopilot.gcp_metrics import GCPMetricsCollector
from ecopilot.gitlab_client import GitLabClient
from ecopilot.reporter import Reporter
from ecopilot.service import EcoPilotService
from ecopilot.webhook import parse_merge_request_context, validate_secret


class _NoopBigQueryClient:
    def insert_rows_json(self, table: str, rows: list[dict]) -> list:
        _ = (table, rows)
        return []


def _build_bq_client() -> object:
    try:
        from google.cloud import bigquery

        return bigquery.Client()
    except Exception:
        return _NoopBigQueryClient()


def _build_reporter(settings: Settings) -> Reporter:
    if settings.duo_anthropic_url and settings.duo_anthropic_token:
        llm_client = DuoAnthropicClient(
            endpoint=settings.duo_anthropic_url,
            token=settings.duo_anthropic_token,
            model=settings.duo_anthropic_model,
        )
        return Reporter(llm_client=llm_client)
    return Reporter()


def create_app(
    webhook_secret: str | None = None, service: EcoPilotService | None = None
) -> FastAPI:
    settings = Settings()
    if webhook_secret is not None:
        settings.webhook_secret = webhook_secret

    app = FastAPI(title="EcoPilot")
    app.state.settings = settings
    if service is None:
        gitlab_client = GitLabClient(settings.gitlab_base_url, settings.gitlab_token)
        bq_client = _build_bq_client()
        sink = None
        if settings.bigquery_table_id:
            sink = BigQuerySink(client=bq_client, table_id=settings.bigquery_table_id)
        gcp_metrics_collector = None
        if settings.gcp_billing_table_id:
            gcp_metrics_collector = GCPMetricsCollector(
                client=bq_client,
                billing_table=settings.gcp_billing_table_id,
            )
        reporter = _build_reporter(settings)
        service = EcoPilotService(
            gitlab_client=gitlab_client,
            reporter=reporter,
            sink=sink,
            runner_cost_per_min=settings.runner_cost_per_min,
            carbon_kg_per_min=settings.carbon_kg_per_min,
            enable_auto_label=settings.enable_auto_label,
            enable_auto_issue=settings.enable_auto_issue,
            gcp_metrics_collector=gcp_metrics_collector,
            gcp_project_id=settings.gcp_project_id,
        )
    app.state.service = service

    @app.get("/health")
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/webhook/gitlab/mr")
    async def handle_merge_request_webhook(request: Request) -> dict:
        payload = await request.json()
        headers = {k.lower(): v for k, v in request.headers.items()}
        validate_secret(settings.webhook_secret, headers.get("x-gitlab-token"))
        context = parse_merge_request_context(headers, payload)
        result = app.state.service.process_event(context, payload)
        return {"status": "processed", "result": result}

    return app


app = create_app()
