# EcoPilot Deployment Runbook (GitLab + GCP)

## 1) Prerequisites

- GitLab project with MR webhook permission.
- Google Cloud project with Cloud Run + BigQuery enabled.
- Service account for Cloud Run with BigQuery write permission.
- GitLab access token (API scope for project read + MR note/issue write).

## 2) Build and Push Container

You can print all setup commands from current env:

```bash
./scripts/print_setup_commands.sh
```

```bash
gcloud builds submit --tag gcr.io/$GCP_PROJECT/ecopilot:latest
```

## 3) Create BigQuery Dataset/Table

```bash
bq mk --dataset --location=US "$GCP_PROJECT:ecopilot"
bq query --use_legacy_sql=false < infra/bigquery/schema.sql
bq query --use_legacy_sql=false < infra/bigquery/views.sql
```

## 4) Deploy to Cloud Run

```bash
gcloud run deploy ecopilot \
  --image gcr.io/$GCP_PROJECT/ecopilot:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ECOPILOT_WEBHOOK_SECRET=$WEBHOOK_SECRET \
  --set-env-vars ECOPILOT_GITLAB_BASE_URL=https://gitlab.com/api/v4 \
  --set-env-vars ECOPILOT_GITLAB_TOKEN=$GITLAB_TOKEN \
  --set-env-vars ECOPILOT_RUNNER_COST_PER_MIN=0.008 \
  --set-env-vars ECOPILOT_CARBON_KG_PER_MIN=0.02 \
  --set-env-vars ECOPILOT_ENABLE_AUTO_LABEL=true \
  --set-env-vars ECOPILOT_ENABLE_AUTO_ISSUE=true \
  --set-env-vars ECOPILOT_BIGQUERY_TABLE_ID=$GCP_PROJECT.ecopilot.analysis_events
```

Optional Anthropic (Duo endpoint) wiring:

```bash
gcloud run services update ecopilot \
  --region us-central1 \
  --set-env-vars ECOPILOT_DUO_ANTHROPIC_URL=$DUO_ANTHROPIC_URL \
  --set-env-vars ECOPILOT_DUO_ANTHROPIC_TOKEN=$DUO_ANTHROPIC_TOKEN \
  --set-env-vars ECOPILOT_DUO_ANTHROPIC_MODEL=claude-sonnet-4-20250514
```

## 5) Configure GitLab Webhook

- URL: `https://<cloud-run-url>/webhook/gitlab/mr`
- Secret token: same value as `ECOPILOT_WEBHOOK_SECRET`
- Trigger: Merge request events

## 6) Smoke Tests

1. `GET /health` returns `{"status":"ok"}`.
2. Update an MR and verify:
   - MR receives EcoPilot comment.
   - Comment includes `<!-- ecopilot:event_id=... -->` marker.
   - Label is applied (`ci-waste-detected`) if findings exist.
   - Follow-up issue is created when high-severity finding exists.
   - Replaying same webhook event id does not create additional comments/labels/issues.
3. Check BigQuery table for new row with expected `event_id`.

Local replay helper:

```bash
ECOPILOT_WEBHOOK_SECRET=$WEBHOOK_SECRET ./scripts/replay_webhook.sh --print-only
ECOPILOT_WEBHOOK_SECRET=$WEBHOOK_SECRET ./scripts/replay_webhook.sh
```

## 7) Looker Studio Dashboard

- Data source: `ecopilot.analysis_events` plus views:
  - `vw_ci_sustainability_trend`
  - `vw_top_rules`
- Minimum charts:
  - baseline vs projected savings (cost and kgCO2e)
  - trend over time
  - top triggered rule IDs

## 8) Troubleshooting

- 401 webhook errors: secret mismatch.
- 500 after webhook: check GitLab token permissions.
- No BigQuery rows: validate table id and service account IAM.
- No LLM output: verify Duo endpoint/token; fallback report should still post.
