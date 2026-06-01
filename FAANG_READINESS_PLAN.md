# Modern ELT Platform - FAANG Readiness Plan

Status: FAANG hardening phase 1 complete (demo to production transition plan implemented)
Last updated: 2026-06-01

## Target SLOs

- ELT pipeline availability: 99.9%
- Raw-to-quality-check completion p95: <= 10 minutes
- Data freshness for marts: <= 15 minutes
- Failed run ratio: < 1%
- Recovery objective (RTO): <= 60 minutes
- Data loss objective (RPO): <= 10 minutes

## Capacity Targets

- Source tables per run: 100+
- Row volume per run: 50 million
- Concurrent domain pipelines: 20

## Security Controls

- Source credential isolation and least privilege access
- Data masking for sensitive fields before serving marts
- Secrets from managed vault provider
- Dependency and image vulnerability scanning

## Reliability and Operations

- Data quality dashboards for completeness and validity
- Alerting on quality failures and freshness breaches
- Backfill and replay runbook for failed domains
- Synthetic checks for extractor and quality paths

## Delivery Gates

- Local demo run required in CI
- Unit tests for extraction and quality logic required
- Contract updates must include migration notes

## Acceptance Criteria

- [x] Release checklist present and maintained
- [x] CI pipeline present and validates demo + tests
- [x] Quality summary artifact in place
- [x] Explicit SLO, security, and reliability targets documented
- [x] Automated readiness audit script present
