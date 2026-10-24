import json
from core.bus import EventBus
from audio.listener import AudioListener
from audio.speaker import Speaker
from brain.llm import OllamaBrain
from brain.registry import ToolRegistry
from memory.database import MemoryManager
from tools.system_tools import SystemTools
from tools.web_tools import WebTools
from tools.app_tools import ApplicationTools

class Orchestrator:
    def __init__(self, config):
        self.config = config
        self.bus = EventBus()
        self.memory = MemoryManager(config["database"]["path"])
        self.listener = AudioListener(
            ambient_duration=config["audio"]["ambient_duration"],
            speech_timeout=config["audio"]["speech_timeout"],
            phrase_limit=config["audio"]["phrase_limit"]
        )
        self.speaker = Speaker(
            rate=config["audio"]["voice_rate"],
            volume=config["audio"]["voice_volume"]
        )
        self.brain = OllamaBrain(
            host=config["ollama"]["host"],
            model=config["ollama"]["model"],
            temperature=config["ollama"]["temperature"]
        )
        self.registry = ToolRegistry()
        self._register_all_tools()
        self.wake_word = config["audio"]["wake_word"].lower()

    def _register_all_tools(self):
        self.registry.register(
            name="get_system_vitals",
            description="Returns CPU, RAM, Disk, and Battery diagnostics.",
            parameters={"type": "object", "properties": {}},
            func=SystemTools.get_system_vitals
        )
        self.registry.register(
            name="execute_terminal",
            description="Runs shell command on the host OS.",
            parameters={"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]},
            func=SystemTools.execute_terminal
        )
        self.registry.register(
            name="manage_process",
            description="Kills a process by name.",
            parameters={"type": "object", "properties": {"process_name": {"type": "string"}}, "required": ["process_name"]},
            func=SystemTools.manage_process
        )
        self.registry.register(
            name="search_web",
            description="Searches DuckDuckGo and returns extracts.",
            parameters={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
            func=WebTools.search_web
        )
        self.registry.register(
            name="open_url",
            description="Launches a URL in default browser.",
            parameters={"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]},
            func=WebTools.open_url
        )
        self.registry.register(
            name="launch_app",
            description="Launches an OS desktop application.",
            parameters={"type": "object", "properties": {"app_name": {"type": "string"}}, "required": ["app_name"]},
            func=ApplicationTools.launch_app
        )
        self.registry.register(
            name="store_memory",
            description="Stores key-value pair to long term database.",
            parameters={"type": "object", "properties": {"key": {"type": "string"}, "value": {"type": "string"}}, "required": ["key", "value"]},
            func=self.memory.remember
        )

    def handle_request(self, user_text):
        self.memory.save_message("user", user_text)
        history = self.memory.get_recent_history(limit=8)
        facts = self.memory.dump_knowledge()
        tools_def = self.registry.get_definitions()
        
        system_msg = {"role": "system", "content": self.brain.construct_system_message(facts, tools_def)}
        messages = [system_msg] + history
        
        raw_response = self.brain.process_turn(messages)
        
        try:
            parsed = json.loads(raw_response)
            if isinstance(parsed, dict) and "name" in parsed:
                tool_name = parsed["name"]
                tool_args = parsed.get("arguments", {})
                tool_res = self.registry.execute(tool_name, **tool_args)
                
                self.memory.save_message("assistant", f"Invoked: {tool_name}")
                self.memory.save_message("user", f"Tool output: {tool_res}")
                
                updated_history = self.memory.get_recent_history(limit=8)
                follow_up_messages = [system_msg] + updated_history
                final_response = self.brain.process_turn(follow_up_messages)
                self.memory.save_message("assistant", final_response)
                self.speaker.speak(final_response)
                return
        except (json.JSONDecodeError, TypeError):
            pass

        self.memory.save_message("assistant", raw_response)
        self.speaker.speak(raw_response)

    def run(self):
        self.speaker.speak("Online and operational, sir.")
        while True:
            heard = self.listener.listen()
            if not heard:
                continue
            
            clean_heard = heard.lower()
            if self.wake_word in clean_heard:
                command = clean_heard.split(self.wake_word, 1)[-1].strip()
                if not command:
                    self.speaker.speak("Yes, sir?")
                    command = self.listener.listen()
                    if not command:
                        continue
                self.handle_request(command)