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
        raw_data:id::NUMBER                 AS activity_id,
        f.value:id::NUMBER                  AS best_effort_id,
        f.value:name::INT                   AS name,
        f.value:distance::FLOAT             AS distance_m,
        f.value:elapsed_time::INT           AS elapsed_time_s,
        f.value:moving_time::FLOAT          AS moving_time_s,
        f.value:start_date::DATETIME        AS start_date
    FROM activities_raw,
    LATERAL FLATTEN(input => raw_data:best_efforts) f
)

SELECT *
FROM final
