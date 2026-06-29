with customers as (

    select * from {{ ref('stg_customers') }}

),

final as (

    select
        customer_id,
        customer_unique_id,
        customer_city,
        customer_state,
        customer_zip_code_prefix
    from customers

)

select * from final