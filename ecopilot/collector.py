from __future__ import annotations

from ecopilot.models import CollectedCIContext, MergeRequestContext


def collect_ci_context(client: object, context: MergeRequestContext, limit: int = 10) -> CollectedCIContext:
    ci_yaml = client.get_ci_config(context.project_id, context.source_branch)
    pipelines = client.list_pipelines(context.project_id, context.source_branch, limit)
    enriched: list[dict] = []
    for pipeline in pipelines:
        jobs = client.list_jobs(context.project_id, int(pipeline["id"]))
        item = dict(pipeline)
        item["jobs"] = jobs
        enriched.append(item)
    return CollectedCIContext(ci_yaml=ci_yaml, pipelines=enriched)

