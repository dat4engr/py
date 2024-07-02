import httpx
import asyncio
import logging
import re

logging.basicConfig(filename='error_log.log', level=logging.ERROR)

response_cache = {}

async def fetch_data(url, params):
    # Asynchronously fetches data from a given URL with parameters.
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()

async def get_time_zone_data(latitude, longitude):
    # Retrieves time zone data based on latitude and longitude.
    api_key = ""
    base_url = "http://api.timezonedb.com/v2.1/get-time-zone"
    params = {
        "key": api_key,
        "format": "json",
        "by": "position",
        "lat": latitude,
        "lng": longitude
    }
    
    return await fetch_data(base_url, params)

async def check_city_existence(city_name, country_code):
    # Checks if a given city exists in OpenWeatherMap API and retrieves weather data.
    try:
        api_key = ""
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "appid": api_key,
            "units": "metric"
        }

        query = f"{city_name},{country_code}"
        key = f"{city_name},{country_code}"
        params['q'] = query

        if key in response_cache:
            print(f"Retrieving cached response for {city_name}, {country_code}.")
            data = response_cache[key]
        else:
            data = await fetch_data(base_url, params)
            response_cache[key] = data

            latitude = data['coord']['lat']
            longitude = data['coord']['lon']

            time_zone_data = await get_time_zone_data(latitude, longitude)

            print(f"Timezone: {time_zone_data['zoneName']}, Current time: {time_zone_data['formatted']}")
            print(f"{city_name}, {country_code} exists in OpenWeatherMap API.")
            print(f"Temperature in {city_name}, {country_code}: {data['main']['temp']}°C")

    except httpx.HTTPStatusError as http_status_error:
        logging.error(f"An HTTP Error occurred: {http_status_error}")
        print(f"An error occurred, please try again later.")
        raise

    except httpx.NetworkError as network_error:
        logging.error(f"An HTTP Network Error occurred: {network_error}")
        print(f"A network error occurred, please check your internet connection.")
        raise

def validate_city_name(city_name):
    # Validates the format of the city name input.
    if not re.match("^[a-zA-Z ]+$", city_name):
        raise ValueError("City name should only contain letters and spaces")

def validate_country_code(country_code):
    # Validates the format of the country code input.
    if not re.match("^[a-zA-Z]{2}$", country_code):
        raise ValueError("Country code should only 2-letter code")

city_name = input("Enter city name: ")
country_code = input("Enter country code: ")

try:
    validate_city_name(city_name)
    validate_country_code(country_code)
    asyncio.run(check_city_existence(city_name, country_code))
except ValueError as value_error:
    print(f"Invalid input: {value_error}.")
