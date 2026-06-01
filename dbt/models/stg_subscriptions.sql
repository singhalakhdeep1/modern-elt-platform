select
    'subscriptions_001' as subscription_id,
    'org_100' as organization_id,
    'active' as status,
    4999 as mrr_amount,
    '2026-05-01' as started_on
union all
select
    'subscriptions_002',
    'org_101',
    'trial',
    0,
    '2026-05-15'
