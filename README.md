# P1 E-Commerce Data Pipeline

> **Production-style data engineering portfolio project** — built to match Germany enterprise job expectations.

![CI](https://github.com/YOUR_USERNAME/p1-ecommerce-pipeline/actions/workflows/ci.yml/badge.svg)

---

## Architecture

```
CSV/API e-commerce data
        │
        ▼
┌───────────────────┐
│  Great Expectations│  ← Schema + quality validation on ingest
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│   Airflow DAGs    │  ← Orchestration (ingest → dbt → tests)
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ PostgreSQL (raw)  │  ← Raw schema: orders, customers, products
└────────┬──────────┘
         │
         ▼
┌───────────────────────────────────┐
│  dbt: staging → intermediate      │  ← Clean, join, enrich
│       → marts (fct/dim/agg)       │
└────────┬──────────────────────────┘
         │
         ├──► dbt tests + anomaly tables  ← Business data quality
         │
         ▼
┌───────────────────┐     ┌─────────────────────┐
│ Prometheus+Grafana│     │   Slack Alerts       │
│ (pipeline ops)    │     │   (KPI drift/breaks) │
└───────────────────┘     └─────────────────────┘
         │
         ▼
┌───────────────────┐
│ Streamlit Dashboard│  ← Data quality + KPI visibility
└───────────────────┘
```

## Stack

| Layer | Tool | Version |
|---|---|---|
| Orchestration | Apache Airflow | 2.9.1 |
| Transformation | dbt-postgres | 1.8.0 |
| Validation | Great Expectations | 0.18.14 |
| Storage | PostgreSQL | 15 |
| Monitoring | Prometheus + Grafana | 2.52 / 10.4 |
| Dashboard | Streamlit | 1.35.0 |
| Alerting | Slack SDK | 3.27.1 |

---

## Quick Start

### Prerequisites
- Docker + Docker Compose
- Python 3.11+
- `git`

### 1. Clone and configure
```bash
git clone https://github.com/YOUR_USERNAME/p1-ecommerce-pipeline.git
cd p1-ecommerce-pipeline
cp .env.example .env
# Edit .env with your values
```

### 2. Start the stack
```bash
docker compose up -d
```

| Service | URL | Credentials |
|---|---|---|
| Airflow | http://localhost:8080 | admin / admin |
| Grafana | http://localhost:3000 | admin / admin |
| Prometheus | http://localhost:9090 | — |
| Streamlit | http://localhost:8501 | — |

### 3. Seed data
```bash
pip install -r requirements.txt
python scripts/seed_postgres.py
```

### 4. Set up dbt
```bash
cp dbt/profiles.yml.example dbt/profiles.yml
cd dbt
dbt deps
dbt build
```

### 5. Trigger Airflow DAGs
Go to http://localhost:8080 → unpause `ingest_orders` → trigger manually.

---

## dbt Models

```
models/
├── staging/          # Clean raw data (views)
│   ├── stg_orders.sql
│   ├── stg_customers.sql
│   └── stg_products.sql
├── intermediate/     # Joins + enrichment (ephemeral)
│   └── int_orders_enriched.sql
└── marts/            # Business-ready tables
    ├── fct_orders.sql        # Fact table
    ├── dim_customers.sql     # Customer LTV + segments
    └── agg_daily_kpis.sql    # Daily KPIs + 7d rolling avg
```

## Data Quality

**Great Expectations** validates on ingest:
- Schema presence
- Null checks
- Value ranges
- Status enum enforcement

**dbt tests** validate after transformation:
- `not_null`, `unique` on all keys
- `accepted_values` for status fields
- Range checks via `dbt_expectations`
- Singular tests for revenue freshness

**Anomaly log** in `monitoring.anomaly_log` — every mart post-hook writes a row count check result.

---

## Project Structure

```
p1-ecommerce-pipeline/
├── .github/workflows/ci.yml       # GitHub Actions CI
├── airflow/dags/                  # Airflow DAGs
├── dbt/                           # dbt project
│   ├── models/staging/
│   ├── models/intermediate/
│   ├── models/marts/
│   ├── macros/
│   └── tests/
├── great_expectations/            # GE config + expectations
├── monitoring/                    # Prometheus + Grafana
├── streamlit/                     # Dashboard app
├── scripts/                       # Seed + init scripts
├── docker-compose.yml
└── requirements.txt
```

---

## Skills Demonstrated

- ✅ ELT pipeline design (ingest → validate → transform → serve)
- ✅ dbt modelling (staging / intermediate / marts pattern)
- ✅ Data quality framework (GE + dbt tests + anomaly tables)
- ✅ Orchestration with Airflow (DAGs, sensors, retries)
- ✅ Warehouse modelling in PostgreSQL
- ✅ Operational monitoring (Prometheus + Grafana)
- ✅ Production mindset (CI, logging, alerting, documentation)
