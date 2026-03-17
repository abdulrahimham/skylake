{{ config(materialized='table', schema='gold') }}

-- Gold airport risk score model
-- Composite 0-100 operational risk score per airport.
-- Combines current conditions, wind severity, and forecast reliability.
-- Centerpiece data product of SkyLake.

WITH conditions AS (
    SELECT * FROM {{ ref('gold_airport_conditions') }}
),

accuracy AS (
    SELECT * FROM {{ ref('gold_forecast_accuracy') }}
),

scored AS (
    SELECT
        c.station_id,
        c.airport_name,
        c.city,
        c.state,
        c.obs_time,
        c.flt_cat,
        c.flt_cat_rank,
        c.wind_speed_kt,
        c.wind_gust_kt,
        c.max_wind_kt,
        c.wind_category,
        c.visibility_miles,
        c.visibility_category,
        c.ceiling_ft,
        c.ceiling_category,
        c.wx_string,

        -- Component 1: Conditions score (0-100) based on flight category
        CASE c.flt_cat_rank
            WHEN 1 THEN 0
            WHEN 2 THEN 25
            WHEN 3 THEN 60
            WHEN 4 THEN 100
            ELSE        0
        END                                                     AS conditions_score,

        -- Component 2: Wind score (0-100) based on max wind
        LEAST(100, ROUND(COALESCE(c.max_wind_kt, 0) * 3.0, 0)) AS wind_score,

        -- Component 3: Forecast penalty (0-20) based on historical accuracy
        -- If wind accuracy < 50%, add up to 20 points of uncertainty penalty
        CASE
            WHEN a.wind_accuracy_rate IS NULL       THEN 10
            WHEN a.wind_accuracy_rate >= 0.8        THEN 0
            WHEN a.wind_accuracy_rate >= 0.6        THEN 5
            WHEN a.wind_accuracy_rate >= 0.4        THEN 10
            ELSE                                         20
        END                                                     AS forecast_penalty,

        -- Accuracy context
        a.wind_accuracy_rate,
        a.avg_wind_error_kt,
        a.total_verifications

    FROM conditions c
    LEFT JOIN accuracy a
        ON c.station_id = a.station_id
),

final AS (
    SELECT
        *,

        -- Composite score: 50% conditions, 30% wind, 20% forecast reliability
        ROUND(
            (conditions_score * 0.50) +
            (wind_score       * 0.30) +
            (forecast_penalty * 0.20)
        , 0)                                                    AS composite_risk_score,

        -- Risk level label
        CASE
            WHEN ROUND((conditions_score * 0.50) +
                       (wind_score       * 0.30) +
                       (forecast_penalty * 0.20), 0) < 20      THEN 'LOW'
            WHEN ROUND((conditions_score * 0.50) +
                       (wind_score       * 0.30) +
                       (forecast_penalty * 0.20), 0) < 40      THEN 'MODERATE'
            WHEN ROUND((conditions_score * 0.50) +
                       (wind_score       * 0.30) +
                       (forecast_penalty * 0.20), 0) < 70      THEN 'HIGH'
            ELSE                                                     'SEVERE'
        END                                                     AS risk_level

    FROM scored
)

SELECT * FROM final
ORDER BY composite_risk_score DESC
