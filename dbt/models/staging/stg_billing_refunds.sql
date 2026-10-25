with source as (
    select * from {{ source('raw', 'billing_refunds') }}
)
select
    refund_id,
    invoice_id,
    amount_usd,
    reason,
    cast(created_at as timestamp) as created_at,
    cast(ingested_at as timestamp) as ingested_at
from source
