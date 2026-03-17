{{ config(materialized='table', schema='gold') }}

-- Gold forecast accuracy model
-- Aggregated TAF forecast accuracy rates per airport.
-- Answers: which airports have the most reliable weather forecasts?

WITH actuals AS (
    SELECT * FROM {{ ref('silver_forecast_actuals') }}
),

aggregated AS (
    SELECT
        station_id,
        city,
        state,
        airport_name,

        -- Overall counts
        COUNT(*)                                                AS total_verifications,
        COUNT(wind_speed_accurate)                              AS wind_verifications,
        COUNT(visibility_accurate)                              AS visibility_verifications,

        -- Overall accuracy rates
        ROUND(AVG(wind_speed_accurate), 3)                     AS wind_accuracy_rate,
        ROUND(AVG(visibility_accurate), 3)                     AS visibility_accuracy_rate,

        -- Average errors
        ROUND(AVG(wind_speed_error_kt), 1)                     AS avg_wind_error_kt,
        ROUND(AVG(visibility_error_miles), 2)                  AS avg_visibility_error_miles,

        -- Accuracy by lead time bucket
        ROUND(AVG(CASE WHEN forecast_lead_hours <= 6
                       THEN wind_speed_accurate END), 3)       AS wind_accuracy_0_6h,
        ROUND(AVG(CASE WHEN forecast_lead_hours BETWEEN 7 AND 12
                       THEN wind_speed_accurate END), 3)       AS wind_accuracy_7_12h,
        ROUND(AVG(CASE WHEN forecast_lead_hours > 12
                       THEN wind_speed_accurate END), 3)       AS wind_accuracy_12h_plus,

        -- Best and worst errors
        MIN(wind_speed_error_kt)                                AS min_wind_error_kt,
        MAX(wind_speed_error_kt)                                AS max_wind_error_kt,

        -- Time range covered
        MIN(taf_issue_time)                                     AS earliest_taf,
        MAX(actual_obs_time)                                    AS latest_observation

    FROM actuals
    GROUP BY station_id, city, state, airport_name
)

SELECT * FROM aggregated
ORDER BY wind_accuracy_rate DESC NULLS LAST
