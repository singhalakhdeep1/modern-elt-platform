{{ config(materialized='table') }}

with subs as (
    select * from {{ ref('stg_billing_subscriptions') }}
),
accounts as (
    select * from {{ ref('stg_crm_accounts') }}
),
sub_status as (
    select
        s.account_id,
        a.name                                                  as account_name,
        a.industry,
        count(*)                                                as total_subscriptions,
        count(case when s.is_active then 1 end)                 as active_subscriptions,
        count(case when not s.is_active then 1 end)             as churned_subscriptions,
        sum(case when s.is_active then s.mrr_usd else 0 end)    as active_mrr_usd,
        sum(case when not s.is_active then s.mrr_usd else 0 end) as churned_mrr_usd,
        min(s.started_at)                                       as cohort_date,
        max(s.cancelled_at)                                     as last_churn_date
    from subs s
    left join accounts a on a.account_id = s.account_id
    group by 1, 2, 3
)
select
    account_id,
    account_name,
    industry,
    total_subscriptions,
    active_subscriptions,
    churned_subscriptions,
    active_mrr_usd,
    churned_mrr_usd,
    case
        when total_subscriptions > 0
        then round(churned_subscriptions * 100.0 / total_subscriptions, 2)
        else 0
    end                                                         as churn_rate_pct,
    case
        when (active_mrr_usd + churned_mrr_usd) > 0
        then round(churned_mrr_usd * 100.0 / (active_mrr_usd + churned_mrr_usd), 2)
        else 0
    end                                                         as mrr_churn_rate_pct,
    cohort_date,
    last_churn_date,
    case when churned_subscriptions > 0 and active_subscriptions = 0 then true else false end as fully_churned
from sub_status
