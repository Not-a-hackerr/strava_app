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
        f.value:segment.id::NUMBER              AS segment_id,
        f.value:segment.name::VARCHAR           AS name,
        f.value:segment.activity_type::VARCHAR  AS activity_type,
        f.value:segment.distance::FLOAT         AS distance_m,
        f.value:segment.average_grade::FLOAT    AS average_grade,
        f.value:segment.maximum_grade::FLOAT    AS maximum_grade,
        f.value:segment.elevation_high::FLOAT   AS elevation_high,
        f.value:segment.elevation_low::FLOAT    AS elevation_low,
        f.value:segment.city::VARCHAR           AS city,
        f.value:segment.state::VARCHAR          AS state,
        f.value:segment.country::VARCHAR        AS country,
        f.value:segment.start_latlng[0]::FLOAT  AS start_lat,
        f.value:segment.start_latlng[1]::FLOAT  AS start_lng,
        f.value:segment.end_latlng[0]::FLOAT    AS end_lat,
        f.value:segment.end_latlng[1]::FLOAT    AS end_lng,
        f.value:segment.hazardous::BOOLEAN      AS hazardous,
        f.value:segment.private::BOOLEAN        AS private
    FROM activities_raw,
    LATERAL FLATTEN(input => raw_data:segment_efforts) f
)

-- DISTINCT because the same segment appears across multiple activities
SELECT DISTINCT * 
FROM flattened
