# ADR-005: Data Source — NOAA Aviation Weather Center API

**Date:** 2026-03-12
**Status:** Accepted
**Deciders:** abdulrahimham

---

## Context

SkyLake needs a reliable, real-world data source for aviation
weather observations and forecasts that is:
- Free to use with no API key required
- Authoritative and production-grade
- Updated frequently (hourly or better)
- Structured and machine-readable
- Specific to aviation operations

---

## Decision

Use the **NOAA Aviation Weather Center (AWC) API** as the
sole data source for SkyLake MVP.

API base URL: https://aviationweather.gov/api/data/

No API key required. Completely free. Official U.S.
government aviation weather data.

---

## Reasoning

NOAA's Aviation Weather Center is the authoritative source
for U.S. aviation weather data. It is the same system used
by real airlines, pilots, air traffic controllers, and
flight dispatchers.

Key advantages:
- No API key or registration required
- No rate limiting for reasonable usage
- Official government data — highest possible credibility
- METARs updated every hour from thousands of stations
- TAFs issued every 6 hours covering 24-30 hour windows
- Returns structured JSON or XML — easy to parse
- Covers all major U.S. airports and many international ones

---

## The Two Core Endpoints

METAR observations:
https://aviationweather.gov/api/data/metar?ids=KJFK,KLAX&format=json

TAF forecasts:
https://aviationweather.gov/api/data/taf?ids=KJFK,KLAX&format=json

Pass comma-separated ICAO airport codes in the ids parameter.
Returns JSON array of observations or forecast periods.

---

## Airports Monitored in MVP

KJFK — John F. Kennedy International (New York)
KLAX — Los Angeles International
KORD — O'Hare International (Chicago)
KATL — Hartsfield-Jackson (Atlanta)
KDFW — Dallas/Fort Worth International
KSEA — Seattle-Tacoma International
KDEN — Denver International
KMIA — Miami International

These eight airports represent major U.S. hubs across
different climate regions, maximizing weather variety
in the dataset.

---

## Alternatives Considered

| Option | Reason Rejected |
|---|---|
| OpenWeatherMap | Requires API key. Rate limited on free tier. Not aviation-specific — no METAR or TAF data. |
| Tomorrow.io | Commercial product. Costs money beyond free tier. Overkill for portfolio project. |
| Weather.gov API | General weather, not aviation-specific. Less structured data format. |
| Synthetic/mock data | No real-world credibility. Defeats the purpose of demonstrating real ingestion skills. |

---

## Consequences

- Ingestion client calls two endpoints: /metar and /taf
- Airport list configured via SKYLAKE_AIRPORTS in .env
- Raw responses stored as JSON in data/raw/ partitioned by date
- No authentication logic needed in the ingestion client
- Data volume: approximately 8 airports x 24 hours = 192 METAR
  records per day plus TAF forecast periods
