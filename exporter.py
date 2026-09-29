from pathlib import Path


def export_markdown(records, output_file: str) -> Path:
    if not records:
        raise ValueError("Нет данных для экспорта.")

    city = records[0].city
    start = records[0].forecast_date
    end = records[-1].forecast_date

    lines = [
        "# Прогноз погоды",
        "",
        f"Автоматически определённая локация: **{city}**",
        f"Период: **{start} – {end}**",
        "",
        "| Дата | Мин. темп. (°C) | Макс. темп. (°C) | Описание | Влажность (%) | Ветер (м/с) |",
        "|---|---:|---:|---|---:|---:|",
    ]

    for row in records:
        description = row.description.replace("|", "\\|")

        lines.append(
            f"| {row.forecast_date} | "
            f"{row.temp_min:.1f} | "
            f"{row.temp_max:.1f} | "
            f"{description.capitalize()} | "
            f"{row.humidity} | "
            f"{row.wind_speed:.1f} |"
        )

    path = Path(output_file)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return path