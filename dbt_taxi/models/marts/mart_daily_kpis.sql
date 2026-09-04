select
    pickup_date,
    count(*) as total_trips,
    round(sum(total_amount), 2) as total_revenue,
    round(avg(total_amount), 2) as avg_trip_value,
    round(avg(trip_distance_miles), 2) as avg_trip_distance_miles,
    round(avg(trip_duration_minutes), 2) as avg_trip_duration_minutes,
    round(avg(tip_rate), 4) as avg_tip_rate,
    round(sum(case when is_airport_trip then 1 else 0 end) * 1.0 / count(*), 4) as airport_trip_share,
    round(sum(case when payment_type = 1 then 1 else 0 end) * 1.0 / count(*), 4) as card_payment_share
from {{ ref('fct_trips') }}
where trip_quality_flag = 'standard'
group by 1
order by 1
