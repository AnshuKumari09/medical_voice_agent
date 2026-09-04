import os


TTS_ENABLED = os.getenv("TTS_ENABLED", "true").lower() == "true"


def speak_text(text: str):
    if not TTS_ENABLED:
        return

    import pythoncom
    import pyttsx3

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
