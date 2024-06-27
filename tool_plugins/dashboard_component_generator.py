import json
from tool_plugins.base_tool import BaseTool
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class DashboardComponentGenerator(BaseTool):
    def execute(self, query):
        prompt = f"""
        Given the following user query for a dashboard component, generate a Python dictionary
        that describes how to create this component. The dictionary should include:
        - 'type': The type of component (e.g., 'chart', 'table', 'metric')
        - 'title': A title for the component
        - 'id': A unique identifier for the component
        - 'data': Sample data for the component
        - 'layout': Layout information for the component (for charts only)

        User query: {query}

        Response format:
        {{
            "type": "component_type",
            "title": "Component Title",
            "id": "unique_id",
            "data": [...],
            "layout": {{...}} (for charts only)
        }}
        """

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates dashboard components based on user queries."},
                {"role": "user", "content": prompt}
            ]
        )

        component_description = response.choices[0].message.content
        return self.format_response(json.loads(component_description))

    def get_schema(self):
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The user's query describing the desired dashboard component"
                }
            },
            "required": ["query"]
        }

    def get_description(self):
        return "Generates a dashboard component based on a user's description"