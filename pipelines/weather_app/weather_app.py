import geocoder
from pyowm import OWM
from datetime import datetime
import json

def get_coordinates(location: str):
    g = geocoder.osm(location)
    return g.latlng if g.latlng else None

def get_current_weather(lat: float, lon: float, api_key: str):
    owm = OWM(api_key)
    mgr = owm.weather_manager()

    observation = mgr.weather_at_coords(lat, lon)
    # Format the current date and time
    current_date = datetime.now().strftime('%m-%d-%Y')
    current_time = datetime.now().strftime('%H:%M:%S')
    # Return the formatted current date and time along with the weather
    return current_date, current_time, observation.weather

def fetch_weather_data(location: str, api_key: str):
    coordinates = get_coordinates(location)

    if coordinates:
        lat, lon = coordinates
        # Get the formatted current date, time, and weather
        current_date, current_time, weather = get_current_weather(lat, lon, api_key)

        weather_data = {
            'location': location,
            'date': current_date,
            'time': current_time,
            'temperature': f"{weather.temperature('celsius')['temp']}",
            'weather_status': weather.status
        }

        try:
            # Load existing weather data from the JSON file
            with open('weather_data.json', 'r') as file:
                existing_data = json.load(file)
        except FileNotFoundError:
            existing_data = []

        # Append the new weather data to the existing data
        existing_data.append(weather_data)

        # Save the updated data back to the JSON file
        with open('weather_data.json', 'w') as file:
            json.dump(existing_data, file, indent=4)

        print(f"Current weather at {location}:")
        print(f"As of: {current_date} / {current_time}")
        print(f"Temperature: {weather_data['temperature']}°C")
        print(f"Weather Status: {weather_data['weather_status']}")
    else:
        print("Unable to fetch weather data for the location.")

fetch_weather_data("Magalang,PH", "Your_API_Key_Here")
