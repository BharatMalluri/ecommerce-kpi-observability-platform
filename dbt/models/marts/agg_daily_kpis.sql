-- agg_daily_kpis: daily aggregated KPIs for dashboard and anomaly detection
{{
  config(materialized='table')
}}

with orders as (
    select * from {{ ref('fct_orders') }}
),

daily as (
    select
        order_date_day                              as date,
        count(*)                                    as total_orders,
        count(distinct customer_id)                 as unique_customers,
        sum(revenue)                                as total_revenue,
        avg(amount)                                 as avg_order_value,
        sum(quantity)                               as total_items_sold,
        count(case when status = 'cancelled' then 1 end) as cancelled_orders,
        count(case when status = 'refunded'  then 1 end) as refunded_orders,
        count(case when status = 'pending'   then 1 end) as pending_orders,
        round(
            count(case when status = 'cancelled' then 1 end)::numeric
            / nullif(count(*), 0) * 100, 2
        )                                           as cancellation_rate_pct
    from orders
    group by order_date_day
),

with_rolling as (
    select
        *,
        avg(total_revenue) over (
            order by date rows between 6 preceding and current row
        )                                           as revenue_7d_avg,
        avg(total_orders) over (
            order by date rows between 6 preceding and current row
        )                                           as orders_7d_avg
    from daily
)

select * from with_rolling
order by date desc
