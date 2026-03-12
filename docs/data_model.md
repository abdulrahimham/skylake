# SkyLake — Data Model

This document describes every table in the SkyLake pipeline,
organized by layer. Each table includes its source, purpose,
and column definitions.

For field-level definitions see docs/data_dictionary.md.
For architecture context see docs/architecture.md.

---

## Layer Overview

| Layer | Tables | Purpose |
|---|---|---|
| Bronze | bronze_metar, bronze_taf | Structured raw data, minimal cleaning |
| Silver | silver_metar_parsed, silver_taf_parsed, silver_forecast_actuals | Cleaned, enriched, joined |
| Gold | gold_airport_conditions, gold_forecast_accuracy, gold_low_visibility_events, gold_wind_disruption_windows, gold_airport_risk_score | Analytical outputs |
| Seeds | airport_metadata | Static reference data |

---

## Seeds (Reference Data)

### airport_metadata
Static reference table loaded from dbt/skylake_dbt/seeds/airport_metadata.csv.
Contains metadata about each monitored airport.

| Column | Type | Description | Example |
|---|---|---|---|
| icao_code | VARCHAR | 4-letter ICAO airport identifier | KJFK |
| iata_code | VARCHAR | 3-letter IATA airport identifier | JFK |
| airport_name | VARCHAR | Full airport name | John F. Kennedy International |
| city | VARCHAR | City name | New York |
| state | VARCHAR | U.S. state abbreviation | NY |
| latitude | FLOAT | Airport latitude coordinate | 40.6413 |
| longitude | FLOAT | Airport longitude coordinate | -73.7781 |
| elevation_ft | INTEGER | Airport elevation in feet | 13 |
| timezone | VARCHAR | IANA timezone string | America/New_York |
| climate_region | VARCHAR | Climate classification | Northeast |

---

## Bronze Layer

Bronze tables contain structured, minimally cleaned data.
One row per raw observation. No business logic applied.
Soda Core checks must pass before data enters this layer.

### bronze_metar
Source: data/raw/metar/ Parquet files
One row per METAR observation per airport per hour.

| Column | Type | Description | Example |
|---|---|---|---|
| station_id | VARCHAR | ICAO airport code | KJFK |
| observation_time | TIMESTAMP | UTC time of observation | 2026-03-12 14:00:00 |
| raw_text | VARCHAR | Full raw METAR string | KJFK 121400Z 28015KT... |
| wind_dir_deg | INTEGER | Wind direction in degrees | 280 |
| wind_speed_kt | INTEGER | Wind speed in knots | 15 |
| wind_gust_kt | INTEGER | Wind gust speed in knots (null if no gust) | 25 |
| visibility_sm | FLOAT | Visibility in statute miles | 10.0 |
| ceiling_ft | INTEGER | Lowest broken or overcast cloud layer in feet | 3000 |
| temp_c | FLOAT | Temperature in Celsius | 12.0 |
| dewpoint_c | FLOAT | Dewpoint in Celsius | 4.0 |
| altimeter_inhg | FLOAT | Altimeter setting in inches of mercury | 29.92 |
| flight_category | VARCHAR | VFR, MVFR, IFR, or LIFR | VFR |
| ingested_at | TIMESTAMP | UTC time this record was ingested | 2026-03-12 14:05:00 |
| source_file | VARCHAR | Path to raw source file | data/raw/metar/2026/03/12/... |

### bronze_taf
Source: data/raw/taf/ Parquet files
One row per TAF forecast period per airport.

| Column | Type | Description | Example |
|---|---|---|---|
| station_id | VARCHAR | ICAO airport code | KJFK |
| issue_time | TIMESTAMP | UTC time TAF was issued | 2026-03-12 12:00:00 |
| valid_time_from | TIMESTAMP | Start of forecast period | 2026-03-12 12:00:00 |
| valid_time_to | TIMESTAMP | End of forecast period | 2026-03-13 12:00:00 |
| forecast_wind_dir_deg | INTEGER | Forecasted wind direction | 270 |
| forecast_wind_speed_kt | INTEGER | Forecasted wind speed in knots | 12 |
| forecast_wind_gust_kt | INTEGER | Forecasted wind gust (null if none) | 20 |
| forecast_visibility_sm | FLOAT | Forecasted visibility in statute miles | 6.0 |
| forecast_ceiling_ft | INTEGER | Forecasted ceiling height in feet | 2500 |
| forecast_flight_category | VARCHAR | Forecasted flight category | MVFR |
| change_indicator | VARCHAR | FM, TEMPO, BECMG, PROB (null if base) | FM |
| ingested_at | TIMESTAMP | UTC time this record was ingested | 2026-03-12 12:05:00 |
| source_file | VARCHAR | Path to raw source file | data/raw/taf/2026/03/12/... |

---

## Silver Layer

Silver tables are cleaned, typed, deduplicated, and enriched.
Business logic begins here. All dbt tests must pass.

### silver_metar_parsed
Source: bronze_metar + airport_metadata seed
Cleaned and enriched METAR observations.

| Column | Type | Description |
|---|---|---|
| metar_id | VARCHAR | Surrogate key (station_id + observation_time) |
| station_id | VARCHAR | ICAO airport code |
| observation_time | TIMESTAMP | UTC observation time |
| wind_dir_deg | INTEGER | Wind direction (null if variable) |
| wind_speed_kt | INTEGER | Wind speed in knots |
| wind_gust_kt | INTEGER | Gust speed (null if calm) |
| visibility_sm | FLOAT | Visibility in statute miles (capped at 10.0) |
| ceiling_ft | INTEGER | Ceiling height in feet (null if clear) |
| temp_c | FLOAT | Temperature in Celsius |
| dewpoint_c | FLOAT | Dewpoint in Celsius |
| altimeter_inhg | FLOAT | Altimeter setting |
| flight_category | VARCHAR | VFR, MVFR, IFR, LIFR |
| is_low_visibility | BOOLEAN | True if visibility < 3 statute miles |
| is_high_wind | BOOLEAN | True if wind speed >= 25kt or gust >= 35kt |
| airport_name | VARCHAR | From airport_metadata seed |
| city | VARCHAR | From airport_metadata seed |
| climate_region | VARCHAR | From airport_metadata seed |

### silver_taf_parsed
Source: bronze_taf + airport_metadata seed
Cleaned and enriched TAF forecast periods.

| Column | Type | Description |
|---|---|---|
| taf_period_id | VARCHAR | Surrogate key |
| station_id | VARCHAR | ICAO airport code |
| issue_time | TIMESTAMP | When TAF was issued |
| valid_time_from | TIMESTAMP | Period start |
| valid_time_to | TIMESTAMP | Period end |
| forecast_wind_speed_kt | INTEGER | Forecasted wind speed |
| forecast_visibility_sm | FLOAT | Forecasted visibility |
| forecast_ceiling_ft | INTEGER | Forecasted ceiling |
| forecast_flight_category | VARCHAR | Forecasted flight category |
| forecast_hours_out | INTEGER | Hours from issue time to period start |

### silver_forecast_actuals
Source: silver_metar_parsed + silver_taf_parsed
Joins TAF forecasts with METAR actuals for the same
airport and time window. Foundation for forecast accuracy.

| Column | Type | Description |
|---|---|---|
| station_id | VARCHAR | ICAO airport code |
| observation_time | TIMESTAMP | Actual observation time |
| issue_time | TIMESTAMP | TAF issue time matched to this observation |
| forecast_hours_out | INTEGER | How far out this forecast was made |
| actual_flight_category | VARCHAR | What actually happened |
| forecast_flight_category | VARCHAR | What was predicted |
| category_matched | BOOLEAN | True if forecast matched actual |
| actual_visibility_sm | FLOAT | Actual visibility |
| forecast_visibility_sm | FLOAT | Forecasted visibility |
| visibility_error_sm | FLOAT | Absolute difference in visibility |
| actual_wind_speed_kt | INTEGER | Actual wind speed |
| forecast_wind_speed_kt | INTEGER | Forecasted wind speed |
| wind_speed_error_kt | INTEGER | Absolute difference in wind speed |

---

## Gold Layer

Gold tables are analytical outputs optimized for reading.
These are the final data products SkyLake delivers.

### gold_airport_conditions
Hourly summary of conditions at each airport.
Primary table for the dashboard airport view.

| Column | Type | Description |
|---|---|---|
| station_id | VARCHAR | ICAO airport code |
| observation_hour | TIMESTAMP | Truncated to hour |
| flight_category | VARCHAR | VFR, MVFR, IFR, LIFR |
| avg_visibility_sm | FLOAT | Average visibility for the hour |
| avg_wind_speed_kt | FLOAT | Average wind speed for the hour |
| max_wind_gust_kt | INTEGER | Maximum gust recorded in the hour |
| avg_ceiling_ft | INTEGER | Average ceiling for the hour |
| is_low_visibility_hour | BOOLEAN | True if any obs in hour was IFR/LIFR |
| is_high_wind_hour | BOOLEAN | True if any obs had high wind |

### gold_forecast_accuracy
TAF forecast accuracy scores by airport and forecast horizon.

| Column | Type | Description |
|---|---|---|
| station_id | VARCHAR | ICAO airport code |
| issue_date | DATE | Date TAF was issued |
| forecast_hours_out | INTEGER | Forecast horizon (6, 12, 18, 24 hours) |
| total_periods | INTEGER | Number of forecast periods evaluated |
| category_match_rate | FLOAT | Percentage of periods with correct flight category |
| avg_visibility_error_sm | FLOAT | Average visibility forecast error |
| avg_wind_error_kt | FLOAT | Average wind speed forecast error |
| accuracy_score | FLOAT | Composite accuracy score 0-100 |

### gold_low_visibility_events
Detected periods of IFR or LIFR conditions.

| Column | Type | Description |
|---|---|---|
| event_id | VARCHAR | Unique event identifier |
| station_id | VARCHAR | ICAO airport code |
| event_start | TIMESTAMP | When low visibility began |
| event_end | TIMESTAMP | When conditions improved |
| duration_hours | FLOAT | Total duration in hours |
| min_visibility_sm | FLOAT | Lowest visibility recorded during event |
| min_flight_category | VARCHAR | Worst flight category during event |
| was_forecast | BOOLEAN | True if TAF predicted this event |

### gold_wind_disruption_windows
Detected periods of operationally significant wind.

| Column | Type | Description |
|---|---|---|
| event_id | VARCHAR | Unique event identifier |
| station_id | VARCHAR | ICAO airport code |
| event_start | TIMESTAMP | When high wind began |
| event_end | TIMESTAMP | When wind subsided |
| duration_hours | FLOAT | Total duration in hours |
| peak_wind_speed_kt | INTEGER | Maximum sustained wind during event |
| peak_gust_kt | INTEGER | Maximum gust during event |
| was_forecast | BOOLEAN | True if TAF predicted this event |

### gold_airport_risk_score
Composite operational risk score per airport per hour.
Primary output used in the dashboard risk view.

| Column | Type | Description |
|---|---|---|
| station_id | VARCHAR | ICAO airport code |
| score_hour | TIMESTAMP | Hour this score applies to |
| visibility_score | FLOAT | Visibility risk component 0-100 |
| wind_score | FLOAT | Wind risk component 0-100 |
| ceiling_score | FLOAT | Ceiling risk component 0-100 |
| forecast_confidence_score | FLOAT | TAF accuracy component 0-100 |
| composite_risk_score | FLOAT | Weighted composite score 0-100 |
| risk_level | VARCHAR | LOW, MODERATE, HIGH, SEVERE |
EOFcat > docs/data_model.md << 'EOF'
# SkyLake — Data Model

This document describes every table in the SkyLake pipeline,
organized by layer. Each table includes its source, purpose,
and column definitions.

For field-level definitions see docs/data_dictionary.md.
For architecture context see docs/architecture.md.

---

## Layer Overview

| Layer | Tables | Purpose |
|---|---|---|
| Bronze | bronze_metar, bronze_taf | Structured raw data, minimal cleaning |
| Silver | silver_metar_parsed, silver_taf_parsed, silver_forecast_actuals | Cleaned, enriched, joined |
| Gold | gold_airport_conditions, gold_forecast_accuracy, gold_low_visibility_events, gold_wind_disruption_windows, gold_airport_risk_score | Analytical outputs |
| Seeds | airport_metadata | Static reference data |

---

## Seeds (Reference Data)

### airport_metadata
Static reference table loaded from dbt/skylake_dbt/seeds/airport_metadata.csv.
Contains metadata about each monitored airport.

| Column | Type | Description | Example |
|---|---|---|---|
| icao_code | VARCHAR | 4-letter ICAO airport identifier | KJFK |
| iata_code | VARCHAR | 3-letter IATA airport identifier | JFK |
| airport_name | VARCHAR | Full airport name | John F. Kennedy International |
| city | VARCHAR | City name | New York |
| state | VARCHAR | U.S. state abbreviation | NY |
| latitude | FLOAT | Airport latitude coordinate | 40.6413 |
| longitude | FLOAT | Airport longitude coordinate | -73.7781 |
| elevation_ft | INTEGER | Airport elevation in feet | 13 |
| timezone | VARCHAR | IANA timezone string | America/New_York |
| climate_region | VARCHAR | Climate classification | Northeast |

---

## Bronze Layer

Bronze tables contain structured, minimally cleaned data.
One row per raw observation. No business logic applied.
Soda Core checks must pass before data enters this layer.

### bronze_metar
Source: data/raw/metar/ Parquet files
One row per METAR observation per airport per hour.

| Column | Type | Description | Example |
|---|---|---|---|
| station_id | VARCHAR | ICAO airport code | KJFK |
| observation_time | TIMESTAMP | UTC time of observation | 2026-03-12 14:00:00 |
| raw_text | VARCHAR | Full raw METAR string | KJFK 121400Z 28015KT... |
| wind_dir_deg | INTEGER | Wind direction in degrees | 280 |
| wind_speed_kt | INTEGER | Wind speed in knots | 15 |
| wind_gust_kt | INTEGER | Wind gust speed in knots (null if no gust) | 25 |
| visibility_sm | FLOAT | Visibility in statute miles | 10.0 |
| ceiling_ft | INTEGER | Lowest broken or overcast cloud layer in feet | 3000 |
| temp_c | FLOAT | Temperature in Celsius | 12.0 |
| dewpoint_c | FLOAT | Dewpoint in Celsius | 4.0 |
| altimeter_inhg | FLOAT | Altimeter setting in inches of mercury | 29.92 |
| flight_category | VARCHAR | VFR, MVFR, IFR, or LIFR | VFR |
| ingested_at | TIMESTAMP | UTC time this record was ingested | 2026-03-12 14:05:00 |
| source_file | VARCHAR | Path to raw source file | data/raw/metar/2026/03/12/... |

### bronze_taf
Source: data/raw/taf/ Parquet files
One row per TAF forecast period per airport.

| Column | Type | Description | Example |
|---|---|---|---|
| station_id | VARCHAR | ICAO airport code | KJFK |
| issue_time | TIMESTAMP | UTC time TAF was issued | 2026-03-12 12:00:00 |
| valid_time_from | TIMESTAMP | Start of forecast period | 2026-03-12 12:00:00 |
| valid_time_to | TIMESTAMP | End of forecast period | 2026-03-13 12:00:00 |
| forecast_wind_dir_deg | INTEGER | Forecasted wind direction | 270 |
| forecast_wind_speed_kt | INTEGER | Forecasted wind speed in knots | 12 |
| forecast_wind_gust_kt | INTEGER | Forecasted wind gust (null if none) | 20 |
| forecast_visibility_sm | FLOAT | Forecasted visibility in statute miles | 6.0 |
| forecast_ceiling_ft | INTEGER | Forecasted ceiling height in feet | 2500 |
| forecast_flight_category | VARCHAR | Forecasted flight category | MVFR |
| change_indicator | VARCHAR | FM, TEMPO, BECMG, PROB (null if base) | FM |
| ingested_at | TIMESTAMP | UTC time this record was ingested | 2026-03-12 12:05:00 |
| source_file | VARCHAR | Path to raw source file | data/raw/taf/2026/03/12/... |

---

## Silver Layer

Silver tables are cleaned, typed, deduplicated, and enriched.
Business logic begins here. All dbt tests must pass.

### silver_metar_parsed
Source: bronze_metar + airport_metadata seed
Cleaned and enriched METAR observations.

| Column | Type | Description |
|---|---|---|
| metar_id | VARCHAR | Surrogate key (station_id + observation_time) |
| station_id | VARCHAR | ICAO airport code |
| observation_time | TIMESTAMP | UTC observation time |
| wind_dir_deg | INTEGER | Wind direction (null if variable) |
| wind_speed_kt | INTEGER | Wind speed in knots |
| wind_gust_kt | INTEGER | Gust speed (null if calm) |
| visibility_sm | FLOAT | Visibility in statute miles (capped at 10.0) |
| ceiling_ft | INTEGER | Ceiling height in feet (null if clear) |
| temp_c | FLOAT | Temperature in Celsius |
| dewpoint_c | FLOAT | Dewpoint in Celsius |
| altimeter_inhg | FLOAT | Altimeter setting |
| flight_category | VARCHAR | VFR, MVFR, IFR, LIFR |
| is_low_visibility | BOOLEAN | True if visibility < 3 statute miles |
| is_high_wind | BOOLEAN | True if wind speed >= 25kt or gust >= 35kt |
| airport_name | VARCHAR | From airport_metadata seed |
| city | VARCHAR | From airport_metadata seed |
| climate_region | VARCHAR | From airport_metadata seed |

### silver_taf_parsed
Source: bronze_taf + airport_metadata seed
Cleaned and enriched TAF forecast periods.

| Column | Type | Description |
|---|---|---|
| taf_period_id | VARCHAR | Surrogate key |
| station_id | VARCHAR | ICAO airport code |
| issue_time | TIMESTAMP | When TAF was issued |
| valid_time_from | TIMESTAMP | Period start |
| valid_time_to | TIMESTAMP | Period end |
| forecast_wind_speed_kt | INTEGER | Forecasted wind speed |
| forecast_visibility_sm | FLOAT | Forecasted visibility |
| forecast_ceiling_ft | INTEGER | Forecasted ceiling |
| forecast_flight_category | VARCHAR | Forecasted flight category |
| forecast_hours_out | INTEGER | Hours from issue time to period start |

### silver_forecast_actuals
Source: silver_metar_parsed + silver_taf_parsed
Joins TAF forecasts with METAR actuals for the same
airport and time window. Foundation for forecast accuracy.

| Column | Type | Description |
|---|---|---|
| station_id | VARCHAR | ICAO airport code |
| observation_time | TIMESTAMP | Actual observation time |
| issue_time | TIMESTAMP | TAF issue time matched to this observation |
| forecast_hours_out | INTEGER | How far out this forecast was made |
| actual_flight_category | VARCHAR | What actually happened |
| forecast_flight_category | VARCHAR | What was predicted |
| category_matched | BOOLEAN | True if forecast matched actual |
| actual_visibility_sm | FLOAT | Actual visibility |
| forecast_visibility_sm | FLOAT | Forecasted visibility |
| visibility_error_sm | FLOAT | Absolute difference in visibility |
| actual_wind_speed_kt | INTEGER | Actual wind speed |
| forecast_wind_speed_kt | INTEGER | Forecasted wind speed |
| wind_speed_error_kt | INTEGER | Absolute difference in wind speed |

---

## Gold Layer

Gold tables are analytical outputs optimized for reading.
These are the final data products SkyLake delivers.

### gold_airport_conditions
Hourly summary of conditions at each airport.
Primary table for the dashboard airport view.

| Column | Type | Description |
|---|---|---|
| station_id | VARCHAR | ICAO airport code |
| observation_hour | TIMESTAMP | Truncated to hour |
| flight_category | VARCHAR | VFR, MVFR, IFR, LIFR |
| avg_visibility_sm | FLOAT | Average visibility for the hour |
| avg_wind_speed_kt | FLOAT | Average wind speed for the hour |
| max_wind_gust_kt | INTEGER | Maximum gust recorded in the hour |
| avg_ceiling_ft | INTEGER | Average ceiling for the hour |
| is_low_visibility_hour | BOOLEAN | True if any obs in hour was IFR/LIFR |
| is_high_wind_hour | BOOLEAN | True if any obs had high wind |

### gold_forecast_accuracy
TAF forecast accuracy scores by airport and forecast horizon.

| Column | Type | Description |
|---|---|---|
| station_id | VARCHAR | ICAO airport code |
| issue_date | DATE | Date TAF was issued |
| forecast_hours_out | INTEGER | Forecast horizon (6, 12, 18, 24 hours) |
| total_periods | INTEGER | Number of forecast periods evaluated |
| category_match_rate | FLOAT | Percentage of periods with correct flight category |
| avg_visibility_error_sm | FLOAT | Average visibility forecast error |
| avg_wind_error_kt | FLOAT | Average wind speed forecast error |
| accuracy_score | FLOAT | Composite accuracy score 0-100 |

### gold_low_visibility_events
Detected periods of IFR or LIFR conditions.

| Column | Type | Description |
|---|---|---|
| event_id | VARCHAR | Unique event identifier |
| station_id | VARCHAR | ICAO airport code |
| event_start | TIMESTAMP | When low visibility began |
| event_end | TIMESTAMP | When conditions improved |
| duration_hours | FLOAT | Total duration in hours |
| min_visibility_sm | FLOAT | Lowest visibility recorded during event |
| min_flight_category | VARCHAR | Worst flight category during event |
| was_forecast | BOOLEAN | True if TAF predicted this event |

### gold_wind_disruption_windows
Detected periods of operationally significant wind.

| Column | Type | Description |
|---|---|---|
| event_id | VARCHAR | Unique event identifier |
| station_id | VARCHAR | ICAO airport code |
| event_start | TIMESTAMP | When high wind began |
| event_end | TIMESTAMP | When wind subsided |
| duration_hours | FLOAT | Total duration in hours |
| peak_wind_speed_kt | INTEGER | Maximum sustained wind during event |
| peak_gust_kt | INTEGER | Maximum gust during event |
| was_forecast | BOOLEAN | True if TAF predicted this event |

### gold_airport_risk_score
Composite operational risk score per airport per hour.
Primary output used in the dashboard risk view.

| Column | Type | Description |
|---|---|---|
| station_id | VARCHAR | ICAO airport code |
| score_hour | TIMESTAMP | Hour this score applies to |
| visibility_score | FLOAT | Visibility risk component 0-100 |
| wind_score | FLOAT | Wind risk component 0-100 |
| ceiling_score | FLOAT | Ceiling risk component 0-100 |
| forecast_confidence_score | FLOAT | TAF accuracy component 0-100 |
| composite_risk_score | FLOAT | Weighted composite score 0-100 |
| risk_level | VARCHAR | LOW, MODERATE, HIGH, SEVERE |
