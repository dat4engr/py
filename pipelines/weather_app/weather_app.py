import geocoder
from pyowm import OWM
from datetime import datetime
import json
import psycopg2
import configparser
import logging
from typing import Union, Tuple, Any

class ErrorCode:
    # This class defines error codes used within the application.
    INVALID_API_KEY = 1
    CONFIG_FILE_READ_ERROR = 2
    COORDINATES_RETRIEVAL_ERROR = 3
    CURRENT_WEATHER_RETRIEVAL_ERROR = 4
    WEATHER_DATA_FETCH_ERROR = 5
    DATABASE_CONNECTION_ERROR = 6
    DATA_INSERTION_ERROR = 7
    JSON_UPDATE_ERROR = 8
    FILE_NOT_FOUND_ERROR = 9

# A class to fetch and handle weather data.
class WeatherDataFetcher:
    def __init__(self, api_key: str):
        # Initializes an instance of WeatherDataFetcher class.
        if self.validate_api_key(api_key):
            self.api_key = api_key
        else:
            logging.error("Invalid API key provided.")
            self.api_key = None
        self.weather_cache = {}
        self.db_conn = None

    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        # Validates if the API key is present and not empty.
        if api_key and not api_key.isspace():
            return True
        else:
            return False

    @staticmethod
    def get_config(key: str) -> str:
        # Retrieves a configuration value from the config.ini file.
        try:
            config = configparser.ConfigParser()
            config.read('config.ini')
            return config.get('API', key)
        except configparser.Error as e:
            logging.error("Issue reading the configuration file.")
            return "", ErrorCode.CONFIG_FILE_READ_ERROR
    
    def get_coordinates(self, location: str) -> Union[Tuple[float, float], None]:
        # Retrieves the latitude and longitude coordinates of a location.
        try:
            geo_location = geocoder.osm(location)
            return geo_location.latlng if geo_location.latlng else None
        except Exception as e:
            logging.error(f"Error getting coordinates for location: {location}. Error message: {e}")
            return None, ErrorCode.COORDINATES_RETRIEVAL_ERROR
    
    def get_current_weather(self, lat: float, lon: float) -> Tuple[str, str, Any]:
        # Retrieves the current weather data for a given set of latitude and longitude coordinates.
        try:
            owm = OWM(self.api_key)
            weather_manager = owm.weather_manager()
            
            observation = weather_manager.weather_at_coords(lat, lon)
            current_date = datetime.now().strftime('%Y-%m-%d')
            current_time = datetime.now().strftime('%H:%M:%S')
            return current_date, current_time, observation.weather
        except Exception as e:
            logging.error(f"Error getting current weather: {e}")
            return "", "", None, ErrorCode.CURRENT_WEATHER_RETRIEVAL_ERROR
    
    def fetch_weather_data(self, location: str) -> None:
        # Fetches weather data for a given location.
        try:
            if location in self.weather_cache:
                weather_data = self.weather_cache[location]
            else:
                coordinates = self.get_coordinates(location)
                if coordinates[1]:
                    lat, lon = coordinates
                    current_date, current_time, weather = self.get_current_weather(lat, lon)
                    if weather:
                        temperature = f"{weather.temperature('celsius')['temp']}"
                        weather_status = weather.status
                        weather_data = {
                            'location': location,
                            'date': current_date,
                            'time': current_time,
                            'temperature': temperature,
                            'weather_status': weather_status
                        }
                        self.weather_cache[location] = weather_data
                    else:
                        logging.error(f"Unable to fetch weather data for {location}.")
                        return ErrorCode.WEATHER_DATA_FETCH_ERROR
                else:
                    logging.error(f"Unable to fetch coordinates for {location}.")
                    return ErrorCode.COORDINATES_RETRIEVAL_ERROR
            
            db_handler = DatabaseHandler()
            db_handler.insert_data(weather_data)

            json_handler = JSONHandler()
            json_handler.update_data(weather_data)

            print(f"Current weather at {location}:")
            print(f"As of: {weather_data['date']} / {weather_data['time']}")
            print(f"Temperature: {weather_data['temperature']}°C")
            print(f"Weather Status: {weather_data['weather_status']}")

        except FileNotFoundError:
            logging.error("Error: The weather data file does not exist.", ErrorCode.FILE_NOT_FOUND_ERROR)
        except Exception as e:
            logging.error(f"Error fetching weather data: {e}", ErrorCode.WEATHER_DATA_FETCH_ERROR)

class DatabaseHandler:
    # A class to handle database operations.
    def __init__(self):
        # Initializes an instance of the DatabaseHandler class.
        self.db_conn = None

    def connect_to_db(self):
        # Connects to the database.
        try:
            config = configparser.ConfigParser()
            config.read('config.ini')
            conn = psycopg2.connect(
                host=config.get('Database', 'host'),
                database=config.get('Database', 'database'),
                user=config.get('Database', 'user'),
                password=config.get('Database', 'password')
            )
            return conn
        except Exception as e:
            logging.error(f"Error connecting to the database: {e}", ErrorCode.DATABASE_CONNECTION_ERROR)
            return None
    
    def insert_data(self, data):
        # Inserts weather data into the database.
        try:
            if self.db_conn is None:
                self.db_conn = self.connect_to_db()
            
            cursor = self.db_conn.cursor()

            insert_query = '''
            INSERT INTO weather_data (location, date, time, temperature, weather_status) 
            VALUES (%s, %s, %s, %s, %s);
            '''

            cursor.execute(insert_query, (
                data['location'],
                data['date'],
                data['time'],
                data['temperature'],
                data['weather_status']
            ))
            self.db_conn.commit()
            logging.info("Data inserted into the database successfully.")
        except Exception as e:
            logging.error(f"Error inserting data into the database: {e}", ErrorCode.DATA_INSERTION_ERROR)

class JSONHandler:
    # A class to handle JSON operations.
    def update_data(self, weather_data):
        try:
            with open('weather_data.json', 'r') as file:
                existing_data = json.load(file)

            existing_data.append(weather_data)

            with open('weather_data.json', 'w') as file:
                json.dump(existing_data, file, indent=4)

        except Exception as e:
            logging.error(f"Error updating JSON data: {e}", ErrorCode.JSON_UPDATE_ERROR)

if __name__ == "__main__":
    api_key = WeatherDataFetcher.get_config('api_key')
    fetcher = WeatherDataFetcher(api_key)
    fetcher.fetch_weather_data("Magalang, PH")
