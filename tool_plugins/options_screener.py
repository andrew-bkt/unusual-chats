import os
import requests
import logging
from tool_plugins.base_tool import BaseTool

class OptionsScreener(BaseTool):
    def execute(self, kwargs):
        api_key = os.getenv("UNUSUAL_WHALES_API_KEY")
        if not api_key:
            error_message = "API key is missing"
            logging.error(error_message)
            return {"error": error_message}
        
        url = "https://api.unusualwhales.com/api/screener/option-contracts"
        headers = {"Authorization": f"Bearer {api_key}"}
        
        # Filter out None values from kwargs
        params = {k: v for k, v in kwargs.items() if v is not None}
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # This will raise an HTTPError for bad responses
            return response.json()
        except requests.RequestException as e:
            error_message = f"Failed to fetch data: {str(e)}"
            logging.error(error_message)
            return {"error": error_message}

    def get_schema(self):
        return {
            "type": "object",
            "properties": {
                "api_key": {"type": "string", "description": "Your API key for authentication"},
                "ticker_symbol": {"type": "string", "description": "Ticker symbol"},
                "sectors[]": {"type": "array", "items": {"type": "string"}, "description": "Sectors"},
                "min_underlying_price": {"type": "number", "description": "Minimum underlying price"},
                "max_underlying_price": {"type": "number", "description": "Maximum underlying price"},
                "is_otm": {"type": "boolean", "description": "Is out of the money"},
                "min_dte": {"type": "integer", "description": "Minimum days to expiration"},
                "max_dte": {"type": "integer", "description": "Maximum days to expiration"},
                "min_diff": {"type": "number", "description": "Minimum price difference"},
                "max_diff": {"type": "number", "description": "Maximum price difference"},
                "min_volume": {"type": "integer", "description": "Minimum volume"},
                "max_volume": {"type": "integer", "description": "Maximum volume"},
                "min_oi": {"type": "integer", "description": "Minimum open interest"},
                "max_oi": {"type": "integer", "description": "Maximum open interest"},
                "min_floor_volume": {"type": "integer", "description": "Minimum floor volume"},
                "max_floor_volume": {"type": "integer", "description": "Maximum floor volume"},
                "vol_greater_oi": {"type": "boolean", "description": "Volume greater than open interest"},
                "issue_types[]": {"type": "array", "items": {"type": "string"}, "description": "Issue types"},
                "order": {"type": "string", "description": "Order by field"},
                "order_direction": {"type": "string", "enum": ["asc", "desc"], "description": "Order direction"}
            },
            "required": ["api_key"]
        }

    def get_description(self):
        return "Screen option contracts based on various parameters using the Unusual Whales API"