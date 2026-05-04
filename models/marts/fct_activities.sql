{{ config(
    database='STRAVA_MART_DB',
    schema='STRAVA',
    materialized='table'
) }}

SELECT
    -- Keys
    activity_id,

    -- Activity Details
    name,
    description,
    sport_type,
    device_name,
    timezone,

    -- Timing (converted to readable formats)
    start_date,
    start_date_local,
    moving_time_s,
    elapsed_time_s,
    ROUND(moving_time_s / 60, 2)                AS moving_time_mins,
    ROUND(elapsed_time_s / 60, 2)               AS elapsed_time_mins,

    -- Distance (converted from metres)
    distance_m,
    ROUND(distance_m / 1000, 2)                 AS distance_km,
    ROUND(distance_m / 1609.34, 2)              AS distance_miles,

    -- Pace (mins per km and mins per mile)
    ROUND((moving_time_s / 60) / 
        (distance_m / 1000), 2)                 AS pace_mins_per_km,
    ROUND((moving_time_s / 60) / 
        (distance_m / 1609.34), 2)              AS pace_mins_per_mile,

    -- Speed
    average_speed,
    ROUND(average_speed * 3.6, 2)               AS average_speed_kmh,
    max_speed,
    ROUND(max_speed * 3.6, 2)                   AS max_speed_kmh,

    -- Elevation
    total_elevation_gain,
    elev_high,
    elev_low,

    -- Performance
    calories,
    perceived_exertion,
    achievement_count,
    pr_count,
    kudos_count,

    -- Race Category (business logic)
    CASE
        WHEN distance_m >= 42195 THEN 'Marathon'
        WHEN distance_m >= 21097 THEN 'Half Marathon'
        WHEN distance_m >= 10000 THEN '10K'
        WHEN distance_m >= 5000  THEN '5K'
        ELSE 'Other'
    END                                          AS race_category,

    -- Effort Level derived from perceived exertion
    CASE
        WHEN perceived_exertion <= 3 THEN 'Easy'
        WHEN perceived_exertion <= 6 THEN 'Moderate'
        WHEN perceived_exertion <= 8 THEN 'Hard'
        ELSE 'Maximum'
    END                                          AS effort_level,

    -- Flags
    commute,
    has_heartrate,
    manual,
    private
FROM {{ ref('stg_activities') }}
