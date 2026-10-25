with source as (
    select * from {{ source('raw', 'support_sla_events') }}
)
select
    sla_id,
    ticket_id,
    sla_type,
    response_hours,
    threshold_hours,
    breached,
    cast(created_at as timestamp) as created_at,
    cast(ingested_at as timestamp) as ingested_at
from source
