from groq import AsyncGroq
from app.core.config import GROQ_API_KEY

client = AsyncGroq(api_key=GROQ_API_KEY)

STT_MODEL = "whisper-large-v3-turbo"


async def transcribe_audio(file):
    audio_bytes = await file.read()

    transcription = await client.audio.transcriptions.create(
        file=(
            file.filename,
            audio_bytes,
            file.content_type
        ),
        model=STT_MODEL,
        response_format="text"
    )

    return transcription