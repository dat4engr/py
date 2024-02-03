import geocoder
from pyowm import OWM
from datetime import datetime
import json
from typing import Union, Tuple, Any
import configparser

# Initialize the WeatherDataFetcher object.
class WeatherDataFetcher:
    def __init__(self, api_key: str):
        if self.validate_api_key(api_key):
            self.api_key = api_key
        else:
            print("Error: Invalid API key provided.")
            self.api_key = None
        self.weather_cache = {}
        
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
                        weather_data = {
                            'location': location,
                            'date': current_date,
                            'time': current_time,
                            'temperature': f"{weather.temperature('celsius')['temp']}",
                            'weather_status': weather.status
                        }
                        self.weather_cache[location] = weather_data
                    else:
                        print(f"Unable to fetch weather data for {location}.")
                        return
                else:
                    print(f"Unable to fetch coordinates for {location}.")
                    return
            try:
                with open('weather_data.json', 'r') as file:
                    existing_data = json.load(file)
            except FileNotFoundError:
                existing_data = []

            existing_data.append(weather_data)

            try:
                with open('weather_data.json', 'w') as file:
                    json.dump(existing_data, file, indent=4)
            except Exception as e:
                print(f"Error writing to the weather data file: {e}")

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
