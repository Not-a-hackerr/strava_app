{{ config(
    database='STRAVA_STAGING_DB',
    schema='STRAVA',
    materialized='view'
) }}

WITH activities_raw AS (
    SELECT
        raw_data,
        ingestested_at
    FROM {{ source('strava_raw_db', 'activities_raw') }}
),

flattened AS (
    SELECT
        -- Primary Key
        raw_data:id::NUMBER                     AS activity_id,

        -- Activity Details
        raw_data:name::VARCHAR                  AS name,
        raw_data:description::VARCHAR           AS description,
        raw_data:sport_type::VARCHAR            AS sport_type,
        raw_data:workout_type::INT              AS workout_type,
        raw_data:device_name::VARCHAR           AS device_name,

        -- Timing
        raw_data:start_date::TIMESTAMP_NTZ      AS start_date,
        raw_data:start_date_local::TIMESTAMP_NTZ AS start_date_local,
        raw_data:timezone::VARCHAR              AS timezone,
        raw_data:moving_time::INT               AS moving_time_s,
        raw_data:elapsed_time::INT              AS elapsed_time_s,

        -- Distance & Speed
        raw_data:distance::FLOAT                AS distance_m,
        raw_data:average_speed::FLOAT           AS average_speed,
        raw_data:max_speed::FLOAT               AS max_speed,

        -- Elevation
        raw_data:total_elevation_gain::FLOAT    AS total_elevation_gain,
        raw_data:elev_high::FLOAT               AS elev_high,
        raw_data:elev_low::FLOAT                AS elev_low,

        -- Performance
        raw_data:calories::INT                  AS calories,
        raw_data:perceived_exertion::INT        AS perceived_exertion,
        raw_data:achievement_count::INT         AS achievement_count,
        raw_data:pr_count::INT                  AS pr_count,
        raw_data:kudos_count::INT               AS kudos_count,

        -- Location
        raw_data:start_latlng[0]::FLOAT         AS start_lat,
        raw_data:start_latlng[1]::FLOAT         AS start_lng,
        raw_data:map:summary_polyline::VARCHAR  AS map_summary_polyline,
        raw_data:commute::BOOLEAN               AS commute,
        raw_data:has_heartrate::BOOLEAN         AS has_heartrate,
        raw_data:manual::BOOLEAN                AS manual,
        raw_data:private::BOOLEAN               AS private,
        ingestested_at

    FROM activities_raw
)

SELECT * 
FROM flattened
