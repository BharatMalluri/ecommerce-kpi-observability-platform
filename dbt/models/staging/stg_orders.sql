-- stg_orders: clean and standardise raw orders
with source as (
    select * from {{ source('raw', 'orders') }}
),

cleaned as (
    select
        order_id                                            as order_id,
        customer_id                                         as customer_id,
        product_id                                          as product_id,
        order_date::timestamp                               as order_date,
        date_trunc('day', order_date::timestamp)::date      as order_date_day,
        lower(trim(status))                                 as status,
        coalesce(amount, 0)                                 as amount,
        coalesce(quantity, 1)                               as quantity,
        upper(trim(country))                                as country,
        loaded_at
    from source
    where order_id is not null
)

select * from cleaned
