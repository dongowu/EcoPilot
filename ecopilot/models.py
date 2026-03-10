from __future__ import annotations

from pydantic import BaseModel


class MergeRequestContext(BaseModel):
    project_id: int
    mr_iid: int
    source_branch: str
    target_branch: str
    commit_sha: str
    event_id: str


class CollectedCIContext(BaseModel):
    ci_yaml: str
    pipelines: list[dict]


class Finding(BaseModel):
    rule_id: str
    title: str
    severity: str
    evidence: dict
    recommendation: str
    savings_ratio: float


class ImpactSummary(BaseModel):
    baseline_duration_min: float
    baseline_cost_usd: float
    baseline_carbon_kgco2e: float
    projected_savings_duration_min: float
    projected_savings_cost_usd: float
    projected_savings_carbon_kgco2e: float


class CloudImpactSummary(BaseModel):
    provider: str
    estimated_monthly_cost_usd: float
    estimated_monthly_savings_usd: float
    estimated_annual_savings_usd: float
    estimated_monthly_carbon_kgco2e: float
    top_services: list[str]
