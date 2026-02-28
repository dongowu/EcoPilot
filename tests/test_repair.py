import pytest
from ecopilot.repair import build_repair_prompt, AIRepairService
from ecopilot.models import Finding


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
