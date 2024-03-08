import configparser
import concurrent.futures
from datetime import datetime
from functools import lru_cache
import json
import logging
from typing import Union, Tuple, Any

from psycopg2 import OperationalError, DatabaseError, pool
from pyowm import OWM
import geocoder
from contextlib import contextmanager
from cachetools import TTLCache
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import backoff
import time
import threading
import queue
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
start_time = time.time()

class APIConfig:
    # Model for storing API related configuration data.
    def __init__(self, api_key: str, config_file: str):
        if not api_key or api_key.isspace():
            error_message = "API key cannot be empty or whitespace only."
            logging.error(error_message)
            raise ValueError(error_message)
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

class DatabasePool:
    # Class representing a database connection pool manager.
    _pool = None
    _pool_mutex = threading.Lock()
    _connection_queue = queue.Queue(maxsize=10)

    def get_pool():
        # Get the database connection pool. If the pool does not exist, creates a new one and returns it.
        if DatabasePool._pool is None:
            with DatabasePool._pool_mutex:
                if DatabasePool._pool is None:
                    config = ConfigParserWrapper('config.ini')
                    db_credentials = config.get_database_credentials()
                    DatabasePool._pool = pool.ThreadedConnectionPool(1, 10,
                                       user=db_credentials.user,
                                       password=db_credentials.password,
                                       host=db_credentials.host,
                                       database=db_credentials.database)
        return DatabasePool._pool

    def get_connection():
        conn = DatabasePool._connection_queue.get()
        if conn is None:
            conn = DatabasePool.get_pool().getconn()
        return conn

    def release_connection(conn):
        DatabasePool._connection_queue.put(conn)

    def close_all_connections():
        # Close all connections in the database connection pool if it exists.
        if DatabasePool._pool is not None:
            with DatabasePool._pool_mutex:
                if DatabasePool._pool is not None:
                    DatabasePool._pool.closeall()

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
            error_message = f"Error while reading config file: {config_parser_error}"
            logging.error(error_message)
            raise ValueError(error_message)

    def get_database_credentials(self) -> DatabaseCredentials:
        # Get the database credentials from the config file.
        try:
            host = self.get_value('Database', 'host')
            database = self.get_value('Database', 'database')
            user = self.get_value('Database', 'user')
            password = self.get_value('Database', 'password')
            return DatabaseCredentials(host, database, user, password)
        except ValueError as value_error:
            error_message = f"Value Error fetching database credentials: {value_error}"
            logging.error(error_message)
            raise RuntimeError(error_message)
        except configparser.NoSectionError as section_error:
            error_message = f"No Section Error fetching database credentials: {section_error}"
            logging.error(error_message)
            raise RuntimeError(error_message)
        except configparser.NoOptionError as option_error:
            error_message = f"No Option Error fetching database credentials: {option_error}"
            logging.error(error_message)
            raise RuntimeError(error_message)

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
        # Initializes the WeatherDataFetcher with the specified API configuration.
        self.weather_cache = TTLCache(maxsize=self.CACHE_SIZE, ttl=self.CACHE_TTL)
        if self.validate_api_key(api_config.api_key):
            self.api_key = api_config.api_key
        else:
            error_message = "Invalid API Key"
            logging.error(error_message)
            raise ValueError(error_message)

    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        # Validates if the given API key is valid.
        return bool(api_key and not api_key.isspace())

    @classmethod
    def get_config(cls, key: str) -> str:
        # Gets the configuration value from the config.ini file.
        try:
            config = ConfigParserWrapper('config.ini')
            return config.get_value('API', key)
        except ValueError as error:
            error_message = f"Configuration error: {error}"
            logging.error(error_message)
            raise RuntimeError(error_message)

    @lru_cache(maxsize=128)
    def get_coordinates(self, location: str) -> Union[Tuple[float, float], None]:
        try:
            # Remove special characters and non-alphanumeric characters from the location name.
            cleaned_location = re.sub(r'[^\w\s]', '', location)

            if cleaned_location.strip() == "":
                raise ValueError("Location cannot be empty or whitespace only.")

            coordinates = self.weather_cache.get(cleaned_location)
            if coordinates is not None:
                return coordinates

            geo_location = geocoder.osm(cleaned_location)
            if geo_location.latlng is None:
                return None

            # Normalize latitude and longitude values to 4 decimal places for precision.
            latitude, longitude = geo_location.latlng
            normalized_latitude = round(latitude, 4)
            normalized_longitude = round(longitude, 4)

            coordinates = (normalized_latitude, normalized_longitude)
            self.weather_cache[cleaned_location] = {'coordinates': coordinates}
            return coordinates
        except ValueError as value_error:
            error_message = f"Value Error getting coordinates for location: {cleaned_location}. {value_error}"
            logging.error(error_message)
            raise RuntimeError(error_message)
        except (GeocoderTimedOut, GeocoderServiceError) as geocoder_error:
            error_message = f"Error getting coordinates for location: {cleaned_location}. {geocoder_error}"
            logging.error(error_message)
            raise RuntimeError(error_message)
        except Exception as exception:
            error_message = f"Unknown error getting coordinates for location: {cleaned_location}. {exception}"
            logging.error(error_message)
            raise RuntimeError(error_message)

    @backoff.on_exception(backoff.expo, (Exception,), max_tries=3)
    def get_current_weather(self, latitude: float, longitude: float) -> Tuple[str, str, Any]:
        # Gets the current weather data for a given latitude and longitude.
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
            error_message = f"Error getting current weather: {exception}"
            logging.error(error_message)
            raise RuntimeError(error_message)

    def fetch_weather_data(self, location: str, lazy_load: bool = True) -> None:
        # Fetches weather data for a given location. Loads from cache if available.
        try:
            logging.info(f"Fetching weather data for location: {location}")

            # Normalize the location name to title case.
            normalized_location = location.title()
            # Normalize the location name to lowercase.
            normalized_location = self.normalize_text_to_lowercase(normalized_location)

            if normalized_location.strip() == "":
                raise ValueError("Location cannot be empty or whitespace only.")

            location_data = None
            if not lazy_load or normalized_location not in self.weather_cache:
                location_data = self.fetch_weather_data_from_api(normalized_location)

            if not location_data:
                raise ValueError(f"Error fetching weather data for location: {normalized_location}. Data is None.")

            # Check for missing or null weather_data before further processing
            if not location_data.get_additional_info() or not self.validate_weather_data(location_data.get_additional_info()):
                raise RuntimeError(f"Weather data missing or invalid for location: {normalized_location}.")

            if location_data and not lazy_load:
                self.weather_cache[normalized_location] = location_data.get_additional_info()
                logging.info(f"Weather data fetched from API and stored in cache for location: {normalized_location}")

            weather_data = location_data.get_additional_info()

            weather_info = WeatherInfo(weather_data['date'], weather_data['time'], weather_data['temperature'], weather_data['humidity'], weather_data['wind_speed'], weather_data['weather_status'])

            logging.info(f"As of: {weather_data['date']} | {weather_data['time']}")
            logging.info(f"Current weather at {location}: {weather_info}")

            with DatabaseHandler() as database_handler:
                database_handler.insert_data(weather_data)

            with JSONHandler() as json_handler:
                json_handler.update_json_data(weather_data)

        except ValueError as value_error:
            logging.error(value_error)
            raise RuntimeError(value_error)
        
        except (GeocoderTimedOut, GeocoderServiceError) as geocoder_error:
            error_message = f"Error getting coordinates for location: {normalized_location}. {geocoder_error}"
            logging.error(error_message)
            raise RuntimeError(error_message)

        except OperationalError as operation_error:
            logging.error(f"Operational error occurred: {operation_error}")
            raise RuntimeError(operation_error)

        except DatabaseError as db_error:
            logging.error(f"Database error occurred: {db_error}")
            raise RuntimeError(db_error)

        except Exception as exception:
            error_message = f"Error fetching weather data for location: {normalized_location}. {exception}"
            logging.error(error_message)
            raise RuntimeError(error_message)

        finally:
            logging.info(f"Finished processing location: {location}")

    def validate_weather_data(self, data: dict) -> bool:
        # Verify the retrieved weather data for consistency and validity.
        required_keys = ['date', 'time', 'temperature', 'humidity', 'wind_speed', 'weather_status']
        if all(key in data for key in required_keys):
            if all([isinstance(data[key], str) for key in ['date', 'time', 'weather_status']]):
                if all([isinstance(data[key], (int, float)) for key in ['temperature', 'humidity', 'wind_speed']]):
                    return True
        return False

    @backoff.on_exception(backoff.expo, (Exception,), max_tries=3)
    def fetch_weather_data_from_api(self, location: str) -> Union[LocationData, None]:
        try:
            coordinates = self.get_coordinates(location)
            if coordinates:
                latitude, longitude = coordinates
                current_date, current_time, weather, wind, humidity = self.get_current_weather(latitude, longitude)
                if weather:
                    temperature = float(weather.temperature('celsius')['temp'])

                    # Data normalization
                    temperature = self.normalize_temperature(temperature)
                    humidity = self.normalize_humidity(humidity)
                    wind_speed = self.normalize_wind_speed(wind['speed'])

                    weather_status = weather.status
                    # Normalize weather status to lowercase.
                    weather_status = self.normalize_text_to_lowercase(weather_status)

                    weather_data = {
                        'date': current_date,
                        'time': current_time,
                        'location': location,
                        'weather_status': weather_status,
                        'temperature': temperature,
                        'wind_speed': wind_speed,
                        'humidity': humidity,
                    }
                    # Create an instance of the WeatherInfo class with the fetched weather data
                    weather_info = WeatherInfo(weather_data['date'], weather_data['time'], weather_data['temperature'],
                                               weather_data['humidity'], weather_data['wind_speed'], weather_data['weather_status'])
                    return LocationData(location, latitude, longitude, weather_data)
                else:
                    logging.error(f"Unable to fetch weather data for {location}.")
                    raise RuntimeError(f"Unable to fetch weather data for {location}.")
            else:
                logging.error(f"Unable to fetch coordinates for {location}.")
                raise RuntimeError(f"Unable to fetch coordinates for {location}.")
        except Exception as exception:
            error_message = f"Error fetching weather data from API: {exception}"
            logging.error(error_message)
            raise RuntimeError(error_message)
    
    def normalize_text_to_lowercase(self, text: str) -> str:
        # Normalize text data to lowercase for uniformity.
        return text.lower()
        
    def normalize_temperature(self, temperature: float) -> float:
        # Normalize temperature to a common scale or range.
        return max(-50.0, min(temperature, 50.0))  # Normalize temperature within the range of -50°C to 50°C

    def normalize_humidity(self, humidity: int) -> int:
        # Normalize humidity to a common scale or range.
        return max(0, min(humidity, 100))  # Example: Ensure humidity percentage is within [0, 100]

    def normalize_wind_speed(self, wind_speed: float) -> float:
        # Normalize wind speed to a common unit or scale.
        return max(0.0, round((wind_speed * 0.44704), 2))  # Convert wind speed from mph to m/s with 2 decimal places

class DatabaseHandler:
    # A helper class to interact with a PostgreSQL database.
    def __enter__(self):
        try:
            self.conn = DatabasePool.get_pool().getconn()
            return self
        except (OperationalError, DatabaseError) as error:
            error_message = f"Error connecting to the database: {error}"
            logging.error(error_message)
            raise ValueError(error_message)

    def __exit__(self, exc_type, exc_val, exc_tb):
        DatabasePool.get_pool().putconn(self.conn)
        self.conn = None

    @staticmethod
    def create_cursor(conn):
        return conn.cursor()

    def insert_data(self, data: dict) -> None:
        try:
            with self.create_cursor(self.conn) as cursor:
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
                self.conn.commit()
                logging.info("Weather data collected was inserted into the database successfully.")
        except (OperationalError, DatabaseError) as error:
            error_message = f"Error inserting data into the database: {error}"
            logging.error(error_message)
            raise ValueError(error_message)

class JSONHandler:
    # Context manager class responsible for handling JSON file operations.
    def __init__(self):
        # Constructor for JSONHandler class.
        self.file = None

    @contextmanager
    # Open the JSON file in the given mode.
    def open_json_file(self, file_path: str, mode: str) -> Any:
        try:
            with open(file_path, mode) as file:
                yield file
        except (PermissionError, IOError, json.JSONDecodeError) as error:
            error_message = f"Error handling JSON file: {error}"
            logging.error(error_message)
            raise RuntimeError(error_message) from error
        except Exception as error:
            error_message = "Unexpected error occurred in JSON file operation."
            logging.error(f"{error_message}: {error}")
            raise RuntimeError(f"{error_message}: {error}")

    def __enter__(self):
        # Context manager enter method.
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Context manager exit method.
        if self.file:
            try:
                self.file.close()
            except Exception as exception:
                error_message = f"Error closing the JSON file: {exception}"
                logging.error(error_message)
            self.file = None

    def update_json_data(self, weather_data: dict) -> None:
        # Update the JSON file with the new weather data.
        try:
            with self.open_json_file('weather_data.json', 'r') as file:
                existing_data = json.load(file)

            existing_data.append(weather_data)

            with self.open_json_file('weather_data.json', 'w') as file:
                json.dump(existing_data, file, indent=4)

        except (PermissionError, IOError, json.JSONDecodeError) as error:
            error_message = f"Error updating JSON data: {error}"
            logging.error(error_message)
            raise RuntimeError(error_message)
        except Exception as error:
            error_message = f"Unexpected error occurred while updating JSON data: {error}"
            logging.error(error_message)
            raise RuntimeError(error_message)
        
if __name__ == "__main__":      
    try:
        config = ConfigParserWrapper('config.ini')
        api_key = config.get_value('API', 'api_key')
        api_config = APIConfig(api_key, 'config.ini')
        locations = sorted(["Angeles, PH", "Mabalacat City, PH", "Magalang, PH"])
        
        logging.info(f"Script execution started at {datetime.now().replace(microsecond=0)}.")

        fetcher = WeatherDataFetcher(api_config)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(fetcher.fetch_weather_data, location) for location in locations]

            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as error:
                    logging.error(f"An error occurred in thread execution: {error}")

        logging.info(f"Script execution completed at {datetime.now().replace(microsecond=0)}.")

        end_time = time.time()
        total_time = end_time - start_time
        logging.info(f"Total time taken is {total_time:.2f} seconds.")

    except ValueError as value_error:
        logging.error(f"Value Error occurred in main execution: {value_error}")
    except ImportError as import_error:
        logging.error(f"Import Error occurred in main execution: {import_error}")
    except (RuntimeError, KeyboardInterrupt) as runtime_error:
        logging.error(f"Runtime Error occurred in main execution: {runtime_error}")
    except Exception as exception:
        logging.exception("Unexpected Error occurred in main execution.", exc_info=True)
