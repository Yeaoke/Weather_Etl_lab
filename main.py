import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError

from db_models import (
    get_city_forecast,
    get_engine,
    init_db,
    save_forecast,
)
from exporter import export_markdown
from geo_locator import GeoLocationError, get_location
from weather_client import WeatherAPIError, get_forecast


BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

if not ENV_PATH.exists():
    raise FileNotFoundError(
        f"Файл .env не найден: {ENV_PATH}"
    )

load_dotenv(dotenv_path=ENV_PATH, override=True)

api_key = os.getenv("WEATHER_API_KEY")

print(f"Путь к .env: {ENV_PATH}")
print(f"Файл существует: {ENV_PATH.exists()}")
print(f"API-ключ загружен: {bool(api_key)}")
print(f"Длина API-ключа: {len(api_key) if api_key else 0}")


def main() -> None:
    load_dotenv(BASE_DIR / ".env")

    try:
        if not os.getenv("WEATHER_API_KEY"):
            raise WeatherAPIError(
                "Не найден WEATHER_API_KEY"
            )

        location = get_location()

        print(
            f"Город: {location.city}\n"
            f"Координаты: {location.latitude:.4f}, "
            f"{location.longitude:.4f}"
        )

        forecast = get_forecast(
            location.latitude,
            location.longitude,
        )

        if not forecast:
            raise WeatherAPIError(
                "API не вернул точки прогноза"
            )

        print(
            "Даты прогноза: " + ", ".join(str(item["forecast_date"])
                for item in forecast
            )
        )

        engine = get_engine()
        init_db(engine)

        saved = save_forecast(
            engine,
            location.city,
            forecast,
        )

        records = get_city_forecast(
            engine,
            location.city,
        )

        output_file = os.getenv(
            "OUTPUT_FILE",
            "weather_report.md",
        )

        path = export_markdown(records, output_file)

        print(f"Новых записей сохранено: {saved}")
        print(f"Всего записей города в БД: {len(records)}")
        print(f"MD-файл: {path.resolve()}")

    except (
        GeoLocationError,
        WeatherAPIError,
        SQLAlchemyError,
        OSError,
        ValueError,
    ) as exc:
        print(f"Ошибка: {exc}")


if __name__ == "__main__":
    main()