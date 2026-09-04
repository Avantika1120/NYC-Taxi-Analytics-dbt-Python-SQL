from __future__ import annotations

from pathlib import Path

import pandas as pd

DATA = Path("data")
DATA.mkdir(exist_ok=True)

trips = pd.DataFrame(
    [
        {
            "VendorID": 1,
            "tpep_pickup_datetime": "2024-01-01 08:00:00",
            "tpep_dropoff_datetime": "2024-01-01 08:20:00",
            "passenger_count": 1,
            "trip_distance": 4.2,
            "RatecodeID": 1,
            "store_and_fwd_flag": "N",
            "PULocationID": 1,
            "DOLocationID": 2,
            "payment_type": 1,
            "fare_amount": 20.0,
            "extra": 1.0,
            "mta_tax": 0.5,
            "tip_amount": 4.0,
            "tolls_amount": 0.0,
            "improvement_surcharge": 1.0,
            "total_amount": 26.5,
            "congestion_surcharge": 0.0,
            "Airport_fee": 0.0,
        },
        {
            "VendorID": 2,
            "tpep_pickup_datetime": "2024-01-01 17:30:00",
            "tpep_dropoff_datetime": "2024-01-01 18:05:00",
            "passenger_count": 2,
            "trip_distance": 9.8,
            "RatecodeID": 2,
            "store_and_fwd_flag": "N",
            "PULocationID": 2,
            "DOLocationID": 3,
            "payment_type": 1,
            "fare_amount": 42.0,
            "extra": 1.0,
            "mta_tax": 0.5,
            "tip_amount": 8.0,
            "tolls_amount": 0.0,
            "improvement_surcharge": 1.0,
            "total_amount": 54.75,
            "congestion_surcharge": 0.0,
            "Airport_fee": 2.25,
        },
        {
            "VendorID": 1,
            "tpep_pickup_datetime": "2024-01-02 12:15:00",
            "tpep_dropoff_datetime": "2024-01-02 12:30:00",
            "passenger_count": 1,
            "trip_distance": 2.1,
            "RatecodeID": 1,
            "store_and_fwd_flag": "N",
            "PULocationID": 3,
            "DOLocationID": 1,
            "payment_type": 2,
            "fare_amount": 13.0,
            "extra": 0.0,
            "mta_tax": 0.5,
            "tip_amount": 0.0,
            "tolls_amount": 0.0,
            "improvement_surcharge": 1.0,
            "total_amount": 14.5,
            "congestion_surcharge": 0.0,
            "Airport_fee": 0.0,
        },
    ]
)
trips["tpep_pickup_datetime"] = pd.to_datetime(trips["tpep_pickup_datetime"])
trips["tpep_dropoff_datetime"] = pd.to_datetime(trips["tpep_dropoff_datetime"])
trips.to_parquet(DATA / "yellow_tripdata_2024-01.parquet", index=False)

zones = pd.DataFrame(
    [
        {"LocationID": 1, "Borough": "Manhattan", "Zone": "Midtown Center", "service_zone": "Yellow Zone"},
        {"LocationID": 2, "Borough": "Queens", "Zone": "JFK Airport", "service_zone": "Airports"},
        {"LocationID": 3, "Borough": "Brooklyn", "Zone": "Downtown Brooklyn", "service_zone": "Boro Zone"},
    ]
)
zones.to_csv(DATA / "taxi_zone_lookup.csv", index=False)

print("Created CI fixture data")
