{{ config(materialized='table') }}

with tickets as (
    select * from {{ ref('stg_support_tickets') }}
),
sla_events as (
    select * from {{ ref('stg_support_sla_events') }}
),
accounts as (
    select * from {{ ref('stg_crm_accounts') }}
),
ticket_sla as (
    select
        t.ticket_id,
        t.account_id,
        t.priority,
        t.status,
        t.category,
        t.created_at,
        t.resolved_at,
        t.is_resolved,
        t.resolution_hours,
        coalesce(se.sla_type, 'first_response')                 as sla_type,
        coalesce(se.response_hours, t.resolution_hours)         as response_hours,
        coalesce(se.threshold_hours, case
            when t.priority = 'critical' then 1
            when t.priority = 'high'     then 4
            when t.priority = 'medium'   then 8
            else 24
        end)                                                    as threshold_hours,
        coalesce(se.breached, case
            when t.resolution_hours is null then false
            when t.priority = 'critical' and t.resolution_hours > 1   then true
            when t.priority = 'high'     and t.resolution_hours > 4   then true
            when t.priority = 'medium'   and t.resolution_hours > 8   then true
            when t.priority = 'low'      and t.resolution_hours > 24  then true
            else false
        end)                                                    as sla_breached
    from tickets t
    left join sla_events se on se.ticket_id = t.ticket_id
),
account_sla as (
    select
        account_id,
        count(*)                                                as total_tickets,
        count(case when is_resolved then 1 end)                 as resolved_tickets,
        count(case when sla_breached then 1 end)                as breached_tickets,
        count(case when priority = 'critical' then 1 end)       as critical_tickets,
        count(case when priority = 'high' then 1 end)           as high_tickets,
        avg(case when is_resolved then resolution_hours end)    as avg_resolution_hours,
        avg(case when is_resolved and priority = 'critical' then resolution_hours end) as avg_critical_resolution_hours,
        max(case when is_resolved then resolution_hours end)    as max_resolution_hours
    from ticket_sla
    group by 1
)
select
    asl.account_id,
    a.name                                                      as account_name,
    a.industry,
    asl.total_tickets,
    asl.resolved_tickets,
    asl.breached_tickets,
    asl.critical_tickets,
    asl.high_tickets,
    round(asl.avg_resolution_hours, 2)                          as avg_resolution_hours,
    round(coalesce(asl.avg_critical_resolution_hours, 0), 2)    as avg_critical_resolution_hours,
    round(coalesce(asl.max_resolution_hours, 0), 2)             as max_resolution_hours,
    case
        when asl.total_tickets > 0
        then round(asl.breached_tickets * 100.0 / asl.total_tickets, 2)
        else 0
    end                                                         as breach_rate_pct,
    case
        when asl.total_tickets > 0
        then round(asl.resolved_tickets * 100.0 / asl.total_tickets, 2)
        else 0
    end                                                         as resolution_rate_pct,
    case
        when asl.total_tickets = 0 then 'no_tickets'
        when asl.breached_tickets * 100.0 / asl.total_tickets <= 5 then 'excellent'
        when asl.breached_tickets * 100.0 / asl.total_tickets <= 15 then 'good'
        when asl.breached_tickets * 100.0 / asl.total_tickets <= 30 then 'needs_improvement'
        else 'critical'
    end                                                         as sla_health
from account_sla asl
left join accounts a on a.account_id = asl.account_id
