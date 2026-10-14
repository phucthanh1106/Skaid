from langchain.tools import tool
import os
from dotenv import load_dotenv
import requests
from src.skaid.config import WEATHER_API_KEY

# Multiplies two numbers supplied by the model.
@tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers together."""
    return a * b

# Give the agent access to current weather information.
@tool
def get_weather(city: str) -> dict:
    """Get the current temperature for a city."""
    if not WEATHER_API_KEY:
        return {"error": "Weather API key is not configured."}

    url = "https://api.weatherapi.com/v1/current.json"
    params = {
        "key": WEATHER_API_KEY,
        "q": city,
        "aqi": "no"
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            error_msg = response.json().get("error", {}).get("message", "Unknown error")
            return {"error": f"Failed to retrieve weather: {error_msg} (Status: {response.status_code})"}

        data = response.json()
        current = data.get("current", {})
        location = data.get("location", {})

        return {
            "city": location.get("name"),
            "region": location.get("region"),
            "country": location.get("country"),
            "temp_f": current.get("temp_f"),
            "temp_c": current.get("temp_c"),
            "condition": current.get("condition", {}).get("text"),
            "humidity": current.get("humidity"),
            "wind_mph": current.get("wind_mph")
        }

    except requests.RequestException as e:
        return {"error": f"Network request failed: {str(e)}"}

# Give the agent information about Skidmore College
@tool
def search_documents(query: str) -> dict | None:
    return