# weather_app.py
The Python app was made to collect weather data using the OpenWeatherMap API key from my location and save it to a json file for weather forecasting. The collected is stored to a data silo (JSON file) and data warehouse (Postgres). You can get the API key for free by registering.

### App requirements:
Python >= 3.11.7, configparser, concurrent.futures, datetime, functools, json, logging, typing, psycopg2-binary, pyowm, geocoder, contextlib, cachetools, retrying, geopy, and OpenWeatherMap.
