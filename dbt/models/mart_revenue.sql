with subscriptions as (
    select *
    from {{ ref('stg_subscriptions') }}
)

select
    count(*) as total_subscriptions,
    sum(case when status = 'active' then 1 else 0 end) as active_subscriptions,
    sum(mrr_amount) as total_mrr
from subscriptions
