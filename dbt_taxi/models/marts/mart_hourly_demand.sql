select
    pickup_weekday,
    pickup_hour,
    count(*) as total_trips,
    round(sum(total_amount), 2) as total_revenue,
    round(avg(total_amount), 2) as avg_trip_value,
    round(avg(trip_duration_minutes), 2) as avg_trip_duration_minutes
from {{ ref('fct_trips') }}
where trip_quality_flag = 'standard'
group by 1, 2
