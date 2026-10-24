class ToolRegistry:
    def __init__(self):
        self._tools = {}

    def register(self, name, description, parameters, func):
        self._tools[name] = {
            "name": name,
            "description": description,
            "parameters": parameters,
            "func": func
        }

    def execute(self, name, **kwargs):
        if name not in self._tools:
            return f"Error: Tool '{name}' does not exist."
        try:
            return self._tools[name]["func"](**kwargs)
        except Exception as error:
            return f"Error executing '{name}': {str(error)}"

    def get_definitions(self):
        definitions = []
        for tool in self._tools.values():
            definitions.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["parameters"]
                }
            })
        return definitions