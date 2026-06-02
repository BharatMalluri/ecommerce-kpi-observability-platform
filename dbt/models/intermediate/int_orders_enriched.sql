-- int_orders_enriched: join orders with customers and products
with orders as (
    select * from {{ ref('stg_orders') }}
),

customers as (
    select * from {{ ref('stg_customers') }}
),

products as (
    select * from {{ ref('stg_products') }}
),

enriched as (
    select
        o.order_id,
        o.order_date,
        o.order_date_day,
        o.status,
        o.amount,
        o.quantity,
        o.country                           as order_country,

        -- Customer fields
        o.customer_id,
        c.customer_name,
        c.email,
        c.signup_date,
        c.country                           as customer_country,

        -- Product fields
        o.product_id,
        p.product_name,
        p.category,
        p.unit_price,

        -- Derived
        (o.quantity * p.unit_price)         as expected_amount,
        abs(o.amount - (o.quantity * p.unit_price)) as amount_discrepancy,
        case
            when o.status = 'completed' then o.amount
            else 0
        end                                 as revenue

    from orders o
    left join customers c using (customer_id)
    left join products  p using (product_id)
)

select * from enriched
