import psutil
import subprocess
import os
import platform

class SystemTools:
    @staticmethod
    def get_system_vitals():
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        battery = psutil.sensors_battery()
        bat_str = f"{battery.percent}%" if battery else "A/C Power"
        return f"CPU: {cpu}% | RAM: {mem.percent}% | Disk: {disk.percent}% | Battery: {bat_str}"

    @staticmethod
    def execute_terminal(command):
        try:
            res = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=15)
            output = res.stdout if res.stdout else res.stderr
            return output.strip() if output else "Execution successful with no output."
        except Exception as e:
            return f"Command failed: {str(e)}"

    @staticmethod
    def manage_process(process_name, action="kill"):
        found = False
        for proc in psutil.process_iter(['name', 'pid']):
            if process_name.lower() in proc.info['name'].lower():
                found = True
                if action == "kill":
                    proc.kill()
        return f"Terminated {process_name}" if found else f"Process {process_name} not found."