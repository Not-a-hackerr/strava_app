-- models/marts/dim_segments.sql
{{ config(
    database='STRAVA_MART_DB',
    schema='STRAVA',
    materialized='table'
) }}

SELECT
    segment_id,
    name,
    activity_type,
    distance_m,
    ROUND(distance_m / 1000, 2)     AS distance_km,
    average_grade,
    maximum_grade,
    elevation_high,
    elevation_low,
    city,
    state,
    country,
    start_lat,
    start_lng,
    end_lat,
    end_lng,
    hazardous,
    private
FROM {{ ref('stg_dim_segments') }}
