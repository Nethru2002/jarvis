import json
from ollama import Client

class OllamaBrain:
    def __init__(self, host="http://localhost:11434", model="llama3.2", temperature=0.4):
        self.client = Client(host=host)
        self.model = model
        self.temperature = temperature

    def construct_system_message(self, memory_facts, tools):
        fact_str = "\n".join([f"- {k}: {v}" for k, v in memory_facts.items()])
        tools_str = json.dumps(tools, indent=2)
        return (
            "You are JARVIS, an autonomous computer operations assistant. "
            "You are direct, exceptionally sharp, professional, and efficient. "
            "You have access to execution tools. If an operation requires a tool, emit a JSON object "
            "matching format: {\"name\": \"tool_name\", \"arguments\": {\"arg\": \"val\"}}. "
            "Do not include conversational formatting when calling tools. "
            f"Tools available:\n{tools_str}\n"
            f"Stored long-term facts:\n{fact_str}\n"
            "If no tools are required, converse directly with the user."
        )

    def process_turn(self, messages):
        response = self.client.chat(
            model=self.model,
            messages=messages,
            options={"temperature": self.temperature}
        )
        return response["message"]["content"].strip()