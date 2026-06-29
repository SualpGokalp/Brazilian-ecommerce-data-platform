with source as (

    select * from {{ source('bronze', 'customers') }}

),

cleaned as (

    select
        customer_id,
        customer_unique_id,
        cast(customer_zip_code_prefix as integer) as customer_zip_code_prefix,
        customer_city,
        customer_state

    from source

)

select * from cleaned