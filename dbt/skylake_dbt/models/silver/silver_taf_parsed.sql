{{ config(materialized='table', schema='silver') }}

-- Silver TAF parsed model
-- Explodes the forecast_periods_json array from bronze_taf
-- into individual rows — one row per forecast period per TAF.

WITH bronze AS (
    SELECT * FROM {{ ref('bronze_taf') }}
),

airport AS (
    SELECT * FROM {{ ref('airport_metadata') }}
),

unnested AS (
    SELECT
        bt.station_id,
        bt.issue_time,
        bt.bulletin_time,
        bt.ingested_at,
        bt.valid_from_epoch,
        bt.valid_to_epoch,
        bt.raw_taf,
        bt.is_most_recent,
        period,
        ROW_NUMBER() OVER (
            PARTITION BY bt.station_id, bt.issue_time
            ORDER BY CAST(period->>'timeFrom' AS BIGINT)
        ) AS period_sequence
    FROM bronze bt,
    UNNEST(CAST(bt.forecast_periods_json AS JSON[])) AS t(period)
),

with_airport AS (
    SELECT
        u.*,
        am.airport_name,
        am.city,
        am.state,
        am.timezone
    FROM unnested u
    LEFT JOIN airport am
        ON u.station_id = am.icao_id
),

parsed AS (
    SELECT
        station_id
            || '_'
            || STRFTIME(issue_time, '%Y%m%dT%H%M%S')
            || '_p'
            || LPAD(CAST(period_sequence AS VARCHAR), 2, '0') AS taf_period_id,

        station_id,
        issue_time,
        bulletin_time,
        ingested_at,
        period_sequence,
        is_most_recent,
        airport_name,
        city,
        state,
        timezone,

        EPOCH_MS(CAST(period->>'timeFrom' AS BIGINT) * 1000) AS period_valid_from,
        EPOCH_MS(CAST(period->>'timeTo'   AS BIGINT) * 1000) AS period_valid_to,

        CAST(period->>'fcstChange' AS VARCHAR)                AS forecast_change_type,

        CASE
            WHEN CAST(period->>'wdir' AS VARCHAR) = 'VRB' THEN NULL
            ELSE TRY_CAST(period->>'wdir' AS INTEGER)
        END                                                   AS forecast_wind_dir_deg,
        TRY_CAST(period->>'wspd' AS INTEGER)                  AS forecast_wind_speed_kt,
        TRY_CAST(period->>'wgst' AS INTEGER)                  AS forecast_wind_gust_kt,

        CAST(period->>'visib' AS VARCHAR)                     AS forecast_visibility_raw,
        CASE
            WHEN CAST(period->>'visib' AS VARCHAR) LIKE '%+%' THEN 10.0
            ELSE TRY_CAST(period->>'visib' AS FLOAT)
        END                                                   AS forecast_visibility_miles,

        EPOCH_MS(valid_from_epoch * 1000)                     AS taf_valid_from,
        EPOCH_MS(valid_to_epoch   * 1000)                     AS taf_valid_to,

        raw_taf

    FROM with_airport
)

SELECT * FROM parsed
