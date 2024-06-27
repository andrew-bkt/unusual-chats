import os
import requests
from tool_plugins.base_tool import BaseTool

class GetOptionContractHistoric(BaseTool):
    def execute(self, contract_id):
        api_key = os.getenv("UNUSUAL_WHALES_API_KEY")
        url = f"https://api.unusualwhales.com/api/option-contract/{contract_id}/historic"
        headers = {"Authorization": f"Bearer {api_key}"}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch data: {response.status_code}"}

    def get_schema(self):
        return {
            "type": "object",
            "properties": {
                "contract_id": {
                    "type": "string",
                    "description": "The ID of the option contract."
                }
            },
            "required": ["contract_id"]
        }

    def get_description(self):
        return "Fetch historical data for a specific option contract from the Unusual Whales API."