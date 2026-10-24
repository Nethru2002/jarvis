import os
import subprocess
import platform

class ApplicationTools:
    @staticmethod
    def launch_app(app_name):
        current_os = platform.system()
        try:
            if current_os == "Darwin":
                subprocess.run(["open", "-a", app_name])
            elif current_os == "Windows":
                subprocess.run(f"start {app_name}", shell=True)
            else:
                subprocess.run([app_name.lower()], shell=True)
            return f"Launched application: {app_name}"
        except Exception as e:
            return f"Failed to start {app_name}: {str(e)}"