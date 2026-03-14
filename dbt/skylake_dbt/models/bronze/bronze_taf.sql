{{ config(materialized='table', schema='bronze') }}

-- Bronze TAF model
-- Reads raw TAF JSON files from data/raw/taf/ and produces
-- a clean, typed, structured table in DuckDB.

WITH raw AS (
    SELECT *
    FROM read_json(
        '../../data/raw/taf/**/*.json',
        auto_detect = true,
        ignore_errors = true
    )
),

cleaned AS (
    SELECT
        icaoId                                              AS station_id,
        CAST(issueTime    AS TIMESTAMP)                     AS issue_time,
        CAST(bulletinTime AS TIMESTAMP)                     AS bulletin_time,
        CAST("_skylake_meta"->>'ingested_at' AS TIMESTAMP)  AS ingested_at,
        CAST(validTimeFrom AS BIGINT)                       AS valid_from_epoch,
        CAST(validTimeTo   AS BIGINT)                       AS valid_to_epoch,
        CASE
            WHEN CAST(json_extract(fcsts, '$[0].wdir') AS VARCHAR) = 'VRB' THEN NULL
            ELSE TRY_CAST(json_extract(fcsts, '$[0].wdir') AS INTEGER)
        END                                                 AS init_wind_dir_deg,
        TRY_CAST(json_extract(fcsts, '$[0].wspd') AS INTEGER) AS init_wind_speed_kt,
        TRY_CAST(json_extract(fcsts, '$[0].wgst') AS INTEGER) AS init_wind_gust_kt,
        CAST(json_extract(fcsts, '$[0].visib') AS VARCHAR)  AS init_visibility,
        CAST(fcsts  AS JSON)                                AS forecast_periods_json,
        CAST(rawTAF AS VARCHAR)                             AS raw_taf,
        CAST(lat    AS FLOAT)                               AS latitude,
        CAST(lon    AS FLOAT)                               AS longitude,
        CAST(elev   AS INTEGER)                             AS elevation_ft,
        CAST(mostRecent AS INTEGER)                         AS is_most_recent
    FROM raw
    WHERE icaoId IS NOT NULL
      AND issueTime IS NOT NULL
)

SELECT * FROM cleaned
