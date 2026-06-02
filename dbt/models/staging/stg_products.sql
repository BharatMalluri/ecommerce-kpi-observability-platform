-- stg_products: clean and standardise raw products
with source as (
    select * from {{ source('raw', 'products') }}
),

cleaned as (
    select
        product_id                      as product_id,
        trim(name)                      as product_name,
        trim(category)                  as category,
        price                           as unit_price,
        loaded_at
    from source
    where product_id is not null
      and price > 0
)

select * from cleaned
