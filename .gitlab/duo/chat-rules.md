# EcoPilot Custom Chat Rules

## CI Optimization Guidelines

- When analyzing CI/CD pipelines, always check for:
  - Missing or misconfigured cache
  - Sequential jobs that could run in parallel
  - Redundant build steps
  - Inefficient Docker layer caching
  - Over-provisioned runner resources

- Provide quantified impact for each finding:
  - Time savings in minutes
  - Cost savings in USD (assume $0.008/min runner cost)
  - Carbon savings in kgCO2e (assume 0.02 kg/min)

- When generating fixes:
  - Only output the optimized .gitlab-ci.yml content
  - Do not include explanations or markdown code blocks
  - Follow GitLab CI/CD best practices

## Response Format

For CI analysis reports, use this structure:

```
## Findings

| Issue | Severity | Impact |
|-------|----------|--------|
| ... | ... | ... |

## Recommendations

1. ...
2. ...

## Potential Savings

- Time: X minutes per pipeline
- Cost: $X USD
- Carbon: X kgCO2e
```
