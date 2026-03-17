{{ config(materialized='table', schema='gold') }}

-- Gold airport conditions model
-- Latest weather conditions per airport.
-- One row per airport — always the most recent observation.
-- Primary data product for the live conditions dashboard.

WITH ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY station_id
            ORDER BY obs_time DESC
        ) AS rn
    FROM {{ ref('silver_metar_parsed') }}
),

latest AS (
    SELECT * FROM ranked WHERE rn = 1
)

SELECT
    station_id,
    airport_name,
    city,
    state,
    timezone,
    obs_time,
    flt_cat,
    flt_cat_rank,
    temp_c,
    dewpoint_c,
    temp_dewpoint_spread_c,
    wind_dir_deg,
    wind_speed_kt,
    wind_gust_kt,
    max_wind_kt,
    wind_category,
    visibility_miles,
    visibility_category,
    ceiling_ft,
    ceiling_category,
    wx_string,
    sky_cover,
    altimeter_hpa,
    sea_level_pressure_hpa,
    precip_in,
    latitude,
    longitude,
    elevation_ft,
    ingested_at
FROM latest
ORDER BY flt_cat_rank DESC, station_id
