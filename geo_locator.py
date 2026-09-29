import os

import requests
from dataclasses import dataclass


class GeoLocationError(Exception):
    """Ошибка определения местоположения."""


@dataclass(frozen=True)
class Location:
    city: str
    latitude: float
    longitude: float


def get_location() -> Location:

    url = os.getenv("GEO_API_URL", "https://ipinfo.io/json")

    fallback_city = os.getenv("GEO_API_FALLBACK_CITY")
    fallback_lat = os.getenv("GEO_API_FALLBACK_LAT")
    fallback_lon = os.getenv("GEO_API_FALLBACK_LON")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        city = data.get("city")
        loc = data.get("loc")

        if city and loc:
            latitude, longitude = map(float, loc.split(","))

            return Location(
                city=city,
                latitude=latitude,
                longitude=longitude,
            )

        raise ValueError("Гео-API вернул некорректные данные.")

    except (
        requests.RequestException,
        ValueError,
    ) as exc:

        if fallback_city and fallback_lat and fallback_lon:
            try:
                return Location(
                    city=fallback_city,
                    latitude=float(fallback_lat),
                    longitude=float(fallback_lon),
                )
            except ValueError as fallback_exc:
                raise GeoLocationError(
                    "Некорректные координаты fallback-параметров."
                ) from fallback_exc

        raise GeoLocationError(
            f"Не удалось определить местоположение: {exc}. "
        ) from exc