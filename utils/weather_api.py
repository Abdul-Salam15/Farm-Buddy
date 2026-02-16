import requests
import os
from collections import Counter
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL_WEATHER = "https://api.openweathermap.org/data/2.5/weather"
BASE_URL_FORECAST = "https://api.openweathermap.org/data/2.5/forecast"

def get_weather(lat, lon):
    """
    Fetch current weather data from OpenWeatherMap API using latitude and longitude.
    """
    if not OPENWEATHER_API_KEY:
        return {"error": "API Key missing. Please add OPENWEATHER_API_KEY to .env"}

    try:
        params = {
            "lat": lat,
            "lon": lon,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"  # Celsius
        }
        response = requests.get(BASE_URL_WEATHER, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        return {"error": f"HTTP error occurred: {http_err}"}
    except Exception as err:
        return {"error": f"An error occurred: {err}"}

def get_forecast(lat, lon):
    """
    Fetch 5-day weather forecast from OpenWeatherMap API.
    """
    if not OPENWEATHER_API_KEY:
        return {"error": "API Key missing"}
        
    try:
        params = {
            "lat": lat,
            "lon": lon,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        }
        response = requests.get(BASE_URL_FORECAST, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        return {"error": f"HTTP error: {http_err}"}
    except Exception as err:
        return {"error": f"Error: {err}"}

def format_weather_for_ai(weather_data):
    """
    Format raw weather JSON into a natural language string for the AI context.
    """
    if "error" in weather_data:
        return f"Weather data unavailable: {weather_data['error']}"

    try:
        location = weather_data.get("name", "Unknown Location")
        main = weather_data.get("main", {})
        weather = weather_data.get("weather", [{}])[0]
        wind = weather_data.get("wind", {})
        
        temp = main.get("temp", "N/A")
        description = weather.get("description", "N/A")
        humidity = main.get("humidity", "N/A")
        wind_speed = wind.get("speed", "N/A")
        
        return (f"Current weather in {location}: {temp}°C, {description}. "
                f"Humidity: {humidity}%. Wind Speed: {wind_speed} m/s.")
    except Exception as e:
        return f"Error formatting weather data: {str(e)}"

def format_forecast_for_ai(forecast_data):
    """
    Format 5-day forecast JSON into a daily summary for AI context.
    """
    if "error" in forecast_data:
        return f"Forecast unavailable: {forecast_data['error']}"

    try:
        # Group by date
        daily_items = {}
        for item in forecast_data.get('list', []):
            # dt_txt format: "2023-10-27 12:00:00"
            date_str = item.get('dt_txt', '').split(' ')[0]
            if not date_str: continue
            
            if date_str not in daily_items:
                daily_items[date_str] = []
            daily_items[date_str].append(item)
            
        summary_lines = []
        # Sort dates to be chronological
        sorted_dates = sorted(daily_items.keys())[:5] # limit to 5 days
        
        for date in sorted_dates:
            items = daily_items[date]
            
            # Calculate averages/most common
            temps = [x['main']['temp'] for x in items]
            descriptions = [x['weather'][0]['description'] for x in items]
            rain_prob = [x.get('pop', 0) for x in items] # Probability of precipitation
            
            avg_temp = sum(temps) / len(temps)
            max_temp = max(temps)
            min_temp = min(temps)
            most_common_desc = Counter(descriptions).most_common(1)[0][0]
            avg_rain_prob = sum(rain_prob) / len(rain_prob) if rain_prob else 0
            
            rain_note = ""
            if avg_rain_prob > 0.3:
                rain_note = f" (Rain chance: {int(avg_rain_prob * 100)}%)"
            
            summary_lines.append(f"- {date}: {most_common_desc}, {int(min_temp)}°C-{int(max_temp)}°C{rain_note}")
            
        return "Upcoming Forecast:\n" + "\n".join(summary_lines)
    except Exception as e:
        return f"Error formatting forecast: {str(e)}"
