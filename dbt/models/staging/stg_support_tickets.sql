with source as (
    select * from {{ source('raw', 'support_tickets') }}
)
select
    ticket_id,
    account_id,
    priority,
    status,
    category,
    cast(created_at as timestamp) as created_at,
    cast(resolved_at as timestamp) as resolved_at,
    cast(ingested_at as timestamp) as ingested_at,
    case when resolved_at is not null then true else false end as is_resolved,
    case
        when resolved_at is not null
        then datediff('hour', cast(created_at as timestamp), cast(resolved_at as timestamp))
        else null
    end as resolution_hours
from source
