import geocoder
import json
from datetime import datetime
from psycopg2 import connect
import configparser
from typing import Union, Tuple, Any
from pyowm import OWM
from contextlib import contextmanager
import logging


logging.basicConfig(level=logging.INFO)


class ErrorCode:
    # Class that defines error codes for different types of errors that can occur.
    INVALID_API_KEY = 1
    CONFIG_FILE_READ_ERROR = 2
    COORDINATES_RETRIEVAL_ERROR = 3
    CURRENT_WEATHER_RETRIEVAL_ERROR = 4
    WEATHER_DATA_FETCH_ERROR = 5
    DATABASE_CONNECTION_ERROR = 6
    DATA_INSERTION_ERROR = 7
    JSON_UPDATE_ERROR = 8
    FILE_NOT_FOUND_ERROR = 9


class WeatherDataFetcher:
    # Class that fetches weather data for a given location.
    api_key = None

    def __init__(self, api_key: str) -> None:
        # Initializes the WeatherDataFetcher object.
        self.weather_cache = {}
        if self.validate_api_key(api_key):
            self.api_key = api_key
        else:
            logging.error("Invalid API key provided.")
            self.api_key = None

    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        # Validates the given API key.
        return bool(api_key and not api_key.isspace())

    @classmethod
    def get_config(cls, key: str) -> str:
        # Retrieves the value associated with the given key from the configuration file.
        try:
            config = configparser.ConfigParser()
            config.read('config.ini')
            return config.get('API', key)
        except configparser.Error as e:
            logging.error("Issue reading the configuration file.")
            return "", ErrorCode.CONFIG_FILE_READ_ERROR
    
    def get_coordinates(self, location: str) -> Union[Tuple[float, float], None]:
        # Retrieves the latitude and longitude coordinates for the given location.
        if location in self.weather_cache:
            return self.weather_cache[location]['coordinates']
        
        try:
            geo_location = geocoder.osm(location)
            coordinates = geo_location.latlng if geo_location.latlng else None
            if coordinates:
                self.weather_cache[location] = {'coordinates': coordinates}
            return coordinates
        except Exception as coordinates_retrieval_error:
            logging.error(f"Error getting coordinates for location: {location}. Error message: {coordinates_retrieval_error}")
            return None, ErrorCode.COORDINATES_RETRIEVAL_ERROR
    
    def get_current_weather(self, lat: float, lon: float) -> Tuple[str, str, Any]:
        # Retrieves the current weather for the given latitude and longitude coordinates.
        try:
            owm = OWM(self.api_key)
            weather_manager = owm.weather_manager()
            observation = weather_manager.weather_at_coords(lat, lon)
            current_date = datetime.now().strftime('%Y-%m-%d')
            current_time = datetime.now().strftime('%H:%M:%S')
            weather = observation.weather
            wind = weather.wind()
            humidity = weather.humidity
            return current_date, current_time, weather, wind, humidity
        except Exception as current_weather_retrieval_error:
            logging.error(f"Error getting current weather: {current_weather_retrieval_error}")
            return "", "", None, ErrorCode.CURRENT_WEATHER_RETRIEVAL_ERROR
    
    def fetch_weather_data(self, location: str) -> None:
        # Fetches weather data for the given location.
        try:
            if location in self.weather_cache:
                weather_data = self.weather_cache[location]
            else:
                weather_data = self.fetch_weather_data_from_api(location)

                if weather_data is not None:
                    self.weather_cache[location] = weather_data

            if weather_data is None:
                logging.error("Error fetching weather data: Weather data is None.")
                return ErrorCode.WEATHER_DATA_FETCH_ERROR
            
            db_handler = DatabaseHandler()
            db_handler.insert_data(weather_data)

            json_handler = JSONHandler()
            json_handler.update_data(weather_data)

            print(f"As of: {weather_data['date']} | {weather_data['time']}")
            print(f"Current weather at {location}:")
            print(f"Weather Status: {weather_data['weather_status']}")
            print(f"Temperature: {weather_data['temperature']}°C")
            print(f"Wind Speed: {weather_data['wind_speed']} m/s")
            print(f"Humidity: {weather_data['humidity']}%")

        except FileNotFoundError:
            logging.error("Error: The weather data file does not exist.", ErrorCode.FILE_NOT_FOUND_ERROR)
        except Exception as weather_data_fetch_error:
            logging.error(f"Error fetching weather data: {weather_data_fetch_error}", ErrorCode.WEATHER_DATA_FETCH_ERROR)
    
    def fetch_weather_data_from_api(self, location: str) -> Union[dict, None]:
        # Fetches weather data for the given location from the weather API.
        coordinates = self.get_coordinates(location)
        if coordinates[1]:
            lat, lon = coordinates
            current_date, current_time, weather, wind, humidity = self.get_current_weather(lat, lon)
            if weather:
                temperature = f"{weather.temperature('celsius')['temp']}"
                weather_status = weather.status
                weather_data = {
                    'date': current_date,
                    'time': current_time,
                    'location': location,
                    'weather_status': weather_status,
                    'temperature': temperature,
                    'wind_speed': wind['speed'],
                    'humidity': humidity,
                }
                return weather_data
            else:
                logging.error(f"Unable to fetch weather data for {location}.")
                return ErrorCode.WEATHER_DATA_FETCH_ERROR
        else:
            logging.error(f"Unable to fetch coordinates for {location}.")
            return ErrorCode.COORDINATES_RETRIEVAL_ERROR


class DatabaseHandler:
    # Class that handles database operations.
    def __init__(self) -> None:
        # Initializes the DatabaseHandler object.
        self.db_conn = None

    def connect_to_db(self) -> Any:
        # Connects to the database.
        try:
            config = configparser.ConfigParser()
            config.read('config.ini')
            conn = connect(
                host=config.get('Database', 'host'),
                database=config.get('Database', 'database'),
                user=config.get('Database', 'user'),
                password=config.get('Database', 'password')
            )
            return conn
        except Exception as database_connection_error:
            logging.error(f"Error connecting to the database: {database_connection_error}", ErrorCode.DATABASE_CONNECTION_ERROR)
            return None
    
    def insert_data(self, data: dict) -> None:
        # Inserts the given data into the database.
        try:
            if self.db_conn is None:
                self.db_conn = self.connect_to_db()
            
            cursor = self.db_conn.cursor()

            insert_query = '''
            INSERT INTO weather_data (date, time, location, weather_status, temperature, wind_speed, humidity) 
            VALUES (%s, %s, %s, %s, %s, %s, %s);
            '''

            cursor.execute(insert_query, (
                data['date'],
                data['time'],
                data['location'],
                data['weather_status'],
                data['temperature'],
                data['wind_speed'],
                data['humidity']
            ))
            self.db_conn.commit()
            logging.info(" Data inserted into the database successfully.")
        except Exception as data_insertion_error:
            logging.error(f"Error inserting data into the database: {data_insertion_error}", ErrorCode.DATA_INSERTION_ERROR)


class JSONHandler:
    # Class that handles JSON operations.
    @contextmanager
    def open_file(self, file_path: str, mode: str) -> Any:
        # Opens the specified file in the specified mode.
        file = None
        try:
            file = open(file_path, mode)
            yield file
        finally:
            if file:
                file.close()

    def update_data(self, weather_data: dict) -> None:
        # Updates the JSON file with the given weather data.
        try:
            with self.open_file('weather_data.json', 'r') as file:
                existing_data = json.load(file)

            existing_data.append(weather_data)

            with self.open_file('weather_data.json', 'w') as file:
                json.dump(existing_data, file, indent=4)

        except Exception as json_update_error:
            logging.error(f"Error updating JSON data: {json_update_error}", ErrorCode.JSON_UPDATE_ERROR)


if __name__ == "__main__":
    api_key = WeatherDataFetcher.get_config('api_key')
    fetcher = WeatherDataFetcher(api_key)
    fetcher.fetch_weather_data("Magalang, PH")
