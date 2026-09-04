select *
from {{ ref('mart_zone_performance') }}
where total_trips < 0
   or total_revenue < 0
   or avg_trip_value < 0
   or avg_trip_distance_miles < 0
   or avg_trip_duration_minutes < 0
