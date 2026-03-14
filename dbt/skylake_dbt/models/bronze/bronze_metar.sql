{{ config(materialized='table', schema='bronze') }}

-- Bronze METAR model
-- Reads raw METAR JSON files from data/raw/metar/ and produces
-- a clean, typed, structured table in DuckDB.

WITH raw AS (
    SELECT *
    FROM read_json(
        '../../data/raw/metar/**/*.json',
        auto_detect = true,
        ignore_errors = true
    )
),

cleaned AS (
    SELECT
        icaoId                                              AS station_id,
        metarType                                           AS metar_type,
        CAST(reportTime AS TIMESTAMP)                       AS obs_time,
        CAST("_skylake_meta"->>'ingested_at' AS TIMESTAMP)  AS ingested_at,
        CAST(temp   AS FLOAT)                               AS temp_c,
        CAST(dewp   AS FLOAT)                               AS dewpoint_c,
        CAST(wdir   AS INTEGER)                             AS wind_dir_deg,
        CAST(wspd   AS INTEGER)                             AS wind_speed_kt,
        CAST(wgst   AS INTEGER)                             AS wind_gust_kt,
        CASE
            WHEN CAST(visib AS VARCHAR) = '10+' THEN 10.0
            WHEN TRY_CAST(visib AS FLOAT) IS NOT NULL THEN CAST(visib AS FLOAT)
            ELSE NULL
        END                                                 AS visibility_miles,
        CAST(altim  AS FLOAT)                               AS altimeter_hpa,
        CAST(slp    AS FLOAT)                               AS sea_level_pressure_hpa,
        CAST(precip AS FLOAT)                               AS precip_in,
        CAST(cover  AS VARCHAR)                             AS sky_cover,
        CAST(json_extract(clouds[1], '$.base') AS INTEGER)  AS ceiling_ft,
        CAST(fltCat AS VARCHAR)                             AS flt_cat,
        CAST(wxString AS VARCHAR)                           AS wx_string,
        CAST(rawOb  AS VARCHAR)                             AS raw_ob,
        CAST(lat    AS FLOAT)                               AS latitude,
        CAST(lon    AS FLOAT)                               AS longitude,
        CAST(elev   AS INTEGER)                             AS elevation_ft
    FROM raw
    WHERE icaoId IS NOT NULL
      AND reportTime IS NOT NULL
)

SELECT * FROM cleaned
