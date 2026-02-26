CREATE OR REPLACE VIEW `demo.dataset.vw_ci_sustainability_trend` AS
SELECT
  DATE(timestamp) AS event_date,
  COUNT(*) AS analyses,
  SUM(baseline_cost_usd) AS baseline_cost_usd,
  SUM(projected_savings_cost_usd) AS projected_savings_cost_usd,
  SUM(baseline_carbon_kgco2e) AS baseline_carbon_kgco2e,
  SUM(projected_savings_carbon_kgco2e) AS projected_savings_carbon_kgco2e
FROM `demo.dataset.analysis_events`
GROUP BY event_date
ORDER BY event_date DESC;

CREATE OR REPLACE VIEW `demo.dataset.vw_top_rules` AS
SELECT
  rule_id,
  COUNT(*) AS hit_count
FROM `demo.dataset.analysis_events`,
UNNEST(top_rule_ids) AS rule_id
GROUP BY rule_id
ORDER BY hit_count DESC;
