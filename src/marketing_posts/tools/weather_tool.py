from crewai_tools import tool
import json


@tool("get_current_weather")
def get_current_weather(location: str, unit: str = "fahrenheit") -> str:
    """
    Get the current weather for a given location.
    
    Args:
        location (str): The city and state/country, e.g., "Paris, France"
        unit (str): Temperature unit - either "celsius" or "fahrenheit" (default: "fahrenheit")
    
    Returns:
        str: A JSON string containing weather information including temperature, conditions, humidity, and wind speed
    """
    # This is a mock implementation that returns realistic weather data
    # In a production environment, this would call a real weather API
    
    # Mock weather data for demonstration purposes
    weather_data = {
        "Paris, France": {
            "celsius": 18,
            "fahrenheit": 65,
            "conditions": "Partly cloudy",
            "humidity": "65%",
            "wind_speed": "15 km/h",
            "feels_like_celsius": 17,
            "feels_like_fahrenheit": 63
        },
        "London, UK": {
            "celsius": 15,
            "fahrenheit": 59,
            "conditions": "Cloudy with light rain",
            "humidity": "78%",
            "wind_speed": "20 km/h",
            "feels_like_celsius": 13,
            "feels_like_fahrenheit": 55
        },
        "New York, USA": {
            "celsius": 22,
            "fahrenheit": 72,
            "conditions": "Sunny",
            "humidity": "55%",
            "wind_speed": "10 km/h",
            "feels_like_celsius": 22,
            "feels_like_fahrenheit": 72
        },
        "Tokyo, Japan": {
            "celsius": 20,
            "fahrenheit": 68,
            "conditions": "Clear",
            "humidity": "60%",
            "wind_speed": "12 km/h",
            "feels_like_celsius": 19,
            "feels_like_fahrenheit": 66
        }
    }
    
    # Normalize location for lookup
    location_normalized = location.strip()
    
    # Try to find the location in our mock data
    weather = None
    for key in weather_data:
        if location_normalized.lower() in key.lower() or key.lower() in location_normalized.lower():
            weather = weather_data[key]
            break
    
    # Default weather if location not found
    if weather is None:
        weather = {
            "celsius": 20,
            "fahrenheit": 68,
            "conditions": "Partly cloudy",
            "humidity": "60%",
            "wind_speed": "15 km/h",
            "feels_like_celsius": 19,
            "feels_like_fahrenheit": 66
        }
    
    # Prepare response based on requested unit
    unit_lower = unit.lower()
    if unit_lower == "celsius":
        temp = weather["celsius"]
        feels_like = weather["feels_like_celsius"]
        temp_unit = "°C"
    else:
        temp = weather["fahrenheit"]
        feels_like = weather["feels_like_fahrenheit"]
        temp_unit = "°F"
    
    result = {
        "location": location,
        "temperature": temp,
        "unit": temp_unit,
        "feels_like": feels_like,
        "conditions": weather["conditions"],
        "humidity": weather["humidity"],
        "wind_speed": weather["wind_speed"]
    }
    
    return json.dumps(result, indent=2)
