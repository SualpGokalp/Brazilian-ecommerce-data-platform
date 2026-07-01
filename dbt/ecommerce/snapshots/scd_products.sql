-- SCD Type 2 snapshot: ürünlerin zaman içindeki değişimini saklar.
-- Kaynakta güncelleme kolonu olmadığı için 'check' stratejisi kullanılır:
-- seçili kolonlardan biri değişirse dbt eski satırı kapatıp yenisini açar
-- (dbt_valid_from / dbt_valid_to alanlarıyla).
{% snapshot scd_products %}

{{
    config(
        target_schema='snapshots',
        unique_key='product_id',
        strategy='check',
        check_cols=[
            'product_category_name',
            'product_weight_g',
            'product_length_cm',
            'product_height_cm',
            'product_width_cm'
        ]
    )
}}

select * from {{ ref('stg_products') }}

{% endsnapshot %}
