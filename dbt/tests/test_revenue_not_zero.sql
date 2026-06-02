-- tests/test_revenue_not_zero.sql
-- Fails if total revenue in the last 7 days is zero (pipeline or data issue)
select
    date,
    total_revenue
from {{ ref('agg_daily_kpis') }}
where date >= current_date - interval '7 days'
  and total_revenue = 0
