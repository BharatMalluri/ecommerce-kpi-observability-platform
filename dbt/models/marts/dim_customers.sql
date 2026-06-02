-- dim_customers: customer dimension with lifetime value metrics
{{
  config(materialized='table')
}}

with customers as (
    select * from {{ ref('stg_customers') }}
),

order_stats as (
    select
        customer_id,
        count(*)                            as total_orders,
        sum(revenue)                        as lifetime_value,
        avg(amount)                         as avg_order_value,
        min(order_date_day)                 as first_order_date,
        max(order_date_day)                 as last_order_date,
        count(case when status = 'cancelled' then 1 end) as cancelled_orders,
        count(case when status = 'refunded'  then 1 end) as refunded_orders
    from {{ ref('fct_orders') }}
    group by customer_id
)

select
    c.customer_id,
    c.customer_name,
    c.email,
    c.country,
    c.signup_date,

    coalesce(o.total_orders, 0)         as total_orders,
    coalesce(o.lifetime_value, 0)       as lifetime_value,
    coalesce(o.avg_order_value, 0)      as avg_order_value,
    o.first_order_date,
    o.last_order_date,
    coalesce(o.cancelled_orders, 0)     as cancelled_orders,
    coalesce(o.refunded_orders, 0)      as refunded_orders,

    case
        when coalesce(o.lifetime_value, 0) >= 1000 then 'high'
        when coalesce(o.lifetime_value, 0) >= 300  then 'medium'
        else 'low'
    end                                 as customer_segment

from customers c
left join order_stats o using (customer_id)
