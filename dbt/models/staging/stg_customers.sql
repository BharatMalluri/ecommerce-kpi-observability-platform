-- stg_customers: clean and standardise raw customers
with source as (
    select * from {{ source('raw', 'customers') }}
),

cleaned as (
    select
        customer_id                                         as customer_id,
        trim(name)                                          as customer_name,
        lower(trim(email))                                  as email,
        signup_date::timestamp                              as signup_date,
        date_trunc('day', signup_date::timestamp)::date     as signup_date_day,
        upper(trim(country))                                as country,
        loaded_at
    from source
    where customer_id is not null
      and email is not null
)

select * from cleaned
