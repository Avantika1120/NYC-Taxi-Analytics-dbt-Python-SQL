select
    cast(LocationID as integer) as location_id,
    trim(Borough) as borough,
    trim(Zone) as zone,
    trim(service_zone) as service_zone
from {{ source('raw', 'taxi_zones') }}
where LocationID is not null
