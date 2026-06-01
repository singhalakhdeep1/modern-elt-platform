# Security Policy — Modern ELT Platform

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 1.x     | ✅ Yes    |
| < 1.0   | ❌ No     |

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Report security issues to: **security@alakhdeepsingh.dev**

Include in your report:

- Description of the vulnerability and its impact
- Steps to reproduce or proof-of-concept
- Affected component (extractors, source contracts, data quality, transforms)
- Suggested remediation if known

We acknowledge reports within **48 hours** and aim to provide a resolution timeline within **7 days**.

## Security Controls

### Dependency Management

- This project uses Python 3.12 standard library only (zero third-party runtime dependencies)
- `ops/security/dependency_scan.py` runs on every CI push — confirms stdlib-only posture
- SBOM is maintained at `ops/security/sbom.txt` (SPDX 2.3 format)

### Source Contract Security

- `source_contracts.json` defines the allowed extraction schema — any source not listed is rejected
- Source credentials (DB connection strings, API keys) are loaded from environment variables only — never from source_contracts.json
- Raw extracted data is written to `extractors/raw_data/` which is excluded from version control

### Data Quality Security

- Quality checks run before data is promoted to the gold layer
- Malformed records are quarantined, not silently dropped — full lineage is preserved
- Quality report output never contains raw row values, only aggregate statistics

### Container Security

- Worker images are built from `python:3.12-slim`
- No secrets baked into images; runtime secrets injected via Kubernetes secrets

### Kubernetes Security

- Worker pods run as non-root (`runAsNonRoot: true`)
- Resource limits prevent extraction jobs from exhausting cluster nodes

## Known Limitations (Demo Scope)

This project simulates Airbyte/dbt/Snowflake ELT patterns using local files. In a production deployment:

- Replace with Airbyte for managed extraction with connector library
- Use dbt for SQL-based transformations with built-in lineage
- Store credentials in Vault or a secrets manager — never in contract files

## Security Changelog

| Date       | Change                                        |
| ---------- | --------------------------------------------- |
| 2025-06-01 | Initial security policy published             |
| 2025-06-01 | Dependency scan and SBOM added to CI pipeline |
