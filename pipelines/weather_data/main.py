import requests
from requests.exceptions import RequestException

response_cache = {}

def get_time_zone_data(latitude, longitude):
    api_key = "Insert_TimezoneDB_API_Key_Here"
    base_url = "http://api.timezonedb.com/v2.1/get-time-zone"
    params = {
        "key": api_key,
        "format": "json",
        "by": "position",
        "lat": latitude,
        "lng": longitude
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()

        data = response.json()
        return data

    except RequestException as request_exception:
        print(f"An error occured: {request_exception}.")

def check_city_existence(city_name, country_code):
    api_key = "Insert_OWM_API_Key_Here"
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
            response = requests.get(base_url, params=params)
            response.raise_for_status()

            data = response.json()

            response_cache[key] = data

            # Get the latitude and longitude from OpenWeatherMap response.
            latitude = data['coord']['lat']
            longitude = data['coord']['lon']

            # Get time zone data.
            time_zone_data = get_time_zone_data(latitude, longitude)

            print(f"Timezone: {time_zone_data['zoneName']}, Current time: {time_zone_data['formatted']}")
            print(f"{city_name}, {country_code} exists in OpenWeatherMap API.")
            print(f"Temperature in {city_name}, {country_code}: {data['main']['temp']}°C")

        except RequestException as request_exception:
            print(f"An error occured: {request_exception}.")

city_name = input("Enter city name: ")
country_code = input("Enter country code: ")

check_city_existence(city_name, country_code)
