-- SCD Type 2 snapshot: müşterinin konum bilgisindeki değişimleri saklar.
-- 'check' stratejisi: şehir/eyalet/posta kodundan biri değişirse dbt
-- eski satırı kapatır ve yeni bir geçerli satır açar.
{% snapshot scd_customers %}

{{
    config(
        target_schema='snapshots',
        unique_key='customer_id',
        strategy='check',
        check_cols=[
            'customer_city',
            'customer_state',
            'customer_zip_code_prefix'
        ]
    )
}}

select * from {{ ref('stg_customers') }}

{% endsnapshot %}
