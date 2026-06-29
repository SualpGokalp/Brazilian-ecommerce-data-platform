with source as (

    select * from {{ source('bronze', 'order_payments') }}

),

cleaned as (

    select
        order_id,
        cast(payment_sequential as integer)   as payment_sequential,
        payment_type,
        cast(payment_installments as integer) as payment_installments,
        cast(payment_value as numeric)        as payment_value

    from source

)

select * from cleaned