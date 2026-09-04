import base64
import tempfile
import os

import edge_tts


async def text_to_speech(text: str) -> str:

    communicate = edge_tts.Communicate(
        text,
        voice="en-US-JennyNeural",
    )

    with tempfile.NamedTemporaryFile(
        suffix=".mp3",
        delete=False
    ) as temp_file:

        temp_path = temp_file.name

    try:

        await communicate.save(temp_path)

        with open(temp_path, "rb") as audio_file:
            audio_bytes = audio_file.read()

        return base64.b64encode(audio_bytes).decode("utf-8")

    finally:

        if os.path.exists(temp_path):
            os.remove(temp_path)
