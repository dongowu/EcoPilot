CREATE TABLE IF NOT EXISTS `demo.dataset.analysis_events` (
  event_id STRING NOT NULL,
  timestamp TIMESTAMP NOT NULL,
  project_id STRING NOT NULL,
  mr_iid STRING NOT NULL,
  pipeline_count INT64,
  baseline_duration_min FLOAT64,
  baseline_cost_usd FLOAT64,
  baseline_carbon_kgco2e FLOAT64,
  projected_savings_duration_min FLOAT64,
  projected_savings_cost_usd FLOAT64,
  projected_savings_carbon_kgco2e FLOAT64,
  top_rule_ids ARRAY<STRING>,
  llm_mode STRING
)
PARTITION BY DATE(timestamp);
