-- fct_orders: fact table — one row per order, fully enriched
{{
  config(
    materialized='table',
    indexes=[
      {'columns': ['order_date_day']},
      {'columns': ['customer_id']},
      {'columns': ['status']}
    ]
  )
}}

with base as (
    select * from {{ ref('int_orders_enriched') }}
)

select
    order_id,
    order_date,
    order_date_day,
    status,
    amount,
    quantity,
    revenue,
    expected_amount,
    amount_discrepancy,
    order_country,
    customer_id,
    customer_name,
    email,
    signup_date,
    customer_country,
    product_id,
    product_name,
    category,
    unit_price
from base
