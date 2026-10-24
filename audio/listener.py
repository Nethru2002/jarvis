import speech_recognition as sr

class AudioListener:
    def __init__(self, ambient_duration=1.0, speech_timeout=5, phrase_limit=10):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.ambient_duration = ambient_duration
        self.speech_timeout = speech_timeout
        self.phrase_limit = phrase_limit
        self._calibrate()

    def _calibrate(self):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=self.ambient_duration)
            self.recognizer.dynamic_energy_threshold = True

    def listen(self):
        with self.microphone as source:
            print("[System Listening...]")
            try:
                audio = self.recognizer.listen(
                    source, 
                    timeout=self.speech_timeout, 
                    phrase_time_limit=self.phrase_limit
                )
                text = self.recognizer.recognize_google(audio)
                print(f"[Captured Voice]: {text}")
                return text.strip()
            except (sr.WaitTimeoutError, sr.UnknownValueError):
                return ""
            except sr.RequestError:
                print("[Listener Error]: Network connectivity issue on STT.")
                return ""