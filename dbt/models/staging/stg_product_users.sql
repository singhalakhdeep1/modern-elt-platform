with source as (
    select * from {{ source('raw', 'product_users') }}
)
select
    user_id,
    workspace_id,
    email,
    role,
    cast(created_at as timestamp) as created_at,
    cast(last_seen_at as timestamp) as last_seen_at,
    cast(ingested_at as timestamp) as ingested_at
from source
