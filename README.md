# Modern ELT Platform with dbt

Warehouse-first ELT system that consolidates CRM, billing, support, and product data into analytics-ready models with tests and lineage.

## Stack

- Extractors: Python
- Orchestration: Airflow
- Warehouse: PostgreSQL local starter, later BigQuery or Snowflake equivalent
- Modeling: dbt
- Data quality: Great Expectations
- BI: Metabase or Power BI

## Domains

- Revenue and subscriptions
- Product usage
- Support performance
- Sales pipeline

## First build milestone

1. Source simulation tables
2. Raw ingestion DAGs
3. dbt staging, intermediate, and marts models
4. Freshness and uniqueness tests
5. KPI dashboard for MRR, churn, and activation

## Implemented baseline

- Source-contract driven raw-data generation script for CRM, billing, support, and product domains
- Airflow DAG wiring extraction and quality validation stages
- Data-quality script validating row IDs and payload shape in generated raw data
- dbt seed-style staging model and revenue mart SQL model
- Unit tests for source-row generation and quality-rule behavior

## Run local scripts

```bash
cd extractors
python generate_raw_sources.py

cd ../data_quality
python check_quality.py
```

## One-command local demo

```bash
python run_local_demo.py
```

Generated artifacts:

- `extractors/raw_data/*.json`
- Data-quality summary printed as JSON (`passed`, `invalid_payloads`, `null_row_ids`)
- `data_quality/quality_summary.json`

## Validate

```bash
cd tests
python -m unittest discover -s . -p "test_*.py"
```

## Planned data model layers

1. Staging: domain-normalized source tables (`stg_*`).
2. Intermediate: reusable business-logic joins.
3. Marts: revenue, product usage, and support performance KPIs.

## Planned quality gates

- Freshness checks per source domain
- Uniqueness checks on key identifiers
- Accepted values for status fields
- Null-threshold alerts on critical columns

---

## License

Proprietary - All rights reserved.
