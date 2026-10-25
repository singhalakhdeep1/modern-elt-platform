with source as (
    select * from {{ source('raw', 'product_workspaces') }}
)
select
    workspace_id,
    account_id,
    name,
    plan,
    cast(created_at as timestamp) as created_at,
    cast(ingested_at as timestamp) as ingested_at
from source
