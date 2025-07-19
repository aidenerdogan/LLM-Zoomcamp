# weather_server.py
from fastmcp import FastMCP

known_weather_data = {"berlin": 20.0}

mcp = FastMCP("Weather Server ☁️")

@mcp.tool
def get_weather(city: str) -> float:
    """Retrieve the temperature for a specific city."""
    city = city.strip().lower()
    if city in known_weather_data:
        return known_weather_data[city]
    return 22.2  # Or use random

@mcp.tool
def set_weather(city: str, temp: float) -> str:
    """Set the temperature for a specific city."""
    city = city.strip().lower()
    known_weather_data[city] = temp
    return "OK"

if __name__ == "__main__":
    mcp.run()