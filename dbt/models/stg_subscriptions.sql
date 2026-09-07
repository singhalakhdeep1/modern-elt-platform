-- staging: clean and type-cast raw subscription data
SELECT
    subscription_id::uuid,
    organization_id::uuid,
    LOWER(status) AS status,
    mrr_amount::numeric(10,2),
    started_on::timestamp WITH TIME ZONE
FROM {{ source('raw', 'subscriptions') }}
WHERE mrr_amount >= 0
