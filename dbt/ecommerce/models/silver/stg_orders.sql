with source as (

    select * from {{ source('bronze', 'orders') }}

),

cleaned as (

    select
        order_id,
        customer_id,
        order_status,
        -- text olan tarihleri gerçek timestamp tipine çeviriyoruz
        cast(order_purchase_timestamp as timestamp)      as order_purchase_timestamp,
cast(order_approved_at as timestamp)             as order_approved_at,
cast(order_delivered_carrier_date as timestamp)  as order_delivered_carrier_date,
cast(order_delivered_customer_date as timestamp) as order_delivered_customer_date,
cast(order_estimated_delivery_date as timestamp) as order_estimated_delivery_date
    from source

)

select * from cleaned