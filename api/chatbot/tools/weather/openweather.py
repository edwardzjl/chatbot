from langchain_community.tools.pubmed.tool import PubmedQueryRun



# import requests
# from langchain_core.callbacks import (
#     AsyncCallbackManagerForToolRun,
#     CallbackManagerForToolRun,
# )
# from langchain_core.tools import BaseTool, ToolException
# from langchain_core.tools.base import ArgsSchema
# from pydantic import BaseModel, Field
# from requests.exceptions import HTTPError


# class WeatherInput(BaseModel):
#     location: str = Field(description="first number")
#     b: int = Field(description="second number")


# # Note: It's important that every field has type hints. BaseTool is a
# # Pydantic class and not having type hints can lead to unexpected behavior.
# class WeatherTool(BaseTool):
#     name: str = "get_weather"
#     description: str = "useful for when you need to answer questions about math"
#     args_schema: ArgsSchema | None = WeatherInput
#     base_url: str = "https://api.openweathermap.org/"
#     api_key: str

#     def _geocoding(self, location: str) -> dict:
#         """
#         See <https://openweathermap.org/api/geocoding-api>
#         """
#         try:
#             response = requests.get(
#                 f"{self.base_url}/geo/1.0/direct",
#                 params={
#                     "q": location,
#                     "limit": 1,
#                     "appid": self.api_key,
#                 }
#             )
#             response.raise_for_status()
#         except HTTPError as http_err:
#             raise ToolException(f"HTTP error occurred: {http_err}")
#         else:
#             first_match = response.json()[0]
#             return {"lat": first_match["lat"], "lon": first_match["lon"]}

#     def _run(
#         self,
#         location: str,
#         run_manager: CallbackManagerForToolRun | None = None,
#     ) -> str:
#         """Use the tool."""
#         loc = self._geocoding(location)
#         # TODO: get weather by location
#         # See <https://openweathermap.org/api/one-call-3>

#     async def _arun(
#         self,
#         location: str,
#         run_manager: AsyncCallbackManagerForToolRun | None = None,
#     ) -> str:
#         """Use the tool asynchronously."""
#         # TODO: async implementation
#         return self._run(location, run_manager=run_manager.get_sync())
