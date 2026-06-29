-- order_items'ı sipariş bazında özetle
with order_items_summary as (

    select
        order_id,
        count(*)           as item_count,
        sum(price)         as total_price,
        sum(freight_value) as total_freight
    from {{ ref('stg_order_items') }}
    group by order_id

),

-- siparişleri özetle birleştir
final as (

    select
        o.order_id,
        o.customer_id,
        o.order_status,
        o.order_purchase_timestamp,
        o.order_delivered_customer_date,
        i.item_count,
        i.total_price,
        i.total_freight
    from {{ ref('stg_orders') }} as o
    left join order_items_summary as i
        on o.order_id = i.order_id

)

select * from final