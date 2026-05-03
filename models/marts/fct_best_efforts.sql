{{ config(
    database='STRAVA_MART_DB',
    schema='STRAVA',
    materialized='table'
) }}

SELECT
    best_effort_id,
    activity_id,
    name,

    -- Distance
    distance_m,
    ROUND(distance_m / 1000, 2)                     AS distance_km,

    -- Timing
    elapsed_time_s,
    moving_time_s,
    ROUND(moving_time_s / 60, 2)                    AS moving_time_mins,

    -- Pace
    ROUND((moving_time_s / 60) /
        NULLIF(distance_m / 1000, 0), 2)            AS pace_mins_per_km,
    ROUND((moving_time_s / 60) /
        NULLIF(distance_m / 1609.34, 0), 2)         AS pace_mins_per_mile,

    -- Performance
    pr_rank,
    CASE
        WHEN pr_rank = 1 THEN 'Personal Record'
        WHEN pr_rank = 2 THEN '2nd Best'
        WHEN pr_rank = 3 THEN '3rd Best'
        WHEN pr_rank IS NULL THEN 'No Rank'
        ELSE 'Top ' || pr_rank::VARCHAR || ' Best'
    END                                             AS pr_label,

    start_date,
    start_date_local,
    loaded_at

FROM {{ ref('stg_best_efforts') }}
