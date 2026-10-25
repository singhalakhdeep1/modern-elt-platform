with source as (
    select * from {{ source('raw', 'product_events') }}
)
select
    event_id,
    user_id,
    workspace_id,
    event_name,
    properties,
    cast(occurred_at as timestamp) as occurred_at,
    cast(ingested_at as timestamp) as ingested_at
from source
