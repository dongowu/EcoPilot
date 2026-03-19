from __future__ import annotations

from collections import Counter

import yaml

from ecopilot.models import Finding

DEPENDENCY_HINTS = ("npm ci", "pip install", "poetry install", "cargo build", "bundle install")


def analyze_ci(ci_yaml: str, pipelines: list[dict]) -> list[Finding]:
    cfg = yaml.safe_load(ci_yaml) or {}
    findings: list[Finding] = []

    jobs = _extract_jobs(cfg)
    if _detect_missing_cache(jobs):
        findings.append(
            Finding(
                rule_id="missing_cache",
                title="Cache is not configured for dependency-heavy jobs",
                severity="high",
                evidence={"jobs": [job["name"] for job in jobs if _job_has_dependency_install(job)]},
                recommendation="Add cache paths/keys for dependency directories to reduce repeated downloads.",
                savings_ratio=0.15,
            )
        )

    duplicate_lines = _detect_redundant_steps(jobs)
    if duplicate_lines:
        findings.append(
            Finding(
                rule_id="redundant_steps",
                title="Repeated CI steps found across jobs",
                severity="medium",
                evidence={"duplicate_script_lines": duplicate_lines},
                recommendation="Move repeated setup commands to cache, reusable templates, or before_script anchors.",
                savings_ratio=0.08,
            )
        )

    test_jobs = [job for job in jobs if "test" in job["name"]]
    if _detect_broad_test_scope(test_jobs):
        findings.append(
            Finding(
                rule_id="broad_test_scope",
                title="Test jobs run broadly without change-based filtering",
                severity="medium",
                evidence={"test_jobs": [job["name"] for job in test_jobs]},
                recommendation="Use rules:changes or path filters so expensive tests run only when relevant files change.",
                savings_ratio=0.12,
            )
        )

    retry_timeout_jobs = _detect_retry_timeout_issues(jobs)
    if retry_timeout_jobs:
        findings.append(
            Finding(
                rule_id="retry_timeout_inefficiency",
                title="Retry and timeout settings appear wasteful",
                severity="medium",
                evidence={"jobs": retry_timeout_jobs},
                recommendation="Lower retry and timeout values for flaky or bounded jobs and fix root causes.",
                savings_ratio=0.05,
            )
        )

    if _detect_serial_pipeline_structure(cfg, pipelines):
        findings.append(
            Finding(
                rule_id="serial_pipeline_structure",
                title="Pipeline appears over-serialized",
                severity="medium",
                evidence={"stages": cfg.get("stages", [])},
                recommendation="Use needs-based dependencies to parallelize independent jobs across stages.",
                savings_ratio=0.1,
            )
        )

    artifact_jobs = _detect_artifact_expiration_issues(jobs)
    if artifact_jobs:
        findings.append(
            Finding(
                rule_id="artifact_expiration",
                title="Artifacts may be retained longer than necessary",
                severity="low",
                evidence={"jobs": artifact_jobs},
                recommendation="Set expire_in to reduce artifact storage costs. Default is 30 days; consider 1-7 days for CI artifacts.",
                savings_ratio=0.03,
            )
        )

    parallel_ops = _detect_parallel_opportunities(jobs)
    if parallel_ops:
        findings.append(
            Finding(
                rule_id="parallel_opportunities",
                title="Jobs could run in parallel but are serialized",
                severity="medium",
                evidence={"jobs": parallel_ops},
                recommendation="Add needs: [] to independent jobs to run them in parallel instead of sequentially.",
                savings_ratio=0.2,
            )
        )

    resource_jobs = _detect_resource_optimization(jobs)
    if resource_jobs:
        findings.append(
            Finding(
                rule_id="resource_optimization",
                title="Jobs may be over-provisioned with resources",
                severity="low",
                evidence={"jobs": resource_jobs},
                recommendation="Review and reduce CPU/memory requests for jobs that don't need high resources.",
                savings_ratio=0.05,
            )
        )

    return findings


def _extract_jobs(cfg: dict) -> list[dict]:
    reserved = {
        "stages",
        "variables",
        "workflow",
        "default",
        "include",
        "cache",
        "before_script",
        "after_script",
        "image",
        "services",
    }
    jobs: list[dict] = []
    for name, config in cfg.items():
        if name in reserved or not isinstance(config, dict):
            continue
        scripts = config.get("script")
        if isinstance(scripts, str):
            scripts = [scripts]
        jobs.append(
            {
                "name": name,
                "stage": config.get("stage", "test"),
                "script": scripts or [],
                "cache": config.get("cache"),
                "rules": config.get("rules"),
                "retry": config.get("retry"),
                "timeout": config.get("timeout"),
                "needs": config.get("needs"),
            }
        )
    return jobs


def _job_has_dependency_install(job: dict) -> bool:
    lines = [str(line) for line in job.get("script", [])]
    return any(any(hint in line for hint in DEPENDENCY_HINTS) for line in lines)


def _detect_missing_cache(jobs: list[dict]) -> bool:
    for job in jobs:
        if _job_has_dependency_install(job) and not job.get("cache"):
            return True
    return False


def _detect_redundant_steps(jobs: list[dict]) -> list[str]:
    line_counts: Counter[str] = Counter()
    for job in jobs:
        for line in job.get("script", []):
            line_counts[str(line)] += 1
    duplicates = [line for line, count in line_counts.items() if count >= 2]
    return duplicates


def _detect_broad_test_scope(test_jobs: list[dict]) -> bool:
    if not test_jobs:
        return False
    for job in test_jobs:
        rules = job.get("rules")
        if not rules:
            return True
        rule_text = str(rules).lower()
        if "changes" not in rule_text:
            return True
    return False


def _timeout_minutes(timeout_value: object) -> int:
    if timeout_value is None:
        return 0
    value = str(timeout_value).strip().lower()
    if value.endswith("m"):
        value = value[:-1]
    try:
        return int(float(value))
    except ValueError:
        return 0


def _retry_count(value: object) -> int:
    if value is None:
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, dict):
        max_value = value.get("max")
        if isinstance(max_value, int):
            return max_value
    return 0


def _detect_retry_timeout_issues(jobs: list[dict]) -> list[str]:
    offenders: list[str] = []
    for job in jobs:
        if _retry_count(job.get("retry")) > 2 or _timeout_minutes(job.get("timeout")) > 30:
            offenders.append(job["name"])
    return offenders


def _detect_artifact_expiration_issues(jobs: list[dict]) -> list[str]:
    """Detect jobs with artifacts but no expiration policy."""
    offenders: list[str] = []
    for job in jobs:
        artifacts = job.get("artifacts")
        if artifacts and isinstance(artifacts, dict):
            if "expire_in" not in artifacts:
                offenders.append(job["name"])
    return offenders


def _detect_parallel_opportunities(jobs: list[dict]) -> list[str]:
    """Detect jobs that could run in parallel but don't have needs defined."""
    offenders: list[str] = []
    for job in jobs:
        if not job.get("needs") and job.get("stage") == "test":
            offenders.append(job["name"])
    return offenders


def _detect_resource_optimization(jobs: list[dict]) -> list[str]:
    """Detect jobs with potentially excessive resource requests."""
    offenders: list[str] = []
    for job in jobs:
        resources = job.get("resources", {})
        if isinstance(resources, dict):
            limits = resources.get("limits", {})
            if isinstance(limits, dict):
                cpu = str(limits.get("cpus", "")).strip()
                memory = str(limits.get("memory", "")).strip()
                if cpu and float(cpu.replace("m", "")) > 2000:
                    offenders.append(job["name"])
                elif memory and float(memory.replace("Mi", "").replace("Gi", "")) > 2048:
                    offenders.append(job["name"])
    return offenders



    stages = cfg.get("stages") or []
    if len(stages) < 3:
        return False

    jobs = _extract_jobs(cfg)
    has_needs = any(job.get("needs") for job in jobs)
    if not has_needs:
        return True

    total_job_count = 0
    total_stage_count = 0
    for pipeline in pipelines:
        pipeline_jobs = pipeline.get("jobs") or []
        total_job_count += len(pipeline_jobs)
        stage_names = {str(job.get("stage", "")) for job in pipeline_jobs}
        total_stage_count += len(stage_names)

    return total_job_count > 0 and total_job_count <= total_stage_count + 1

