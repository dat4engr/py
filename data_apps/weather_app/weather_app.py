import pyttsx3
import requests
import datetime
import geocoder
import json

def speak(text):
    # This function uses the pyttsx3 library to convert text to speech using the default system voice.
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.say(text)
    engine.runAndWait()

def get_weather_data(api_key, location):
    # This function retrieves weather data from the OpenWeatherMap API based on the provided location.
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": location,
        "appid": api_key,
        "units": "metric"
    }
    response = requests.get(base_url, params=params)
    return response.json()

def get_user_location():
    # This function uses the geocoder library to retrieve the user's current location based on their IP address.
    g = geocoder.ip('me')
    return g.city

def format_date(timestamp):
    # This function formats a UNIX timestamp into a readable date and time string.
    return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

def collect_weather_data():
    # This function collects weather data for the user's current location, prints the data to the console, and saves it to a JSON file.
    api_key = "Input your OpenWeatherMap API key here."
    location = get_user_location()
    weather_data = get_weather_data(api_key, location)

    speak("Weather information for " + location)
    speak("Time of data collection: " + format_date(weather_data['dt']))
    speak("Temperature: " + str(weather_data['main']['temp']) + "°C")
    speak("Weather description: " + weather_data['weather'][0]['description'])

    # For testing of data collected using OpenWeatherMap API:
    # print("Weather information for", location)
    # print("Time of data collection:", format_date(weather_data['dt']))
    # print("Temperature:", weather_data['main']['temp'], "°C")
    # print("Weather description:", weather_data['weather'][0]['description'])

    data = {
        "location": location,
        "data_collection_time": format_date(weather_data['dt']),
        "temperature": weather_data['main']['temp'],
        "weather_description": weather_data['weather'][0]['description']
    }

    # Read existing weather data from the JSON file
    try:
        with open('weather_data.json', 'r') as file:
            existing_data = json.load(file)
    except FileNotFoundError:
        existing_data = []

    # Append the new weather data to the existing data
    existing_data.append(data)

    # Write the updated data back to the JSON file
    with open('weather_data.json', 'w') as file:
        json.dump(existing_data, file, indent=4)

collect_weather_data()
