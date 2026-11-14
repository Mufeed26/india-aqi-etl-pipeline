import sqlite3

conn = sqlite3.connect("india_environment.db")
cursor = conn.cursor()

print("\n--- 1. Latest Air Quality Ranking (Using SQL Window Function) ---")
query_ranking = """
WITH LatestReadings AS (
    SELECT 
        city,
        pm2_5,
        air_quality_status,
        temperature_c,
        ROW_NUMBER() OVER (PARTITION BY city ORDER BY recorded_hour DESC) as rn
    FROM city_metrics
)
SELECT 
    city, 
    pm2_5, 
    air_quality_status, 
    temperature_c
FROM LatestReadings
WHERE rn = 1
ORDER BY pm2_5 DESC;
"""

for row in cursor.execute(query_ranking):
  print(
      f"City: {row[0]:<10} | PM2.5: {row[1]:<6} | Status: {row[2]:<10} | Temp:"
      f" {row[3]}°C"
  )

print("\n--- 2. Average PM2.5 & Total Records per City ---")
query_summary = """
SELECT 
    city,
    COUNT(*) as total_snapshots,
    ROUND(AVG(pm2_5), 2) as avg_pm25,
    MAX(temperature_c) as max_temp
FROM city_metrics
GROUP BY city
ORDER BY avg_pm25 DESC;
"""

for row in cursor.execute(query_summary):
  print(
      f"City: {row[0]:<10} | Snapshots: {row[1]:<3} | Avg PM2.5: {row[2]:<6} |"
      f" Max Temp: {row[3]}°C"
  )

conn.close()