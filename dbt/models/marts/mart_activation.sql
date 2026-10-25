{{ config(materialized='table') }}

with workspaces as (
    select * from {{ ref('stg_product_workspaces') }}
),
users as (
    select * from {{ ref('stg_product_users') }}
),
events as (
    select * from {{ ref('stg_product_events') }}
),
accounts as (
    select * from {{ ref('stg_crm_accounts') }}
),
workspace_users as (
    select
        w.workspace_id,
        w.account_id,
        w.name                              as workspace_name,
        w.plan                              as workspace_plan,
        w.created_at                        as workspace_created_at,
        count(distinct u.user_id)           as total_users,
        count(distinct case when u.last_seen_at >= dateadd('day', -30, current_timestamp) then u.user_id end) as active_users_30d
    from workspaces w
    left join users u on u.workspace_id = w.workspace_id
    group by 1, 2, 3, 4, 5
),
workspace_events as (
    select
        workspace_id,
        count(*)                                                as total_events,
        count(distinct user_id)                                 as unique_event_users,
        count(distinct event_name)                              as unique_event_types,
        count(distinct case when occurred_at >= dateadd('day', -30, current_timestamp) then user_id end) as dau_30d,
        min(occurred_at)                                        as first_event_at,
        max(occurred_at)                                        as last_event_at
    from events
    group by 1
)
select
    wu.workspace_id,
    wu.account_id,
    a.name                                                      as account_name,
    wu.workspace_name,
    wu.workspace_plan,
    wu.workspace_created_at,
    wu.total_users,
    wu.active_users_30d,
    coalesce(we.total_events, 0)                                as total_events,
    coalesce(we.unique_event_users, 0)                          as unique_event_users,
    coalesce(we.unique_event_types, 0)                          as unique_event_types,
    coalesce(we.dau_30d, 0)                                     as dau_30d,
    we.first_event_at,
    we.last_event_at,
    case
        when wu.total_users > 0
        then round(wu.active_users_30d * 100.0 / wu.total_users, 2)
        else 0
    end                                                         as activation_rate_pct,
    case
        when coalesce(we.total_events, 0) >= 10
            and coalesce(we.unique_event_types, 0) >= 3
            and wu.active_users_30d > 0
        then true
        else false
    end                                                         as is_activated
from workspace_users wu
left join workspace_events we on we.workspace_id = wu.workspace_id
left join accounts a on a.account_id = wu.account_id
