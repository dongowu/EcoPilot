from ecopilot.rules import analyze_ci


def test_rule_engine_detects_expected_waste_patterns() -> None:
    ci_yaml = """
stages:
  - build
  - test
  - deploy

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

e2e_tests:
  stage: test
  script:
    - npm ci
    - npm run test:e2e
  retry: 3
  timeout: 45m

deploy_app:
  stage: deploy
  script:
    - ./deploy.sh
"""
    pipelines = [
        {
            "id": 1,
            "duration": 1800,
            "status": "success",
            "jobs": [
                {"name": "build_app", "stage": "build", "duration": 600},
                {"name": "unit_tests", "stage": "test", "duration": 700},
                {"name": "e2e_tests", "stage": "test", "duration": 500},
            ],
        }
    ]

    findings = analyze_ci(ci_yaml, pipelines)
    rule_ids = {finding.rule_id for finding in findings}
    assert "missing_cache" in rule_ids
    assert "redundant_steps" in rule_ids
    assert "broad_test_scope" in rule_ids
    assert "retry_timeout_inefficiency" in rule_ids
    assert "serial_pipeline_structure" in rule_ids
