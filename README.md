# India Weather & Air Quality (AQI) ETL Pipeline

An automated, idempotent **Extract, Transform, Load (ETL)** data pipeline built with **Python** and **SQLite**. It ingests live meteorological and air quality data across 5 major Indian cities, enforces schema integrity and deduplication, and exposes analytical insights using SQL window functions.

## Architecture

```text
+-----------------------+      +-----------------------+
| Open-Meteo Weather API|      | Open-Meteo AQI API    |
+-----------+-----------+      +-----------+-----------+
            |                              |
            +--------------+---------------+
                           |
                           v
              +-------------------------+
              |  Python ETL (pipeline)  |
              | - Schema Validation     |
              | - AQI Categorization    |
              | - Fault-Tolerant Logs   |
              +------------+------------+
                           |
                           v
              +-------------------------+
              |  SQLite Data Warehouse  |
              | (Composite Primary Key) |
              +------------+------------+
                           |
                           v
              +-------------------------+
              | SQL Analytics Layer     |
              | (CTEs & Window Funcs)   |
              +-------------------------+