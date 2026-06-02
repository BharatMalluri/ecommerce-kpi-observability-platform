-- Initialise schemas for the e-commerce pipeline
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS intermediate;
CREATE SCHEMA IF NOT EXISTS marts;
CREATE SCHEMA IF NOT EXISTS monitoring;

-- Raw orders table
CREATE TABLE IF NOT EXISTS raw.orders (
    order_id        VARCHAR(50),
    customer_id     VARCHAR(50),
    order_date      TIMESTAMP,
    status          VARCHAR(30),
    amount          NUMERIC(10,2),
    product_id      VARCHAR(50),
    quantity        INTEGER,
    country         VARCHAR(50),
    loaded_at       TIMESTAMP DEFAULT NOW()
);

-- Raw customers table
CREATE TABLE IF NOT EXISTS raw.customers (
    customer_id     VARCHAR(50),
    name            VARCHAR(100),
    email           VARCHAR(100),
    signup_date     TIMESTAMP,
    country         VARCHAR(50),
    loaded_at       TIMESTAMP DEFAULT NOW()
);

-- Raw products table
CREATE TABLE IF NOT EXISTS raw.products (
    product_id      VARCHAR(50),
    name            VARCHAR(100),
    category        VARCHAR(50),
    price           NUMERIC(10,2),
    loaded_at       TIMESTAMP DEFAULT NOW()
);

-- Monitoring: anomaly log
CREATE TABLE IF NOT EXISTS monitoring.anomaly_log (
    id              SERIAL PRIMARY KEY,
    check_name      VARCHAR(100),
    table_name      VARCHAR(100),
    metric_value    NUMERIC,
    threshold       NUMERIC,
    status          VARCHAR(20),
    detected_at     TIMESTAMP DEFAULT NOW()
);

-- Monitoring: pipeline run log
CREATE TABLE IF NOT EXISTS monitoring.pipeline_runs (
    id              SERIAL PRIMARY KEY,
    dag_id          VARCHAR(100),
    run_id          VARCHAR(100),
    status          VARCHAR(20),
    rows_loaded     INTEGER,
    started_at      TIMESTAMP,
    finished_at     TIMESTAMP DEFAULT NOW()
);
