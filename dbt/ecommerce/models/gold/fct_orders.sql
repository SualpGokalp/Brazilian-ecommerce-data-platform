-- Sipariş bazlı fact tablosu — INCREMENTAL.
-- İlk çalıştırmada tüm siparişleri kurar; sonrakilerde yalnızca en son
-- yüklenen tarihten daha yeni siparişleri işler (tam yeniden kurma yok).
{{
    config(
        materialized='incremental',
        unique_key='order_id',
        incremental_strategy='delete+insert'
    )
}}

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

-- siparişler (incremental çalışmada sadece yeni olanlar)
orders as (

    select * from {{ ref('stg_orders') }}

    {% if is_incremental() %}
    -- {{ this }} = bu modelin mevcut hali; sadece daha yeni siparişleri al
    where order_purchase_timestamp > (select max(order_purchase_timestamp) from {{ this }})
    {% endif %}

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
    from orders as o
    left join order_items_summary as i
        on o.order_id = i.order_id

)

select * from final
