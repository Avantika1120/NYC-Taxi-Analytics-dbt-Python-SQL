from __future__ import annotations

import argparse
from pathlib import Path

import requests

TRIP_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year}-{month:02d}.parquet"
ZONE_URL = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"


def download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_size > 0:
        print(f"Skipping existing file: {destination}")
        return

    print(f"Downloading {url}")
    with requests.get(url, stream=True, timeout=120) as response:
        response.raise_for_status()
        with destination.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    handle.write(chunk)
    print(f"Saved {destination} ({destination.stat().st_size / 1_000_000:.1f} MB)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Download NYC TLC Yellow Taxi data.")
    parser.add_argument("--year", type=int, default=2024)
    parser.add_argument("--month", type=int, default=1, choices=range(1, 13))
    args = parser.parse_args()

    data_dir = Path("data")
    trip_file = data_dir / f"yellow_tripdata_{args.year}-{args.month:02d}.parquet"
    zone_file = data_dir / "taxi_zone_lookup.csv"

    download(TRIP_URL.format(year=args.year, month=args.month), trip_file)
    download(ZONE_URL, zone_file)


if __name__ == "__main__":
    main()
