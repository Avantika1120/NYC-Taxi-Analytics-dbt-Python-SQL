with source as (
    select * from {{ source('raw', 'yellow_tripdata') }}
),

cleaned as (
    select
        {{ generate_surrogate_key([
            'tpep_pickup_datetime',
            'tpep_dropoff_datetime',
            'PULocationID',
            'DOLocationID',
            'fare_amount',
            'total_amount'
        ]) }} as trip_id,
        cast(VendorID as integer) as vendor_id,
        cast(tpep_pickup_datetime as timestamp) as pickup_datetime,
        cast(tpep_dropoff_datetime as timestamp) as dropoff_datetime,
        cast(passenger_count as integer) as passenger_count,
        cast(trip_distance as double) as trip_distance_miles,
        cast(RatecodeID as integer) as rate_code_id,
        cast(store_and_fwd_flag as varchar) as store_and_fwd_flag,
        cast(PULocationID as integer) as pickup_location_id,
        cast(DOLocationID as integer) as dropoff_location_id,
        cast(payment_type as integer) as payment_type,
        cast(fare_amount as double) as fare_amount,
        cast(extra as double) as extra_amount,
        cast(mta_tax as double) as mta_tax,
        cast(tip_amount as double) as tip_amount,
        cast(tolls_amount as double) as tolls_amount,
        cast(improvement_surcharge as double) as improvement_surcharge,
        cast(total_amount as double) as total_amount,
        cast(congestion_surcharge as double) as congestion_surcharge,
        cast(coalesce(Airport_fee, 0) as double) as airport_fee
    from source
    where tpep_pickup_datetime is not null
      and tpep_dropoff_datetime is not null
      and tpep_dropoff_datetime > tpep_pickup_datetime
      and trip_distance >= 0
      and total_amount >= 0
)

select * from cleaned
