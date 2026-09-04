import edge_tts


async def text_to_speech(text: str) -> bytes:
    communicate = edge_tts.Communicate(
        text,
        voice="en-US-JennyNeural"
    )

    audio_chunks = []

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_chunks.append(chunk["data"])

    return b"".join(audio_chunks)
