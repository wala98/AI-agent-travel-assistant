# travel_agent/src/travel_agent/tools/custom_tool.py
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool, tool

class MyCustomToolInput(BaseModel):
    argument: str = Field(..., description="Description of the argument.")

class MyCustomTool(BaseTool):
    name: str = "Name of my tool"
    description: str = (
        "Clear description for what this tool is useful for."
    )
    args_schema: Type[BaseModel] = MyCustomToolInput

    def _run(self, argument: str) -> str:
        return "this is an example of a tool output, ignore it and move along."

@tool("get_weather")
def get_weather(city: str) -> str:
    """Return a short stubbed forecast string for the given city."""
    return f"Stub weather for {city}: 24–28°C, partly cloudy."

@tool("get_weather_range")
def get_weather_range(city: str, start: str, end: str) -> str:
    """Return a short stubbed daily forecast list for a city and date range."""
    return f"Stub multi-day weather for {city} from {start} to {end}: mostly mild, some clouds."

@tool("get_city_info")
def get_city_info(city: str) -> str:
    """Return a short stubbed city overview."""
    return f"{city}: Coastal city known for beaches, medina, and historic sites."

@tool("get_hotel_info")
def get_hotel_info(hotel_name: str, city: str | None = None) -> str:
    """Return a short stubbed hotel summary."""
    loc = f" in {city}" if city else ""
    return f"{hotel_name}{loc}: 4-star, beach access, pool, breakfast, family-friendly."

@tool("get_nearby_places")
def get_nearby_places(place_type: str, near_name: str | None = None, near_city: str | None = None) -> str:
    """Return a short stubbed list of nearby places of a type."""
    base = near_name or near_city or "the area"
    return f"Nearby {place_type} around {base}: Cafe A (0.4km), Cafe B (0.9km), Cafe C (1.3km)."