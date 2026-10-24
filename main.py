import json
import sys
import os
from core.orchestrator import Orchestrator

def load_config(config_path="config.json"):
    if not os.path.exists(config_path):
        print(f"Configuration file {config_path} not found.")
        sys.exit(1)
    with open(config_path, "r") as file:
        return json.load(file)

def main():
    config = load_config()
    orchestrator = Orchestrator(config)
    try:
        orchestrator.run()
    except KeyboardInterrupt:
        orchestrator.speaker.speak("Deactivating subsystems.")
        orchestrator.speaker.stop()
        sys.exit(0)

if __name__ == "__main__":
    main()