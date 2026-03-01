from gtts import gTTS
from playsound import playsound
import os
import tempfile

class MarathiTTS:
    def speak(self, text):
        tts = gTTS(text=text, lang='mr')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            temp_path = fp.name
        tts.save(temp_path)
        playsound(temp_path)
        os.remove(temp_path)
