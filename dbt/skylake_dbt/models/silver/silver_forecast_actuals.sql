{{ config(materialized='table', schema='silver') }}

-- Silver forecast actuals model
-- Joins TAF forecast periods to actual METAR observations
-- to enable forecast accuracy scoring in the gold layer.
-- Each row pairs one forecast period with one METAR observation
-- that occurred during that period's validity window.

WITH taf AS (
    SELECT * FROM {{ ref('silver_taf_parsed') }}
),

metar AS (
    SELECT * FROM {{ ref('silver_metar_parsed') }}
),

joined AS (
    SELECT
        -- Surrogate key
        t.taf_period_id || '_' || m.metar_id     AS forecast_actual_id,

        -- Identity
        t.station_id,
        t.city,
        t.state,
        t.airport_name,

        -- TAF forecast side
        t.issue_time                              AS taf_issue_time,
        t.period_sequence,
        t.forecast_change_type,
        t.period_valid_from,
        t.period_valid_to,
        t.forecast_wind_speed_kt,
        t.forecast_wind_gust_kt,
        t.forecast_wind_dir_deg,
        t.forecast_visibility_miles,

        -- METAR actual side
        m.obs_time                                AS actual_obs_time,
        m.wind_speed_kt                           AS actual_wind_speed_kt,
        m.wind_gust_kt                            AS actual_wind_gust_kt,
        m.wind_dir_deg                            AS actual_wind_dir_deg,
        m.visibility_miles                        AS actual_visibility_miles,
        m.flt_cat                                 AS actual_flt_cat,
        m.flt_cat_rank                            AS actual_flt_cat_rank,
        m.ceiling_ft                              AS actual_ceiling_ft,

        -- Wind speed error (absolute difference in knots)
        CASE
            WHEN t.forecast_wind_speed_kt IS NULL
              OR m.wind_speed_kt IS NULL           THEN NULL
            ELSE ABS(t.forecast_wind_speed_kt - m.wind_speed_kt)
        END                                       AS wind_speed_error_kt,

        -- Wind speed accuracy flag (within 5 knots = accurate)
        CASE
            WHEN t.forecast_wind_speed_kt IS NULL
              OR m.wind_speed_kt IS NULL           THEN NULL
            WHEN ABS(t.forecast_wind_speed_kt - m.wind_speed_kt) <= 5
                                                  THEN 1
            ELSE 0
        END                                       AS wind_speed_accurate,

        -- Visibility error (absolute difference in miles)
        CASE
            WHEN t.forecast_visibility_miles IS NULL
              OR m.visibility_miles IS NULL        THEN NULL
            ELSE ABS(t.forecast_visibility_miles - m.visibility_miles)
        END                                       AS visibility_error_miles,

        -- Visibility accuracy flag (within 1 mile = accurate)
        CASE
            WHEN t.forecast_visibility_miles IS NULL
              OR m.visibility_miles IS NULL        THEN NULL
            WHEN ABS(t.forecast_visibility_miles - m.visibility_miles) <= 1.0
                                                  THEN 1
            ELSE 0
        END                                       AS visibility_accurate,

        -- How far into the future this period was when TAF was issued
        DATEDIFF('hour', t.issue_time, t.period_valid_from)
                                                  AS forecast_lead_hours

    FROM taf t
    INNER JOIN metar m
        ON  m.station_id = t.station_id
        AND m.obs_time  >= t.period_valid_from
        AND m.obs_time  <  t.period_valid_to
)

SELECT * FROM joined
