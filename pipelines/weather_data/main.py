import httpx
import asyncio
import logging

# Configure logging
logging.basicConfig(filename='error_log.log', level=logging.ERROR)

response_cache = {}

async def get_time_zone_data(latitude, longitude):
    try:
        # Function to retrieve time zone data based on OWM's latitude and longitude using the TimezoneDB API.
        api_key = "Insert_TimeZoneDB_API_Here"
        base_url = "http://api.timezonedb.com/v2.1/get-time-zone"
        params = {
            "key": api_key,
            "format": "json",
            "by": "position",
            "lat": latitude,
            "lng": longitude
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(base_url, params=params)
            response.raise_for_status()

            data = response.json()
            return data

    except httpx.HTTPStatusError as http_status_error:
        logging.error(f"An HTTP Error occurred: {http_status_error}")
        raise

    except httpx.NetworkError as network_error:
        logging.error(f"An HTTP Network Error occurred: {network_error}")
        raise

async def check_city_existence(city_name, country_code):
    try:
        # Function to check if a city exists in OpenWeatherMap API based on the user's provided city name and country code.
        api_key = "Insert_OWM_API_Here"
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "appid": api_key,
            "units": "metric"  # Specify the unit system here
        }

        query = f"{city_name},{country_code}"
        key = f"{city_name},{country_code}"
        params['q'] = query

        if key in response_cache:
            print(f"Retrieving cached response for {city_name}, {country_code}.")
            data = response_cache[key]
        else:
            async with httpx.AsyncClient() as client:
                response = await client.get(base_url, params=params)
                response.raise_for_status()

                data = response.json()

                response_cache[key] = data

                # Get the latitude and longitude from OpenWeatherMap response.
                latitude = data['coord']['lat']
                longitude = data['coord']['lon']

                # Get time zone data.
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

city_name = input("Enter city name: ")
country_code = input("Enter country code: ")

asyncio.run(check_city_existence(city_name, country_code))
