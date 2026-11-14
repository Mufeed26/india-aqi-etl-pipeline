from datetime import datetime
import logging
import sqlite3
import requests

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

CITIES = {
    "Bengaluru": (12.9716, 77.5946),
    "Delhi": (28.7041, 77.1025),
    "Mumbai": (19.0760, 72.8777),
    "Chennai": (13.0827, 80.2707),
    "Hyderabad": (17.3850, 78.4867),
}

DB_NAME = "india_environment.db"


def setup_database():
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS city_metrics (
            city TEXT,
            recorded_hour TEXT,
            temperature_c REAL,
            wind_speed_kmh REAL,
            pm2_5 REAL,
            air_quality_status TEXT,
            ingested_at TEXT,
            PRIMARY KEY (city, recorded_hour)
        )
    """)
  conn.commit()
  conn.close()


def classify_air_quality(pm25):
  if pm25 is None:
    return "UNKNOWN"
  if pm25 <= 30:
    return "GOOD"
  elif pm25 <= 60:
    return "MODERATE"
  elif pm25 <= 90:
    return "POOR"
  else:
    return "SEVERE"


def extract_and_transform():
  clean_records = []
  ingested_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  for city, (lat, lon) in CITIES.items():
    try:
      weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m"
      w_res = requests.get(weather_url, timeout=10)
      w_res.raise_for_status()
      weather = w_res.json().get("current", {})

      aqi_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=pm2_5"
      a_res = requests.get(aqi_url, timeout=10)
      a_res.raise_for_status()
      aqi = a_res.json().get("current", {})

      recorded_hour = weather.get("time")
      temp = float(weather.get("temperature_2m", 0.0))
      wind = float(weather.get("wind_speed_10m", 0.0))
      pm25 = float(aqi.get("pm2_5", 0.0))
      status = classify_air_quality(pm25)

      clean_records.append(
          (city.upper(), recorded_hour, temp, wind, pm25, status, ingested_at)
      )
      logging.info(
          f"Fetched {city}: Temp={temp}°C, PM2.5={pm25} ({status})"
      )

    except requests.exceptions.RequestException as e:
      logging.error(f"API failed for {city}: {e}")

  return clean_records


def load_data(records):
  if not records:
    logging.warning("No records to insert.")
    return

  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()

  cursor.executemany(
      """
        INSERT OR IGNORE INTO city_metrics 
        (city, recorded_hour, temperature_c, wind_speed_kmh, pm2_5, air_quality_status, ingested_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
      records,
  )

  inserted_count = cursor.rowcount
  conn.commit()
  conn.close()
  logging.info(
      f"Load complete. {inserted_count} new rows inserted into {DB_NAME}."
  )


if __name__ == "__main__":
  logging.info("Starting India Weather & AQI ETL Pipeline...")
  setup_database()
  data = extract_and_transform()
  load_data(data)