import os
import sys
import json
import importlib
import importlib.util
import logging
from tool_plugins.base_tool import BaseTool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ToolManager:
    def __init__(self, plugin_dir='tool_plugins'):
        self.plugin_dir = plugin_dir
        self.config_file = os.path.join(plugin_dir, 'tools_config.json')
        self.tools = {}
        
        # Add the plugin directory to the Python path
        plugin_path = os.path.abspath(plugin_dir)
        if plugin_path not in sys.path:
            sys.path.insert(0, plugin_path)
            logger.info(f"Added {plugin_path} to Python path")
        
        self.load_tools()

    def load_tools(self):
        logger.info(f"Loading tools from {self.plugin_dir}")
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded config: {config}")
        except FileNotFoundError:
            logger.warning(f"Config file not found: {self.config_file}")
            config = {}

        for filename in os.listdir(self.plugin_dir):
            if filename.endswith('.py') and filename != 'base_tool.py':
                module_name = filename[:-3]
                logger.info(f"Found potential tool: {module_name}")
                if module_name in config and config[module_name].get('enabled', True):
                    logger.info(f"Attempting to load tool: {module_name}")
                    try:
                        module = importlib.import_module(module_name)
                        for item_name in dir(module):
                            item = getattr(module, item_name)
                            if isinstance(item, type) and issubclass(item, BaseTool) and item != BaseTool:
                                logger.info(f"Loaded tool class: {item_name}")
                                self.tools[module_name] = item()
                    except Exception as e:
                        logger.error(f"Error loading tool {module_name}: {str(e)}")
                else:
                    logger.info(f"Tool {module_name} is disabled or not in config")

    logger.info(f"Loaded tools: {list(self.tools.keys())}")


    def get_tool(self, name):
        return self.tools.get(name)

    def get_all_tools(self):
        return self.tools

    def create_tool(self, name, code):
        file_path = os.path.join(self.plugin_dir, f"{name}.py")
        with open(file_path, 'w') as f:
            f.write(code)
        
        with open(self.config_file, 'r+') as f:
            config = json.load(f)
            config[name] = {"enabled": True}
            f.seek(0)
            json.dump(config, f, indent=4)
            f.truncate()
        
        self.load_tools()

    def update_tool(self, name, code):
        file_path = os.path.join(self.plugin_dir, f"{name}.py")
        with open(file_path, 'w') as f:
            f.write(code)
        self.load_tools()

    def delete_tool(self, name):
        file_path = os.path.join(self.plugin_dir, f"{name}.py")
        if os.path.exists(file_path):
            os.remove(file_path)
        
        with open(self.config_file, 'r+') as f:
            config = json.load(f)
            if name in config:
                del config[name]
            f.seek(0)
            json.dump(config, f, indent=4)
            f.truncate()
        
        if name in self.tools:
            del self.tools[name]

    def get_tool_code(self, name):
        file_path = os.path.join(self.plugin_dir, f"{name}.py")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return f.read()
        return None

    def get_available_tools(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": tool.get_description(),
                    "parameters": tool.get_schema()
                }
            }
            for name, tool in self.tools.items()
        ]

    def get_all_tools(self):
        return self.tools