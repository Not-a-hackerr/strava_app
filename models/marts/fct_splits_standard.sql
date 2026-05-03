{{ config(
    database='STRAVA_MART_DB',
    schema='STRAVA',
    materialized='table'
) }}

SELECT
    activity_id,
    split_number,
    distance_m,
    ROUND(distance_m / 1609.34, 2)                  AS distance_miles,
    elapsed_time_s,
    moving_time_s,
    ROUND(moving_time_s / 60, 2)                    AS moving_time_mins,
    average_speed,
    ROUND(average_speed * 3.6, 2)                   AS average_speed_kmh,
    grade_adj_speed,
    elevation_difference,
    pace_zone,
    ROUND((moving_time_s / 60) / 
        (distance_m / 1609.34), 2)                  AS pace_mins_per_mile,
    loaded_at
FROM {{ ref('stg_splits_standard') }}
