{{ config(
    database='STRAVA_STAGING_DB',
    schema='STRAVA',
    materialized='view'
) }}

WITH activities_raw AS (
    SELECT *
    FROM {{ source('strava_raw_db', 'activities_raw') }}
),

flattened AS (
    SELECT
        raw_data:id::NUMBER                         AS activity_id,
        f.value:split::INT                          AS split_number,
        f.value:distance::FLOAT                     AS distance_m,
        f.value:elapsed_time::INT                   AS elapsed_time_s,
        f.value:moving_time::INT                    AS moving_time_s,
        f.value:average_speed::FLOAT                AS average_speed,
        f.value:average_grade_adjusted_speed::FLOAT AS grade_adj_speed,
        f.value:elevation_difference::FLOAT         AS elevation_difference,
        f.value:pace_zone::INT                      AS pace_zone,
        ingestested_at
    FROM activities_raw,
    LATERAL FLATTEN(input => raw_data:splits_standard) f
)

SELECT *
FROM flattened
