import edge_tts
import tempfile
import os


async def text_to_speech(text: str) -> str:

    communicate = edge_tts.Communicate(
        text,
        voice="en-US-JennyNeural",
    )

    temp_file = tempfile.NamedTemporaryFile(
        suffix=".mp3",
        delete=False
    )

    temp_path = temp_file.name
    temp_file.close()

    try:
        await communicate.save(temp_path)

        return temp_path

    except Exception:
        if os.path.exists(temp_path):
            os.remove(temp_path)

        raise
