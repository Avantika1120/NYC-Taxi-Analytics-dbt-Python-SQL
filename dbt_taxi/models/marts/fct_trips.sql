{{ config(
    materialized='incremental',
    unique_key='trip_id',
    incremental_strategy='delete+insert'
) }}

select
    trip_id,
    vendor_id,
    pickup_datetime,
    dropoff_datetime,
    pickup_date,
    pickup_month,
    pickup_hour,
    pickup_weekday,
    daypart,
    passenger_count,
    trip_distance_miles,
    trip_duration_minutes,
    avg_speed_mph,
    pickup_location_id,
    pickup_borough,
    pickup_zone,
    dropoff_location_id,
    dropoff_borough,
    dropoff_zone,
    payment_type,
    fare_amount,
    tip_amount,
    tip_rate,
    tolls_amount,
    total_amount,
    revenue_per_mile,
    congestion_surcharge,
    airport_fee,
    is_airport_trip,
    trip_quality_flag
from {{ ref('int_trips_enriched') }}

{% if is_incremental() %}
where pickup_datetime > (select coalesce(max(pickup_datetime), timestamp '1900-01-01') from {{ this }})
{% endif %}
