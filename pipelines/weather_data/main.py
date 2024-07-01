import httpx
import asyncio

response_cache = {}

async def get_time_zone_data(latitude, longitude):
    # Function to retrieve time zone data based on OWM's latitude and longitude using the TimezoneDB API.
    api_key = "NGW248HZVWV8"
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

async def check_city_existence(city_name, country_code):
    # Function to check if a city exists in OpenWeatherMap API based on the user's provided city name and country code.
    api_key = "5c9026775828973746c850fa10e2f45c"
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
        try:
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

        except httpx.HTTPError as http_exception:
            print(f"An error occurred: {http_exception}.")

city_name = input("Enter city name: ")
country_code = input("Enter country code: ")

asyncio.run(check_city_existence(city_name, country_code))
