with source as (
    select * from {{ source('raw', 'crm_contacts') }}
)
select
    contact_id,
    account_id,
    name,
    email,
    role,
    is_active,
    cast(created_at as timestamp) as created_at,
    cast(ingested_at as timestamp) as ingested_at
from source
