{{config(
    database='STRAVA_STAGING_DB',
    schema='STRAVA',
    materialized='view'
)}}

WITH activities_raw AS (
    SELECT *
    FROM {{ source('strava_raw_db', 'activities_raw') }}
),

final AS (
    SELECT
        raw_data:id::NUMBER                   AS activity_id,
        f.value:id::NUMBER                    AS lap_id,
        f.value:lap_index::INT                AS lap_index,
        f.value:distance::FLOAT               AS distance_m,
        f.value:moving_time::INT              AS moving_time_s,
        f.value:average_speed::FLOAT          AS average_speed,
        f.value:max_speed::FLOAT              AS max_speed,
        f.value:total_elevation_gain::FLOAT   AS total_elevation_gain_m,
        f.value:pace_zone::INT                AS pace_zone,
        f.value:start_date::TIMESTAMP         AS start_date
    FROM activities_raw,
    LATERAL FLATTEN(input => raw_data:laps) f
)

SELECT *
FROM final
