{{ config(materialized='table') }}

with subs as (
    select * from {{ ref('stg_billing_subscriptions') }}
),
accounts as (
    select * from {{ ref('stg_crm_accounts') }}
),
invoices as (
    select * from {{ ref('stg_billing_invoices') }}
),
mrr_per_account as (
    select
        s.account_id,
        a.name                                          as account_name,
        a.industry,
        a.plan                                          as account_plan,
        count(s.sub_id)                                 as active_subscriptions,
        sum(case when s.is_active then s.mrr_usd else 0 end) as current_mrr_usd,
        sum(s.mrr_usd)                                  as total_mrr_usd,
        min(s.started_at)                               as first_subscription_date,
        max(s.started_at)                               as latest_subscription_date
    from subs s
    left join accounts a on a.account_id = s.account_id
    group by 1, 2, 3, 4
),
paid_invoices as (
    select
        sub_id,
        count(*)                    as paid_invoice_count,
        sum(amount_usd)             as total_paid_usd,
        avg(days_to_pay)            as avg_days_to_pay
    from invoices
    where is_paid
    group by 1
)
select
    m.account_id,
    m.account_name,
    m.industry,
    m.account_plan,
    m.active_subscriptions,
    m.current_mrr_usd,
    m.total_mrr_usd,
    m.current_mrr_usd * 12                                  as arr_usd,
    coalesce(pi.paid_invoice_count, 0)                      as paid_invoice_count,
    coalesce(pi.total_paid_usd, 0)                          as total_paid_usd,
    coalesce(pi.avg_days_to_pay, 0)                         as avg_days_to_pay,
    m.first_subscription_date,
    m.latest_subscription_date
from mrr_per_account m
left join (
    select
        inv.sub_id,
        s.account_id,
        sum(case when inv.is_paid then 1 else 0 end)    as paid_invoice_count,
        sum(case when inv.is_paid then inv.amount_usd else 0 end) as total_paid_usd,
        avg(inv.days_to_pay)                            as avg_days_to_pay
    from invoices inv
    join subs s on s.sub_id = inv.sub_id
    group by 1, 2
) pi on pi.account_id = m.account_id
