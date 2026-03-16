{{ config(materialized='table', schema='silver') }}

-- Silver METAR parsed model
-- Enriches bronze_metar with derived categories, rankings,
-- a surrogate key, and airport metadata join.

WITH bronze AS (
    SELECT * FROM {{ ref('bronze_metar') }}
),

airport AS (
    SELECT * FROM {{ ref('airport_metadata') }}
),

enriched AS (
    SELECT
        -- Surrogate key
        bm.station_id || '_' || STRFTIME(bm.obs_time, '%Y%m%dT%H%M%S') AS metar_id,

        -- Identity
        bm.station_id,
        bm.metar_type,
        bm.obs_time,
        bm.ingested_at,

        -- Airport metadata
        am.airport_name,
        am.city,
        am.state,
        am.timezone,
        am.latitude,
        am.longitude,
        am.elevation_ft,

        -- Temperature
        bm.temp_c,
        bm.dewpoint_c,
        ROUND(bm.temp_c - bm.dewpoint_c, 1)              AS temp_dewpoint_spread_c,

        -- Wind
        bm.wind_dir_deg,
        bm.wind_speed_kt,
        bm.wind_gust_kt,
        COALESCE(bm.wind_gust_kt, bm.wind_speed_kt)       AS max_wind_kt,
        CASE
            WHEN bm.wind_speed_kt IS NULL    THEN 'UNKNOWN'
            WHEN bm.wind_speed_kt = 0        THEN 'CALM'
            WHEN bm.wind_speed_kt <= 10      THEN 'LIGHT'
            WHEN bm.wind_speed_kt <= 20      THEN 'MODERATE'
            WHEN bm.wind_speed_kt <= 33      THEN 'STRONG'
            ELSE                                  'GALE'
        END                                                AS wind_category,

        -- Visibility
        bm.visibility_miles,
        CASE
            WHEN bm.visibility_miles IS NULL   THEN 'UNKNOWN'
            WHEN bm.visibility_miles >= 7      THEN 'CLEAR'
            WHEN bm.visibility_miles >= 5      THEN 'GOOD'
            WHEN bm.visibility_miles >= 3      THEN 'MODERATE'
            WHEN bm.visibility_miles >= 1      THEN 'POOR'
            ELSE                                    'VERY_POOR'
        END                                                AS visibility_category,

        -- Ceiling
        bm.ceiling_ft,
        CASE
            WHEN bm.ceiling_ft IS NULL         THEN 'UNKNOWN'
            WHEN bm.ceiling_ft >= 3000         THEN 'HIGH'
            WHEN bm.ceiling_ft >= 1000         THEN 'SCATTERED'
            WHEN bm.ceiling_ft >= 500          THEN 'BROKEN'
            WHEN bm.ceiling_ft >= 200          THEN 'LOW'
            ELSE                                    'VERY_LOW'
        END                                                AS ceiling_category,

        -- Flight category with numeric rank for sorting
        bm.flt_cat,
        CASE bm.flt_cat
            WHEN 'VFR'  THEN 1
            WHEN 'MVFR' THEN 2
            WHEN 'IFR'  THEN 3
            WHEN 'LIFR' THEN 4
            ELSE             0
        END                                                AS flt_cat_rank,

        -- Pressure
        bm.altimeter_hpa,
        bm.sea_level_pressure_hpa,

        -- Precipitation and weather
        bm.precip_in,
        bm.wx_string,
        bm.sky_cover,

        -- Raw string preserved for debugging
        bm.raw_ob

    FROM bronze bm
    LEFT JOIN airport am
        ON bm.station_id = am.icao_id
)

SELECT * FROM enriched
