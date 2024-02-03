import geocoder
from pyowm import OWM
from datetime import datetime
import json
from typing import Union, Tuple, Any
import configparser
import psycopg2

# Initialize the WeatherDataFetcher object.
class WeatherDataFetcher:
    def __init__(self, api_key: str):
        if self.validate_api_key(api_key):
            self.api_key = api_key
        else:
            print("Error: Invalid API key provided.")
            self.api_key = None
        self.weather_cache = {}
        self.db_conn = self.connect_to_db()
        
    # Validate the API key.
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        if api_key and not api_key.isspace():
            return True
        else:
            return False
        
    # Get the value of a key from the configuration file.
    @staticmethod
    def get_config(key: str) -> str:
        try:
            config = configparser.ConfigParser()
            config.read('config.ini')
            return config.get('API', key)
        except configparser.Error:
            print("Error: Issue reading the configuration file.")
            return ""
    
    # Get the coordinates (latitude and longitude) of a location.
    def get_coordinates(self, location: str) -> Union[Tuple[float, float], None]:
        try:
            geo_location = geocoder.osm(location)
            return geo_location.latlng if geo_location.latlng else None
        except Exception as e:
            print(f"Error getting coordinates for location: {location}. Error message: {e}")
            return None
    
    # Get the current weather at a specified latitude and longitude.
    def get_current_weather(self, lat: float, lon: float) -> Tuple[str, str, Any]:
        try:
            owm = OWM(self.api_key)
            weather_manager = owm.weather_manager()
            
            observation = weather_manager.weather_at_coords(lat, lon)
            current_date = datetime.now().strftime('%m-%d-%Y')
            current_time = datetime.now().strftime('%H:%M:%S')
            return current_date, current_time, observation.weather
        except Exception as e:
            print(f"Error getting current weather: {e}")
            return "", "", None
    
    # Connect to the Postgres database.
    def connect_to_db(self):
        try:
            conn = psycopg2.connect(
                host='localhost', # Replace with your host
                database='postgres', # Replace with your database name
                user='postgres', # Replace with your username
                password='041688' # Replace with your password
            )
            return conn
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            return None
    
    # Insert the weather data into the Postgres database.
    def insert_data_into_db(self, data):
        try:
            cursor = self.db_conn.cursor()

            insert_query = '''
            INSERT INTO weather_data (location, date, time, temperature, weather_status) 
            VALUES (%s, %s, %s, %s, %s);
            '''

            cursor.execute(insert_query, data)
            self.db_conn.commit()
            print("Data inserted into the database successfully.")
        except Exception as e:
            print(f"Error inserting data into the database: {e}")
    
    # Fetch weather data for a specified location.
    def fetch_weather_data(self, location: str) -> None:
        try:
            if location in self.weather_cache:
                weather_data = self.weather_cache[location]
            else:
                coordinates = self.get_coordinates(location)
                if coordinates:
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
                        print(f"Unable to fetch weather data for {location}.")
                        return
                else:
                    print(f"Unable to fetch coordinates for {location}.")
                    return
            
            self.insert_data_into_db((
                weather_data['location'],
                weather_data['date'],
                weather_data['time'],
                weather_data['temperature'],
                weather_data['weather_status']
            ))

            with open('weather_data.json', 'r') as file:
                existing_data = json.load(file)

            existing_data.append(weather_data)

            with open('weather_data.json', 'w') as file:
                json.dump(existing_data, file, indent=4)

            print(f"Current weather at {location}:")
            print(f"As of: {weather_data['date']} / {weather_data['time']}")
            print(f"Temperature: {weather_data['temperature']}°C")
            print(f"Weather Status: {weather_data['weather_status']}")

        except FileNotFoundError:
            print("Error: The weather data file does not exist.")
        except Exception as e:
            print(f"Error fetching weather data: {e}")

# Retrieve API key from configuration file.
api_key = WeatherDataFetcher.get_config('api_key')

fetcher = WeatherDataFetcher(api_key)
fetcher.fetch_weather_data("Magalang, PH")
