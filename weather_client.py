import os

import requests

from collections import Counter
from datetime import date, datetime, timedelta, timezone


class WeatherAPIError(Exception):
    """Ошибка при работе с OpenWeatherMap API."""


def get_forecast(city: str, latitude: float, longitude: float) -> list[dict]:

    if not (city or (latitude is not None and longitude is not None)):
        raise WeatherAPIError("Необходимо указать city либо latitude/longitude.")

    base_url = os.getenv("WEATHER_API_BASE_URL", "https://api.openweathermap.org/data/2.5").rstrip("/")

    api_key = os.getenv("WEATHER_API_KEY")

    if not api_key:
        raise WeatherAPIError("Не задан WEATHER_API_KEY. Проверь файл .env.")

    url = f"{base_url}/forecast"

    print("city", city, "lan", latitude, "lon", longitude)

    params = {}

    if latitude is not None and longitude is not None:
        params["lat"] = latitude
        params["lon"] = longitude
    else:
        params["q"] = city

    params.update({
        "appid": api_key,
        "units": "metric",
        "lang": "ru",
    })

    try:
        response = requests.get(url, params=params, timeout=15)

    except requests.RequestException as exc:
        raise WeatherAPIError(
            f"Сетевая ошибка OpenWeatherMap: {exc}"
        ) from exc

    if response.status_code == 401:
        try:
            error_data = response.json()
            message = error_data.get("message", "Причина не указана")
        except ValueError:
            message = response.text

        raise WeatherAPIError(
            f"OpenWeatherMap HTTP 401: {message}"
        )

    if response.status_code == 404:
        raise WeatherAPIError(
            "Город или координаты не найдены (HTTP 404)."
        )

    try:
        response.raise_for_status()
        data = response.json()

    except (requests.RequestException, ValueError) as exc:
        raise WeatherAPIError(
            f"Ошибка ответа OpenWeatherMap: {exc}"
        ) from exc

    if str(data.get("cod")) != "200":
        raise WeatherAPIError(
            data.get("message", "Неизвестная ошибка API.")
        )

    forecast_points = data.get("list", [])

    if not forecast_points:
        raise WeatherAPIError(
            "OpenWeatherMap не вернул точки прогноза."
        )

    timezone_offset = data.get("city", {}).get("timezone", 0)

    return aggregate_forecast(
        forecast_points,
        timezone_offset,
    )


def aggregate_forecast(points: list[dict], timezone_offset: int = 0) -> list[dict]:

    if not points:
        return []

    groups: dict[date, list[dict]] = {}

    for point in points:
        local_datetime = (datetime.fromtimestamp(point["dt"], tz=timezone.utc) + timedelta(seconds=timezone_offset))

        groups.setdefault(local_datetime.date(), []).append(point)

    result = []

    for forecast_date, items in sorted(groups.items())[:4]:

        descriptions = [
            item.get("weather", [{}])[0].get("description", "Нет данных")
            for item in items
        ]

        noon_item = min(items, key=lambda item: abs(
                (
                    datetime.fromtimestamp
                    (
                        item["dt"],
                        tz=timezone.utc,
                    )
                    + timedelta(seconds=timezone_offset)
                ).hour - 12
            ),
        )

        description = (
            noon_item.get("weather", [{}])[0].get("description")
            or Counter(descriptions).most_common(1)[0][0]
        )

        result.append(
            {
                "forecast_date": forecast_date,

                "temp_min": min(
                    item["main"]["temp_min"]
                    for item in items
                ),

                "temp_max": max(
                    item["main"]["temp_max"]
                    for item in items
                ),

                "humidity": round(
                    sum(
                        item["main"]["humidity"]
                        for item in items
                    ) / len(items)
                ),

                "wind_speed": max(
                    item["wind"]["speed"]
                    for item in items
                ),

                "description": description,
            }
        )

    return result