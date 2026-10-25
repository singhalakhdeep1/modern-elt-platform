with source as (
    select * from {{ source('raw', 'billing_invoices') }}
)
select
    invoice_id,
    sub_id,
    amount_usd,
    status,
    cast(due_date as timestamp) as due_date,
    cast(paid_at as timestamp) as paid_at,
    cast(ingested_at as timestamp) as ingested_at,
    case when status = 'paid' then true else false end as is_paid,
    case
        when paid_at is not null and due_date is not null
        then datediff('day', cast(due_date as timestamp), cast(paid_at as timestamp))
        else null
    end as days_to_pay
from source
