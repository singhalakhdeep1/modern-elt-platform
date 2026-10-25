with source as (
    select * from {{ source('raw', 'billing_subscriptions') }}
)
select
    sub_id,
    account_id,
    plan,
    mrr_usd,
    status,
    cast(started_at as timestamp) as started_at,
    cast(cancelled_at as timestamp) as cancelled_at,
    cast(ingested_at as timestamp) as ingested_at,
    case when status = 'active' then true else false end as is_active
from source
