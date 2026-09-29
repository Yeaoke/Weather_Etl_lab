# Weather ETL Lab

Вводная лабораторная работа по Python: программа автоматически определяет местоположение по IP, получает прогноз OpenWeatherMap, агрегирует 3-часовые данные до дневных сводок, сохраняет результат в SQLite через SQLAlchemy и экспортирует его в Markdown.

## Технологии

- Python 3.10+
- `requests` — HTTP-запросы
- `SQLAlchemy 2.x` — ORM и SQLite
- `python-dotenv` — конфигурация через `.env`
- OpenWeatherMap Forecast API
- IP Geolocation API (`ipinfo.io` по умолчанию)

## Структура

```
weather-etl-lab/
├── .gitignore
├── .env.example
├── README.md
├── requirements.txt
├── main.py
├── geo_locator.py
├── weather_client.py
├── db_models.py
└── exporter.py
```

## Установка

```bash
git clone <URL_ВАШЕГО_REPOSITORY>
cd weather-etl-lab

python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Установить зависимости:

```bash
pip install -r requirements.txt
```

## Настройка

Скопируйте `.env.example` в `.env`:

```bash
cp .env.example .env
```

Получите API-ключ на OpenWeatherMap и укажите его:

```env
WEATHER_API_KEY=your_real_key
WEATHER_API_BASE_URL=https://api.openweathermap.org/data/2.5
GEO_API_URL=https://ipinfo.io/json
GEO_API_FALLBACK_CITY=Moscow

DB_URL=sqlite:///weather_lab.db
DB_USER=
DB_PASSWORD=

ENVIRONMENT=dev
OUTPUT_FILE=weather_report.md
```

Для fallback с координатами можно дополнительно задать:

```env
GEO_API_FALLBACK_LAT=55.7558
GEO_API_FALLBACK_LON=37.6176
```

`.env` содержит секреты и не должен публиковаться.

## Запуск

```bash
python main.py
```

Пример консольного отчёта:

```text
=== Weather ETL Lab ===
Город: Москва
Координаты: 55.7558, 37.6176
Даты прогноза: 2026-09-15, 2026-09-16, 2026-09-17, 2026-09-18
Новых записей сохранено: 4
Всего записей города в БД: 4
Markdown-файл: .../weather_report.md
```

## Пример Markdown

```markdown
# Прогноз погоды

Автоматически определённая локация: **Москва**
Период: **2026-09-15 – 2026-09-18**

| Дата | Мин. темп. (°C) | Макс. темп. (°C) | Описание | Влажность (%) | Ветер (м/с) |
|---|---:|---:|---|---:|---:|
| 2026-09-15 | 8.0 | 14.0 | Облачно | 75 | 4.0 |
```

## Обработка ошибок

Предусмотрены сетевые ошибки, HTTP 401/404/429 OpenWeatherMap, некорректные данные геолокации, отсутствие API-ключа и отсутствие данных для экспорта.

## GitHub

Перед публикацией проверьте:

```bash
git status
```

Убедитесь, что `.env`, `*.db` и `weather_report.md` не попали в список отслеживаемых файлов.

```bash
git add .
git commit -m "Add weather ETL laboratory"
git push
```
