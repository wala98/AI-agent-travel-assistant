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
