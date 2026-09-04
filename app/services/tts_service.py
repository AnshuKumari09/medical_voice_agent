import pythoncom
import pyttsx3

def speak_text(text: str):
    pythoncom.CoInitialize()

    try:
        engine = pyttsx3.init()

        engine.setProperty("rate", 165)
        engine.setProperty("volume", 1.0)

        engine.say(text)
        engine.runAndWait()

        engine.stop()

    finally:
        pythoncom.CoUninitialize()