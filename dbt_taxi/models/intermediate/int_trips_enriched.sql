with trips as (
    select * from {{ ref('stg_yellow_trips') }}
),

zones as (
    select * from {{ ref('stg_taxi_zones') }}
),

enriched as (
    select
        t.*,
        pu.borough as pickup_borough,
        pu.zone as pickup_zone,
        do.borough as dropoff_borough,
        do.zone as dropoff_zone,
        date_diff('minute', pickup_datetime, dropoff_datetime) as trip_duration_minutes,
        case
            when date_diff('minute', pickup_datetime, dropoff_datetime) > 0
            then trip_distance_miles / (date_diff('minute', pickup_datetime, dropoff_datetime) / 60.0)
        end as avg_speed_mph,
        case when fare_amount > 0 then tip_amount / fare_amount else 0 end as tip_rate,
        case when trip_distance_miles > 0 then total_amount / trip_distance_miles end as revenue_per_mile,
        extract(hour from pickup_datetime) as pickup_hour,
        strftime(pickup_datetime, '%A') as pickup_weekday,
        cast(pickup_datetime as date) as pickup_date,
        date_trunc('month', pickup_datetime) as pickup_month,
        case
            when extract(hour from pickup_datetime) between 5 and 10 then 'Morning'
            when extract(hour from pickup_datetime) between 11 and 15 then 'Midday'
            when extract(hour from pickup_datetime) between 16 and 20 then 'Evening'
            else 'Overnight'
        end as daypart,
        case
            when lower(coalesce(pu.zone, '')) like '%airport%'
              or lower(coalesce(do.zone, '')) like '%airport%'
              or airport_fee > 0
            then true else false
        end as is_airport_trip,
        case
            when trip_distance_miles = 0 then 'zero_distance'
            when date_diff('minute', pickup_datetime, dropoff_datetime) > 180 then 'long_duration'
            when total_amount > 300 then 'high_value'
            else 'standard'
        end as trip_quality_flag
    from trips t
    left join zones pu on t.pickup_location_id = pu.location_id
    left join zones do on t.dropoff_location_id = do.location_id
)

select * from enriched
