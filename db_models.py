from datetime import date, datetime, timezone
import os

from sqlalchemy import (
    Date,
    DateTime,
    Float,
    Integer,
    String,
    UniqueConstraint,
    create_engine,
    select,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
)


class Base(DeclarativeBase):
    pass


class WeatherForecast(Base):
    __tablename__ = "weather_lab_db"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    forecast_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    temp_min: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    temp_max: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    humidity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    wind_speed: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "city",
            "forecast_date",
            name="uq_weather_city_date",
        ),
    )


def get_engine():
    db_url = os.getenv("DB_URL")

    if not db_url:
        raise ValueError("Не задан DB_URL.")

    return create_engine(db_url)


def init_db(engine) -> None:
    Base.metadata.create_all(engine)


def save_forecast(engine, city: str, forecast: list[dict]) -> int:

    saved = 0

    with Session(engine) as session:
        for item in forecast:
            exists = session.scalar(
                select(WeatherForecast).where(
                    WeatherForecast.city == city,
                    WeatherForecast.forecast_date
                    == item["forecast_date"],
                )
            )

            if exists:
                continue

            session.add(
                WeatherForecast(
                    city=city,
                    forecast_date=item["forecast_date"],
                    temp_min=item["temp_min"],
                    temp_max=item["temp_max"],
                    humidity=item["humidity"],
                    wind_speed=item["wind_speed"],
                    description=item["description"],
                )
            )

            saved += 1

        session.commit()

    return saved


def get_city_forecast(engine, city: str) -> list[WeatherForecast]:

    with Session(engine) as session:
        return list(
            session.scalars(select(WeatherForecast).where(WeatherForecast.city == city).order_by(WeatherForecast.forecast_date))
        )