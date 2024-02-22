import configparser
import concurrent.futures
from datetime import datetime
from functools import lru_cache
import json
import logging
from typing import Union, Tuple, Any

from psycopg2 import connect
from pyowm import OWM
import geocoder
from contextlib import contextmanager
from cachetools import TTLCache
from retrying import retry
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class APIConfig:
    # Model for storing API related configuration data.
    def __init__(self, api_key: str, config_file: str):
        self.api_key = api_key
        self.config_file = config_file


class ErrorResult:
    # Model for error results with error code, message, and details.
    def __init__(self, error_code: int, error_message: str, error_details=None):
        self.error_code = error_code
        self.error_message = error_message
        self.error_details = error_details if error_details else {}

    def __str__(self):
        return f"Error Code: {self.error_code}. Error Message: {self.error_message}, Error Details: {self.error_details}"


class ErrorCode:
    # Define the error results as class attributes.
    INVALID_API_KEY = ErrorResult(1, "Invalid API Key")
    CONFIG_FILE_READ_ERROR = ErrorResult(2, "Configuration File Read Error")
    COORDINATES_RETRIEVAL_ERROR = ErrorResult(3, "Coordinates Retrieval Error")
    CURRENT_WEATHER_RETRIEVAL_ERROR = ErrorResult(4, "Current Weather Retrieval Error")
    WEATHER_DATA_FETCH_ERROR = ErrorResult(5, "Weather Data Fetch Error")
    DATABASE_CONNECTION_ERROR = ErrorResult(6, "Database Connection Error")
    DATA_INSERTION_ERROR = ErrorResult(7, "Data Insertion Error")
    JSON_UPDATE_ERROR = ErrorResult(8, "JSON Update Error")
    FILE_NOT_FOUND_ERROR = ErrorResult(9, "File Not Found Error")


class LocationData:
    # Data class for storing location information.
    def __init__(self, location_name: str, latitude: float, longitude: float, additional_info: dict):
        self.location_name = location_name
        self.latitude = latitude
        self.longitude = longitude
        self.additional_info = additional_info

    def get_location_name(self):
        return self.location_name

    def get_latitude(self):
        return self.latitude

    def get_longitude(self):
        return self.longitude

    def get_additional_info(self):
        return self.additional_info

    def __str__(self):
        return f"Location Name: {self.location_name}, Latitude: {self.latitude}, Longitude: {self.longitude}, Additional Info: {self.additional_info}"


class DatabaseCredentials:
    # Model for database credentials.
    def __init__(self, host: str, database: str, user: str, password: str):
        self.host = host
        self.database = database
        self.user = user
        self.password = password

    def __str__(self):
        return f"Host: {self.host}, Database: {self.database}, User: {self.user}"
    

class ConfigParserWrapper:
    # Wrapper class for configparser to read config values.
    def __init__(self, config_file: str) -> None:
        self.config_file = config_file
        self.config_parser = configparser.ConfigParser()
        self.config_parser.read(config_file)

    def get_value(self, section: str, key: str) -> str:
        # Get the value from the config file for the given section and key.
        try:
            return self.config_parser.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError) as config_parser_error:
            raise ValueError(ErrorCode.CONFIG_FILE_READ_ERROR.error_code, ErrorCode.CONFIG_FILE_READ_ERROR.error_message) from config_parser_error

    def get_database_credentials(self) -> DatabaseCredentials:
        # Get the database credentials from the config file.
        try:
            host = self.get_value('Database', 'host')
            database = self.get_value('Database', 'database')
            user = self.get_value('Database', 'user')
            password = self.get_value('Database', 'password')
            return DatabaseCredentials(host, database, user, password)
        except ValueError as error:
            logging.exception(f"Error reading database credentials: {error}")
            raise RuntimeError(ErrorCode.DATABASE_CONNECTION_ERROR.error_code, ErrorCode.DATABASE_CONNECTION_ERROR.error_message) from error


class WeatherInfo:
    # Model for storing weather information for a location.
    def __init__(self, date: str, time: str, temperature: float, humidity: int, wind_speed: float, weather_status: str):
        self.date = date
        self.time = time
        self.temperature = temperature
        self.humidity = humidity
        self.wind_speed = wind_speed
        self.weather_status = weather_status

    def __str__(self):
        return f"Date: {self.date}, Time: {self.time}, Temperature: {self.temperature}°C, Humidity: {self.humidity}%, Wind Speed: {self.wind_speed} m/s, Weather Status: {self.weather_status}"


class WeatherDataFetcher:
    # Class responsible for fetching weather data.
    CACHE_SIZE = 128
    CACHE_TTL = 3600
    
    def __init__(self, api_config: APIConfig) -> None:
        self.weather_cache = TTLCache(maxsize=self.CACHE_SIZE, ttl=self.CACHE_TTL)
        if self.validate_api_key(api_config.api_key):
            self.api_key = api_config.api_key
        else:
            raise ValueError(ErrorCode.INVALID_API_KEY.error_code, ErrorCode.INVALID_API_KEY.error_message)

    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        # Validate if the given API key is valid.
        return bool(api_key and not api_key.isspace())

    @classmethod
    def get_config(cls, key: str) -> str:
        # Get the configuration value from the config.ini file.
        try:
            config = ConfigParserWrapper('config.ini')
            return config.get_value('API', key)
        except ValueError as error:
            logging.exception(f"Configuration error: {error}")
            raise RuntimeError(ErrorCode.CONFIG_FILE_READ_ERROR.error_code, ErrorCode.CONFIG_FILE_READ_ERROR.error_message) from error

    @lru_cache(maxsize=128)
    def get_coordinates(self, location: str) -> Union[Tuple[float, float], None]:
        # Get the coordinates (latitude, longitude) for a given location.
        coordinates = self.weather_cache.get(location)
        if coordinates is not None:
            return coordinates

        try:
            geo_location = geocoder.osm(location)
            coordinates = geo_location.latlng if geo_location.latlng else None
            if coordinates:
                self.weather_cache[location] = {'coordinates': coordinates}
            return coordinates
        except (GeocoderTimedOut, GeocoderServiceError) as geocoder_error:
            logging.exception(f"Error getting coordinates for location: {location}. Error message: {geocoder_error}")
            raise RuntimeError(ErrorCode.COORDINATES_RETRIEVAL_ERROR.error_code, ErrorCode.COORDINATES_RETRIEVAL_ERROR.error_message) from geocoder_error
        except Exception as exception:
            logging.exception(f"Unknown error getting coordinates for location: {location}. Error message: {exception}")
            raise RuntimeError(ErrorCode.COORDINATES_RETRIEVAL_ERROR.error_code, ErrorCode.COORDINATES_RETRIEVAL_ERROR.error_message) from exception

    def get_current_weather(self, latitude: float, longitude: float) -> Tuple[str, str, Any]:
        # Get the current weather data for a given latitude and longitude.
        try:
            owm = OWM(self.api_key)
            weather_manager = owm.weather_manager()
            observation = weather_manager.weather_at_coords(latitude, longitude)
            current_date = datetime.now().strftime('%Y-%m-%d')
            current_time = datetime.now().strftime('%H:%M:%S')
            weather = observation.weather
            wind = weather.wind()
            humidity = weather.humidity
            return current_date, current_time, weather, wind, humidity
        except Exception as exception:
            logging.exception(f"Error getting current weather: {exception}")
            raise RuntimeError(ErrorCode.CURRENT_WEATHER_RETRIEVAL_ERROR.error_code, ErrorCode.CURRENT_WEATHER_RETRIEVAL_ERROR.error_message) from exception

    def fetch_weather_data(self, location: str) -> None:
        # Fetch weather data for a given location and perform necessary operations like inserting into database and updating JSON file.
        try:
            logging.info(f"Fetching weather data for location: {location}")
            if location in self.weather_cache:
                weather_data = self.weather_cache[location]
            else:
                location_data = self.fetch_weather_data_from_api(location)
                if location_data is not None:
                    self.weather_cache[location] = location_data.get_additional_info()
                    
            if location_data is None:
                logging.exception("Error fetching weather data: Weather data is None.")
                raise RuntimeError(ErrorCode.WEATHER_DATA_FETCH_ERROR.error_code, ErrorCode.WEATHER_DATA_FETCH_ERROR.error_message)

            weather_data = location_data.get_additional_info()
            with DatabaseHandler() as database_handler:
                database_handler.insert_data(weather_data)

            with JSONHandler() as json_handler:
                json_handler.update_json_data(weather_data)

            weather_info = WeatherInfo(weather_data['date'], weather_data['time'], weather_data['temperature'], weather_data['humidity'], weather_data['wind_speed'], weather_data['weather_status'])

            print(f"As of: {weather_data['date']} | {weather_data['time']}")
            print(f"Current weather at {location}: {weather_info}")

        except Exception as exception:
            logging.exception(f"Error fetching weather data: {exception}", exc_info=True)
            raise RuntimeError(ErrorCode.WEATHER_DATA_FETCH_ERROR.error_code, ErrorCode.WEATHER_DATA_FETCH_ERROR.error_message) from exception

    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def fetch_weather_data_from_api(self, location: str) -> Union[LocationData, None]:
        # Fetch weather data for a given location from the API.
        try:
            coordinates = self.get_coordinates(location)
            if coordinates:
                latitude, longitude = coordinates
                current_date, current_time, weather, wind, humidity = self.get_current_weather(latitude, longitude)
                if weather:
                    temperature = float(weather.temperature('celsius')['temp'])  # Convert temperature to float
                    weather_status = weather.status

                    # Create a dictionary with weather data
                    weather_data = {
                        'date': current_date,
                        'time': current_time,
                        'location': location,
                        'weather_status': weather_status,
                        'temperature': temperature,
                        'wind_speed': wind['speed'],
                        'humidity': humidity,
                    }

                    # Create an instance of the WeatherInfo class with the fetched weather data
                    weather_info = WeatherInfo(weather_data['date'], weather_data['time'], weather_data['temperature'], weather_data['humidity'], weather_data['wind_speed'], weather_data['weather_status'])

                    return LocationData(location, latitude, longitude, weather_data)
                else:
                    logging.exception(f"Unable to fetch weather data for {location}.")
                    raise RuntimeError(ErrorCode.WEATHER_DATA_FETCH_ERROR.error_code, ErrorCode.WEATHER_DATA_FETCH_ERROR.error_message)
            else:
                logging.exception(f"Unable to fetch coordinates for {location}.")
                raise RuntimeError(ErrorCode.COORDINATES_RETRIEVAL_ERROR.error_code, ErrorCode.COORDINATES_RETRIEVAL_ERROR.error_message)
        except Exception as exception:
            logging.exception(f"Error fetching weather data from API: {exception}")
            raise RuntimeError(ErrorCode.WEATHER_DATA_FETCH_ERROR.error_code, ErrorCode.WEATHER_DATA_FETCH_ERROR.error_message) from exception


class DatabaseHandler:
    # Context manager class responsible for handling database connections and operations.
    def __init__(self) -> None:
        # Constructor for DatabaseHandler class.
        self.database_connection = None

    def connect_to_database(self) -> Any:
        # Connect to the database using the credentials from the config.ini file.
        try:
            config = configparser.ConfigParser()
            config.read('config.ini')
            connection = None
            try:
                connection = connect(
                    host=config.get('Database', 'host'),
                    database=config.get('Database', 'database'),
                    user=config.get('Database', 'user'),
                    password=config.get('Database', 'password')
                )
                return connection
            except Exception as exception:
                logging.exception(f"Error connecting to the database: {exception}")
                raise RuntimeError(ErrorCode.DATABASE_CONNECTION_ERROR.error_code, ErrorCode.DATABASE_CONNECTION_ERROR.error_message) from exception
        except (configparser.NoSectionError, configparser.NoOptionError, FileNotFoundError) as error:
            logging.exception(f"Error reading database configuration: {error}")
            raise ImportError(ErrorCode.CONFIG_FILE_READ_ERROR.error_code, ErrorCode.CONFIG_FILE_READ_ERROR.error_message) from error

    def __enter__(self) -> 'DatabaseHandler':
        # Context manager enter method.
        try:
            self.database_connection = self.connect_to_database()
            return self
        except RuntimeError as error:
            logging.exception(f"Error connecting to database: {ErrorCode.DATABASE_CONNECTION_ERROR}")
            raise error
        except Exception as exception:
            logging.exception(f"Error connecting to the database: {exception}")
            raise RuntimeError(ErrorCode.DATABASE_CONNECTION_ERROR.error_code, ErrorCode.DATABASE_CONNECTION_ERROR.error_message) from exception

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        # Context manager exit method.
        if self.database_connection:
            try:
                if exc_type is not None:
                    self.database_connection.rollback()
            finally:
                try:
                    self.database_connection.close()
                except Exception as exception:
                    logging.exception(f"Error closing the database connection: {exception}", exc_info=True)
                self.database_connection = None

    @contextmanager
    def create_cursor(self):
        try:
            cursor = self.database_connection.cursor()
            yield cursor
        finally:
            if cursor:
                cursor.close()

    def insert_data(self, data: dict) -> None:
        try:
            with self.create_cursor() as cursor:
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
                self.database_connection.commit()
                logging.info("Data inserted into the database successfully.")
        except Exception as exception:
            logging.exception(f"Error inserting data into the database: {exception}", exc_info=True)
            raise RuntimeError(ErrorCode.DATA_INSERTION_ERROR.error_code, ErrorCode.DATA_INSERTION_ERROR.error_message) from exception


class JSONHandler:
    # Context manager class responsible for handling JSON file operations.
    def __init__(self):
        # Constructor for JSONHandler class.
        self.file = None

    @contextmanager
    def open_json_file(self, file_path: str, mode: str) -> Any:
        # Open the JSON file in the given mode.
        try:
            self.file = open(file_path, mode)
            yield self.file
        except (PermissionError, IOError) as file_error:
            logging.exception(f"Error occurred while opening JSON file: {file_error}")
            raise RuntimeError(ErrorCode.FILE_NOT_FOUND_ERROR.error_code, ErrorCode.FILE_NOT_FOUND_ERROR.error_message) from file_error
        except json.JSONDecodeError as json_error:
            logging.exception(f"Error decoding JSON file: {json_error}")
            raise RuntimeError(ErrorCode.JSON_UPDATE_ERROR.error_code, ErrorCode.JSON_UPDATE_ERROR.error_message) from json_error
        except Exception as exception:
            logging.exception("An unexpected error occurred:", exc_info=True)
            raise RuntimeError("Unknown error occurred") from exception
        finally:
            if self.file:
                self.file.close()
                self.file = None

    def __enter__(self):
        # Context manager enter method.
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Context manager exit method.
        if self.file:
            try:
                self.file.close()
            except Exception as exception:
                logging.exception(f"Error closing the JSON file: {exception}", exc_info=True)
            self.file = None

    def update_json_data(self, weather_data: dict) -> None:
        # Update the JSON file with the new weather data.
        try:
            with self.open_json_file('weather_data.json', 'r') as file:
                existing_data = json.load(file)

            existing_data.append(weather_data)

            with self.open_json_file('weather_data.json', 'w') as file:
                json.dump(existing_data, file, indent=4)

        except (PermissionError, IOError) as file_error:
            logging.exception(f"File error occurred while updating JSON data: {file_error}")
            raise RuntimeError(ErrorCode.JSON_UPDATE_ERROR.error_code, ErrorCode.JSON_UPDATE_ERROR.error_message) from file_error
        except json.JSONDecodeError as json_error:
            logging.exception(f"JSON decoding error while updating JSON data: {json_error}")
            raise RuntimeError(ErrorCode.JSON_UPDATE_ERROR.error_code, ErrorCode.JSON_UPDATE_ERROR.error_message) from json_error
        except Exception as exception:
            logging.exception(f"Error updating JSON data: {exception}", exc_info=True)
            raise RuntimeError("Unknown error occurred", ErrorCode.JSON_UPDATE_ERROR.error_code, ErrorCode.JSON_UPDATE_ERROR.error_message) from exception


if __name__ == "__main__":
    api_key = WeatherDataFetcher.get_config('api_key')
    api_config = APIConfig(api_key, 'config.ini')
    locations = sorted(["Angeles, PH", "Mabalacat City, PH", "Magalang, PH"])

    fetcher = WeatherDataFetcher(api_config)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        try:
            executor.map(lambda location: fetcher.fetch_weather_data(location), locations)
        except RuntimeError as runtime_error:
            logging.exception(f"Runtime Error: {runtime_error}")
        except Exception as exception:
            logging.exception("Error executing fetch_weather_data.", exc_info=True)
