from __future__ import annotations

import yaml

from ecopilot.models import Finding


def build_repair_prompt(ci_yaml: str, findings: list[Finding]) -> str:
    """Build prompt for AI to generate CI fix."""
    lines = [
        "You are a GitLab CI optimization expert.",
        "Generate optimized .gitlab-ci.yml based on findings.",
        "Only return the YAML content, no explanations.",
        "",
        "Original .gitlab-ci.yml:",
        ci_yaml,
        "",
        "Findings to fix:",
    ]
    for f in findings:
        lines.append(f"- {f.rule_id}: {f.title} ({f.severity})")
        lines.append(f"  Recommendation: {f.recommendation}")
    lines.append("")
    lines.append("Return optimized .gitlab-ci.yml:")
    return "\n".join(lines)


def build_guardrail_prompt(
    ci_yaml: str, findings: list[Finding], fix_content: str
) -> str:
    lines = [
        "Assess deployment risk for this GitLab CI remediation.",
        "Return YAML with keys: merge_confidence, rollback_note, reasoning.",
        "",
        "Original CI:",
        ci_yaml,
        "",
        "Proposed fix:",
        fix_content,
        "",
        "Findings:",
    ]
    for finding in findings:
        lines.append(
            f"- {finding.rule_id}: {finding.title}; severity={finding.severity}"
        )
    return "\n".join(lines)


class AIRepairService:
    def __init__(self, llm_client: object | None = None):
        self._llm_client = llm_client

    def generate_fix(self, ci_yaml: str, findings: list[Finding]) -> str | None:
        """Generate fixed CI YAML using LLM."""
        if not findings:
            return None

        prompt = build_repair_prompt(ci_yaml, findings)

        if self._llm_client is not None:
            try:
                response = self._llm_client.generate(prompt)
                if isinstance(response, str) and response.strip():
                    validated = self._validate_fix_content(response.strip())
                    if validated is not None:
                        return validated
            except Exception:
                pass

        return self._generate_deterministic_fix(ci_yaml, findings)

    def _generate_deterministic_fix(
        self, ci_yaml: str, findings: list[Finding]
    ) -> str | None:
        try:
            config = yaml.safe_load(ci_yaml) or {}
        except Exception:
            return None

        if not isinstance(config, dict):
            return None

        rule_ids = {finding.rule_id for finding in findings}
        updated = False

        if "missing_cache" in rule_ids and "cache" not in config:
            config["cache"] = {
                "key": "${CI_COMMIT_REF_SLUG}",
                "paths": ["node_modules/", ".npm/", ".cache/pip/"],
                "policy": "pull-push",
            }
            updated = True

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

        for job_name, job_config in config.items():
            if job_name in reserved or not isinstance(job_config, dict):
                continue

            if (
                "broad_test_scope" in rule_ids
                and "test" in job_name
                and "rules" not in job_config
            ):
                job_config["rules"] = [
                    {"changes": ["src/**/*", "tests/**/*", ".gitlab-ci.yml"]},
                    {"when": "manual"},
                ]
                updated = True

            if "retry_timeout_inefficiency" in rule_ids:
                retry = job_config.get("retry")
                timeout = str(job_config.get("timeout", "")).strip().lower()
                if isinstance(retry, int) and retry > 1:
                    job_config["retry"] = 1
                    updated = True
                if timeout.endswith("m"):
                    try:
                        timeout_value = int(float(timeout[:-1]))
                    except ValueError:
                        timeout_value = 0
                    if timeout_value > 20:
                        job_config["timeout"] = "20m"
                        updated = True

        if not updated:
            return None

        return yaml.safe_dump(config, sort_keys=False)

    def _validate_fix_content(self, fix_content: str) -> str | None:
        try:
            parsed = yaml.safe_load(fix_content)
        except Exception:
            return None
        if not isinstance(parsed, dict):
            return None
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
        has_job = any(
            isinstance(value, dict)
            for key, value in parsed.items()
            if key not in reserved
        )
        has_cache = "cache" in parsed
        if not has_job and not has_cache:
            return None
        return fix_content

    def assess_remediation(
        self,
        ci_yaml: str,
        findings: list[Finding],
        fix_content: str,
    ) -> dict[str, str]:
        fallback = self._fallback_assessment(findings)
        if self._llm_client is None:
            return fallback

        prompt = build_guardrail_prompt(ci_yaml, findings, fix_content)
        try:
            response = self._llm_client.generate(prompt)
            if not isinstance(response, str) or not response.strip():
                return fallback
            parsed = yaml.safe_load(response) or {}
            if not isinstance(parsed, dict):
                return fallback
            confidence = str(
                parsed.get("merge_confidence", fallback["merge_confidence"])
            )
            rollback_note = str(parsed.get("rollback_note", fallback["rollback_note"]))
            reasoning = str(parsed.get("reasoning", fallback["reasoning"]))
            return {
                "merge_confidence": confidence,
                "rollback_note": rollback_note,
                "reasoning": reasoning,
            }
        except Exception:
            return fallback

    def _fallback_assessment(self, findings: list[Finding]) -> dict[str, str]:
        severities = {finding.severity for finding in findings}
        confidence = "medium" if "high" in severities else "high"
        return {
            "merge_confidence": confidence,
            "rollback_note": "Revert the EcoPilot MR if pipeline duration, cache behavior, or job stability gets worse after merge.",
            "reasoning": "The remediation only changes CI configuration and can be reverted with a single merge rollback.",
        }

    def create_fix_mr(
        self,
        gitlab_client: object,
        project_id: int,
        source_branch: str,
        target_branch: str,
        fix_content: str,
        original_mr_iid: int,
    ) -> dict | None:
        """Create MR with fixed CI config."""
        fix_branch = f"ecopilot-fix-mr-{original_mr_iid}"

        try:
            gitlab_client.create_branch(project_id, fix_branch, source_branch)
        except Exception:
            pass

        try:
            gitlab_client.commit_file(
                project_id,
                fix_branch,
                ".gitlab-ci.yml",
                fix_content,
                f"EcoPilot: Auto-fix CI configuration (MR !{original_mr_iid})",
            )
        except Exception:
            return None

        try:
            mr = gitlab_client.create_mr(
                project_id,
                fix_branch,
                target_branch,
                f"CI Optimization: Auto-fix for MR !{original_mr_iid}",
                f"Auto-generated by EcoPilot AI to fix CI issues.\n\n"
                f"Original MR: !{original_mr_iid}",
            )
            return {"web_url": mr.get("web_url"), "iid": mr.get("iid")}
        except Exception:
            return None
