from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    webhook_secret: str = ""
    gitlab_base_url: str = "https://gitlab.com/api/v4"
    gitlab_token: str = ""
    runner_cost_per_min: float = 0.008
    carbon_kg_per_min: float = 0.02
    enable_auto_label: bool = False
    enable_auto_issue: bool = False
    bigquery_table_id: str = ""
    gcp_billing_table_id: str = ""
    gcp_project_id: str = ""
    duo_anthropic_url: str = ""
    duo_anthropic_token: str = ""
    duo_anthropic_model: str = "claude-sonnet-4-20250514"
    model_config = SettingsConfigDict(env_prefix="ECOPILOT_", extra="ignore")
