import configparser
from datetime import datetime
from functools import lru_cache, partial
import json
import logging
from typing import Union, Tuple, Any

from dask import delayed, compute
from psycopg2 import OperationalError, DatabaseError, pool, sql
from pyowm import OWM
import geocoder
from contextlib import contextmanager
from cachetools import TTLCache, LRUCache
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from tenacity import retry, stop_after_attempt, wait_exponential
from queue import LifoQueue
import time
import threading
import re
import traceback
import atexit
import psutil

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler('app_run.log'),
                        logging.StreamHandler()
                    ])

start_time = time.time()

weather_data_collection_completed = False

class APIConfig:
    # Model for storing API related configuration data.
    def __init__(self, api_key: str, config_file: str):
        # Initialize APIConfig with API key and configuration file.
        if not api_key or api_key.isspace():
            error_message = "API key cannot be empty or whitespace only."
            logging.error(error_message)
            raise ValueError(error_message)
        
        self.api_key = api_key
        self.config_file = config_file

class ErrorResult:
    # Model for error results with error code, message, and details.
    def __init__(self, error_code: int, error_message: str, error_details=None):
        # Initialize ErrorResult object with error code, error message, and optional error details.
        self.error_code = error_code
        self.error_message = error_message
        self.error_details = error_details if error_details else {}

    def __str__(self):
        # Override the string representation of the object.
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
        # Initialize LocationData object with provided data.
        self.location_name = location_name
        self.latitude = latitude
        self.longitude = longitude
        self.additional_info = additional_info

    def get_location_name(self):
        # Return the name of the location.
        return self.location_name

    def get_latitude(self):
        # Return the latitude coordinate of the location.
        return self.latitude

    def get_longitude(self):
        # Return the longitude coordinate of the location.
        return self.longitude

    def get_additional_info(self):
        # Return the additional information about the location.
        return self.additional_info

    def __str__(self):
        # Return a formatted string representation of the LocationData object.
        return f"Location Name: {self.location_name}, Latitude: {self.latitude}, Longitude: {self.longitude}, Additional Info: {self.additional_info}"
    
    def validate_data(self):
        # Check if required fields are not empty and have the correct type.
        if not isinstance(self.location_name, str) or not isinstance(self.latitude, (int, float)) or not isinstance(self.longitude, (int, float)) or not isinstance(self.additional_info, dict):
            raise ValueError("Invalid data in LocationData object. Please provide valid data for insertion.")

class DatabasePool:
    # Class representing a database connection pool manager.
    _pool = None
    _pool_mutex = threading.Lock()
    _connection_queue = LifoQueue(maxsize=10)  # Updated to LIFO queue.
    _active_connections = []

    @staticmethod
    def get_pool():
        # Get the database connection pool. If the pool does not exist, creates a new one and returns it.
        if DatabasePool._pool is None:
            with DatabasePool._pool_mutex:
                if DatabasePool._pool is None:
                    config = ConfigParserWrapper('config.ini')
                    db_credentials = config.get_database_credentials()
                    # Adjust the minconn and maxconn values based on available resources and usage patterns.
                    DatabasePool._pool = pool.ThreadedConnectionPool(minconn=1, maxconn=20,  # Adjust based on requirements.
                                       user=db_credentials.user,
                                       password=db_credentials.password,
                                       host=db_credentials.host,
                                       database=db_credentials.database)
        return DatabasePool._pool


    @staticmethod
    def get_connection():
        # Get a database connection from the connection pool.
        conn = None
        
        if not DatabasePool._connection_queue.empty():  # Check if there's an available connection in the queue.
            conn = DatabasePool._connection_queue.get()
        else:
            conn = DatabasePool.get_pool().getconn()
            DatabasePool._active_connections.append(conn)  # Add to the active connections list.
        
        return conn
    
    @staticmethod
    def release_connection(conn):
        # Release a connection back to the connection pool.
        DatabasePool._connection_queue.put(conn)

    @staticmethod
    def close_all_connections():
        # Close all connections in the database connection pool if it exists.
        for conn in DatabasePool._active_connections:
            DatabasePool._pool.putconn(conn)
        DatabasePool._active_connections.clear()

    def cleanup():
        # Perform cleanup tasks by closing all connections.
        DatabasePool.close_all_connections()

class DatabaseCredentials:
    # Model for database credentials.
    def __init__(self, host: str, database: str, user: str, password: str):
        # Initialize the DatabaseCredentials object with host, database, user, and password.
        self.host = host
        self.database = database
        self.user = user
        self.password = password

    def __str__(self):
        # Returns a string representation of the database credentials.
        return f"Host: {self.host}, Database: {self.database}, User: {self.user}"

class ConfigParserWrapper:
    # Wrapper class for configparser to read config values.
    def __init__(self, config_file: str) -> None:
        # Initialize the ConfigParserWrapper object with the config file.
        self.config_file = config_file
        self.config_parser = configparser.ConfigParser()
        self.config_parser.read(config_file)

    def get_value(self, section: str, key: str) -> str:
        # Gets the value from the config file for the given section and key.
        try:
            return self.config_parser.get(section, key)
        
        except (configparser.NoSectionError, configparser.NoOptionError) as config_parser_error:
            error_message = f"Error while reading config file: {config_parser_error}"
            logging.error(error_message)
            raise ValueError(error_message)

    def get_database_credentials(self) -> DatabaseCredentials:
        # Gets the database credentials from the config file.
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
        # Initialize a WeatherInfo object.
        self.date = date
        self.time = time
        self.temperature = temperature
        self.humidity = humidity
        self.wind_speed = wind_speed
        self.weather_status = weather_status

    def __str__(self):
        # Get a string representation of the WeatherInfo object.
        return f"Date: {self.date}, Time: {self.time}, Temperature: {self.temperature}°C, Humidity: {self.humidity}%, Wind Speed: {self.wind_speed} m/s, Weather Status: {self.weather_status}"

class WeatherDataFetcher:
    # Class responsible for fetching weather data.
    CACHE_SIZE = 256  # Adjust based on memory availability and access patterns.
    CACHE_TTL = 3600  # Adjust the TTL in seconds based on data freshness requirements.
    
    def __init__(self, api_config: APIConfig) -> None:
        # Initializes the WeatherDataFetcher with the specified API configuration.
        self.weather_cache = TTLCache(maxsize=self.CACHE_SIZE, ttl=self.CACHE_TTL)
        self.lru_cache = LRUCache(maxsize=128)  # Adding an LRU cache for faster access
        self.cache_lock = threading.Lock()
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_accesses = 0
        self.cache_hit_rate_threshold = 0.7  # Adjust the threshold appropriately.
        
        if self.validate_api_key(api_config.api_key):
            self.api_key = api_config.api_key
        else:
            error_message = "Invalid API Key"
            logging.error(error_message)
            raise ValueError(error_message)

    def calculate_cache_hit_rate(self) -> float:
        # Calculate the cache hit rate by dividing the number of cache hits by the total number of accesses.
        if self.total_accesses == 0:
            return 0
        return self.cache_hits / self.total_accesses
    
    def adjust_cache_size(self):
            # Adjust the size of the caches based on the cache hit rate.
            hit_rate = self.calculate_cache_hit_rate()
            if hit_rate > self.cache_hit_rate_threshold:
                # Increase cache size if hit rate is high
                self.weather_cache = TTLCache(maxsize=min(512, self.weather_cache.maxsize * 2), ttl=3600)
                self.lru_cache = LRUCache(maxsize=min(256, self.lru_cache.maxsize * 2))
            else:
                # Decrease cache size if hit rate is low
                self.weather_cache = TTLCache(maxsize=max(128, self.weather_cache.maxsize // 2), ttl=3600)
                self.lru_cache = LRUCache(maxsize=max(64, self.lru_cache.maxsize // 2))

    def get_weather_data(self, location: str) -> dict:
        # Retrieve weather data for a given location from the cache or API.
        self.total_accesses += 1
        with self.cache_lock:
            if location in self.weather_cache:
                self.cache_hits += 1
                return self.weather_cache[location]
            elif location in self.lru_cache:
                self.cache_hits += 1
                return self.lru_cache[location]
            else:
                self.cache_misses += 1
                data = self.fetch_weather_data_from_api(location)
                self.weather_cache[location] = data
                self.lru_cache[location] = data
                return data

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

    @partial(lru_cache(maxsize=128))
    def get_coordinates(self, location: str) -> Union[Tuple[float, float], None]:
        # Fetches the latitude and longitude coordinates for a given location.
        try:
            # Remove special characters and non-alphanumeric characters from the location name.
            cleaned_location = re.sub(r'[^\w\s]', '', location)

            if cleaned_location.strip() == "":
                raise ValueError("Location cannot be empty or whitespace only.")

            with self.cache_lock:
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

            with self.cache_lock:
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

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
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
        # Fetches weather data for a given location and stores it in the cache.
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
            else:
                with self.cache_lock:
                    location_data = self.weather_cache.get(normalized_location)

            if not location_data:
                raise ValueError(f"Error fetching weather data for location: {normalized_location}. Data is None.")

            # Check for missing or null weather_data before further processing.
            if not location_data.get_additional_info() or not self.validate_weather_data(location_data.get_additional_info()):
                raise RuntimeError(f"Weather data missing or invalid for location: {normalized_location}.")

            if location_data and not lazy_load:
                # Protect access to the shared weather_cache with a lock.
                with self.cache_lock:
                    self.weather_cache[normalized_location] = location_data.get_additional_info()
                    logging.info(f"Weather data fetched from API and stored in cache for location: {normalized_location}")

            weather_data = location_data.get_additional_info()
            weather_info = WeatherInfo(weather_data['date'], weather_data['time'], weather_data['temperature'], weather_data['humidity'], weather_data['wind_speed'], weather_data['weather_status'])

            try:
            # Validate the data before insertion.
                location_data.validate_data()

            except ValueError as value_error:
                logging.error(value_error)
                raise RuntimeError(value_error)

            logging.info(f"As of: {weather_data['date']} | {weather_data['time']}")
            logging.info(f"Current weather at {location}: {weather_info}")

            with DatabaseHandler() as database_handler:
                database_handler.insert_data(weather_data)

            with JSONHandler() as json_handler:
                json_handler.update_json_data(weather_data)

        except ValueError as value_error:
            logging.error(value_error)
            raise RuntimeError(value_error, f"Error fetching weather data for location: {normalized_location}")
        
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
            logging.exception(error_message)
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

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def fetch_weather_data_from_api(self, location: str) -> Union[LocationData, None]:
        # Fetches weather data for a location from the API.
        try:
            coordinates = self.get_coordinates(location)
            if coordinates:
                latitude, longitude = coordinates

                with self.cache_lock:
                    current_date, current_time, weather, wind, humidity = self.get_current_weather(latitude, longitude)
                    if weather:
                        temperature = float(weather.temperature('celsius')['temp'])

                        # Data normalization.
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
                        # Create an instance of the WeatherInfo class with the fetched weather data.
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
        return max(-50.0, min(temperature, 50.0))  # Normalize temperature within the range of -50°C to 50°C.

    def normalize_humidity(self, humidity: int) -> int:
        # Normalize humidity to a common scale or range.
        return max(0, min(humidity, 100))  # Example: Ensure humidity percentage is within [0, 100].

    def normalize_wind_speed(self, wind_speed: float) -> float:
        # Normalize wind speed to a common unit or scale.
        return max(0.0, round((wind_speed * 0.44704), 2))  # Convert wind speed from mph to m/s with 2 decimal places.

class SchemaManager:
    # A class to manage the schema of the weather data table.
    @staticmethod
    def create_weather_data_table():
        # Create the initial schema for the weather data table.
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS weather_data (
            id SERIAL PRIMARY KEY,
            date DATE,
            time TIME,
            location VARCHAR(255),
            weather_status VARCHAR(50),
            temperature NUMERIC,
            wind_speed NUMERIC,
            humidity INTEGER,
            climate_data JSONB
        );
        '''
        try:
            with DatabaseHandler() as database_handler:
                database_handler.create_cursor(database_handler.conn).execute(create_table_query)
                database_handler.conn.commit()
                logging.info("Created weather_data table successfully.")
        except (OperationalError, DatabaseError) as error:
            error_message = f"Error creating weather_data table: {error}"
            logging.error(error_message)
            raise ValueError(error_message)

    @staticmethod
    def alter_weather_data_table():
        # Alter the schema of the weather data table as needed.
        alter_table_query = '''
        ALTER TABLE weather_data ADD COLUMN IF NOT EXISTS temperature_upper_limit NUMERIC;
        '''
        try:
            with DatabaseHandler() as database_handler:
                database_handler.create_cursor(database_handler.conn).execute(alter_table_query)
                database_handler.conn.commit()
                logging.info("Altered weather_data table successfully.")
        except (OperationalError, DatabaseError) as error:
            error_message = f"Error altering weather_data table: {error}"
            logging.error(error_message)
            raise ValueError(error_message)

    @staticmethod
    def optimize_query_performance():
        # Perform optimizations like creating indexes and analyzing table data for the weather data table.
        with DatabaseHandler() as database_handler:
            database_handler.create_indexes()
            logging.info("Database query performance optimizations completed.")

class DatabaseHandler:
    # A helper class to interact with a PostgreSQL database.
    def __enter__(self):
        # Get a connection from the database pool when entering the context.
        try:
            self.conn = DatabasePool.get_pool().getconn()
            return self
        
        except (OperationalError, DatabaseError) as error:
            error_message = f"Error connecting to the database: {error}"
            logging.error(error_message)
            raise ValueError(error_message)

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Put the database connection back to the pool when exiting the context.
        DatabasePool.get_pool().putconn(self.conn)
        self.conn = None
        
        # Close the database connection if it's not None.
        if self.conn:
            try:
                self.conn.close()
                logging.info("Closing database connection.")
            except Exception as e:
                logging.error(f"Error closing database connection: {e}")
            self.conn = None

    @staticmethod
    def create_cursor(conn):
        # Create and return a cursor object for database interaction.
        return conn.cursor()
    
    def create_indexes(self):
        # Create necessary indexes on the weather_data table for improved query performance.
        try:
            with self.create_cursor(self.conn) as cursor:
                indexes = [
                    'idx_date',
                    'idx_time',
                    'idx_location',
                    'idx_temperature',
                    'idx_weather_status',
                    'idx_climate_data'
                ]
                
                for index_name in indexes:
                    # Check if the index already exists.
                    cursor.execute(sql.SQL('SELECT count(*) FROM pg_indexes WHERE indexname = %s;'), (index_name,))
                    count = cursor.fetchone()[0]

                    if count == 0:
                        if index_name.startswith('idx_'):
                            column = index_name[4:]  # Get the column name for indexing.
                            cursor.execute(sql.SQL('CREATE INDEX {} ON weather_data ({});').format(sql.Identifier(index_name), sql.Identifier(column.lower())))
                
                self.conn.commit()

                logging.info("Indexes created for improved query performance.")
        except (OperationalError, DatabaseError) as error:
            error_message = f"Error creating indexes: {error}"
            logging.error(error_message)
            raise ValueError(error_message)

    def insert_data(self, data: dict) -> None:
        try:
            # Missing data handling and normalization.
            cleaned_data = {k: data[k].strip() if isinstance(data[k], str) else data[k] for k in data}
            
            # Check for missing or null data.
            required_keys = ['date', 'time', 'location', 'weather_status', 'temperature', 'wind_speed', 'humidity']
            if any(key not in cleaned_data for key in required_keys):
                raise ValueError("One or more weather data fields are missing.")

            with self.create_cursor(self.conn) as cursor:
                query = '''
                INSERT INTO weather_data (date, time, location, weather_status, temperature, wind_speed, humidity, climate_data) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                '''
                values = (
                    cleaned_data['date'],
                    cleaned_data['time'],
                    cleaned_data['location'],
                    cleaned_data['weather_status'],
                    cleaned_data['temperature'],
                    cleaned_data['wind_speed'],
                    cleaned_data['humidity'],
                    json.dumps(cleaned_data)  # Convert dictionary to JSON string for insertion into the jsonb column.
                )
                cursor.execute(query, values)
                self.conn.commit()

                logging.info("Weather data inserted into the database successfully.")
            
        except OperationalError as operation_error:
            logging.error(f"Operational error occurred during insertion: {operation_error}")
            raise ValueError(operation_error)

        except DatabaseError as db_error:
            logging.error(f"Database error occurred: {db_error}")
            raise ValueError(db_error)

        except Exception as exception:
            error_message = f"Error inserting data into the database: {exception}"
            logging.error(error_message)
            raise ValueError(error_message)
    
    def create_initial_schema(self):
        # Create the initial schema for the application.
        SchemaManager.create_weather_data_table()
        
class JSONHandler:    
    # Context manager class responsible for handling JSON file operations.
    def __init__(self) -> None:
        # Constructor for JSONHandler class.
        self.lock = threading.Lock()
        self.file = None

    @contextmanager
    def lock_acquire(self):
        # Acquires the lock.
        try:
            self.lock.acquire()
            yield

        finally:
            self.lock.release()

    @contextmanager
    def open_json_file(self, file_path: str, mode: str) -> Any:
        # Open the JSON file in the given mode.
        try:
            with self.lock_acquire():
                with open(file_path, mode) as file:
                    self.file = file
                    if mode == 'r':
                        logging.info(f"Reading JSON file: {file_path}")
                    elif mode == 'w':
                        logging.info(f"Opening JSON file: {file_path}")
                    yield self.file

        except (PermissionError, IOError) as file_error:
            error_message = f"Error handling JSON file: {file_error}"
            logging.error(error_message)
            raise RuntimeError(error_message)

        except json.JSONDecodeError as decode_error:
            error_message = f"Error decoding JSON file: {decode_error}"
            logging.error(error_message)
            raise RuntimeError(error_message)

        except Exception as exception:
            error_message = "Unexpected error occurred in JSON file operation."
            logging.error(f"{error_message}: {exception}")
            raise RuntimeError(error_message)

    def __enter__(self):
        # Context manager enter method.
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Context manager exit method.
        if self.file:
            try:
                self.file.close()
                logging.info("Closing JSON file.")

            except Exception as exception:
                error_message = f"Error closing the JSON file: {exception}"
                logging.error(error_message)
            self.file = None

    def update_json_data(self, weather_data: dict) -> None:
        # Update JSON data with the provided weather data dictionary after validating the data.
        try:
            # Cleanse data before updating JSON file.
            cleaned_data = {k: str(weather_data[k]).strip() if isinstance(weather_data[k], str) else weather_data[k] for k in weather_data}

            # Validate the data before writing to the JSON file.
            if 'date' not in cleaned_data or 'time' not in cleaned_data or 'location' not in cleaned_data or 'weather_status' not in cleaned_data \
                or 'temperature' not in cleaned_data or 'wind_speed' not in cleaned_data or 'humidity' not in cleaned_data:
                raise ValueError("One or more required fields missing in the weather data.")

            for key in ['date', 'time', 'location', 'weather_status']:
                if not cleaned_data[key]:
                    raise ValueError(f"Invalid value for field '{key}' in weather data.")

            for key in ['temperature', 'wind_speed', 'humidity']:
                if not isinstance(cleaned_data[key], (int, float)) or not 0 <= cleaned_data[key] <= 100:
                    raise ValueError(f"Invalid value for field '{key}' in weather data. Must be a number between 0 and 100.")

            with self.open_json_file('weather_data.json', 'r') as file:
                existing_data = json.load(file)

            cleaned_data['version'] = 2  # Update the version number.

            # Update with normalized, cleaned data.
            existing_data.append(cleaned_data)

            with self.open_json_file('weather_data.json', 'w') as file:
                json.dump(existing_data, file, indent=4)
                logging.info("Updated JSON data with weather data.")

        except ValueError as value_error:
            logging.error(f"Value Error occurred while updating JSON data: {value_error}")
            raise ValueError("JSON update failed due to invalid weather data.")

        except RuntimeError as run_error:
            logging.error(f"Runtime Error occurred while updating JSON data: {run_error}")
            raise RuntimeError("JSON update operation failed.")

        except Exception as error:
            error_message = f"Unexpected error occurred while updating JSON data: {error}"
            logging.error(error_message)
            raise RuntimeError("An unexpected error occurred during JSON update.")

def process_location(fetcher, location):
    # Helper method to process weather data fetching for a single location.
    conn = DatabasePool.get_connection()
    try:
        fetcher.fetch_weather_data(location)
    except Exception as error:
        logging.error(f"Error processing location {location}: {error}")
    finally:
        # Check if the connection is still valid before releasing it.
        if conn and conn.closed == 0:
            DatabasePool.release_connection(conn)
        else:
            logging.error("Invalid database connection. Discarding and creating a new connection.")
            if conn:
                conn.close()

def monitor_resources():
    # Monitor system resources during script execution.
    logging.info("Resource Usage Monitoring:")
    process = psutil.Process()

    try:
        while not weather_data_collection_completed:
            # Get detailed resource metrics.
            cpu_percent = psutil.cpu_percent(interval=1.0)
            memory_info = process.memory_info()
            disk_usage = psutil.disk_usage('/')
            network_io = psutil.net_io_counters()

            # Log resource metrics.
            logging.info(f"CPU Usage: {cpu_percent:.2f}%")
            logging.info(f"Memory Usage: {memory_info.rss / (1024*1024):.2f} MB")
            logging.info(f"Disk Usage - Total: {disk_usage.total / (1024*1024*1024):.2f} GB, Used: {disk_usage.used / (1024*1024*1024):.2f} GB")
            logging.info(f"Network IO - Bytes Sent: {network_io.bytes_sent}, Bytes Received: {network_io.bytes_recv}")

    except Exception as monitoring_error:
        logging.error(f"Error occurred during resource monitoring: {monitoring_error}")

    finally:
        logging.info("Weather data collection completed. Terminating resource monitoring.")

def main():
    # Main function that fetches weather data from API for multiple locations concurrently.
    try:
        config = ConfigParserWrapper('config.ini')
        api_key = config.get_value('API', 'api_key')
        api_config = APIConfig(api_key, 'config.ini')
        locations = sorted(["Angeles, PH", "Mabalacat City, PH", "Magalang, PH"])
        resource_monitor_thread = threading.Thread(target=monitor_resources)
        atexit.register(DatabasePool.cleanup)  # Register the cleanup function to run on normal program termination.
        
        logging.info(f"Script execution started at {datetime.now().replace(microsecond=0)}.")
        resource_monitor_thread.start()

        # Adjusted chunk size for optimized concurrent processing.
        chunk_size = 1  # Update chunk size based on resource availability and processing requirements.
        location_chunks = [locations[i:i + chunk_size] for i in range(0, len(locations), chunk_size)]

        with DatabaseHandler() as database_handler:
            database_handler.create_initial_schema()

        SchemaManager.optimize_query_performance()

        # Create delayed tasks for each location processing.
        delayed_tasks = [delayed(process_location)(WeatherDataFetcher(api_config), location) for location in locations]

        # Execute the delayed tasks concurrently using Dask.
        results = []
        for chunk in location_chunks:
            delayed_tasks = [delayed(process_location)(WeatherDataFetcher(api_config), location) for location in chunk]
            results.extend(compute(*delayed_tasks))

        # Set the flag to indicate weather data collection is completed.
        global weather_data_collection_completed
        weather_data_collection_completed = True

        logging.info(f"Script execution completed at {datetime.now().replace(microsecond=0)}.")

        end_time = time.time()
        total_time = end_time - start_time
        logging.info(f'Total time taken is {total_time:.2f} seconds.')

    except ValueError as value_error:
        logging.error(f"Value Error occurred in main execution: {value_error}")
        traceback.print_exc()

    except ImportError as import_error:
        logging.error(f"Import Error occurred in main execution: {import_error}")
        traceback.print_exc()

    except (RuntimeError, KeyboardInterrupt) as runtime_error:
        logging.error(f"Runtime Error occurred in main execution: {runtime_error}")
        traceback.print_exc()

    except Exception as exception:
        logging.exception("Unexpected Error occurred in main execution.")

if __name__ == "__main__":
    main()
