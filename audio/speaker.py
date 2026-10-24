import pyttsx3
import queue
import threading

class Speaker:
    def __init__(self, rate=185, volume=1.0):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", rate)
        self.engine.setProperty("volume", volume)
        self._configure_voice()
        self.queue = queue.Queue()
        self.is_running = True
        self.thread = threading.Thread(target=self._process_queue, daemon=True)
        self.thread.start()

    def _configure_voice(self):
        voices = self.engine.getProperty("voices")
        for voice in voices:
            if "male" in voice.name.lower() or "david" in voice.name.lower():
                self.engine.setProperty("voice", voice.id)
                break

    def _process_queue(self):
        while self.is_running:
            text = self.queue.get()
            if text is None:
                break
            self.engine.say(text)
            self.engine.runAndWait()
            self.queue.task_done()

    def speak(self, text):
        print(f"\nJARVIS: {text}\n")
        self.queue.put(text)

    def stop(self):
        self.is_running = False
        self.queue.put(None)
        self.thread.join()