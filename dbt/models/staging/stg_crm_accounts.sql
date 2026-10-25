with source as (
    select * from {{ source('raw', 'crm_accounts') }}
)
select
    account_id,
    name,
    industry,
    arr_usd,
    status,
    region,
    cast(created_at as timestamp) as created_at,
    cast(ingested_at as timestamp) as ingested_at
from source
