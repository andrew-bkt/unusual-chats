import os
import requests
from tool_plugins.base_tool import BaseTool

class GetOptionContracts(BaseTool):
    def execute(self, ticker):
        api_key = os.getenv("UNUSUAL_WHALES_API_KEY")
        url = f"https://api.unusualwhales.com/api/stock/{ticker}/option-contracts"
        headers = {"Authorization": f"Bearer {api_key}"}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return self.format_response(data)
        else:
            return {"error": f"Failed to fetch data: {response.status_code}"}

    def get_schema(self):
        return {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "The stock ticker."
                }
            },
            "required": ["ticker"]
        }

    def get_description(self):
        return "Fetch option contract data for a specific stock ticker from the Unusual Whales API."