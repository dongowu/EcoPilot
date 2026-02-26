from __future__ import annotations

from ecopilot.action import ActionPublisher
from ecopilot.analyzer import run_analysis
from ecopilot.collector import collect_ci_context
from ecopilot.models import MergeRequestContext
from ecopilot.reporter import Reporter


class NullSink:
    def write(self, **_: object) -> None:
        return None


class EcoPilotService:
    """Coordinates the deterministic analyzer, reporting, and persistence path."""

    def __init__(
        self,
        gitlab_client: object,
        collector=collect_ci_context,
        reporter: Reporter | None = None,
        publisher: ActionPublisher | None = None,
        sink: object | None = None,
        runner_cost_per_min: float = 0.008,
        carbon_kg_per_min: float = 0.02,
        enable_auto_label: bool = False,
        enable_auto_issue: bool = False,
    ):
        self._gitlab_client = gitlab_client
        self._collector = collector
        self._reporter = reporter or Reporter()
        self._publisher = publisher or ActionPublisher(gitlab_client)
        self._sink = sink or NullSink()
        self._runner_cost_per_min = runner_cost_per_min
        self._carbon_kg_per_min = carbon_kg_per_min
        self._enable_auto_label = enable_auto_label
        self._enable_auto_issue = enable_auto_issue

    def process_event(self, context: MergeRequestContext, payload: dict) -> dict:
        _ = payload
        if self._publisher.is_duplicate_event(context):
            return {
                "event_id": context.event_id,
                "project_id": context.project_id,
                "mr_iid": context.mr_iid,
                "comment_posted": False,
                "label_applied": False,
                "issue_created": False,
                "finding_count": 0,
                "llm_mode": "skipped",
                "status": "duplicate",
            }

        collected = self._collector(self._gitlab_client, context, limit=10)
        findings, impact = run_analysis(
            ci_yaml=collected.ci_yaml,
            pipelines=collected.pipelines,
            runner_cost_per_min=self._runner_cost_per_min,
            carbon_kg_per_min=self._carbon_kg_per_min,
        )
        body, llm_mode = self._reporter.render(context, findings, impact)
        posted = self._publisher.publish_comment(context, body)
        optional_actions = {"label_applied": False, "issue_created": False}
        if posted:
            optional_actions = self._publisher.apply_optional_actions(
                context=context,
                findings=findings,
                enable_auto_label=self._enable_auto_label,
                enable_auto_issue=self._enable_auto_issue,
            )
            self._sink.write(
                context=context,
                findings=findings,
                impact=impact,
                llm_mode=llm_mode,
                pipeline_count=len(collected.pipelines),
            )
        return {
            "event_id": context.event_id,
            "project_id": context.project_id,
            "mr_iid": context.mr_iid,
            "comment_posted": posted,
            "label_applied": optional_actions["label_applied"],
            "issue_created": optional_actions["issue_created"],
            "finding_count": len(findings),
            "llm_mode": llm_mode,
            "status": "processed",
        }
