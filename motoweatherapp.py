import requests
import os

print(f"Using API Key: {API_KEY}")

API_KEY = os.getenv("API_KEY")
API_URL = "https://api.tomorrow.io/v4/timelines?apikey={API_KEY}"
THRESHOLD_WEATHER_CODE = 1000
THRESHOLD_WIND_GUST = 40
THRESHOLD_WIND_SPEED = 30
THRESHOLD_PRECIPITATION = 65
THRESHOLD_TEMPERATURE = 45

def make_api_request():
    payload = {
        "location": "45.3319, -122.6292",
        "fields": ["precipitationProbability", "temperature", "weatherCode", "windSpeed", "windGust"],
        "units": "imperial",
        "timesteps": ["1d"],
        "startTime": "now",
        "endTime": "nowPlus4d"
    }
    headers = {
        "accept": "application/json",
        "Accept-Encoding": "gzip",
        "content-type": "application/json"
    }
    response = requests.post(API_URL, json=payload, headers=headers)
    return response

def parse_response(response):
    try:
        api_response = response.json()
        return api_response
    except ValueError:
        # Handle JSON decoding error
        return None

def print_weather_forecast(results):
    print("Weather Forecast")
    print("================")
    for daily_result in results:
        date = daily_result['startTime'][0:10]
        temp = round(daily_result['values']["temperature"])
        precip_prob = daily_result['values']["precipitationProbability"]
        weather_code = daily_result['values']["weatherCode"]
        wind_speed = daily_result['values']["windSpeed"]
        wind_gust = daily_result['values']["windGust"]
        print(", ".join([
            f"On {date}",
            f"{temp}°F with a {precip_prob}% chance of precipitation",
            f"Weather code: {weather_code}",
            f"Wind speed: {wind_speed} mph",
            f"Wind gust: {wind_gust} mph"
        ]))

def main():
    response = make_api_request()

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        api_response = parse_response(response)

        if api_response:
            # Extract specific fields from the response
            precipitation_probability = api_response["data"]["timelines"][0]["intervals"][0]["values"]["precipitationProbability"]
            temperature = api_response["data"]["timelines"][0]["intervals"][0]["values"]["temperature"]
            weather_code = api_response["data"]["timelines"][0]["intervals"][0]["values"]["weatherCode"]
            wind_speed = api_response["data"]["timelines"][0]["intervals"][0]["values"]["windSpeed"]
            wind_gust = api_response["data"]["timelines"][0]["intervals"][0]["values"]["windGust"]

            print_weather_forecast(api_response['data']['timelines'][0]['intervals'])

            # If-else statements based on the extracted data = safety algorithm if a rider should ride
            if weather_code != THRESHOLD_WEATHER_CODE or wind_gust > THRESHOLD_WIND_GUST or wind_speed > THRESHOLD_WIND_SPEED or \
                    precipitation_probability > THRESHOLD_PRECIPITATION or temperature < THRESHOLD_TEMPERATURE:
                print("DO NOT RIDE")
            else:
                print('When in doubt, throttle out!')

        else:
            # Handle the case when the response cannot be parsed
            print("Error: Unable to parse API response")

    else:
        # Handle the case when the request was not successful
        print(f"Error: {response.status_code}, {response.text}")

if __name__ == "__main__":
    main()
