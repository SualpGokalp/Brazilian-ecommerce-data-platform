with products as (

    select * from {{ ref('stg_products') }}

),

categories as (

    select * from {{ ref('stg_category_translation') }}

),

final as (

    select
        p.product_id,
        p.product_category_name,
        c.product_category_name_english,
        p.product_weight_g,
        p.product_length_cm,
        p.product_height_cm,
        p.product_width_cm
    from products as p
    left join categories as c
        on p.product_category_name = c.product_category_name

)

select * from final