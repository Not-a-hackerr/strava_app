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
        raw_data:id::NUMBER                     AS activity_id,
        f.value:id::NUMBER                      AS segment_effort_id,
        f.value:segment.id::NUMBER              AS segment_id,        
        f.value:elapsed_time::INT               AS elapsed_time_s,
        f.value:moving_time::INT                AS moving_time_s,
        f.value:distance::FLOAT                 AS distance_m,
        f.value:start_date::TIMESTAMP_NTZ       AS start_date,
        f.value:pr_rank::INT                    AS pr_rank,
        f.value:hidden::BOOLEAN                 AS hidden
    FROM activities_raw,
    LATERAL FLATTEN(input => raw_data:segment_efforts) f
)

SELECT *
FROM final
