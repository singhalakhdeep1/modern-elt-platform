# Architecture — Modern ELT Platform

## Overview

The Modern ELT Platform simulates a data engineering extraction, load, and transform pipeline. Source contracts define which tables to extract from which systems. Extractors generate raw source files. A data quality layer validates extracted rows before promotion. The entire pipeline is stdlib-only Python — no Airbyte, dbt, or Snowflake dependency in the demo.

## Component Diagram

```mermaid
flowchart TD
    subgraph Contracts["Source Contracts"]
        SC["extractors/source_contracts.json\n{sources: [{name, tables[]}]}"]
    end

    subgraph Extract["Extract Layer"]
        GRS["extractors/generate_raw_sources.py\nload_contracts()\nbuild_rows()  — synthetic rows\nwrites raw_data/{source}_{table}.json"]
    end

    subgraph RawData["Raw Data Store"]
        Raw["extractors/raw_data/\n*.json  (one file per source+table)"]
    end

    subgraph Quality["Data Quality Layer"]
        DQ["data_quality/check_quality.py\n- null checks\n- type validation\n- row count thresholds\nwrites quality_summary.json"]
    end

    subgraph Transform["Transform / Gold"]
        Demo["run_local_demo.py\n(simulates dbt models)\nreads raw → applies transforms\nwrites gold output"]
    end

    subgraph Ops["Ops / CI"]
        LoadTest["ops/loadtest/run_load_test.py\nthroughput bench: 6000 iterations\nSLO: ≥ 30 000 rows/sec"]
        SLO["ops/perf/validate_slo.py"]
        DepScan["ops/security/dependency_scan.py\n(confirms stdlib-only)"]
    end

    subgraph K8s["Kubernetes"]
        Staging["staging worker  2 replicas"]
        Prod["prod worker  3 replicas"]
        Canary["canary  1 replica"]
    end

    SC --> GRS
    GRS --> Raw
    Raw --> DQ
    DQ --> Transform
    GRS -.->|"perf bench"| LoadTest
    LoadTest --> SLO
    Transform --> Staging & Prod & Canary
```

## Data Flow

1. **Contract read** — `load_contracts()` reads `source_contracts.json` to discover sources and tables
2. **Row generation** — `build_rows(source, table)` generates synthetic rows with `row_id`, `payload`, `ingested_at`
3. **Raw write** — One JSON file per `{source}_{table}` pair written to `extractors/raw_data/`
4. **Quality check** — `check_quality.py` validates null rates, row counts, and type consistency; writes quality summary
5. **Transform** — `run_local_demo.py` applies column projections and aggregations (simulating dbt models)
6. **SLO gate** — Throughput benchmark ensures `build_rows()` sustains ≥ 30 000 rows/sec in CI

## Source Contract Schema

```json
{
  "sources": [
    {
      "name": "payments_db",
      "tables": ["transactions", "refunds", "chargebacks"]
    }
  ]
}
```

## Key Design Decisions

| Decision                   | Rationale                                                                             |
| -------------------------- | ------------------------------------------------------------------------------------- |
| Contract-driven extraction | Schema is declared before running — prevents extracting undeclared tables             |
| Synthetic row generation   | Demo-portable without real DB connectivity; swap `build_rows` for a DB cursor in prod |
| Per-table output files     | Maps naturally to partitioned S3/GCS paths in a real lakehouse                        |
| Quality before promotion   | Rows failing quality checks never reach the gold layer                                |
| Stdlib-only                | Zero dependencies; replace with Airbyte connectors and dbt models in production       |

## Production Architecture (Target)

```mermaid
flowchart LR
    Airbyte["Airbyte\n(managed connectors)"] --> RawLayer["S3 Raw Layer\n(partitioned by date)"]
    RawLayer --> dbt["dbt Cloud\n(SQL transforms + tests)"]
    dbt --> Warehouse["Snowflake / BigQuery\n(gold tables)"]
    Warehouse --> Looker["Looker / Metabase\n(BI)"]
    GreatExpectations["Great Expectations"] --> RawLayer
```

## Directory Map

```
modern-elt-platform/
├── extractors/
│   ├── generate_raw_sources.py  # extract + build rows
│   ├── source_contracts.json    # schema declaration
│   └── raw_data/                # output JSON files
├── data_quality/
│   └── check_quality.py         # row-level validation
├── run_local_demo.py            # end-to-end demo
├── tests/test_elt_scripts.py
├── deploy/k8s/
│   ├── staging/ prod/ canary/
├── ops/
│   ├── alerts/ loadtest/ perf/ runbooks/ security/
└── .github/workflows/ci.yml
```
