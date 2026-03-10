import pytest
from ecopilot.repair import build_repair_prompt, AIRepairService
from ecopilot.models import Finding


class GuardrailLLM:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return (
            "merge_confidence: high\n"
            "rollback_note: Revert the EcoPilot MR if pipeline duration increases after merge.\n"
            "reasoning: Cache and rules changes are low risk."
        )


def test_build_repair_prompt():
    yaml_content = "stages: [test]"
    findings = [
        Finding(
            rule_id="missing_cache",
            title="Cache not configured",
            severity="high",
            evidence={"jobs": ["test"]},
            recommendation="Add cache",
            savings_ratio=0.15,
        )
    ]
    prompt = build_repair_prompt(yaml_content, findings)
    assert "stages: [test]" in prompt
    assert "missing_cache" in prompt


def test_air_repair_service_init():
    service = AIRepairService(llm_client=None)
    assert service._llm_client is None


def test_repair_service_generates_deterministic_fix_without_llm():
    ci_yaml = """
stages:
  - build
  - test

build_app:
  stage: build
  script:
    - npm ci
    - npm run build

unit_tests:
  stage: test
  script:
    - npm ci
    - npm test
  retry: 3
  timeout: 45m
"""
    findings = [
        Finding(
            rule_id="missing_cache",
            title="Cache not configured",
            severity="high",
            evidence={"jobs": ["build_app", "unit_tests"]},
            recommendation="Add cache",
            savings_ratio=0.15,
        ),
        Finding(
            rule_id="broad_test_scope",
            title="Broad test scope",
            severity="medium",
            evidence={"test_jobs": ["unit_tests"]},
            recommendation="Use rules:changes",
            savings_ratio=0.12,
        ),
        Finding(
            rule_id="retry_timeout_inefficiency",
            title="Retry and timeout inefficiency",
            severity="medium",
            evidence={"jobs": ["unit_tests"]},
            recommendation="Reduce retry and timeout",
            savings_ratio=0.05,
        ),
    ]

    service = AIRepairService(llm_client=None)
    result = service.generate_fix(ci_yaml, findings)

    assert result is not None
    assert "cache:" in result
    assert "key: ${CI_COMMIT_REF_SLUG}" in result
    assert "rules:" in result
    assert "changes:" in result
    assert "retry: 1" in result
    assert "timeout: 20m" in result


def test_repair_service_uses_llm_for_guardrail_assessment():
    findings = [
        Finding(
            rule_id="missing_cache",
            title="Cache not configured",
            severity="high",
            evidence={"jobs": ["build_app"]},
            recommendation="Add cache",
            savings_ratio=0.15,
        )
    ]
    llm = GuardrailLLM()
    service = AIRepairService(llm_client=llm)

    assessment = service.assess_remediation(
        ci_yaml="build_app:\n  script: [npm ci]\n",
        findings=findings,
        fix_content="cache:\n  key: ${CI_COMMIT_REF_SLUG}\n",
    )

    assert assessment["merge_confidence"] == "high"
    assert "Revert the EcoPilot MR" in assessment["rollback_note"]
    assert llm.prompts


class InvalidFixLLM:
    def generate(self, prompt: str) -> str:
        _ = prompt
        return "definitely not yaml for gitlab ci"


def test_repair_service_rejects_invalid_llm_fix_and_falls_back_to_deterministic_fix():
    ci_yaml = """
build_app:
  script:
    - npm ci
test_app:
  script:
    - npm test
  retry: 3
  timeout: 45m
"""
    findings = [
        Finding(
            rule_id="missing_cache",
            title="Cache not configured",
            severity="high",
            evidence={"jobs": ["build_app", "test_app"]},
            recommendation="Add cache",
            savings_ratio=0.15,
        )
    ]

    service = AIRepairService(llm_client=InvalidFixLLM())
    result = service.generate_fix(ci_yaml, findings)

    assert result is not None
    assert "cache:" in result
    assert "definitely not yaml for gitlab ci" not in result
