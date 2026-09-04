select
    pickup_location_id as location_id,
    pickup_borough as borough,
    pickup_zone as zone,
    count(*) as total_trips,
    round(sum(total_amount), 2) as total_revenue,
    round(avg(total_amount), 2) as avg_trip_value,
    round(avg(trip_distance_miles), 2) as avg_trip_distance_miles,
    round(avg(trip_duration_minutes), 2) as avg_trip_duration_minutes,
    round(avg(revenue_per_mile), 2) as avg_revenue_per_mile,
    round(avg(tip_rate), 4) as avg_tip_rate,
    round(sum(case when is_airport_trip then 1 else 0 end) * 1.0 / count(*), 4) as airport_trip_share
from {{ ref('fct_trips') }}
where trip_quality_flag = 'standard'
  and pickup_location_id is not null
group by 1, 2, 3
order by total_revenue desc
