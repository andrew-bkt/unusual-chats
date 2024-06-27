import uuid
import json
import os
from typing import Dict, Any

class APIResponseManager:
    def __init__(self, response_dir='api_responses'):
        self.response_dir = response_dir
        os.makedirs(self.response_dir, exist_ok=True)

    def store_response(self, response: Any) -> str:
        response_id = str(uuid.uuid4())
        file_path = os.path.join(self.response_dir, f"{response_id}.json")
        with open(file_path, 'w') as f:
            json.dump(response, f)
        return response_id

    def get_response(self, response_id: str) -> Any:
        file_path = os.path.join(self.response_dir, f"{response_id}.json")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return None

    def get_response_summary(self, response: Any) -> str:
        if isinstance(response, dict):
            return f"API Response: {len(response)} key-value pairs"
        elif isinstance(response, list):
            return f"API Response: List with {len(response)} items"
        else:
            return f"API Response: {type(response).__name__}"

    def format_large_response(self, response: Any) -> Dict[str, Any]:
        response_id = self.store_response(response)
        summary = self.get_response_summary(response)
        return {
            "type": "large_response",
            "id": response_id,
            "summary": summary
        }

api_response_manager = APIResponseManager()