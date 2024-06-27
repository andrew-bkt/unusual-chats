from abc import ABC, abstractmethod
import json
from api_response_manager import api_response_manager

class BaseTool(ABC):
    @abstractmethod
    def execute(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_schema(self):
        pass

    @abstractmethod
    def get_description(self):
        pass

    def handle_large_response(self, response):
        if isinstance(response, (dict, list)) and len(json.dumps(response)) > 500:
            return api_response_manager.format_large_response(response)
        return response

    def format_response(self, response):
        handled_response = self.handle_large_response(response)
        if isinstance(handled_response, dict) and handled_response.get('type') == 'large_response':
            return json.dumps(handled_response)
        return json.dumps(response)