with source as (
    select * from {{ source('raw', 'crm_opportunities') }}
)
select
    opp_id,
    account_id,
    stage,
    amount_usd,
    probability,
    cast(close_date as timestamp) as close_date,
    cast(created_at as timestamp) as created_at,
    cast(ingested_at as timestamp) as ingested_at,
    case when stage = 'closed_won' then true else false end as is_won
from source
