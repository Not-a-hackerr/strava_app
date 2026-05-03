{{ config(
    database='STRAVA_MART_DB',
    schema='STRAVA',
    materialized='table'
) }}

SELECT
    lap_id,
    activity_id,
    lap_index,
    name,
    distance_m,
    ROUND(distance_m / 1000, 2)                     AS distance_km,
    ROUND(distance_m / 1609.34, 2)                  AS distance_miles,
    elapsed_time_s,
    moving_time_s,
    ROUND(moving_time_s / 60, 2)                    AS moving_time_mins,
    average_speed,
    ROUND(average_speed * 3.6, 2)                   AS average_speed_kmh,
    max_speed,
    ROUND(max_speed * 3.6, 2)                       AS max_speed_kmh,
    ROUND((moving_time_s / 60) /
        NULLIF(distance_m / 1000, 0), 2)            AS pace_mins_per_km,
    ROUND((moving_time_s / 60) /
        NULLIF(distance_m / 1609.34, 0), 2)         AS pace_mins_per_mile,
    total_elevation_gain,
    pace_zone,
    CASE
        WHEN pace_zone = 1 THEN 'Active Recovery'
        WHEN pace_zone = 2 THEN 'Endurance'
        WHEN pace_zone = 3 THEN 'Tempo'
        WHEN pace_zone = 4 THEN 'Threshold'
        WHEN pace_zone = 5 THEN 'VO2 Max'
        ELSE 'Unknown'
    END                                             AS pace_zone_label,
    start_date,
    start_date_local,
    ingestested_at
FROM {{ ref('stg_laps') }}
