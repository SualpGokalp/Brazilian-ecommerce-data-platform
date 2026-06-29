with source as (

    select * from {{ source('bronze', 'category_translation') }}

),

cleaned as (

    select
        product_category_name,
        product_category_name_english
    from source

)

select * from cleaned