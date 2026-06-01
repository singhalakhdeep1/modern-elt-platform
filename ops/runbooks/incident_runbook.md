# Incident Runbook - Modern ELT Platform

## Triggers

- Data quality failure alerts
- Freshness SLO breach
- Extractor pipeline timeouts

## Immediate Steps

1. Identify failing source domain and affected marts.
2. Verify extractor and quality check job logs.
3. Stop downstream publication for invalid datasets.
4. Reprocess last known good batch if needed.

## Recovery Steps

1. Restore extractor and quality check success path.
2. Execute `python run_local_demo.py` for baseline validation.
3. Confirm quality summary returns `passed: true`.

## Post-Incident

1. Record root cause and data impact.
2. Add tests for failing schema or quality condition.
3. Update source contract migration notes.
